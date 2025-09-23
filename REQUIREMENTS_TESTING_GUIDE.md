# Requirements JSON Testing Guide

## Overview

This guide explains how to use the three comprehensive requirements JSON files with the enhanced three-tier test automation system. Each file contains detailed test scenarios, configurations, and business rules for different application types.

## Available Requirements Files

### 1. `requirements_ecommerce.json`
- **Application Type**: E-commerce platform
- **Target URL**: https://demo.automationexercise.com
- **Focus Areas**: Product browsing, shopping cart, checkout, user authentication
- **Test Scenarios**: 6 comprehensive scenarios
- **Special Features**: Payment processing, inventory management, user journeys

### 2. `requirements_hrms.json`
- **Application Type**: Human Resource Management System
- **Target URL**: https://opensource-demo.orangehrmlive.com
- **Focus Areas**: Employee management, leave management, attendance, performance
- **Test Scenarios**: 7 enterprise scenarios
- **Special Features**: Role-based access, workflow validations, compliance

### 3. `requirements_banking.json`
- **Application Type**: Financial/Banking application
- **Target URL**: https://demo.testfire.net
- **Focus Areas**: Account management, transactions, security, compliance
- **Test Scenarios**: 7 financial scenarios
- **Special Features**: Security validations, regulatory compliance, fraud detection

## Local Testing Instructions

### Prerequisites

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AutoTest-Hub/autogen-ai-test-automation.git
   cd autogen-ai-test-automation
   git checkout phase-9.5-implementation
   ```

2. **Install Dependencies**
   ```bash
   pip install pytest pytest-asyncio pytest-html pytest-json-report playwright pyautogen
   playwright install chromium
   ```

3. **Verify System Components**
   ```bash
   # Test enhanced discovery agent
   python -c "from agents.enhanced_discovery_agent import create_enhanced_discovery_agent; print('✓ Enhanced Discovery Agent')"
   
   # Test step generator
   python -c "from utils.step_generator import create_step_generator; print('✓ Step Generator')"
   
   # Test intelligent flow handler
   python -c "from utils.intelligent_flow_handler import create_intelligent_flow_handler; print('✓ Intelligent Flow Handler')"
   
   # Test integrated generator
   python -c "import asyncio; from agents.integrated_test_generator import create_integrated_test_generator; asyncio.run(create_integrated_test_generator().get_capabilities()); print('✓ Integrated Test Generator')"
   ```

### Method 1: Using the Enhanced Workflow Script

#### Basic Usage
```bash
# Test E-commerce application
bash run_proper_multi_agent_workflow.sh --url "https://demo.automationexercise.com" --name "ecommerce_test" --no-headless

# Test HRMS application
bash run_proper_multi_agent_workflow.sh --url "https://opensource-demo.orangehrmlive.com" --name "hrms_test" --no-headless

# Test Banking application
bash run_proper_multi_agent_workflow.sh --url "https://demo.testfire.net" --name "banking_test" --no-headless
```

#### Advanced Usage with Requirements Files
```bash
# Create a custom script to use requirements files
cat > test_with_requirements.py << 'EOF'
import json
import asyncio
import sys
from agents.integrated_test_generator import create_integrated_test_generator

async def test_with_requirements(requirements_file):
    # Load requirements
    with open(requirements_file, 'r') as f:
        requirements = json.load(f)
    
    print(f"Testing {requirements['app_name']} ({requirements['application_type']})")
    print(f"URL: {requirements['base_url']}")
    
    # Create integrated generator
    generator = create_integrated_test_generator()
    
    # Configure task
    task_data = {
        'type': 'integrated_generation',
        'url': requirements['base_url'],
        'app_name': requirements['app_name'],
        'config': {
            'discovery_depth': 'comprehensive',
            'enable_autogen': True,  # Enable for full features
            'complexity_level': 'high',
            'requirements_data': requirements
        }
    }
    
    # Execute test generation
    result = await generator.process_task(task_data)
    
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'success':
        summary = result.get('summary', {})
        print(f"Workflow ID: {result.get('workflow_id')}")
        print(f"Phases Completed: {summary.get('phases_completed', 0)}")
        
        artifacts = summary.get('artifacts_generated', {})
        print(f"Test Files: {artifacts.get('test_files', 0)}")
        print(f"Documentation: {artifacts.get('documentation', 0)}")
        print(f"Configuration: {artifacts.get('configuration', 0)}")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_with_requirements.py <requirements_file>")
        sys.exit(1)
    
    asyncio.run(test_with_requirements(sys.argv[1]))
