import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  Globe, 
  Plus, 
  Settings, 
  Play, 
  Trash2, 
  ExternalLink,
  Shield,
  Clock,
  CheckCircle,
  AlertCircle,
  Bot,
  Sparkles,
  Target
} from 'lucide-react';
import { apiService } from '../lib/api';

const Applications = ({ user, onNavigate }) => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newApp, setNewApp] = useState({
    name: '',
    url: '',
    type: '',
    description: '',
    credentials: {
      username: '',
      password: ''
    },
    testingGoals: ''
  });

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = async () => {
    try {
      // Simulate loading user's applications
      setApplications([
        {
          id: 1,
          name: 'E-commerce Store',
          url: 'https://mystore.example.com',
          type: 'ecommerce',
          status: 'active',
          testsCount: 24,
          lastRun: '2 hours ago',
          successRate: 96.5,
          description: 'Main customer-facing e-commerce platform'
        },
        {
          id: 2,
          name: 'Admin Dashboard',
          url: 'https://admin.mystore.example.com',
          type: 'admin',
          status: 'active',
          testsCount: 18,
          lastRun: '1 day ago',
          successRate: 94.2,
          description: 'Internal admin panel for store management'
        }
      ]);
    } catch (error) {
      console.error('Failed to load applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddApplication = async () => {
    try {
      // Here we would call the API to add the application
      const newApplication = {
        id: Date.now(),
        ...newApp,
        status: 'pending',
        testsCount: 0,
        lastRun: 'Never',
        successRate: 0
      };
      
      setApplications([...applications, newApplication]);
      setShowAddDialog(false);
      setNewApp({
        name: '',
        url: '',
        type: '',
        description: '',
        credentials: { username: '', password: '' },
        testingGoals: ''
      });
      
      // Trigger AI analysis of the new application
      setTimeout(() => {
        setApplications(prev => prev.map(app => 
          app.id === newApplication.id 
            ? { ...app, status: 'active', testsCount: 12 }
            : app
        ));
      }, 3000);
    } catch (error) {
      console.error('Failed to add application:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'pending': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'error': return <AlertCircle className="h-4 w-4 text-red-500" />;
      default: return <Globe className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'ecommerce': return '🛒';
      case 'admin': return '⚙️';
      case 'banking': return '🏦';
      case 'healthcare': return '🏥';
      case 'education': return '🎓';
      default: return '🌐';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Applications</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-muted rounded w-3/4" />
              </CardHeader>
              <CardContent>
                <div className="h-20 bg-muted rounded" />
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Your Applications</h1>
          <p className="text-muted-foreground">
            Manage your web applications and their AI-powered test automation
          </p>
        </div>
        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Application
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add New Application</DialogTitle>
              <DialogDescription>
                Connect your web application for AI-powered test automation
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Application Name</Label>
                  <Input
                    id="name"
                    value={newApp.name}
                    onChange={(e) => setNewApp({...newApp, name: e.target.value})}
                    placeholder="My E-commerce Store"
                  />
                </div>
                <div>
                  <Label htmlFor="type">Application Type</Label>
                  <Select value={newApp.type} onValueChange={(value) => setNewApp({...newApp, type: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ecommerce">E-commerce</SelectItem>
                      <SelectItem value="admin">Admin Panel</SelectItem>
                      <SelectItem value="banking">Banking</SelectItem>
                      <SelectItem value="healthcare">Healthcare</SelectItem>
                      <SelectItem value="education">Education</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div>
                <Label htmlFor="url">Application URL</Label>
                <Input
                  id="url"
                  value={newApp.url}
                  onChange={(e) => setNewApp({...newApp, url: e.target.value})}
                  placeholder="https://myapp.example.com"
                />
              </div>
              
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={newApp.description}
                  onChange={(e) => setNewApp({...newApp, description: e.target.value})}
                  placeholder="Brief description of your application"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="username">Test Username (Optional)</Label>
                  <Input
                    id="username"
                    value={newApp.credentials.username}
                    onChange={(e) => setNewApp({
                      ...newApp, 
                      credentials: {...newApp.credentials, username: e.target.value}
                    })}
                    placeholder="test@example.com"
                  />
                </div>
                <div>
                  <Label htmlFor="password">Test Password (Optional)</Label>
                  <Input
                    id="password"
                    type="password"
                    value={newApp.credentials.password}
                    onChange={(e) => setNewApp({
                      ...newApp, 
                      credentials: {...newApp.credentials, password: e.target.value}
                    })}
                    placeholder="••••••••"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="goals">What would you like to test?</Label>
                <Textarea
                  id="goals"
                  value={newApp.testingGoals}
                  onChange={(e) => setNewApp({...newApp, testingGoals: e.target.value})}
                  placeholder="Describe what you want to test (e.g., user registration, checkout process, login functionality)"
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddApplication}>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Add & Analyze with AI
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Applications Grid */}
      {applications.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <Globe className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Applications Yet</h3>
            <p className="text-muted-foreground mb-6">
              Add your first web application to start AI-powered test automation
            </p>
            <Button onClick={() => setShowAddDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Application
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {applications.map((app) => (
            <Card key={app.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{getTypeIcon(app.type)}</span>
                    <div>
                      <CardTitle className="text-lg">{app.name}</CardTitle>
                      <CardDescription className="flex items-center gap-1">
                        {getStatusIcon(app.status)}
                        {app.status}
                      </CardDescription>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">{app.description}</p>
                    <div className="flex items-center gap-1 text-sm text-blue-600">
                      <ExternalLink className="h-3 w-3" />
                      <span className="truncate">{app.url}</span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="font-medium">{app.testsCount}</div>
                      <div className="text-muted-foreground">AI Tests</div>
                    </div>
                    <div>
                      <div className="font-medium">{app.successRate}%</div>
                      <div className="text-muted-foreground">Success Rate</div>
                    </div>
                  </div>
                  
                  <div className="text-xs text-muted-foreground">
                    Last run: {app.lastRun}
                  </div>
                  
                  <div className="flex gap-2">
                    <Button size="sm" className="flex-1">
                      <Play className="w-3 h-3 mr-1" />
                      Run Tests
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <Bot className="w-3 h-3 mr-1" />
                      AI Insights
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* AI Recommendations for Applications */}
      {applications.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              AI Recommendations
            </CardTitle>
            <CardDescription>
              Suggestions to improve your test automation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <h4 className="font-semibold text-sm">Add Mobile Testing</h4>
                <p className="text-sm text-muted-foreground">
                  Your e-commerce store would benefit from mobile responsiveness tests
                </p>
              </div>
              <div className="border-l-4 border-green-500 pl-4">
                <h4 className="font-semibold text-sm">Performance Testing</h4>
                <p className="text-sm text-muted-foreground">
                  Consider adding load testing for your checkout process
                </p>
              </div>
              <div className="border-l-4 border-purple-500 pl-4">
                <h4 className="font-semibold text-sm">Security Testing</h4>
                <p className="text-sm text-muted-foreground">
                  AI suggests adding authentication boundary tests for admin panel
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Applications;
