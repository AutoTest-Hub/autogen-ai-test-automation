import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
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
  Calendar
} from 'lucide-react'
import { apiService } from '../lib/api'

const TestResults = ({ user }) => {
  const [executions, setExecutions] = useState([])
  const [filteredExecutions, setFilteredExecutions] = useState([])
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
      setLoading(true)
      const response = await apiService.getTestExecutions()
      console.log('Loaded executions:', response)
      setExecutions(response.executions || [])
    } catch (error) {
      console.error('Failed to load executions:', error)
      setExecutions([])
    } finally {
      setLoading(false)
    }
  }

  const filterExecutions = () => {
    let filtered = executions

    if (searchTerm) {
      filtered = filtered.filter(execution =>
        execution.test_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        execution.application_url?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(execution => execution.status === statusFilter)
    }

    setFilteredExecutions(filtered)
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

  const formatDuration = (duration) => {
    if (!duration) return 'N/A'
    return `${Math.round(duration)}s`
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  const handleViewDetails = (execution) => {
    console.log('View details for execution:', execution)
    // For now, just log the execution details
    alert(`Execution Details:\nID: ${execution.id}\nTest: ${execution.test_name}\nStatus: ${execution.status}`)
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <Clock className="w-8 h-8 animate-spin text-blue-500 mr-3" />
          <span className="text-lg">Loading test results...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Test Results</h1>
          <p className="text-muted-foreground">View and analyze your test execution results</p>
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
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search executions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <div className="flex gap-2">
          <Button
            variant={statusFilter === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setStatusFilter('all')}
          >
            All
          </Button>
          <Button
            variant={statusFilter === 'completed' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setStatusFilter('completed')}
          >
            Completed
          </Button>
          <Button
            variant={statusFilter === 'failed' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setStatusFilter('failed')}
          >
            Failed
          </Button>
          <Button
            variant={statusFilter === 'running' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setStatusFilter('running')}
          >
            Running
          </Button>
        </div>
      </div>

      {/* Results Table */}
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
              <Button onClick={() => window.location.href = '/create'}>
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
                  <TableHead>Success Rate</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredExecutions.map((execution, index) => (
                  <TableRow key={execution.id || `execution-${index}`}>
                    <TableCell className="font-medium">
                      {execution.test_name || 'Unnamed Test'}
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      {execution.application_url || 'N/A'}
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
                        {formatDate(execution.created_at)}
                      </div>
                    </TableCell>
                    <TableCell>
                      {formatDuration(execution.duration)}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm font-medium">
                        {execution.success_rate ? `${execution.success_rate}%` : 'N/A'}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewDetails(execution)}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default TestResults
