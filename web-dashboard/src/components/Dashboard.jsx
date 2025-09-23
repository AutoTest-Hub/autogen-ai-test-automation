import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import {
  Play,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  Users,
  Zap,
  Bot,
  Activity,
  Target
} from 'lucide-react'
import { apiService } from '../lib/api'

const Dashboard = ({ user }) => {
  const [stats, setStats] = useState({
    totalExecutions: 0,
    successfulExecutions: 0,
    failedExecutions: 0,
    averageDuration: 0,
    successRate: 0
  })
  const [recentExecutions, setRecentExecutions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const executions = await apiService.getTestExecutions()
      
      // Calculate stats from executions
      const total = executions.executions?.length || 0
      const successful = executions.executions?.filter(e => e.status === 'completed').length || 0
      const failed = executions.executions?.filter(e => e.status === 'failed').length || 0
      const successRate = total > 0 ? (successful / total) * 100 : 0
      
      setStats({
        totalExecutions: total,
        successfulExecutions: successful,
        failedExecutions: failed,
        averageDuration: 285, // Mock data
        successRate: successRate
      })
      
      setRecentExecutions(executions.executions?.slice(0, 5) || [])
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const chartData = [
    { name: 'Mon', executions: 12, success: 10 },
    { name: 'Tue', executions: 19, success: 16 },
    { name: 'Wed', executions: 8, success: 7 },
    { name: 'Thu', executions: 15, success: 13 },
    { name: 'Fri', executions: 22, success: 20 },
    { name: 'Sat', executions: 6, success: 5 },
    { name: 'Sun', executions: 4, success: 4 }
  ]

  const applicationTypeData = [
    { name: 'E-commerce', value: 35, color: '#8884d8' },
    { name: 'HRMS', value: 25, color: '#82ca9d' },
    { name: 'Banking', value: 20, color: '#ffc658' },
    { name: 'Healthcare', value: 12, color: '#ff7300' },
    { name: 'Other', value: 8, color: '#00ff00' }
  ]

  const StatCard = ({ title, value, icon: Icon, trend, color = "primary" }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="relative overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          <Icon className={`h-4 w-4 text-${color}`} />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{value}</div>
          {trend && (
            <p className="text-xs text-muted-foreground">
              <span className={`inline-flex items-center ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                <TrendingUp className="w-3 h-3 mr-1" />
                {trend > 0 ? '+' : ''}{trend}%
              </span>
              {' '}from last week
            </p>
          )}
        </CardContent>
        <div className={`absolute top-0 right-0 w-2 h-full bg-gradient-to-b from-${color} to-${color}/50`} />
      </Card>
    </motion.div>
  )

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
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.username}! Here's your test automation overview.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1">
            <Activity className="w-3 h-3" />
            System Healthy
          </Badge>
          <Button>
            <Play className="w-4 h-4 mr-2" />
            New Test
          </Button>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Executions"
          value={stats.totalExecutions}
          icon={Target}
          trend={12}
          color="blue-500"
        />
        <StatCard
          title="Success Rate"
          value={`${stats.successRate.toFixed(1)}%`}
          icon={CheckCircle}
          trend={5}
          color="green-500"
        />
        <StatCard
          title="Avg Duration"
          value={`${stats.averageDuration}s`}
          icon={Clock}
          trend={-8}
          color="orange-500"
        />
        <StatCard
          title="API Usage"
          value={`${user?.api_usage || 0}/${user?.api_quota || 0}`}
          icon={Zap}
          color="purple-500"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Execution Trends */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Execution Trends</CardTitle>
              <CardDescription>Daily test execution statistics</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="executions" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    dot={{ fill: '#8884d8' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="success" 
                    stroke="#82ca9d" 
                    strokeWidth={2}
                    dot={{ fill: '#82ca9d' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Application Types */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Application Types</CardTitle>
              <CardDescription>Distribution of tested applications</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={applicationTypeData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {applicationTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Executions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Recent Test Executions</CardTitle>
            <CardDescription>Latest test automation runs</CardDescription>
          </CardHeader>
          <CardContent>
            {recentExecutions.length === 0 ? (
              <div className="text-center py-8">
                <Bot className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No test executions yet</p>
                <Button className="mt-4">
                  <Play className="w-4 h-4 mr-2" />
                  Start Your First Test
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {recentExecutions.map((execution, index) => (
                  <motion.div
                    key={execution.execution_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-3 h-3 rounded-full ${
                        execution.status === 'completed' ? 'bg-green-500' :
                        execution.status === 'failed' ? 'bg-red-500' :
                        execution.status === 'running' ? 'bg-blue-500' :
                        'bg-yellow-500'
                      }`} />
                      <div>
                        <p className="font-medium">{execution.request?.name || 'Test Execution'}</p>
                        <p className="text-sm text-muted-foreground">
                          {execution.request?.url || 'No URL'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={
                        execution.status === 'completed' ? 'default' :
                        execution.status === 'failed' ? 'destructive' :
                        execution.status === 'running' ? 'secondary' :
                        'outline'
                      }>
                        {execution.status}
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(execution.start_time).toLocaleDateString()}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

export default Dashboard
