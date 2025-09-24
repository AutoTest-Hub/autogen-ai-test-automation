import React, { useState, useEffect } from 'react';
import { Activity, Bot, CheckCircle, AlertCircle, Clock, Zap, Eye, Play } from 'lucide-react';

const AgentActivityMonitorStable = ({ userId, taskId = null, className = "", onTaskComplete, ...props }) => {
  const [activities, setActivities] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [systemStats, setSystemStats] = useState({
    activeAgents: 0,
    completedTasks: 0,
    totalActivities: 0
  });

  // Simulate agent activities for demo purposes
  useEffect(() => {
    // Set initial demo data
    const demoActivities = [
      {
        id: 'demo-1',
        agent_type: 'discovery',
        status: 'completed',
        message: 'Application discovery completed',
        created_at: new Date(Date.now() - 300000).toISOString(),
        progress: 100
      },
      {
        id: 'demo-2',
        agent_type: 'test_generation',
        status: 'processing',
        message: 'Generating test cases based on requirements',
        created_at: new Date(Date.now() - 180000).toISOString(),
        progress: 65
      },
      {
        id: 'demo-3',
        agent_type: 'code_generation',
        status: 'idle',
        message: 'Waiting for test generation to complete',
        created_at: new Date(Date.now() - 60000).toISOString(),
        progress: 0
      },
      {
        id: 'demo-4',
        agent_type: 'validation',
        status: 'idle',
        message: 'Waiting for code generation to complete',
        created_at: new Date().toISOString(),
        progress: 0
      }
    ];

    setActivities(demoActivities);
    setSystemStats({
      activeAgents: 1,
      completedTasks: 1,
      totalActivities: 4
    });
  }, [userId]);

  // Get status color and icon
  const getStatusDisplay = (status) => {
    const statusMap = {
      idle: { color: 'text-gray-500', bgColor: 'bg-gray-100', icon: Clock },
      processing: { color: 'text-blue-500', bgColor: 'bg-blue-100', icon: Play },
      analyzing: { color: 'text-purple-500', bgColor: 'bg-purple-100', icon: Eye },
      generating: { color: 'text-orange-500', bgColor: 'bg-orange-100', icon: Zap },
      completed: { color: 'text-green-500', bgColor: 'bg-green-100', icon: CheckCircle },
      error: { color: 'text-red-500', bgColor: 'bg-red-100', icon: AlertCircle }
    };
    
    return statusMap[status] || statusMap.idle;
  };

  // Get agent type display
  const getAgentTypeDisplay = (agentType) => {
    const agentMap = {
      discovery: { name: 'Discovery Agent', color: 'bg-blue-500', icon: '🔍' },
      test_generation: { name: 'Test Generation Agent', color: 'bg-green-500', icon: '🧪' },
      code_generation: { name: 'Code Generation Agent', color: 'bg-orange-500', icon: '💻' },
      validation: { name: 'Validation Agent', color: 'bg-yellow-500', icon: '✅' }
    };
    
    return agentMap[agentType] || { name: agentType, color: 'bg-gray-500', icon: '🤖' };
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Agent Activity Monitor
              </h2>
              <p className="text-sm text-gray-500">
                Real-time AI agent status and progress tracking
              </p>
            </div>
          </div>
          
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-sm text-gray-600">Real-time AI Connected</span>
          </div>
        </div>
        
        {/* System Statistics */}
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {systemStats.activeAgents}
            </div>
            <div className="text-sm text-blue-600">Active Agents</div>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {systemStats.completedTasks}
            </div>
            <div className="text-sm text-green-600">Completed Tasks</div>
          </div>
          <div className="bg-purple-50 p-3 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {systemStats.totalActivities}
            </div>
            <div className="text-sm text-purple-600">Total Activities</div>
          </div>
        </div>
      </div>

      {/* Activities List */}
      <div className="p-6">
        {activities.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Agent Activities
            </h3>
            <p className="text-gray-500">
              Start a test creation task to see AI agents in action
            </p>
          </div>
        ) : (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {activities.map((activity) => {
              const statusDisplay = getStatusDisplay(activity.status);
              const agentDisplay = getAgentTypeDisplay(activity.agent_type);
              const StatusIcon = statusDisplay.icon;
              
              return (
                <div
                  key={activity.id}
                  className={`border rounded-lg p-4 transition-all duration-200 ${
                    activity.status === 'processing' 
                      ? 'border-blue-300 bg-blue-50 shadow-md' 
                      : activity.status === 'completed'
                      ? 'border-green-300 bg-green-50'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 ${agentDisplay.color} rounded-full flex items-center justify-center text-white text-sm`}>
                        {agentDisplay.icon}
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">{agentDisplay.name}</h4>
                        <p className="text-sm text-gray-600">{activity.message}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${statusDisplay.bgColor}`}>
                        <StatusIcon className={`w-3 h-3 ${statusDisplay.color}`} />
                        <span className={`text-xs font-medium ${statusDisplay.color} capitalize`}>
                          {activity.status}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  {activity.progress !== undefined && (
                    <div className="mt-3">
                      <div className="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span>{activity.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-300 ${
                            activity.status === 'completed' ? 'bg-green-500' :
                            activity.status === 'processing' ? 'bg-blue-500' :
                            activity.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
                          }`}
                          style={{ width: `${activity.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Timestamp */}
                  <div className="mt-2 text-xs text-gray-500">
                    {new Date(activity.created_at).toLocaleTimeString()}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentActivityMonitorStable;