EOF

# Run tests with requirements files
python test_with_requirements.py requirements_ecommerce.json
python test_with_requirements.py requirements_hrms.json
python test_with_requirements.py requirements_banking.json
```

### Method 2: Direct Python Integration

#### Test Individual Components
```python
import json
import asyncio
from agents.enhanced_discovery_agent import create_enhanced_discovery_agent
from utils.step_generator import create_step_generator
from utils.intelligent_flow_handler import create_intelligent_flow_handler

async def test_components_with_requirements():
    # Load requirements
    with open('requirements_ecommerce.json', 'r') as f:
        requirements = json.load(f)
    
    # Test Enhanced Discovery
    discovery_agent = create_enhanced_discovery_agent()
    discovery_task = {
        'type': 'enhanced_discovery',
        'url': requirements['base_url'],
        'analysis_depth': 'comprehensive',
        'requirements_context': requirements
    }
    discovery_result = await discovery_agent.process_task(discovery_task)
    
    # Test Step Generator
    step_generator = create_step_generator()
    test_suite = step_generator.generate_comprehensive_test_suite(
        discovery_result.get('discovery_data', {}),
        requirements
    )
    
    # Test Flow Handler
    flow_handler = create_intelligent_flow_handler()
    flow_analysis = flow_handler.analyze_application_flows(
        discovery_result.get('discovery_data', {})
    )
    
    print(f"Discovery Status: {discovery_result.get('status')}")
    print(f"Test Suite Tiers: {list(test_suite.keys())}")
    print(f"Flow Analysis: {list(flow_analysis.keys())}")

# Run the test
asyncio.run(test_components_with_requirements())
```

### Method 3: Custom Test Scenarios

#### Create Custom Requirements
```python
# Create a custom requirements file
custom_requirements = {
    "app_name": "my_custom_app",
    "base_url": "https://your-app-url.com",
    "application_type": "custom",
    "priority_areas": ["authentication", "core_functionality"],
    "test_scenarios": {
        "login_test": {
            "priority": "high",
            "description": "Test user login functionality",
            "test_data": {
                "valid_credentials": [
                    {"username": "testuser", "password": "testpass"}
                ]
            },
            "expected_elements": [
                "input[name='username']",
                "input[name='password']",
                "button[type='submit']"
            ]
        }
    },
    "test_environment": {
        "headless": True,
        "timeout": 30000
    }
}

# Save custom requirements
import json
with open('requirements_custom.json', 'w') as f:
    json.dump(custom_requirements, indent=2)

