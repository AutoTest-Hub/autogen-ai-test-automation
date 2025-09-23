# Local Testing Instructions - Three-Tier System

## Overview

This guide provides comprehensive instructions for setting up and testing the enhanced three-tier test automation system locally. The system includes intelligent discovery, multi-tier test generation, and AutoGen collaboration capabilities.

## Prerequisites

Before beginning, ensure your system meets the following requirements:

**System Requirements:**
- Python 3.8 or higher with pip package manager
- Node.js 16+ for Playwright browser automation
- Git for version control and repository management
- At least 4GB RAM and 2GB free disk space
- Stable internet connection for browser downloads and API access

**Optional Requirements:**
- OpenAI API key for AutoGen collaboration features
- Docker for containerized testing environments
- Visual Studio Code or similar IDE for development

## Installation and Setup

### Step 1: Repository Setup

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/AutoTest-Hub/autogen-ai-test-automation.git
cd autogen-ai-test-automation
```

### Step 2: Python Environment Setup

Create and activate a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

Install all required Python packages:

```bash
# Install core dependencies
pip install -r requirements.txt

# Install additional packages for enhanced features
pip install autogen-agentchat  # For AutoGen collaboration (optional)
pip install pytest-html pytest-json-report  # For enhanced reporting
pip install pytest-xdist  # For parallel test execution
```

### Step 4: Browser Setup

Install Playwright browsers for test execution:

```bash
# Install Playwright browsers
playwright install

# Verify installation
playwright --version
```

### Step 5: Configuration Setup

Create configuration files for your testing environment:

```bash
# Copy configuration templates
cp config/config.template.json config/config.json
cp config/test_config.template.json config/test_config.json
```

Edit the configuration files to match your testing requirements:

```json
{
  "default_timeout": 30,
  "headless": true,
  "browser": "chromium",
  "viewport": {"width": 1920, "height": 1080},
  "enable_autogen": true,
  "discovery_depth": "comprehensive",
  "complexity_level": "high"
}
```

## Testing the Enhanced System

### Basic System Verification

Verify that all components are properly installed and configured:

```bash
# Test Python environment
python -c "import pytest, playwright; print('Core dependencies OK')"

# Test enhanced agents
python -c "from agents.enhanced_discovery_agent import create_enhanced_discovery_agent; print('Enhanced agents OK')"

# Test three-tier system
python -c "from utils.step_generator import create_step_generator; print('Three-tier system OK')"
```

### Running the Enhanced Workflow

Execute the complete three-tier workflow with a test application:

```bash
# Run with comprehensive configuration
python proper_multi_agent_workflow.py \
  --url "https://demo.automationexercise.com" \
  --app-name "demo_app" \
  --enable-autogen \
  --complexity-level high \
  --discovery-depth comprehensive
```

### Testing Individual Components

Test each component of the three-tier system independently:

#### Enhanced Discovery Agent
```bash
# Test enhanced discovery
python -c "
import asyncio
from agents.enhanced_discovery_agent import create_enhanced_discovery_agent

async def test_discovery():
    agent = create_enhanced_discovery_agent()
    result = await agent.process_task({
        'type': 'enhanced_discovery',
        'url': 'https://demo.automationexercise.com',
        'analysis_depth': 'comprehensive'
    })
    print(f'Discovery status: {result.get(\"status\")}')

asyncio.run(test_discovery())
"
```

#### Three-Tier Step Generator
```bash
# Test step generator
python -c "
from utils.step_generator import create_step_generator

generator = create_step_generator()
test_suite = generator.generate_comprehensive_test_suite(
    {'pages': {'login': {'elements': []}}},
    {'flow_types': ['user_journey']}
)
print(f'Generated tiers: {list(test_suite.keys())}')
"
```

#### AutoGen Test Creation
```bash
# Test AutoGen integration (requires OpenAI API key)
export OPENAI_API_KEY="your-api-key-here"

python -c "
import asyncio
from agents.autogen_test_creation_agent import create_autogen_test_creation_agent

