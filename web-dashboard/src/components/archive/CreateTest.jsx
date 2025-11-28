import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Progress } from './ui/progress';
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
  Brain
} from 'lucide-react';
import { apiService } from '../lib/api';

const CreateTest = ({ user, onNavigate }) => {
  const [applications, setApplications] = useState([]);
  const [selectedApp, setSelectedApp] = useState('');
  const [testDescription, setTestDescription] = useState('');
  const [testType, setTestType] = useState('');
  const [priority, setPriority] = useState('medium');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStep, setGenerationStep] = useState(0);
  const [generatedTests, setGeneratedTests] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

  const generationSteps = [
    'Analyzing your application...',
    'Understanding user flows...',
    'Generating test scenarios...',
    'Creating test automation code...',
    'Optimizing test coverage...',
    'Finalizing test suite...'
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
  }, []);

  const loadApplications = async () => {
    // Simulate loading user's applications
    setApplications([
      { id: 1, name: 'E-commerce Store', url: 'https://mystore.example.com', type: 'ecommerce' },
      { id: 2, name: 'Admin Dashboard', url: 'https://admin.mystore.example.com', type: 'admin' }
    ]);
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

  const handleGenerateTests = async () => {
    if (!selectedApp || !testDescription) return;

    setIsGenerating(true);
    setGenerationStep(0);

    // Simulate AI test generation process
    for (let i = 0; i < generationSteps.length; i++) {
      setGenerationStep(i);
      await new Promise(resolve => setTimeout(resolve, 1500));
    }

    // Simulate generated test results
    setGeneratedTests([
      {
        id: 1,
        name: 'User Registration Flow',
        description: 'Tests complete user registration process including email verification',
        scenarios: 5,
        estimatedTime: '3 minutes',
        coverage: 'High'
      },
      {
        id: 2,
        name: 'Login Authentication',
        description: 'Validates login with various credential combinations and error handling',
        scenarios: 8,
        estimatedTime: '2 minutes',
        coverage: 'High'
      },
      {
        id: 3,
        name: 'Form Validation',
        description: 'Tests all form fields for proper validation and error messages',
        scenarios: 12,
        estimatedTime: '4 minutes',
        coverage: 'Medium'
      }
    ]);

    setIsGenerating(false);
  };

  const handleSuggestionClick = (suggestion) => {
    setTestDescription(suggestion);
  };

  const handleRunTests = async () => {
    // Navigate to test execution or results
    onNavigate('test-results');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Create AI-Powered Tests</h1>
        <p className="text-muted-foreground">
          Describe what you want to test in plain English, and our AI will create comprehensive test suites
        </p>
      </div>

      {!isGenerating && generatedTests.length === 0 && (
        <>
          {/* Test Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Test Configuration
              </CardTitle>
              <CardDescription>
                Tell our AI what you want to test
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
                          {app.name}
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
                disabled={!selectedApp || !testDescription}
                className="w-full"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Generate AI-Powered Tests
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

      {/* AI Generation Progress */}
      {isGenerating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5 animate-pulse" />
              AI is Creating Your Tests
            </CardTitle>
            <CardDescription>
              Our AI agents are analyzing your application and generating comprehensive tests
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>{generationSteps[generationStep]}</span>
                <span>{Math.round(((generationStep + 1) / generationSteps.length) * 100)}%</span>
              </div>
              <Progress value={((generationStep + 1) / generationSteps.length) * 100} />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              {generationSteps.slice(0, generationStep + 1).map((step, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-muted-foreground">{step}</span>
                </div>
              ))}
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
              AI-Generated Test Suite
            </CardTitle>
            <CardDescription>
              Your comprehensive test suite is ready! Review and run the tests below.
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
                  {generatedTests.reduce((sum, test) => sum + test.scenarios, 0)}
                </div>
                <div className="text-sm text-muted-foreground">Test Scenarios</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">~9 min</div>
                <div className="text-sm text-muted-foreground">Estimated Runtime</div>
              </div>
            </div>

            <div className="space-y-3">
              {generatedTests.map((test) => (
                <div key={test.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">{test.name}</h3>
                    <Badge variant={test.coverage === 'High' ? 'default' : 'secondary'}>
                      {test.coverage} Coverage
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{test.description}</p>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="flex items-center gap-1">
                      <FileText className="h-3 w-3" />
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
              <Button onClick={handleRunTests} className="flex-1">
                <Play className="w-4 h-4 mr-2" />
                Run All Tests
              </Button>
              <Button variant="outline" onClick={() => setGeneratedTests([])}>
                Generate New Tests
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CreateTest;
