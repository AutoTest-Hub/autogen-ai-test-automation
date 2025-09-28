import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  Play, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertCircle,
  Eye,
  Code,
  FileText,
  Loader2
} from 'lucide-react';
import directApiService from '../lib/api-direct';

const TestCasesList = ({ suiteId }) => {
  const [testCases, setTestCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [executingCases, setExecutingCases] = useState(new Set());
  const [executionStatuses, setExecutionStatuses] = useState(new Map());

  useEffect(() => {
    loadTestCases();
  }, [suiteId]);

  // Polling for execution status updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Poll for status updates of executing test cases
      executingCases.forEach(async (testCaseId) => {
        const status = executionStatuses.get(testCaseId);
        if (status && status.executionId && status.status === 'running') {
          try {
            const response = await directApiService.getExecutionStatus(status.executionId);
            if (response.status === 'success') {
              const statusData = response.data;
              
              setExecutionStatuses(prev => new Map(prev.set(testCaseId, {
                ...status,
                status: statusData.status,
                message: statusData.message,
                details: statusData.details,
                progress: statusData.progress || 0,
                currentStep: statusData.current_step,
                executionTime: statusData.execution_time,
                result: statusData.result
              })));

              // If execution completed, remove from executing set and update test case
              if (statusData.status === 'completed' || statusData.status === 'failed') {
                setExecutingCases(prev => {
                  const newSet = new Set(prev);
                  newSet.delete(testCaseId);
                  return newSet;
                });
                
                // Update the test case with final status
                setTestCases(prev => prev.map(tc => 
                  tc.id === testCaseId 
                    ? { 
                        ...tc, 
                        status: statusData.status === 'completed' ? 'passed' : 'failed',
                        execution_result: statusData.result,
                        last_executed: new Date().toISOString()
                      }
                    : tc
                ));
              }
            }
          } catch (error) {
            console.error('Failed to poll execution status:', error);
          }
        }
      });
    }, 2000); // Poll every 2 seconds for faster updates

    return () => clearInterval(interval);
  }, [executingCases, executionStatuses]);

  const loadTestCases = async () => {
    try {
      setLoading(true);
      const response = await directApiService.getTestCasesForSuite(suiteId);
      setTestCases(response.data || []);
    } catch (err) {
      console.error('Failed to load test cases:', err);
      setError('Failed to load test cases');
    } finally {
      setLoading(false);
    }
  };

  const executeTestCase = async (testCase) => {
    try {
      setExecutingCases(prev => new Set([...prev, testCase.id]));
      
      // Call the test execution API
      const response = await directApiService.executeTestCase(testCase.id);

      if (response.status === 'success') {
        // Store execution info for real-time tracking
        setExecutionStatuses(prev => new Map(prev.set(testCase.id, {
          executionId: response.execution_id,
          status: 'running',
          message: 'Starting test execution...',
          details: 'Initializing test environment',
          progress: 0,
          startTime: new Date()
        })));

        // Update the test case status to running
        setTestCases(prev => prev.map(tc => 
          tc.id === testCase.id 
            ? { ...tc, status: 'running', execution_id: response.execution_id }
            : tc
        ));
      } else {
        throw new Error(response.message || 'Unknown error');
      }
      
    } catch (error) {
      console.error('Failed to execute test case:', error);
      
      // Remove from executing set on error
      setExecutingCases(prev => {
        const newSet = new Set(prev);
        newSet.delete(testCase.id);
        return newSet;
      });
      
      // Set error status
      setExecutionStatuses(prev => new Map(prev.set(testCase.id, {
        status: 'failed',
        message: `Failed to start execution: ${error.message}`,
        details: 'Please try again',
        progress: 0
      })));
      
      // Update test case status
      setTestCases(prev => prev.map(tc => 
        tc.id === testCase.id 
          ? { ...tc, status: 'failed' }
          : tc
      ));
    }
  };

  const executeAllTestCases = async () => {
    // Execute all test cases that are not currently running
    const casesToExecute = testCases.filter(tc => 
      !executingCases.has(tc.id) && tc.status !== 'running'
    );
    
    for (const testCase of casesToExecute) {
      await executeTestCase(testCase);
      // Small delay between executions to avoid overwhelming the system
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  };

  const getStatusIcon = (testCase) => {
    // Check if there's a real-time execution status
    const executionStatus = executionStatuses.get(testCase.id);
    if (executionStatus) {
      switch (executionStatus.status) {
        case 'running':
          return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
        case 'completed':
          return <CheckCircle className="w-4 h-4 text-green-500" />;
        case 'failed':
          return <XCircle className="w-4 h-4 text-red-500" />;
        default:
          return <Clock className="w-4 h-4 text-yellow-500" />;
      }
    }

    // Default status icons
    switch (testCase.status) {
      case 'passed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'running':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'timeout':
        return <AlertCircle className="w-4 h-4 text-orange-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (testCase) => {
    // Check if there's a real-time execution status
    const executionStatus = executionStatuses.get(testCase.id);
    if (executionStatus) {
      const variants = {
        running: 'secondary',
        completed: 'default',
        failed: 'destructive'
      };
      
      return (
        <Badge variant={variants[executionStatus.status] || 'outline'}>
          {executionStatus.status === 'running' ? 'Executing' : executionStatus.status.charAt(0).toUpperCase() + executionStatus.status.slice(1)}
        </Badge>
      );
    }

    // Default status badges
    const variants = {
      passed: 'default',
      failed: 'destructive',
      running: 'secondary',
      timeout: 'outline',
      generated: 'outline'
    };

    return (
      <Badge variant={variants[testCase.status] || 'outline'}>
        {testCase.status || 'generated'}
      </Badge>
    );
  };

  const getStatusMessage = (testCase) => {
    const executionStatus = executionStatuses.get(testCase.id);
    if (executionStatus) {
      return executionStatus.message || 'Execution in progress...';
    }
    return null;
  };

  const getExecutionProgress = (testCaseId) => {
    const executionStatus = executionStatuses.get(testCaseId);
    if (executionStatus && executionStatus.status === 'running') {
      return executionStatus.progress || 0;
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
          <p>Loading test cases...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center text-red-500">
          <XCircle className="w-8 h-8 mx-auto mb-2" />
          <p>{error}</p>
          <Button onClick={loadTestCases} className="mt-2">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (testCases.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center text-muted-foreground">
          <FileText className="w-8 h-8 mx-auto mb-2" />
          <p>No test cases found for this suite</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-medium">Test Cases ({testCases.length})</h4>
        <Button 
          onClick={executeAllTestCases}
          disabled={executingCases.size > 0}
          size="sm"
        >
          {executingCases.size > 0 ? (
            <>
              <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              Running ({executingCases.size})
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-1" />
              Run All Tests
            </>
          )}
        </Button>
      </div>

      <div className="space-y-3">
        {testCases.map((testCase) => (
          <Card key={testCase.id} className="border-l-4 border-l-blue-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {getStatusIcon(testCase)}
                    <h5 className="font-medium">{testCase.name}</h5>
                    {getStatusBadge(testCase)}
                  </div>
                  
                  <p className="text-sm text-muted-foreground mb-2">
                    {testCase.description}
                  </p>
                  
                  {/* Real-time execution status message */}
                  {getStatusMessage(testCase) && (
                    <div className="text-xs text-blue-600 mb-2">
                      {getStatusMessage(testCase)}
                    </div>
                  )}
                  
                  {/* Progress bar for running executions */}
                  {getExecutionProgress(testCase.id) !== null && (
                    <div className="w-full bg-gray-200 rounded-full h-1.5 mb-2">
                      <div 
                        className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${getExecutionProgress(testCase.id)}%` }}
                      />
                    </div>
                  )}
                  
                  {testCase.last_executed && (
                    <p className="text-xs text-muted-foreground">
                      Last executed: {new Date(testCase.last_executed).toLocaleString()}
                    </p>
                  )}
                </div>
                
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => executeTestCase(testCase)}
                    disabled={executingCases.has(testCase.id) || testCase.status === 'running'}
                  >
                    {executingCases.has(testCase.id) || testCase.status === 'running' ? (
                      <>
                        <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                        Running
                      </>
                    ) : (
                      <>
                        <Play className="w-3 h-3 mr-1" />
                        Run
                      </>
                    )}
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      // Show test case details/code
                      const executionStatus = executionStatuses.get(testCase.id);
                      let details = `Test Case Details:\n\nName: ${testCase.name}\nDescription: ${testCase.description}\nStatus: ${testCase.status}`;
                      
                      if (executionStatus) {
                        details += `\n\nExecution Status: ${executionStatus.status}`;
                        if (executionStatus.message) {
                          details += `\nMessage: ${executionStatus.message}`;
                        }
                        if (executionStatus.details) {
                          details += `\nDetails: ${executionStatus.details}`;
                        }
                        if (executionStatus.executionTime) {
                          details += `\nExecution Time: ${executionStatus.executionTime}`;
                        }
                      }
                      
                      details += `\n\nTest steps and code would be shown here in a detailed view.`;
                      alert(details);
                    }}
                  >
                    <Eye className="w-3 h-3 mr-1" />
                    View
                  </Button>
                </div>
              </div>
              
              {testCase.execution_result && (
                <div className="mt-3 p-3 bg-muted rounded-md">
                  <h6 className="text-sm font-medium mb-1">Execution Result:</h6>
                  <pre className="text-xs text-muted-foreground whitespace-pre-wrap">
                    {JSON.stringify(testCase.execution_result, null, 2)}
                  </pre>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default TestCasesList;
