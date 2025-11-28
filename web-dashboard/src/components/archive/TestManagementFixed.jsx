import React, { useState, useEffect } from 'react';

const TestManagementFixed = ({ user, deploymentMode }) => {
  const [testSuites, setTestSuites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      const mockSuites = [
        {
          id: '1',
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
        }
      ];
      
      // Check localStorage for latest test suite
      const latestSuiteData = localStorage.getItem('latest_test_suite');
      if (latestSuiteData) {
        try {
          const latestSuite = JSON.parse(latestSuiteData);
          mockSuites.unshift(latestSuite);
        } catch (e) {
          console.error('Error parsing latest test suite:', e);
        }
      }
      
      setTestSuites(mockSuites);
      setLoading(false);
    }, 500);
  }, []);

  const executeTests = (suiteId) => {
    alert(`Executing tests for suite ${suiteId}...`);
  };

  const downloadSuite = (suiteId) => {
    alert(`Downloading test suite ${suiteId}...`);
  };

  if (loading) {
    return (
      <div style={{ 
        padding: '40px', 
        textAlign: 'center',
        minHeight: '400px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #3498db',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <p style={{ marginTop: '20px', color: '#666' }}>Loading test suites...</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div style={{ 
      padding: '30px',
      backgroundColor: '#f8f9fa',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ 
          fontSize: '32px', 
          fontWeight: 'bold', 
          color: '#2c3e50',
          marginBottom: '8px'
        }}>
          🎯 Test Management
        </h1>
        <p style={{ 
          color: '#7f8c8d', 
          fontSize: '16px',
          marginBottom: '20px'
        }}>
          Manage and execute your AI-generated test suites
        </p>
        
        {/* Stats Bar */}
        <div style={{
          display: 'flex',
          gap: '20px',
          marginBottom: '20px'
        }}>
          <div style={{
            backgroundColor: '#3498db',
            color: 'white',
            padding: '15px 20px',
            borderRadius: '8px',
            textAlign: 'center',
            minWidth: '120px'
          }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{testSuites.length}</div>
            <div style={{ fontSize: '14px', opacity: 0.9 }}>Test Suites</div>
          </div>
          <div style={{
            backgroundColor: '#27ae60',
            color: 'white',
            padding: '15px 20px',
            borderRadius: '8px',
            textAlign: 'center',
            minWidth: '120px'
          }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
              {testSuites.reduce((sum, suite) => sum + (suite.test_count || 0), 0)}
            </div>
            <div style={{ fontSize: '14px', opacity: 0.9 }}>Total Tests</div>
          </div>
          <div style={{
            backgroundColor: '#e74c3c',
            color: 'white',
            padding: '15px 20px',
            borderRadius: '8px',
            textAlign: 'center',
            minWidth: '120px'
          }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
              {testSuites.length > 0 ? Math.round(testSuites.reduce((sum, suite) => sum + (suite.coverage || 0), 0) / testSuites.length) : 0}%
            </div>
            <div style={{ fontSize: '14px', opacity: 0.9 }}>Avg Coverage</div>
          </div>
        </div>
      </div>

      {/* Test Suites */}
      {testSuites.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          backgroundColor: 'white',
          borderRadius: '12px',
          border: '2px dashed #bdc3c7'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>📋</div>
          <h3 style={{ fontSize: '24px', color: '#2c3e50', marginBottom: '10px' }}>
            No Test Suites Found
          </h3>
          <p style={{ color: '#7f8c8d', marginBottom: '30px' }}>
            Create your first test suite to get started with AI-powered testing
          </p>
          <button 
            onClick={() => window.location.hash = '#/create-test'}
            style={{
              backgroundColor: '#3498db',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '6px',
              fontSize: '16px',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            Create Test Suite
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {testSuites.map((suite) => (
            <div key={suite.id} style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '30px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
              border: '1px solid #ecf0f1'
            }}>
              {/* Suite Header */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '20px'
              }}>
                <div>
                  <h3 style={{
                    fontSize: '24px',
                    fontWeight: 'bold',
                    color: '#2c3e50',
                    marginBottom: '8px'
                  }}>
                    {suite.name}
                  </h3>
                  <p style={{ color: '#7f8c8d', marginBottom: '4px' }}>
                    {suite.application_name}
                  </p>
                  <p style={{ color: '#95a5a6', fontSize: '14px' }}>
                    {suite.application_url}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <span style={{
                    backgroundColor: suite.status === 'ready' ? '#27ae60' : '#95a5a6',
                    color: 'white',
                    padding: '6px 12px',
                    borderRadius: '20px',
                    fontSize: '12px',
                    fontWeight: '500'
                  }}>
                    {suite.status}
                  </span>
                  <span style={{
                    backgroundColor: '#3498db',
                    color: 'white',
                    padding: '6px 12px',
                    borderRadius: '20px',
                    fontSize: '12px',
                    fontWeight: '500'
                  }}>
                    {suite.application_type}
                  </span>
                </div>
              </div>

              {/* Metrics */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '20px',
                marginBottom: '20px',
                padding: '20px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px'
              }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#3498db' }}>
                    {suite.test_count}
                  </div>
                  <div style={{ fontSize: '14px', color: '#7f8c8d' }}>Test Cases</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#27ae60' }}>
                    {suite.coverage}%
                  </div>
                  <div style={{ fontSize: '14px', color: '#7f8c8d' }}>Coverage</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#e74c3c' }}>
                    {suite.features?.length || 0}
                  </div>
                  <div style={{ fontSize: '14px', color: '#7f8c8d' }}>Features</div>
                </div>
              </div>

              {/* Features */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ 
                  fontSize: '16px', 
                  fontWeight: '600', 
                  color: '#2c3e50',
                  marginBottom: '10px'
                }}>
                  Features Tested:
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {suite.features?.map((feature, index) => (
                    <span key={index} style={{
                      backgroundColor: '#ecf0f1',
                      color: '#2c3e50',
                      padding: '6px 12px',
                      borderRadius: '16px',
                      fontSize: '14px'
                    }}>
                      {feature}
                    </span>
                  ))}
                </div>
              </div>

              {/* Files */}
              <div style={{ marginBottom: '25px' }}>
                <h4 style={{ 
                  fontSize: '16px', 
                  fontWeight: '600', 
                  color: '#2c3e50',
                  marginBottom: '10px'
                }}>
                  Generated Files:
                </h4>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                  gap: '10px'
                }}>
                  {suite.files?.map((file, index) => (
                    <div key={index} style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '12px',
                      backgroundColor: '#f8f9fa',
                      borderRadius: '6px',
                      border: '1px solid #ecf0f1'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{ marginRight: '8px', fontSize: '16px' }}>📄</span>
                        <span style={{ fontSize: '14px', fontWeight: '500' }}>
                          {file.name}
                        </span>
                      </div>
                      <span style={{ fontSize: '12px', color: '#7f8c8d' }}>
                        {file.size}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <button 
                  onClick={() => executeTests(suite.id)}
                  style={{
                    backgroundColor: '#27ae60',
                    color: 'white',
                    border: 'none',
                    padding: '12px 20px',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  ▶️ Execute Tests
                </button>
                <button 
                  style={{
                    backgroundColor: '#3498db',
                    color: 'white',
                    border: 'none',
                    padding: '12px 20px',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  👁️ View Details
                </button>
                <button 
                  onClick={() => downloadSuite(suite.id)}
                  style={{
                    backgroundColor: '#95a5a6',
                    color: 'white',
                    border: 'none',
                    padding: '12px 20px',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
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

export default TestManagementFixed;
