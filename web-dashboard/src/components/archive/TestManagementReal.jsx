import React, { useState, useEffect } from 'react';
import { 
  Play, 
  FileText, 
  Download, 
  Eye, 
  Settings, 
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  MoreVertical,
  Search,
  Filter,
  Plus
} from 'lucide-react';

const TestManagementReal = ({ user, onNavigate }) => {
  const [testSuites, setTestSuites] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedSuite, setSelectedSuite] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTestSuites();
  }, []);

  const loadTestSuites = () => {
    try {
      // Load the latest test suite from localStorage
      const latestSuite = localStorage.getItem('latest_test_suite');
      const allSuites = localStorage.getItem('all_test_suites');
      
      let suites = [];
      
      // Add the latest suite if it exists
      if (latestSuite) {
        const suite = JSON.parse(latestSuite);
        suites.push(suite);
      }
      
      // Add any other stored suites
      if (allSuites) {
        const storedSuites = JSON.parse(allSuites);
        // Merge with latest, avoiding duplicates
        storedSuites.forEach(stored => {
          if (!suites.find(s => s.id === stored.id)) {
            suites.push(stored);
          }
        });
      }
      
      // If no suites found, add some demo data for demonstration
      if (suites.length === 0) {
        suites = [
          {
            id: 'demo-1',
            name: 'E-commerce Demo Test Suite',
            application_name: 'E-commerce Store',
            application_url: 'https://demo-store.example.com',
            application_type: 'E-commerce',
            status: 'ready',
            created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
            test_count: 15,
            coverage: 92,
            features: ['User Authentication', 'Product Catalog', 'Shopping Cart', 'Checkout Process'],
            files: [
              { name: 'test_suite.py', type: 'python', size: '12.5 KB' },
              { name: 'page_objects.py', type: 'python', size: '8.2 KB' },
              { name: 'test_data.json', type: 'json', size: '3.1 KB' }
            ]
          }
        ];
      }
      
      setTestSuites(suites);
      setLoading(false);
    } catch (error) {
      console.error('Error loading test suites:', error);
      setLoading(false);
    }
  };

  const filteredSuites = testSuites.filter(suite => {
    const matchesSearch = suite.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         suite.application_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || suite.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const executeTestSuite = async (suite) => {
    try {
      // Here you would implement the actual test execution
      console.log('Executing test suite:', suite.id);
      
      // For now, show a success message
      alert(`🚀 Executing test suite: ${suite.name}\n\nThis will start the automated test execution process.`);
      
      // You could navigate to test results to show execution progress
      if (onNavigate) {
        onNavigate('results');
      }
    } catch (error) {
      console.error('Error executing test suite:', error);
      alert('Failed to execute test suite. Please try again.');
    }
  };

  const downloadTestSuite = (suite) => {
    // Create a downloadable file with test suite data
    const data = {
      suite_info: {
        name: suite.name,
        application: suite.application_name,
        url: suite.application_url,
        type: suite.application_type,
        created: suite.created_at
      },
      test_files: suite.files || [],
      features: suite.features || [],
      metadata: {
        test_count: suite.test_count,
        coverage: suite.coverage,
        status: suite.status
      }
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${suite.name.replace(/\s+/g, '_').toLowerCase()}_test_suite.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'running':
        return <Clock className="w-5 h-5 text-blue-500" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready':
        return 'bg-green-100 text-green-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Test Management</h1>
          <p className="text-gray-600">Manage and execute your AI-generated test suites</p>
        </div>
        <button
          onClick={() => onNavigate && onNavigate('create-test')}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Create New Tests</span>
        </button>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search test suites..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Status</option>
            <option value="ready">Ready</option>
            <option value="running">Running</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Test Suites List */}
      {filteredSuites.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchTerm || filterStatus !== 'all' ? 'No matching test suites' : 'No test suites found'}
          </h3>
          <p className="text-gray-500 mb-4">
            {searchTerm || filterStatus !== 'all' 
              ? 'Try adjusting your search or filter criteria'
              : 'Create your first test suite to get started'
            }
          </p>
          {!searchTerm && filterStatus === 'all' && (
            <button
              onClick={() => onNavigate && onNavigate('create-test')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Test Suite
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-6">
          {filteredSuites.map((suite) => (
            <div
              key={suite.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{suite.name}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(suite.status)}`}>
                      {suite.status}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-2">{suite.application_name}</p>
                  <p className="text-sm text-gray-500">{suite.application_url}</p>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(suite.status)}
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{suite.test_count}</div>
                  <div className="text-sm text-gray-500">Tests</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{suite.coverage}%</div>
                  <div className="text-sm text-gray-500">Coverage</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{suite.features?.length || 0}</div>
                  <div className="text-sm text-gray-500">Features</div>
                </div>
              </div>

              {/* Features */}
              {suite.features && suite.features.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Features Tested:</h4>
                  <div className="flex flex-wrap gap-2">
                    {suite.features.slice(0, 4).map((feature, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                      >
                        {feature}
                      </span>
                    ))}
                    {suite.features.length > 4 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                        +{suite.features.length - 4} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-500">
                  Created {new Date(suite.created_at).toLocaleDateString()}
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setSelectedSuite(selectedSuite?.id === suite.id ? null : suite)}
                    className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                    title="View Details"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => downloadTestSuite(suite)}
                    className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                    title="Download"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => executeTestSuite(suite)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                  >
                    <Play className="w-4 h-4" />
                    <span>Execute Tests</span>
                  </button>
                </div>
              </div>

              {/* Expanded Details */}
              {selectedSuite?.id === suite.id && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Test Files:</h4>
                  <div className="space-y-2">
                    {suite.files && suite.files.length > 0 ? (
                      suite.files.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <div className="flex items-center space-x-2">
                            <FileText className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-700">{file.name}</span>
                            <span className="text-xs text-gray-500">({file.size})</span>
                          </div>
                          <button className="text-blue-600 hover:text-blue-700 text-sm">
                            Download
                          </button>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-gray-500">No files available</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TestManagementReal;
