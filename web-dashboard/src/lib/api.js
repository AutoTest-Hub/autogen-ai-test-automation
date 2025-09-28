/**
 * API Service for AI Test Automation SaaS Platform
 * Handles all communication with the backend API
 */

class ApiService {
  constructor() {
    // Use empty string for relative URLs when VITE_API_URL is empty (uses vite proxy)
    this.baseUrl = import.meta.env.VITE_API_URL || ''
    this.authToken = null
    // Initialize auth token from localStorage if available
    if (typeof window !== 'undefined' && window.localStorage) {
      this.authToken = localStorage.getItem('authToken')
    }
  }

  setBaseUrl(url) {
    this.baseUrl = url
  }

  setAuthToken(token) {
    this.authToken = token
    if (typeof window !== 'undefined' && window.localStorage) {
      if (token) {
        localStorage.setItem('authToken', token)
      } else {
        localStorage.removeItem('authToken')
      }
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
    // Convert email to username for backend compatibility
    const loginData = {
      username: credentials.email || credentials.username,
      password: credentials.password
    }
    
    console.log('Login attempt:', { username: loginData.username, hasPassword: !!loginData.password })
    console.log('API Base URL:', this.baseUrl)
    
    try {
      const response = await this.request('/api/v1/auth/login', {
        method: 'POST',
        body: loginData,
      })
      
      console.log('Login response:', response)
      
      if (response.access_token) {
        this.setAuthToken(response.access_token)
      }
      
      return response
    } catch (error) {
      console.error('Login error in API service:', error)
      throw error
    }
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

  // Test Execution
  async executeTest(testConfig) {
    return this.request('/api/v1/test/executions', {
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

  // Applications
  async getApplications() {
    return this.request('/api/v1/applications')
  }

  async createApplication(applicationData) {
    return this.request('/api/v1/applications', {
      method: 'POST',
      body: applicationData,
    })
  }

  // Test Creation
  async createTest(testConfig) {
    return this.request('/api/v1/create-test', {
      method: 'POST',
      body: testConfig,
    })
  }

  async getAgentJobStatus(jobId) {
    return this.request(`/api/v1/agent-jobs/${jobId}/status`)
  }

  async getAgentJobTests(jobId) {
    return this.request(`/api/v1/agent-jobs/${jobId}/tests`)
  }

  // Test Management
  async getTests() {
    return this.request('/api/v1/tests')
  }

  async getTestSuites() {
    return this.request('/api/v1/tests')
  }

  // Requirements Management
  async validateRequirements(requirementsData) {
    return this.request('/api/v1/requirements/validate', {
      method: 'POST',
      body: requirementsData,
    })
  }

  async uploadRequirementsFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const url = `${this.baseUrl}/api/v1/requirements/upload`
    const config = {
      method: 'POST',
      headers: {},
      body: formData,
    }

    if (this.authToken) {
      config.headers.Authorization = `Bearer ${this.authToken}`
    }

    try {
      const response = await fetch(url, config)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.detail || `HTTP error! status: ${response.status}`)
      }

      return data
    } catch (error) {
      console.error('File upload failed:', error)
      throw error
    }
  }

  async getRequirementsTemplates() {
    return this.request('/api/v1/requirements/templates')
  }

  // Duplicate Prevention
  async checkForDuplicates(applicationId, testName, testDescription, requirementsData = null) {
    return this.request('/api/v1/tests/check-duplicates', {
      method: 'POST',
      body: {
        application_id: applicationId,
        test_name: testName,
        test_description: testDescription,
        requirements_data: requirementsData,
      },
    })
  }

  async getUpdateStrategy(existingSuiteId, newRequirements = null) {
    return this.request('/api/v1/tests/update-strategy', {
      method: 'POST',
      body: {
        existing_suite_id: existingSuiteId,
        new_requirements: newRequirements,
      },
    })
  }

  async getRecentTestSuites(applicationId, hours = 24) {
    return this.request(`/api/v1/tests/recent/${applicationId}?hours=${hours}`)
  }

  async updateExistingTestSuite(suiteId, applicationId, testName, testDescription, requirementsData = null) {
    return this.request(`/api/v1/tests/${suiteId}/update`, {
      method: 'PUT',
      body: {
        application_id: applicationId,
        test_name: testName,
        test_description: testDescription,
        requirements_data: requirementsData,
      },
    })
  }

  // Test Editing and Management
  async getTestCases(suiteId) {
    return this.request(`/api/v1/test-suites/${suiteId}/test-cases`)
  }

  async updateTestSuite(suiteId, suiteData) {
    return this.request(`/api/v1/test-suites/${suiteId}`, {
      method: 'PUT',
      body: suiteData,
    })
  }

  async updateTestCase(testCaseId, testCaseData) {
    return this.request(`/api/v1/test-cases/${testCaseId}`, {
      method: 'PUT',
      body: testCaseData,
    })
  }

  async deleteTestCase(testCaseId) {
    return this.request(`/api/v1/test-cases/${testCaseId}`, {
      method: 'DELETE',
    })
  }

  async createTestCase(suiteId, testCaseData) {
    return this.request(`/api/v1/test-suites/${suiteId}/test-cases`, {
      method: 'POST',
      body: testCaseData,
    })
  }
}

export const apiService = new ApiService()
export default apiService
