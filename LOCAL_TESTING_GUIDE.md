# Local Testing Guide for AutoGen AI Test Automation Framework

## Prerequisites

### 1. Python Environment
```bash
# Ensure you have Python 3.11+ installed
python3 --version

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

### 3. Local AI Setup (Optional but Recommended)
```bash
# Install Ollama for local AI models
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models
ollama pull phi3:mini
ollama pull tinyllama:latest

# Verify Ollama is running
ollama list
```

## Testing Steps

### Step 1: Test Agent Communication (Foundation Test)
```bash
# Test basic agent communication and data flow
python3 test_agent_communication.py
```

**Expected Output:**
- ✅ All 5 agents communicate properly
- ✅ Data flows correctly between agents
- ✅ 100% success rate
- Creates: `agent_communication_test_results_*.json`

### Step 2: Test Discovery Agent (New Feature)
```bash
# Test the new Discovery Agent capabilities
python3 test_discovery_agent.py
```

**Expected Output:**
- ✅ Application Analysis: Discovers 5 pages, 18+ elements, 3 workflows
- ✅ Page Element Discovery: Identifies forms, buttons, links
- ✅ Workflow Mapping: Maps authentication and shopping workflows
- ✅ Selector Generation: Creates robust element selectors
- ✅ 100% success rate
- Creates: `discovery_agent_test_results_*.json`
- Creates: `work_dir/DiscoveryAgent/application_analysis_*.json`

### Step 3: Test Real Scenarios (End-to-End Test)
```bash
# Test with real Advantage Online Shopping scenarios
python3 test_real_scenarios.py
```

**Expected Output:**
- ✅ Scenario Parsing: Processes advantage_shopping_scenarios.txt
- ✅ Planning Agent: Creates test plans from scenarios
- ✅ Test Creation Agent: Generates test files (currently templates)
- ⚠️ 75% success rate (template generation issue expected)
- Creates: `real_scenario_test_results_*.json`
- Creates: Generated test files in `work_dir/test_creation_agent/`

### Step 4: Test Complete Orchestrator (Integration Test)
```bash
# Test the complete multi-agent workflow
python3 comprehensive_agent_tests.py
```

**Expected Output:**
- ✅ All 5 specialized agents working
- ✅ Multi-agent coordination functional
- ✅ 100% success rate for agent validation
- Creates: Various result files and work artifacts

## What to Look For

### ✅ Success Indicators
1. **Agent Communication**: All agents respond and process tasks
2. **Discovery Agent**: 
   - Discovers application structure automatically
   - Generates element selectors (ID, CSS, XPath)
   - Maps user workflows with detailed steps
   - Provides framework recommendations
3. **Real Scenario Processing**: 
   - Parses text scenarios correctly
   - Creates comprehensive test plans
   - Generates test files (even if templates)
4. **File Generation**: 
   - JSON result files with detailed analysis
   - Test code files in work_dir folders
   - HTML reports from reporting agent

### ⚠️ Known Issues (Expected)
1. **Test Creation Agent**: Currently generates template code, not real executable tests
2. **Element Selectors**: Simulated selectors, not from real browser analysis
3. **Application Analysis**: Mock analysis, not real web scraping

### ❌ Failure Indicators
1. Import errors or missing dependencies
2. Agent initialization failures
3. 0% success rates in any test
4. No file generation in work_dir folders

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# If you get import errors
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Local AI Not Available
```bash
# Check if Ollama is running
ollama list

# If not installed, framework will work without local AI
# (will use mock responses)
```

#### 3. Permission Errors
```bash
# Ensure work_dir can be created
mkdir -p work_dir
chmod 755 work_dir
```

#### 4. JSON Serialization Errors
```bash
# If you see JSON serialization errors in test results
# This is usually fixed in the latest code, but if it occurs:
# Check the test result files are being created properly
```

## Expected File Structure After Testing

```
autogen-ai-test-automation/
├── work_dir/
│   ├── DiscoveryAgent/
│   │   └── application_analysis_*.json
│   ├── planning_agent/
│   │   └── test_plan_*.json
│   ├── test_creation_agent/
│   │   ├── test_*.py (generated test files)
│   │   ├── test_config.py
│   │   └── requirements.txt
│   ├── review_agent/
│   │   └── review_report_*.json
│   ├── execution_agent/
│   │   └── execution_results_*.json
│   └── reporting_agent/
│       ├── test_report_*.html
│       └── test_report_*.json
├── *_test_results_*.json (various test result files)
└── advantage_shopping_scenarios.txt
```

## Performance Benchmarks

### Current Framework Status
- **Agent Communication**: 100% success rate
- **Discovery Agent**: 100% success rate  
- **Real Scenario Processing**: 75% success rate
- **Overall Framework**: Foundation solid, ready for enhancement

### Next Phase Ready
The framework is now ready for:
1. **Enhanced Test Creation**: Generate real working code instead of templates
2. **Browser Integration**: Real application analysis using browser automation
3. **API Integration**: Real API testing capabilities
4. **Production Deployment**: Platform development

## Support

If you encounter issues:
1. Check the generated JSON result files for detailed error information
2. Verify all dependencies are installed correctly
3. Ensure Python 3.11+ is being used
4. Check that work_dir has proper permissions

The framework is designed to be resilient - even if local AI is not available, it will use mock responses to demonstrate the agent coordination and workflow.

