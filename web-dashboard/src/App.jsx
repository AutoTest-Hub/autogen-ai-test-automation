import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import './App.css'

// Deployment Configuration
import { DeploymentProvider, useDeployment, FeatureGate, getNavigationItems } from './components/DeploymentConfig'

// Components
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import Applications from './components/Applications'
import CreateTest from './components/CreateTest'
import CreateTestAdvanced from './components/CreateTestAdvanced'
import TestExecution from './components/TestExecution'
import TestResults from './components/TestResults'
import Requirements from './components/Requirements'
import Settings from './components/Settings'
import Login from './components/Login'
import LoginEnhanced from './components/LoginEnhanced'

// API Service
import { apiService } from './lib/api'

// Enhanced App Component with Deployment Awareness
function AppContent() {
  const { deploymentMode, features, branding, loading: deploymentLoading, isSaaS, isOnPrem } = useDeployment()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [systemInfo, setSystemInfo] = useState(null)

  useEffect(() => {
    // Set API base URL based on deployment mode
    const apiBaseUrl = isSaaS 
      ? import.meta.env.VITE_API_URL || 'http://localhost:8000'
      : import.meta.env.VITE_ONPREM_API_URL || 'http://localhost:8000'
    
    apiService.setBaseUrl(apiBaseUrl)
  }, [deploymentMode, isSaaS])

  useEffect(() => {
    // Check for existing authentication
    const token = localStorage.getItem('auth_token')
    if (token) {
      apiService.setAuthToken(token)
      // Verify token is still valid and get system info
      Promise.all([
        apiService.getCurrentUser(),
        apiService.getSystemInfo()
      ])
        .then(([userData, sysInfo]) => {
          setUser(userData)
          setSystemInfo(sysInfo)
        })
        .catch(() => {
          localStorage.removeItem('auth_token')
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
      localStorage.setItem('auth_token', response.access_token)
      apiService.setAuthToken(response.access_token)
      setUser(response.user)
      
      // Get system info after login
      try {
        const sysInfo = await apiService.getSystemInfo()
        setSystemInfo(sysInfo)
      } catch (error) {
        console.warn('Could not fetch system info:', error)
      }
      
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    apiService.setAuthToken(null)
    setUser(null)
    setSystemInfo(null)
  }

  // Show loading while deployment config is loading
  if (deploymentLoading || loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full"
        />
        <span className="ml-3 text-muted-foreground">
          {deploymentLoading ? 'Initializing platform...' : 'Loading...'}
        </span>
      </div>
    )
  }

  // Show enhanced login for authenticated users
  if (!user) {
    return <LoginEnhanced onLogin={handleLogin} />
  }

  // Get navigation items based on deployment features
  const navigationItems = getNavigationItems(features)

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
                  
                  <FeatureGate feature="billing">
                    <span className="text-sm text-muted-foreground">
                      API Usage: {user?.api_calls_used || 0} / {user?.api_calls_limit || 1000}
                    </span>
                  </FeatureGate>
                  
                  <FeatureGate feature="auditCompliance">
                    <span className="text-sm text-muted-foreground">
                      Compliance: SOC 2 Type II
                    </span>
                  </FeatureGate>
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
                      <CreateTestAdvanced 
                        user={user} 
                        deploymentMode={deploymentMode}
                        onNavigate={(page) => window.location.hash = `#/${page}`} 
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
                  
                  {/* SaaS-specific routes */}
                  <FeatureGate feature="billing">
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
                  </FeatureGate>
                  
                  <FeatureGate feature="subscriptionPlans">
                    <Route path="/subscription" element={
                      <motion.div
                        key="subscription"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                      >
                        <div className="p-6 bg-card rounded-lg">
                          <h2 className="text-2xl font-bold mb-4">Subscription Plans</h2>
                          <p className="text-muted-foreground">Manage your subscription and upgrade options.</p>
                        </div>
                      </motion.div>
                    } />
                  </FeatureGate>
                  
                  {/* OnPrem-specific routes */}
                  <FeatureGate feature="ldapIntegration">
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
                  </FeatureGate>
                  
                  <FeatureGate feature="auditCompliance">
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
                  </FeatureGate>
                  
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

// Main App Component with Deployment Provider
function App() {
  return (
    <DeploymentProvider>
      <AppContent />
    </DeploymentProvider>
  )
}

export default App
