import React, { useState } from 'react';
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
  TrendingUp,
  RefreshCw,
  Trash2
} from 'lucide-react';
import { useTests, useDashboardStats } from '../hooks/useTests';
import { apiService } from '../lib/api';

const TestManagementDynamic = ({ user }) => {
  const { tests, isLoading, isError, mutate } = useTests();
  const { stats } = useDashboardStats();
  const [selectedSuite, setSelectedSuite] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  // Filter tests based on search and filters
  const filteredTests = tests.filter(test => {
    const matchesSearch = test.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         test.application_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || test.status === statusFilter;
    const matchesType = typeFilter === 'all' || test.type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

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
      
      // Refresh data
      mutate();
      
    } catch (error) {
      console.error('Failed to execute tests:', error);
      alert('Failed to start test execution. Please try again.');
    }
  };

  const deleteTestSuite = async (suiteId) => {
    if (window.confirm('Are you sure you want to delete this test suite?')) {
      try {
        await apiService.request(`/api/v1/test-suite/${suiteId}`, { method: 'DELETE' });
        mutate(); // Refresh data
        alert('Test suite deleted successfully');
      } catch (error) {
        console.error('Failed to delete test suite:', error);
        alert('Failed to delete test suite. Please try again.');
      }
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'running':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'draft':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      completed: 'default',
      running: 'secondary',
      failed: 'destructive',
      draft: 'outline'
    };
    
    return (
      <Badge variant={variants[status] || 'outline'}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
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

  if (isError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Test Management</h1>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="text-center py-8">
              <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Tests</h3>
              <p className="text-gray-600 mb-4">Failed to load test data. Please try again.</p>
              <Button onClick={() => mutate()}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
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
            {tests.length} test suites
          </Badge>
          <Button onClick={() => window.location.href = '/create-test'}>
            <Plus className="w-4 h-4 mr-2" />
            Create New Tests
          </Button>
        </div>
      </motion.div>

      {/* Stats Cards */}
      {stats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4"
        >
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-blue-500" />
                <div>
                  <div className="text-2xl font-bold">{tests.length}</div>
                  <div className="text-sm text-muted-foreground">Total Tests</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <div>
                  <div className="text-2xl font-bold">{stats.completed_jobs}</div>
                  <div className="text-sm text-muted-foreground">Completed</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-yellow-500" />
                <div>
                  <div className="text-2xl font-bold">{stats.running_jobs}</div>
                  <div className="text-sm text-muted-foreground">Running</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-purple-500" />
                <div>
                  <div className="text-2xl font-bold">{stats.success_rate}%</div>
                  <div className="text-sm text-muted-foreground">Success Rate</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
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
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="running">Running</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>

        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="functional">Functional</SelectItem>
            <SelectItem value="integration">Integration</SelectItem>
            <SelectItem value="performance">Performance</SelectItem>
            <SelectItem value="security">Security</SelectItem>
          </SelectContent>
        </Select>

        <Button variant="outline" onClick={() => mutate()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </motion.div>

      {/* Test Suites Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Test Suites</CardTitle>
            <CardDescription>
              {filteredTests.length} of {tests.length} test suites
            </CardDescription>
          </CardHeader>
          <CardContent>
            {filteredTests.length === 0 ? (
              <div className="text-center py-12">
                <TestTube className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No test suites found</h3>
                <p className="text-muted-foreground mb-4">
                  {tests.length === 0 
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
                    <TableHead>Success Rate</TableHead>
                    <TableHead>Last Run</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTests.map((suite) => (
                    <TableRow key={suite.id} className="group">
                      <TableCell className="font-medium">
                        <div>
                          <div className="font-medium">{suite.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {suite.description}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            {suite.total_test_cases} test cases
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{suite.application_name}</div>
                          <div className="text-sm text-muted-foreground">
                            {suite.application_url}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{suite.type}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(suite.status)}
                          {getStatusBadge(suite.status)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${suite.success_rate || 0}%` }}
                            />
                          </div>
                          <span className="text-sm">{suite.success_rate || 0}%</span>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {suite.passed_test_cases || 0}/{suite.total_test_cases || 0} passed
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          {suite.last_run_at ? formatDate(suite.last_run_at) : 'Never'}
                        </div>
                        {suite.duration_minutes && (
                          <div className="text-xs text-muted-foreground">
                            {suite.duration_minutes}m duration
                          </div>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => executeTestSuite(suite)}
                            disabled={suite.status === 'running'}
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
                                  Test suite details and information
                                </DialogDescription>
                              </DialogHeader>
                              
                              <Tabs defaultValue="overview" className="w-full">
                                <TabsList>
                                  <TabsTrigger value="overview">Overview</TabsTrigger>
                                  <TabsTrigger value="details">Details</TabsTrigger>
                                </TabsList>
                                
                                <TabsContent value="overview" className="space-y-4">
                                  <div className="grid grid-cols-3 gap-4">
                                    <Card>
                                      <CardContent className="p-4">
                                        <div className="flex items-center gap-2">
                                          <TestTube className="w-4 h-4 text-blue-500" />
                                          <div>
                                            <div className="text-2xl font-bold">{suite.total_test_cases || 0}</div>
                                            <div className="text-sm text-muted-foreground">Test Cases</div>
                                          </div>
                                        </div>
                                      </CardContent>
                                    </Card>
                                    
                                    <Card>
                                      <CardContent className="p-4">
                                        <div className="flex items-center gap-2">
                                          <CheckCircle className="w-4 h-4 text-green-500" />
                                          <div>
                                            <div className="text-2xl font-bold">{suite.success_rate || 0}%</div>
                                            <div className="text-sm text-muted-foreground">Success Rate</div>
                                          </div>
                                        </div>
                                      </CardContent>
                                    </Card>
                                    
                                    <Card>
                                      <CardContent className="p-4">
                                        <div className="flex items-center gap-2">
                                          <Clock className="w-4 h-4 text-purple-500" />
                                          <div>
                                            <div className="text-2xl font-bold">{suite.duration_minutes || 0}m</div>
                                            <div className="text-sm text-muted-foreground">Avg Duration</div>
                                          </div>
                                        </div>
                                      </CardContent>
                                    </Card>
                                  </div>
                                </TabsContent>
                                
                                <TabsContent value="details" className="space-y-4">
                                  <div className="space-y-4">
                                    <div>
                                      <h4 className="font-medium mb-2">Application Details</h4>
                                      <div className="text-sm text-muted-foreground space-y-1">
                                        <div><strong>Name:</strong> {suite.application_name}</div>
                                        <div><strong>URL:</strong> {suite.application_url}</div>
                                        <div><strong>Type:</strong> {suite.type}</div>
                                        <div><strong>Created:</strong> {formatDate(suite.created_at)}</div>
                                        <div><strong>Updated:</strong> {formatDate(suite.updated_at)}</div>
                                      </div>
                                    </div>
                                    
                                    <div>
                                      <h4 className="font-medium mb-2">Test Statistics</h4>
                                      <div className="text-sm text-muted-foreground space-y-1">
                                        <div><strong>Total Test Cases:</strong> {suite.total_test_cases || 0}</div>
                                        <div><strong>Passed:</strong> {suite.passed_test_cases || 0}</div>
                                        <div><strong>Failed:</strong> {suite.failed_test_cases || 0}</div>
                                        <div><strong>Success Rate:</strong> {suite.success_rate || 0}%</div>
                                      </div>
                                    </div>
                                  </div>
                                </TabsContent>
                              </Tabs>
                            </DialogContent>
                          </Dialog>

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteTestSuite(suite.id)}
                          >
                            <Trash2 className="w-3 h-3 mr-1" />
                          </Button>
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

export default TestManagementDynamic;
