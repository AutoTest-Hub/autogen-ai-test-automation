import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  FileText,
  Search,
  Download,
  Eye,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  BarChart3,
  TrendingUp,
  Calendar,
  Filter
} from 'lucide-react'
import { apiService } from '../lib/api'

const TestResults = ({ user }) => {
  const [executions, setExecutions] = useState([])
  const [filteredExecutions, setFilteredExecutions] = useState([])
  const [selectedExecution, setSelectedExecution] = useState(null)
  const [executionDetails, setExecutionDetails] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    loadExecutions()
  }, [])

  useEffect(() => {
    filterExecutions()
  }, [executions, searchTerm, statusFilter])

  const loadExecutions = async () => {
    try {
      const response = await apiService.getTestExecutions()
      setExecutions(response.executions || [])
    } catch (error) {
      console.error('Failed to load executions:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterExecutions = () => {
    let filtered = executions

    if (searchTerm) {
      filtered = filtered.filter(execution =>
        execution.request?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        execution.request?.url?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(execution => execution.status === statusFilter)
    }

    setFilteredExecutions(filtered)
  }

  const loadExecutionDetails = async (executionId) => {
    try {
      const details = await apiService.getTestResults(executionId)
      setExecutionDetails(details)
    } catch (error) {
      console.error('Failed to load execution details:', error)
      setExecutionDetails(null)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />
      case 'running': return <Clock className="w-4 h-4 text-blue-500 animate-spin" />
      case 'timeout': return <AlertCircle className="w-4 h-4 text-orange-500" />
      default: return <Clock className="w-4 h-4 text-yellow-500" />
    }
  }

  const getStatusBadge = (status) => {
    const variants = {
      completed: 'default',
      failed: 'destructive',
      running: 'secondary',
      timeout: 'outline',
      pending: 'outline'
    }
    return <Badge variant={variants[status] || 'outline'}>{status}</Badge>
  }

  const formatDuration = (startTime, endTime) => {
    if (!endTime) return 'Running...'
    const duration = new Date(endTime) - new Date(startTime)
    return `${Math.round(duration / 1000)}s`
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  const ExecutionDetailsDialog = ({ execution, details }) => (
    <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2">
          {getStatusIcon(execution.status)}
          {execution.request?.name || 'Test Execution'}
        </DialogTitle>
        <DialogDescription>
          Execution ID: {execution.execution_id}
        </DialogDescription>
      </DialogHeader>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
          <TabsTrigger value="files">Files</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Execution Info</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-sm">
                  <strong>URL:</strong> {execution.request?.url}
                </div>
                <div className="text-sm">
                  <strong>Started:</strong> {formatDate(execution.start_time)}
                </div>
                <div className="text-sm">
                  <strong>Duration:</strong> {formatDuration(execution.start_time, execution.end_time)}
                </div>
                <div className="text-sm">
                  <strong>Status:</strong> {getStatusBadge(execution.status)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-sm">
                  <strong>Headless:</strong> {execution.request?.headless ? 'Yes' : 'No'}
                </div>
                <div className="text-sm">
                  <strong>Template:</strong> {execution.request?.requirements_config?.application_type || 'None'}
                </div>
                <div className="text-sm">
                  <strong>User:</strong> {execution.user}
                </div>
              </CardContent>
            </Card>
          </div>

          {execution.results_summary && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Results Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-green-600">
                      {execution.results_summary.summary?.total_tests || 0}
                    </div>
                    <div className="text-xs text-muted-foreground">Total Tests</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-blue-600">
                      {execution.results_summary.summary?.success_rate || 0}%
                    </div>
                    <div className="text-xs text-muted-foreground">Success Rate</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-orange-600">
                      {execution.results_summary.summary?.execution_time || 0}s
                    </div>
                    <div className="text-xs text-muted-foreground">Execution Time</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          {details ? (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Test Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="text-xs bg-muted p-4 rounded overflow-x-auto">
                    {details.stdout || 'No output available'}
                  </pre>
                </CardContent>
              </Card>
              
              {details.stderr && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm text-red-600">Errors</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="text-xs bg-red-50 p-4 rounded overflow-x-auto text-red-800">
                      {details.stderr}
                    </pre>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">Loading detailed results...</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Execution Logs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {execution.progress ? (
                  <div className="text-sm font-mono">
                    <div>Phase: {execution.progress.phase}</div>
                    <div>Progress: {Math.round((execution.progress.progress || 0) * 100)}%</div>
                    <div>Message: {execution.progress.message}</div>
                  </div>
                ) : (
                  <p className="text-muted-foreground">No logs available</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="files" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Generated Files</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <FileText className="w-4 h-4" />
                  <span>HTML Report</span>
                  <Button size="sm" variant="outline">
                    <Download className="w-3 h-3 mr-1" />
                    Download
                  </Button>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <FileText className="w-4 h-4" />
                  <span>JSON Report</span>
                  <Button size="sm" variant="outline">
                    <Download className="w-3 h-3 mr-1" />
                    Download
                  </Button>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <FileText className="w-4 h-4" />
                  <span>Test Files (ZIP)</span>
                  <Button size="sm" variant="outline">
                    <Download className="w-3 h-3 mr-1" />
                    Download
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </DialogContent>
  )

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Test Results</h1>
        </div>
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
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
    )
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
          <h1 className="text-3xl font-bold">Test Results</h1>
          <p className="text-muted-foreground">
            View and analyze your test execution results
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1">
            <BarChart3 className="w-3 h-3" />
            {executions.length} executions
          </Badge>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export All
          </Button>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex gap-4"
      >
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search executions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Tabs value={statusFilter} onValueChange={setStatusFilter}>
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="failed">Failed</TabsTrigger>
            <TabsTrigger value="running">Running</TabsTrigger>
          </TabsList>
        </Tabs>
      </motion.div>

      {/* Results Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Execution History</CardTitle>
            <CardDescription>
              {filteredExecutions.length} of {executions.length} executions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {filteredExecutions.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No test results found</h3>
                <p className="text-muted-foreground mb-4">
                  {executions.length === 0 
                    ? "You haven't run any tests yet." 
                    : "No executions match your current filters."
                  }
                </p>
                <Button onClick={() => window.location.href = '/execute'}>
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Start Your First Test
                </Button>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Test Name</TableHead>
                    <TableHead>URL</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Started</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredExecutions.map((execution, index) => (
                    <motion.tr
                      key={execution.execution_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="group"
                    >
                      <TableCell className="font-medium">
                        {execution.request?.name || 'Unnamed Test'}
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {execution.request?.url}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(execution.status)}
                          {getStatusBadge(execution.status)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm">
                          <Calendar className="w-3 h-3" />
                          {formatDate(execution.start_time)}
                        </div>
                      </TableCell>
                      <TableCell>
                        {formatDuration(execution.start_time, execution.end_time)}
                      </TableCell>
                      <TableCell>
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedExecution(execution)
                                loadExecutionDetails(execution.execution_id)
                              }}
                            >
                              <Eye className="w-4 h-4 mr-1" />
                              View
                            </Button>
                          </DialogTrigger>
                          {selectedExecution?.execution_id === execution.execution_id && (
                            <ExecutionDetailsDialog 
                              execution={selectedExecution} 
                              details={executionDetails}
                            />
                          )}
                        </Dialog>
                      </TableCell>
                    </motion.tr>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

export default TestResults
