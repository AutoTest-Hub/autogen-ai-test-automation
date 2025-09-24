import React, { useState, useEffect, useRef } from 'react';
import { Activity, Bot, CheckCircle, AlertCircle, Clock, Zap, Eye, Play, Pause, RotateCcw } from 'lucide-react';

const AgentActivityMonitor = ({ userId, taskId = null, className = "", onTaskComplete, ...props }) => {
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

  // WebSocket connection management with improved stability
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 10;
  const baseReconnectDelay = 1000; // 1 second

  useEffect(() => {
    if (!userId) return;

    const connectWebSocket = () => {
      try {
        // Clear any existing reconnection timeout
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }

        const wsUrl = `ws://localhost:8000/api/v1/ws/agent-activity/${userId}`;
        console.log(`Attempting WebSocket connection to: ${wsUrl}`);
        
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          console.log('WebSocket connected successfully');
          setConnectionStatus('connected');
          reconnectAttemptsRef.current = 0; // Reset reconnect attempts on successful connection
          
          // Request current activities with error handling
          try {
            wsRef.current.send(JSON.stringify({
              type: 'get_activities',
              user_id: userId
            }));
          } catch (error) {
            console.error('Error sending initial message:', error);
          }
        };

        wsRef.current.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error, event.data);
          }
        };

        wsRef.current.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          setConnectionStatus('disconnected');
          
          // Only attempt reconnection if we haven't exceeded max attempts
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            const delay = Math.min(baseReconnectDelay * Math.pow(2, reconnectAttemptsRef.current), 30000);
            console.log(`Attempting reconnection in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
            
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttemptsRef.current++;
              setConnectionStatus('reconnecting');
              connectWebSocket();
            }, delay);
          } else {
            console.error('Max reconnection attempts reached');
            setConnectionStatus('failed');
          }
        };

        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnectionStatus('error');
        };

      } catch (error) {
        console.error('Error creating WebSocket connection:', error);
        setConnectionStatus('error');
        
        // Attempt reconnection on connection creation error
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(baseReconnectDelay * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connectWebSocket();
          }, delay);
        }
      }
    };

    connectWebSocket();

    return () => {
      // Clean up on unmount
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId]);

  // Handle WebSocket messages
  const handleWebSocketMessage = (message) => {
    console.log('WebSocket message received:', message.type, message);
    
    switch (message.type) {
      case 'connection_established':
        console.log('WebSocket connection established');
        break;
        
      case 'activities_list':
        console.log('Activities list received:', message.activities);
        console.log('Number of activities:', (message.activities || []).length);
        setActivities(message.activities || []);
        updateSystemStats(message.activities || []);
        break;
        
      case 'activity_created':
        console.log('Activity created:', message.activity);
        setActivities(prev => {
          // Check if activity already exists to avoid duplicates
          const exists = prev.some(activity => activity.id === message.activity.id);
          if (!exists) {
            return [message.activity, ...prev];
          }
          return prev;
        });
        break;
        
      case 'activity_update':
      case 'progress_update':
      case 'status_update':
        console.log('Activity update:', message.type, message);
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
        
        // Close WebSocket connection to stop continuous polling
        if (wsRef.current) {
          console.log('Closing WebSocket connection after task completion');
          wsRef.current.close();
          wsRef.current = null;
          setConnectionStatus('disconnected');
        }
        
        // Notify parent component if callback is provided
        if (onTaskComplete) {
          console.log('Calling onTaskComplete callback with:', {
            taskId: message.task?.id,
            status: message.type.split('_')[1],
            task: message.task,
            error: message.error
          });
          onTaskComplete({
            taskId: message.task?.id,
            status: message.type.split('_')[1], // 'completed' or 'failed'
            task: message.task,
            error: message.error
          });
        } else {
          console.log('No onTaskComplete callback provided');
        }
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
                connectionStatus === 'reconnecting' ? 'bg-yellow-500 animate-pulse' :
                connectionStatus === 'error' || connectionStatus === 'failed' ? 'bg-red-500' : 
                'bg-gray-500'
              }`} />
              <span className="text-sm text-gray-600 capitalize">
                {connectionStatus === 'reconnecting' ? 'Reconnecting...' : connectionStatus}
              </span>
              {connectionStatus === 'failed' && (
                <button
                  onClick={() => {
                    reconnectAttemptsRef.current = 0;
                    setConnectionStatus('disconnected');
                    // Trigger reconnection by updating userId dependency
                    const currentUserId = userId;
                    setTimeout(() => {
                      if (wsRef.current) {
                        wsRef.current.close();
                      }
                    }, 100);
                  }}
                  className="text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                  title="Retry connection"
                >
                  Retry
                </button>
              )}
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
            {/* Show all 4 agents in sequence with their current status */}
            {(() => {
              // Define the expected agent sequence
              const agentSequence = ['discovery', 'test_generation', 'code_generation', 'validation'];
              
              // Group activities by agent type and get the latest activity for each
              const agentGroups = filteredActivities.reduce((groups, activity) => {
                const agentType = activity.agent_type || 'unknown';
                if (!groups[agentType] || new Date(activity.created_at) > new Date(groups[agentType].created_at)) {
                  groups[agentType] = activity;
                }
                return groups;
              }, {});
              
              // Create display for all agents in sequence
              return agentSequence.map((agentType) => {
                const activity = agentGroups[agentType];
                
                // If no activity for this agent yet, show as pending
                if (!activity) {
                  const agentDisplay = getAgentTypeDisplay(agentType);
                  return (
                    <div
                      key={agentType}
                      className="border rounded-lg p-4 border-gray-200 bg-gray-50 opacity-60"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                          <span className="font-medium text-gray-600">{agentDisplay.name}</span>
                        </div>
                        <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded-full">
                          Pending
                        </span>
                      </div>
                      <p className="text-sm text-gray-500">Waiting to start...</p>
                    </div>
                  );
                }
                
                // Show actual activity
                return activity;
              }).filter(Boolean);
            })().map((activity, index) => {
              if (typeof activity !== 'object' || !activity.agent_type) {
                return activity; // Return pending agent display as-is
              }
              
              const statusDisplay = getStatusDisplay(activity.status);
              const agentDisplay = getAgentTypeDisplay(activity.agent_type);
              const StatusIcon = statusDisplay.icon;
              
              return (
                <div
                  key={activity.agent_type || index}
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
