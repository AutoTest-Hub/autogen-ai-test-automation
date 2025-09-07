# Contributing to AutoGen AI Test Automation Framework

Thank you for your interest in contributing to the AutoGen AI Test Automation Framework! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Git
- Ollama (for local AI models)
- Basic understanding of test automation concepts

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/autogen-ai-test-automation.git
   cd autogen-ai-test-automation
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv autogen_env
   source autogen_env/bin/activate  # Linux/macOS
   # autogen_env\Scripts\activate   # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama serve
   ollama pull phi3:mini
   ollama pull tinyllama:latest
   ```

5. **Run Tests**
   ```bash
   python fixed_quick_test.py
   ```

## 🎯 How to Contribute

### Types of Contributions

1. **Bug Reports**
   - Use GitHub Issues
   - Include detailed reproduction steps
   - Provide system information and logs

2. **Feature Requests**
   - Use GitHub Issues with "enhancement" label
   - Describe the use case and expected behavior
   - Consider backward compatibility

3. **Code Contributions**
   - Bug fixes
   - New features
   - Performance improvements
   - Documentation updates

4. **Documentation**
   - README improvements
   - Code comments
   - Usage examples
   - Tutorial content

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test Your Changes**
   ```bash
   python fixed_quick_test.py
   # Run additional tests as needed
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write descriptive docstrings
- Keep functions focused and small

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

**Examples:**
```
feat(agents): add new planning agent capabilities
fix(parser): resolve JSON schema validation issue
docs(readme): update installation instructions
```

### Code Organization

```
autogen-ai-test-automation/
├── agents/                 # AI agent implementations
├── models/                 # Local AI integration
├── config/                 # Configuration management
├── orchestrator/           # Multi-agent coordination
├── parsers/               # File parsing utilities
├── sample_scenarios/      # Example test scenarios
├── tests/                 # Unit and integration tests
└── docs/                  # Documentation
```

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests**
   - Test individual components
   - Mock external dependencies
   - Fast execution

2. **Integration Tests**
   - Test component interactions
   - Use real local AI models
   - Validate end-to-end workflows

3. **System Tests**
   - Test complete scenarios
   - Validate against real applications
   - Performance and reliability testing

### Writing Tests

```python
import pytest
from agents.standalone_base_agent import StandalonePlanningAgent

def test_planning_agent_creation():
    """Test planning agent initialization"""
    agent = StandalonePlanningAgent()
    assert agent.name == "planning_agent"
    assert agent.role.value == "planning"

def test_scenario_parsing():
    """Test scenario file parsing"""
    # Test implementation
    pass
```

### Running Tests

```bash
# Run quick validation
python fixed_quick_test.py

# Run specific test modules (when pytest is set up)
pytest tests/test_agents.py
pytest tests/test_parsers.py

# Run all tests with coverage
pytest --cov=. tests/
```

## 📚 Documentation

### Code Documentation
- Use clear, descriptive docstrings
- Include parameter and return type information
- Provide usage examples

```python
def parse_scenario_file(self, file_path: str) -> Dict[str, Any]:
    """
    Parse a test scenario file and extract test information.
    
    Args:
        file_path: Absolute path to the scenario file
        
    Returns:
        Dictionary containing parsed scenario data with keys:
        - success: Boolean indicating parse success
        - scenario: Parsed scenario object
        - error: Error message if parsing failed
        
    Example:
        >>> parser = ScenarioParser()
        >>> result = parser.parse_scenario_file("test.txt")
        >>> if result["success"]:
        ...     print(result["scenario"]["name"])
    """
```

### README Updates
- Keep installation instructions current
- Update feature lists
- Include new examples
- Maintain compatibility information

## 🔧 Architecture Guidelines

### Agent Development
- Inherit from `StandaloneBaseAgent`
- Implement role-specific functionality
- Use appropriate AI model types
- Handle errors gracefully

### Parser Development
- Support multiple file formats
- Validate input data
- Provide detailed error messages
- Maintain backward compatibility

### Local AI Integration
- Use `LocalAIProvider` for AI interactions
- Handle model availability gracefully
- Implement fallback mechanisms
- Optimize for performance

## 🚀 Release Process

### Version Numbering
- Follow Semantic Versioning (SemVer)
- Format: MAJOR.MINOR.PATCH
- Example: 1.2.3

### Release Checklist
1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release tag
6. Publish release notes

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

### Getting Help
- Check existing issues and documentation
- Ask questions in GitHub Discussions
- Provide context and examples
- Be patient and helpful to others

## 📞 Contact

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Security**: Report security issues privately

## 🎉 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to the AutoGen AI Test Automation Framework! 🚀

