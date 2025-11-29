import React, { useState, useEffect } from 'react';

const TestManagementBasic = ({ user }) => {
  const [testSuites, setTestSuites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTestSuites();
  }, []);

  const loadTestSuites = async () => {
    try {
      // Load existing test suites (mock data for now)
      const mockSuites = [];
      
      // Check for latest test suite from localStorage
      const latestSuiteData = localStorage.getItem('latest_test_suite');
      if (latestSuiteData) {
        try {
          const latestSuite = JSON.parse(latestSuiteData);
          mockSuites.push(latestSuite);
        } catch (e) {
          console.error('Error parsing latest test suite:', e);
        }
      }
      
      // Add default HRMS demo if no suites exist
      if (mockSuites.length === 0) {
        mockSuites.push({
          id: '294971fc-903e-4c58-9135-b07bc261827d',
          name: 'HRMS Demo Test Suite',
          application_name: 'HRMS Demo',
          application_url: 'https://opensource-demo.orangehrmlive.com',
          application_type: 'HRMS',
          status: 'ready',
          created_at: new Date().toISOString(),
          test_count: 12,
          coverage: 87,
          features: ['Employee management', 'Leave management', 'Attendance tracking', 'Performance reviews'],
          files: [
            { name: 'test_login.py', type: 'test', size: '2.4 KB' },
            { name: 'test_employee_management.py', type: 'test', size: '5.1 KB' },
            { name: 'test_leave_management.py', type: 'test', size: '3.8 KB' },
            { name: 'page_objects.py', type: 'page_object', size: '4.2 KB' }
          ]
        });
      }
      
      setTestSuites(mockSuites);
      setLoading(false);
    } catch (error) {
      console.error('Error loading test suites:', error);
      setLoading(false);
    }
  };

  const executeTests = async (suiteId) => {
    try {
      alert(`Executing tests for suite ${suiteId}...`);
      // Here you would call the actual test execution API
    } catch (error) {
      console.error('Error executing tests:', error);
      alert('Failed to execute tests');
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading test suites...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Test Management</h1>
        <p className="text-gray-600 mt-2">Manage and execute your AI-generated test suites</p>
      </div>

      {testSuites.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📋</div>
          <h3 className="text-xl font-medium text-gray-900 mb-2">No Test Suites Found</h3>
          <p className="text-gray-500 mb-6">Create your first test suite to get started</p>
          <button 
            onClick={() => window.location.hash = '#/create-test'}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
          >
            Create Test Suite
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {testSuites.map((suite) => (
            <div key={suite.id} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{suite.name}</h3>
                  <p className="text-gray-600">{suite.application_name}</p>
                  <p className="text-sm text-gray-500">{suite.application_url}</p>
                </div>
                <div className="flex space-x-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    suite.status === 'ready' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {suite.status}
                  </span>
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {suite.application_type}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{suite.test_count}</div>
                  <div className="text-sm text-gray-500">Test Cases</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{suite.coverage}%</div>
                  <div className="text-sm text-gray-500">Coverage</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{suite.features?.length || 0}</div>
                  <div className="text-sm text-gray-500">Features</div>
                </div>
              </div>

              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Features Tested:</h4>
                <div className="flex flex-wrap gap-2">
                  {suite.features?.map((feature, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                      {feature}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Generated Files:</h4>
                <div className="grid grid-cols-2 gap-2">
                  {suite.files?.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex items-center">
                        <span className="text-blue-500 mr-2">📄</span>
                        <span className="text-sm font-medium">{file.name}</span>
                      </div>
                      <span className="text-xs text-gray-500">{file.size}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex space-x-3">
                <button 
                  onClick={() => executeTests(suite.id)}
                  className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center"
                >
                  ▶️ Execute Tests
                </button>
                <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center">
                  👁️ View Details
                </button>
                <button className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg flex items-center">
                  📥 Download
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TestManagementBasic;
