# AutoGen Test Automation Framework - Setup and Testing Guide

## 🚀 Complete Setup and Testing Instructions

This guide provides step-by-step instructions to set up and test the enhanced AutoGen Test Automation Framework with local AI integration.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB+ for local AI models
- **Storage**: 10GB+ free space for models and framework
- **Python**: 3.9+ (3.11 recommended)
- **Network**: Internet access for initial setup

### Required Software
- Python 3.9+
- pip (Python package manager)
- Git (for version control)
- curl (for Ollama installation)

## 🔧 Installation Steps

### Step 1: Clone/Extract Framework
```bash
# If you have the framework package
cd /path/to/complete_autogen_framework_package

# Or clone from repository (if available)
# git clone <repository-url>
# cd autogen-test-framework
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv autogen_env

# Activate virtual environment
# On Linux/macOS:
source autogen_env/bin/activate

# On Windows:
# autogen_env\Scripts\activate
```

### Step 3: Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# If you encounter permission issues, use:
pip install --user -r requirements.txt
```

### Step 4: Install Ollama (Local AI)
```bash
# Install Ollama for local AI models
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# In a new terminal, download recommended models
ollama pull phi3:mini        # For code generation and analysis
ollama pull tinyllama:latest # For fast general tasks

# Verify installation
ollama list
```

### Step 5: Install Browser Dependencies (Optional)
```bash
# For web automation testing
playwright install
playwright install-deps
```

## 🧪 Testing the Framework

### Test 1: Basic Framework Initialization
```bash
# Test basic framework components
python framework_integration_demo.py
```

**Expected Output:**
- Framework structure display
- Integration points explanation
- Workflow example
- Benefits overview
- Status confirmation

### Test 2: Local AI Integration Test
```bash
# Test local AI provider
python -c "
from models.local_ai_provider import LocalAIProvider, ModelType
provider = LocalAIProvider()
print('Local AI Status:', provider.get_status_report())
if provider.is_available():
    result = provider.generate_response_sync('Hello, test message', ModelType.GENERAL_INTELLIGENCE)
    print('AI Response:', result)
else:
    print('Local AI not available - check Ollama installation')
"
```

**Expected Output:**
- Local AI service status
- Available models list
- Test AI response (if models are loaded)

### Test 3: Agent Creation and Integration
```bash
# Test agent creation with local AI
python -c "
import asyncio
from enhanced_main_framework import EnhancedAutoGenFramework

async def test_agents():
    framework = EnhancedAutoGenFramework(use_local_ai=True)
    result = await framework.initialize()
    print('Initialization Result:')
    print(result)
    
    status = framework.get_framework_status()
    print('Framework Status:')
    print(status)

asyncio.run(test_agents())
"
```

**Expected Output:**
- Framework initialization success
- Agent creation confirmation
- Local AI integration status
- Agent status reports

### Test 4: Scenario File Processing
Create a test scenario file:

```bash
# Create test scenario
cat > test_scenario.txt << 'EOF'
Test Name: Simple Login Test
Target: https://www.advantageonlineshopping.com/#/
Priority: Medium
Tags: login, authentication

Description: Test user login functionality

Test Steps:
1. Navigate to the website
2. Click on user account icon
3. Enter username 'helios'
4. Enter password 'Password123'
5. Click Sign In button
6. Verify successful login
EOF
```

```bash
# Test scenario processing
python -c "
import asyncio
from enhanced_main_framework import EnhancedAutoGenFramework

async def test_scenario():
    framework = EnhancedAutoGenFramework(use_local_ai=True)
    await framework.initialize()
    
    result = await framework.process_scenario_file('test_scenario.txt')
    print('Scenario Processing Result:')
    print(result)

asyncio.run(test_scenario())
"
```

**Expected Output:**
- Scenario parsing success
- Agent workflow execution
- Generated test artifacts
- Complete processing results

### Test 5: Complete Framework Demo
```bash
# Run complete framework demonstration
python enhanced_main_framework.py
```

**Expected Output:**
- Framework initialization
- Sample scenario processing
- Multi-agent collaboration
- Generated test files
- Final status report

## 📊 Verification Checklist

### ✅ Installation Verification
- [ ] Python 3.9+ installed and accessible
- [ ] Virtual environment created and activated
- [ ] All pip packages installed successfully
- [ ] Ollama service running (`ollama list` shows models)
- [ ] At least one AI model downloaded (phi3:mini or tinyllama)

### ✅ Framework Verification
- [ ] `framework_integration_demo.py` runs without errors
- [ ] Local AI provider connects to Ollama
- [ ] Agents initialize with local AI integration
- [ ] Scenario parsing works for .txt files
- [ ] Multi-agent workflows execute successfully

### ✅ Feature Verification
- [ ] Local AI models respond to prompts
- [ ] Agents use appropriate model types
- [ ] Scenario files generate test artifacts
- [ ] Framework saves generated code to disk
- [ ] Status reporting shows healthy system

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Ollama Connection Issues
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama service
pkill ollama
ollama serve

# Check Ollama API
curl http://localhost:11434/api/tags
```

