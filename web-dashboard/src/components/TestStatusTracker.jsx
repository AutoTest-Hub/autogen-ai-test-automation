import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { 
  Bot, 
  CheckCircle, 
  Clock, 
  RefreshCw, 
  AlertTriangle,
  Zap,
  Target,
  Code,
  Shield
} from 'lucide-react';

const TestStatusTracker = ({ jobId, apiService, onComplete, onError }) => {
  const [status, setStatus] = useState('initializing');
  const [phases, setPhases] = useState([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [currentAgent, setCurrentAgent] = useState('');
  const [startTime, setStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Agent phase definitions with icons
  const agentPhases = [
    { 
      name: 'Discovery Agent', 
      description: 'Analyzing application structure and user flows',
      icon: Target,
      color: 'blue'
    },
    { 
      name: 'Generation Agent', 
      description: 'Creating comprehensive test scenarios',
      icon: Zap,
      color: 'purple'
    },
    { 
      name: 'Code Agent', 
      description: 'Generating automated test code',
      icon: Code,
      color: 'green'
    },
    { 
      name: 'Validation Agent', 
      description: 'Validating and optimizing test suite',
      icon: Shield,
      color: 'orange'
    }
  ];

  useEffect(() => {
    if (!jobId) return;

    setStartTime(Date.now());
    const interval = setInterval(async () => {
      try {
        const response = await apiService.getAgentJobStatus(jobId);
        
        if (response && response.data) {
          setStatus(response.data.status);
          setPhases(response.data.phases || []);
          setOverallProgress(response.data.progress_percentage || 0);
          setCurrentAgent(response.data.current_agent || '');

          // Handle completion
          if (response.data.status === 'completed') {
            clearInterval(interval);
            onComplete && onComplete(jobId);
          } else if (response.data.status === 'failed') {
            clearInterval(interval);
            onError && onError('Test creation failed');
          }
        }
      } catch (error) {
        console.error('Status polling error:', error);
      }
    }, 2000);

    // Update elapsed time
    const timeInterval = setInterval(() => {
      if (startTime) {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(timeInterval);
    };
  }, [jobId, apiService, onComplete, onError, startTime]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'running':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Running</Badge>;
      case 'completed':
        return <Badge variant="default" className="bg-green-100 text-green-800">Completed</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return <Badge variant="secondary">Initializing</Badge>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 animate-pulse text-blue-500" />
            <CardTitle>AI Agents Working</CardTitle>
          </div>
          <div className="flex items-center gap-4">
            {getStatusBadge()}
            <span className="text-sm text-muted-foreground">
              {formatTime(elapsedTime)}
            </span>
          </div>
        </div>
        <CardDescription>
          Real-time progress of AI agents creating your tests
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-sm text-muted-foreground">{overallProgress}%</span>
          </div>
          <Progress value={overallProgress} className="h-3" />
          {currentAgent && (
            <p className="text-xs text-blue-600">Current: {currentAgent}</p>
          )}
        </div>

        {/* Agent Phases */}
        <div className="space-y-4">
          {agentPhases.map((phase, index) => {
            const progress = phases.find(p => p.name === phase.name);
            const isActive = progress?.status === 'running';
            const isComplete = progress?.status === 'completed';
            const isFailed = progress?.status === 'failed';
            const progressPercent = progress?.progress || 0;
            const PhaseIcon = phase.icon;

            return (
              <div key={index} className="space-y-2">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    isComplete ? 'bg-green-100 text-green-600' :
                    isActive ? 'bg-blue-100 text-blue-600' :
                    isFailed ? 'bg-red-100 text-red-600' :
                    'bg-gray-100 text-gray-400'
                  }`}>
                    {isComplete ? (
                      <CheckCircle className="h-5 w-5" />
                    ) : isActive ? (
                      <RefreshCw className="h-5 w-5 animate-spin" />
                    ) : isFailed ? (
                      <AlertTriangle className="h-5 w-5" />
                    ) : (
                      <PhaseIcon className="h-5 w-5" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{phase.name}</h4>
                      {(isActive || isComplete) && (
                        <span className="text-xs text-muted-foreground">{progressPercent}%</span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{phase.description}</p>
                    {progress?.message && (
                      <p className="text-xs text-blue-600 mt-1">{progress.message}</p>
                    )}
                  </div>
                </div>
                {(isActive || isComplete) && (
                  <div className="ml-14">
                    <Progress value={progressPercent} className="h-2" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Status Messages */}
        {status === 'completed' && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="font-medium text-green-800">Test Creation Completed!</span>
            </div>
            <p className="text-sm text-green-700 mt-1">
              Your test suite has been successfully generated and is ready for execution.
            </p>
          </div>
        )}

        {status === 'failed' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <span className="font-medium text-red-800">Test Creation Failed</span>
            </div>
            <p className="text-sm text-red-700 mt-1">
              There was an error during test creation. Please try again or contact support.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TestStatusTracker;
