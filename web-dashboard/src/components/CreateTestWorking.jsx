import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import TestStatusTracker from './TestStatusTracker';
import DuplicateDetectionDialog from './DuplicateDetectionDialog';
import { 
  Sparkles, 
  Bot, 
  Target, 
  CheckCircle, 
  Clock, 
  ArrowRight,
  Lightbulb,
  Zap,
  Globe,
  Play,
  FileText,
  Brain,
  Upload,
  Eye,
  RefreshCw,
  AlertTriangle,
  Building2,
  ShoppingCart,
  CreditCard,
  GraduationCap,
  Stethoscope,
  Car,
  Plane,
  Home
} from 'lucide-react';

const CreateTestWorking = ({ user, onNavigate, apiService }) => {
  // Core state
  const [applications, setApplications] = useState([]);
  const [selectedApp, setSelectedApp] = useState('');
  const [testDescription, setTestDescription] = useState('');
  const [testName, setTestName] = useState('');
  const [priority, setPriority] = useState('medium');
  
  // Test creation state
  const [isCreating, setIsCreating] = useState(false);
  const [currentJobId, setCurrentJobId] = useState(null);
  const [agentProgress, setAgentProgress] = useState([]);
  const [createdTests, setCreatedTests] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  
  // Duplicate detection state
  const [showDuplicateDialog, setShowDuplicateDialog] = useState(false);
  const [duplicateData, setDuplicateData] = useState(null);
  const [pendingTestConfig, setPendingTestConfig] = useState(null);
  
  // Requirements.json support
  const [requirementsFile, setRequirementsFile] = useState(null);
  const [requirementsData, setRequirementsData] = useState(null);
  
  // Polling for real-time updates
  const pollingInterval = useRef(null);

  // Industry templates
  const industryTemplates = [
    {
      name: 'HRMS/HCM',
      icon: Building2,
      description: 'Human Resource Management System with employee lifecycle management',
      testDescription: 'Test HRMS platform including employee management, leave requests, performance reviews, and payroll processing'
    },
    {
      name: 'E-Commerce',
      icon: ShoppingCart,
      description: 'Online retail platform with shopping and payment workflows',
      testDescription: 'Test e-commerce platform including product catalog, shopping cart, checkout process, and order management'
    },
    {
      name: 'Banking/FinTech',
      icon: CreditCard,
      description: 'Financial services platform with secure transactions',
      testDescription: 'Test banking platform including account management, fund transfers, bill payments, and transaction history'
    },
    {
      name: 'Education/LMS',
      icon: GraduationCap,
      description: 'Learning Management System with course delivery',
      testDescription: 'Test LMS platform including course enrollment, content delivery, assessments, and progress tracking'
    },
    {
      name: 'Healthcare',
      icon: Stethoscope,
      description: 'Healthcare management system with patient workflows',
      testDescription: 'Test healthcare platform including patient registration, appointment scheduling, medical records, and billing'
    },
    {
      name: 'Real Estate',
      icon: Home,
      description: 'Property management platform with listings and transactions',
      testDescription: 'Test real estate platform including property listings, search functionality, agent management, and lead tracking'
    },
    {
      name: 'Travel/Booking',
      icon: Plane,
      description: 'Travel booking platform with reservation management',
      testDescription: 'Test travel platform including flight search, hotel bookings, itinerary management, and payment processing'
    },
    {
      name: 'Automotive',
      icon: Car,
      description: 'Automotive platform with vehicle management and services',
      testDescription: 'Test automotive platform including vehicle listings, dealer management, service scheduling, and financing workflows'
    }
  ];

  // Agent phases for progress tracking
  const agentPhases = [
    { name: 'Discovery Agent', description: 'Analyzing application structure and user flows', color: 'blue' },
    { name: 'Generation Agent', description: 'Creating comprehensive test scenarios', color: 'purple' },
    { name: 'Code Agent', description: 'Generating automated test code', color: 'green' },
    { name: 'Validation Agent', description: 'Validating and optimizing test suite', color: 'orange' }
  ];

  // Load applications on component mount
  useEffect(() => {
    loadApplications();
  }, []);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, []);

  const loadApplications = async () => {
    try {
      console.log('🔍 Loading applications...');
      const response = await apiService.getApplications();
      console.log('📊 Applications API response:', response);
      if (response && response.data) {
        console.log('✅ Setting applications:', response.data.length, 'applications found');
        setApplications(response.data);
      } else {
        console.log('❌ No applications data in response');
      }
    } catch (error) {
      console.error('❌ Failed to load applications:', error);
      setError('Failed to load applications. Please refresh the page.');
    }
  };

  const handleTemplateClick = (template) => {
    console.log('🎯 Template clicked:', template.name);
    console.log('📝 Before update - selectedApp:', selectedApp, 'testDescription:', testDescription);
    
    setTestName(`${template.name} Test Suite`);
    setTestDescription(template.testDescription);
    setError(null);
    
    console.log('📝 After update - testDescription will be:', template.testDescription);
    console.log('🔘 Button should be enabled if selectedApp exists:', !!selectedApp);
  };

  const handleRequirementsUpload = async (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/json') {
      setRequirementsFile(file);
      setError(null);
      
      try {
        // Use API service to upload and validate the file
        const response = await apiService.uploadRequirementsFile(file);
        
        if (response.status === 'success') {
          const data = response.data.requirements_data;
          setRequirementsData(data);
          setTestName(data.testSuiteName || 'Requirements-based Test Suite');
          setTestDescription(data.description || 'Test suite based on uploaded requirements');
          
          // Show validation results
          const validation = response.data.validation;
          if (validation.errors && validation.errors.length > 0) {
            setError(`Validation errors: ${validation.errors.join(', ')}`);
          } else if (validation.warnings && validation.warnings.length > 0) {
            console.warn('Validation warnings:', validation.warnings);
          }
        }
      } catch (error) {
        console.error('Requirements upload failed:', error);
        setError(`Failed to upload requirements file: ${error.message}`);
        setRequirementsFile(null);
      }
    } else {
      setError('Please upload a valid JSON file.');
    }
  };

  // Polling is now handled by TestStatusTracker component

  const loadCreatedTests = async (jobId) => {
    try {
      const response = await apiService.getAgentJobTests(jobId);
      if (response && response.data) {
        setCreatedTests(response.data);
      }
    } catch (error) {
      console.error('Failed to load created tests:', error);
    }
  };

  const handleCreateTests = async () => {
    if (!selectedApp || !testDescription.trim()) {
      setError('Please select an application and provide a test description.');
      return;
    }

    // Find the full application object
    const selectedApplication = applications.find(app => app.id.toString() === selectedApp);
    if (!selectedApplication) {
      setError('Selected application not found. Please refresh and try again.');
      return;
    }

    setError(null);
    setSuccess(null);

    try {
      // First, check for duplicates
      const duplicateResponse = await apiService.checkForDuplicates(
        selectedApplication.id,
        testName || `${selectedApplication.name} Test Suite`,
        testDescription,
        requirementsData
      );

      if (duplicateResponse && duplicateResponse.data) {
        const duplicateInfo = duplicateResponse.data;
        
        // Store the test configuration for later use
        const testConfig = {
          application_id: selectedApplication.id,
          test_name: testName || `${selectedApplication.name} Test Suite`,
          test_description: testDescription,
          priority: priority,
          requirements_data: requirementsData
        };
        setPendingTestConfig(testConfig);
        
        // Show duplicate detection dialog
        setDuplicateData(duplicateInfo);
        setShowDuplicateDialog(true);
      } else {
        // No duplicates found, proceed with creation
        await createTestDirectly();
      }
    } catch (error) {
      setError(`Failed to check for duplicates: ${error.message}`);
    }
  };

  const createTestDirectly = async (testConfig = null) => {
    // Find the full application object
    const selectedApplication = applications.find(app => app.id.toString() === selectedApp);
    if (!selectedApplication) {
      setError('Selected application not found. Please refresh and try again.');
      return;
    }

    const config = testConfig || pendingTestConfig || {
      application_id: selectedApplication.id,
      test_name: testName || `${selectedApplication.name} Test Suite`,
      test_description: testDescription,
      priority: priority,
      requirements_data: requirementsData
    };

    setIsCreating(true);
    setError(null);

    try {
      const response = await apiService.createTest(config);

      if (response && response.data && response.data.job_id) {
        setCurrentJobId(response.data.job_id);
        // Real-time polling is now handled by TestStatusTracker component
        
        // Auto-scroll to agent processing section
        setTimeout(() => {
          const agentSection = document.getElementById('agent-processing-section');
          if (agentSection) {
            agentSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, 500);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      setIsCreating(false);
      setError(`Failed to create tests: ${error.message}`);
    }
  };

  const handleUpdateExisting = async (existingSuite) => {
    setIsCreating(true);
    setError(null);

    try {
      const response = await apiService.updateExistingTestSuite(
        existingSuite.id,
        selectedApp.id,
        testName || `${selectedApp.name} Test Suite`,
        testDescription,
        requirementsData
      );

      if (response && response.status === 'success') {
        setSuccess('Test suite updated successfully!');
        // Optionally refresh the page or redirect
      } else {
        throw new Error('Failed to update test suite');
      }
    } catch (error) {
      setError(`Failed to update test suite: ${error.message}`);
    } finally {
      setIsCreating(false);
    }
  };

  const resetForm = () => {
    setTestName('');
    setTestDescription('');
    setRequirementsFile(null);
    setRequirementsData(null);
    setError(null);
    setSuccess(null);
    setShowResults(false);
    setCreatedTests([]);
    setAgentProgress([]);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Create AI-Powered Tests</h1>
        <p className="text-muted-foreground">
          Generate comprehensive test suites using AI agents with real-time progress tracking
        </p>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800 flex items-center justify-between">
            <span>{success}</span>
            <Button 
              onClick={() => onNavigate('manage-tests')}
              size="sm"
              className="ml-4"
            >
              Go to Test Management
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Main Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Test Configuration
          </CardTitle>
          <CardDescription>
            Configure your test suite with application selection and test requirements
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="application">Select Application</Label>
              <Select value={selectedApp} onValueChange={setSelectedApp}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose your application" />
                </SelectTrigger>
                <SelectContent>
                  {applications.map((app) => (
                    <SelectItem key={app.id} value={app.id.toString()}>
                      <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4" />
                        {app.name}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              {/* Application URL Display */}
              {selectedApp && (() => {
                const selectedApplication = applications.find(app => app.id.toString() === selectedApp);
                return selectedApplication ? (
                  <div className="mt-3 space-y-2">
                    <Label htmlFor="appUrl">Application URL</Label>
                    <Input
                      id="appUrl"
                      value={selectedApplication.url}
                      readOnly
                      className="bg-gray-50 text-gray-700"
                    />
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        {selectedApplication.type}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {selectedApplication.category}
                      </Badge>
                      <span className="text-xs text-gray-600">• {selectedApplication.description}</span>
                    </div>
                  </div>
                ) : null;
              })()}
            </div>
            
            <div>
              <Label htmlFor="priority">Test Priority</Label>
              <Select value={priority} onValueChange={setPriority}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low Priority</SelectItem>
                  <SelectItem value="medium">Medium Priority</SelectItem>
                  <SelectItem value="high">High Priority</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <Label htmlFor="testName">Test Suite Name (Optional)</Label>
            <Input
              id="testName"
              value={testName}
              onChange={(e) => setTestName(e.target.value)}
              placeholder="e.g., User Registration Flow Test"
            />
          </div>

          <div>
            <Label htmlFor="description">Test Description</Label>
            <Textarea
              id="description"
              value={testDescription}
              onChange={(e) => setTestDescription(e.target.value)}
              placeholder="Describe what you want to test in plain English..."
              rows={4}
            />
          </div>

          <div className="flex gap-4">
            <Button 
              onClick={() => {
                console.log('🔘 Button clicked - selectedApp:', selectedApp, 'testDescription:', testDescription.trim());
                console.log('🔘 Button disabled conditions:', {
                  isCreating,
                  noSelectedApp: !selectedApp,
                  noTestDescription: !testDescription.trim()
                });
                handleCreateTests();
              }}
              disabled={isCreating || !selectedApp || !testDescription.trim()}
              className="flex-1"
            >
              {isCreating ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Creating Tests...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Create Tests
                </>
              )}
            </Button>
            
            <Button variant="outline" onClick={resetForm}>
              Reset Form
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Industry Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Industry Templates
          </CardTitle>
          <CardDescription>
            Quick start with pre-configured templates for popular application types
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {industryTemplates.map((template, index) => (
              <div
                key={index}
                className="border rounded-lg p-4 cursor-pointer hover:border-blue-300 hover:bg-blue-50 transition-colors group"
                onClick={() => handleTemplateClick(template)}
              >
                <div className="flex items-center gap-3 mb-3">
                  <template.icon className="h-6 w-6 text-blue-500 group-hover:text-blue-600" />
                  <h3 className="font-semibold text-sm">{template.name}</h3>
                </div>
                <p className="text-xs text-muted-foreground">{template.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Requirements.json Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Requirements Upload
          </CardTitle>
          <CardDescription>
            Upload a requirements.json file with structured test definitions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              accept=".json"
              onChange={handleRequirementsUpload}
              className="hidden"
              id="requirements-upload"
            />
            <label htmlFor="requirements-upload" className="cursor-pointer">
              <Upload className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-600">
                Click to upload requirements.json file
              </p>
              {requirementsFile && (
                <p className="text-xs text-green-600 mt-2">
                  ✓ {requirementsFile.name} uploaded
                </p>
              )}
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Real-time Agent Progress */}
      {isCreating && currentJobId && (
        <div id="agent-processing-section">
          <TestStatusTracker
          jobId={currentJobId}
          apiService={apiService}
          onComplete={async (jobId) => {
            setIsCreating(false);
            await loadCreatedTests(jobId);
            setSuccess('🎉 Tests created successfully! Go to "Test Management" to view, edit, and execute your test suite.');
            setShowResults(true);
          }}
          onError={(error) => {
            setIsCreating(false);
            setError(error);
          }}
        />
        </div>
      )}

      {/* Created Tests Results */}
      {showResults && createdTests.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Created Tests
            </CardTitle>
            <CardDescription>
              {createdTests.length} test{createdTests.length !== 1 ? 's' : ''} created successfully
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {createdTests.map((test, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{test.name}</h4>
                    <Badge variant="outline">{test.type || 'Functional'}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{test.description}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span>📁 {test.file_path}</span>
                    <span>⚡ {test.confidence_score}% confidence</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Duplicate Detection Dialog */}
      <DuplicateDetectionDialog
        isOpen={showDuplicateDialog}
        onClose={() => setShowDuplicateDialog(false)}
        duplicateData={duplicateData}
        onCreateNew={() => {
          setShowDuplicateDialog(false);
          createTestDirectly();
        }}
        onUpdateExisting={(existingSuite) => {
          setShowDuplicateDialog(false);
          handleUpdateExisting(existingSuite);
        }}
        onCancel={() => {
          setShowDuplicateDialog(false);
          setPendingTestConfig(null);
          setDuplicateData(null);
        }}
      />
    </div>
  );
};

export default CreateTestWorking;
