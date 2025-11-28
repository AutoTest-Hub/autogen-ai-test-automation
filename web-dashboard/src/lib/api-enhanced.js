/**
 * Enhanced API Service for AI Test Automation SaaS Platform
 * Includes hybrid test management and duplicate detection capabilities
 */

class EnhancedApiService {
  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    this.authToken = localStorage.getItem('authToken')
  }

  setBaseUrl(url) {
    this.baseUrl = url
  }

  setAuthToken(token) {
    this.authToken = token
    if (token) {
      localStorage.setItem('authToken', token)
    } else {
      localStorage.removeItem('authToken')
    }
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    if (this.authToken) {
      config.headers.Authorization = `Bearer ${this.authToken}`
    }

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body)
    }

    try {
      const response = await fetch(url, config)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.detail || `HTTP error! status: ${response.status}`)
      }

      return data
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Authentication
  async login(credentials) {
    const loginData = {
      username: credentials.email || credentials.username,
      password: credentials.password
    }
    
    const response = await this.request('/api/v1/auth/login', {
      method: 'POST',
      body: loginData,
    })
    
    if (response.access_token) {
      this.setAuthToken(response.access_token)
    }
    
    return response
  }

  async register(userData) {
    return this.request('/api/v1/auth/register', {
      method: 'POST',
      body: userData,
    })
  }

  async getCurrentUser() {
    return this.request('/api/v1/auth/me')
  }

  async getSystemInfo() {
    return this.request('/api/v1/system/info')
  }

  logout() {
    this.setAuthToken(null)
  }

  // Applications
  async getApplications() {
    return this.request('/api/v1/applications')
  }

  async createApplication(appData) {
    return this.request('/api/v1/applications', {
      method: 'POST',
      body: appData
    })
  }

  // Test Creation
  async createTest(testConfig) {
    return this.request('/api/v1/create-test', {
      method: 'POST',
      body: testConfig,
    })
  }

  async getTestSuites() {
    return this.request('/api/v1/tests')
  }

  async getTestSuite(suiteId) {
    return this.request(`/api/v1/test-suite/${suiteId}`)
  }

  async getTestSuiteTests(suiteId) {
    return this.request(`/api/v1/test-suite/${suiteId}/tests`)
  }

  // Agent Job Monitoring
  async getAgentJobStatus(jobId) {
    return this.request(`/api/v1/agent-job/${jobId}`)
  }

  // Hybrid Test Management - NEW ENDPOINTS
  async checkForDuplicates(applicationId, testName, testDescription, similarityThreshold = 0.8) {
    return this.request('/api/v1/hybrid/check-duplicates', {
      method: 'POST',
      body: {
        application_id: applicationId,
        test_name: testName,
        test_description: testDescription,
        similarity_threshold: similarityThreshold
      }
    })
  }

  async analyzeCoverage(applicationId, testDescription) {
    return this.request('/api/v1/hybrid/analyze-coverage', {
      method: 'POST',
      body: {
        application_id: applicationId,
        test_description: testDescription
      }
    })
  }

  async updateExistingTest(testId, updateData) {
    return this.request('/api/v1/hybrid/update-test', {
      method: 'PUT',
      body: {
        test_id: testId,
        ...updateData
      }
    })
  }

  async getApplicationTestSummary(applicationId) {
    return this.request(`/api/v1/hybrid/application/${applicationId}/test-summary`)
  }

  // Test Execution
  async executeTest(testConfig) {
    return this.request('/api/v1/test/execute', {
      method: 'POST',
      body: testConfig,
    })
  }

  async getExecutionStatus(executionId) {
    return this.request(`/api/v1/test/execution/${executionId}`)
  }

  async getExecutionResults(executionId) {
    return this.request(`/api/v1/test/execution/${executionId}/results`)
  }

  async stopExecution(executionId) {
    return this.request(`/api/v1/test/execution/${executionId}/stop`, {
      method: 'POST'
    })
  }

  async getTestStatus(executionId) {
    return this.request(`/api/v1/test/status/${executionId}`)
  }

  async getTestResults(executionId) {
    return this.request(`/api/v1/test/results/${executionId}`)
  }

  async getTestExecutions() {
    return this.request('/api/v1/test/executions')
  }

  // Requirements
  async getRequirementsTemplates() {
    return this.request('/api/v1/requirements/templates')
  }

  async getRequirementsTemplate(templateName) {
    return this.request(`/api/v1/requirements/template/${templateName}`)
  }

  async validateRequirements(requirements) {
    return this.request('/api/v1/requirements/validate', {
      method: 'POST',
      body: requirements,
    })
  }

  // Advanced AI Features
  async selfHealTest(testData) {
    return this.request('/api/v1/ai/self-heal', {
      method: 'POST',
      body: testData,
    })
  }

  async prioritizeTests(testFiles) {
    return this.request('/api/v1/ai/prioritize-tests', {
      method: 'POST',
      body: { test_files: testFiles },
    })
  }

  async generateCrossBrowserPlan(planData) {
    return this.request('/api/v1/ai/cross-browser-plan', {
      method: 'POST',
      body: planData,
    })
  }

  async predictPerformance(performanceData) {
    return this.request('/api/v1/ai/predict-performance', {
      method: 'POST',
      body: performanceData,
    })
  }

  // Health Check
  async getHealth() {
    return this.request('/api/v1/health')
  }

  // Dashboard Stats
  async getDashboardStats() {
    return this.request('/api/v1/dashboard/stats')
  }

  // Utility methods
  isAuthenticated() {
    return !!this.authToken
  }

  getToken() {
    return this.authToken
  }

  // Real-time monitoring utilities
  createPollingInterval(callback, interval = 2000) {
    return setInterval(callback, interval)
  }

  clearPollingInterval(intervalId) {
    if (intervalId) {
      clearInterval(intervalId)
    }
  }

  // Notification helpers
  async sendNotification(type, message, data = {}) {
    // This could be extended to send notifications to external services
    console.log(`[${type.toUpperCase()}] ${message}`, data)
    
    // Could integrate with browser notifications
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(message, {
        icon: '/favicon.ico',
        tag: type,
        data: data
      })
    }
  }

  async requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      return await Notification.requestPermission()
    }
    return Notification.permission
  }
}

export const enhancedApiService = new EnhancedApiService()
export default enhancedApiService
