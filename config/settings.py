import os
from typing import Dict, List, Optional, Any
from enum import Enum

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"

class TestFramework(str, Enum):
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    REQUESTS = "requests"
    HTTPX = "httpx"

class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    PLANNING = "planning"
    TEST_CREATION = "test_creation"
    REVIEW = "review"
    EXECUTION = "execution"
    REPORTING = "reporting"
    DISCOVERY = "discovery"

class AutoGenTestFrameworkSettings:
    app_name: str = "AutoGen Test Automation Framework"
    app_version: str = "1.0.0"
    debug: bool = False
    default_llm_provider: LLMProvider = LLMProvider.OPENAI
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 4000
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    anthropic_temperature: float = 0.1
    anthropic_max_tokens: int = 4000
    google_api_key: Optional[str] = None
    google_model: str = "gemini-1.5-pro"
    google_temperature: float = 0.1
    google_max_tokens: int = 4000
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_deployment: str = "gpt-4"
    azure_openai_api_version: str = "2024-02-01"
    max_round: int = 10
    max_consecutive_auto_reply: int = 5
    human_input_mode: str = "NEVER"
    default_test_framework: TestFramework = TestFramework.PLAYWRIGHT
    browser_type: str = "chromium"
    headless: bool = False
    browser_timeout: int = 30000
    max_parallel_tests: int = 5
    test_timeout: int = 300
    retry_attempts: int = 3
    retry_delay: int = 5
    supported_input_formats: List[str] = [".txt", ".json"]
    max_file_size_mb: int = 10
    batch_processing_size: int = 10
    database_url: str = "sqlite:///autogen_test_framework.db"
    enable_monitoring: bool = True
    metrics_port: int = 8090
    log_level: str = "INFO"
    web_interface_enabled: bool = True
    web_interface_host: str = "0.0.0.0"
    web_interface_port: int = 8080
    enable_cors: bool = True
    cors_origins: List[str] = ["*"]
    api_key_required: bool = False
    api_key: Optional[str] = None
    min_code_quality_score: float = 0.8
    require_review_approval: bool = True
    max_review_iterations: int = 3
    generate_html_reports: bool = True
    generate_json_reports: bool = True
    generate_pdf_reports: bool = False
    report_retention_days: int = 30

    def get_llm_config(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
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
        base_config = {
            "max_consecutive_auto_reply": self.max_consecutive_auto_reply,
            "human_input_mode": self.human_input_mode,
            "llm_config": self.get_llm_config(),
        }
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

settings = AutoGenTestFrameworkSettings()

