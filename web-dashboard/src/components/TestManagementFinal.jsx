import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  FileText,
  Download,
  Eye,
  Play,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react'

const TestManagementFinal = () => {
  const [testSuites, setTestSuites] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTestSuites()
  }, [])

  const loadTestSuites = () => {
    try {
      // Load from localStorage
      const storedSuites = localStorage.getItem('testSuites')
      if (storedSuites) {
        const suites = JSON.parse(storedSuites)
        setTestSuites(Array.isArray(suites) ? suites : [suites])
      }
      
      // Add sample data if no suites exist
      if (!storedSuites) {
        const sampleSuite = {
          id: 'sample-1',
          name: 'HRMS Demo Test Suite',
          applicationUrl: 'https://opensource-demo.orangehrmlive.com',
          applicationType: 'HRMS',
          createdAt: new Date().toISOString(),
          status: 'ready',
          testCount: 15,
          coverage: '85%',
          files: [
            { name: 'test_login.py', type: 'test', size: '2.3 KB' },
            { name: 'test_employee_management.py', type: 'test', size: '4.1 KB' },
            { name: 'test_leave_management.py', type: 'test', size: '3.7 KB' },
            { name: 'page_objects.py', type: 'page_object', size: '5.2 KB' },
            { name: 'test_report.html', type: 'report', size: '12.8 KB' }
          ]
        }
        setTestSuites([sampleSuite])
      }
    } catch (error) {
      console.error('Error loading test suites:', error)
    } finally {
      setLoading(false)
    }
  }

  const executeTestSuite = (suite) => {
    alert(`Executing test suite: ${suite.name}\\n\\nThis would start the test execution process with real-time monitoring.`)
  }

  const downloadFile = (file) => {
    alert(`Downloading: ${file.name}\\n\\nThis would download the generated test file.`)
  }

  const viewFile = (file) => {
    alert(`Viewing: ${file.name}\\n\\nThis would open the file in a preview modal.`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Clock className="w-8 h-8 animate-spin mx-auto mb-2" />
          <p>Loading test suites...</p>
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
        className="flex justify-between items-center"
      >
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Test Management</h1>
          <p className="text-muted-foreground">
            Manage and execute your AI-generated test suites
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{testSuites.length} Test Suites</Badge>
        </div>
      </motion.div>

      {/* Test Suites */}
      <div className="space-y-4">
        {testSuites.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <AlertCircle className="w-12 h-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Test Suites Found</h3>
              <p className="text-muted-foreground text-center mb-4">
                Create your first test suite using the AI-powered test creation workflow.
              </p>
              <Button onClick={() => window.location.href = '/create-test'}>
                Create Test Suite
              </Button>
            </CardContent>
          </Card>
        ) : (
          testSuites.map((suite) => (
            <motion.div
              key={suite.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {suite.name}
                        <Badge variant={suite.status === 'ready' ? 'default' : 'secondary'}>
                          {suite.status}
                        </Badge>
                      </CardTitle>
                      <CardDescription>
                        {suite.applicationUrl} • {suite.applicationType}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={() => executeTestSuite(suite)} className="gap-2">
                        <Play className="w-4 h-4" />
                        Execute Tests
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold">{suite.testCount}</div>
                      <div className="text-sm text-muted-foreground">Test Cases</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{suite.coverage}</div>
                      <div className="text-sm text-muted-foreground">Coverage</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{suite.files?.length || 0}</div>
                      <div className="text-sm text-muted-foreground">Files</div>
                    </div>
                  </div>

                  {/* Generated Files */}
                  <div>
                    <h4 className="font-semibold mb-3">Generated Files</h4>
                    <div className="grid gap-2">
                      {suite.files?.map((file, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 border rounded-lg"
                        >
                          <div className="flex items-center gap-3">
                            <FileText className="w-4 h-4 text-muted-foreground" />
                            <div>
                              <div className="font-medium">{file.name}</div>
                              <div className="text-sm text-muted-foreground">
                                {file.type} • {file.size}
                              </div>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => viewFile(file)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => downloadFile(file)}
                            >
                              <Download className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))
        )}
      </div>
    </div>
  )
}

export default TestManagementFinal