async def test_autogen():
    agent = create_autogen_test_creation_agent()
    result = await agent.process_task({
        'type': 'create_tests',
        'discovery_data': {'pages': {}},
        'requirements': {'app_name': 'test_app'}
    })
    print(f'AutoGen status: {result.get(\"status\")}')

asyncio.run(test_autogen())
"
```

#### Integrated Test Generator
```bash
# Test complete integration
python -c "
import asyncio
from agents.integrated_test_generator import create_integrated_test_generator

async def test_integration():
    generator = create_integrated_test_generator()
    result = await generator.process_task({
        'type': 'integrated_generation',
        'url': 'https://demo.automationexercise.com',
        'app_name': 'demo_app',
        'config': {'discovery_depth': 'comprehensive'}
    })
    print(f'Integration status: {result.get(\"status\")}')

asyncio.run(test_integration())
"
```

## Advanced Testing Scenarios

### Testing with Different Applications

Test the system with various application types to verify versatility:

```bash
# E-commerce application
python proper_multi_agent_workflow.py \
  --url "https://demo.automationexercise.com" \
  --app-name "ecommerce_demo"

# Business application
python proper_multi_agent_workflow.py \
  --url "https://opensource-demo.orangehrmlive.com" \
  --app-name "orangehrm_demo"

# Custom application
python proper_multi_agent_workflow.py \
  --url "https://your-app.com" \
  --app-name "custom_app"
```

### Performance Testing

Evaluate system performance with different configurations:

```bash
# Measure generation time
time python proper_multi_agent_workflow.py \
  --url "https://demo.automationexercise.com" \
  --app-name "perf_test" \
  --complexity-level high

# Test with parallel execution
python proper_multi_agent_workflow.py \
  --url "https://demo.automationexercise.com" \
  --app-name "parallel_test" \
  --enable-parallel
```

### Quality Assessment Testing

Verify quality metrics and assessment capabilities:

```bash
# Run with quality assessment enabled
python proper_multi_agent_workflow.py \
  --url "https://demo.automationexercise.com" \
  --app-name "quality_test" \
  --enable-quality-assessment \
  --minimum-quality-score 85
```

## Executing Generated Tests

After generating tests, execute them to verify functionality:

### Basic Test Execution
```bash
# Run all generated tests
pytest tests/ -v

# Run with HTML report
pytest tests/ --html=reports/test_report.html --self-contained-html

# Run with JSON report
pytest tests/ --json-report --json-report-file=reports/test_report.json
```

### Tier-Specific Execution
```bash
# Run Tier 1 tests (basic functionality)
pytest tests/ -k "tier1" -v

# Run Tier 2 tests (intelligent flows)
pytest tests/ -k "tier2" -v

# Run Tier 3 tests (advanced scenarios)
pytest tests/ -k "tier3" -v
```

### Parallel Test Execution
```bash
# Run tests in parallel
pytest tests/ -n auto -v

# Run with specific worker count
pytest tests/ -n 4 -v
```

## Troubleshooting Common Issues

### Installation Issues

**Problem**: Playwright installation fails
**Solution**: 
```bash
# Clear Playwright cache and reinstall
playwright uninstall --all
playwright install
```

**Problem**: Python dependency conflicts
**Solution**:
```bash
# Create fresh virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Runtime Issues

**Problem**: Discovery agent fails to analyze application
**Solution**:
- Verify application URL is accessible
- Check network connectivity
- Increase timeout values in configuration
- Try with headless=false for debugging

**Problem**: AutoGen collaboration fails
**Solution**:
- Verify OpenAI API key is set correctly
- Check API quota and billing status
- Try with fallback mode disabled
- Review AutoGen configuration parameters

**Problem**: Generated tests fail to execute
**Solution**:
- Verify application is accessible during test execution
- Check element selectors in generated tests
- Review test data and configuration
- Run tests with --pdb for debugging

### Performance Issues

**Problem**: Slow test generation
**Solution**:
- Reduce discovery depth for initial testing
- Disable AutoGen collaboration temporarily
- Use focused complexity levels
- Check system resources and network speed

