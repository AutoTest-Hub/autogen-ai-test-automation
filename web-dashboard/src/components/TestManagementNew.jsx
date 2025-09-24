import React, { useState, useEffect } from 'react';

const TestManagementNew = () => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading test data
    setTimeout(() => {
      setTests([
        {
          id: 1,
          name: 'HRMS Login Flow Test',
          status: 'Completed',
          lastRun: '2024-09-24 14:30',
          success: true,
          coverage: '95%'
        },
        {
          id: 2,
          name: 'Employee Management Test',
          status: 'Running',
          lastRun: '2024-09-24 15:45',
          success: null,
          coverage: '87%'
        },
        {
          id: 3,
          name: 'Leave Application Test',
          status: 'Failed',
          lastRun: '2024-09-24 13:15',
          success: false,
          coverage: '78%'
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const handleRunTest = (testId) => {
    setTests(tests.map(test => 
      test.id === testId 
        ? { ...test, status: 'Running', lastRun: new Date().toLocaleString() }
        : test
    ));
  };

  const handleDeleteTest = (testId) => {
    setTests(tests.filter(test => test.id !== testId));
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '28px', marginBottom: '20px' }}>🎯 Test Management</h1>
        <div style={{ fontSize: '18px', color: '#666' }}>Loading tests...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 'bold', color: '#2c3e50', marginBottom: '10px' }}>
          🎯 Test Management
        </h1>
        <p style={{ fontSize: '16px', color: '#666', marginBottom: '20px' }}>
          Manage and execute your AI-generated test suites
        </p>
        
        <div style={{ display: 'flex', gap: '15px', marginBottom: '30px' }}>
          <button 
            onClick={() => window.location.href = '/create-test'}
            style={{ 
              backgroundColor: '#007bff', 
              color: 'white', 
              padding: '12px 24px', 
              border: 'none', 
              borderRadius: '6px', 
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '500'
            }}
          >
            + Create New Test
          </button>
          <button 
            style={{ 
              backgroundColor: '#28a745', 
              color: 'white', 
              padding: '12px 24px', 
              border: 'none', 
              borderRadius: '6px', 
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '500'
            }}
          >
            Run All Tests
          </button>
        </div>
      </div>

      <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #eee' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#2c3e50', margin: 0 }}>
            Test Suites ({tests.length})
          </h2>
        </div>
        
        <div style={{ padding: '0' }}>
          {tests.map((test, index) => (
            <div 
              key={test.id}
              style={{ 
                padding: '20px', 
                borderBottom: index < tests.length - 1 ? '1px solid #eee' : 'none',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '18px', fontWeight: '500', color: '#2c3e50', margin: '0 0 8px 0' }}>
                  {test.name}
                </h3>
                <div style={{ display: 'flex', gap: '20px', fontSize: '14px', color: '#666' }}>
                  <span>Last Run: {test.lastRun}</span>
                  <span>Coverage: {test.coverage}</span>
                </div>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <span 
                  style={{ 
                    padding: '4px 12px', 
                    borderRadius: '20px', 
                    fontSize: '12px', 
                    fontWeight: '500',
                    backgroundColor: 
                      test.status === 'Completed' ? '#d4edda' :
                      test.status === 'Running' ? '#fff3cd' : '#f8d7da',
                    color: 
                      test.status === 'Completed' ? '#155724' :
                      test.status === 'Running' ? '#856404' : '#721c24'
                  }}
                >
                  {test.status}
                </span>
                
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button 
                    onClick={() => handleRunTest(test.id)}
                    style={{ 
                      backgroundColor: '#17a2b8', 
                      color: 'white', 
                      padding: '6px 12px', 
                      border: 'none', 
                      borderRadius: '4px', 
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}
                  >
                    Run
                  </button>
                  <button 
                    style={{ 
                      backgroundColor: '#6c757d', 
                      color: 'white', 
                      padding: '6px 12px', 
                      border: 'none', 
                      borderRadius: '4px', 
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}
                  >
                    Edit
                  </button>
                  <button 
                    onClick={() => handleDeleteTest(test.id)}
                    style={{ 
                      backgroundColor: '#dc3545', 
                      color: 'white', 
                      padding: '6px 12px', 
                      border: 'none', 
                      borderRadius: '4px', 
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {tests.length === 0 && (
        <div style={{ 
          textAlign: 'center', 
          padding: '60px 20px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          marginTop: '20px'
        }}>
          <h3 style={{ fontSize: '20px', color: '#6c757d', marginBottom: '10px' }}>No tests found</h3>
          <p style={{ color: '#6c757d', marginBottom: '20px' }}>Create your first test to get started</p>
          <button 
            onClick={() => window.location.href = '/create-test'}
            style={{ 
              backgroundColor: '#007bff', 
              color: 'white', 
              padding: '12px 24px', 
              border: 'none', 
              borderRadius: '6px', 
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Create First Test
          </button>
        </div>
      )}
    </div>
  );
};

export default TestManagementNew;
