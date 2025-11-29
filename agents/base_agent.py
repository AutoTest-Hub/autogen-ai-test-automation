"""
Base Agent class for AutoGen Test Automation Framework
Enhanced with Local AI Provider integration for enterprise deployment

This module provides the foundation for all AI-powered agents in the test automation
framework. It includes:
- Unified LLM response generation (local and external)
- Response caching for performance optimization
- Retry logic with exponential backoff
- Proper error handling and metrics tracking
"""

import asyncio
import json
import logging
import os
import hashlib
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from functools import lru_cache

try:
    import autogen
    from autogen import AssistantAgent as ConversableAgent, UserProxyAgent
    AUTOGEN_AVAILABLE = True
except ImportError:
    autogen = None
    ConversableAgent = None
    UserProxyAgent = None
    AUTOGEN_AVAILABLE = False
from config.settings import settings, AgentRole, LLMProvider
from models.local_ai_provider import LocalAIProvider, ModelType

# Try to import external LLM libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class BaseTestAgent(ABC):
    """
    Base class for all test automation agents.

    Provides unified LLM access with support for:
    - Local AI (Ollama) for enterprise/offline deployment
    - External LLMs (OpenAI, Anthropic) for cloud deployment
    - Response caching for repeated queries
    - Retry logic with exponential backoff
    - Comprehensive error handling and metrics
    """

    # Class-level response cache for performance
    _response_cache: Dict[str, Dict[str, Any]] = {}
    _cache_max_size: int = 100
    _cache_ttl_seconds: int = 3600  # 1 hour default TTL

    def __init__(
        self,
        role: AgentRole,
        name: Optional[str] = None,
        system_message: Optional[str] = None,
        llm_provider: Optional[LLMProvider] = None,
        local_ai_provider: Optional[LocalAIProvider] = None,
        enable_caching: bool = True,
        max_retries: int = 3,
        **kwargs
    ):
        self.role = role
        self.name = name or f"{role.value}_agent"
        self.llm_provider = llm_provider or settings.default_llm_provider
        self.logger = logging.getLogger(f"agent.{self.name}")

        # LLM configuration
        self.enable_caching = enable_caching
        self.max_retries = max_retries

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
            "llm_calls": 0,
            "cache_hits": 0,
            "total_tokens": 0,
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

    async def request_validation(
        self,
        validator_agent: 'BaseTestAgent',
        artifact: Dict[str, Any],
        validation_criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Request validation of an artifact from another agent.

        This enables cross-agent validation where one agent can ask
        another to review and validate its work before proceeding.

        Args:
            validator_agent: The agent to request validation from
            artifact: The work artifact to validate (e.g., generated tests, discovery results)
            validation_criteria: List of criteria to validate against

        Returns:
            Dict[str, Any]: Validation result including:
                - is_valid: bool
                - score: float (0-1)
                - issues: List of identified issues
                - suggestions: List of improvement suggestions
                - approved: bool (overall approval)
        """
        try:
            self.logger.info(f"Requesting validation from {validator_agent.name}")

            # Build validation request message
            validation_request = {
                "type": "validation_request",
                "from_agent": self.name,
                "artifact_type": artifact.get("type", "unknown"),
                "artifact_summary": artifact.get("summary", ""),
                "criteria": validation_criteria,
                "artifact_data": artifact
            }

            # Create validation prompt
            criteria_list = "\n".join([f"- {c}" for c in validation_criteria])
            validation_prompt = f"""
Please validate the following artifact from {self.name}:

Artifact Type: {artifact.get("type", "unknown")}
Summary: {artifact.get("summary", "No summary provided")}

Validation Criteria:
{criteria_list}

Please review and provide:
1. Is the artifact valid? (yes/no)
2. Quality score (0-100)
3. Any issues found
4. Suggestions for improvement
5. Overall approval recommendation

Respond with your validation assessment.
"""

            # Request validation via chat
            reply = await self.send_message(
                validator_agent,
                validation_prompt,
                request_reply=True
            )

            # Parse validation response
            validation_result = self._parse_validation_response(reply, validation_criteria)

            self.logger.info(
                f"Validation from {validator_agent.name}: "
                f"approved={validation_result['approved']}, score={validation_result['score']}"
            )

            return validation_result

        except Exception as e:
            self.logger.error(f"Validation request failed: {e}")
            return {
                "is_valid": False,
                "score": 0.0,
                "issues": [f"Validation failed: {str(e)}"],
                "suggestions": [],
                "approved": False,
                "error": str(e)
            }

    def _parse_validation_response(
        self,
        response: str,
        criteria: List[str]
    ) -> Dict[str, Any]:
        """Parse validation response from validator agent"""
        result = {
            "is_valid": True,
            "score": 0.75,  # Default moderate score
            "issues": [],
            "suggestions": [],
            "approved": True,
            "raw_response": response
        }

        if not response:
            result["is_valid"] = False
            result["approved"] = False
            result["score"] = 0.0
            result["issues"].append("No response from validator")
            return result

        response_lower = response.lower()

        # Check for rejection indicators
        rejection_keywords = ["invalid", "rejected", "fail", "not acceptable", "major issues"]
        for keyword in rejection_keywords:
            if keyword in response_lower:
                result["is_valid"] = False
                result["approved"] = False
                result["score"] = max(result["score"] - 0.3, 0.0)

        # Check for approval indicators
        approval_keywords = ["valid", "approved", "pass", "acceptable", "good quality"]
        for keyword in approval_keywords:
            if keyword in response_lower:
                result["score"] = min(result["score"] + 0.1, 1.0)

        # Extract issues (lines with "issue" or starting with "-")
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("-") or "issue" in line.lower():
                if len(line) > 5:  # Avoid empty bullet points
                    result["issues"].append(line.lstrip("- "))

        # Extract suggestions (lines with "suggest" or "recommend")
        for line in response.split("\n"):
            line = line.strip()
            if "suggest" in line.lower() or "recommend" in line.lower():
                if len(line) > 10:
                    result["suggestions"].append(line)

        # Final approval decision
        result["approved"] = result["is_valid"] and result["score"] >= 0.6

        return result

    async def collaborate_with(
        self,
        collaborator: 'BaseTestAgent',
        task: Dict[str, Any],
        max_rounds: int = 3
    ) -> Dict[str, Any]:
        """
        Collaborate with another agent on a task.

        This enables iterative collaboration where agents can work together,
        sharing feedback and refining outputs.

        Args:
            collaborator: The agent to collaborate with
            task: The task to collaborate on
            max_rounds: Maximum collaboration rounds

        Returns:
            Dict[str, Any]: Collaboration results
        """
        try:
            self.logger.info(f"Starting collaboration with {collaborator.name}")

            collaboration_results = {
                "rounds": [],
                "final_output": None,
                "consensus_reached": False
            }

            current_output = None

            for round_num in range(max_rounds):
                self.logger.info(f"Collaboration round {round_num + 1}/{max_rounds}")

                # This agent processes the task
                if current_output is None:
                    # Initial processing
                    if hasattr(self, 'process_task'):
                        current_output = await self.process_task(task)
                    else:
                        current_output = {"status": "initial", "data": task}

                # Request feedback from collaborator
                feedback_prompt = f"""
Please review and provide feedback on the following output:

{json.dumps(current_output, indent=2, default=str)[:2000]}

Provide specific feedback and suggestions for improvement.
If you approve, indicate "APPROVED" in your response.
"""

                feedback = await self.send_message(
                    collaborator,
                    feedback_prompt,
                    request_reply=True
                )

                round_result = {
                    "round": round_num + 1,
                    "output_summary": str(current_output)[:500],
                    "feedback": feedback
                }
                collaboration_results["rounds"].append(round_result)

                # Check for approval/consensus
                if feedback and "approved" in feedback.lower():
                    collaboration_results["consensus_reached"] = True
                    collaboration_results["final_output"] = current_output
                    self.logger.info(f"Consensus reached in round {round_num + 1}")
                    break

                # Update task with feedback for next round
                task["previous_output"] = current_output
                task["feedback"] = feedback

            if not collaboration_results["consensus_reached"]:
                collaboration_results["final_output"] = current_output
                self.logger.info("Max rounds reached without consensus")

            return collaboration_results

        except Exception as e:
            self.logger.error(f"Collaboration failed: {e}")
            return {
                "rounds": [],
                "final_output": None,
                "consensus_reached": False,
                "error": str(e)
            }
    
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

    # =========================================================================
    # UNIFIED LLM RESPONSE GENERATION
    # =========================================================================

    def _get_cache_key(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a cache key for the given prompt and system prompt"""
        content = f"{system_prompt or ''}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        if not self.enable_caching:
            return None

        if cache_key in self._response_cache:
            cached = self._response_cache[cache_key]
            # Check if cache entry is still valid
            if time.time() - cached.get("cached_at", 0) < self._cache_ttl_seconds:
                self.state["cache_hits"] += 1
                self.logger.debug(f"Cache hit for key {cache_key[:8]}...")
                return cached.get("response")

            # Remove expired entry
            del self._response_cache[cache_key]

        return None

    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache a response for future use"""
        if not self.enable_caching:
            return

        # Enforce cache size limit
        if len(self._response_cache) >= self._cache_max_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self._response_cache.keys(),
                key=lambda k: self._response_cache[k].get("cached_at", 0)
            )[:10]
            for key in oldest_keys:
                del self._response_cache[key]

        self._response_cache[cache_key] = {
            "response": response,
            "cached_at": time.time()
        }

    async def generate_llm_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_cache: bool = True,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None  # "json" for JSON responses
    ) -> Dict[str, Any]:
        """
        Generate a response using the configured LLM provider.

        This is the primary method for agents to get LLM responses. It handles:
        - Response caching for repeated queries
        - Retry logic with exponential backoff
        - Automatic fallback between local and external LLMs
        - Structured JSON response parsing when requested

        Args:
            prompt: The prompt to send to the LLM
            system_prompt: Optional system prompt (defaults to agent's system message)
            use_cache: Whether to use caching (default: True)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            response_format: Set to "json" to parse response as JSON

        Returns:
            Dict containing:
                - response: The LLM response text
                - success: Boolean indicating success
                - model: Model used
                - cached: Whether response was from cache
                - error: Error message if failed
        """
        # Use agent's system message if not provided
        effective_system_prompt = system_prompt or self.config.get("system_message", "")

        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(prompt, effective_system_prompt)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return {**cached_response, "cached": True}

        # Try to generate response with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                if self.use_local_ai:
                    result = await self._generate_local_ai_response(
                        prompt, effective_system_prompt, temperature, max_tokens
                    )
                else:
                    result = await self._generate_external_llm_response(
                        prompt, effective_system_prompt, temperature, max_tokens
                    )

                if result.get("success"):
                    # Parse JSON if requested
                    if response_format == "json":
                        result = self._parse_json_response(result)

                    # Cache successful response
                    if use_cache:
                        self._cache_response(cache_key, result)

                    # Update metrics
                    self.state["llm_calls"] += 1
                    self.state["last_activity"] = datetime.now()

                    return {**result, "cached": False}

                last_error = result.get("error", "Unknown error")

            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")

            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                self.logger.info(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

        # All retries failed
        self.state["errors"] += 1
        return {
            "response": "",
            "success": False,
            "error": f"All {self.max_retries} attempts failed. Last error: {last_error}",
            "cached": False
        }

    def generate_llm_response_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_cache: bool = True,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronous version of generate_llm_response"""
        return asyncio.get_event_loop().run_until_complete(
            self.generate_llm_response(
                prompt, system_prompt, use_cache, temperature, max_tokens, response_format
            )
        )

    async def _generate_local_ai_response(
        self,
        prompt: str,
        system_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate response using local AI (Ollama)"""
        if not self.model_type:
            raise ValueError("No model type configured for this agent")

        try:
            result = await self.local_ai_provider.generate_response_async(
                prompt=prompt,
                model_type=self.model_type,
                system_prompt=system_prompt
            )

            return {
                "response": result.get("response", ""),
                "success": result.get("success", False),
                "model": result.get("model", "local"),
                "model_type": self.model_type.value,
                "response_time": result.get("response_time", 0),
                "error": result.get("error")
            }

        except Exception as e:
            self.logger.error(f"Local AI generation failed: {e}")
            return {
                "response": "",
                "success": False,
                "error": str(e)
            }

    async def _generate_external_llm_response(
        self,
        prompt: str,
        system_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate response using external LLM (OpenAI, Anthropic, etc.)"""
        llm_config = self.config.get("llm_config", {})
        provider = self.llm_provider

        try:
            if provider == LLMProvider.OPENAI:
                return await self._call_openai(
                    prompt, system_prompt, llm_config, temperature, max_tokens
                )
            elif provider == LLMProvider.ANTHROPIC:
                return await self._call_anthropic(
                    prompt, system_prompt, llm_config, temperature, max_tokens
                )
            else:
                # Fallback to OpenAI-compatible API
                return await self._call_openai(
                    prompt, system_prompt, llm_config, temperature, max_tokens
                )

        except Exception as e:
            self.logger.error(f"External LLM generation failed: {e}")
            return {
                "response": "",
                "success": False,
                "error": str(e)
            }

    async def _call_openai(
        self,
        prompt: str,
        system_prompt: str,
        llm_config: Dict[str, Any],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        if not OPENAI_AVAILABLE:
            return {
                "response": "",
                "success": False,
                "error": "OpenAI library not installed. Run: pip install openai"
            }

        api_key = llm_config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {
                "response": "",
                "success": False,
                "error": "OpenAI API key not configured"
            }

        try:
            client = openai.AsyncOpenAI(api_key=api_key)
            start_time = time.time()

            response = await client.chat.completions.create(
                model=llm_config.get("model", "gpt-4o"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature or llm_config.get("temperature", 0.1),
                max_tokens=max_tokens or llm_config.get("max_tokens", 4000)
            )

            response_time = time.time() - start_time
            content = response.choices[0].message.content

            # Track token usage
            if response.usage:
                self.state["total_tokens"] += response.usage.total_tokens

            return {
                "response": content,
                "success": True,
                "model": response.model,
                "response_time": response_time,
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }

        except Exception as e:
            return {
                "response": "",
                "success": False,
                "error": f"OpenAI API error: {str(e)}"
            }

    async def _call_anthropic(
        self,
        prompt: str,
        system_prompt: str,
        llm_config: Dict[str, Any],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Call Anthropic API"""
        if not ANTHROPIC_AVAILABLE:
            return {
                "response": "",
                "success": False,
                "error": "Anthropic library not installed. Run: pip install anthropic"
            }

        api_key = llm_config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {
                "response": "",
                "success": False,
                "error": "Anthropic API key not configured"
            }

        try:
            client = anthropic.AsyncAnthropic(api_key=api_key)
            start_time = time.time()

            response = await client.messages.create(
                model=llm_config.get("model", "claude-3-5-sonnet-20241022"),
                max_tokens=max_tokens or llm_config.get("max_tokens", 4000),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_time = time.time() - start_time
            content = response.content[0].text if response.content else ""

            # Track token usage
            if response.usage:
                self.state["total_tokens"] += response.usage.input_tokens + response.usage.output_tokens

            return {
                "response": content,
                "success": True,
                "model": response.model,
                "response_time": response_time,
                "tokens_used": (response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0
            }

        except Exception as e:
            return {
                "response": "",
                "success": False,
                "error": f"Anthropic API error: {str(e)}"
            }

    def _parse_json_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response as JSON"""
        response_text = result.get("response", "")

        try:
            # Try to extract JSON from the response
            # Handle cases where JSON is wrapped in markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            parsed = json.loads(response_text)
            result["parsed_json"] = parsed
            result["json_parse_success"] = True

        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            result["json_parse_success"] = False
            result["json_parse_error"] = str(e)

        return result

    def clear_cache(self):
        """Clear the response cache for this agent"""
        self._response_cache.clear()
        self.logger.info("Response cache cleared")

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