**Problem**: High memory usage
**Solution**:
- Reduce parallel execution workers
- Clear browser cache between tests
- Monitor system resources
- Use headless mode for better performance

## Validation and Quality Checks

### System Health Checks

Run comprehensive system health checks:

```bash
# Create health check script
cat > health_check.py << 'EOF'
import asyncio
import sys
from agents.enhanced_discovery_agent import create_enhanced_discovery_agent
from agents.integrated_test_generator import create_integrated_test_generator
from utils.step_generator import create_step_generator

async def health_check():
    print("Running system health checks...")
    
    # Test discovery agent
    try:
        discovery_agent = create_enhanced_discovery_agent()
        print("✓ Enhanced Discovery Agent: OK")
    except Exception as e:
        print(f"✗ Enhanced Discovery Agent: FAILED - {e}")
        return False
    
    # Test step generator
    try:
        step_generator = create_step_generator()
        print("✓ Step Generator: OK")
    except Exception as e:
        print(f"✗ Step Generator: FAILED - {e}")
        return False
    
    # Test integrated generator
    try:
        integrated_generator = create_integrated_test_generator()
        print("✓ Integrated Test Generator: OK")
    except Exception as e:
        print(f"✗ Integrated Test Generator: FAILED - {e}")
        return False
    
    print("All health checks passed!")
    return True

if __name__ == "__main__":
    result = asyncio.run(health_check())
    sys.exit(0 if result else 1)
EOF

python health_check.py
```

### Quality Validation

Validate generated test quality:

```bash
# Run quality validation
python -c "
import json
from pathlib import Path

# Check for generated artifacts
work_dir = Path('work_dir')
if work_dir.exists():
    artifacts = list(work_dir.rglob('*.json'))
    print(f'Found {len(artifacts)} artifacts')
    
    for artifact in artifacts[:3]:  # Show first 3
        with open(artifact) as f:
            data = json.load(f)
            print(f'Artifact: {artifact.name}')
            print(f'Status: {data.get(\"status\", \"unknown\")}')
else:
    print('No artifacts found - run workflow first')
"
```

## Best Practices for Local Testing

### Development Workflow

Follow this recommended workflow for local development and testing:

1. **Start with Basic Verification**: Always run health checks before beginning development
2. **Use Incremental Testing**: Test individual components before running full workflows
3. **Monitor Resource Usage**: Keep an eye on memory and CPU usage during testing
4. **Maintain Clean Environment**: Regularly clean up generated artifacts and logs
5. **Document Issues**: Keep track of issues and solutions for future reference

### Configuration Management

Maintain different configuration profiles for various testing scenarios:

```bash
# Create configuration profiles
mkdir -p config/profiles

# Development profile
cat > config/profiles/development.json << 'EOF'
{
  "headless": false,
  "discovery_depth": "basic",
  "complexity_level": "medium",
  "enable_autogen": false,
  "timeout": 15
}
EOF

# Production profile
cat > config/profiles/production.json << 'EOF'
{
  "headless": true,
  "discovery_depth": "comprehensive",
  "complexity_level": "high",
  "enable_autogen": true,
  "timeout": 30
}
EOF
```

### Continuous Improvement

Regularly assess and improve your local testing setup:

- **Performance Monitoring**: Track generation and execution times
- **Quality Metrics**: Monitor test quality scores and coverage
- **Resource Optimization**: Optimize configuration for your hardware
- **Feature Updates**: Stay updated with new system capabilities

## Support and Resources

### Documentation Resources
- **System Architecture**: See `COMPREHENSIVE_SYSTEM_REPORT.md`
- **API Documentation**: Check individual agent files for detailed API docs
- **Configuration Reference**: Review configuration templates and examples

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Join community discussions for tips and best practices
- **Contributing**: Contribute improvements and enhancements

### Professional Support
For enterprise deployments and professional support, contact the development team through the official channels.

---

**Last Updated**: 2024-09-22  
**Version**: 1.0  
**Compatibility**: Python 3.8+, Playwright 1.30+
