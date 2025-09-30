import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  Play, 
  Plus,
  Upload,
  Download,
  Edit,
  Trash2,
  Eye,
  Code,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Loader2,
  ChevronDown,
  ChevronRight,
  Settings,
  Save,
  X
} from 'lucide-react';
import directApiService from '../lib/api-direct';

const UnifiedTestManagement = () => {
  const [testSuites, setTestSuites] = useState([]);
  const [selectedSuite, setSelectedSuite] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [selectedTestCase, setSelectedTestCase] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // overview, create, requirements
  const [expandedCases, setExpandedCases] = useState(new Set());
  const [executingCases, setExecutingCases] = useState(new Set());
  const [executionStatuses, setExecutionStatuses] = useState(new Map());
  const [editingCase, setEditingCase] = useState(null);
  const [showCodeView, setShowCodeView] = useState(false);

  // New test case form state
  const [newTestCase, setNewTestCase] = useState({
    name: '',
    description: '',
    priority: 'medium',
    test_steps: [],
    expected_result: '',
    preconditions: '',
    test_data: {}
  });

  // Requirements upload state
  const [uploadingRequirements, setUploadingRequirements] = useState(false);
  const [requirementsFile, setRequirementsFile] = useState(null);

  useEffect(() => {
    loadTestSuites();
  }, []);

  useEffect(() => {
    if (selectedSuite) {
      loadTestCases(selectedSuite.id);
    }
  }, [selectedSuite]);

  // Polling for execution status updates
  useEffect(() => {
    const interval = setInterval(() => {
      executingCases.forEach(async (testCaseId) => {
        const status = executionStatuses.get(testCaseId);
        if (status && status.executionId && status.status === 'running') {
          try {
            const response = await directApiService.getExecutionStatus(status.executionId);
            if (response.status === 'success') {
              const statusData = response.data;
              
              setExecutionStatuses(prev => new Map(prev.set(testCaseId, {
                ...status,
                status: statusData.status,
                message: statusData.message,
                details: statusData.details,
                progress: statusData.progress || 0,
                currentStep: statusData.current_step,
                executionTime: statusData.execution_time,
                result: statusData.result
              })));

              if (statusData.status === 'completed' || statusData.status === 'failed') {
                setExecutingCases(prev => {
                  const newSet = new Set(prev);
                  newSet.delete(testCaseId);
                  return newSet;
                });
                
                // Update the test case with final status
                setTestCases(prev => prev.map(tc => 
                  tc.id === testCaseId 
                    ? { 
                        ...tc, 
                        status: statusData.status === 'completed' ? 'passed' : 'failed',
                        execution_result: statusData.result,
                        last_executed: new Date().toISOString()
                      }
                    : tc
                ));
              }
            }
          } catch (error) {
            console.error('Failed to poll execution status:', error);
          }
        }
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [executingCases, executionStatuses]);

  const loadTestSuites = async () => {
    try {
      setLoading(true);
      // Mock data for now - replace with actual API call
      const mockSuites = [
        {
          id: 'suite-1',
          name: 'E-commerce Authentication Tests',
          description: 'Comprehensive authentication and user management tests',
          test_type: 'functional',
          total_test_cases: 8,
          passed_test_cases: 6,
          failed_test_cases: 1,
          success_rate: 87.5,
          last_executed: '2024-01-15T10:30:00Z',
          status: 'active'
        },
        {
          id: 'suite-2',
          name: 'Product Catalog Tests',
          description: 'Product search, filtering, and display functionality',
          test_type: 'functional',
          total_test_cases: 12,
          passed_test_cases: 10,
          failed_test_cases: 2,
          success_rate: 83.3,
          last_executed: '2024-01-14T15:45:00Z',
          status: 'active'
        }
      ];
      setTestSuites(mockSuites);
      if (mockSuites.length > 0) {
        setSelectedSuite(mockSuites[0]);
      }
    } catch (err) {
      console.error('Failed to load test suites:', err);
      setError('Failed to load test suites');
    } finally {
      setLoading(false);
    }
  };

  const loadTestCases = async (suiteId) => {
    try {
      // Mock detailed test cases with actual test steps
      const mockTestCases = [
        {
          id: 'case-1',
          name: 'Valid User Login',
          description: 'Test successful login with valid credentials',
          priority: 'high',
          status: 'passed',
          test_steps: [
            {
              step: 1,
              action: 'navigate',
              description: 'Navigate to login page',
              target: '/login',
              expected: 'Login page loads successfully'
            },
            {
              step: 2,
              action: 'input',
              description: 'Enter valid username',
              target: '#username',
              value: 'testuser@example.com',
              expected: 'Username field accepts input'
            },
            {
              step: 3,
              action: 'input',
              description: 'Enter valid password',
              target: '#password',
              value: 'SecurePass123!',
              expected: 'Password field accepts input'
            },
            {
              step: 4,
              action: 'click',
              description: 'Click login button',
              target: '#login-btn',
              expected: 'Login button is clickable'
            },
            {
              step: 5,
              action: 'verify',
              description: 'Verify successful login',
              target: '.dashboard',
              expected: 'Dashboard page is displayed with user information'
            }
          ],
          expected_result: 'User should be successfully logged in and redirected to dashboard',
          preconditions: 'User account exists with valid credentials',
          test_data: {
            username: 'testuser@example.com',
            password: 'SecurePass123!'
          },
          last_executed: '2024-01-15T10:30:00Z',
          execution_time: '2.3s',
          automation_status: 'automated'
        },
        {
          id: 'case-2',
          name: 'Invalid Password Login',
          description: 'Test login failure with invalid password',
          priority: 'high',
          status: 'failed',
          test_steps: [
            {
              step: 1,
              action: 'navigate',
              description: 'Navigate to login page',
              target: '/login',
              expected: 'Login page loads successfully'
            },
            {
              step: 2,
              action: 'input',
              description: 'Enter valid username',
              target: '#username',
              value: 'testuser@example.com',
              expected: 'Username field accepts input'
            },
            {
              step: 3,
              action: 'input',
              description: 'Enter invalid password',
              target: '#password',
              value: 'WrongPassword',
              expected: 'Password field accepts input'
            },
            {
              step: 4,
              action: 'click',
              description: 'Click login button',
              target: '#login-btn',
              expected: 'Login button is clickable'
            },
            {
              step: 5,
              action: 'verify',
              description: 'Verify error message',
              target: '.error-message',
              expected: 'Error message "Invalid credentials" is displayed'
            }
          ],
          expected_result: 'Login should fail with appropriate error message',
          preconditions: 'User account exists',
          test_data: {
            username: 'testuser@example.com',
            password: 'WrongPassword'
          },
          last_executed: '2024-01-15T10:32:00Z',
          execution_time: '1.8s',
          automation_status: 'automated'
        },
        {
          id: 'case-3',
          name: 'User Registration',
          description: 'Test new user registration process',
          priority: 'medium',
          status: 'draft',
          test_steps: [
            {
              step: 1,
              action: 'navigate',
              description: 'Navigate to registration page',
              target: '/register',
              expected: 'Registration page loads successfully'
            },
            {
              step: 2,
              action: 'input',
              description: 'Enter first name',
              target: '#firstName',
              value: 'John',
              expected: 'First name field accepts input'
            },
            {
              step: 3,
              action: 'input',
              description: 'Enter last name',
              target: '#lastName',
              value: 'Doe',
              expected: 'Last name field accepts input'
            },
            {
              step: 4,
              action: 'input',
              description: 'Enter email address',
              target: '#email',
              value: 'john.doe@example.com',
              expected: 'Email field accepts valid email format'
            },
            {
              step: 5,
              action: 'input',
              description: 'Enter password',
              target: '#password',
              value: 'SecurePass123!',
              expected: 'Password meets complexity requirements'
            },
            {
              step: 6,
              action: 'input',
              description: 'Confirm password',
              target: '#confirmPassword',
              value: 'SecurePass123!',
              expected: 'Password confirmation matches'
            },
            {
              step: 7,
              action: 'click',
              description: 'Click register button',
              target: '#register-btn',
              expected: 'Registration button is clickable'
            },
            {
              step: 8,
              action: 'verify',
              description: 'Verify successful registration',
              target: '.success-message',
              expected: 'Success message and email verification notice displayed'
            }
          ],
          expected_result: 'User should be successfully registered and receive verification email',
          preconditions: 'Email address is not already registered',
          test_data: {
            firstName: 'John',
            lastName: 'Doe',
            email: 'john.doe@example.com',
            password: 'SecurePass123!'
          },
          automation_status: 'manual'
        }
      ];
      setTestCases(mockTestCases);
    } catch (err) {
      console.error('Failed to load test cases:', err);
      setError('Failed to load test cases');
    }
  };

  const executeTestCase = async (testCase) => {
    try {
      setExecutingCases(prev => new Set([...prev, testCase.id]));
      
      // For now, simulate execution - replace with actual API call
      setExecutionStatuses(prev => new Map(prev.set(testCase.id, {
        executionId: `exec_${Date.now()}`,
        status: 'running',
        message: 'Starting test execution...',
        details: 'Initializing test environment',
        progress: 0,
        startTime: new Date()
      })));

      // Update the test case status to running
      setTestCases(prev => prev.map(tc => 
        tc.id === testCase.id 
          ? { ...tc, status: 'running' }
          : tc
      ));

      // Simulate execution progress
      setTimeout(() => {
        setExecutionStatuses(prev => new Map(prev.set(testCase.id, {
          ...prev.get(testCase.id),
          progress: 50,
          message: 'Executing test steps...',
          details: 'Running automated test script'
        })));
      }, 2000);

      setTimeout(() => {
        const finalStatus = Math.random() > 0.3 ? 'completed' : 'failed';
        setExecutionStatuses(prev => new Map(prev.set(testCase.id, {
          ...prev.get(testCase.id),
          status: finalStatus,
          progress: 100,
          message: finalStatus === 'completed' ? 'Test completed successfully' : 'Test failed',
          details: finalStatus === 'completed' ? 'All test steps passed' : 'Step 3 failed: Element not found'
        })));

        setExecutingCases(prev => {
          const newSet = new Set(prev);
          newSet.delete(testCase.id);
          return newSet;
        });

        setTestCases(prev => prev.map(tc => 
          tc.id === testCase.id 
            ? { 
                ...tc, 
                status: finalStatus === 'completed' ? 'passed' : 'failed',
                last_executed: new Date().toISOString()
              }
            : tc
        ));
      }, 5000);
      
    } catch (error) {
      console.error('Failed to execute test case:', error);
      setExecutingCases(prev => {
        const newSet = new Set(prev);
        newSet.delete(testCase.id);
        return newSet;
      });
    }
  };

  const executeAllTestCases = async () => {
    const casesToExecute = testCases.filter(tc => 
      !executingCases.has(tc.id) && tc.status !== 'running'
    );
    
    for (const testCase of casesToExecute) {
      await executeTestCase(testCase);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  };

  const toggleCaseExpansion = (caseId) => {
    setExpandedCases(prev => {
      const newSet = new Set(prev);
      if (newSet.has(caseId)) {
        newSet.delete(caseId);
      } else {
        newSet.add(caseId);
      }
      return newSet;
    });
  };

  const handleRequirementsUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingRequirements(true);
    setRequirementsFile(file);

    try {
      const formData = new FormData();
      formData.append('requirements', file);
      
      // Simulate upload and processing
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Mock generated test cases from requirements
      const generatedCases = [
        {
          id: 'generated-1',
          name: 'Product Search Functionality',
          description: 'Generated from requirements: Test product search with various criteria',
          priority: 'high',
          status: 'draft',
          test_steps: [
            {
              step: 1,
              action: 'navigate',
              description: 'Navigate to product catalog page',
              target: '/products',
              expected: 'Product catalog page loads'
            },
            {
              step: 2,
              action: 'input',
              description: 'Enter search term',
              target: '#search-input',
              value: 'laptop',
              expected: 'Search input accepts text'
            },
            {
              step: 3,
              action: 'click',
              description: 'Click search button',
              target: '#search-btn',
              expected: 'Search is triggered'
            },
            {
              step: 4,
              action: 'verify',
              description: 'Verify search results',
              target: '.search-results',
              expected: 'Relevant products are displayed'
            }
          ],
          expected_result: 'Search should return relevant products matching the search criteria',
          automation_status: 'generated'
        }
      ];

      setTestCases(prev => [...prev, ...generatedCases]);
      alert(`Successfully generated ${generatedCases.length} test cases from requirements file!`);
      
    } catch (error) {
      console.error('Failed to upload requirements:', error);
      alert('Failed to process requirements file');
    } finally {
      setUploadingRequirements(false);
    }
  };

  const addNewTestStep = () => {
    setNewTestCase(prev => ({
      ...prev,
      test_steps: [
        ...prev.test_steps,
        {
          step: prev.test_steps.length + 1,
          action: 'navigate',
          description: '',
          target: '',
          expected: ''
        }
      ]
    }));
  };

  const updateTestStep = (index, field, value) => {
    setNewTestCase(prev => ({
      ...prev,
      test_steps: prev.test_steps.map((step, i) => 
        i === index ? { ...step, [field]: value } : step
      )
    }));
  };

  const removeTestStep = (index) => {
    setNewTestCase(prev => ({
      ...prev,
      test_steps: prev.test_steps.filter((_, i) => i !== index)
    }));
  };

  const saveNewTestCase = async () => {
    try {
      const testCaseToSave = {
        ...newTestCase,
        id: `case-${Date.now()}`,
        test_suite_id: selectedSuite.id,
        status: 'draft',
        automation_status: 'manual',
        created_at: new Date().toISOString()
      };

      setTestCases(prev => [...prev, testCaseToSave]);
      
      // Reset form
      setNewTestCase({
        name: '',
        description: '',
        priority: 'medium',
        test_steps: [],
        expected_result: '',
        preconditions: '',
        test_data: {}
      });

      setActiveTab('overview');
      alert('Test case created successfully!');
      
    } catch (error) {
      console.error('Failed to save test case:', error);
      alert('Failed to save test case');
    }
  };

  const getStatusIcon = (testCase) => {
    const executionStatus = executionStatuses.get(testCase.id);
    if (executionStatus) {
      switch (executionStatus.status) {
        case 'running':
          return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
        case 'completed':
          return <CheckCircle className="w-4 h-4 text-green-500" />;
        case 'failed':
          return <XCircle className="w-4 h-4 text-red-500" />;
        default:
          return <Clock className="w-4 h-4 text-yellow-500" />;
      }
    }

    switch (testCase.status) {
      case 'passed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'running':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'draft':
        return <FileText className="w-4 h-4 text-gray-500" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (testCase) => {
    const executionStatus = executionStatuses.get(testCase.id);
    if (executionStatus) {
      const variants = {
        running: 'secondary',
        completed: 'default',
        failed: 'destructive'
      };
      
      return (
        <Badge variant={variants[executionStatus.status] || 'outline'}>
          {executionStatus.status === 'running' ? 'Executing' : executionStatus.status.charAt(0).toUpperCase() + executionStatus.status.slice(1)}
        </Badge>
      );
    }

    const variants = {
      passed: 'default',
      failed: 'destructive',
      running: 'secondary',
      draft: 'outline'
    };

    return (
      <Badge variant={variants[testCase.status] || 'outline'}>
        {testCase.status || 'draft'}
      </Badge>
    );
  };

  const generateTestCode = (testCase) => {
    const code = `
# Generated Test Code for: ${testCase.name}
# Description: ${testCase.description}

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Test${testCase.name.replace(/\s+/g, '')}:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        
    def teardown_method(self):
        self.driver.quit()
        
    def test_${testCase.name.toLowerCase().replace(/\s+/g, '_')}(self):
        """${testCase.description}"""
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        
        # Preconditions: ${testCase.preconditions}
        
${testCase.test_steps.map(step => {
  switch(step.action) {
    case 'navigate':
      return `        # Step ${step.step}: ${step.description}
        driver.get("${step.target}")`;
    case 'input':
      return `        # Step ${step.step}: ${step.description}
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "${step.target}")))
        element.clear()
        element.send_keys("${step.value}")`;
    case 'click':
      return `        # Step ${step.step}: ${step.description}
        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "${step.target}")))
        element.click()`;
    case 'verify':
      return `        # Step ${step.step}: ${step.description}
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "${step.target}")))
        assert element.is_displayed(), "${step.expected}"`;
    default:
      return `        # Step ${step.step}: ${step.description}
        # TODO: Implement ${step.action} action`;
  }
}).join('\n\n')}
        
        # Expected Result: ${testCase.expected_result}
        print("Test completed successfully")
