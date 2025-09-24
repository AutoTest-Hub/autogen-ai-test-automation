import React, { useState, useEffect } from 'react';
import { 
  Play, 
  FileText, 
  TestTube, 
  Globe, 
  Zap, 
  Settings, 
  CheckCircle, 
  AlertCircle,
  Clock,
  Bot,
  Eye,
  Sparkles
} from 'lucide-react';
import AgentActivityMonitor from './AgentActivityMonitor';

const CreateTestRealTime = ({ user, onNavigate }) => {
  const [activeTab, setActiveTab] = useState('requirements');
  const [isCreating, setIsCreating] = useState(false);
  const [currentTask, setCurrentTask] = useState(null);
  const [showAgentMonitor, setShowAgentMonitor] = useState(false);
  const [taskResult, setTaskResult] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);
  
  // Form states for different creation types
  const [requirementsForm, setRequirementsForm] = useState({
    applicationUrl: '',
    applicationName: '',
    applicationType: 'web_application',
    requirementsText: '',
    priority: 'normal',
    generatePerformanceTests: false,
    generateCrossBrowserTests: false
  });

  const [testCasesForm, setTestCasesForm] = useState({
    applicationUrl: '',
    applicationName: '',
    applicationType: 'web_application',
    testCases: [
      {
        id: 1,
        title: '',
        description: '',
        steps: [''],
        expectedResult: ''
      }
    ],
    priority: 'normal',
    generatePerformanceTests: false,
    generateCrossBrowserTests: false
  });

  const [urlMetadataForm, setUrlMetadataForm] = useState({
    applicationUrl: '',
    applicationName: '',
    applicationType: 'web_application',
    keyFeatures: [''],
    userFlows: [''],
    priority: 'normal',
    generatePerformanceTests: false,
    generateCrossBrowserTests: false
  });

  // Application types
  const applicationTypes = [
    { value: 'web_application', label: 'Web Application', icon: '🌐' },
    { value: 'ecommerce', label: 'E-commerce', icon: '🛒' },
    { value: 'banking', label: 'Banking/Finance', icon: '🏦' },
    { value: 'healthcare', label: 'Healthcare', icon: '🏥' },
    { value: 'education', label: 'Education', icon: '🎓' },
    { value: 'social_media', label: 'Social Media', icon: '📱' },
    { value: 'crm', label: 'CRM', icon: '👥' },
    { value: 'hrms', label: 'HRMS', icon: '👨‍💼' },
    { value: 'other', label: 'Other', icon: '⚙️' }
  ];

  // Priority levels
  const priorityLevels = [
    { value: 'low', label: 'Low Priority', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'normal', label: 'Normal Priority', color: 'text-blue-600', bgColor: 'bg-blue-100' },
    { value: 'high', label: 'High Priority', color: 'text-orange-600', bgColor: 'bg-orange-100' },
    { value: 'urgent', label: 'Urgent', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Quick start templates
  const quickStartTemplates = [
    {
      name: 'E-commerce Demo',
      url: 'https://demo.automationexercise.com',
      type: 'ecommerce',
      description: 'Complete e-commerce testing with cart, checkout, and user management',
      features: ['Product browsing', 'Shopping cart', 'User registration', 'Checkout process', 'Payment flow'],
      flows: ['Browse products', 'Add to cart', 'Complete purchase', 'User account management']
    },
    {
      name: 'Banking Demo',
      url: 'https://demo.testfire.net',
      type: 'banking',
      description: 'Comprehensive banking application testing with security focus',
      features: ['Account login', 'Balance inquiry', 'Fund transfer', 'Transaction history', 'Security features'],
      flows: ['User authentication', 'Account operations', 'Money transfer', 'Statement generation']
    },
    {
      name: 'HRMS Demo',
      url: 'https://opensource-demo.orangehrmlive.com',
      type: 'hrms',
      description: 'Employee management system with full workflow testing',
      features: ['Employee management', 'Leave management', 'Attendance tracking', 'Performance reviews', 'Recruitment'],
      flows: ['Employee onboarding', 'Leave application', 'Performance evaluation', 'Recruitment process']
    }
  ];

  // Handle form submission
  const handleCreateTest = async () => {
    try {
      setIsCreating(true);
      setShowAgentMonitor(true);

      let requestData;
      
      switch (activeTab) {
        case 'requirements':
          requestData = {
            creation_type: 'requirements',
            application_url: requirementsForm.applicationUrl,
            application_name: requirementsForm.applicationName,
            application_type: requirementsForm.applicationType,
            business_requirements: requirementsForm.requirementsText,
            priority: requirementsForm.priority,
            generate_performance_tests: requirementsForm.generatePerformanceTests,
            generate_cross_browser_tests: requirementsForm.generateCrossBrowserTests
          };
          break;
        case 'test_cases':
          requestData = {
            creation_type: 'test_cases',
            application_url: testCasesForm.applicationUrl,
            application_name: testCasesForm.applicationName,
            application_type: testCasesForm.applicationType,
            test_cases: testCasesForm.testCases,
            priority: testCasesForm.priority,
            generate_performance_tests: testCasesForm.generatePerformanceTests,
            generate_cross_browser_tests: testCasesForm.generateCrossBrowserTests
          };
          break;
        case 'url_metadata':
          requestData = {
            creation_type: 'url_metadata',
            application_url: urlMetadataForm.applicationUrl,
            application_name: urlMetadataForm.applicationName,
            application_type: urlMetadataForm.applicationType,
            key_features: urlMetadataForm.keyFeatures,
            user_flows: urlMetadataForm.userFlows,
            priority: urlMetadataForm.priority,
            generate_performance_tests: urlMetadataForm.generatePerformanceTests,
            generate_cross_browser_tests: urlMetadataForm.generateCrossBrowserTests
          };
          break;
        default:
          throw new Error('Invalid creation type');
      }

      const response = await fetch('http://localhost:8000/api/v1/test/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setCurrentTask(result);
      setShowAgentMonitor(true);
      console.log('Test creation started:', result);
      
      // Start polling as fallback in case WebSocket fails
      startTaskPolling(result.task_id);
      
    } catch (error) {
      console.error('Error creating test:', error);
      alert(`Failed to create test: ${error.message}`);
      setIsCreating(false);
      setShowAgentMonitor(false);
    }
  };

  // Handle quick start template selection
  const handleQuickStart = (template) => {
    const formData = {
      applicationUrl: template.url,
      applicationName: template.name,
      applicationType: template.type,
      keyFeatures: template.features,
      userFlows: template.flows,
      priority: 'normal',
      generatePerformanceTests: false,
      generateCrossBrowserTests: false
    };
    
    setUrlMetadataForm(formData);
    setActiveTab('url_metadata');
  };

  // Polling mechanism as fallback for WebSocket failures
  const startTaskPolling = (taskId) => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }
    
    const interval = setInterval(async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch(`http://localhost:8000/api/v1/test/status/${taskId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const taskStatus = await response.json();
          console.log('Polling task status:', taskStatus);
          
          if (taskStatus.status === 'completed' || taskStatus.status === 'failed') {
            clearInterval(interval);
            setPollingInterval(null);
            
            // Trigger completion handler if WebSocket didn't already handle it
            if (isCreating) {
              handleTaskComplete({
                taskId: taskId,
                status: taskStatus.status,
                task: taskStatus,
                error: taskStatus.error
              });
            }
          }
        }
      } catch (error) {
        console.error('Error polling task status:', error);
      }
    }, 3000); // Poll every 3 seconds
    
    setPollingInterval(interval);
  };
  
  const stopTaskPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
  };

  // Handle task completion from AgentActivityMonitor
  const handleTaskComplete = (result) => {
    console.log('Task completion received:', result);
    stopTaskPolling(); // Stop polling when task completes
    setIsCreating(false);
    setTaskResult(result);
    
    if (result.status === 'completed') {
      // Show success message and redirect to results
      alert('Test creation completed successfully! Redirecting to test results...');
      setTimeout(() => {
        if (onNavigate) {
          onNavigate('results');
        }
      }, 2000);
    } else if (result.status === 'failed') {
      // Show error message
      alert(`Test creation failed: ${result.error || 'Unknown error'}`);
    }
  };

  // Add/remove dynamic form fields
  const addTestCase = () => {
    setTestCasesForm(prev => ({
      ...prev,
      testCases: [
        ...prev.testCases,
        {
          id: Date.now(),
          title: '',
          description: '',
          steps: [''],
          expectedResult: ''
        }
      ]
    }));
  };

  const removeTestCase = (id) => {
    setTestCasesForm(prev => ({
      ...prev,
      testCases: prev.testCases.filter(tc => tc.id !== id)
    }));
  };

  const addStep = (testCaseId) => {
    setTestCasesForm(prev => ({
      ...prev,
      testCases: prev.testCases.map(tc =>
        tc.id === testCaseId
          ? { ...tc, steps: [...tc.steps, ''] }
          : tc
      )
    }));
  };

  const addKeyFeature = () => {
    setUrlMetadataForm(prev => ({
      ...prev,
      keyFeatures: [...prev.keyFeatures, '']
    }));
  };

  const addUserFlow = () => {
    setUrlMetadataForm(prev => ({
      ...prev,
      userFlows: [...prev.userFlows, '']
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-white/20 rounded-lg">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">AI-Powered Test Creation</h1>
            <p className="text-blue-100">
              Create comprehensive test suites using advanced AI agents
            </p>
          </div>
        </div>
        
        {/* Quick Start Templates */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          {quickStartTemplates.map((template, index) => (
            <div
              key={index}
              className="bg-white/10 backdrop-blur-sm rounded-lg p-4 cursor-pointer hover:bg-white/20 transition-all duration-200"
              onClick={() => handleQuickStart(template)}
            >
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-lg">
                  {applicationTypes.find(t => t.value === template.type)?.icon}
                </span>
                <h3 className="font-semibold">{template.name}</h3>
              </div>
              <p className="text-sm text-blue-100 mb-2">{template.description}</p>
              <div className="flex items-center text-xs text-blue-200">
                <Zap className="w-3 h-3 mr-1" />
                Quick Start
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Test Creation Form */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-lg">
            {/* Tab Navigation */}
            <div className="border-b border-gray-200">
              <nav className="flex space-x-8 px-6">
                {[
                  { id: 'requirements', label: 'From Requirements', icon: FileText },
                  { id: 'test_cases', label: 'From Test Cases', icon: TestTube },
                  { id: 'url_metadata', label: 'From URL + Metadata', icon: Globe }
                ].map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                        activeTab === tab.id
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {/* Requirements-Based Creation */}
              {activeTab === 'requirements' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Create Tests from Business Requirements
                    </h3>
                    <p className="text-gray-600 mb-6">
                      Provide business requirements and let AI agents analyze and create comprehensive test suites.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Application URL *
                      </label>
                      <input
                        type="url"
                        value={requirementsForm.applicationUrl}
                        onChange={(e) => setRequirementsForm(prev => ({
                          ...prev,
                          applicationUrl: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="https://your-application.com"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Application Name *
                      </label>
                      <input
                        type="text"
                        value={requirementsForm.applicationName}
                        onChange={(e) => setRequirementsForm(prev => ({
                          ...prev,
                          applicationName: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="My Application"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Application Type
                    </label>
                    <select
                      value={requirementsForm.applicationType}
                      onChange={(e) => setRequirementsForm(prev => ({
                        ...prev,
                        applicationType: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {applicationTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.icon} {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Business Requirements *
                    </label>
                    <textarea
                      value={requirementsForm.requirementsText}
                      onChange={(e) => setRequirementsForm(prev => ({
                        ...prev,
                        requirementsText: e.target.value
                      }))}
                      rows={6}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Describe your business requirements, user stories, acceptance criteria, and what needs to be tested..."
                      required
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      Be specific about user flows, business rules, and expected behaviors.
                    </p>
                  </div>
                </div>
              )}

              {/* Test Cases-Based Creation */}
              {activeTab === 'test_cases' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Convert Manual Test Cases to Automated Tests
                    </h3>
                    <p className="text-gray-600 mb-6">
                      Upload or input your existing manual test cases and AI will convert them to automated tests.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Application URL *
                      </label>
                      <input
                        type="url"
                        value={testCasesForm.applicationUrl}
                        onChange={(e) => setTestCasesForm(prev => ({
                          ...prev,
                          applicationUrl: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="https://your-application.com"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Application Name *
                      </label>
                      <input
                        type="text"
                        value={testCasesForm.applicationName}
                        onChange={(e) => setTestCasesForm(prev => ({
                          ...prev,
                          applicationName: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="My Application"
                        required
                      />
                    </div>
                  </div>

                  {/* Test Cases */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <label className="block text-sm font-medium text-gray-700">
                        Test Cases *
                      </label>
                      <button
                        onClick={addTestCase}
                        className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Add Test Case
                      </button>
                    </div>

                    <div className="space-y-4">
                      {testCasesForm.testCases.map((testCase, index) => (
                        <div key={testCase.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="font-medium text-gray-900">Test Case {index + 1}</h4>
                            {testCasesForm.testCases.length > 1 && (
                              <button
                                onClick={() => removeTestCase(testCase.id)}
                                className="text-red-600 hover:text-red-800 text-sm"
                              >
                                Remove
                              </button>
                            )}
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Title
                              </label>
                              <input
                                type="text"
                                value={testCase.title}
                                onChange={(e) => {
                                  const newTestCases = testCasesForm.testCases.map(tc =>
                                    tc.id === testCase.id ? { ...tc, title: e.target.value } : tc
                                  );
                                  setTestCasesForm(prev => ({ ...prev, testCases: newTestCases }));
                                }}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Test case title"
                              />
                            </div>

                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Expected Result
                              </label>
                              <input
                                type="text"
                                value={testCase.expectedResult}
                                onChange={(e) => {
                                  const newTestCases = testCasesForm.testCases.map(tc =>
                                    tc.id === testCase.id ? { ...tc, expectedResult: e.target.value } : tc
                                  );
                                  setTestCasesForm(prev => ({ ...prev, testCases: newTestCases }));
                                }}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Expected outcome"
                              />
                            </div>
                          </div>

                          <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Description
                            </label>
                            <textarea
                              value={testCase.description}
                              onChange={(e) => {
                                const newTestCases = testCasesForm.testCases.map(tc =>
                                  tc.id === testCase.id ? { ...tc, description: e.target.value } : tc
                                );
                                setTestCasesForm(prev => ({ ...prev, testCases: newTestCases }));
                              }}
                              rows={2}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="Describe what this test case validates"
                            />
                          </div>

                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <label className="block text-sm font-medium text-gray-700">
                                Test Steps
                              </label>
                              <button
                                onClick={() => addStep(testCase.id)}
                                className="text-blue-600 hover:text-blue-800 text-sm"
                              >
                                Add Step
                              </button>
                            </div>
                            <div className="space-y-2">
                              {testCase.steps.map((step, stepIndex) => (
                                <div key={stepIndex} className="flex items-center space-x-2">
                                  <span className="text-sm text-gray-500 min-w-[2rem]">
                                    {stepIndex + 1}.
                                  </span>
                                  <input
                                    type="text"
                                    value={step}
                                    onChange={(e) => {
                                      const newTestCases = testCasesForm.testCases.map(tc =>
                                        tc.id === testCase.id
                                          ? {
                                              ...tc,
                                              steps: tc.steps.map((s, i) =>
                                                i === stepIndex ? e.target.value : s
                                              )
                                            }
                                          : tc
                                      );
                                      setTestCasesForm(prev => ({ ...prev, testCases: newTestCases }));
                                    }}
                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="Describe the test step"
                                  />
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* URL + Metadata Creation */}
              {activeTab === 'url_metadata' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Smart Test Generation from URL
                    </h3>
                    <p className="text-gray-600 mb-6">
                      Provide minimal information and let AI discover and create comprehensive test suites.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Application URL *
                      </label>
                      <input
                        type="url"
                        value={urlMetadataForm.applicationUrl}
                        onChange={(e) => setUrlMetadataForm(prev => ({
                          ...prev,
                          applicationUrl: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="https://your-application.com"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Application Name *
                      </label>
                      <input
                        type="text"
                        value={urlMetadataForm.applicationName}
                        onChange={(e) => setUrlMetadataForm(prev => ({
                          ...prev,
                          applicationName: e.target.value
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="My Application"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Application Type
                    </label>
                    <select
                      value={urlMetadataForm.applicationType}
                      onChange={(e) => setUrlMetadataForm(prev => ({
                        ...prev,
                        applicationType: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {applicationTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.icon} {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Key Features to Test
                      </label>
                      <button
                        onClick={addKeyFeature}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        Add Feature
                      </button>
                    </div>
                    <div className="space-y-2">
                      {urlMetadataForm.keyFeatures.map((feature, index) => (
                        <input
                          key={index}
                          type="text"
                          value={feature}
                          onChange={(e) => {
                            const newFeatures = urlMetadataForm.keyFeatures.map((f, i) =>
                              i === index ? e.target.value : f
                            );
                            setUrlMetadataForm(prev => ({ ...prev, keyFeatures: newFeatures }));
                          }}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="e.g., User login, Product search, Shopping cart"
                        />
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Important User Flows
                      </label>
                      <button
                        onClick={addUserFlow}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        Add Flow
                      </button>
                    </div>
                    <div className="space-y-2">
                      {urlMetadataForm.userFlows.map((flow, index) => (
                        <input
                          key={index}
                          type="text"
                          value={flow}
                          onChange={(e) => {
                            const newFlows = urlMetadataForm.userFlows.map((f, i) =>
                              i === index ? e.target.value : f
                            );
                            setUrlMetadataForm(prev => ({ ...prev, userFlows: newFlows }));
                          }}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="e.g., Complete purchase flow, User registration process"
                        />
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Common Options */}
              <div className="border-t border-gray-200 pt-6 mt-6">
                <h4 className="text-md font-semibold text-gray-900 mb-4">Additional Options</h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Priority Level
                    </label>
                    <select
                      value={
                        activeTab === 'requirements' ? requirementsForm.priority :
                        activeTab === 'test_cases' ? testCasesForm.priority :
                        urlMetadataForm.priority
                      }
                      onChange={(e) => {
                        const priority = e.target.value;
                        if (activeTab === 'requirements') {
                          setRequirementsForm(prev => ({ ...prev, priority }));
                        } else if (activeTab === 'test_cases') {
                          setTestCasesForm(prev => ({ ...prev, priority }));
                        } else {
                          setUrlMetadataForm(prev => ({ ...prev, priority }));
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {priorityLevels.map((level) => (
                        <option key={level.value} value={level.value}>
                          {level.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="performanceTests"
                      checked={
                        activeTab === 'requirements' ? requirementsForm.generatePerformanceTests :
                        activeTab === 'test_cases' ? testCasesForm.generatePerformanceTests :
                        urlMetadataForm.generatePerformanceTests
                      }
                      onChange={(e) => {
                        const checked = e.target.checked;
                        if (activeTab === 'requirements') {
                          setRequirementsForm(prev => ({ ...prev, generatePerformanceTests: checked }));
                        } else if (activeTab === 'test_cases') {
                          setTestCasesForm(prev => ({ ...prev, generatePerformanceTests: checked }));
                        } else {
                          setUrlMetadataForm(prev => ({ ...prev, generatePerformanceTests: checked }));
                        }
                      }}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="performanceTests" className="ml-2 text-sm text-gray-700">
                      Generate performance tests
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="crossBrowserTests"
                      checked={
                        activeTab === 'requirements' ? requirementsForm.generateCrossBrowserTests :
                        activeTab === 'test_cases' ? testCasesForm.generateCrossBrowserTests :
                        urlMetadataForm.generateCrossBrowserTests
                      }
                      onChange={(e) => {
                        const checked = e.target.checked;
                        if (activeTab === 'requirements') {
                          setRequirementsForm(prev => ({ ...prev, generateCrossBrowserTests: checked }));
                        } else if (activeTab === 'test_cases') {
                          setTestCasesForm(prev => ({ ...prev, generateCrossBrowserTests: checked }));
                        } else {
                          setUrlMetadataForm(prev => ({ ...prev, generateCrossBrowserTests: checked }));
                        }
                      }}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="crossBrowserTests" className="ml-2 text-sm text-gray-700">
                      Generate cross-browser tests
                    </label>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-6 border-t border-gray-200">
                <div className="text-sm text-gray-500">
                  {isCreating ? (
                    <div className="flex items-center space-x-2">
                      <Bot className="w-4 h-4 animate-pulse" />
                      <span>AI agents are working...</span>
                    </div>
                  ) : (
                    <span>Ready to create comprehensive test suite</span>
                  )}
                </div>
                
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => setShowAgentMonitor(!showAgentMonitor)}
                    className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors flex items-center space-x-2"
                  >
                    <Eye className="w-4 h-4" />
                    <span>{showAgentMonitor ? 'Hide' : 'Show'} Agent Activity</span>
                  </button>
                  
                  <button
                    onClick={handleCreateTest}
                    disabled={isCreating}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                  >
                    <Play className="w-4 h-4" />
                    <span>{isCreating ? 'Creating...' : 'Create Tests'}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Agent Activity Monitor */}
        <div className="lg:col-span-1">
          {showAgentMonitor && (
            <AgentActivityMonitor
              userId={user?.id}
              taskId={currentTask?.task_id}
              className="sticky top-6"
              onTaskComplete={handleTaskComplete}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default CreateTestRealTime;
