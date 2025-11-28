/**
 * CreateTestUnified.jsx - Consolidated from 8 CreateTest variants
 *
 * Features combined from:
 * - CreateTest.jsx: Basic UI, test type suggestions, AI suggestions
 * - CreateTestWorking.jsx: Real API, industry templates, requirements upload, duplicate detection
 * - CreateTestComplete.jsx: Enhanced API, coverage analysis, notifications, app summary
 * - CreateTestAdvanced.jsx: Tabbed creation modes (Requirements/TestCases/URL)
 * - CreateTestEnhanced.jsx: Real-time monitoring, duplicate warning
 * - CreateTestRealTime.jsx: Quick start templates, performance/cross-browser options
 * - CreateTestRealTimeEnhanced.jsx: WebSocket support, animations
 * - CreateTestRealTimeFixed.jsx: useAgentStatus hook integration
 */

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import {
  Sparkles, Bot, Target, CheckCircle, Clock, Lightbulb, Zap, Globe, Play,
  FileText, Brain, AlertTriangle, RefreshCw, Eye, Activity, Loader2,
  CheckCircle2, XCircle, Bell, TrendingUp, Shield, Edit, Merge, Info,
  BarChart3, Building2, ShoppingCart, CreditCard, GraduationCap, Stethoscope,
  Car, Plane, Home, Upload, Code, Plus, Trash2, X
} from 'lucide-react';
import { apiService } from '../lib/api';

// Try to import enhanced API service
let enhancedApiService = null;
try {
  const enhanced = require('../lib/api-enhanced');
  enhancedApiService = enhanced.enhancedApiService;
} catch (e) { /* fallback to apiService */ }

// Constants
const AGENT_PHASES = [
  { name: 'Discovery Agent', description: 'Analyzing application structure', icon: Eye, color: 'blue' },
  { name: 'Generation Agent', description: 'Creating test scenarios', icon: Brain, color: 'purple' },
  { name: 'Code Agent', description: 'Generating test code', icon: Code, color: 'green' },
  { name: 'Validation Agent', description: 'Validating test suite', icon: CheckCircle, color: 'orange' }
];

const TEST_TYPES = [
  { type: 'functional', title: 'Functional', icon: Target, examples: ['User registration', 'Login', 'Forms'] },
  { type: 'ui', title: 'UI/UX', icon: Sparkles, examples: ['Buttons', 'Validation', 'Responsive'] },
  { type: 'integration', title: 'Integration', icon: Zap, examples: ['API', 'Database', 'Payment'] },
  { type: 'performance', title: 'Performance', icon: Clock, examples: ['Load time', 'Stress test'] }
];

const INDUSTRY_TEMPLATES = [
  { id: 'hrms', name: 'HRMS', icon: Building2, url: 'https://opensource-demo.orangehrmlive.com',
    features: ['Employee Mgmt', 'Leave', 'Attendance', 'Performance'],
    description: 'Test HRMS functionality including employee management and HR workflows' },
  { id: 'ecommerce', name: 'E-Commerce', icon: ShoppingCart, url: 'https://demo.opencart.com',
    features: ['Products', 'Cart', 'Checkout', 'Orders'],
    description: 'Test e-commerce flows including shopping cart and payment processing' },
  { id: 'banking', name: 'Banking', icon: CreditCard, url: 'https://demo.testfire.net',
    features: ['Accounts', 'Transfers', 'Payments', 'Security'],
    description: 'Test banking application security and transaction workflows' },
  { id: 'education', name: 'Education', icon: GraduationCap, url: 'https://school.moodledemo.net',
    features: ['Courses', 'Enrollment', 'Grades', 'Reports'],
    description: 'Test LMS including course management and assessments' },
  { id: 'healthcare', name: 'Healthcare', icon: Stethoscope, url: 'https://demo.openmrs.org',
    features: ['Patients', 'Appointments', 'Records', 'Prescriptions'],
    description: 'Test healthcare system patient management workflows' },
  { id: 'travel', name: 'Travel', icon: Plane, url: 'https://phptravels.net/demo',
    features: ['Flights', 'Hotels', 'Bookings', 'Payment'],
    description: 'Test travel booking platform reservations and payments' }
];

