"""
AutoGen-Based Agentic Test Automation Framework Configuration
"""

import os
from typing import Dict, List, Optional, Any
from pydantic_settings import BaseSettings
from pydantic import Field
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"


class TestFramework(str, Enum):
    """Supported test automation frameworks"""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    REQUESTS = "requests"
    HTTPX = "httpx"


class AgentRole(str, Enum):
    """Agent roles in the system"""
    ORCHESTRATOR = "orchestrator"
    PLANNING = "planning"
    TEST_CREATION = "test_creation"
    REVIEW = "review"
    EXECUTION = "execution"
    REPORTING = "reporting"
    DISCOVERY = "discovery"


class AutoGenTestFrameworkSettings(BaseSettings):
    """Configuration settings for the AutoGen Test Automation Framework"""
    
    # Application settings
    app_name: str = Field(default="AutoGen Test Automation Framework", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # LLM Configuration
    default_llm_provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="Default LLM provider")
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_api_base: Optional[str] = Field(default=None, description="OpenAI API base URL")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model to use")
    openai_temperature: float = Field(default=0.1, description="OpenAI temperature")
    openai_max_tokens: int = Field(default=4000, description="OpenAI max tokens")
    
    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", description="Anthropic model to use")
    anthropic_temperature: float = Field(default=0.1, description="Anthropic temperature")
    anthropic_max_tokens: int = Field(default=4000, description="Anthropic max tokens")
    
    # Google Configuration
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    google_model: str = Field(default="gemini-1.5-pro", description="Google model to use")
    google_temperature: float = Field(default=0.1, description="Google temperature")
    google_max_tokens: int = Field(default=4000, description="Google max tokens")
    
    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    azure_openai_endpoint: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    azure_openai_deployment: str = Field(default="gpt-4", description="Azure OpenAI deployment name")
    azure_openai_api_version: str = Field(default="2024-02-01", description="Azure OpenAI API version")
    
    # Agent Configuration
    max_round: int = Field(default=10, description="Maximum conversation rounds")
    max_consecutive_auto_reply: int = Field(default=5, description="Maximum consecutive auto replies")
    human_input_mode: str = Field(default="NEVER", description="Human input mode (ALWAYS, TERMINATE, NEVER)")
    
    # Test Framework Configuration
    default_test_framework: TestFramework = Field(default=TestFramework.PLAYWRIGHT, description="Default test framework")
    browser_type: str = Field(default="chromium", description="Browser type for UI testing")
    headless: bool = Field(default=False, description="Run browser in headless mode")
    browser_timeout: int = Field(default=30000, description="Browser timeout in milliseconds")
    
    # Test Execution Configuration
    max_parallel_tests: int = Field(default=5, description="Maximum parallel test executions")
    test_timeout: int = Field(default=300, description="Test timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts for failed tests")
    retry_delay: int = Field(default=5, description="Delay between retry attempts in seconds")
    
    # File Processing Configuration
    supported_input_formats: List[str] = Field(default=[".txt", ".json"], description="Supported input file formats")
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    batch_processing_size: int = Field(default=10, description="Batch processing size")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///autogen_test_framework.db", description="Database URL")
    
    # Monitoring Configuration
    enable_monitoring: bool = Field(default=True, description="Enable monitoring and metrics")
    metrics_port: int = Field(default=8090, description="Metrics server port")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Web Interface Configuration
    web_interface_enabled: bool = Field(default=True, description="Enable web interface")
    web_interface_host: str = Field(default="0.0.0.0", description="Web interface host")
    web_interface_port: int = Field(default=8080, description="Web interface port")
    
    # Security Configuration
    enable_cors: bool = Field(default=True, description="Enable CORS")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    api_key_required: bool = Field(default=False, description="Require API key for access")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    
    # Quality Gates Configuration
    min_code_quality_score: float = Field(default=0.8, description="Minimum code quality score")
    require_review_approval: bool = Field(default=True, description="Require review agent approval")
    max_review_iterations: int = Field(default=3, description="Maximum review iterations")
    
    # Reporting Configuration
    generate_html_reports: bool = Field(default=True, description="Generate HTML reports")
    generate_json_reports: bool = Field(default=True, description="Generate JSON reports")
    generate_pdf_reports: bool = Field(default=False, description="Generate PDF reports")
    report_retention_days: int = Field(default=30, description="Report retention period in days")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def get_llm_config(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """Get LLM configuration for specified provider"""
        provider = provider or self.default_llm_provider
        
        if provider == LLMProvider.OPENAI:
            return {
                "model": self.openai_model,
                "api_key": self.openai_api_key or os.getenv("OPENAI_API_KEY"),
                "base_url": self.openai_api_base or os.getenv("OPENAI_API_BASE"),
                "temperature": self.openai_temperature,
                "max_tokens": self.openai_max_tokens,
            }
        elif provider == LLMProvider.ANTHROPIC:
            return {
                "model": self.anthropic_model,
                "api_key": self.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"),
                "temperature": self.anthropic_temperature,
                "max_tokens": self.anthropic_max_tokens,
            }
        elif provider == LLMProvider.GOOGLE:
            return {
                "model": self.google_model,
                "api_key": self.google_api_key or os.getenv("GOOGLE_API_KEY"),
                "temperature": self.google_temperature,
                "max_tokens": self.google_max_tokens,
            }
        elif provider == LLMProvider.AZURE_OPENAI:
            return {
                "model": self.azure_openai_deployment,
                "api_key": self.azure_openai_api_key or os.getenv("AZURE_OPENAI_API_KEY"),
                "azure_endpoint": self.azure_openai_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT"),
                "api_version": self.azure_openai_api_version,
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def get_agent_config(self, role: AgentRole) -> Dict[str, Any]:
        """Get agent-specific configuration"""
        base_config = {
            "max_consecutive_auto_reply": self.max_consecutive_auto_reply,
            "human_input_mode": self.human_input_mode,
            "llm_config": self.get_llm_config(),
        }
        
        # Role-specific configurations
        role_configs = {
            AgentRole.ORCHESTRATOR: {
                "name": "orchestrator_agent",
                "system_message": "You are the Orchestrator Agent responsible for coordinating the entire test automation workflow.",
            },
            AgentRole.PLANNING: {
                "name": "planning_agent",
                "system_message": "You are the Planning Agent responsible for analyzing requirements and creating comprehensive test strategies.",
            },
            AgentRole.TEST_CREATION: {
                "name": "test_creation_agent",
                "system_message": "You are the Test Creation Agent responsible for generating high-quality test automation code.",
            },
            AgentRole.REVIEW: {
                "name": "review_agent",
                "system_message": "You are the Review Agent responsible for reviewing and validating generated test code.",
            },
            AgentRole.EXECUTION: {
                "name": "execution_agent",
                "system_message": "You are the Execution Agent responsible for running tests and monitoring execution.",
            },
            AgentRole.REPORTING: {
                "name": "reporting_agent",
                "system_message": "You are the Reporting Agent responsible for analyzing results and generating insights.",
            },
        }
        
        base_config.update(role_configs.get(role, {}))
        return base_config


# Global settings instance
settings = AutoGenTestFrameworkSettings()

