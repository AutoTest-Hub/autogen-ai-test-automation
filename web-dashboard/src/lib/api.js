/**
 * API Service for AI Test Automation SaaS Platform
 * Handles all communication with the backend API
 */

class ApiService {
  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    this.authToken = localStorage.getItem('authToken')
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
    const response = await this.request('/api/v1/auth/login', {
      method: 'POST',
      body: credentials,
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

  logout() {
    this.setAuthToken(null)
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

  // Utility methods
  isAuthenticated() {
    return !!this.authToken
  }

  getToken() {
    return this.authToken
  }
}

export const apiService = new ApiService()
export default apiService
