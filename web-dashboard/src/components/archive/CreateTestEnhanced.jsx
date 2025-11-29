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
  Pause
} from 'lucide-react';
import { apiService } from '../lib/api';

const CreateTestEnhanced = ({ user, onNavigate }) => {
  const [applications, setApplications] = useState([]);
  const [selectedApp, setSelectedApp] = useState('');
  const [testDescription, setTestDescription] = useState('');
  const [testType, setTestType] = useState('');
  const [priority, setPriority] = useState('medium');
  const [isCreating, setIsCreating] = useState(false);
  const [currentJobId, setCurrentJobId] = useState(null);
  const [agentStatus, setAgentStatus] = useState(null);
  const [generatedTests, setGeneratedTests] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState(null);
  const [duplicateTests, setDuplicateTests] = useState([]);
  const [showDuplicateWarning, setShowDuplicateWarning] = useState(false);
  const [existingTests, setExistingTests] = useState([]);
  
  // Real-time monitoring
  const pollingInterval = useRef(null);
  const [realTimeUpdates, setRealTimeUpdates] = useState([]);

  const agentPhases = [
    { name: 'Discovery Agent', description: 'Analyzing application structure and user flows', icon: Eye },
    { name: 'Generation Agent', description: 'Creating comprehensive test scenarios', icon: Brain },
    { name: 'Code Agent', description: 'Generating automated test code', icon: FileText },
    { name: 'Validation Agent', description: 'Validating and optimizing test suite', icon: CheckCircle }
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
    loadExistingTests();
    
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, []);

  useEffect(() => {
    if (selectedApp && testDescription) {
      checkForDuplicates();
    }
  }, [selectedApp, testDescription]);

  const loadApplications = async () => {
    try {
      // Load real applications from API
      const response = await apiService.request('/api/v1/applications');
      if (response.status === 'success') {
        setApplications(response.data);
      }
    } catch (error) {
      console.error('Failed to load applications:', error);
      // Fallback to mock data
      setApplications([
        { id: 1, name: 'E-commerce Store', url: 'https://mystore.example.com', type: 'ecommerce' },
        { id: 2, name: 'Admin Dashboard', url: 'https://admin.mystore.example.com', type: 'admin' }
      ]);
    }
  };

  const loadExistingTests = async () => {
    try {
      const response = await apiService.request('/api/v1/tests');
      if (response.status === 'success') {
        setExistingTests(response.data);
      }
    } catch (error) {
      console.error('Failed to load existing tests:', error);
    }
  };

  const loadSuggestions = () => {
    setSuggestions([
      'Test the complete checkout process from cart to payment confirmation',
      'Verify user registration with email verification workflow',
      'Test product search and filtering functionality',
      'Validate form error handling and validation messages',
      'Test user login with different credential scenarios',
      'Verify responsive design on mobile and tablet devices'
    ]);
  };

  const checkForDuplicates = async () => {
    if (!selectedApp || !testDescription) return;

    // Check for similar existing tests
    const similar = existingTests.filter(test => {
      const selectedAppData = applications.find(app => app.id.toString() === selectedApp);
      return test.application_name === selectedAppData?.name &&
             (test.description?.toLowerCase().includes(testDescription.toLowerCase().split(' ')[0]) ||
              testDescription.toLowerCase().includes(test.name?.toLowerCase()));
    });

    if (similar.length > 0) {
      setDuplicateTests(similar);
      setShowDuplicateWarning(true);
    } else {
      setDuplicateTests([]);
      setShowDuplicateWarning(false);
    }
  };

  const startRealTimeMonitoring = (jobId) => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
    }

    pollingInterval.current = setInterval(async () => {
      try {
        const response = await apiService.request(`/api/v1/agent-job/${jobId}`);
        if (response.status === 'success') {
          setAgentStatus(response.data);
          
          // Add real-time update
          const timestamp = new Date().toLocaleTimeString();
          const currentAgent = response.data.job.current_agent;
          const progress = response.data.job.progress_percentage;
          
          setRealTimeUpdates(prev => [
            ...prev.slice(-4), // Keep only last 5 updates
            {
              timestamp,
              agent: currentAgent,
              progress,
              status: response.data.job.status,
              message: `${currentAgent} - ${progress}% complete`
            }
          ]);

          // Check if job is completed
          if (response.data.job.status === 'completed') {
            clearInterval(pollingInterval.current);
            setIsCreating(false);
            loadGeneratedTests(response.data.job.test_suite_id);
          } else if (response.data.job.status === 'failed') {
            clearInterval(pollingInterval.current);
            setIsCreating(false);
            setError('Test creation failed. Please try again.');
          }
        }
      } catch (error) {
        console.error('Failed to get agent status:', error);
      }
    }, 2000); // Poll every 2 seconds
  };

  const loadGeneratedTests = async (testSuiteId) => {
    try {
      const response = await apiService.request(`/api/v1/test-suite/${testSuiteId}/tests`);
      if (response.status === 'success') {
        setGeneratedTests(response.data);
      }
    } catch (error) {
      console.error('Failed to load generated tests:', error);
    }
  };

  const handleGenerateTests = async () => {
    if (!selectedApp || !testDescription) return;

    setError(null);
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

      const response = await apiService.request('/api/v1/create-test', {
        method: 'POST',
        body: testRequest
      });

      if (response.status === 'success') {
        setCurrentJobId(response.data.job_id);
        startRealTimeMonitoring(response.data.job_id);
        
        // Add initial update
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
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setTestDescription(suggestion);
  };

  const handleRunTests = async () => {
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Create AI-Powered Tests</h1>
        <p className="text-muted-foreground">
          Describe what you want to test in plain English, and our AI agents will create comprehensive test suites
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Duplicate Warning */}
      {showDuplicateWarning && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Found {duplicateTests.length} similar test(s) for this application. Consider updating existing tests instead of creating duplicates.
            <div className="mt-2 space-y-1">
              {duplicateTests.map((test, index) => (
                <div key={index} className="text-sm font-medium">
                  • {test.name}
                </div>
              ))}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {!isCreating && generatedTests.length === 0 && (
        <>
          {/* Test Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Test Configuration
              </CardTitle>
              <CardDescription>
                Configure your test requirements with intelligent duplicate detection
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
                <Label htmlFor="description">What would you like to test?</Label>
                <Textarea
                  id="description"
                  value={testDescription}
                  onChange={(e) => setTestDescription(e.target.value)}
                  placeholder="Describe what you want to test in plain English. For example: 'Test the complete user registration process including email verification and welcome email'"
                  rows={4}
                />
              </div>

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
                <div className="text-sm text-muted-foreground">Test Suites</div>
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

export default CreateTestEnhanced;
