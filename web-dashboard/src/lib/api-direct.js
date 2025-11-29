/**
 * Direct API Service - Bypasses authentication for testing
 * Temporary solution to test functionality without auth issues
 */

class DirectApiService {
  constructor() {
    this.baseUrl = '';  // Use relative URLs for proxy
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    console.log(`🔗 Direct API request: ${options.method || 'GET'} ${url}`);

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`✅ Direct API response:`, data);
      return data;
    } catch (error) {
      console.error(`❌ Direct API request failed:`, error);
      throw error;
    }
  }

  // Get test cases for a test suite (direct endpoint)
  async getTestCasesForSuite(suiteId) {
    return this.request(`/api/v1/test-suites/${suiteId}/test-cases-direct`);
  }

  // Execute test suite (direct endpoint)
  async executeTestSuite(suiteId, config = {}) {
    return this.request('/api/v1/test/executions-direct', {
      method: 'POST',
      body: JSON.stringify({
        test_suite_id: suiteId,
        environment: config.environment || 'staging',
        browser: config.browser || 'chrome',
        parallel: config.parallel || false
      }),
    });
  }

  // Get execution status (using real backend endpoint)
  async getExecutionStatus(executionId) {
    return this.request(`/api/v1/test/execution-status-direct/${executionId}`);
  }

  // Execute single test case (using real backend endpoint)
  async executeTestCase(testCaseId) {
    return this.request('/api/v1/test/execute-case-direct', {
      method: 'POST',
      body: JSON.stringify({
        test_case_id: testCaseId
      }),
    });
  }
}

// Create and export instance
const directApiService = new DirectApiService();
export default directApiService;
