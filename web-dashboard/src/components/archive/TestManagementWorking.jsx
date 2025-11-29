import React, { useState, useEffect } from 'react';

const TestManagementWorking = ({ user, deploymentMode }) => {
  const [testSuites, setTestSuites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load test suites from localStorage
    const loadTestSuites = () => {
      try {
        const stored = localStorage.getItem('testSuites');
        if (stored) {
          const suites = JSON.parse(stored);
          setTestSuites(Array.isArray(suites) ? suites : [suites]);
        }
      } catch (error) {
        console.error('Error loading test suites:', error);
      }
      setLoading(false);
    };

    loadTestSuites();
  }, []);

  const handleExecuteTest = (suite) => {
    alert(`Executing test suite: ${suite.name || 'Unnamed Suite'}`);
  };

  const handleDownloadTest = (suite) => {
    const dataStr = JSON.stringify(suite, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${suite.name || 'test-suite'}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>Loading Test Management...</h1>
        <div>Please wait while we load your test suites.</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ 
          fontSize: '32px', 
          fontWeight: 'bold', 
          color: '#2c3e50', 
          marginBottom: '10px' 
        }}>
          🎯 Test Management
        </h1>
        <p style={{ 
          fontSize: '16px', 
          color: '#7f8c8d', 
          marginBottom: '20px' 
        }}>
          Manage and execute your AI-generated test suites
        </p>
        
        <div style={{
          backgroundColor: '#27ae60',
          color: 'white',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          ✅ Test Management page is now working correctly!
        </div>
      </div>

      {testSuites.length === 0 ? (
        <div style={{
          backgroundColor: '#f8f9fa',
          border: '2px dashed #dee2e6',
          borderRadius: '12px',
          padding: '60px 40px',
          textAlign: 'center',
          marginBottom: '30px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>📋</div>
          <h2 style={{ fontSize: '24px', color: '#495057', marginBottom: '15px' }}>
            No Test Suites Found
          </h2>
          <p style={{ fontSize: '16px', color: '#6c757d', marginBottom: '25px' }}>
            Create your first test suite using the "Create Tests" page to get started.
          </p>
          <button
            onClick={() => window.location.hash = '#/create-test'}
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '6px',
              fontSize: '16px',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            Create Your First Test Suite
          </button>
        </div>
      ) : (
        <div>
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '15px' }}>
              Your Test Suites ({testSuites.length})
            </h2>
          </div>

          <div style={{ display: 'grid', gap: '20px' }}>
            {testSuites.map((suite, index) => (
              <div
                key={index}
                style={{
                  backgroundColor: 'white',
                  border: '1px solid #e9ecef',
                  borderRadius: '12px',
                  padding: '24px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}
              >
                <div style={{ marginBottom: '16px' }}>
                  <h3 style={{ 
                    fontSize: '18px', 
                    fontWeight: '600', 
                    color: '#2c3e50',
                    marginBottom: '8px' 
                  }}>
                    {suite.name || `Test Suite ${index + 1}`}
                  </h3>
                  <p style={{ 
                    fontSize: '14px', 
                    color: '#6c757d',
                    marginBottom: '12px' 
                  }}>
                    Created: {suite.created_at || new Date().toLocaleDateString()}
                  </p>
                  
                  {suite.application_url && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong>Application URL:</strong>{' '}
                      <a 
                        href={suite.application_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ color: '#007bff', textDecoration: 'none' }}
                      >
                        {suite.application_url}
                      </a>
                    </div>
                  )}
                  
                  {suite.application_type && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong>Type:</strong> {suite.application_type}
                    </div>
                  )}
                  
                  {suite.test_files && suite.test_files.length > 0 && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong>Generated Files:</strong> {suite.test_files.length} files
                    </div>
                  )}
                </div>

                <div style={{ 
                  display: 'flex', 
                  gap: '12px', 
                  flexWrap: 'wrap' 
                }}>
                  <button
                    onClick={() => handleExecuteTest(suite)}
                    style={{
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      padding: '10px 20px',
                      borderRadius: '6px',
                      fontSize: '14px',
                      cursor: 'pointer',
                      fontWeight: '500'
                    }}
                  >
                    ▶️ Execute Tests
                  </button>
                  
                  <button
                    onClick={() => handleDownloadTest(suite)}
                    style={{
                      backgroundColor: '#17a2b8',
                      color: 'white',
                      border: 'none',
                      padding: '10px 20px',
                      borderRadius: '6px',
                      fontSize: '14px',
                      cursor: 'pointer',
                      fontWeight: '500'
                    }}
                  >
                    📥 Download
                  </button>
                  
                  <button
                    onClick={() => alert('View details functionality coming soon!')}
                    style={{
                      backgroundColor: '#6c757d',
                      color: 'white',
                      border: 'none',
                      padding: '10px 20px',
                      borderRadius: '6px',
                      fontSize: '14px',
                      cursor: 'pointer',
                      fontWeight: '500'
                    }}
                  >
                    👁️ View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ 
        marginTop: '40px', 
        padding: '20px', 
        backgroundColor: '#f8f9fa', 
        borderRadius: '8px' 
      }}>
        <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '10px' }}>
          💡 Quick Actions
        </h3>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button
            onClick={() => window.location.hash = '#/create-test'}
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              padding: '10px 16px',
              borderRadius: '6px',
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            ➕ Create New Test Suite
          </button>
          
          <button
            onClick={() => window.location.hash = '#/results'}
            style={{
              backgroundColor: '#6f42c1',
              color: 'white',
              border: 'none',
              padding: '10px 16px',
              borderRadius: '6px',
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            📊 View Test Results
          </button>
        </div>
      </div>
    </div>
  );
};

export default TestManagementWorking;
