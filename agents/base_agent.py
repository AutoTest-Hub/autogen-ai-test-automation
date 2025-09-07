"""
Base Agent class for AutoGen Test Automation Framework
Enhanced with Local AI Provider integration for enterprise deployment
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

import autogen_agentchat as autogen
from autogen_agentchat.agents import AssistantAgent as ConversableAgent, UserProxyAgent
from config.settings import settings, AgentRole, LLMProvider
from models.local_ai_provider import LocalAIProvider, ModelType


class BaseTestAgent(ABC):
    """Base class for all test automation agents"""
    
    def __init__(
        self, 
        role: AgentRole,
        name: Optional[str] = None,
        system_message: Optional[str] = None,
        llm_provider: Optional[LLMProvider] = None,
        local_ai_provider: Optional[LocalAIProvider] = None,
        **kwargs
    ):
        self.role = role
        self.name = name or f"{role.value}_agent"
        self.llm_provider = llm_provider or settings.default_llm_provider
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
        
        # Get agent configuration
        self.config = settings.get_agent_config(role)
        if system_message:
            self.config["system_message"] = system_message
        
        # Update config with any additional kwargs
        self.config.update(kwargs)
        
        # Initialize the AutoGen agent
        self.agent = self._create_autogen_agent()
        
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
    
    def _create_autogen_agent(self) -> ConversableAgent:
        """Create the underlying AutoGen agent"""
        # For the new AutoGen API, we'll create a simplified agent
        # In practice, you would create a proper model client here
        
        try:
            # Try to create with new API (simplified for testing)
            # For now, we'll create a minimal agent that can be tested
            return self._create_test_agent()
        except Exception as e:
            self.logger.warning(f"Could not create new-style agent: {e}")
            # Fallback to old API if needed
            return self._create_legacy_agent()
    
    def _create_test_agent(self):
        """Create a test agent for validation purposes"""
        # For the new AutoGen API, this would require a model client
        # For testing purposes, we'll create a mock agent
        class MockAgent:
            def __init__(self, name, system_message):
                self.name = name
                self.system_message = system_message
                self._description = "Test agent for validation"
            
            def send(self, *args, **kwargs):
                return "Mock response from agent"
            
            def initiate_chat(self, *args, **kwargs):
                class MockChatResult:
                    def __init__(self):
                        self.chat_history = [{"role": "assistant", "content": "Mock chat response"}]
                return MockChatResult()
            
            def register_function(self, *args, **kwargs):
                pass
        
        return MockAgent(self.name, self.config["system_message"])
    
    def _create_legacy_agent(self):
        """Fallback to legacy agent creation if needed"""
        # This would be used if we need to support older AutoGen versions
        return self._create_test_agent()
    
    def _get_code_execution_config(self) -> Dict[str, Any]:
        """Get code execution configuration for the agent"""
        return {
            "work_dir": f"./work_dir/{self.name}",
            "use_docker": False,  # Set to True for production
            "timeout": 60,
            "last_n_messages": 3,
        }
    
    def _get_function_map(self) -> Dict[str, callable]:
        """Get function map for the agent's custom functions"""
        return {}
    
    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task assigned to this agent"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this agent provides"""
        pass
    
    def update_state(self, status: str, **kwargs):
        """Update agent state"""
        self.state.update({
            "status": status,
            "last_activity": datetime.now(),
            **kwargs
        })
        self.logger.info(f"Agent state updated: {status}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return self.state.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            "name": self.name,
            "role": self.role.value,
            "tasks_completed": self.state["tasks_completed"],
            "errors": self.state["errors"],
            "success_rate": (
                (self.state["tasks_completed"] - self.state["errors"]) / 
                max(self.state["tasks_completed"], 1)
            ),
            "last_activity": self.state["last_activity"],
        }
    
    async def send_message(
        self, 
        recipient: Union['BaseTestAgent', ConversableAgent], 
        message: str,
        request_reply: bool = True
    ) -> Optional[str]:
        """Send message to another agent"""
        try:
            target_agent = recipient.agent if isinstance(recipient, BaseTestAgent) else recipient
            
            self.logger.info(f"Sending message to {target_agent.name}: {message[:100]}...")
            
            if request_reply:
                reply = await asyncio.to_thread(
                    self.agent.send,
                    message,
                    target_agent,
                    request_reply=True
                )
                return reply
            else:
                await asyncio.to_thread(
                    self.agent.send,
                    message,
                    target_agent,
                    request_reply=False
                )
                return None
                
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            self.state["errors"] += 1
            raise
    
    async def initiate_chat(
        self, 
        recipient: Union['BaseTestAgent', ConversableAgent], 
        message: str,
        max_turns: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Initiate a chat conversation with another agent"""
        try:
            target_agent = recipient.agent if isinstance(recipient, BaseTestAgent) else recipient
            
            self.logger.info(f"Initiating chat with {target_agent.name}")
            
            chat_result = await asyncio.to_thread(
                self.agent.initiate_chat,
                target_agent,
                message=message,
                max_turns=max_turns or settings.max_round
            )
            
            return chat_result.chat_history if hasattr(chat_result, 'chat_history') else []
            
        except Exception as e:
            self.logger.error(f"Error initiating chat: {e}")
            self.state["errors"] += 1
            raise
    
    def register_function(self, func: callable, description: str):
        """Register a custom function for this agent"""
        self.agent.register_function(
            function_map={func.__name__: func},
            description=description
        )
        self.logger.info(f"Registered function: {func.__name__}")
    
    def save_work_artifact(self, filename: str, content: str, artifact_type: str = "text"):
        """Save work artifact to agent's work directory"""
        import os
        
        work_dir = f"./work_dir/{self.name}"
        os.makedirs(work_dir, exist_ok=True)
        
        filepath = os.path.join(work_dir, filename)
        
        if artifact_type == "json":
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=2)
        else:
            with open(filepath, 'w') as f:
                f.write(content)
        
        self.logger.info(f"Saved artifact: {filepath}")
        return filepath
    
    def load_work_artifact(self, filename: str, artifact_type: str = "text") -> Any:
        """Load work artifact from agent's work directory"""
        import os
        
        work_dir = f"./work_dir/{self.name}"
        filepath = os.path.join(work_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Artifact not found: {filepath}")
        
        if artifact_type == "json":
            with open(filepath, 'r') as f:
                return json.load(f)
        else:
            with open(filepath, 'r') as f:
                return f.read()
    
    def generate_local_ai_response(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate response using local AI models
        
        This method provides direct access to local AI inference for agents
        that need to bypass AutoGen's conversation flow
        """
        if not self.use_local_ai:
            raise RuntimeError("Local AI is not available. Use external LLM instead.")
        
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
            raise RuntimeError("Local AI is not available. Use external LLM instead.")
        
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
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, role={self.role.value})"
    
    def __repr__(self) -> str:
        return self.__str__()


class UserProxyTestAgent(BaseTestAgent):
    """User proxy agent for human interaction when needed"""
    
    def __init__(self, name: str = "user_proxy", **kwargs):
        super().__init__(
            role=AgentRole.ORCHESTRATOR,  # Default role
            name=name,
            system_message="You are a user proxy agent that facilitates human interaction when needed.",
            **kwargs
        )
        
        # Override with UserProxyAgent
        self.agent = UserProxyAgent(
            name=self.name,
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=0,
            code_execution_config=self._get_code_execution_config(),
        )
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user proxy tasks"""
        return {
            "status": "completed",
            "message": "User proxy task processed",
            "data": task_data
        }
    
    def get_capabilities(self) -> List[str]:
        """Get user proxy capabilities"""
        return ["human_interaction", "task_coordination", "workflow_management"]

