import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'

// Test each import one by one to find the problematic one
import { DeploymentProvider, useDeployment } from './components/DeploymentConfig'
import { apiService } from './lib/api'

function TestApp() {
  return (
    <DeploymentProvider>
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">AI Test Automation Platform</h1>
          <p className="text-gray-600">Testing component loading...</p>
        </div>
      </div>
    </DeploymentProvider>
  )
}

export default TestApp
