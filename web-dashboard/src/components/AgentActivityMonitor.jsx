import React, { useState, useEffect, useRef } from 'react';
import { Activity, Bot, CheckCircle, AlertCircle, Clock, Zap, Eye, Play, Pause, RotateCcw } from 'lucide-react';

const AgentActivityMonitor = ({ userId, taskId = null, className = "" }) => {
  const [activities, setActivities] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [systemStats, setSystemStats] = useState({
    activeAgents: 0,
    completedTasks: 0,
    totalActivities: 0
  });
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [autoScroll, setAutoScroll] = useState(true);
  
  const wsRef = useRef(null);
  const activitiesEndRef = useRef(null);

  // WebSocket connection management
  useEffect(() => {
    if (!userId) return;

    const connectWebSocket = () => {
      try {
        const wsUrl = `ws://localhost:8000/api/v1/ws/agent-activity/${userId}`;
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          console.log('WebSocket connected');
          setConnectionStatus('connected');
          
          // Request current activities
          wsRef.current.send(JSON.stringify({
            type: 'get_activities'
          }));
        };

        wsRef.current.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected');
          setConnectionStatus('disconnected');
          
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };

        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnectionStatus('error');
        };

      } catch (error) {
        console.error('Error creating WebSocket connection:', error);
        setConnectionStatus('error');
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId]);

  // Handle WebSocket messages
  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'connection_established':
        console.log('WebSocket connection established');
        break;
        
      case 'activities_list':
        setActivities(message.activities || []);
        updateSystemStats(message.activities || []);
        break;
        
      case 'activity_created':
        setActivities(prev => [message.activity, ...prev]);
        break;
        
      case 'activity_update':
      case 'progress_update':
      case 'status_update':
        setActivities(prev => 
          prev.map(activity => 
            activity.id === message.activity_id || activity.id === message.activity?.id
              ? { ...activity, ...(message.activity || {}) }
              : activity
          )
        );
        break;
        
      case 'log_update':
        setActivities(prev =>
          prev.map(activity =>
            activity.id === message.activity_id
              ? {
                  ...activity,
                  logs: [...(activity.logs || []), message.log]
                }
              : activity
          )
        );
        break;
        
      case 'task_completed':
      case 'task_failed':
        // Handle task completion
        console.log(`Task ${message.task?.id} ${message.type.split('_')[1]}`);
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  };

  // Update system statistics
  const updateSystemStats = (activitiesList) => {
    const activeAgents = activitiesList.filter(
      activity => !['completed', 'error'].includes(activity.status)
    ).length;
    
    const completedTasks = activitiesList.filter(
      activity => activity.status === 'completed'
    ).length;

    setSystemStats({
      activeAgents,
      completedTasks,
      totalActivities: activitiesList.length
    });
  };

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && activitiesEndRef.current) {
      activitiesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activities, autoScroll]);

  // Get status color and icon
  const getStatusDisplay = (status) => {
    const statusMap = {
      idle: { color: 'text-gray-500', bgColor: 'bg-gray-100', icon: Clock },
      initializing: { color: 'text-blue-500', bgColor: 'bg-blue-100', icon: RotateCcw },
      analyzing: { color: 'text-purple-500', bgColor: 'bg-purple-100', icon: Eye },
      processing: { color: 'text-orange-500', bgColor: 'bg-orange-100', icon: Play },
      generating: { color: 'text-indigo-500', bgColor: 'bg-indigo-100', icon: Zap },
      validating: { color: 'text-yellow-500', bgColor: 'bg-yellow-100', icon: CheckCircle },
      completed: { color: 'text-green-500', bgColor: 'bg-green-100', icon: CheckCircle },
      error: { color: 'text-red-500', bgColor: 'bg-red-100', icon: AlertCircle },
      paused: { color: 'text-gray-500', bgColor: 'bg-gray-100', icon: Pause }
    };
    
    return statusMap[status] || statusMap.idle;
  };

  // Get agent type display
  const getAgentTypeDisplay = (agentType) => {
    const agentMap = {
      discovery: { name: 'Discovery Agent', color: 'bg-blue-500', icon: '🔍' },
      requirements: { name: 'Requirements Agent', color: 'bg-purple-500', icon: '📋' },
      test_generation: { name: 'Test Generation Agent', color: 'bg-green-500', icon: '🧪' },
      code_generation: { name: 'Code Generation Agent', color: 'bg-orange-500', icon: '💻' },
      validation: { name: 'Validation Agent', color: 'bg-yellow-500', icon: '✅' },
      execution: { name: 'Execution Agent', color: 'bg-red-500', icon: '🚀' },
      reporting: { name: 'Reporting Agent', color: 'bg-indigo-500', icon: '📊' },
      self_healing: { name: 'Self-Healing Agent', color: 'bg-teal-500', icon: '🔧' },
      prioritization: { name: 'Prioritization Agent', color: 'bg-pink-500', icon: '📈' },
      cross_browser: { name: 'Cross-Browser Agent', color: 'bg-cyan-500', icon: '🌐' },
      performance: { name: 'Performance Agent', color: 'bg-emerald-500', icon: '⚡' }
    };
    
    return agentMap[agentType] || { name: agentType, color: 'bg-gray-500', icon: '🤖' };
  };

  // Filter activities by task if specified
  const filteredActivities = taskId 
    ? activities.filter(activity => activity.task_id === taskId)
    : activities;

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
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-500' : 
                connectionStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500'
              }`} />
              <span className="text-sm text-gray-600 capitalize">
                {connectionStatus}
              </span>
            </div>
            
            {/* Auto-scroll toggle */}
            <button
              onClick={() => setAutoScroll(!autoScroll)}
              className={`p-2 rounded-lg transition-colors ${
                autoScroll 
                  ? 'bg-blue-100 text-blue-600' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              title="Toggle auto-scroll"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
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
        {filteredActivities.length === 0 ? (
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
            {filteredActivities.map((activity) => {
              const statusDisplay = getStatusDisplay(activity.status);
              const agentDisplay = getAgentTypeDisplay(activity.agent_type);
              const StatusIcon = statusDisplay.icon;
              
              return (
                <div
                  key={activity.id}
                  className={`border rounded-lg p-4 transition-all duration-200 hover:shadow-md cursor-pointer ${
                    selectedActivity?.id === activity.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedActivity(
                    selectedActivity?.id === activity.id ? null : activity
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {/* Agent Type Badge */}
                      <div className={`w-8 h-8 ${agentDisplay.color} rounded-full flex items-center justify-center text-white text-sm`}>
                        {agentDisplay.icon}
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {agentDisplay.name}
                        </h4>
                        <p className="text-sm text-gray-500">
                          {activity.current_step || 'Waiting...'}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      {/* Progress */}
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${activity.progress}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600 min-w-[3rem]">
                          {activity.progress}%
                        </span>
                      </div>
                      
                      {/* Status */}
                      <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${statusDisplay.bgColor}`}>
                        <StatusIcon className={`w-4 h-4 ${statusDisplay.color}`} />
                        <span className={`text-xs font-medium ${statusDisplay.color} capitalize`}>
                          {activity.status}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Expanded Details */}
                  {selectedActivity?.id === activity.id && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <span className="text-sm font-medium text-gray-700">Task ID:</span>
                          <p className="text-sm text-gray-600 font-mono">{activity.task_id}</p>
                        </div>
                        <div>
                          <span className="text-sm font-medium text-gray-700">Duration:</span>
                          <p className="text-sm text-gray-600">
                            {activity.duration ? `${activity.duration.toFixed(1)}s` : 'In progress...'}
                          </p>
                        </div>
                        <div>
                          <span className="text-sm font-medium text-gray-700">Steps:</span>
                          <p className="text-sm text-gray-600">
                            {activity.steps_completed} / {activity.total_steps}
                          </p>
                        </div>
                        <div>
                          <span className="text-sm font-medium text-gray-700">Started:</span>
                          <p className="text-sm text-gray-600">
                            {new Date(activity.start_time).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                      
                      {/* Recent Logs */}
                      {activity.logs && activity.logs.length > 0 && (
                        <div>
                          <h5 className="text-sm font-medium text-gray-700 mb-2">Recent Activity:</h5>
                          <div className="bg-gray-50 rounded-lg p-3 max-h-32 overflow-y-auto">
                            {activity.logs.slice(-5).map((log, index) => (
                              <div key={index} className="text-xs text-gray-600 mb-1">
                                <span className="text-gray-400">
                                  {new Date(log.timestamp).toLocaleTimeString()}
                                </span>
                                {' - '}
                                <span className={
                                  log.level === 'error' ? 'text-red-600' :
                                  log.level === 'warning' ? 'text-yellow-600' :
                                  'text-gray-600'
                                }>
                                  {log.message}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
            <div ref={activitiesEndRef} />
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentActivityMonitor;