const PRIORITIES = [
  { value: 'low', label: 'Low' }, { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' }, { value: 'critical', label: 'Critical' }
];

const APP_TYPES = [
  { value: 'web_application', label: 'Web App' }, { value: 'ecommerce', label: 'E-commerce' },
  { value: 'banking', label: 'Banking' }, { value: 'healthcare', label: 'Healthcare' },
  { value: 'education', label: 'Education' }, { value: 'hrms', label: 'HRMS' }
];

const AI_SUGGESTIONS = [
  'Test the complete checkout process from cart to payment',
  'Verify user registration with email verification',
  'Test product search and filtering functionality',
  'Validate form error handling and validation',
  'Test user login with different credentials',
  'Verify responsive design on mobile devices'
];

const CreateTestUnified = ({ user, onNavigate, apiServiceProp, config = {} }) => {
  // Config with defaults
  const cfg = {
    enableTabs: true, enableDuplicateDetection: true, enableCoverageAnalysis: true,
    enableNotifications: true, enableRequirementsUpload: true, enableAppSummary: true,
    ...config
  };

  const api = apiServiceProp || enhancedApiService || apiService;

  // Core state
  const [applications, setApplications] = useState([]);
  const [selectedApp, setSelectedApp] = useState('');
  const [activeTab, setActiveTab] = useState('simple');
  const [isCreating, setIsCreating] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [agentStatus, setAgentStatus] = useState(null);
  const [generatedTests, setGeneratedTests] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Form state
  const [testName, setTestName] = useState('');
  const [testDescription, setTestDescription] = useState('');
  const [testType, setTestType] = useState('');
  const [priority, setPriority] = useState('medium');

  // Requirements tab
  const [requirementsText, setRequirementsText] = useState('');
  const [coverage, setCoverage] = useState('comprehensive');

  // Test cases tab
  const [testCases, setTestCases] = useState([
    { id: 1, title: '', description: '', steps: [''], expectedResult: '' }
  ]);

  // URL tab
  const [urlForm, setUrlForm] = useState({
    url: '', name: '', type: 'web_application',
    features: [''], flows: [''],
    performanceTests: false, crossBrowserTests: false
  });

  // Advanced features state
  const [duplicateAnalysis, setDuplicateAnalysis] = useState(null);
  const [showDuplicateDialog, setShowDuplicateDialog] = useState(false);
  const [coverageAnalysis, setCoverageAnalysis] = useState(null);
  const [appSummary, setAppSummary] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [realTimeUpdates, setRealTimeUpdates] = useState([]);
  const [requirementsFile, setRequirementsFile] = useState(null);
  const [showCompletionModal, setShowCompletionModal] = useState(false);

  const pollingRef = useRef(null);

  // Initialize
  useEffect(() => {
    loadApplications();
    if (cfg.enableNotifications && 'Notification' in window) {
      Notification.requestPermission();
    }
    return () => { if (pollingRef.current) clearInterval(pollingRef.current); };
  }, []);

  // Load app summary when selected
  useEffect(() => {
    if (selectedApp && cfg.enableAppSummary) loadAppSummary();
  }, [selectedApp]);

  // Duplicate check debounce
  useEffect(() => {
    if (cfg.enableDuplicateDetection && selectedApp && testDescription?.length > 10) {
      const timer = setTimeout(checkDuplicates, 1000);
      return () => clearTimeout(timer);
    }
  }, [selectedApp, testDescription]);

  // API calls
  const loadApplications = async () => {
    try {
      const res = api.getApplications ? await api.getApplications() : await api.request('/api/v1/applications');
      setApplications(res?.data || res || [
        { id: 1, name: 'Demo App', url: 'https://demo.example.com', type: 'web_application' }
      ]);
    } catch (e) {
      console.error('Failed to load apps:', e);
      setApplications([{ id: 1, name: 'Demo App', url: 'https://demo.example.com', type: 'web_application' }]);
    }
  };

  const loadAppSummary = async () => {
    try {
      const res = api.getApplicationTestSummary
        ? await api.getApplicationTestSummary(selectedApp)
        : await api.request(`/api/v1/applications/${selectedApp}/test-summary`);
      if (res?.status === 'success') setAppSummary(res.data);
    } catch (e) { console.error('Failed to load summary:', e); }
  };

  const checkDuplicates = async () => {
    if (!selectedApp || !testDescription) return;
    setIsAnalyzing(true);
    try {
      if (api.checkForDuplicates) {
        const res = await api.checkForDuplicates(selectedApp, testName, testDescription);
        if (res?.data?.has_duplicates) {
          setDuplicateAnalysis(res.data);
          setShowDuplicateDialog(true);
          addNotification('warning', `Found ${res.data.duplicate_count} similar test(s)`);
        }
      }
      if (cfg.enableCoverageAnalysis && api.analyzeCoverage) {
        const res = await api.analyzeCoverage(selectedApp, testDescription);
        if (res?.status === 'success') setCoverageAnalysis(res.data);
      }
    } catch (e) { console.error('Analysis error:', e); }
    finally { setIsAnalyzing(false); }
  };

  // Notifications
  const addNotification = (type, message) => {
    if (!cfg.enableNotifications) return;
    const notif = { id: Date.now(), type, message, time: new Date().toLocaleTimeString() };
    setNotifications(prev => [notif, ...prev.slice(0, 4)]);
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('AI Test Automation', { body: message });
    }
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== notif.id)), 5000);
  };

  // Real-time monitoring
  const startMonitoring = (jobId) => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    pollingRef.current = setInterval(async () => {
      try {
        const res = api.getAgentJobStatus
          ? await api.getAgentJobStatus(jobId)
          : await api.request(`/api/v1/agent-jobs/${jobId}/status`);
        const data = res?.data || res;
        setAgentStatus(data);

        const agent = data?.job?.current_agent || data?.current_agent || 'System';
        const progress = data?.job?.progress_percentage || data?.progress_percentage || 0;
        setRealTimeUpdates(prev => [...prev.slice(-4), {
          time: new Date().toLocaleTimeString(), agent, progress,
          message: `${agent} - ${progress}%`
        }]);

        const status = data?.job?.status || data?.status;
        if (status === 'completed') {
          clearInterval(pollingRef.current);
          setIsCreating(false);
          setShowCompletionModal(true);
          addNotification('success', 'Tests created successfully!');
          loadGeneratedTests(data?.job?.test_suite_id || data?.test_suite_id);
        } else if (status === 'failed') {
          clearInterval(pollingRef.current);
          setIsCreating(false);
          setError('Test creation failed');
          addNotification('error', 'Test creation failed');
        }
      } catch (e) { console.error('Polling error:', e); }
    }, 2000);
  };

  const loadGeneratedTests = async (suiteId) => {
    try {
      const res = api.getTestSuiteTests
        ? await api.getTestSuiteTests(suiteId)
        : await api.request(`/api/v1/test-suites/${suiteId}/tests`);
      setGeneratedTests(res?.data || res || []);
      setSuccess(`Created ${(res?.data || res || []).length} test(s)!`);
    } catch (e) { console.error('Failed to load tests:', e); }
  };

  // Main generate handler
  const handleGenerate = async () => {
    if (activeTab === 'simple' && (!selectedApp || !testDescription)) {
      setError('Please select an application and provide a description');
      return;
    }

    setError(null);
    setSuccess(null);
    setIsCreating(true);
    setAgentStatus(null);
    setRealTimeUpdates([]);

    try {
      let request;
      if (activeTab === 'simple') {
        const app = applications.find(a => a.id.toString() === selectedApp);
        request = {
          application_name: app?.name, application_url: app?.url,
          application_type: app?.type || 'web_application',
          requirements_text: testDescription, test_type: testType || 'functional', priority
        };
      } else if (activeTab === 'requirements') {
        request = { creation_type: 'requirements', business_requirements: requirementsText, priority, coverage };
      } else if (activeTab === 'testcases') {
        request = { creation_type: 'test_cases', test_cases: testCases.filter(tc => tc.title) };
      } else if (activeTab === 'url') {
        request = {
          creation_type: 'url_metadata', application_url: urlForm.url,
          application_name: urlForm.name, application_type: urlForm.type,
          key_features: urlForm.features.filter(f => f),
          user_flows: urlForm.flows.filter(f => f),
          generate_performance_tests: urlForm.performanceTests,
          generate_cross_browser_tests: urlForm.crossBrowserTests, priority
        };
      }

      const res = api.createTest
        ? await api.createTest(request)
        : await api.request('/api/v1/tests/create', { method: 'POST', body: request });

      if (res?.status === 'success' || res?.job_id) {
        const id = res?.data?.job_id || res?.job_id;
        setJobId(id);
        startMonitoring(id);
        addNotification('info', 'Test creation started!');
        setRealTimeUpdates([{ time: new Date().toLocaleTimeString(), agent: 'System', progress: 0, message: 'Started' }]);
      } else {
        throw new Error(res?.message || 'Failed to create tests');
      }
    } catch (e) {
      setError(e.message);
      setIsCreating(false);
      addNotification('error', e.message);
    }
  };

  // Template handler
  const applyTemplate = (template) => {
    setTestName(`${template.name} Test Suite`);
    setTestDescription(template.description);
    setUrlForm(prev => ({
      ...prev, url: template.url, name: template.name,
      type: template.id, features: template.features, flows: []
    }));
  };

  // File upload handler
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      const parsed = JSON.parse(text);
      setRequirementsFile(parsed);
      if (parsed.application_name) setTestName(`${parsed.application_name} Test Suite`);
      if (parsed.description) setTestDescription(parsed.description);
      addNotification('success', 'Requirements file loaded');
    } catch (e) {
      addNotification('error', 'Failed to parse file');
    }
  };

  // Dynamic form helpers
  const addTestCase = () => setTestCases(prev => [...prev, { id: Date.now(), title: '', description: '', steps: [''], expectedResult: '' }]);
  const removeTestCase = (id) => setTestCases(prev => prev.filter(tc => tc.id !== id));
  const addStep = (tcId) => setTestCases(prev => prev.map(tc => tc.id === tcId ? { ...tc, steps: [...tc.steps, ''] } : tc));
  const addFeature = () => setUrlForm(prev => ({ ...prev, features: [...prev.features, ''] }));
  const addFlow = () => setUrlForm(prev => ({ ...prev, flows: [...prev.flows, ''] }));

  // Reset
  const resetForm = () => {
    setGeneratedTests([]);
    setAgentStatus(null);
    setRealTimeUpdates([]);
    setSuccess(null);
    setTestName('');
    setTestDescription('');
    setShowCompletionModal(false);
  };

  // Agent status helpers
  const getCurrentPhase = () => {
    if (!agentStatus) return -1;
    const current = agentStatus?.job?.current_agent || agentStatus?.current_agent;
    return AGENT_PHASES.findIndex(p => p.name === current);
  };

  const getStatusIcon = (phaseName, idx) => {
    const currentIdx = getCurrentPhase();
    if (currentIdx > idx) return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    if (currentIdx === idx) return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
    return <Clock className="h-4 w-4 text-gray-400" />;
  };

  // Render
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Create AI-Powered Tests</h1>
          <p className="text-muted-foreground">Generate comprehensive test suites with AI agents</p>
        </div>
        {cfg.enableNotifications && notifications.length > 0 && (
          <div className="space-y-2 max-w-xs">
            {notifications.map(n => (
              <Alert key={n.id} className={`text-sm ${n.type === 'success' ? 'border-green-300 bg-green-50' : n.type === 'error' ? 'border-red-300 bg-red-50' : n.type === 'warning' ? 'border-orange-300 bg-orange-50' : 'border-blue-300 bg-blue-50'}`}>
                <Bell className="h-3 w-3" />
                <AlertDescription>{n.time} - {n.message}</AlertDescription>
              </Alert>
            ))}
          </div>
        )}
      </div>

      {/* Alerts */}
      {error && <Alert variant="destructive"><AlertTriangle className="h-4 w-4" /><AlertDescription>{error}</AlertDescription></Alert>}
      {success && !isCreating && generatedTests.length === 0 && <Alert className="border-green-300 bg-green-50"><CheckCircle className="h-4 w-4 text-green-600" /><AlertDescription className="text-green-800">{success}</AlertDescription></Alert>}

      {/* Main content when not creating and no results */}
      {!isCreating && generatedTests.length === 0 && (
        <>
          {/* Quick Start Templates */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Zap className="h-5 w-5" />Quick Start Templates</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                {INDUSTRY_TEMPLATES.map(t => (
                  <div key={t.id} onClick={() => applyTemplate(t)} className="border rounded-lg p-3 cursor-pointer hover:border-blue-300 hover:bg-blue-50 transition-colors text-center">
                    <t.icon className="h-6 w-6 mx-auto mb-2 text-blue-500" />
                    <div className="font-medium text-sm">{t.name}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* App Summary */}
          {cfg.enableAppSummary && appSummary && (
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><BarChart3 className="h-5 w-5" />Test Overview</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-4 text-center">
                  <div><div className="text-2xl font-bold text-blue-600">{appSummary.test_summary?.total_tests || 0}</div><div className="text-sm text-muted-foreground">Total</div></div>
                  <div><div className="text-2xl font-bold text-green-600">{appSummary.test_summary?.status_distribution?.generated || 0}</div><div className="text-sm text-muted-foreground">Generated</div></div>
                  <div><div className="text-2xl font-bold text-orange-600">{appSummary.test_summary?.status_distribution?.active || 0}</div><div className="text-sm text-muted-foreground">Active</div></div>
                  <div><div className="text-2xl font-bold text-purple-600">{appSummary.test_summary?.top_keywords?.length || 0}</div><div className="text-sm text-muted-foreground">Areas</div></div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Main Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />Test Configuration
                {isAnalyzing && <Loader2 className="h-4 w-4 animate-spin" />}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {cfg.enableTabs ? (
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="simple">Simple</TabsTrigger>
                    <TabsTrigger value="requirements">Requirements</TabsTrigger>
                    <TabsTrigger value="testcases">Test Cases</TabsTrigger>
                    <TabsTrigger value="url">URL + Metadata</TabsTrigger>
                  </TabsList>

                  {/* Simple Tab */}
                  <TabsContent value="simple" className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Application</Label>
                        <Select value={selectedApp} onValueChange={setSelectedApp}>
                          <SelectTrigger><SelectValue placeholder="Select app" /></SelectTrigger>
                          <SelectContent>
                            {applications.map(a => <SelectItem key={a.id} value={a.id.toString()}>{a.name}</SelectItem>)}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Priority</Label>
                        <Select value={priority} onValueChange={setPriority}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>{PRIORITIES.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}</SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div>
                      <Label>Test Name (optional)</Label>
                      <Input value={testName} onChange={e => setTestName(e.target.value)} placeholder="e.g., Login Flow Test" />
                    </div>
                    <div>
                      <Label>What to test?</Label>
                      <Textarea value={testDescription} onChange={e => setTestDescription(e.target.value)} placeholder="Describe in plain English..." rows={4} />
                    </div>
                    {cfg.enableRequirementsUpload && (
                      <div>
                        <Label>Or upload requirements.json</Label>
                        <Input type="file" accept=".json" onChange={handleFileUpload} />
                        {requirementsFile && <p className="text-sm text-green-600 mt-1">Loaded: {requirementsFile.application_name}</p>}
                      </div>
                    )}
                    {coverageAnalysis && (
                      <div className="border rounded p-3 bg-blue-50">
                        <div className="flex items-center gap-2 font-medium"><TrendingUp className="h-4 w-4" />Coverage: +{Math.round((coverageAnalysis.coverage_improvement || 0) * 100)}%</div>
                      </div>
                    )}
                  </TabsContent>

                  {/* Requirements Tab */}
                  <TabsContent value="requirements" className="space-y-4">
                    <div className="border rounded p-3 bg-blue-50 text-sm">Provide business requirements or user stories for AI analysis.</div>
                    <Textarea value={requirementsText} onChange={e => setRequirementsText(e.target.value)} placeholder="Enter requirements..." rows={8} />
                    <div className="grid grid-cols-2 gap-4">
                      <div><Label>Priority</Label><Select value={priority} onValueChange={setPriority}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{PRIORITIES.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}</SelectContent></Select></div>
                      <div><Label>Coverage</Label><Select value={coverage} onValueChange={setCoverage}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent><SelectItem value="basic">Basic</SelectItem><SelectItem value="comprehensive">Comprehensive</SelectItem><SelectItem value="exhaustive">Exhaustive</SelectItem></SelectContent></Select></div>
                    </div>
                  </TabsContent>

                  {/* Test Cases Tab */}
                  <TabsContent value="testcases" className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div className="border rounded p-3 bg-green-50 text-sm flex-1 mr-4">Convert manual test cases to automated tests.</div>
                      <Button size="sm" onClick={addTestCase}><Plus className="h-4 w-4 mr-1" />Add</Button>
                    </div>
                    {testCases.map((tc, idx) => (
                      <div key={tc.id} className="border rounded p-4">
                        <div className="flex justify-between mb-3">
                          <span className="font-medium">Test Case {idx + 1}</span>
                          {testCases.length > 1 && <Button variant="ghost" size="sm" onClick={() => removeTestCase(tc.id)}><Trash2 className="h-4 w-4 text-red-500" /></Button>}
                        </div>
                        <div className="grid grid-cols-2 gap-3 mb-3">
                          <Input placeholder="Title" value={tc.title} onChange={e => setTestCases(prev => prev.map(t => t.id === tc.id ? { ...t, title: e.target.value } : t))} />
                          <Input placeholder="Expected Result" value={tc.expectedResult} onChange={e => setTestCases(prev => prev.map(t => t.id === tc.id ? { ...t, expectedResult: e.target.value } : t))} />
                        </div>
                        <Textarea placeholder="Description" value={tc.description} rows={2} className="mb-3" onChange={e => setTestCases(prev => prev.map(t => t.id === tc.id ? { ...t, description: e.target.value } : t))} />
                        <div className="flex justify-between items-center mb-2">
                          <Label className="text-sm">Steps</Label>
                          <Button variant="ghost" size="sm" onClick={() => addStep(tc.id)}><Plus className="h-3 w-3" /></Button>
                        </div>
                        {tc.steps.map((step, i) => (
                          <div key={i} className="flex items-center gap-2 mb-1">
                            <span className="text-sm text-gray-500 w-5">{i + 1}.</span>
                            <Input placeholder="Step" value={step} onChange={e => setTestCases(prev => prev.map(t => t.id === tc.id ? { ...t, steps: t.steps.map((s, si) => si === i ? e.target.value : s) } : t))} />
                          </div>
                        ))}
                      </div>
                    ))}
                  </TabsContent>

                  {/* URL Tab */}
                  <TabsContent value="url" className="space-y-4">
                    <div className="border rounded p-3 bg-purple-50 text-sm">Smart test generation from URL and metadata.</div>
                    <div className="grid grid-cols-2 gap-4">
                      <div><Label>URL *</Label><Input value={urlForm.url} onChange={e => setUrlForm(p => ({ ...p, url: e.target.value }))} placeholder="https://..." /></div>
                      <div><Label>Name *</Label><Input value={urlForm.name} onChange={e => setUrlForm(p => ({ ...p, name: e.target.value }))} placeholder="App Name" /></div>
                    </div>
                    <div><Label>Type</Label><Select value={urlForm.type} onValueChange={v => setUrlForm(p => ({ ...p, type: v }))}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{APP_TYPES.map(t => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}</SelectContent></Select></div>
                    <div>
                      <div className="flex justify-between mb-2"><Label>Features</Label><Button variant="ghost" size="sm" onClick={addFeature}><Plus className="h-3 w-3" /></Button></div>
                      {urlForm.features.map((f, i) => <Input key={i} className="mb-2" value={f} onChange={e => setUrlForm(p => ({ ...p, features: p.features.map((x, xi) => xi === i ? e.target.value : x) }))} placeholder="Feature" />)}
                    </div>
                    <div>
                      <div className="flex justify-between mb-2"><Label>User Flows</Label><Button variant="ghost" size="sm" onClick={addFlow}><Plus className="h-3 w-3" /></Button></div>
                      {urlForm.flows.map((f, i) => <Input key={i} className="mb-2" value={f} onChange={e => setUrlForm(p => ({ ...p, flows: p.flows.map((x, xi) => xi === i ? e.target.value : x) }))} placeholder="Flow" />)}
                    </div>
                    <div className="flex gap-6">
                      <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={urlForm.performanceTests} onChange={e => setUrlForm(p => ({ ...p, performanceTests: e.target.checked }))} />Performance tests</label>
                      <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={urlForm.crossBrowserTests} onChange={e => setUrlForm(p => ({ ...p, crossBrowserTests: e.target.checked }))} />Cross-browser tests</label>
                    </div>
                  </TabsContent>
                </Tabs>
              ) : (
                /* Simple mode only */
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div><Label>Application</Label><Select value={selectedApp} onValueChange={setSelectedApp}><SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger><SelectContent>{applications.map(a => <SelectItem key={a.id} value={a.id.toString()}>{a.name}</SelectItem>)}</SelectContent></Select></div>
                    <div><Label>Priority</Label><Select value={priority} onValueChange={setPriority}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{PRIORITIES.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}</SelectContent></Select></div>
                  </div>
                  <div><Label>What to test?</Label><Textarea value={testDescription} onChange={e => setTestDescription(e.target.value)} placeholder="Describe..." rows={4} /></div>
                </div>
              )}

              <Button onClick={handleGenerate} disabled={isCreating} className="w-full" size="lg">
                <Sparkles className="w-4 h-4 mr-2" />{isCreating ? 'Creating...' : 'Generate AI-Powered Tests'}
              </Button>
            </CardContent>
          </Card>

          {/* Duplicate Dialog */}
          <Dialog open={showDuplicateDialog} onOpenChange={setShowDuplicateDialog}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle><Shield className="h-5 w-5 inline mr-2" />Duplicates Detected</DialogTitle>
                <DialogDescription>Found {duplicateAnalysis?.duplicate_count || 0} similar test(s)</DialogDescription>
              </DialogHeader>
              {duplicateAnalysis?.recommendations?.map((r, i) => (
                <div key={i} className="border rounded p-3 mb-2">
                  <div className="flex justify-between"><span className="font-medium">{r.test_name}</span><Badge>{Math.round((r.similarity_score || 0) * 100)}%</Badge></div>
                  <p className="text-sm text-muted-foreground mt-1">{r.update_reason}</p>
                </div>
              ))}
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowDuplicateDialog(false)}>Cancel</Button>
                <Button onClick={() => { setShowDuplicateDialog(false); handleGenerate(); }}>Create Anyway</Button>
              </div>
            </DialogContent>
          </Dialog>

          {/* Test Types */}
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><Lightbulb className="h-5 w-5" />Test Types</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 gap-3">
                {TEST_TYPES.map(t => (
                  <div key={t.type} onClick={() => setTestType(t.type)} className={`border rounded p-3 cursor-pointer transition-colors ${testType === t.type ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'}`}>
                    <div className="flex items-center gap-2 mb-1"><t.icon className="h-4 w-4 text-blue-500" /><span className="font-medium text-sm">{t.title}</span></div>
                    <div className="flex flex-wrap gap-1">{t.examples.map((e, i) => <Badge key={i} variant="secondary" className="text-xs">{e}</Badge>)}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI Suggestions */}
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><Bot className="h-5 w-5" />AI Suggestions</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                {AI_SUGGESTIONS.map((s, i) => (
                  <div key={i} onClick={() => setTestDescription(s)} className="border rounded p-3 cursor-pointer hover:border-blue-300 hover:bg-blue-50 transition-colors text-sm">{s}</div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Agent Monitor - During Creation */}
      {isCreating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Activity className="h-5 w-5 animate-pulse text-blue-500" />AI Agents Working</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {agentStatus && (
              <div>
                <div className="flex justify-between text-sm mb-1"><span>Progress</span><span>{agentStatus?.job?.progress_percentage || agentStatus?.progress_percentage || 0}%</span></div>
                <Progress value={agentStatus?.job?.progress_percentage || agentStatus?.progress_percentage || 0} />
              </div>
            )}
            <div className="grid grid-cols-2 gap-3">
              {AGENT_PHASES.map((p, i) => (
                <div key={p.name} className={`border rounded p-3 ${getCurrentPhase() === i ? 'border-blue-500 bg-blue-50' : getCurrentPhase() > i ? 'border-green-500 bg-green-50' : ''}`}>
                  <div className="flex items-center gap-2 mb-1">{getStatusIcon(p.name, i)}<span className="font-medium text-sm">{p.name}</span></div>
                  <p className="text-xs text-muted-foreground">{p.description}</p>
                </div>
              ))}
            </div>
            {realTimeUpdates.length > 0 && (
              <div className="border rounded p-3 bg-gray-50">
                <div className="font-medium text-sm mb-2 flex items-center gap-2"><RefreshCw className="h-4 w-4" />Live Updates</div>
                <div className="space-y-1 max-h-24 overflow-y-auto">
                  {realTimeUpdates.slice().reverse().map((u, i) => (
                    <div key={i} className="text-xs flex justify-between"><span className="text-muted-foreground">{u.time}</span><span>{u.message}</span></div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {generatedTests.length > 0 && !isCreating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><CheckCircle className="h-5 w-5 text-green-500" />Tests Created!</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div><div className="text-2xl font-bold text-blue-600">{generatedTests.length}</div><div className="text-sm text-muted-foreground">Tests</div></div>
              <div><div className="text-2xl font-bold text-green-600">{generatedTests.reduce((s, t) => s + (t.scenarios || 0), 0)}</div><div className="text-sm text-muted-foreground">Scenarios</div></div>
              <div><div className="text-2xl font-bold text-purple-600">Ready</div><div className="text-sm text-muted-foreground">Status</div></div>
            </div>
            <div className="space-y-2">
              {generatedTests.map(t => (
                <div key={t.id} className="border rounded p-3">
                  <div className="flex justify-between mb-1"><span className="font-medium">{t.name}</span><Badge>Generated</Badge></div>
                  <p className="text-sm text-muted-foreground">{t.description}</p>
                  <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                    <span><FileText className="h-3 w-3 inline mr-1" />{t.scenarios || 0} scenarios</span>
                    {t.file_path && <span><Code className="h-3 w-3 inline mr-1" />{t.file_path}</span>}
                  </div>
                </div>
              ))}
            </div>
            <div className="flex gap-3">
              <Button onClick={() => onNavigate?.('test-results')} className="flex-1"><Play className="w-4 h-4 mr-2" />Run Tests</Button>
              <Button variant="outline" onClick={resetForm}>Create New</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Completion Modal */}
      {showCompletionModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Tests Created!</h3>
            <p className="text-muted-foreground mb-6">Your test suite is ready.</p>
            <div className="space-y-2">
              <Button className="w-full" onClick={() => { setShowCompletionModal(false); onNavigate?.('test-management'); }}>Go to Test Management</Button>
              <Button variant="outline" className="w-full" onClick={() => setShowCompletionModal(false)}>Stay Here</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreateTestUnified;
