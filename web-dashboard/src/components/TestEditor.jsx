import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Code, 
  Eye, 
  Edit3, 
  Save, 
  X, 
  Plus, 
  Trash2, 
  Play, 
  CheckCircle, 
  AlertTriangle,
  User,
  Settings,
  FileText,
  Zap
} from 'lucide-react';

const TestEditor = ({ testSuite, testCases, onSave, onClose, apiService }) => {
  const [activeTab, setActiveTab] = useState('visual');
  const [editedTestCases, setEditedTestCases] = useState([]);
  const [suiteInfo, setSuiteInfo] = useState({
    name: testSuite?.name || '',
    description: testSuite?.description || ''
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (testCases) {
      setEditedTestCases(testCases.map(tc => ({
        ...tc,
        steps: tc.steps || [
          { action: 'navigate', target: testSuite?.application_url, description: 'Navigate to application' },
          { action: 'click', target: '', description: 'Click element' },
          { action: 'verify', target: '', description: 'Verify result' }
        ]
      })));
    }
  }, [testCases, testSuite]);

  const handleTestCaseUpdate = (index, field, value) => {
    const updated = [...editedTestCases];
    updated[index] = { ...updated[index], [field]: value };
    setEditedTestCases(updated);
  };

  const handleStepUpdate = (testIndex, stepIndex, field, value) => {
    const updated = [...editedTestCases];
    updated[testIndex].steps[stepIndex] = { 
      ...updated[testIndex].steps[stepIndex], 
      [field]: value 
    };
    setEditedTestCases(updated);
  };

  const addTestStep = (testIndex) => {
    const updated = [...editedTestCases];
    updated[testIndex].steps.push({
      action: 'click',
      target: '',
      description: 'New test step'
    });
    setEditedTestCases(updated);
  };

  const removeTestStep = (testIndex, stepIndex) => {
    const updated = [...editedTestCases];
    updated[testIndex].steps.splice(stepIndex, 1);
    setEditedTestCases(updated);
  };

  const addNewTestCase = () => {
    const newTestCase = {
      id: `new-${Date.now()}`,
      name: 'New Test Case',
      description: 'Description of the new test case',
      status: 'draft',
      steps: [
        { action: 'navigate', target: testSuite?.application_url, description: 'Navigate to application' }
      ]
    };
    setEditedTestCases([...editedTestCases, newTestCase]);
  };

  const removeTestCase = (index) => {
    const updated = [...editedTestCases];
    updated.splice(index, 1);
    setEditedTestCases(updated);
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      // Save suite info and test cases
      const saveData = {
        suite: suiteInfo,
        testCases: editedTestCases
      };

      await apiService.updateTestSuite(testSuite.id, saveData);
      setSuccess('Test suite updated successfully!');
      onSave && onSave(saveData);
    } catch (err) {
      setError(`Failed to save changes: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const generateCodePreview = (testCase) => {
    const steps = testCase.steps || [];
    return `// ${testCase.name}
describe('${testCase.name}', () => {
  it('${testCase.description}', async () => {
${steps.map(step => {
  switch (step.action) {
    case 'navigate':
      return `    await page.goto('${step.target}');`;
    case 'click':
      return `    await page.click('${step.target}');`;
    case 'type':
      return `    await page.type('${step.target}', '${step.value || ''}');`;
    case 'verify':
      return `    await expect(page.locator('${step.target}')).toBeVisible();`;
    default:
      return `    // ${step.description}`;
  }
}).join('\n')}
  });
});`;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold">Edit Test Suite</h2>
            <p className="text-muted-foreground">{testSuite?.application_name}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Error/Success Messages */}
          {error && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="mb-4 border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{success}</AlertDescription>
            </Alert>
          )}

          {/* Suite Information */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Test Suite Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="suiteName">Suite Name</Label>
                <Input
                  id="suiteName"
                  value={suiteInfo.name}
                  onChange={(e) => setSuiteInfo({...suiteInfo, name: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="suiteDescription">Description</Label>
                <Textarea
                  id="suiteDescription"
                  value={suiteInfo.description}
                  onChange={(e) => setSuiteInfo({...suiteInfo, description: e.target.value})}
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          {/* Test Cases Editor */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Test Cases ({editedTestCases.length})
                </div>
                <Button onClick={addNewTestCase} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Test Case
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="visual" className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Visual Editor (Non-Technical)
                  </TabsTrigger>
                  <TabsTrigger value="code" className="flex items-center gap-2">
                    <Code className="h-4 w-4" />
                    Code View (Technical)
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="visual" className="space-y-6">
                  {editedTestCases.map((testCase, testIndex) => (
                    <Card key={testCase.id || testIndex} className="border-l-4 border-l-blue-500">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex-1 space-y-2">
                            <Input
                              value={testCase.name}
                              onChange={(e) => handleTestCaseUpdate(testIndex, 'name', e.target.value)}
                              className="font-semibold"
                              placeholder="Test case name"
                            />
                            <Textarea
                              value={testCase.description}
                              onChange={(e) => handleTestCaseUpdate(testIndex, 'description', e.target.value)}
                              placeholder="Test case description"
                              rows={2}
                            />
                          </div>
                          <div className="flex items-center gap-2 ml-4">
                            <Badge variant={testCase.status === 'passed' ? 'default' : 'secondary'}>
                              {testCase.status}
                            </Badge>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeTestCase(testIndex)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <Label className="text-sm font-medium">Test Steps</Label>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => addTestStep(testIndex)}
                            >
                              <Plus className="h-3 w-3 mr-1" />
                              Add Step
                            </Button>
                          </div>
                          
                          {testCase.steps?.map((step, stepIndex) => (
                            <div key={stepIndex} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-medium">
                                {stepIndex + 1}
                              </div>
                              
                              <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-3">
                                <Select
                                  value={step.action}
                                  onValueChange={(value) => handleStepUpdate(testIndex, stepIndex, 'action', value)}
                                >
                                  <SelectTrigger>
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="navigate">Navigate</SelectItem>
                                    <SelectItem value="click">Click</SelectItem>
                                    <SelectItem value="type">Type Text</SelectItem>
                                    <SelectItem value="verify">Verify</SelectItem>
                                    <SelectItem value="wait">Wait</SelectItem>
                                  </SelectContent>
                                </Select>
                                
                                <Input
                                  placeholder="Target element or URL"
                                  value={step.target}
                                  onChange={(e) => handleStepUpdate(testIndex, stepIndex, 'target', e.target.value)}
                                />
                                
                                <Input
                                  placeholder="Description"
                                  value={step.description}
                                  onChange={(e) => handleStepUpdate(testIndex, stepIndex, 'description', e.target.value)}
                                />
                              </div>
                              
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeTestStep(testIndex, stepIndex)}
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </TabsContent>

                <TabsContent value="code" className="space-y-4">
                  {editedTestCases.map((testCase, testIndex) => (
                    <Card key={testCase.id || testIndex}>
                      <CardHeader>
                        <CardTitle className="text-lg">{testCase.name}</CardTitle>
                        <CardDescription>{testCase.description}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm">
                          <code>{generateCodePreview(testCase)}</code>
                        </pre>
                      </CardContent>
                    </Card>
                  ))}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <div className="text-sm text-muted-foreground">
            {editedTestCases.length} test case{editedTestCases.length !== 1 ? 's' : ''} • 
            Last modified: {new Date().toLocaleDateString()}
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <>
                  <Zap className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestEditor;
