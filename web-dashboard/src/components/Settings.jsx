import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  User,
  Settings as SettingsIcon,
  Zap,
  Shield,
  Bell,
  Moon,
  Sun,
  Monitor,
  Globe,
  Database,
  Key,
  AlertCircle,
  CheckCircle,
  Info
} from 'lucide-react'
import { apiService } from '../lib/api'

const Settings = ({ user }) => {
  const [profile, setProfile] = useState({
    username: user?.username || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const [preferences, setPreferences] = useState({
    theme: 'system',
    notifications: true,
    emailNotifications: true,
    autoSave: true,
    defaultHeadless: true,
    defaultTimeout: 30000,
    language: 'en'
  })
  const [apiSettings, setApiSettings] = useState({
    apiKey: '',
    webhookUrl: '',
    rateLimitNotifications: true
  })
  const [systemHealth, setSystemHealth] = useState(null)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    loadSystemHealth()
  }, [])

  const loadSystemHealth = async () => {
    try {
      const health = await apiService.getHealth()
      setSystemHealth(health)
    } catch (error) {
      console.error('Failed to load system health:', error)
    }
  }

  const showMessage = (type, text) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 5000)
  }

  const handleProfileSave = async () => {
    setSaving(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      showMessage('success', 'Profile updated successfully')
    } catch (error) {
      showMessage('error', 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handlePreferencesSave = async () => {
    setSaving(true)
    try {
      // Save to localStorage for demo
      localStorage.setItem('user_preferences', JSON.stringify(preferences))
      showMessage('success', 'Preferences saved successfully')
    } catch (error) {
      showMessage('error', 'Failed to save preferences')
    } finally {
      setSaving(false)
    }
  }

  const handleApiSettingsSave = async () => {
    setSaving(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      showMessage('success', 'API settings updated successfully')
    } catch (error) {
      showMessage('error', 'Failed to update API settings')
    } finally {
      setSaving(false)
    }
  }

  const generateApiKey = () => {
    const key = 'sk-' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
    setApiSettings({ ...apiSettings, apiKey: key })
  }

  const getHealthIcon = (status) => {
    if (status?.includes('✅')) return <CheckCircle className="w-4 h-4 text-green-500" />
    if (status?.includes('⚠️')) return <AlertCircle className="w-4 h-4 text-yellow-500" />
    if (status?.includes('❌')) return <AlertCircle className="w-4 h-4 text-red-500" />
    return <Info className="w-4 h-4 text-blue-500" />
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
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account, preferences, and system configuration
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1">
            <User className="w-3 h-3" />
            {user?.username}
          </Badge>
          <Badge variant="outline" className="gap-1">
            <Zap className="w-3 h-3" />
            {user?.api_usage || 0}/{user?.api_quota || 0} API calls
          </Badge>
        </div>
      </motion.div>

      {message && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          <Alert variant={message.type === 'error' ? 'destructive' : 'default'}>
            {message.type === 'success' ? 
              <CheckCircle className="h-4 w-4" /> : 
              <AlertCircle className="h-4 w-4" />
            }
            <AlertDescription>{message.text}</AlertDescription>
          </Alert>
        </motion.div>
      )}

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
          <TabsTrigger value="api">API & Keys</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Profile Information
                </CardTitle>
                <CardDescription>
                  Update your account details and password
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      value={profile.username}
                      onChange={(e) => setProfile({ ...profile, username: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profile.email}
                      onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    />
                  </div>
                </div>

                <div className="border-t pt-6">
                  <h3 className="text-lg font-medium mb-4">Change Password</h3>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="current-password">Current Password</Label>
                      <Input
                        id="current-password"
                        type="password"
                        value={profile.currentPassword}
                        onChange={(e) => setProfile({ ...profile, currentPassword: e.target.value })}
                      />
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="new-password">New Password</Label>
                        <Input
                          id="new-password"
                          type="password"
                          value={profile.newPassword}
                          onChange={(e) => setProfile({ ...profile, newPassword: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="confirm-password">Confirm Password</Label>
                        <Input
                          id="confirm-password"
                          type="password"
                          value={profile.confirmPassword}
                          onChange={(e) => setProfile({ ...profile, confirmPassword: e.target.value })}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <Button onClick={handleProfileSave} disabled={saving}>
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="preferences" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <SettingsIcon className="w-5 h-5" />
                  Application Preferences
                </CardTitle>
                <CardDescription>
                  Customize your application experience
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Theme</Label>
                      <p className="text-sm text-muted-foreground">
                        Choose your preferred color scheme
                      </p>
                    </div>
                    <Select value={preferences.theme} onValueChange={(value) => 
                      setPreferences({ ...preferences, theme: value })
                    }>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="light">
                          <div className="flex items-center gap-2">
                            <Sun className="w-4 h-4" />
                            Light
                          </div>
                        </SelectItem>
                        <SelectItem value="dark">
                          <div className="flex items-center gap-2">
                            <Moon className="w-4 h-4" />
                            Dark
                          </div>
                        </SelectItem>
                        <SelectItem value="system">
                          <div className="flex items-center gap-2">
                            <Monitor className="w-4 h-4" />
                            System
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Language</Label>
                      <p className="text-sm text-muted-foreground">
                        Select your preferred language
                      </p>
                    </div>
                    <Select value={preferences.language} onValueChange={(value) => 
                      setPreferences({ ...preferences, language: value })
                    }>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">
                          <div className="flex items-center gap-2">
                            <Globe className="w-4 h-4" />
                            English
                          </div>
                        </SelectItem>
                        <SelectItem value="es">Español</SelectItem>
                        <SelectItem value="fr">Français</SelectItem>
                        <SelectItem value="de">Deutsch</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Auto-save</Label>
                      <p className="text-sm text-muted-foreground">
                        Automatically save your work
                      </p>
                    </div>
                    <Switch
                      checked={preferences.autoSave}
                      onCheckedChange={(checked) => 
                        setPreferences({ ...preferences, autoSave: checked })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Default Headless Mode</Label>
                      <p className="text-sm text-muted-foreground">
                        Run tests in headless mode by default
                      </p>
                    </div>
                    <Switch
                      checked={preferences.defaultHeadless}
                      onCheckedChange={(checked) => 
                        setPreferences({ ...preferences, defaultHeadless: checked })
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Default Timeout (ms)</Label>
                    <Input
                      type="number"
                      value={preferences.defaultTimeout}
                      onChange={(e) => setPreferences({ 
                        ...preferences, 
                        defaultTimeout: parseInt(e.target.value) || 30000 
                      })}
                    />
                  </div>
                </div>

                <Button onClick={handlePreferencesSave} disabled={saving}>
                  {saving ? 'Saving...' : 'Save Preferences'}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="api" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="w-5 h-5" />
                  API Configuration
                </CardTitle>
                <CardDescription>
                  Manage your API keys and integration settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* API Usage */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>API Usage</span>
                    <span>{user?.api_usage || 0} / {user?.api_quota || 0}</span>
                  </div>
                  <Progress value={((user?.api_usage || 0) / (user?.api_quota || 1)) * 100} />
                  <p className="text-xs text-muted-foreground">
                    {(user?.api_quota || 0) - (user?.api_usage || 0)} calls remaining this month
                  </p>
                </div>

                {/* API Key */}
                <div className="space-y-2">
                  <Label htmlFor="api-key">API Key</Label>
                  <div className="flex gap-2">
                    <Input
                      id="api-key"
                      type="password"
                      value={apiSettings.apiKey}
                      onChange={(e) => setApiSettings({ ...apiSettings, apiKey: e.target.value })}
                      placeholder="sk-..."
                    />
                    <Button variant="outline" onClick={generateApiKey}>
                      Generate
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Use this key to authenticate API requests
                  </p>
                </div>

                {/* Webhook URL */}
                <div className="space-y-2">
                  <Label htmlFor="webhook-url">Webhook URL</Label>
                  <Input
                    id="webhook-url"
                    type="url"
                    value={apiSettings.webhookUrl}
                    onChange={(e) => setApiSettings({ ...apiSettings, webhookUrl: e.target.value })}
                    placeholder="https://your-app.com/webhook"
                  />
                  <p className="text-xs text-muted-foreground">
                    Receive notifications when test executions complete
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Rate Limit Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Get notified when approaching rate limits
                    </p>
                  </div>
                  <Switch
                    checked={apiSettings.rateLimitNotifications}
                    onCheckedChange={(checked) => 
                      setApiSettings({ ...apiSettings, rateLimitNotifications: checked })
                    }
                  />
                </div>

                <Button onClick={handleApiSettingsSave} disabled={saving}>
                  {saving ? 'Saving...' : 'Save API Settings'}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="w-5 h-5" />
                  Notification Settings
                </CardTitle>
                <CardDescription>
                  Configure how and when you receive notifications
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Browser Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Show notifications in your browser
                      </p>
                    </div>
                    <Switch
                      checked={preferences.notifications}
                      onCheckedChange={(checked) => 
                        setPreferences({ ...preferences, notifications: checked })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Email Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive notifications via email
                      </p>
                    </div>
                    <Switch
                      checked={preferences.emailNotifications}
                      onCheckedChange={(checked) => 
                        setPreferences({ ...preferences, emailNotifications: checked })
                      }
                    />
                  </div>
                </div>

                <div className="border-t pt-4">
                  <h3 className="font-medium mb-3">Notification Types</h3>
                  <div className="space-y-3">
                    {[
                      { key: 'test_completion', label: 'Test Completion', description: 'When test executions finish' },
                      { key: 'test_failure', label: 'Test Failures', description: 'When tests fail or encounter errors' },
                      { key: 'quota_warning', label: 'Quota Warnings', description: 'When approaching API limits' },
                      { key: 'system_updates', label: 'System Updates', description: 'Platform updates and maintenance' }
                    ].map((notification) => (
                      <div key={notification.key} className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <Label>{notification.label}</Label>
                          <p className="text-sm text-muted-foreground">
                            {notification.description}
                          </p>
                        </div>
                        <Switch defaultChecked />
                      </div>
                    ))}
                  </div>
                </div>

                <Button onClick={handlePreferencesSave} disabled={saving}>
                  {saving ? 'Saving...' : 'Save Notification Settings'}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="system" className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="w-5 h-5" />
                  System Health
                </CardTitle>
                <CardDescription>
                  Monitor system status and performance
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {systemHealth ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Overall Status</span>
                      <Badge variant={systemHealth.status === 'healthy' ? 'default' : 'destructive'}>
                        {systemHealth.status}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      {Object.entries(systemHealth.system_status || {}).map(([key, status]) => (
                        <div key={key} className="flex items-center justify-between text-sm">
                          <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                          <div className="flex items-center gap-2">
                            {getHealthIcon(status)}
                            <span className="text-xs">{status}</span>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="pt-4 border-t">
                      <div className="text-sm">
                        <strong>Version:</strong> {systemHealth.version}
                      </div>
                      <div className="text-sm">
                        <strong>Last Updated:</strong> {new Date(systemHealth.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Database className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">Loading system health...</p>
                  </div>
                )}

                <div className="flex gap-2">
                  <Button variant="outline" onClick={loadSystemHealth}>
                    Refresh Status
                  </Button>
                  <Button variant="outline">
                    Download Logs
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Settings
