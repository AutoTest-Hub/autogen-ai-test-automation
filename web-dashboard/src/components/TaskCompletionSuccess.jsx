import React, { useState, useEffect } from 'react';
import { CheckCircle, Download, Play, Eye, FileText, Code, TestTube, AlertCircle } from 'lucide-react';
import { apiService } from '../lib/api';

const TaskCompletionSuccess = ({ taskData, onClose, onNavigate }) => {
  const [activeTab, setActiveTab] = useState('summary');
  const [testFiles, setTestFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch generated test files and artifacts
    fetchTestArtifacts();
  }, [taskData]);

  const fetchTestArtifacts = async () => {
    try {
      setLoading(true);
      // Mock test artifacts - in real implementation, fetch from API
      const mockArtifacts = [
        {
          id: 1,
          name: 'hrms_login_test.py',
          type: 'test_file',
          size: '2.4 KB',
          description: 'Login functionality test suite',
          content: `# HRMS Login Test Suite
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestHRMSLogin:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://opensource-demo.orangehrmlive.com")
    
    def test_valid_login(self):
        # Test valid login credentials
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        
        username_field.send_keys("Admin")
        password_field.send_keys("admin123")
        login_button.click()
        
        # Verify successful login
        dashboard = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "oxd-topbar-header-breadcrumb"))
        )
        assert dashboard.is_displayed()
    
    def teardown_method(self):
        self.driver.quit()`
        },
        {
          id: 2,
          name: 'hrms_employee_management_test.py',
          type: 'test_file',
          size: '3.8 KB',
          description: 'Employee management functionality tests',
          content: `# HRMS Employee Management Test Suite
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from page_objects.employee_page import EmployeePage

class TestEmployeeManagement:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.employee_page = EmployeePage(self.driver)
    
    def test_add_employee(self):
        # Test adding new employee
        self.employee_page.navigate_to_add_employee()
        self.employee_page.fill_employee_details("John", "Doe", "12345")
        self.employee_page.save_employee()
        
        # Verify employee was added
        assert self.employee_page.is_employee_saved()
    
    def teardown_method(self):
        self.driver.quit()`
        },
        {
          id: 3,
          name: 'page_objects.py',
          type: 'page_object',
          size: '1.9 KB',
          description: 'Page Object Model classes',
          content: `# Page Object Model for HRMS Application
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

class LoginPage(BasePage):
    USERNAME_FIELD = (By.NAME, "username")
    PASSWORD_FIELD = (By.NAME, "password")
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit']")
    
    def login(self, username, password):
        self.driver.find_element(*self.USERNAME_FIELD).send_keys(username)
        self.driver.find_element(*self.PASSWORD_FIELD).send_keys(password)
        self.driver.find_element(*self.LOGIN_BUTTON).click()

class EmployeePage(BasePage):
    ADD_EMPLOYEE_BUTTON = (By.XPATH, "//a[contains(@href, 'addEmployee')]")
    FIRST_NAME_FIELD = (By.NAME, "firstName")
    LAST_NAME_FIELD = (By.NAME, "lastName")
    EMPLOYEE_ID_FIELD = (By.NAME, "employeeId")
    SAVE_BUTTON = (By.XPATH, "//button[@type='submit']")
    
    def navigate_to_add_employee(self):
        self.driver.find_element(*self.ADD_EMPLOYEE_BUTTON).click()
    
    def fill_employee_details(self, first_name, last_name, employee_id):
        self.driver.find_element(*self.FIRST_NAME_FIELD).send_keys(first_name)
        self.driver.find_element(*self.LAST_NAME_FIELD).send_keys(last_name)
        self.driver.find_element(*self.EMPLOYEE_ID_FIELD).clear()
        self.driver.find_element(*self.EMPLOYEE_ID_FIELD).send_keys(employee_id)`
        },
        {
          id: 4,
          name: 'test_report.html',
          type: 'report',
          size: '15.2 KB',
          description: 'Comprehensive test validation report',
          content: `<!DOCTYPE html>
<html>
<head>
    <title>HRMS Test Suite Validation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #4CAF50; color: white; padding: 20px; }
        .summary { background: #f5f5f5; padding: 15px; margin: 20px 0; }
        .test-case { border: 1px solid #ddd; margin: 10px 0; padding: 15px; }
        .pass { border-left: 5px solid #4CAF50; }
        .warning { border-left: 5px solid #FF9800; }
    </style>
</head>
<body>
    <div class="header">
        <h1>HRMS Test Suite Validation Report</h1>
        <p>Generated on: ${new Date().toLocaleString()}</p>
    </div>
    
    <div class="summary">
        <h2>Test Suite Summary</h2>
        <ul>
            <li><strong>Total Test Cases:</strong> 12</li>
            <li><strong>Validation Status:</strong> ✅ Passed</li>
            <li><strong>Code Quality Score:</strong> 94/100</li>
            <li><strong>Coverage:</strong> 87% of identified features</li>
        </ul>
    </div>
    
    <div class="test-case pass">
        <h3>✅ Login Functionality Tests</h3>
        <p>Comprehensive coverage of authentication flows including valid/invalid credentials, password reset, and session management.</p>
    </div>
    
    <div class="test-case pass">
        <h3>✅ Employee Management Tests</h3>
        <p>Complete CRUD operations for employee data with proper validation and error handling.</p>
    </div>
    
    <div class="test-case warning">
        <h3>⚠️ Performance Tests</h3>
        <p>Basic performance tests included. Consider adding load testing for production readiness.</p>
    </div>
</body>
</html>`
        },
        {
          id: 5,
          name: 'requirements.txt',
          type: 'config',
          size: '0.8 KB',
          description: 'Python dependencies for test execution',
          content: `# Test Dependencies
pytest==7.4.0
selenium==4.11.2
webdriver-manager==3.8.6
pytest-html==3.2.0
pytest-xdist==3.3.1
allure-pytest==2.13.2
requests==2.31.0
python-dotenv==1.0.0`
        }
      ];
      
      setTestFiles(mockArtifacts);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching test artifacts:', error);
      setLoading(false);
    }
  };

  const downloadFile = (file) => {
    const blob = new Blob([file.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadAllFiles = () => {
    testFiles.forEach(file => {
      setTimeout(() => downloadFile(file), 100 * file.id);
    });
  };

  const executeTests = async () => {
    try {
      setLoading(true);
      
      // Create execution request
      const executionRequest = {
        test_id: taskResult?.task_id || 'generated_test',
        execution_name: `Execution of ${taskResult?.application_name || 'Generated Tests'}`,
        environment: 'production',
        browser: 'chrome',
        headless: true,
        parallel: false,
        max_workers: 1,
        timeout: 300,
        retry_failed: true,
        max_retries: 2
      };

      const response = await apiService.executeTest(executionRequest);
      
      // Close this modal and navigate to test results
      onClose();
      
      // Show success message and navigate
      alert(`Test execution started! Execution ID: ${response.execution_id}`);
      
      // If onNavigate is available, navigate to test results
      if (onNavigate) {
        onNavigate('test-results');
      }
      
    } catch (error) {
      console.error('Failed to execute tests:', error);
      alert(`Failed to start test execution: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = (type) => {
    switch (type) {
      case 'test_file': return <TestTube className="w-5 h-5 text-green-500" />;
      case 'page_object': return <Code className="w-5 h-5 text-blue-500" />;
      case 'report': return <FileText className="w-5 h-5 text-purple-500" />;
      case 'config': return <AlertCircle className="w-5 h-5 text-orange-500" />;
      default: return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading test artifacts...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-8 h-8" />
              <div>
                <h2 className="text-2xl font-bold">Tests Created Successfully!</h2>
                <p className="text-green-100">Your AI-powered test suite is ready</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex h-[calc(90vh-120px)]">
          {/* Sidebar */}
          <div className="w-64 bg-gray-50 border-r">
            <div className="p-4">
              <nav className="space-y-2">
                <button
                  onClick={() => setActiveTab('summary')}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'summary'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  📊 Summary
                </button>
                <button
                  onClick={() => setActiveTab('files')}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'files'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  📁 Generated Files
                </button>
                <button
                  onClick={() => setActiveTab('agents')}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'agents'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  🤖 Agent Activity
                </button>
                <button
                  onClick={() => setActiveTab('execution')}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'execution'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  🚀 Execute Tests
                </button>
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'summary' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4">Test Suite Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <CheckCircle className="w-8 h-8 text-green-500 mr-3" />
                      <div>
                        <p className="text-sm text-green-600">Test Cases</p>
                        <p className="text-2xl font-bold text-green-700">12</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <Code className="w-8 h-8 text-blue-500 mr-3" />
                      <div>
                        <p className="text-sm text-blue-600">Files Generated</p>
                        <p className="text-2xl font-bold text-blue-700">{testFiles.length}</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <TestTube className="w-8 h-8 text-purple-500 mr-3" />
                      <div>
                        <p className="text-sm text-purple-600">Coverage</p>
                        <p className="text-2xl font-bold text-purple-700">87%</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <h4 className="font-semibold mb-2">Features Covered:</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      Employee Management
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      Leave Management
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      Attendance Tracking
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      Performance Reviews
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      Recruitment Process
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      User Authentication
                    </div>
                  </div>
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={downloadAllFiles}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download All Files
                  </button>
                  <button
                    onClick={executeTests}
                    className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Execute Tests
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'files' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4">Generated Test Files</h3>
                <div className="space-y-3">
                  {testFiles.map((file) => (
                    <div key={file.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getFileIcon(file.type)}
                          <div>
                            <p className="font-medium">{file.name}</p>
                            <p className="text-sm text-gray-600">{file.description}</p>
                            <p className="text-xs text-gray-500">{file.size}</p>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setActiveTab('preview');
                              setPreviewFile(file);
                            }}
                            className="flex items-center px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            Preview
                          </button>
                          <button
                            onClick={() => downloadFile(file)}
                            className="flex items-center px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                          >
                            <Download className="w-4 h-4 mr-1" />
                            Download
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'agents' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4">AI Agent Activity Summary</h3>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4 bg-green-50 border-green-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm">🔍</div>
                        <div>
                          <p className="font-medium">Discovery Agent</p>
                          <p className="text-sm text-gray-600">Analyzed application structure and identified 15 interactive elements</p>
                        </div>
                      </div>
                      <div className="text-green-600 font-semibold">✅ Completed</div>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-green-50 border-green-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white text-sm">🧪</div>
                        <div>
                          <p className="font-medium">Test Generation Agent</p>
                          <p className="text-sm text-gray-600">Generated 12 comprehensive test scenarios covering all user flows</p>
                        </div>
                      </div>
                      <div className="text-green-600 font-semibold">✅ Completed</div>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-green-50 border-green-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center text-white text-sm">💻</div>
                        <div>
                          <p className="font-medium">Code Generation Agent</p>
                          <p className="text-sm text-gray-600">Created Python test automation code with Page Object Model</p>
                        </div>
                      </div>
                      <div className="text-green-600 font-semibold">✅ Completed</div>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-green-50 border-green-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center text-white text-sm">✅</div>
                        <div>
                          <p className="font-medium">Validation Agent</p>
                          <p className="text-sm text-gray-600">Validated test quality and generated comprehensive report</p>
                        </div>
                      </div>
                      <div className="text-green-600 font-semibold">✅ Completed</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'execution' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4">Test Execution Options</h3>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2">🚀 Run All Tests</h4>
                    <p className="text-sm text-gray-600 mb-3">Execute the complete test suite with all 12 test cases</p>
                    <button
                      onClick={executeTests}
                      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      Start Full Test Run
                    </button>
                  </div>

                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2">🎯 Smoke Tests</h4>
                    <p className="text-sm text-gray-600 mb-3">Run critical path tests for quick validation</p>
                    <button
                      onClick={() => alert('Smoke tests would run here')}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Run Smoke Tests
                    </button>
                  </div>

                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2">📊 Schedule Execution</h4>
                    <p className="text-sm text-gray-600 mb-3">Set up automated test runs on a schedule</p>
                    <button
                      onClick={() => alert('Test scheduling would be configured here')}
                      className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
                    >
                      Configure Schedule
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskCompletionSuccess;
