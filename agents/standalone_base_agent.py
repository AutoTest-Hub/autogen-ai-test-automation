#!/usr/bin/env python3
"""
Standalone Base Agent for AutoGen Test Automation Framework
Works without external AutoGen dependency for basic functionality
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

# Import local AI provider
from models.local_ai_provider import LocalAIProvider, ModelType

# Define AgentRole enum locally to avoid config dependency
class AgentRole(Enum):
    """Agent roles for test automation"""
    PLANNING = "planning"
    TEST_CREATION = "test_creation"
    REVIEW = "review"
    EXECUTION = "execution"
    REPORTING = "reporting"
    ORCHESTRATOR = "orchestrator"

class StandaloneBaseAgent(ABC):
    """
    Standalone base agent that works without external AutoGen dependency
    Provides core functionality for local AI integration and agent operations
    """
    
    def __init__(
        self, 
        role: AgentRole,
        name: Optional[str] = None,
        system_message: Optional[str] = None,
        local_ai_provider: Optional[LocalAIProvider] = None,
        **kwargs
    ):
        self.role = role
        self.name = name or f"{role.value}_agent"
        self.logger = logging.getLogger(f"agent.{self.name}")
        
        # Initialize local AI provider for enterprise deployment
        self.local_ai_provider = local_ai_provider or LocalAIProvider()
        self.model_type = self._get_model_type_for_role(role)
        
        # Check if local AI is available, fallback to external if needed
        self.use_local_ai = self.local_ai_provider.is_available()
        if self.use_local_ai:
            self.logger.info(f"Using local AI models for {self.name}")
        else:
            self.logger.warning(f"Local AI not available for {self.name}, using external LLM")
        
        # Agent configuration
        self.config = {
            "system_message": system_message or self._get_default_system_message(),
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        # Update config with any additional kwargs
        self.config.update(kwargs)
        
        # Agent state and metrics
        self.state = {
            "status": "initialized",
            "tasks_completed": 0,
            "errors": 0,
            "last_activity": datetime.now(),
            "local_ai_enabled": self.use_local_ai,
            "model_type": self.model_type.value if self.model_type else None
        }
        
        self.logger.info(f"Initialized {self.name} with role {role.value}")
    
    def _get_model_type_for_role(self, role: AgentRole) -> Optional[ModelType]:
        """Map agent role to appropriate local AI model type"""
        role_to_model_map = {
            AgentRole.PLANNING: ModelType.PLANNING,
            AgentRole.TEST_CREATION: ModelType.CODE_GENERATION,
            AgentRole.REVIEW: ModelType.REVIEW,
            AgentRole.EXECUTION: ModelType.EXECUTION,
            AgentRole.REPORTING: ModelType.REPORTING,
            AgentRole.ORCHESTRATOR: ModelType.GENERAL_INTELLIGENCE
        }
        return role_to_model_map.get(role, ModelType.GENERAL_INTELLIGENCE)
    
    def _get_default_system_message(self) -> str:
        """Get default system message based on agent role"""
        system_messages = {
            AgentRole.PLANNING: "You are an expert test planning agent. Analyze requirements and create comprehensive test strategies.",
            AgentRole.TEST_CREATION: "You are an expert test automation developer. Generate high-quality, maintainable test code.",
            AgentRole.REVIEW: "You are an expert code reviewer. Analyze test code for quality, completeness, and best practices.",
            AgentRole.EXECUTION: "You are a test execution specialist. Monitor test runs and provide execution insights.",
            AgentRole.REPORTING: "You are a test reporting expert. Create detailed, actionable test reports and quality insights.",
            AgentRole.ORCHESTRATOR: "You are a test orchestration expert. Coordinate complex testing workflows and agent collaboration."
        }
        return system_messages.get(self.role, "You are a helpful AI assistant for test automation.")
    
    def generate_local_ai_response(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate response using local AI models
        
        This method provides direct access to local AI inference for agents
        that need to bypass AutoGen's conversation flow
        """
        if not self.use_local_ai:
            return {
                "response": "Local AI not available. In production, this would use external LLM or AutoGen conversation.",
                "success": False,
                "error": "Local AI not available",
                "fallback": True
            }
        
        if not self.model_type:
            raise ValueError("No model type configured for this agent")
        
        try:
            result = self.local_ai_provider.generate_response_sync(
                prompt=prompt,
                model_type=self.model_type,
                system_prompt=system_prompt or self.config.get("system_message")
            )
            
            # Update agent metrics
            if result["success"]:
                self.state["tasks_completed"] += 1
            else:
                self.state["errors"] += 1
            
            self.state["last_activity"] = datetime.now()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Local AI generation failed: {e}")
            self.state["errors"] += 1
            return {
                "response": "",
                "error": str(e),
                "success": False
            }
    
    async def generate_local_ai_response_async(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Async version of local AI response generation"""
        if not self.use_local_ai:
            return {
                "response": "Local AI not available. In production, this would use external LLM or AutoGen conversation.",
                "success": False,
                "error": "Local AI not available",
                "fallback": True
            }
        
        if not self.model_type:
            raise ValueError("No model type configured for this agent")
        
        try:
            result = await self.local_ai_provider.generate_response_async(
                prompt=prompt,
                model_type=self.model_type,
                system_prompt=system_prompt or self.config.get("system_message")
            )
            
            # Update agent metrics
            if result["success"]:
                self.state["tasks_completed"] += 1
            else:
                self.state["errors"] += 1
            
            self.state["last_activity"] = datetime.now()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Local AI generation failed: {e}")
            self.state["errors"] += 1
            return {
                "response": "",
                "error": str(e),
                "success": False
            }
    
    def get_local_ai_status(self) -> Dict[str, Any]:
        """Get status of local AI integration for this agent"""
        return {
            "agent_name": self.name,
            "agent_role": self.role.value,
            "local_ai_enabled": self.use_local_ai,
            "model_type": self.model_type.value if self.model_type else None,
            "local_ai_provider_status": self.local_ai_provider.get_status_report() if self.use_local_ai else None,
            "tasks_completed": self.state["tasks_completed"],
            "errors": self.state["errors"],
            "last_activity": self.state["last_activity"].isoformat()
        }
    
    def execute_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task using this agent
        
        Args:
            task_description: Description of the task to execute
            context: Optional context information
            
        Returns:
            Task execution results
        """
        self.logger.info(f"Executing task: {task_description[:50]}...")
        
        try:
            # Prepare the prompt with context
            prompt = self._prepare_task_prompt(task_description, context)
            
            # Generate response using local AI
            result = self.generate_local_ai_response(prompt)
            
            if result["success"]:
                self.logger.info(f"Task completed successfully by {self.name}")
                return {
                    "success": True,
                    "agent": self.name,
                    "task": task_description,
                    "result": result["response"],
                    "metadata": result.get("metadata", {}),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                self.logger.error(f"Task failed: {result.get('error')}")
                return {
                    "success": False,
                    "agent": self.name,
                    "task": task_description,
                    "error": result.get("error"),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return {
                "success": False,
                "agent": self.name,
                "task": task_description,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _prepare_task_prompt(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Prepare the prompt for task execution"""
        prompt_parts = [
            f"Task: {task_description}",
            "",
            "Please provide a comprehensive response based on your role and expertise."
        ]
        
        if context:
            prompt_parts.insert(1, f"Context: {context}")
            prompt_parts.insert(2, "")
        
        return "\n".join(prompt_parts)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get comprehensive agent information"""
        return {
            "name": self.name,
            "role": self.role.value,
            "status": self.state["status"],
            "local_ai_enabled": self.use_local_ai,
            "model_type": self.model_type.value if self.model_type else None,
            "tasks_completed": self.state["tasks_completed"],
            "errors": self.state["errors"],
            "last_activity": self.state["last_activity"].isoformat(),
            "config": {
                "system_message": self.config["system_message"][:100] + "..." if len(self.config["system_message"]) > 100 else self.config["system_message"],
                "max_tokens": self.config["max_tokens"],
                "temperature": self.config["temperature"]
            }
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, role={self.role.value})"
    
    def __repr__(self) -> str:
        return self.__str__()


class StandalonePlanningAgent(StandaloneBaseAgent):
    """Specialized planning agent for test strategy and analysis"""
    
    def __init__(self, **kwargs):
        super().__init__(
            role=AgentRole.PLANNING,
            name="planning_agent",
            system_message="You are an expert test planning agent. Analyze test requirements and create comprehensive test strategies with risk assessment, test data requirements, and success criteria.",
            **kwargs
        )
    
    def analyze_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a test scenario and create a test strategy"""
        task_description = f"""
        Analyze this test scenario and create a comprehensive test strategy:
        
        Scenario Name: {scenario.get('name', 'Unnamed')}
        Description: {scenario.get('description', 'No description')}
        Target Application: {scenario.get('application', 'Not specified')}
        Test Steps: {len(scenario.get('test_steps', []))} steps defined
        
        Provide:
        1. Test strategy and approach
        2. Risk assessment and mitigation
        3. Required test data and setup
        4. Success criteria and validation points
        5. Potential challenges and solutions
        """
        
        return self.execute_task(task_description, {"scenario": scenario})


class StandaloneTestCreationAgent(StandaloneBaseAgent):
    """Specialized test creation agent for generating test automation code"""
    
    def __init__(self, **kwargs):
        super().__init__(
            role=AgentRole.TEST_CREATION,
            name="test_creation_agent",
            system_message="You are an expert test automation developer. Generate high-quality, maintainable test automation code using modern frameworks like Playwright, Selenium, or REST API testing libraries.",
            **kwargs
        )
    
    def generate_test_code(self, test_strategy: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test automation code based on strategy and scenario"""
        task_description = f"""
        Generate complete test automation code based on this test strategy:
        
        Test Strategy:
        {test_strategy}
        
        Original Scenario:
        Name: {scenario.get('name', 'Unnamed')}
        Target: {scenario.get('application', 'Not specified')}
        Steps: {scenario.get('test_steps', [])}
        
        Generate:
        1. Complete Python test automation code (using Playwright or Selenium)
        2. Test data setup and configuration
        3. Error handling and logging
        4. Clear documentation and comments
        5. Assertions and validation logic
        """
        
        return self.execute_task(task_description, {"strategy": test_strategy, "scenario": scenario})