#### 2. Memory Issues with Models
```bash
# Use smaller models if you have limited RAM
ollama pull tinyllama:latest  # ~637MB
ollama pull phi3:mini         # ~2.3GB

# Check system memory
free -h
```

#### 3. Python Import Errors
```bash
# Ensure virtual environment is activated
which python
pip list | grep autogen

# Reinstall if needed
pip install --force-reinstall autogen-agentchat
```

#### 4. Permission Issues
```bash
# Use user installation if needed
pip install --user -r requirements.txt

# Or fix permissions
sudo chown -R $USER:$USER ~/.local/
```

## 🎯 Advanced Testing

### Performance Testing
```bash
# Test with multiple scenarios
for i in {1..5}; do
    echo "Test run $i"
    python enhanced_main_framework.py
done
```

### Load Testing
```bash
# Test concurrent agent operations
python -c "
import asyncio
from enhanced_main_framework import EnhancedAutoGenFramework

async def load_test():
    tasks = []
    for i in range(3):
        framework = EnhancedAutoGenFramework(use_local_ai=True)
        tasks.append(framework.initialize())
    
    results = await asyncio.gather(*tasks)
    print(f'Concurrent initialization results: {len(results)} successful')

asyncio.run(load_test())
"
```

### Integration Testing
```bash
# Test with real web application
python -c "
import asyncio
from enhanced_main_framework import EnhancedAutoGenFramework

async def integration_test():
    framework = EnhancedAutoGenFramework(use_local_ai=True)
    await framework.initialize()
    
    # Test with Advantage Online Shopping
    result = await framework.process_scenario_file('test_scenario.txt')
    
    if result['success']:
        print('✅ Integration test passed')
        print(f'Generated {len(result.get(\"results\", []))} test artifacts')
    else:
        print('❌ Integration test failed')
        print(f'Error: {result.get(\"error\")}')

asyncio.run(integration_test())
"
```

## 📈 Performance Expectations

### Local AI Performance
- **Response Time**: 2-10 seconds per AI inference (depending on model size)
- **Memory Usage**: 2-6GB RAM (depending on loaded models)
- **Concurrent Agents**: 3-5 agents simultaneously (with 16GB RAM)

### Framework Performance
- **Scenario Processing**: 30-120 seconds per scenario (depending on complexity)
- **Agent Initialization**: 5-15 seconds for complete framework
- **File Generation**: 1-5 seconds for test artifact creation

## 🎉 Success Indicators

### Framework is Working Correctly When:
1. **All tests pass** without errors
2. **Local AI responds** to prompts within reasonable time
3. **Agents initialize** with correct model assignments
4. **Scenario processing** generates complete test artifacts
5. **Generated code** is syntactically correct and executable
6. **Status reports** show healthy system state

### Ready for Production When:
1. **Performance meets** your requirements
2. **All security features** are configured
3. **Enterprise deployment** is tested
4. **Internal network access** is configured (if needed)
5. **Monitoring and logging** are set up

## 🚀 Next Steps

After successful testing:

1. **Deploy to Production Environment**
   - Set up on enterprise hardware (16GB+ RAM)
   - Configure enterprise security settings
   - Set up monitoring and alerting

2. **Configure for Internal Applications**
   - Set up VPN connectivity
   - Configure internal network access
   - Test with internal applications

3. **Create Custom Scenarios**
   - Write scenario files for your applications
   - Test with your specific use cases
   - Optimize agent configurations

4. **Scale the Deployment**
   - Deploy multiple framework instances
   - Set up load balancing
   - Configure high availability

## 📞 Support

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Review the logs** for detailed error messages
3. **Verify system requirements** are met
4. **Test with minimal configuration** first
5. **Gradually add complexity** once basic setup works

The framework is designed to be robust and self-healing, but proper setup is crucial for optimal performance.

---

**🎯 You now have a complete, enterprise-ready AI test automation framework with local AI capabilities!**

