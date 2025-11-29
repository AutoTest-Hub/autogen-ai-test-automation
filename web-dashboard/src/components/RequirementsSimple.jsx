import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
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
      setLoading(true)
      const response = await apiService.getRequirementsTemplates()
      console.log('Loaded templates:', response)
      setTemplates(response.templates || [])
    } catch (error) {
      console.error('Failed to load templates:', error)
      setTemplates([])
    } finally {
      setLoading(false)
    }
  }

  const loadTemplateData = async (templateName) => {
    try {
      const response = await apiService.getRequirementsTemplate(templateName)
      console.log('Loaded template data:', response)
      setTemplateData(response)
      setSelectedTemplate(templateName)
    } catch (error) {
      console.error('Failed to load template data:', error)
      setTemplateData(null)
    }
  }

  const validateRequirements = async () => {
    try {
      const requirements = customRequirements || templateData?.requirements?.join('\n') || ''
      const response = await apiService.validateRequirements({ requirements })
      setValidationResult(response)
    } catch (error) {
      console.error('Failed to validate requirements:', error)
      setValidationResult({ valid: false, errors: ['Validation failed'] })
    }
  }

  const getTemplateIcon = (templateId) => {
    switch (templateId) {
      case 'ecommerce': return <Globe className="w-5 h-5" />
      case 'banking': return <Shield className="w-5 h-5" />
      case 'hrms': return <Target className="w-5 h-5" />
      default: return <FileText className="w-5 h-5" />
    }
  }

  const getTemplateColor = (templateId) => {
    switch (templateId) {
      case 'ecommerce': return 'bg-blue-500'
      case 'banking': return 'bg-green-500'
      case 'hrms': return 'bg-purple-500'
      default: return 'bg-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <Bot className="w-8 h-8 animate-pulse text-blue-500 mr-3" />
          <span className="text-lg">Loading templates...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Templates</h1>
          <p className="text-muted-foreground">Manage requirements templates for different application types</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1">
            <FileText className="w-3 h-3" />
            {templates.length} templates
          </Badge>
          <Button variant="outline">
            <Upload className="w-4 h-4 mr-2" />
            Import Template
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Templates List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="w-5 h-5" />
              Available Templates
            </CardTitle>
            <CardDescription>
              Pre-built requirement templates for common application types
            </CardDescription>
          </CardHeader>
          <CardContent>
            {templates.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No templates found</h3>
                <p className="text-muted-foreground mb-4">
                  No requirement templates are available.
                </p>
                <Button>
                  <Upload className="w-4 h-4 mr-2" />
                  Create First Template
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {templates.map((template) => (
                  <div
                    key={template.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                      selectedTemplate === template.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                    }`}
                    onClick={() => loadTemplateData(template.id)}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg text-white ${getTemplateColor(template.id)}`}>
                        {getTemplateIcon(template.id)}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium">{template.name}</h3>
                        <p className="text-sm text-muted-foreground mb-2">
                          {template.description}
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {template.application_types?.map((type) => (
                            <Badge key={type} variant="secondary" className="text-xs">
                              {type}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          loadTemplateData(template.id)
                        }}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Template Details / Custom Requirements */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              {selectedTemplate ? 'Template Details' : 'Custom Requirements'}
            </CardTitle>
            <CardDescription>
              {selectedTemplate 
                ? `Requirements for ${templates.find(t => t.id === selectedTemplate)?.name}`
                : 'Create custom requirements for your application'
              }
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {selectedTemplate && templateData ? (
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Template Information</h4>
                  <div className="text-sm space-y-1">
                    <p><strong>Name:</strong> {templateData.name}</p>
                    <p><strong>Description:</strong> {templateData.description}</p>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium mb-2">Requirements</h4>
                  <div className="bg-muted p-4 rounded-lg">
                    {Array.isArray(templateData.requirements) ? (
                      <ul className="space-y-1 text-sm">
                        {templateData.requirements.map((req, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                            {req}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm">{templateData.requirements || 'No requirements specified'}</p>
                    )}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button onClick={() => setSelectedTemplate(null)}>
                    <FileText className="w-4 h-4 mr-2" />
                    Use as Base
                  </Button>
                  <Button variant="outline">
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Custom Requirements
                  </label>
                  <Textarea
                    placeholder="Enter your custom requirements here..."
                    value={customRequirements}
                    onChange={(e) => setCustomRequirements(e.target.value)}
                    rows={10}
                  />
                </div>

                <div className="flex gap-2">
                  <Button onClick={validateRequirements} disabled={!customRequirements.trim()}>
                    <Zap className="w-4 h-4 mr-2" />
                    Validate Requirements
                  </Button>
                  <Button variant="outline" disabled={!customRequirements.trim()}>
                    <Upload className="w-4 h-4 mr-2" />
                    Save as Template
                  </Button>
                </div>

                {validationResult && (
                  <Alert className={validationResult.valid ? 'border-green-500' : 'border-red-500'}>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      {validationResult.valid 
                        ? 'Requirements are valid and well-structured!'
                        : `Validation failed: ${validationResult.errors?.join(', ') || 'Unknown error'}`
                      }
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Requirements
