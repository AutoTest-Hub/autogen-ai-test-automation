import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import './App.css'

// Components
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import Applications from './components/Applications'
import CreateTestRealTime from './components/CreateTestRealTime'
import CreateTestRealTimeFixed from './components/CreateTestRealTimeFixed'
import CreateTestWorking from './components/CreateTestWorking'
import TestManagementNew from './components/TestManagementNew'
import TestManagementDynamic from './components/TestManagementDynamic'
import TestExecution from './components/TestExecution'
import TestResults from './components/TestResultsSimple'
import Requirements from './components/RequirementsSimple'
import Settings from './components/Settings'
import LoginSimple from './components/LoginSimple'

// API Service
import { apiService } from './lib/api'

// Simplified deployment configuration
const DEPLOYMENT_MODES = {
  SAAS: 'SaaS',
  ONPREM: 'OnPrem'
}

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [systemInfo, setSystemInfo] = useState(null)
  const [deploymentMode, setDeploymentMode] = useState(DEPLOYMENT_MODES.SAAS)
  const [features, setFeatures] = useState({})
  const [branding, setBranding] = useState({
    title: 'AI Test Automation Platform',
    subtitle: 'Enterprise-grade test automation powered by AI',
    primaryColor: '#3b82f6',
    secondaryColor: '#1e40af'
  })

  // Fetch system info and set deployment configuration
  useEffect(() => {
    const fetchSystemInfo = async () => {
      try {
        // Get API base URL
        const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

        // Fetch system info
        const response = await fetch(`${apiBaseUrl}/api/v1/system/info`)
        if (response.ok) {
          const sysInfo = await response.json()
          setSystemInfo(sysInfo)
          setDeploymentMode(sysInfo.deployment_mode)
          setFeatures(sysInfo.features || {})
          
          // Set branding based on deployment mode
          if (sysInfo.branding) {
            setBranding({
              title: sysInfo.branding.name || 'AI Test Automation Platform',
              subtitle: sysInfo.branding.edition || 'Enterprise-grade test automation',
              primaryColor: sysInfo.branding.primary_color || '#3b82f6',
              secondaryColor: sysInfo.branding.secondary_color || '#1e40af'
            })
          }
        }
      } catch (error) {
        console.warn('Could not fetch system info:', error)
        // Use defaults
      }
    }

    fetchSystemInfo()
  }, [])

  // Check for existing authentication
  useEffect(() => {
    const token = localStorage.getItem('authToken')
    if (token) {
      apiService.setAuthToken(token)
      // Verify token is still valid
      apiService.getCurrentUser()
        .then((userData) => {
          setUser(userData)
        })
        .catch(() => {
          localStorage.removeItem('authToken')
          apiService.setAuthToken(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const handleLogin = async (credentials) => {
    try {
      const response = await apiService.login(credentials)
      localStorage.setItem('authToken', response.access_token)
      apiService.setAuthToken(response.access_token)
      
      // Get user data after successful login
      const userData = await apiService.getCurrentUser()
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: error.message || 'Login failed' }
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('authToken')
    apiService.setAuthToken(null)
    setUser(null)
  }

  // Show loading while initializing
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full"
        />
        <span className="ml-3 text-muted-foreground">Loading application...</span>
      </div>
    )
  }

  // Show login for unauthenticated users
  if (!user) {
    return <LoginSimple onLogin={handleLogin} />
  }

  // Get navigation items based on deployment features
  const getNavigationItems = () => {
    const baseItems = [
      { id: 'dashboard', label: 'Dashboard', icon: 'LayoutDashboard', path: '/dashboard' },
      { id: 'applications', label: 'Applications', icon: 'Globe', path: '/applications' },
      { id: 'create-test', label: 'Create Tests', icon: 'Plus', path: '/create-test' },
      { id: 'test-management', label: 'Test Management', icon: 'Settings', path: '/manage-tests' },
      { id: 'test-results', label: 'Test Results', icon: 'BarChart3', path: '/results' },
      { id: 'requirements', label: 'Requirements', icon: 'FileText', path: '/requirements' }
    ]

    const conditionalItems = []

    // SaaS-specific items
    if (features.billing) {
      conditionalItems.push({ id: 'billing', label: 'Billing', icon: 'CreditCard', path: '/billing' })
    }

    // OnPrem-specific items
    if (features.ldapIntegration) {
      conditionalItems.push({ id: 'users', label: 'User Management', icon: 'Users', path: '/users' })
    }

    if (features.auditCompliance) {
      conditionalItems.push({ id: 'audit', label: 'Audit Logs', icon: 'Shield', path: '/audit' })
    }

    // Settings
    conditionalItems.push({ id: 'settings', label: 'Settings', icon: 'Settings', path: '/settings' })

    return [...baseItems, ...conditionalItems]
  }

  const navigationItems = getNavigationItems()
  const isSaaS = deploymentMode === DEPLOYMENT_MODES.SAAS

  return (
    <Router>
      <div 
        className="min-h-screen bg-background text-foreground"
        style={{
          '--primary-color': branding.primaryColor,
          '--secondary-color': branding.secondaryColor
        }}
      >
        <div className="flex">
          <Sidebar 
            open={sidebarOpen} 
            onToggle={() => setSidebarOpen(!sidebarOpen)}
            user={user}
            onLogout={handleLogout}
            navigationItems={navigationItems}
            branding={branding}
            deploymentMode={deploymentMode}
          />
          
          <main className={`flex-1 transition-all duration-300 ${
            sidebarOpen ? 'ml-64' : 'ml-16'
          }`}>
            {/* Deployment Mode Header */}
            <div className="bg-muted/30 border-b px-6 py-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    isSaaS ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {deploymentMode} Edition
                  </span>
                  
                  {features.billing && (
                    <span className="text-sm text-muted-foreground">
                      API Usage: {user?.api_calls_used || 0} / {user?.api_calls_limit || 1000}
                    </span>
                  )}
                  
                  {features.auditCompliance && (
                    <span className="text-sm text-muted-foreground">
                      Compliance: SOC 2 Type II
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-2">
                  {systemInfo && (
                    <span className="text-xs text-muted-foreground">
                      v{systemInfo.version}
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="p-6">
              <AnimatePresence mode="wait">
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  
                  <Route path="/dashboard" element={
                    <motion.div
                      key="dashboard"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Dashboard 
                        user={user} 
                        systemInfo={systemInfo}
                        deploymentMode={deploymentMode}
                        onNavigate={(page) => window.location.hash = `#/${page}`} 
                      />
                    </motion.div>
                  } />
                  
                  <Route path="/applications" element={
                    <motion.div
                      key="applications"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Applications 
                        user={user} 
                        deploymentMode={deploymentMode}
                        onNavigate={(page) => window.location.hash = `#/${page}`} 
                      />
                    </motion.div>
                  } />
                  
                  <Route path="/create-test" element={
                    <motion.div
                      key="create-test"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <CreateTestWorking
                        user={user}
                        deploymentMode={deploymentMode}
                        apiService={apiService}
                        onNavigate={(page) => window.location.hash = `#/${page}`}
                      />
                    </motion.div>
                  } />

                  <Route path="/manage-tests" element={
                    <motion.div
                      key="manage-tests"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <TestManagementDynamic
                        user={user}
                        deploymentMode={deploymentMode}
                      />
                    </motion.div>
                  } />
                  
                  <Route path="/execute" element={
                    <motion.div
                      key="execute"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <TestExecution user={user} deploymentMode={deploymentMode} />
                    </motion.div>
                  } />
                  
                  <Route path="/results" element={
                    <motion.div
                      key="results"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <TestResults user={user} deploymentMode={deploymentMode} />
                    </motion.div>
                  } />
                  
                  <Route path="/requirements" element={
                    <motion.div
                      key="requirements"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Requirements user={user} deploymentMode={deploymentMode} />
                    </motion.div>
                  } />
                  
                  {/* Conditional routes based on features */}
                  {features.billing && (
                    <Route path="/billing" element={
                      <motion.div
                        key="billing"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                      >
                        <div className="p-6 bg-card rounded-lg">
                          <h2 className="text-2xl font-bold mb-4">Billing & Usage</h2>
                          <p className="text-muted-foreground">Billing management interface for SaaS deployment.</p>
                        </div>
                      </motion.div>
                    } />
                  )}
                  
                  {features.ldapIntegration && (
                    <Route path="/users" element={
                      <motion.div
                        key="users"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                      >
                        <div className="p-6 bg-card rounded-lg">
                          <h2 className="text-2xl font-bold mb-4">User Management</h2>
                          <p className="text-muted-foreground">Manage users and LDAP integration for OnPrem deployment.</p>
                        </div>
                      </motion.div>
                    } />
                  )}
                  
                  {features.auditCompliance && (
                    <Route path="/audit" element={
                      <motion.div
                        key="audit"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                      >
                        <div className="p-6 bg-card rounded-lg">
                          <h2 className="text-2xl font-bold mb-4">Audit Logs</h2>
                          <p className="text-muted-foreground">View comprehensive audit logs and compliance reports.</p>
                        </div>
                      </motion.div>
                    } />
                  )}
                  
                  <Route path="/settings" element={
                    <motion.div
                      key="settings"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Settings 
                        user={user} 
                        systemInfo={systemInfo}
                        deploymentMode={deploymentMode}
                        features={features}
                      />
                    </motion.div>
                  } />
                </Routes>
              </AnimatePresence>
            </div>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App