# Test with custom requirements
python test_with_requirements.py requirements_custom.json
```

## Understanding Requirements File Structure

### Core Sections

1. **Application Metadata**
   - `app_name`: Unique identifier for the application
   - `base_url`: Target application URL
   - `application_type`: Type classification (ecommerce, enterprise_hrms, financial_banking)
   - `description`: Detailed application description

2. **Test Configuration**
   - `priority_areas`: Key functional areas to focus testing on
   - `test_scenarios`: Detailed test case definitions with data and expectations
   - `business_rules`: Application-specific business logic constraints
   - `test_environment`: Browser and execution settings

3. **Advanced Features**
   - `security_requirements`: Security validation rules
   - `performance_requirements`: Performance benchmarks
   - `integration_points`: External system integrations
   - `accessibility_requirements`: WCAG compliance levels

### Test Scenario Structure
```json
{
  "scenario_name": {
    "priority": "high|medium|low",
    "description": "What this test validates",
    "test_data": {
      "valid_inputs": [...],
      "invalid_inputs": [...],
      "edge_cases": [...]
    },
    "expected_elements": [
      "CSS selectors for key elements"
    ],
    "validation_rules": {
      "success_criteria": "What indicates success",
      "failure_conditions": "What indicates failure"
    }
  }
}
```

## Expected Results

### Successful Test Execution Should Produce:

1. **Generated Test Files**
   - Playwright test files for each scenario
   - Page object models for application pages
   - Configuration files (conftest.py, pytest.ini)

2. **Documentation**
   - Test execution reports (HTML and JSON)
   - Coverage analysis
   - Quality assessment reports

3. **Artifacts**
   - Screenshots on failure
   - Execution logs
   - Performance metrics

### Output Locations
- **Test Files**: `tests/` directory
- **Page Objects**: `pages/` directory
- **Reports**: `work_dir/reporting_agent/` directory
- **Logs**: `work_dir/` subdirectories by agent

## Troubleshooting

### Common Issues

1. **Network Connectivity**
   ```bash
   # Test if target URLs are accessible
   curl -I https://demo.automationexercise.com
   curl -I https://opensource-demo.orangehrmlive.com
   curl -I https://demo.testfire.net
   ```

2. **Missing Dependencies**
   ```bash
   # Reinstall all dependencies
   pip install -r requirements.txt
   playwright install
   ```

3. **Browser Issues**
   ```bash
   # Install specific browser
   playwright install chromium
   
   # Test browser installation
   playwright --version
   ```

4. **Local AI Issues**
   ```bash
   # Check if Ollama is running (for local AI features)
   curl http://localhost:11434/api/tags
   
   # If not available, system will fallback to external APIs
   ```

### Debug Mode
```bash
# Run with debug logging
export PYTHONPATH=$PWD
export LOG_LEVEL=DEBUG
python test_with_requirements.py requirements_ecommerce.json
```

## Advanced Configuration

### Environment Variables
```bash
# Set OpenAI API key for AutoGen features
export OPENAI_API_KEY="your-api-key"

# Configure local AI endpoint
export OLLAMA_HOST="http://localhost:11434"

# Set test environment
export TEST_ENV="local"
export HEADLESS_MODE="true"
```

### Custom Configuration Files
Create `config/local_settings.py`:
```python
# Override default settings
DEFAULT_TIMEOUT = 60000
RETRY_ATTEMPTS = 3
SCREENSHOT_ON_FAILURE = True
VIDEO_RECORDING = False

# Browser settings
BROWSER_ARGS = [
    "--disable-web-security",
    "--disable-features=VizDisplayCompositor"
]
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Requirements Testing
on: [push, pull_request]

jobs:
  test-requirements:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        requirements: [ecommerce, hrms, banking]
    
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install chromium
    
    - name: Test requirements
      run: |
        python test_with_requirements.py requirements_${{ matrix.requirements }}.json
    
    - name: Upload reports
      uses: actions/upload-artifact@v3
      with:
        name: test-reports-${{ matrix.requirements }}
        path: work_dir/reporting_agent/
```

## Performance Optimization

### Parallel Execution
```bash
# Run multiple requirements in parallel
python test_with_requirements.py requirements_ecommerce.json &
python test_with_requirements.py requirements_hrms.json &
python test_with_requirements.py requirements_banking.json &
wait
```

### Resource Management
```python
# Configure for resource-constrained environments
task_config = {
    'discovery_depth': 'basic',  # Reduce discovery complexity
    'enable_autogen': False,     # Disable AutoGen for faster execution
    'complexity_level': 'medium', # Reduce test complexity
    'parallel_execution': False   # Sequential execution
}
```

This comprehensive guide provides everything needed to effectively test and use the requirements JSON files with the enhanced three-tier test automation system.
