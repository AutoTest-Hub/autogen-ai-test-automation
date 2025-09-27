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
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
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
  AlertTriangle,
  RefreshCw,
  Eye,
  Users,
  Activity,
  Loader2,
  CheckCircle2,
  XCircle,
  Pause,
  Bell,
  TrendingUp,
  Shield,
  Edit,
  Merge,
  Info,
  BarChart3,
  Building2,
  ShoppingCart,
  CreditCard,
  GraduationCap,
  Stethoscope,
  Car,
  Plane,
  Home
} from 'lucide-react';
import { enhancedApiService } from '../lib/api-enhanced';

const CreateTestComplete = ({ user, onNavigate }) => {
  const [applications, setApplications] = useState([]);
  const [selectedApp, setSelectedApp] = useState('');
  const [testDescription, setTestDescription] = useState('');
  const [testName, setTestName] = useState('');
  const [testType, setTestType] = useState('');
  const [priority, setPriority] = useState('medium');
  const [isCreating, setIsCreating] = useState(false);
  const [currentJobId, setCurrentJobId] = useState(null);
  const [agentStatus, setAgentStatus] = useState(null);
  const [generatedTests, setGeneratedTests] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Duplicate detection and hybrid management
  const [duplicateAnalysis, setDuplicateAnalysis] = useState(null);
  const [showDuplicateDialog, setShowDuplicateDialog] = useState(false);
  const [coverageAnalysis, setCoverageAnalysis] = useState(null);
  const [applicationSummary, setApplicationSummary] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // Real-time monitoring
  const pollingInterval = useRef(null);
  const [realTimeUpdates, setRealTimeUpdates] = useState([]);
  const [notifications, setNotifications] = useState([]);

  const agentPhases = [
    { name: 'Discovery Agent', description: 'Analyzing application structure and user flows', icon: Eye, color: 'blue' },
    { name: 'Generation Agent', description: 'Creating comprehensive test scenarios', icon: Brain, color: 'purple' },
    { name: 'Code Agent', description: 'Generating automated test code', icon: FileText, color: 'green' },
    { name: 'Validation Agent', description: 'Validating and optimizing test suite', icon: CheckCircle, color: 'orange' }
  ];

  const testTypeSuggestions = [
    {
      type: 'functional',
      title: 'Functional Testing',
      description: 'Test core features and user workflows',
      icon: Target,
      examples: ['User registration', 'Login/logout', 'Form submissions', 'Navigation']
    },
    {
      type: 'ui',
      title: 'UI/UX Testing',
      description: 'Verify visual elements and user experience',
      icon: Sparkles,
      examples: ['Button clicks', 'Form validation', 'Responsive design', 'Accessibility']
    },
    {
      type: 'integration',
      title: 'Integration Testing',
      description: 'Test API calls and data flow',
      icon: Zap,
      examples: ['API responses', 'Database operations', 'Third-party services', 'Payment processing']
    },
    {
      type: 'performance',
      title: 'Performance Testing',
      description: 'Check speed and responsiveness',
      icon: Clock,
      examples: ['Page load times', 'Response times', 'Resource usage', 'Stress testing']
    }
  ];

  useEffect(() => {
    loadApplications();
    loadSuggestions();
    requestNotificationPermission();
    
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, []);

  useEffect(() => {
    if (selectedApp) {
      loadApplicationSummary();
    }
  }, [selectedApp]);

  useEffect(() => {
    if (selectedApp && testDescription && testDescription.length > 10) {
      const debounceTimer = setTimeout(() => {
        checkForDuplicatesAndAnalyze();
      }, 1000);
      
      return () => clearTimeout(debounceTimer);
    }
  }, [selectedApp, testDescription, testName]);

  const requestNotificationPermission = async () => {
    await enhancedApiService.requestNotificationPermission();
  };

  const addNotification = (type, message, data = {}) => {
    const notification = {
      id: Date.now(),
      type,
      message,
      timestamp: new Date().toLocaleTimeString(),
      data
    };
    
    setNotifications(prev => [notification, ...prev.slice(0, 4)]);
    enhancedApiService.sendNotification(type, message, data);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  };

  const loadApplications = async () => {
    try {
      const response = await enhancedApiService.getApplications();
      if (response.status === 'success') {
        setApplications(response.data);
      }
    } catch (error) {
      console.error('Failed to load applications:', error);
      setApplications([
        { id: 1, name: 'E-commerce Store', url: 'https://mystore.example.com', type: 'ecommerce' },
        { id: 2, name: 'Admin Dashboard', url: 'https://admin.mystore.example.com', type: 'admin' }
      ]);
    }
  };

  const loadApplicationSummary = async () => {
    if (!selectedApp) return;
    
    try {
      const response = await enhancedApiService.getApplicationTestSummary(selectedApp);
      if (response.status === 'success') {
        setApplicationSummary(response.data);
      }
    } catch (error) {
      console.error('Failed to load application summary:', error);
    }
  };

  // Initialize suggestions
  React.useEffect(() => {
    setSuggestions([
      "Test the complete checkout process from cart to payment confirmation",
      "Verify user registration with email verification workflow", 
      "Test product search and filtering functionality",
      "Validate form error handling and validation messages",
      "Test user login with different credential scenarios",
      "Verify responsive design on mobile and tablet devices"
    ]);
  }, []);

  const industryTemplates = [
    {
      name: 'HRMS/HCM',
      icon: Building2,
      description: 'Human Resource Management Systems with employee lifecycle management',
      url: 'https://opensource-demo.orangehrmlive.com',
      features: ['Employee Management', 'Leave Management', 'Attendance', 'Performance Reviews', 'Recruitment', 'Payroll'],
      testDescription: 'Test complete HRMS functionality including employee onboarding, leave management, attendance tracking, and performance evaluation workflows'
    },
    {
      name: 'E-Commerce',
      icon: ShoppingCart,
      description: 'Online retail platforms with shopping cart and payment processing',
      url: 'https://demo.opencart.com',
      features: ['Product Catalog', 'Shopping Cart', 'Payment Processing', 'Order Management', 'User Accounts', 'Inventory'],
      testDescription: 'Test end-to-end e-commerce functionality including product browsing, cart operations, checkout process, and order management'
    },
    {
      name: 'Banking/FinTech',
      icon: CreditCard,
      description: 'Financial services with secure transactions and account management',
      url: 'https://demo.testfire.net',
      features: ['Account Management', 'Fund Transfers', 'Bill Payments', 'Transaction History', 'Security', 'Reporting'],
      testDescription: 'Test banking application security, fund transfers, account management, and transaction processing workflows'
    },
    {
      name: 'Education/LMS',
      icon: GraduationCap,
      description: 'Learning Management Systems with course delivery and assessment',
      url: 'https://school.moodledemo.net',
      features: ['Course Management', 'Student Enrollment', 'Assessments', 'Gradebook', 'Communication', 'Reports'],
      testDescription: 'Test learning management system including course creation, student enrollment, assessment delivery, and grade management'
    },
    {
      name: 'Healthcare',
      icon: Stethoscope,
      description: 'Healthcare management systems with patient records and scheduling',
      url: 'https://demo.openmrs.org',
      features: ['Patient Records', 'Appointment Scheduling', 'Medical History', 'Prescriptions', 'Lab Results', 'Billing'],
      testDescription: 'Test healthcare system functionality including patient management, appointment scheduling, and medical record management'
    },
    {
      name: 'Real Estate',
      icon: Home,
      description: 'Property management and real estate platforms',
      url: 'https://demo.propertywebbuilder.com',
      features: ['Property Listings', 'Search & Filter', 'Agent Management', 'Lead Generation', 'Virtual Tours', 'CRM'],
      testDescription: 'Test real estate platform including property search, listing management, agent workflows, and lead generation'
    },
    {
      name: 'Travel/Booking',
      icon: Plane,
      description: 'Travel booking systems with reservations and itinerary management',
      url: 'https://phptravels.net/demo',
      features: ['Flight Booking', 'Hotel Reservations', 'Car Rentals', 'Package Deals', 'User Profiles', 'Payment'],
      testDescription: 'Test travel booking platform including flight search, hotel reservations, payment processing, and itinerary management'
    },
    {
      name: 'Automotive',
      icon: Car,
      description: 'Automotive platforms with vehicle management and services',
      url: 'https://demo.autotrader.com',
      features: ['Vehicle Listings', 'Search & Compare', 'Dealer Management', 'Financing', 'Service Booking', 'Reviews'],
      testDescription: 'Test automotive platform including vehicle search, comparison tools, dealer interactions, and service booking workflows'
    }
  ];

  const handleTemplateClick = (template) => {
    setFormData(prev => ({
      ...prev,
      testName: `${template.name} Test Suite`,
      testDescription: template.testDescription
    }));
    
    // Show success message
    setNotifications(prev => [...prev, {
      id: Date.now(),
      type: 'success',
      message: `Applied ${template.name} template successfully!`
    }]);
  };

  const checkForDuplicatesAndAnalyze = async () => {
    if (!selectedApp || !testDescription) return;

    setIsAnalyzing(true);
    try {
      // Check for duplicates
      const duplicateResponse = await enhancedApiService.checkForDuplicates(
        selectedApp, testName, testDescription
      );
      
      if (duplicateResponse.status === 'success') {
        setDuplicateAnalysis(duplicateResponse.data);
        
        if (duplicateResponse.data.has_duplicates) {
          setShowDuplicateDialog(true);
          addNotification('warning', `Found ${duplicateResponse.data.duplicate_count} similar test(s)`);
        }
      }

      // Analyze coverage
      const coverageResponse = await enhancedApiService.analyzeCoverage(selectedApp, testDescription);
      if (coverageResponse.status === 'success') {
        setCoverageAnalysis(coverageResponse.data);
      }
      
    } catch (error) {
      console.error('Failed to analyze duplicates:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const startRealTimeMonitoring = (jobId) => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
    }

    pollingInterval.current = setInterval(async () => {
      try {
        const response = await enhancedApiService.getAgentJobStatus(jobId);
        if (response.status === 'success') {
          setAgentStatus(response.data);
          
          const timestamp = new Date().toLocaleTimeString();
          const currentAgent = response.data.job.current_agent;
          const progress = response.data.job.progress_percentage;
          
          setRealTimeUpdates(prev => [
            ...prev.slice(-4),
            {
              timestamp,
              agent: currentAgent,
              progress,
              status: response.data.job.status,
              message: `${currentAgent} - ${progress}% complete`
            }
          ]);

          // Check for completion
          if (response.data.job.status === 'completed') {
            clearInterval(pollingInterval.current);
            setIsCreating(false);
            addNotification('success', 'Test creation completed successfully!');
            loadGeneratedTests(response.data.job.test_suite_id);
          } else if (response.data.job.status === 'failed') {
            clearInterval(pollingInterval.current);
            setIsCreating(false);
            setError('Test creation failed. Please try again.');
            addNotification('error', 'Test creation failed');
          }
        }
      } catch (error) {
        console.error('Failed to get agent status:', error);
      }
    }, 2000);
  };

  const loadGeneratedTests = async (testSuiteId) => {
    try {
      const response = await enhancedApiService.getTestSuiteTests(testSuiteId);
      if (response.status === 'success') {
        setGeneratedTests(response.data);
        setSuccess(`Successfully created ${response.data.length} test case(s)!`);
      }
    } catch (error) {
      console.error('Failed to load generated tests:', error);
    }
  };

  const handleGenerateTests = async () => {
    if (!selectedApp || !testDescription) return;

    // Check if user wants to proceed despite duplicates
    if (duplicateAnalysis?.has_duplicates && !window.confirm(
      `Found ${duplicateAnalysis.duplicate_count} similar test(s). Do you want to proceed with creating a new test?`
    )) {
      return;
    }

    setError(null);
    setSuccess(null);
    setIsCreating(true);
    setAgentStatus(null);
    setRealTimeUpdates([]);

    try {
      const selectedAppData = applications.find(app => app.id.toString() === selectedApp);
      
      const testRequest = {
        application_name: selectedAppData.name,
        application_url: selectedAppData.url,
        application_type: selectedAppData.type || 'web_application',
        requirements_text: testDescription,
        test_type: testType || 'functional',
        priority: priority
      };

      const response = await enhancedApiService.createTest(testRequest);

      if (response.status === 'success') {
        setCurrentJobId(response.data.job_id);
        startRealTimeMonitoring(response.data.job_id);
        addNotification('info', 'Test creation started successfully!');
        
        setRealTimeUpdates([{
          timestamp: new Date().toLocaleTimeString(),
          agent: 'System',
          progress: 0,
          status: 'started',
          message: 'Test creation initiated successfully'
        }]);
      } else {
        throw new Error(response.message || 'Failed to create tests');
      }
    } catch (error) {
      setError(error.message);
      setIsCreating(false);
      addNotification('error', `Test creation failed: ${error.message}`);
    }
  };

  const handleUpdateExistingTest = async (testId, updateData) => {
    try {
      const response = await enhancedApiService.updateExistingTest(testId, updateData);
      if (response.status === 'success') {
        addNotification('success', 'Test updated successfully!');
        setShowDuplicateDialog(false);
        // Refresh application summary
        loadApplicationSummary();
      }
    } catch (error) {
      addNotification('error', `Failed to update test: ${error.message}`);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setTestDescription(suggestion);
  };

  const handleRunTests = async () => {
    addNotification('info', 'Navigating to test execution...');
    onNavigate('test-results');
  };

  const getAgentStatusIcon = (agentName, currentAgent, status) => {
    if (status === 'completed') return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    if (status === 'failed') return <XCircle className="h-4 w-4 text-red-500" />;
    if (currentAgent === agentName) return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
    return <Clock className="h-4 w-4 text-gray-400" />;
  };

  const getCurrentPhaseIndex = () => {
    if (!agentStatus) return -1;
    const currentAgent = agentStatus.job.current_agent;
    return agentPhases.findIndex(phase => phase.name === currentAgent);
  };

  const getDuplicateActionColor = (recommendation) => {
    switch (recommendation.action_recommendation) {
      case 'update': return 'bg-orange-100 border-orange-300 text-orange-800';
      case 'review': return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      default: return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Notifications */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Create AI-Powered Tests</h1>
          <p className="text-muted-foreground">
            Intelligent test creation with duplicate detection and hybrid management
          </p>
        </div>
        
        {/* Notification Panel */}
        {notifications.length > 0 && (
          <div className="space-y-2 max-w-sm">
            {notifications.map((notification) => (
              <Alert key={notification.id} className={`
                ${notification.type === 'success' ? 'border-green-300 bg-green-50' : ''}
                ${notification.type === 'error' ? 'border-red-300 bg-red-50' : ''}
                ${notification.type === 'warning' ? 'border-orange-300 bg-orange-50' : ''}
                ${notification.type === 'info' ? 'border-blue-300 bg-blue-50' : ''}
              `}>
                <Bell className="h-4 w-4" />
                <AlertDescription className="text-sm">
                  <span className="font-medium">{notification.timestamp}</span> - {notification.message}
                </AlertDescription>
              </Alert>
            ))}
          </div>
        )}
      </div>

      {/* Error/Success Alerts */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-300 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {!isCreating && generatedTests.length === 0 && (
        <>
          {/* Application Summary */}
          {applicationSummary && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Application Test Overview
                </CardTitle>
                <CardDescription>
                  Current test coverage for {applicationSummary.application.name}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {applicationSummary.test_summary.total_tests}
                    </div>
                    <div className="text-sm text-muted-foreground">Total Tests</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {applicationSummary.test_summary.status_distribution.generated || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">Generated</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {applicationSummary.test_summary.status_distribution.active || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">Active</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {applicationSummary.test_summary.top_keywords.length}
                    </div>
                    <div className="text-sm text-muted-foreground">Coverage Areas</div>
                  </div>
                </div>
                
                {applicationSummary.test_summary.top_keywords.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Top Coverage Areas:</h4>
                    <div className="flex flex-wrap gap-2">
                      {applicationSummary.test_summary.top_keywords.slice(0, 8).map((keyword, index) => (
                        <Badge key={index} variant="secondary">
                          {keyword.keyword} ({keyword.count})
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Test Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Test Configuration
                {isAnalyzing && <Loader2 className="h-4 w-4 animate-spin ml-2" />}
              </CardTitle>
              <CardDescription>
                Configure your test with intelligent duplicate detection and coverage analysis
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
                <Label htmlFor="testName">Test Name (Optional)</Label>
                <Input
                  id="testName"
                  value={testName}
                  onChange={(e) => setTestName(e.target.value)}
                  placeholder="e.g., User Registration Flow Test"
                />
              </div>

              <div>
                <Label htmlFor="description">What would you like to test?</Label>
                <Textarea
                  id="description"
                  value={testDescription}
                  onChange={(e) => setTestDescription(e.target.value)}
                  placeholder="Describe what you want to test in plain English. For example: 'Test the complete user registration process including email verification and welcome email'"
                  rows={4}
                />
              </div>

              {/* Coverage Analysis Preview */}
              {coverageAnalysis && (
                <div className="border rounded-lg p-4 bg-blue-50">
                  <h4 className="font-semibold mb-2 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Coverage Analysis
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium">New Coverage:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {coverageAnalysis.new_coverage_areas.slice(0, 3).map((area, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {area}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <span className="font-medium">Coverage Improvement:</span>
                      <div className="text-lg font-bold text-green-600">
                        {Math.round(coverageAnalysis.coverage_improvement * 100)}%
                      </div>
                    </div>
                    <div>
                      <span className="font-medium">Recommendation:</span>
                      <div className="text-xs mt-1">{coverageAnalysis.recommendation}</div>
                    </div>
                  </div>
                </div>
              )}

              <Button 
                onClick={handleGenerateTests} 
                disabled={!selectedApp || !testDescription || isCreating}
                className="w-full"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                {isCreating ? 'Creating Tests...' : 'Generate AI-Powered Tests'}
              </Button>
            </CardContent>
          </Card>

          {/* Duplicate Detection Dialog */}
          <Dialog open={showDuplicateDialog} onOpenChange={setShowDuplicateDialog}>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Duplicate Tests Detected
                </DialogTitle>
                <DialogDescription>
                  We found {duplicateAnalysis?.duplicate_count} similar test(s) for this application. 
                  Review the recommendations below.
                </DialogDescription>
              </DialogHeader>
              
              {duplicateAnalysis && (
                <div className="space-y-4">
                  {/* Overall Recommendation */}
                  <Alert>
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Recommendation:</strong> {duplicateAnalysis.overall_recommendation}
                    </AlertDescription>
                  </Alert>

                  {/* Duplicate Tests */}
                  <div className="space-y-3">
                    {duplicateAnalysis.recommendations.map((rec, index) => (
                      <div key={index} className={`border rounded-lg p-4 ${getDuplicateActionColor(rec)}`}>
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold">{rec.test_name}</h4>
                          <Badge variant={rec.should_update ? 'default' : 'secondary'}>
                            {Math.round(rec.similarity_score * 100)}% similar
                          </Badge>
                        </div>
                        <p className="text-sm mb-3">{rec.update_reason}</p>
                        <div className="flex gap-2">
                          {rec.should_update && (
                            <Button
                              size="sm"
                              onClick={() => handleUpdateExistingTest(rec.test_id, {
                                description: testDescription,
                                name: testName
                              })}
                            >
                              <Edit className="h-3 w-3 mr-1" />
                              Update This Test
                            </Button>
                          )}
                          <Button variant="outline" size="sm">
                            <Eye className="h-3 w-3 mr-1" />
                            View Test
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="flex justify-end gap-2 pt-4 border-t">
                    <Button variant="outline" onClick={() => setShowDuplicateDialog(false)}>
                      Cancel
                    </Button>
                    <Button onClick={() => {
                      setShowDuplicateDialog(false);
                      handleGenerateTests();
                    }}>
                      <Merge className="h-4 w-4 mr-2" />
                      Create New Test Anyway
                    </Button>
                  </div>
                </div>
              )}
            </DialogContent>
          </Dialog>

          {/* Test Type Suggestions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5" />
                Test Type Suggestions
              </CardTitle>
              <CardDescription>
                Choose the type of testing that best fits your needs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {testTypeSuggestions.map((suggestion) => (
                  <div
                    key={suggestion.type}
                    className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                      testType === suggestion.type ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'
                    }`}
                    onClick={() => setTestType(suggestion.type)}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <suggestion.icon className="h-5 w-5 text-blue-500" />
                      <h3 className="font-semibold">{suggestion.title}</h3>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{suggestion.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {suggestion.examples.map((example, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {example}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Industry Templates */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                One-Click Industry Templates
              </CardTitle>
              <CardDescription>
                Get started instantly with pre-configured templates for popular application types
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {industryTemplates.map((template, index) => (
                  <div
                    key={index}
                    className="border rounded-lg p-4 cursor-pointer hover:border-blue-300 hover:bg-blue-50 transition-colors group"
                    onClick={() => handleTemplateClick(template)}
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <template.icon className="h-6 w-6 text-blue-500 group-hover:text-blue-600" />
                      <h3 className="font-semibold">{template.name}</h3>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{template.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {template.features.slice(0, 3).map((feature, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {feature}
                        </Badge>
                      ))}
                      {template.features.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{template.features.length - 3} more
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI Suggestions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                AI Suggestions
              </CardTitle>
              <CardDescription>
                Click on any suggestion to use it as your test description
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className="border rounded-lg p-3 cursor-pointer hover:border-blue-300 hover:bg-blue-50 transition-colors"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    <p className="text-sm">{suggestion}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Real-Time Agent Activity Monitor */}
      {isCreating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 animate-pulse text-blue-500" />
              AI Agents Working
            </CardTitle>
            <CardDescription>
              Our specialized AI agents are analyzing your application and creating comprehensive tests
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Overall Progress */}
            {agentStatus && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Overall Progress</span>
                  <span>{agentStatus.job.progress_percentage}%</span>
                </div>
                <Progress value={agentStatus.job.progress_percentage} />
              </div>
            )}

            {/* Agent Phases */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {agentPhases.map((phase, index) => {
                const isActive = getCurrentPhaseIndex() === index;
                const isCompleted = getCurrentPhaseIndex() > index;
                const isFailed = agentStatus?.job.status === 'failed' && getCurrentPhaseIndex() === index;
                
                return (
                  <div
                    key={phase.name}
                    className={`border rounded-lg p-4 transition-colors ${
                      isActive ? 'border-blue-500 bg-blue-50' : 
                      isCompleted ? 'border-green-500 bg-green-50' :
                      isFailed ? 'border-red-500 bg-red-50' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      {getAgentStatusIcon(phase.name, agentStatus?.job.current_agent, 
                        isCompleted ? 'completed' : isFailed ? 'failed' : agentStatus?.job.status)}
                      <h3 className="font-semibold">{phase.name}</h3>
                    </div>
                    <p className="text-sm text-muted-foreground">{phase.description}</p>
                    {isActive && agentStatus && (
                      <div className="mt-2">
                        <Progress value={agentStatus.job.progress_percentage} className="h-2" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Real-Time Updates */}
            {realTimeUpdates.length > 0 && (
              <div className="border rounded-lg p-4 bg-gray-50">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <RefreshCw className="h-4 w-4" />
                  Live Updates
                </h4>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {realTimeUpdates.slice().reverse().map((update, index) => (
                    <div key={index} className="text-sm flex items-center justify-between">
                      <span className="text-muted-foreground">{update.timestamp}</span>
                      <span className="font-medium">{update.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Generated Tests Results */}
      {generatedTests.length > 0 && !isCreating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              AI-Generated Test Suite Complete
            </CardTitle>
            <CardDescription>
              Your comprehensive test suite is ready! All agents have completed their work.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{generatedTests.length}</div>
                <div className="text-sm text-muted-foreground">Test Cases</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {generatedTests.reduce((sum, test) => sum + (test.scenarios || 0), 0)}
                </div>
                <div className="text-sm text-muted-foreground">Test Scenarios</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">Ready</div>
                <div className="text-sm text-muted-foreground">Status</div>
              </div>
            </div>

            <div className="space-y-3">
              {generatedTests.map((test) => (
                <div key={test.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">{test.name}</h3>
                    <Badge variant="default">Generated</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{test.description}</p>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="flex items-center gap-1">
                      <FileText className="h-3 w-3" />
                      {test.scenarios || 0} scenarios
                    </span>
                    <span className="flex items-center gap-1">
                      <CheckCircle className="h-3 w-3 text-green-500" />
                      Ready to run
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-3 pt-4">
              <Button onClick={handleRunTests} className="flex-1">
                <Play className="w-4 h-4 mr-2" />
                Run All Tests
              </Button>
              <Button variant="outline" onClick={() => {
                setGeneratedTests([]);
                setAgentStatus(null);
                setRealTimeUpdates([]);
                setSuccess(null);
              }}>
                Create New Tests
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CreateTestComplete;