`;
    return code;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
          <p>Loading test management interface...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Test Management & Creation</h2>
          <p className="text-muted-foreground">Unified interface for managing and creating test cases</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setActiveTab('requirements')}
            className="flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            Upload Requirements
          </Button>
          <Button
            onClick={() => setActiveTab('create')}
            className="flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Create Test Case
          </Button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', label: 'Test Overview', icon: Eye },
            { id: 'create', label: 'Create Test', icon: Plus },
            { id: 'requirements', label: 'Requirements', icon: Upload }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content based on active tab */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Test Suites Sidebar */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Test Suites
                  <Badge variant="outline">{testSuites.length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {testSuites.map(suite => (
                  <div
                    key={suite.id}
                    onClick={() => setSelectedSuite(suite)}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedSuite?.id === suite.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-sm">{suite.name}</h4>
                      <Badge variant="outline" className="text-xs">
                        {suite.total_test_cases}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">
                      {suite.description}
                    </p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-green-600">
                        {suite.passed_test_cases} passed
                      </span>
                      <span className="text-red-600">
                        {suite.failed_test_cases} failed
                      </span>
                      <span className="font-medium">
                        {suite.success_rate}%
                      </span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Test Cases Main Content */}
          <div className="lg:col-span-2">
            {selectedSuite && (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>{selectedSuite.name}</CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {selectedSuite.description}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        onClick={executeAllTestCases}
                        disabled={executingCases.size > 0}
                        className="flex items-center gap-2"
                      >
                        {executingCases.size > 0 ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Running ({executingCases.size})
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4" />
                            Run All Tests
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {testCases.map(testCase => (
                      <div key={testCase.id} className="border rounded-lg">
                        {/* Test Case Header */}
                        <div className="p-4 border-b bg-gray-50">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <button
                                onClick={() => toggleCaseExpansion(testCase.id)}
                                className="text-gray-500 hover:text-gray-700"
                              >
                                {expandedCases.has(testCase.id) ? (
                                  <ChevronDown className="w-4 h-4" />
                                ) : (
                                  <ChevronRight className="w-4 h-4" />
                                )}
                              </button>
                              {getStatusIcon(testCase)}
                              <div>
                                <h4 className="font-medium">{testCase.name}</h4>
                                <p className="text-sm text-muted-foreground">
                                  {testCase.description}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {getStatusBadge(testCase)}
                              <Badge variant="outline" className="text-xs">
                                {testCase.priority}
                              </Badge>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => executeTestCase(testCase)}
                                disabled={executingCases.has(testCase.id)}
                              >
                                {executingCases.has(testCase.id) ? (
                                  <>
                                    <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                                    Running
                                  </>
                                ) : (
                                  <>
                                    <Play className="w-3 h-3 mr-1" />
                                    Run
                                  </>
                                )}
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setSelectedTestCase(testCase);
                                  setShowCodeView(true);
                                }}
                              >
                                <Code className="w-3 h-3 mr-1" />
                                Code
                              </Button>
                            </div>
                          </div>

                          {/* Execution Status */}
                          {executionStatuses.has(testCase.id) && (
                            <div className="mt-3 p-2 bg-blue-50 rounded">
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-blue-700">
                                  {executionStatuses.get(testCase.id).message}
                                </span>
                                <span className="text-blue-600">
                                  {executionStatuses.get(testCase.id).progress}%
                                </span>
                              </div>
                              <div className="w-full bg-blue-200 rounded-full h-1.5 mt-1">
                                <div 
                                  className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                                  style={{ width: `${executionStatuses.get(testCase.id).progress}%` }}
                                />
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Expanded Test Case Details */}
                        {expandedCases.has(testCase.id) && (
                          <div className="p-4 space-y-4">
                            {/* Test Information */}
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="font-medium">Expected Result:</span>
                                <p className="text-muted-foreground mt-1">
                                  {testCase.expected_result}
                                </p>
                              </div>
                              <div>
                                <span className="font-medium">Preconditions:</span>
                                <p className="text-muted-foreground mt-1">
                                  {testCase.preconditions}
                                </p>
                              </div>
                            </div>

                            {/* Test Steps */}
                            <div>
                              <h5 className="font-medium mb-3">Test Steps:</h5>
                              <div className="space-y-2">
                                {testCase.test_steps.map((step, index) => (
                                  <div key={index} className="flex gap-3 p-3 bg-gray-50 rounded">
                                    <div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-medium">
                                      {step.step}
                                    </div>
                                    <div className="flex-1">
                                      <div className="flex items-center gap-2 mb-1">
                                        <Badge variant="outline" className="text-xs">
                                          {step.action}
                                        </Badge>
                                        {step.target && (
                                          <code className="text-xs bg-gray-200 px-1 rounded">
                                            {step.target}
                                          </code>
                                        )}
                                      </div>
                                      <p className="text-sm font-medium">{step.description}</p>
                                      <p className="text-xs text-muted-foreground mt-1">
                                        Expected: {step.expected}
                                      </p>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>

                            {/* Test Data */}
                            {testCase.test_data && Object.keys(testCase.test_data).length > 0 && (
                              <div>
                                <h5 className="font-medium mb-2">Test Data:</h5>
                                <div className="bg-gray-50 p-3 rounded">
                                  <pre className="text-xs">
                                    {JSON.stringify(testCase.test_data, null, 2)}
                                  </pre>
                                </div>
                              </div>
                            )}

                            {/* Execution History */}
                            {testCase.last_executed && (
                              <div className="text-sm text-muted-foreground">
                                Last executed: {new Date(testCase.last_executed).toLocaleString()}
                                {testCase.execution_time && ` (${testCase.execution_time})`}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Create Test Case Tab */}
      {activeTab === 'create' && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Test Case</CardTitle>
            <p className="text-sm text-muted-foreground">
              Create a detailed test case with step-by-step instructions
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Test Case Name</label>
                <input
                  type="text"
                  value={newTestCase.name}
                  onChange={(e) => setNewTestCase(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full p-2 border rounded-md"
                  placeholder="Enter test case name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Priority</label>
                <select
                  value={newTestCase.priority}
                  onChange={(e) => setNewTestCase(prev => ({ ...prev, priority: e.target.value }))}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                value={newTestCase.description}
                onChange={(e) => setNewTestCase(prev => ({ ...prev, description: e.target.value }))}
                className="w-full p-2 border rounded-md"
                rows={3}
                placeholder="Describe what this test case validates"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Preconditions</label>
              <textarea
                value={newTestCase.preconditions}
                onChange={(e) => setNewTestCase(prev => ({ ...prev, preconditions: e.target.value }))}
                className="w-full p-2 border rounded-md"
                rows={2}
                placeholder="What conditions must be met before running this test"
              />
            </div>

            {/* Test Steps */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium">Test Steps</label>
                <Button onClick={addNewTestStep} size="sm" variant="outline">
                  <Plus className="w-4 h-4 mr-1" />
                  Add Step
                </Button>
              </div>
              
              <div className="space-y-3">
                {newTestCase.test_steps.map((step, index) => (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-medium">Step {step.step}</span>
                      <Button
                        onClick={() => removeTestStep(index)}
                        size="sm"
                        variant="ghost"
                        className="text-red-500 hover:text-red-700"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3 mb-3">
                      <div>
                        <label className="block text-xs font-medium mb-1">Action Type</label>
                        <select
                          value={step.action}
                          onChange={(e) => updateTestStep(index, 'action', e.target.value)}
                          className="w-full p-2 border rounded text-sm"
                        >
                          <option value="navigate">Navigate</option>
                          <option value="input">Input</option>
                          <option value="click">Click</option>
                          <option value="verify">Verify</option>
                          <option value="wait">Wait</option>
                          <option value="scroll">Scroll</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium mb-1">Target Element</label>
                        <input
                          type="text"
                          value={step.target}
                          onChange={(e) => updateTestStep(index, 'target', e.target.value)}
                          className="w-full p-2 border rounded text-sm"
                          placeholder="CSS selector or URL"
                        />
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <label className="block text-xs font-medium mb-1">Description</label>
                      <input
                        type="text"
                        value={step.description}
                        onChange={(e) => updateTestStep(index, 'description', e.target.value)}
                        className="w-full p-2 border rounded text-sm"
                        placeholder="Describe what this step does"
                      />
                    </div>
                    
                    {step.action === 'input' && (
                      <div className="mb-3">
                        <label className="block text-xs font-medium mb-1">Input Value</label>
                        <input
                          type="text"
                          value={step.value || ''}
                          onChange={(e) => updateTestStep(index, 'value', e.target.value)}
                          className="w-full p-2 border rounded text-sm"
                          placeholder="Value to input"
                        />
                      </div>
                    )}
                    
                    <div>
                      <label className="block text-xs font-medium mb-1">Expected Result</label>
                      <input
                        type="text"
                        value={step.expected}
                        onChange={(e) => updateTestStep(index, 'expected', e.target.value)}
                        className="w-full p-2 border rounded text-sm"
                        placeholder="What should happen after this step"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Expected Result</label>
              <textarea
                value={newTestCase.expected_result}
                onChange={(e) => setNewTestCase(prev => ({ ...prev, expected_result: e.target.value }))}
                className="w-full p-2 border rounded-md"
                rows={3}
                placeholder="Overall expected outcome of the test"
              />
            </div>

            <div className="flex items-center gap-3">
              <Button onClick={saveNewTestCase} className="flex items-center gap-2">
                <Save className="w-4 h-4" />
                Save Test Case
              </Button>
              <Button
                variant="outline"
                onClick={() => setActiveTab('overview')}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Requirements Upload Tab */}
      {activeTab === 'requirements' && (
        <Card>
          <CardHeader>
            <CardTitle>Upload Requirements</CardTitle>
            <p className="text-sm text-muted-foreground">
              Upload a requirements JSON file to automatically generate test cases
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <div className="space-y-2">
                <p className="text-lg font-medium">Upload Requirements File</p>
                <p className="text-sm text-muted-foreground">
                  Supports JSON format with test requirements and specifications
                </p>
                <div className="flex items-center justify-center">
                  <label className="cursor-pointer">
                    <input
                      type="file"
                      accept=".json"
                      onChange={handleRequirementsUpload}
                      className="hidden"
                      disabled={uploadingRequirements}
                    />
                    <Button
                      variant="outline"
                      disabled={uploadingRequirements}
                      className="flex items-center gap-2"
                    >
                      {uploadingRequirements ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4" />
                          Choose File
                        </>
                      )}
                    </Button>
                  </label>
                </div>
              </div>
            </div>

            {requirementsFile && (
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-blue-900">{requirementsFile.name}</p>
                    <p className="text-sm text-blue-700">
                      {(requirementsFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-4">
              <h4 className="font-medium">Sample Requirements Format:</h4>
              <div className="bg-gray-50 p-4 rounded-lg">
                <pre className="text-xs overflow-x-auto">
{`{
  "testSuiteName": "E-commerce Platform Tests",
  "description": "Comprehensive test coverage for e-commerce platform",
  "testCategories": [
    {
      "category": "Authentication",
      "priority": "high",
      "tests": [
        {
          "name": "User Login",
          "description": "Test user login functionality",
          "steps": [
            "Navigate to login page",
            "Enter valid credentials",
            "Verify successful login"
          ]
        }
      ]
    }
  ]
}`}
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Code View Modal */}
      {showCodeView && selectedTestCase && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">Generated Test Code</h3>
              <Button
                variant="ghost"
                onClick={() => setShowCodeView(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
              <pre className="text-sm">
                {generateTestCode(selectedTestCase)}
              </pre>
            </div>
            <div className="flex items-center gap-2 mt-4">
              <Button
                onClick={() => {
                  navigator.clipboard.writeText(generateTestCode(selectedTestCase));
                  alert('Code copied to clipboard!');
                }}
              >
                Copy Code
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  const blob = new Blob([generateTestCode(selectedTestCase)], { type: 'text/plain' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `test_${selectedTestCase.name.toLowerCase().replace(/\s+/g, '_')}.py`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
              >
                <Download className="w-4 h-4 mr-1" />
                Download
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedTestManagement;
