import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const TestManagementEnhanced = () => {
  const [testSuites, setTestSuites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSuite, setSelectedSuite] = useState(null);
  const [executingTests, setExecutingTests] = useState(new Set());
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchTestSuites();
  }, []);

  const fetchTestSuites = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/test-suites', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTestSuites(data);
      setError(null);
    } catch (error) {
      console.error('Failed to fetch test suites:', error);
      setError('Failed to load test suites. Please try again.');
      // Fallback to mock data for development
      setTestSuites(getMockTestSuites());
    } finally {
      setLoading(false);
    }
  };

  const getMockTestSuites = () => [
    {
      id: '1',
      name: 'HRMS Login Flow Test',
      description: 'Comprehensive login and authentication testing',
      test_type: 'functional',
      status: 'active',
      total_test_cases: 8,
      estimated_duration_minutes: 15,
      last_execution_status: 'completed',
      success_rate: 95.0,
      last_execution_date: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      application_name: 'HRMS Demo'
    },
    {
      id: '2',
      name: 'Employee Management Test',
      description: 'Employee CRUD operations and data validation',
      test_type: 'functional',
      status: 'active',
      total_test_cases: 12,
      estimated_duration_minutes: 25,
      last_execution_status: 'running',
      success_rate: 87.0,
      last_execution_date: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
      application_name: 'HRMS Demo'
    },
    {
      id: '3',
      name: 'Leave Application Test',
      description: 'Leave request workflow and approval process',
      test_type: 'integration',
      status: 'active',
      total_test_cases: 6,
      estimated_duration_minutes: 18,
      last_execution_status: 'failed',
      success_rate: 78.0,
      last_execution_date: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
      created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      application_name: 'HRMS Demo'
    }
  ];

  const executeTestSuite = async (suiteId) => {
    try {
      setExecutingTests(prev => new Set([...prev, suiteId]));
      
      const response = await fetch(`/api/v1/test-suites/${suiteId}/execute`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        // Update the test suite status to running
        setTestSuites(prev => 
          prev.map(suite => 
            suite.id === suiteId 
              ? { ...suite, last_execution_status: 'running' }
              : suite
          )
        );

        // Simulate execution completion after some time
        setTimeout(() => {
          setExecutingTests(prev => {
            const newSet = new Set(prev);
            newSet.delete(suiteId);
            return newSet;
          });
          
          // Update with completed status
          setTestSuites(prev => 
            prev.map(suite => 
              suite.id === suiteId 
                ? { 
                    ...suite, 
                    last_execution_status: 'completed',
                    last_execution_date: new Date().toISOString(),
                    success_rate: Math.random() > 0.3 ? 95 + Math.random() * 5 : 70 + Math.random() * 20
                  }
                : suite
            )
          );
        }, 10000); // 10 seconds simulation
      }
    } catch (error) {
      console.error('Failed to execute test suite:', error);
      setExecutingTests(prev => {
        const newSet = new Set(prev);
        newSet.delete(suiteId);
        return newSet;
      });
    }
  };

  const deleteTestSuite = async (suiteId) => {
    if (!confirm('Are you sure you want to delete this test suite?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/test-suites/${suiteId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        setTestSuites(prev => prev.filter(suite => suite.id !== suiteId));
      }
    } catch (error) {
      console.error('Failed to delete test suite:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSuccessRateColor = (rate) => {
    if (rate >= 90) return 'text-green-600';
    if (rate >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredTestSuites = testSuites.filter(suite => {
    const matchesFilter = filter === 'all' || suite.status === filter;
    const matchesSearch = suite.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         suite.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getTimeAgo = (dateString) => {
    if (!dateString) return 'Never';
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
              <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-20 bg-gray-200 rounded"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-lg p-8"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Test Management</h1>
              <p className="text-gray-600 mt-2">Manage and execute your AI-generated test suites</p>
            </div>
            
            <div className="flex space-x-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={fetchTestSuites}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              >
                Refresh
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => window.location.href = '/create-test'}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Create New Test
              </motion.button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md"
            >
              <div className="text-red-800">{error}</div>
            </motion.div>
          )}

          {/* Filters and Search */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex space-x-2">
              {['all', 'active', 'completed', 'failed'].map(filterOption => (
                <button
                  key={filterOption}
                  onClick={() => setFilter(filterOption)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    filter === filterOption
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
                </button>
              ))}
            </div>
            
            <div className="flex-1 max-w-md">
              <input
                type="text"
                placeholder="Search test suites..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-600">{testSuites.length}</div>
              <div className="text-sm text-blue-800">Total Test Suites</div>
            </div>
            
            <div className="bg-green-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-green-600">
                {testSuites.filter(s => s.last_execution_status === 'completed').length}
              </div>
              <div className="text-sm text-green-800">Completed</div>
            </div>
            
            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-yellow-600">
                {testSuites.filter(s => s.last_execution_status === 'running').length}
              </div>
              <div className="text-sm text-yellow-800">Running</div>
            </div>
            
            <div className="bg-red-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-red-600">
                {testSuites.filter(s => s.last_execution_status === 'failed').length}
              </div>
              <div className="text-sm text-red-800">Failed</div>
            </div>
          </div>

          {/* Test Suites List */}
          <div className="space-y-4">
            <AnimatePresence>
              {filteredTestSuites.map((suite, index) => (
                <motion.div
                  key={suite.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-gray-50 rounded-lg p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{suite.name}</h3>
                        
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(suite.last_execution_status)}`}>
                          {suite.last_execution_status || 'pending'}
                        </span>
                        
                        <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded-full text-xs">
                          {suite.test_type}
                        </span>
                      </div>
                      
                      <p className="text-gray-600 mb-3">{suite.description}</p>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Test Cases:</span>
                          <span className="ml-1 font-medium">{suite.total_test_cases}</span>
                        </div>
                        
                        <div>
                          <span className="text-gray-500">Duration:</span>
                          <span className="ml-1 font-medium">{suite.estimated_duration_minutes}m</span>
                        </div>
                        
                        <div>
                          <span className="text-gray-500">Success Rate:</span>
                          <span className={`ml-1 font-medium ${getSuccessRateColor(suite.success_rate)}`}>
                            {suite.success_rate ? `${suite.success_rate.toFixed(1)}%` : 'N/A'}
                          </span>
                        </div>
                        
                        <div>
                          <span className="text-gray-500">Last Run:</span>
                          <span className="ml-1 font-medium">{getTimeAgo(suite.last_execution_date)}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2 ml-6">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => executeTestSuite(suite.id)}
                        disabled={executingTests.has(suite.id)}
                        className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                          executingTests.has(suite.id)
                            ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
                            : 'bg-green-600 text-white hover:bg-green-700'
                        }`}
                      >
                        {executingTests.has(suite.id) ? 'Running...' : 'Run'}
                      </motion.button>
                      
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setSelectedSuite(suite)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
                      >
                        Edit
                      </motion.button>
                      
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => deleteTestSuite(suite.id)}
                        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm font-medium"
                      >
                        Delete
                      </motion.button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Empty State */}
          {filteredTestSuites.length === 0 && !loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No test suites found</h3>
              <p className="text-gray-600 mb-4">
                {searchTerm || filter !== 'all' 
                  ? 'Try adjusting your search or filter criteria.'
                  : 'Get started by creating your first AI-powered test suite.'
                }
              </p>
              {!searchTerm && filter === 'all' && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => window.location.href = '/create-test'}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Create Your First Test
                </motion.button>
              )}
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default TestManagementEnhanced;
