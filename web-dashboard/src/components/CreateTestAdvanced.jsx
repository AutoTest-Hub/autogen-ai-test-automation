import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { 
  FileText, 
  Globe, 
  Upload, 
  Bot, 
  Sparkles, 
  Target, 
  CheckCircle, 
  Clock, 
  ArrowRight,
  Eye,
  Brain,
  Zap,
  Search,
  Code,
  Shield,
  Play,
  AlertCircle
} from 'lucide-react';
import { apiService } from '../lib/api';

const CreateTestAdvanced = ({ user, onNavigate }) => {
  const [activeTab, setActiveTab] = useState('requirements');
  const [applications, setApplications] = useState([]);
  const [selectedApp, setSelectedApp] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(null);
  const [agentProgress, setAgentProgress] = useState(0);
  const [agentLogs, setAgentLogs] = useState([]);
  const [generatedTests, setGeneratedTests] = useState([]);

  // Form states for different creation modes
  const [requirementsForm, setRequirementsForm] = useState({
    requirements: '',
    priority: 'medium',
    coverage: 'comprehensive'
  });

  const [testCasesForm, setTestCasesForm] = useState({
    testCases: '',
    format: 'gherkin',
    includeNegative: true
  });

  const [urlForm, setUrlForm] = useState({
    url: '',
    appType: '',
    keyFeatures: '',
    userFlows: ''
  });

  const agents = [
    {
      id: 'discovery',
      name: 'Discovery Agent',
      description: 'Analyzing application structure and user flows',
      icon: Search,
      color: 'text-blue-500'
    },
    {
      id: 'requirements',
      name: 'Requirements Agent',
      description: 'Processing business requirements and acceptance criteria',
      icon: FileText,
      color: 'text-green-500'
    },
    {
      id: 'test_generation',
      name: 'Test Generation Agent',
      description: 'Creating comprehensive test scenarios and edge cases',
      icon: Brain,
      color: 'text-purple-500'
    },
    {
      id: 'code_generation',
      name: 'Code Generation Agent',
      description: 'Writing robust automation code with best practices',
      icon: Code,
      color: 'text-orange-500'
    },
    {
      id: 'validation',
      name: 'Validation Agent',
      description: 'Reviewing and optimizing test quality and coverage',
      icon: Shield,
      color: 'text-red-500'
    }
  ];

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = async () => {
    // Simulate loading user's applications
    setApplications([
      { id: 1, name: 'E-commerce Store', url: 'https://mystore.example.com', type: 'ecommerce' },
      { id: 2, name: 'Admin Dashboard', url: 'https://admin.mystore.example.com', type: 'admin' },
      { id: 3, name: 'Customer Portal', url: 'https://portal.mystore.example.com', type: 'portal' }
    ]);
  };

  const simulateAgentWork = async () => {
    setIsGenerating(true);
    setAgentProgress(0);
    setAgentLogs([]);

    for (let i = 0; i < agents.length; i++) {
      const agent = agents[i];
      setCurrentAgent(agent);
      
      // Add agent start log
      setAgentLogs(prev => [...prev, {
        id: Date.now() + i,
        agent: agent.name,
        message: `${agent.name} started: ${agent.description}`,
        timestamp: new Date().toLocaleTimeString(),
        type: 'start'
      }]);

      // Simulate agent work with progress
      for (let progress = 0; progress <= 100; progress += 10) {
        setAgentProgress(progress);
        await new Promise(resolve => setTimeout(resolve, 200));
      }

      // Add agent completion log
      setAgentLogs(prev => [...prev, {
        id: Date.now() + i + 1000,
        agent: agent.name,
        message: `${agent.name} completed successfully`,
        timestamp: new Date().toLocaleTimeString(),
        type: 'complete'
      }]);

      // Add some intermediate logs for realism
      if (i === 0) { // Discovery Agent
        setAgentLogs(prev => [...prev, {
          id: Date.now() + i + 2000,
          agent: agent.name,
          message: 'Found 15 interactive elements, 8 forms, 3 user workflows',
          timestamp: new Date().toLocaleTimeString(),
          type: 'info'
        }]);
      } else if (i === 2) { // Test Generation Agent
        setAgentLogs(prev => [...prev, {
          id: Date.now() + i + 2000,
          agent: agent.name,
          message: 'Generated 24 test scenarios covering happy path and edge cases',
          timestamp: new Date().toLocaleTimeString(),
          type: 'info'
        }]);
      }

      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // Generate final test results
    setGeneratedTests([
      {
        id: 1,
        name: 'User Authentication Suite',
        scenarios: 12,
        coverage: 'High',
        type: 'Functional',
        estimatedTime: '5 minutes'
      },
      {
        id: 2,
        name: 'E-commerce Checkout Flow',
        scenarios: 18,
        coverage: 'High',
        type: 'Integration',
        estimatedTime: '8 minutes'
      },
      {
        id: 3,
        name: 'Form Validation Tests',
        scenarios: 15,
        coverage: 'Medium',
        type: 'UI/UX',
        estimatedTime: '4 minutes'
      }
    ]);

    setCurrentAgent(null);
    setIsGenerating(false);
  };

  const handleCreateTests = async () => {
    if (!selectedApp) {
      alert('Please select an application first');
      return;
    }

    await simulateAgentWork();
  };

  const getLogIcon = (type) => {
    switch (type) {
      case 'start': return <Play className="h-3 w-3 text-blue-500" />;
      case 'complete': return <CheckCircle className="h-3 w-3 text-green-500" />;
      case 'info': return <Eye className="h-3 w-3 text-purple-500" />;
      case 'error': return <AlertCircle className="h-3 w-3 text-red-500" />;
      default: return <Clock className="h-3 w-3 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Create AI-Powered Tests</h1>
        <p className="text-muted-foreground">
          Multiple ways to create comprehensive test automation for your applications
        </p>
      </div>

      {/* Application Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Select Application
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Select value={selectedApp} onValueChange={setSelectedApp}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Choose the application you want to test" />
            </SelectTrigger>
            <SelectContent>
              {applications.map((app) => (
                <SelectItem key={app.id} value={app.id.toString()}>
                  <div className="flex items-center gap-2">
                    <span>{app.name}</span>
                    <Badge variant="secondary">{app.type}</Badge>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Test Creation Methods */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Choose Test Creation Method
          </CardTitle>
          <CardDescription>
            Select the approach that best fits your workflow and available documentation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="requirements" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Requirements
              </TabsTrigger>
              <TabsTrigger value="testcases" className="flex items-center gap-2">
                <Target className="h-4 w-4" />
                Test Cases
              </TabsTrigger>
              <TabsTrigger value="url" className="flex items-center gap-2">
                <Globe className="h-4 w-4" />
                URL + Metadata
              </TabsTrigger>
            </TabsList>

            <TabsContent value="requirements" className="space-y-4">
              <div className="border rounded-lg p-4 bg-blue-50">
                <h3 className="font-semibold mb-2">Requirements-Based Test Creation</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Provide business requirements, user stories, or acceptance criteria. AI will analyze and create comprehensive test scenarios.
                </p>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="requirements">Business Requirements / User Stories</Label>
                  <Textarea
                    id="requirements"
                    value={requirementsForm.requirements}
                    onChange={(e) => setRequirementsForm({...requirementsForm, requirements: e.target.value})}
                    placeholder="Enter your requirements, user stories, or acceptance criteria. For example:

As a customer, I want to be able to register for an account so that I can make purchases.
- User should be able to enter email, password, and confirm password
- System should validate email format and password strength
- User should receive confirmation email after successful registration
- User should be redirected to dashboard after email verification"
                    rows={8}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="priority">Test Priority</Label>
                    <Select value={requirementsForm.priority} onValueChange={(value) => setRequirementsForm({...requirementsForm, priority: value})}>
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
                  
                  <div>
                    <Label htmlFor="coverage">Test Coverage</Label>
                    <Select value={requirementsForm.coverage} onValueChange={(value) => setRequirementsForm({...requirementsForm, coverage: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="basic">Basic Coverage</SelectItem>
                        <SelectItem value="comprehensive">Comprehensive</SelectItem>
                        <SelectItem value="exhaustive">Exhaustive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="testcases" className="space-y-4">
              <div className="border rounded-lg p-4 bg-green-50">
                <h3 className="font-semibold mb-2">Test Case-Based Creation</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Import existing manual test cases with steps and expected results. AI will convert them to automated tests.
                </p>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="testcases">Manual Test Cases</Label>
                  <Textarea
                    id="testcases"
                    value={testCasesForm.testCases}
                    onChange={(e) => setTestCasesForm({...testCasesForm, testCases: e.target.value})}
                    placeholder="Enter your test cases in any format (Gherkin, step-by-step, etc.):

Test Case: User Login
1. Navigate to login page
2. Enter valid email address
3. Enter valid password
4. Click login button
Expected Result: User is redirected to dashboard

Test Case: Invalid Login
1. Navigate to login page
2. Enter invalid email
3. Enter any password
4. Click login button
Expected Result: Error message displayed"
                    rows={8}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="format">Test Case Format</Label>
                    <Select value={testCasesForm.format} onValueChange={(value) => setTestCasesForm({...testCasesForm, format: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="gherkin">Gherkin (Given/When/Then)</SelectItem>
                        <SelectItem value="steps">Step-by-Step</SelectItem>
                        <SelectItem value="mixed">Mixed Format</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="flex items-center space-x-2 pt-6">
                    <input
                      type="checkbox"
                      id="includeNegative"
                      checked={testCasesForm.includeNegative}
                      onChange={(e) => setTestCasesForm({...testCasesForm, includeNegative: e.target.checked})}
                    />
                    <Label htmlFor="includeNegative">Include negative test cases</Label>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="url" className="space-y-4">
              <div className="border rounded-lg p-4 bg-purple-50">
                <h3 className="font-semibold mb-2">URL + Metadata Creation</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Provide just the URL and basic information. AI will discover the application and create comprehensive tests.
                </p>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="url">Application URL</Label>
                  <Input
                    id="url"
                    value={urlForm.url}
                    onChange={(e) => setUrlForm({...urlForm, url: e.target.value})}
                    placeholder="https://myapp.example.com"
                  />
                </div>
                
                <div>
                  <Label htmlFor="appType">Application Type</Label>
                  <Select value={urlForm.appType} onValueChange={(value) => setUrlForm({...urlForm, appType: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select application type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ecommerce">E-commerce</SelectItem>
                      <SelectItem value="admin">Admin Panel</SelectItem>
                      <SelectItem value="banking">Banking</SelectItem>
                      <SelectItem value="healthcare">Healthcare</SelectItem>
                      <SelectItem value="education">Education</SelectItem>
                      <SelectItem value="saas">SaaS Platform</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="keyFeatures">Key Features (Optional)</Label>
                  <Textarea
                    id="keyFeatures"
                    value={urlForm.keyFeatures}
                    onChange={(e) => setUrlForm({...urlForm, keyFeatures: e.target.value})}
                    placeholder="List the main features of your application (e.g., user registration, product catalog, shopping cart, payment processing)"
                    rows={3}
                  />
                </div>
                
                <div>
                  <Label htmlFor="userFlows">Important User Flows (Optional)</Label>
                  <Textarea
                    id="userFlows"
                    value={urlForm.userFlows}
                    onChange={(e) => setUrlForm({...urlForm, userFlows: e.target.value})}
                    placeholder="Describe critical user journeys (e.g., new user registration → email verification → first purchase)"
                    rows={3}
                  />
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <div className="pt-6">
            <Button 
              onClick={handleCreateTests} 
              disabled={!selectedApp || isGenerating}
              className="w-full"
              size="lg"
            >
              {isGenerating ? (
                <>
                  <Bot className="w-4 h-4 mr-2 animate-pulse" />
                  AI Agents Working...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Create AI-Powered Tests
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Agent Activity Monitor */}
      {isGenerating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5 animate-pulse" />
              AI Agents at Work
            </CardTitle>
            <CardDescription>
              Watch our AI agents analyze your application and create comprehensive tests
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Current Agent */}
            {currentAgent && (
              <div className="border rounded-lg p-4 bg-blue-50">
                <div className="flex items-center gap-3 mb-3">
                  <currentAgent.icon className={`h-6 w-6 ${currentAgent.color}`} />
                  <div>
                    <h3 className="font-semibold">{currentAgent.name}</h3>
                    <p className="text-sm text-muted-foreground">{currentAgent.description}</p>
                  </div>
                </div>
                <Progress value={agentProgress} className="h-2" />
                <p className="text-xs text-muted-foreground mt-2">{agentProgress}% complete</p>
              </div>
            )}

            {/* Agent Progress Overview */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {agents.map((agent, index) => {
                const isCompleted = agentLogs.some(log => log.agent === agent.name && log.type === 'complete');
                const isActive = currentAgent?.id === agent.id;
                
                return (
                  <div
                    key={agent.id}
                    className={`border rounded-lg p-3 text-center ${
                      isCompleted ? 'bg-green-50 border-green-200' :
                      isActive ? 'bg-blue-50 border-blue-200' :
                      'bg-gray-50'
                    }`}
                  >
                    <agent.icon className={`h-5 w-5 mx-auto mb-2 ${
                      isCompleted ? 'text-green-500' :
                      isActive ? agent.color :
                      'text-gray-400'
                    }`} />
                    <p className="text-xs font-medium">{agent.name}</p>
                    {isCompleted && <CheckCircle className="h-3 w-3 text-green-500 mx-auto mt-1" />}
                    {isActive && <div className="w-3 h-3 bg-blue-500 rounded-full mx-auto mt-1 animate-pulse" />}
                  </div>
                );
              })}
            </div>

            {/* Agent Logs */}
            <div className="border rounded-lg p-4 bg-gray-50 max-h-60 overflow-y-auto">
              <h4 className="font-semibold mb-3">Agent Activity Log</h4>
              <div className="space-y-2">
                {agentLogs.map((log) => (
                  <div key={log.id} className="flex items-start gap-2 text-sm">
                    {getLogIcon(log.type)}
                    <div className="flex-1">
                      <span className="font-medium">{log.agent}:</span> {log.message}
                      <span className="text-xs text-muted-foreground ml-2">{log.timestamp}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generated Tests Results */}
      {generatedTests.length > 0 && !isGenerating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              AI-Generated Test Suite Ready!
            </CardTitle>
            <CardDescription>
              Your comprehensive test suite has been created. Review and execute the tests below.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{generatedTests.length}</div>
                <div className="text-sm text-muted-foreground">Test Suites</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {generatedTests.reduce((sum, test) => sum + test.scenarios, 0)}
                </div>
                <div className="text-sm text-muted-foreground">Test Scenarios</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">~17 min</div>
                <div className="text-sm text-muted-foreground">Estimated Runtime</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">High</div>
                <div className="text-sm text-muted-foreground">Coverage Level</div>
              </div>
            </div>

            <div className="space-y-3">
              {generatedTests.map((test) => (
                <div key={test.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">{test.name}</h3>
                    <div className="flex gap-2">
                      <Badge variant={test.coverage === 'High' ? 'default' : 'secondary'}>
                        {test.coverage} Coverage
                      </Badge>
                      <Badge variant="outline">{test.type}</Badge>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Target className="h-3 w-3" />
                      {test.scenarios} scenarios
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {test.estimatedTime}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-3 pt-4">
              <Button onClick={() => onNavigate('results')} className="flex-1">
                <Play className="w-4 h-4 mr-2" />
                Execute All Tests
              </Button>
              <Button variant="outline" onClick={() => setGeneratedTests([])}>
                Create New Tests
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CreateTestAdvanced;
