import React from 'react';

const TestManagementTest = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Test Management - WORKING!</h1>
      <p>This is a simple test component to verify routing works.</p>
      <div style={{ 
        backgroundColor: '#f0f8ff', 
        padding: '20px', 
        borderRadius: '8px',
        border: '2px solid #007bff'
      }}>
        <h2>🎉 Success!</h2>
        <p>If you can see this page, the routing is working correctly.</p>
        <p>The issue was likely with the TestManagementBasic component, not the routing itself.</p>
      </div>
    </div>
  );
};

export default TestManagementTest;
