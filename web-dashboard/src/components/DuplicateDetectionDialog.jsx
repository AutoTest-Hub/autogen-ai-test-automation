import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { 
  AlertTriangle, 
  Clock, 
  RefreshCw, 
  CheckCircle,
  Copy,
  Edit,
  Plus
} from 'lucide-react';

const DuplicateDetectionDialog = ({ 
  isOpen, 
  onClose, 
  duplicateData, 
  onCreateNew, 
  onUpdateExisting, 
  onCancel 
}) => {
  const [selectedAction, setSelectedAction] = useState(null);
  const [selectedSuite, setSelectedSuite] = useState(null);

  if (!duplicateData) return null;

  const { has_duplicates, duplicate_type, existing_suites, recommendation, confidence, message } = duplicateData;

  const getTypeIcon = (type) => {
    switch (type) {
      case 'exact_name':
        return <Copy className="h-4 w-4 text-red-500" />;
      case 'similar_name':
        return <Edit className="h-4 w-4 text-yellow-500" />;
      case 'similar_content':
        return <RefreshCw className="h-4 w-4 text-blue-500" />;
      case 'recent_creation':
        return <Clock className="h-4 w-4 text-purple-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'exact_name':
        return 'Exact Name Match';
      case 'similar_name':
        return 'Similar Name';
      case 'similar_content':
        return 'Similar Content';
      case 'recent_creation':
        return 'Recent Creation';
      default:
        return 'Unknown';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-100 text-green-800">Completed</Badge>;
      case 'running':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Running</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleAction = () => {
    if (selectedAction === 'create_new') {
      onCreateNew();
    } else if (selectedAction === 'update_existing' && selectedSuite) {
      onUpdateExisting(selectedSuite);
    }
    onClose();
  };

  if (!has_duplicates) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              No Duplicates Found
            </DialogTitle>
            <DialogDescription>
              No existing test suites were found that match your configuration. You can proceed with creating a new test suite.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button onClick={onCreateNew} className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Create New Test Suite
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {getTypeIcon(duplicate_type)}
            Potential Duplicates Detected
          </DialogTitle>
          <DialogDescription>
            {message} (Confidence: {confidence}%)
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Duplicate Type Info */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                {getTypeIcon(duplicate_type)}
                {getTypeLabel(duplicate_type)}
              </CardTitle>
            </CardHeader>
          </Card>

          {/* Existing Suites */}
          <div className="space-y-3">
            <h4 className="font-medium">Existing Test Suites:</h4>
            {existing_suites.map((suite, index) => (
              <Card 
                key={index} 
                className={`cursor-pointer transition-colors ${
                  selectedSuite?.id === suite.id ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => setSelectedSuite(suite)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h5 className="font-medium">{suite.name}</h5>
                      <p className="text-sm text-muted-foreground mt-1">
                        {suite.description}
                      </p>
                      <div className="flex items-center gap-4 mt-2">
                        {getStatusBadge(suite.status)}
                        <span className="text-xs text-muted-foreground">
                          Created: {formatDate(suite.created_at)}
                        </span>
                        {suite.similarity_score && (
                          <span className="text-xs text-blue-600">
                            {suite.similarity_score}% similar
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Action Selection */}
          <div className="space-y-3">
            <h4 className="font-medium">What would you like to do?</h4>
            
            <div className="space-y-2">
              <Card 
                className={`cursor-pointer transition-colors ${
                  selectedAction === 'create_new' ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => setSelectedAction('create_new')}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <Plus className="h-5 w-5 text-green-500" />
                    <div>
                      <h5 className="font-medium">Create New Test Suite</h5>
                      <p className="text-sm text-muted-foreground">
                        Proceed with creating a new test suite anyway
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {recommendation === 'update_existing' && (
                <Card 
                  className={`cursor-pointer transition-colors ${
                    selectedAction === 'update_existing' ? 'ring-2 ring-blue-500' : ''
                  }`}
                  onClick={() => setSelectedAction('update_existing')}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <Edit className="h-5 w-5 text-blue-500" />
                      <div>
                        <h5 className="font-medium">Update Existing Test Suite</h5>
                        <p className="text-sm text-muted-foreground">
                          Update the selected existing test suite with new configuration
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button 
            onClick={handleAction}
            disabled={!selectedAction || (selectedAction === 'update_existing' && !selectedSuite)}
          >
            {selectedAction === 'create_new' ? 'Create New' : 'Update Selected'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default DuplicateDetectionDialog;
