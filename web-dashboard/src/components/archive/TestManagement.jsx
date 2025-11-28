import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Button,
} from '@/components/ui/button';
import {
  Badge,
} from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  Input,
} from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Play,
  Eye,
  Download,
  FileText,
  Code,
  TestTube,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Search,
  Filter,
  Plus,
  Settings,
  BarChart3,
  TrendingUp
} from 'lucide-react';
import { apiService } from '../lib/api';

const TestManagement = ({ user }) => {
  const [testSuites, setTestSuites] = useState([]);
  const [filteredSuites, setFilteredSuites] = useState([]);
  const [selectedSuite, setSelectedSuite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  useEffect(() => {
    loadTestSuites();
  }, []);

  useEffect(() => {
    filterTestSuites();
  }, [testSuites, searchTerm, statusFilter, typeFilter]);

  const loadTestSuites = async () => {
    try {
      // Load existing test suites (mock data for now)
      const mockSuites = [];
      
      // Check for latest test suite from localStorage
      const latestSuiteData = localStorage.getItem('latest_test_suite');
      if (latestSuiteData) {
        try {
          const latestSuite = JSON.parse(latestSuiteData);
          mockSuites.push(latestSuite);
          // Clear it after loading to avoid duplicates
          localStorage.removeItem('latest_test_suite');
        } catch (e) {
          console.error('Error parsing latest test suite:', e);
        }
      }
      
      // Add default HRMS demo if no suites exist
      if (mockSuites.length === 0) {
        mockSuites.push({
          id: '294971fc-903e-4c58-9135-b07bc261827d',
          name: 'HRMS Demo Test Suite',
          application_name: 'HRMS Demo',
          application_url: 'https://opensource-demo.orangehrmlive.com',
          application_type: 'HRMS',
          status: 'ready',
          created_at: new Date().toISOString(),
          test_count: 12,
          coverage: 87,
          last_execution: null,
          features: [
            'Employee Management',
            'Leave Management', 
            'Attendance Tracking',
            'Performance Reviews',
            'Recruitment Process',
            'User Authentication'
          ],
          files: [
            { name: 'hrms_login_test.py', type: 'test_file', size: '2.4 KB' },
            { name: 'employee_management_test.py', type: 'test_file', size: '3.1 KB' },
            { name: 'leave_management_test.py', type: 'test_file', size: '2.8 KB' },
            { name: 'test_config.json', type: 'config', size: '1.2 KB' },
            { name: 'page_objects.py', type: 'support', size: '4.5 KB' }
          ]
        });
      }
      
      setTestSuites(mockSuites);
    } catch (error) {
      console.error('Failed to load test suites:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterTestSuites = () => {
    let filtered = testSuites;

    if (searchTerm) {
      filtered = filtered.filter(suite =>
        suite.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        suite.application_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        suite.application_url.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(suite => suite.status === statusFilter);
    }

    if (typeFilter !== 'all') {
      filtered = filtered.filter(suite => suite.application_type === typeFilter);
    }

    setFilteredSuites(filtered);
  };

  const executeTestSuite = async (suite) => {
    try {
      const executionRequest = {
        test_id: suite.id,
        execution_name: `Execution of ${suite.application_name}`,
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
      
      // Show success message
      alert(`Test execution started! Execution ID: ${response.execution_id}`);
      
      // Navigate to test results page
      window.location.href = '/test-results';
      
    } catch (error) {
      console.error('Failed to execute tests:', error);
      alert('Failed to start test execution. Please try again.');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'running':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      ready: 'default',
      running: 'secondary',
      failed: 'destructive'
    };
    
    return (
      <Badge variant={variants[status] || 'outline'}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Test Management</h1>
        </div>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-2">
                    <div className="h-4 bg-muted rounded w-48" />
                    <div className="h-3 bg-muted rounded w-32" />
                  </div>
                  <div className="h-6 bg-muted rounded w-20" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold">Test Management</h1>
          <p className="text-muted-foreground">
            Manage and execute your AI-generated test suites
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1">
            <TestTube className="w-3 h-3" />
            {testSuites.length} test suites
          </Badge>
          <Button onClick={() => window.location.href = '/create-test'}>
            <Plus className="w-4 h-4 mr-2" />
            Create New Tests
          </Button>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex items-center gap-4"
      >
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search test suites..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="ready">Ready</SelectItem>
            <SelectItem value="running">Running</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>

        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="HRMS">HRMS</SelectItem>
            <SelectItem value="E-commerce">E-commerce</SelectItem>
            <SelectItem value="Banking">Banking</SelectItem>
            <SelectItem value="Web Application">Web App</SelectItem>
          </SelectContent>
        </Select>
      </motion.div>

      {/* Test Suites Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Test Suites</CardTitle>
            <CardDescription>
              {filteredSuites.length} of {testSuites.length} test suites
            </CardDescription>
          </CardHeader>
          <CardContent>
            {filteredSuites.length === 0 ? (
              <div className="text-center py-12">
                <TestTube className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No test suites found</h3>
                <p className="text-muted-foreground mb-4">
                  {testSuites.length === 0 
                    ? "You haven't created any test suites yet." 
                    : "No test suites match your current filters."
                  }
                </p>
                <Button onClick={() => window.location.href = '/create-test'}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Test Suite
                </Button>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Test Suite</TableHead>
                    <TableHead>Application</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Tests</TableHead>
                    <TableHead>Coverage</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredSuites.map((suite) => (
                    <TableRow key={suite.id} className="group">
                      <TableCell className="font-medium">
                        <div>
                          <div className="font-medium">{suite.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {suite.application_url}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{suite.application_name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{suite.application_type}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(suite.status)}
                          {getStatusBadge(suite.status)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <TestTube className="w-3 h-3" />
                          {suite.test_count}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${suite.coverage}%` }}
                            />
                          </div>
                          <span className="text-sm">{suite.coverage}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm">
                          <Calendar className="w-3 h-3" />
                          {formatDate(suite.created_at)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => executeTestSuite(suite)}
                            disabled={suite.status !== 'ready'}
                          >
                            <Play className="w-3 h-3 mr-1" />
                            Execute
                          </Button>
                          
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setSelectedSuite(suite)}
                              >
                                <Eye className="w-3 h-3 mr-1" />
                                View
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-4xl">
                              <DialogHeader>
                                <DialogTitle>{suite.name}</DialogTitle>
                                <DialogDescription>
                                  Test suite details and generated files
                                </DialogDescription>
                              </DialogHeader>
                              
                              <Tabs defaultValue="overview" className="w-full">
                                <TabsList>
                                  <TabsTrigger value="overview">Overview</TabsTrigger>
                                  <TabsTrigger value="files">Files</TabsTrigger>
                                  <TabsTrigger value="features">Features</TabsTrigger>
                                </TabsList>
                                
                                <TabsContent value="overview" className="space-y-4">
                                  <div className="grid grid-cols-3 gap-4">
                                    <Card>
                                      <CardContent className="p-4">
                                        <div className="flex items-center gap-2">
                                          <TestTube className="w-4 h-4 text-blue-500" />
                                          <div>
                                            <div className="text-2xl font-bold">{suite.test_count}</div>
                                            <div className="text-sm text-muted-foreground">Test Cases</div>
                                          </div>
                                        </div>
                                      </CardContent>
                                    </Card>
                                    
                                    <Card>
                                      <CardContent className="p-4">
                                        <div className="flex items-center gap-2">
                                          <FileText className="w-4 h-4 text-green-500" />
                                          <div>
                                            <div className="text-2xl font-bold">{suite.files?.length || 0}</div>
                                            <div className="text-sm text-muted-foreground">Files Generated</div>
                                          </div>
                                        </div>
                                      </CardContent>
                                    </Card>
                                    
                                    <Card>
                                      <CardContent className="p-4">
                                        <div className="flex items-center gap-2">
                                          <BarChart3 className="w-4 h-4 text-purple-500" />
                                          <div>
                                            <div className="text-2xl font-bold">{suite.coverage}%</div>
                                            <div className="text-sm text-muted-foreground">Coverage</div>
                                          </div>
                                        </div>
                                      </CardContent>
                                    </Card>
                                  </div>
                                  
                                  <div className="space-y-2">
                                    <h4 className="font-medium">Application Details</h4>
                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                      <div>
                                        <span className="text-muted-foreground">URL:</span>
                                        <div className="font-mono">{suite.application_url}</div>
                                      </div>
                                      <div>
                                        <span className="text-muted-foreground">Type:</span>
                                        <div>{suite.application_type}</div>
                                      </div>
                                    </div>
                                  </div>
                                </TabsContent>
                                
                                <TabsContent value="files" className="space-y-4">
                                  <div className="space-y-2">
                                    {suite.files?.map((file, index) => (
                                      <div key={index} className="flex items-center justify-between p-3 border rounded">
                                        <div className="flex items-center gap-2">
                                          <FileText className="w-4 h-4" />
                                          <div>
                                            <div className="font-medium">{file.name}</div>
                                            <div className="text-sm text-muted-foreground">{file.type} • {file.size}</div>
                                          </div>
                                        </div>
                                        <Button variant="outline" size="sm">
                                          <Download className="w-3 h-3 mr-1" />
                                          Download
                                        </Button>
                                      </div>
                                    ))}
                                  </div>
                                </TabsContent>
                                
                                <TabsContent value="features" className="space-y-4">
                                  <div className="grid grid-cols-2 gap-2">
                                    {suite.features?.map((feature, index) => (
                                      <div key={index} className="flex items-center gap-2 p-2 border rounded">
                                        <CheckCircle className="w-4 h-4 text-green-500" />
                                        <span>{feature}</span>
                                      </div>
                                    ))}
                                  </div>
                                </TabsContent>
                              </Tabs>
                            </DialogContent>
                          </Dialog>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default TestManagement;
