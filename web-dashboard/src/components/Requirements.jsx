import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Bot,
  FileText,
  Eye,
  CheckCircle,
  AlertCircle,
  Download,
  Upload,
  Settings,
  Zap,
  Globe,
  Shield,
  Target
} from 'lucide-react'
import { apiService } from '../lib/api'

const Requirements = ({ user }) => {
  const [templates, setTemplates] = useState([])
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [templateData, setTemplateData] = useState(null)
  const [customRequirements, setCustomRequirements] = useState('')
  const [validationResult, setValidationResult] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      const response = await apiService.getRequirementsTemplates()
      setTemplates(response.templates || [])
    } catch (error) {
      console.error('Failed to load templates:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTemplateData = async (templateName) => {
    try {
      const data = await apiService.getRequirementsTemplate(templateName)
      setTemplateData(data)
    } catch (error) {
      console.error('Failed to load template data:', error)
      setTemplateData(null)
    }
  }

  const validateRequirements = async () => {
    if (!customRequirements.trim()) return

    try {
      const requirements = JSON.parse(customRequirements)
      const result = await apiService.validateRequirements(requirements)
      setValidationResult(result)
    } catch (error) {
      setValidationResult({
        valid: false,
        errors: ['Invalid JSON format'],
        warnings: [],
        suggestions: [],
        score: 0
      })
    }
  }

  const getTemplateIcon = (templateName) => {
    switch (templateName) {
      case 'ecommerce': return <Globe className="w-5 h-5 text-blue-500" />
      case 'hrms': return <Bot className="w-5 h-5 text-green-500" />
      case 'banking': return <Shield className="w-5 h-5 text-orange-500" />
      default: return <FileText className="w-5 h-5 text-gray-500" />
    }
  }

  const getValidationIcon = (valid) => {
    return valid ? 
      <CheckCircle className="w-4 h-4 text-green-500" /> : 
      <AlertCircle className="w-4 h-4 text-red-500" />
  }

  const TemplateDetailsDialog = ({ template, data }) => (
    <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2">
          {getTemplateIcon(template.name)}
          {template.display_name}
        </DialogTitle>
        <DialogDescription>
          Requirements template for {template.display_name.toLowerCase()} applications
        </DialogDescription>
      </DialogHeader>

      {data ? (
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
            <TabsTrigger value="config">Configuration</TabsTrigger>
            <TabsTrigger value="json">JSON</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Application Info</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-sm">
                    <strong>Type:</strong> {data.application_type}
                  </div>
                  <div className="text-sm">
                    <strong>Base URL:</strong> {data.base_url}
                  </div>
                  <div className="text-sm">
                    <strong>App Name:</strong> {data.app_name}
                  </div>
                  <div className="text-sm">
                    <strong>Description:</strong> {data.description}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Test Coverage</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-sm">
                    <strong>Test Scenarios:</strong> {Object.keys(data.test_scenarios || {}).length}
                  </div>
                  <div className="text-sm">
                    <strong>Priority Areas:</strong> {data.priority_areas?.length || 0}
                  </div>
                  <div className="text-sm">
                    <strong>User Roles:</strong> {data.user_roles?.length || 0}
                  </div>
                  <div className="text-sm">
                    <strong>Business Rules:</strong> {data.business_rules?.length || 0}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Priority Areas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {data.priority_areas?.map((area, index) => (
                    <Badge key={index} variant="secondary">
                      {area}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {data.user_roles && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">User Roles</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {data.user_roles.map((role, index) => (
                      <div key={index} className="flex items-center justify-between p-2 border rounded">
                        <div>
                          <div className="font-medium">{role.role}</div>
                          <div className="text-sm text-muted-foreground">{role.description}</div>
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {role.permissions?.map((permission, pIndex) => (
                            <Badge key={pIndex} variant="outline" className="text-xs">
                              {permission}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="scenarios" className="space-y-4">
            <div className="space-y-4">
              {Object.entries(data.test_scenarios || {}).map(([scenarioKey, scenario]) => (
                <Card key={scenarioKey}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      {scenario.name}
                    </CardTitle>
                    <CardDescription>{scenario.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <div className="text-sm font-medium mb-2">Test Steps:</div>
                      <div className="space-y-1">
                        {scenario.steps?.map((step, index) => (
                          <div key={index} className="text-sm flex items-start gap-2">
                            <span className="text-muted-foreground">{index + 1}.</span>
                            <span>{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {scenario.expected_results && (
                      <div>
                        <div className="text-sm font-medium mb-2">Expected Results:</div>
                        <div className="space-y-1">
                          {scenario.expected_results.map((result, index) => (
                            <div key={index} className="text-sm flex items-start gap-2">
                              <CheckCircle className="w-3 h-3 text-green-500 mt-0.5" />
                              <span>{result}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center gap-2">
                      <Badge variant="outline">
                        Priority: {scenario.priority || 'Medium'}
                      </Badge>
                      {scenario.category && (
                        <Badge variant="secondary">
                          {scenario.category}
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="config" className="space-y-4">
            {data.performance_requirements && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Performance Requirements</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-sm">
                    <strong>Page Load Time:</strong> {data.performance_requirements.page_load_time}
                  </div>
                  <div className="text-sm">
                    <strong>Response Time:</strong> {data.performance_requirements.response_time}
                  </div>
                  <div className="text-sm">
                    <strong>Timeout:</strong> {data.performance_requirements.timeout}
                  </div>
                </CardContent>
              </Card>
            )}

            {data.security_validations && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Security Validations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {data.security_validations.map((validation, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Shield className="w-4 h-4 text-orange-500" />
                        <span className="text-sm">{validation}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {data.business_rules && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Business Rules</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {data.business_rules.map((rule, index) => (
                      <div key={index} className="text-sm p-2 border-l-2 border-blue-500 bg-blue-50 dark:bg-blue-950">
                        {rule}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="json" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">JSON Configuration</CardTitle>
                <CardDescription>
                  Raw JSON data for this requirements template
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="text-xs bg-muted p-4 rounded overflow-x-auto max-h-96">
                  {JSON.stringify(data, null, 2)}
                </pre>
                <div className="mt-4 flex gap-2">
                  <Button size="sm" variant="outline">
                    <Download className="w-3 h-3 mr-1" />
                    Download JSON
                  </Button>
                  <Button size="sm" variant="outline">
                    <Upload className="w-3 h-3 mr-1" />
                    Copy to Custom
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      ) : (
        <div className="text-center py-8">
          <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">Loading template data...</p>
        </div>
      )}
    </DialogContent>
  )

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Requirements</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-muted rounded w-3/4" />
                <div className="h-3 bg-muted rounded w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="h-20 bg-muted rounded" />
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
          <h1 className="text-3xl font-bold">Requirements</h1>
          <p className="text-muted-foreground">
            Manage and customize test automation requirements templates
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1">
            <Bot className="w-3 h-3" />
            {templates.length} templates
          </Badge>
          <Button variant="outline">
            <Upload className="w-4 h-4 mr-2" />
            Import Template
          </Button>
        </div>
      </motion.div>

      <Tabs defaultValue="templates" className="space-y-6">
        <TabsList>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="custom">Custom Requirements</TabsTrigger>
          <TabsTrigger value="validator">Validator</TabsTrigger>
        </TabsList>

        <TabsContent value="templates" className="space-y-6">
          {/* Templates Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template, index) => (
              <motion.div
                key={template.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="group hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      {getTemplateIcon(template.name)}
                      {template.display_name}
                    </CardTitle>
                    <CardDescription>
                      Requirements template for {template.display_name.toLowerCase()} applications
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-sm text-muted-foreground">
                      Template file: <code>{template.file}</code>
                    </div>
                    
                    <div className="flex gap-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex-1"
                            onClick={() => {
                              setSelectedTemplate(template)
                              loadTemplateData(template.name)
                            }}
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View Details
                          </Button>
                        </DialogTrigger>
                        {selectedTemplate?.name === template.name && (
                          <TemplateDetailsDialog 
                            template={selectedTemplate} 
                            data={templateData}
                          />
                        )}
                      </Dialog>
                      
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-1" />
                        Export
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="custom" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Custom Requirements</CardTitle>
              <CardDescription>
                Create or modify requirements configurations in JSON format
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder={`{
  "app_name": "my_application",
  "application_type": "web_app",
  "base_url": "https://example.com",
  "description": "Custom application requirements",
  "test_scenarios": {
    "login_test": {
      "name": "User Login",
      "description": "Test user authentication",
      "steps": [
        "Navigate to login page",
        "Enter valid credentials",
        "Click login button",
        "Verify successful login"
      ],
      "expected_results": [
        "User is redirected to dashboard",
        "Welcome message is displayed"
      ],
      "priority": "High"
    }
  },
  "priority_areas": ["authentication", "navigation"],
  "performance_requirements": {
    "page_load_time": "< 3s",
    "response_time": "< 1s"
  }
}`}
                value={customRequirements}
                onChange={(e) => setCustomRequirements(e.target.value)}
                rows={20}
                className="font-mono text-sm"
              />
              
              <div className="flex gap-2">
                <Button onClick={validateRequirements}>
                  <Settings className="w-4 h-4 mr-2" />
                  Validate Requirements
                </Button>
                <Button variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Save as Template
                </Button>
              </div>

              {validationResult && (
                <Alert variant={validationResult.valid ? "default" : "destructive"}>
                  <div className="flex items-center gap-2">
                    {getValidationIcon(validationResult.valid)}
                    <AlertDescription>
                      <div className="space-y-2">
                        <div>
                          <strong>Validation Score:</strong> {Math.round(validationResult.score * 100)}%
                        </div>
                        
                        {validationResult.errors?.length > 0 && (
                          <div>
                            <strong>Errors:</strong>
                            <ul className="list-disc list-inside ml-4">
                              {validationResult.errors.map((error, index) => (
                                <li key={index} className="text-red-600">{error}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {validationResult.warnings?.length > 0 && (
                          <div>
                            <strong>Warnings:</strong>
                            <ul className="list-disc list-inside ml-4">
                              {validationResult.warnings.map((warning, index) => (
                                <li key={index} className="text-yellow-600">{warning}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {validationResult.suggestions?.length > 0 && (
                          <div>
                            <strong>Suggestions:</strong>
                            <ul className="list-disc list-inside ml-4">
                              {validationResult.suggestions.map((suggestion, index) => (
                                <li key={index} className="text-blue-600">{suggestion}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </AlertDescription>
                  </div>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="validator" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Requirements Validator</CardTitle>
              <CardDescription>
                Validate and analyze requirements configurations for quality and completeness
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      Structure Validation
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Validates JSON structure and required fields
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Zap className="w-4 h-4 text-blue-500" />
                      Quality Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Analyzes test coverage and scenario quality
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Target className="w-4 h-4 text-orange-500" />
                      Best Practices
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Suggests improvements and best practices
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Use the Custom Requirements tab to validate your JSON configurations.
                  The validator checks for structural integrity, completeness, and provides
                  suggestions for improvement.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Requirements
