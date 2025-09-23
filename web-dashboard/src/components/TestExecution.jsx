import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Play,
  Settings,
  Globe,
  Bot,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap,
  FileText,
  Monitor
} from 'lucide-react'
import { apiService } from '../lib/api'

const TestExecution = ({ user }) => {
  const [formData, setFormData] = useState({
    url: '',
    name: '',
    headless: true,
    requirements_config: null,
    custom_config: {}
  })
  const [templates, setTemplates] = useState([])
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [executing, setExecuting] = useState(false)
  const [executionId, setExecutionId] = useState(null)
  const [executionStatus, setExecutionStatus] = useState(null)
  const [error, setError] = useState('')
  const [urlValidation, setUrlValidation] = useState(null)

  useEffect(() => {
    loadTemplates()
  }, [])

  useEffect(() => {
    let interval
    if (executionId && executionStatus?.status !== 'completed' && executionStatus?.status !== 'failed') {
      interval = setInterval(checkExecutionStatus, 2000)
    }
    return () => clearInterval(interval)
  }, [executionId, executionStatus])

  const loadTemplates = async () => {
    try {
      const response = await apiService.getRequirementsTemplates()
      setTemplates(response.templates || [])
    } catch (error) {
      console.error('Failed to load templates:', error)
    }
  }

  const validateUrl = async (url) => {
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      setUrlValidation({ valid: false, message: 'URL must start with http:// or https://' })
      return
    }

    try {
      // Simple URL validation
      new URL(url)
      setUrlValidation({ valid: true, message: 'URL format is valid' })
      
      // Auto-detect application type
      if (url.includes('automationexercise')) {
        setSelectedTemplate('ecommerce')
      } else if (url.includes('orangehrm')) {
        setSelectedTemplate('hrms')
      } else if (url.includes('testfire')) {
        setSelectedTemplate('banking')
      }
    } catch {
      setUrlValidation({ valid: false, message: 'Invalid URL format' })
    }
  }

  const handleUrlChange = (url) => {
    setFormData({ ...formData, url })
    if (url) {
      validateUrl(url)
    } else {
      setUrlValidation(null)
    }
  }

  const loadTemplate = async (templateName) => {
    if (!templateName) return
    
    try {
      const template = await apiService.getRequirementsTemplate(templateName)
      setFormData({
        ...formData,
        requirements_config: template,
        name: formData.name || `${template.app_name}_test_${Date.now()}`
      })
    } catch (error) {
      console.error('Failed to load template:', error)
    }
  }

  const checkExecutionStatus = async () => {
    if (!executionId) return
    
    try {
      const status = await apiService.getTestStatus(executionId)
      setExecutionStatus(status)
      
      if (status.status === 'completed' || status.status === 'failed') {
        setExecuting(false)
      }
    } catch (error) {
      console.error('Failed to check execution status:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setExecuting(true)
    setExecutionStatus(null)

    try {
      const response = await apiService.executeTest(formData)
      setExecutionId(response.execution_id)
      setExecutionStatus({
        execution_id: response.execution_id,
        status: response.status,
        progress: { progress: 0, phase: 'Initializing', message: 'Starting test execution...' }
      })
    } catch (error) {
      setError(error.message)
      setExecuting(false)
    }
  }

  const resetForm = () => {
    setFormData({
      url: '',
      name: '',
      headless: true,
      requirements_config: null,
      custom_config: {}
    })
    setSelectedTemplate('')
    setExecutionId(null)
    setExecutionStatus(null)
    setExecuting(false)
    setError('')
    setUrlValidation(null)
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed': return <AlertCircle className="w-5 h-5 text-red-500" />
      case 'running': return <Clock className="w-5 h-5 text-blue-500 animate-spin" />
      default: return <Clock className="w-5 h-5 text-yellow-500" />
    }
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
          <h1 className="text-3xl font-bold">Execute Tests</h1>
          <p className="text-muted-foreground">
            Start a new test automation run with our enhanced three-tier AI system
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1">
            <Bot className="w-3 h-3" />
            Enhanced AI
          </Badge>
          <Badge variant="outline" className="gap-1">
            <Zap className="w-3 h-3" />
            {user?.api_quota - user?.api_usage || 0} calls left
          </Badge>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-2"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Test Configuration
              </CardTitle>
              <CardDescription>
                Configure your test automation parameters
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <Tabs defaultValue="basic" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="basic">Basic</TabsTrigger>
                    <TabsTrigger value="template">Template</TabsTrigger>
                    <TabsTrigger value="advanced">Advanced</TabsTrigger>
                  </TabsList>

                  <TabsContent value="basic" className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="url">Application URL *</Label>
                      <div className="relative">
                        <Globe className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                        <Input
                          id="url"
                          type="url"
                          placeholder="https://example.com"
                          value={formData.url}
                          onChange={(e) => handleUrlChange(e.target.value)}
                          className="pl-10"
                          required
                        />
                      </div>
                      {urlValidation && (
                        <Alert variant={urlValidation.valid ? "default" : "destructive"}>
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>{urlValidation.message}</AlertDescription>
                        </Alert>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="name">Test Name *</Label>
                      <Input
                        id="name"
                        placeholder="My Test Execution"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                      />
                    </div>

                    <div className="flex items-center space-x-2">
                      <Switch
                        id="headless"
                        checked={formData.headless}
                        onCheckedChange={(checked) => setFormData({ ...formData, headless: checked })}
                      />
                      <Label htmlFor="headless" className="flex items-center gap-2">
                        <Monitor className="w-4 h-4" />
                        Run in headless mode (faster execution)
                      </Label>
                    </div>
                  </TabsContent>

                  <TabsContent value="template" className="space-y-4">
                    <div className="space-y-2">
                      <Label>Requirements Template</Label>
                      <Select value={selectedTemplate} onValueChange={(value) => {
                        setSelectedTemplate(value)
                        loadTemplate(value)
                      }}>
                        <SelectTrigger>
                          <SelectValue placeholder="Choose a template" />
                        </SelectTrigger>
                        <SelectContent>
                          {templates.map((template) => (
                            <SelectItem key={template.name} value={template.name}>
                              {template.display_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {formData.requirements_config && (
                      <Card className="bg-muted/50">
                        <CardHeader className="pb-3">
                          <CardTitle className="text-sm">Template Preview</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                          <div className="text-sm">
                            <strong>Type:</strong> {formData.requirements_config.application_type}
                          </div>
                          <div className="text-sm">
                            <strong>Scenarios:</strong> {Object.keys(formData.requirements_config.test_scenarios || {}).length}
                          </div>
                          <div className="text-sm">
                            <strong>Priority Areas:</strong> {formData.requirements_config.priority_areas?.length || 0}
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </TabsContent>

                  <TabsContent value="advanced" className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="custom-config">Custom Configuration (JSON)</Label>
                      <Textarea
                        id="custom-config"
                        placeholder='{"timeout": 30000, "viewport": {"width": 1920, "height": 1080}}'
                        value={JSON.stringify(formData.custom_config, null, 2)}
                        onChange={(e) => {
                          try {
                            const config = JSON.parse(e.target.value || '{}')
                            setFormData({ ...formData, custom_config: config })
                          } catch {
                            // Invalid JSON, ignore
                          }
                        }}
                        rows={6}
                      />
                    </div>
                  </TabsContent>
                </Tabs>

                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <div className="flex gap-3">
                  <Button
                    type="submit"
                    disabled={executing || !formData.url || !formData.name}
                    className="flex-1"
                  >
                    {executing ? (
                      <>
                        <Clock className="w-4 h-4 mr-2 animate-spin" />
                        Executing...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Start Test Execution
                      </>
                    )}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetForm}>
                    Reset
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </motion.div>

        {/* Execution Status */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          {executionStatus && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {getStatusIcon(executionStatus.status)}
                  Execution Status
                </CardTitle>
                <CardDescription>
                  ID: {executionStatus.execution_id}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Progress</span>
                    <span>{Math.round((executionStatus.progress?.progress || 0) * 100)}%</span>
                  </div>
                  <Progress value={(executionStatus.progress?.progress || 0) * 100} />
                </div>

                <div className="space-y-2">
                  <div className="text-sm">
                    <strong>Phase:</strong> {executionStatus.progress?.phase || 'Unknown'}
                  </div>
                  <div className="text-sm">
                    <strong>Status:</strong>{' '}
                    <Badge variant={
                      executionStatus.status === 'completed' ? 'default' :
                      executionStatus.status === 'failed' ? 'destructive' :
                      'secondary'
                    }>
                      {executionStatus.status}
                    </Badge>
                  </div>
                  {executionStatus.progress?.message && (
                    <div className="text-sm text-muted-foreground">
                      {executionStatus.progress.message}
                    </div>
                  )}
                </div>

                {executionStatus.status === 'completed' && (
                  <Button className="w-full" onClick={() => window.location.href = '/results'}>
                    <FileText className="w-4 h-4 mr-2" />
                    View Results
                  </Button>
                )}
              </CardContent>
            </Card>
          )}

          {/* Quick Start Templates */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Start</CardTitle>
              <CardDescription>Popular application templates</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { name: 'ecommerce', label: 'E-commerce', url: 'https://demo.automationexercise.com' },
                { name: 'hrms', label: 'HRMS', url: 'https://opensource-demo.orangehrmlive.com' },
                { name: 'banking', label: 'Banking', url: 'https://demo.testfire.net' }
              ].map((template) => (
                <Button
                  key={template.name}
                  variant="outline"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => {
                    setFormData({
                      ...formData,
                      url: template.url,
                      name: `${template.label}_test_${Date.now()}`
                    })
                    setSelectedTemplate(template.name)
                    loadTemplate(template.name)
                    validateUrl(template.url)
                  }}
                >
                  <Bot className="w-4 h-4 mr-2" />
                  {template.label} Demo
                </Button>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

export default TestExecution
