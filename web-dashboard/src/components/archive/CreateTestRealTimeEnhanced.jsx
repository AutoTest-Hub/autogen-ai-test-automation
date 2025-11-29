import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AgentActivityMonitorStable from './AgentActivityMonitorStable';

const CreateTestRealTimeEnhanced = () => {
  const [formData, setFormData] = useState({
    application_url: '',
    application_name: '',
    application_type: 'Web Application',
    key_features: [],
    user_flows: [],
    creation_type: 'url_metadata'
  });

  const [isCreating, setIsCreating] = useState(false);
  const [showAgentActivity, setShowAgentActivity] = useState(false);
  const [testCreationSession, setTestCreationSession] = useState(null);
  const [agents, setAgents] = useState([]);
  const [creationComplete, setCreationComplete] = useState(false);
  const [error, setError] = useState(null);

  // WebSocket connection for real-time updates
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // Initialize WebSocket connection
    const websocket = new WebSocket('ws://localhost:8000/api/v1/ws/agent-activity');
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
      setWs(websocket);
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setWs(null);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const handleWebSocketMessage = (data) => {
    if (data.type === 'agent_status_update') {
      updateAgentStatus(data.agent);
    } else if (data.type === 'test_creation_completed') {
      setCreationComplete(true);
      setIsCreating(false);
      setTestCreationSession(prev => ({
        ...prev,
        status: 'completed',
        created_test_suites: data.test_suites
      }));
    }
  };

  const updateAgentStatus = (agentUpdate) => {
    setAgents(prevAgents => 
      prevAgents.map(agent => 
        agent.name === agentUpdate.name 
          ? { ...agent, ...agentUpdate }
          : agent
      )
    );
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleKeyFeaturesChange = (e) => {
    const features = e.target.value.split('\n').filter(f => f.trim());
    setFormData(prev => ({
      ...prev,
      key_features: features
    }));
  };

  const handleUserFlowsChange = (e) => {
    const flows = e.target.value.split('\n').filter(f => f.trim());
    setFormData(prev => ({
      ...prev,
      user_flows: flows
    }));
  };

  const handleHRMSQuickStart = () => {
    setFormData({
      application_url: 'https://opensource-demo.orangehrmlive.com',
      application_name: 'HRMS Demo',
      application_type: 'HRMS',
      key_features: [
        'Employee management',
        'Leave management',
        'Attendance tracking',
        'Performance reviews',
        'Recruitment'
      ],
      user_flows: [
        'Employee onboarding',
        'Leave application',
        'Performance evaluation',
        'Recruitment process'
      ],
      creation_type: 'url_metadata'
    });
  };

  const handleCreateTests = async () => {
    if (!formData.application_url || !formData.application_name) {
      setError('Please fill in required fields');
      return;
    }

    setIsCreating(true);
    setError(null);
    setCreationComplete(false);
    setShowAgentActivity(true);

    // Initialize agents with pending status
    const initialAgents = [
      { name: 'Discovery Agent', type: 'discovery', status: 'pending', progress: 0, current_task: 'Waiting to start...' },
      { name: 'Test Generation Agent', type: 'test_generation', status: 'pending', progress: 0, current_task: 'Waiting to start...' },
      { name: 'Code Generation Agent', type: 'code_generation', status: 'pending', progress: 0, current_task: 'Waiting to start...' },
      { name: 'Validation Agent', type: 'validation', status: 'pending', progress: 0, current_task: 'Waiting to start...' }
    ];
    setAgents(initialAgents);

    try {
      const response = await fetch('/api/v1/tests/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setTestCreationSession(result.data);
        // Start polling for status updates
        pollTestCreationStatus(result.data.session_id);
      } else {
        throw new Error(result.message || 'Test creation failed');
      }

    } catch (error) {
      console.error('Test creation error:', error);
      setError(error.message);
      setIsCreating(false);
      setShowAgentActivity(false);
    }
  };

  const pollTestCreationStatus = async (sessionId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/tests/status/${sessionId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (response.ok) {
          const status = await response.json();
          setTestCreationSession(status);
          setAgents(status.agents || []);

          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(pollInterval);
            setIsCreating(false);
            if (status.status === 'completed') {
              setCreationComplete(true);
            } else {
              setError(status.error_message || 'Test creation failed');
            }
          }
        }
      } catch (error) {
        console.error('Status polling error:', error);
      }
    }, 2000); // Poll every 2 seconds

    // Clear interval after 5 minutes to prevent infinite polling
    setTimeout(() => clearInterval(pollInterval), 300000);
  };

  const navigateToTestManagement = () => {
    window.location.href = '/manage-tests';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-lg p-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Create AI-Powered Tests</h1>

          {/* Quick Start Options */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Start Options</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleHRMSQuickStart}
                className="p-4 border-2 border-orange-200 rounded-lg hover:border-orange-400 transition-colors"
              >
                <div className="text-orange-600 font-semibold">HRMS Demo</div>
                <div className="text-sm text-gray-600">Quick start with HRMS testing</div>
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="p-4 border-2 border-blue-200 rounded-lg hover:border-blue-400 transition-colors"
              >
                <div className="text-blue-600 font-semibold">E-commerce Demo</div>
                <div className="text-sm text-gray-600">Online store testing</div>
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="p-4 border-2 border-green-200 rounded-lg hover:border-green-400 transition-colors"
              >
                <div className="text-green-600 font-semibold">Banking Demo</div>
                <div className="text-sm text-gray-600">Financial app testing</div>
              </motion.button>
            </div>
          </div>

          {/* Test Creation Form */}
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Application URL *
                </label>
                <input
                  type="url"
                  name="application_url"
                  value={formData.application_url}
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
                  name="application_name"
                  value={formData.application_name}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                name="application_type"
                value={formData.application_type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Web Application">Web Application</option>
                <option value="E-commerce">E-commerce</option>
                <option value="HRMS">HRMS</option>
                <option value="Banking">Banking</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Education">Education</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Key Features to Test
              </label>
              <textarea
                value={formData.key_features.join('\n')}
                onChange={handleKeyFeaturesChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="4"
                placeholder="Enter each feature on a new line..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Important User Flows
              </label>
              <textarea
                value={formData.user_flows.join('\n')}
                onChange={handleUserFlowsChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="4"
                placeholder="Enter each user flow on a new line..."
              />
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md"
            >
              <div className="text-red-800">{error}</div>
            </motion.div>
          )}

          {/* Agent Activity Monitor */}
          <AnimatePresence>
            {showAgentActivity && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-8"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Agent Activity</h3>
                  <button
                    onClick={() => setShowAgentActivity(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    Hide Agent Activity
                  </button>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-6">
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                      <span className="text-sm text-gray-600">
                        {testCreationSession?.progress_percentage || 0}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${testCreationSession?.progress_percentage || 0}%` }}
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    {agents.map((agent, index) => (
                      <motion.div
                        key={agent.name}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="bg-white rounded-lg p-4 shadow-sm"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full ${
                              agent.status === 'completed' ? 'bg-green-500' :
                              agent.status === 'processing' ? 'bg-blue-500 animate-pulse' :
                              agent.status === 'failed' ? 'bg-red-500' :
                              'bg-gray-300'
                            }`} />
                            <span className="font-medium text-gray-900">{agent.name}</span>
                          </div>
                          <span className="text-sm text-gray-600">{agent.progress}%</span>
                        </div>
                        
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-300 ${
                              agent.status === 'completed' ? 'bg-green-500' :
                              agent.status === 'processing' ? 'bg-blue-500' :
                              agent.status === 'failed' ? 'bg-red-500' :
                              'bg-gray-300'
                            }`}
                            style={{ width: `${agent.progress}%` }}
                          />
                        </div>
                        
                        <div className="text-sm text-gray-600">{agent.current_task}</div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Success Message */}
          {creationComplete && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg"
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-green-800">Tests Created Successfully!</h3>
              </div>
              
              <p className="text-green-700 mb-4">
                Your AI-powered tests have been generated and are ready for execution.
                {testCreationSession?.created_test_suites?.length > 0 && 
                  ` Created ${testCreationSession.created_test_suites.length} test suite(s).`
                }
              </p>
              
              <button
                onClick={navigateToTestManagement}
                className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
              >
                View Test Management
              </button>
            </motion.div>
          )}

          {/* Action Buttons */}
          <div className="mt-8 flex space-x-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleCreateTests}
              disabled={isCreating}
              className={`px-8 py-3 rounded-md font-semibold transition-colors ${
                isCreating
                  ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isCreating ? 'Creating...' : 'Create Tests'}
            </motion.button>

            {!showAgentActivity && !isCreating && (
              <button
                onClick={() => setShowAgentActivity(true)}
                className="px-8 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              >
                Show Agent Activity
              </button>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default CreateTestRealTimeEnhanced;
