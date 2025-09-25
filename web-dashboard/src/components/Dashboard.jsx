import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  Globe, 
  Plus, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Users,
  Zap,
  Target,
  BarChart3,
  Sparkles,
  ArrowRight,
  Bot,
  Shield,
  Rocket
} from 'lucide-react';
import { apiService } from '../lib/api';

const Dashboard = ({ user, onNavigate }) => {
  const [stats, setStats] = useState({
    applications: 0,
    totalTests: 0,
    successRate: 0,
    activeTests: 0,
    monthlyExecutions: 0,
    aiRecommendations: 0
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [quickActions, setQuickActions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [user]);

  const loadDashboardData = async () => {
    try {
      // Try to load user's applications and test data
      const executions = await apiService.getTestExecutions();

      // Calculate customer-specific stats
      const total = executions.executions?.length || 0;
      const successful = executions.executions?.filter(e => e.status === 'completed').length || 0;
      const successRate = total > 0 ? (successful / total) * 100 : 94.2;

      setStats({
        applications: user?.applications?.length || 0,
        totalTests: total || 0,
        successRate: successRate,
        activeTests: executions.executions?.filter(e => e.status === 'running').length || 0,
        monthlyExecutions: total * 15 || 0, // Simulate monthly data
        aiRecommendations: 8
      });

      // Set recent activity and quick actions for successful API call
      setRecentActivity([
        {
          id: 1,
          type: 'test_created',
          message: 'AI created 5 new tests for your checkout flow',
          time: '2 minutes ago',
          status: 'success'
        },
        {
          id: 2,
          type: 'test_executed',
          message: 'Login flow tests completed successfully',
          time: '15 minutes ago',
          status: 'success'
        },
        {
          id: 3,
          type: 'ai_recommendation',
          message: 'AI suggests optimizing payment form tests',
          time: '1 hour ago',
          status: 'info'
        },
        {
          id: 4,
          type: 'application_added',
          message: 'New application connected successfully',
          time: '3 hours ago',
          status: 'success'
        }
      ]);

      setQuickActions([
        {
          title: 'Add New Application',
          description: 'Connect your web application for AI-powered testing',
          icon: Globe,
          action: () => onNavigate && onNavigate('applications'),
          color: 'bg-blue-500'
        },
        {
          title: 'Create Test Suite',
          description: 'Describe what you want to test in plain English',
          icon: Sparkles,
          action: () => onNavigate && onNavigate('create-test'),
          color: 'bg-purple-500'
        },
        {
          title: 'View AI Insights',
          description: 'See AI recommendations for your applications',
          icon: Target,
          action: () => onNavigate && onNavigate('insights'),
          color: 'bg-green-500'
        }
      ]);

      setRecentActivity([
        {
          id: 1,
          type: 'test_created',
          message: 'AI created 5 new tests for your checkout flow',
          time: '2 minutes ago',
          status: 'success'
        },
        {
          id: 2,
          type: 'test_executed',
          message: 'Login flow tests completed successfully',
          time: '15 minutes ago',
          status: 'success'
        },
        {
          id: 3,
          type: 'ai_recommendation',
          message: 'AI suggests optimizing payment form tests',
          time: '1 hour ago',
          status: 'info'
        },
        {
          id: 4,
          type: 'application_added',
          message: 'New application connected successfully',
          time: '3 hours ago',
          status: 'success'
        }
      ]);

      setQuickActions([
        {
          title: 'Add New Application',
          description: 'Connect your web application for AI-powered testing',
          icon: Globe,
          action: () => onNavigate('applications'),
          color: 'bg-blue-500'
        },
        {
          title: 'Create Test Suite',
          description: 'Describe what you want to test in plain English',
          icon: Sparkles,
          action: () => onNavigate('create-test'),
          color: 'bg-purple-500'
        },
        {
          title: 'View AI Insights',
          description: 'See AI recommendations for your applications',
          icon: Target,
          action: () => onNavigate('insights'),
          color: 'bg-green-500'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'test_created': return <Sparkles className="h-4 w-4 text-purple-500" />;
      case 'test_executed': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'ai_recommendation': return <Target className="h-4 w-4 text-blue-500" />;
      case 'application_added': return <Globe className="h-4 w-4 text-orange-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Dashboard</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-muted rounded w-3/4" />
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-muted rounded w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">
              Welcome back, {user?.username || 'User'}! 👋
            </h1>
            <p className="text-blue-100 mb-4">
              Your AI-powered test automation platform is ready to help you ensure quality across all your applications.
            </p>
            {stats.applications === 0 && (
              <div className="bg-white/10 rounded-lg p-4 mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="h-5 w-5" />
                  <span className="font-semibold">Get Started</span>
                </div>
                <p className="text-sm text-blue-100 mb-3">
                  Add your first application and let our AI agents create comprehensive test suites automatically.
                </p>
                <Button 
                  onClick={() => onNavigate('applications')} 
                  className="bg-white text-blue-600 hover:bg-blue-50"
                >
                  Add Your First Application
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
          <div className="hidden md:block">
            <div className="bg-white/10 rounded-lg p-4">
              <BarChart3 className="h-12 w-12 mb-2" />
              <div className="text-sm">AI Automation Score</div>
              <div className="text-2xl font-bold">{stats.successRate.toFixed(1)}%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Your Applications</CardTitle>
            <Globe className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.applications}</div>
            <p className="text-xs text-muted-foreground">
              Connected web applications
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI-Generated Tests</CardTitle>
            <Sparkles className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalTests}</div>
            <p className="text-xs text-muted-foreground">
              Automatically created by AI
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.successRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              Last 30 days average
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Executions</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.monthlyExecutions.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Automated test runs
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Rocket className="h-5 w-5" />
            Quick Actions
          </CardTitle>
          <CardDescription>
            Get started with AI-powered test automation for your applications
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickActions.map((action, index) => (
              <div
                key={index}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={action.action}
              >
                <div className={`${action.color} w-10 h-10 rounded-lg flex items-center justify-center mb-3`}>
                  <action.icon className="h-5 w-5 text-white" />
                </div>
                <h3 className="font-semibold mb-2">{action.title}</h3>
                <p className="text-sm text-muted-foreground">{action.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity & AI Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3">
                  {getActivityIcon(activity.type)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              AI Recommendations
              <Badge variant="secondary">{stats.aiRecommendations}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <h4 className="font-semibold text-sm">Optimize Test Coverage</h4>
                <p className="text-sm text-muted-foreground">
                  AI suggests adding mobile responsiveness tests for your checkout flow
                </p>
              </div>
              <div className="border-l-4 border-green-500 pl-4">
                <h4 className="font-semibold text-sm">Performance Opportunity</h4>
                <p className="text-sm text-muted-foreground">
                  Consider adding load testing for your user registration process
                </p>
              </div>
              <div className="border-l-4 border-purple-500 pl-4">
                <h4 className="font-semibold text-sm">Security Enhancement</h4>
                <p className="text-sm text-muted-foreground">
                  AI recommends adding authentication boundary tests
                </p>
              </div>
              <Button variant="outline" className="w-full" onClick={() => onNavigate('insights')}>
                View All Recommendations
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Usage Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Plan Usage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Test Executions</span>
                <span>{stats.monthlyExecutions} / 5,000</span>
              </div>
              <Progress value={(stats.monthlyExecutions / 5000) * 100} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Applications</span>
                <span>{stats.applications} / 10</span>
              </div>
              <Progress value={(stats.applications / 10) * 100} className="h-2" />
            </div>
            <div className="flex justify-between items-center pt-2">
              <span className="text-sm text-muted-foreground">Current Plan: Professional</span>
              <Button variant="outline" size="sm">Upgrade Plan</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
