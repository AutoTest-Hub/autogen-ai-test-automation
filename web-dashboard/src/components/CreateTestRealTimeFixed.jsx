import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '../lib/api';
import { useAgentStatus } from '../hooks/useAgentStatus';

const CreateTestRealTimeFixed = () => {
  const [formData, setFormData] = useState({
    url: '',
    name: '',
    type: '',
    key_features: '',
    user_flows: ''
  });
  
  const [isCreating, setIsCreating] = useState(false);
  const [showAgentActivity, setShowAgentActivity] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Use the custom hook for agent status
  const { jobData, activities, isLoading, isError } = useAgentStatus(jobId, isCreating);

  // Quick start options
  const quickStartOptions = [
    {
      name: 'HRMS Demo',
      url: 'https://opensource-demo.orangehrmlive.com',
      type: 'HRMS',
      features: 'Employee management, Leave management, Attendance tracking, Performance reviews',
      flows: 'Employee onboarding, Leave application, Performance evaluation, Recruitment process'
    },
    {
      name: 'E-commerce Demo',
      url: 'https://demo.opencart.com',
      type: 'E-commerce',
      features: 'Product catalog, Shopping cart, Payment processing, Order management',
      flows: 'Product browsing, Add to cart, Checkout process, Order tracking'
    },
    {
      name: 'Banking Demo',
      url: 'https://demo.testfire.net',
      type: 'Banking',
      features: 'Account management, Fund transfers, Bill payments, Transaction history',
      flows: 'Login authentication, Balance inquiry, Money transfer, Bill payment'
    }
  ];

  // Check if job is completed
  React.useEffect(() => {
    if (jobData && (jobData.status === 'completed' || jobData.status === 'failed')) {
      setIsCreating(false);
      if (jobData.status === 'failed') {
        setError('Test creation failed. Please try again.');
      } else if (jobData.status === 'completed') {
        setSuccess('Test creation completed successfully!');
      }
    }
  }, [jobData]);

  const handleQuickStart = (option) => {
    setFormData({
      url: option.url,
      name: option.name,
      type: option.type,
      key_features: option.features,
      user_flows: option.flows
    });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCreateTest = async () => {
    if (!formData.url || !formData.name || !formData.type) {
      setError('Please fill in all required fields');
      return;
    }

    setIsCreating(true);
    setError(null);
    setSuccess(null);
    setJobId(null);

    try {
      const data = await apiService.request('/api/v1/create-test', {
        method: 'POST',
        body: formData
      });

      setJobId(data.job_id);
      setShowAgentActivity(true);
      setSuccess('Test creation started successfully!');
    } catch (err) {
      setError(err.message || 'Network error. Please check your connection.');
      setIsCreating(false);
    }
  };

  const getAgentProgress = (agentName) => {
    const progressActivity = activities.find(activity => 
      activity.agent_name === agentName && activity.activity_type === 'progress'
    );
    const completedActivity = activities.find(activity => 
      activity.agent_name === agentName && activity.activity_type === 'completed'
    );
    
    if (completedActivity) return 100;
    return progressActivity ? progressActivity.progress_percentage : 0;
  };

  const getAgentStatus = (agentName) => {
    const completedActivity = activities.find(activity => 
      activity.agent_name === agentName && activity.activity_type === 'completed'
    );
    if (completedActivity) return 'completed';
    
    const runningActivity = activities.find(activity => 
      activity.agent_name === agentName && activity.status === 'running'
    );
    if (runningActivity) return 'running';
    
    return 'pending';
  };

  const getAgentMessage = (agentName) => {
    const latestActivity = activities
      .filter(activity => activity.agent_name === agentName)
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];
    
    return latestActivity?.message || 'Waiting to start...';
  };

  const agents = [
    { name: 'Discovery Agent', description: 'Analyzing application structure' },
    { name: 'Test Generation Agent', description: 'Generating test scenarios' },
    { name: 'Code Generation Agent', description: 'Creating test automation code' },
    { name: 'Validation Agent', description: 'Validating generated tests' }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-4xl mx-auto p-6"
    >
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Create AI-Powered Tests</h1>
        
        {/* Quick Start Options */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Start Options</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickStartOptions.map((option, index) => (
              <button
                key={index}
                onClick={() => handleQuickStart(option)}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
              >
                <h3 className="font-semibold text-gray-900">{option.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{option.type}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Form */}
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Application URL *
            </label>
            <input
              type="url"
              name="url"
              value={formData.url}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Application Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="My Application"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Application Type *
            </label>
            <select
              name="type"
              value={formData.type}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select type...</option>
              <option value="E-commerce">E-commerce</option>
              <option value="Banking">Banking</option>
              <option value="HRMS">HRMS</option>
              <option value="CRM">CRM</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Key Features
            </label>
            <textarea
              name="key_features"
              value={formData.key_features}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="List the main features to test..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Important User Flows
            </label>
            <textarea
              name="user_flows"
              value={formData.user_flows}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe the critical user journeys..."
            />
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {success && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-green-800">{success}</p>
          </div>
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-blue-800">Loading agent status...</p>
          </div>
        )}

        {/* Agent Activity Toggle */}
        <div className="mt-8 flex justify-between items-center">
          <button
            onClick={() => setShowAgentActivity(!showAgentActivity)}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
          >
            {showAgentActivity ? 'Hide Agent Activity' : 'Show Agent Activity'}
          </button>

          <button
            onClick={handleCreateTest}
            disabled={isCreating}
            className={`px-8 py-3 rounded-md font-semibold transition-colors ${
              isCreating
                ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isCreating ? 'Creating...' : 'Create Tests'}
          </button>
        </div>

        {/* Agent Activity Monitor */}
        {showAgentActivity && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
            className="mt-8 p-6 bg-gray-50 rounded-lg"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Activity Monitor</h3>
            
            {jobData && (
              <div className="mb-4 p-4 bg-white rounded-md">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium">Overall Progress</span>
                  <span className="text-sm text-gray-600">{jobData.progress_percentage || 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${jobData.progress_percentage || 0}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Status: {jobData.status} | Current Agent: {jobData.current_agent}
                </p>
              </div>
            )}

            <div className="space-y-4">
              {agents.map((agent, index) => {
                const progress = getAgentProgress(agent.name);
                const status = getAgentStatus(agent.name);
                const message = getAgentMessage(agent.name);
                
                return (
                  <div key={index} className="p-4 bg-white rounded-md">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-medium text-gray-900">{agent.name}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        status === 'completed' ? 'bg-green-100 text-green-800' :
                        status === 'running' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {status === 'completed' ? 'Completed' :
                         status === 'running' ? 'Processing' : 'Pending'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{message}</p>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${
                          status === 'completed' ? 'bg-green-500' :
                          status === 'running' ? 'bg-yellow-500' : 'bg-gray-300'
                        }`}
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                    <div className="text-right text-xs text-gray-500 mt-1">
                      {progress}%
                    </div>
                  </div>
                );
              })}
            </div>

            {activities.length === 0 && !isCreating && (
              <div className="text-center py-8 text-gray-500">
                <p>No agent activities yet. Start a test creation task to see real-time progress.</p>
              </div>
            )}

            {/* Debug info for development */}
            {process.env.NODE_ENV === 'development' && activities.length > 0 && (
              <div className="mt-4 p-4 bg-gray-100 rounded-md">
                <h4 className="font-medium text-gray-900 mb-2">Debug: Recent Activities</h4>
                <div className="text-xs text-gray-600 space-y-1">
                  {activities.slice(0, 5).map((activity, index) => (
                    <div key={index}>
                      {activity.agent_name} - {activity.activity_type} - {activity.status} - {activity.progress_percentage}%
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default CreateTestRealTimeFixed;
