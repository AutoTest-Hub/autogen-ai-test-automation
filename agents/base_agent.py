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
import hashlib
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from functools import lru_cache

# Try to import AutoGen - make it optional
try:
    import autogen_agentchat as autogen
    from autogen_agentchat.agents import AssistantAgent as ConversableAgent, UserProxyAgent
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
    openai = None
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None
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
        application_context: Optional['ApplicationContext'] = None,
        enable_caching: bool = True,
        max_retries: int = 3,
        **kwargs
    ):
        self.role = role
        self.name = name or f"{role.value}_agent"
        self.llm_provider = llm_provider or settings.default_llm_provider
        self.logger = logging.getLogger(f"agent.{self.name}")

        # Application context for domain awareness
        self.application_context = application_context

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
            self.logger.info(f"Local AI not available for {self.name}, will use external LLM")

        # Initialize OpenAI client if available
        self._openai_client = None
        if OPENAI_AVAILABLE:
            llm_config = settings.get_llm_config(LLMProvider.OPENAI)
            api_key = llm_config.get("api_key")
            if api_key:
                self._openai_client = openai.AsyncOpenAI(api_key=api_key)
                self.logger.info(f"OpenAI client initialized for {self.name}")

        # Initialize Anthropic client if available
        self._anthropic_client = None
        if ANTHROPIC_AVAILABLE:
            llm_config = settings.get_llm_config(LLMProvider.ANTHROPIC)
            api_key = llm_config.get("api_key")
            if api_key:
                self._anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
                self.logger.info(f"Anthropic client initialized for {self.name}")

        # Get agent configuration
        self.config = settings.get_agent_config(role)
        if system_message:
            self.config["system_message"] = system_message

        # Update config with any additional kwargs
        self.config.update(kwargs)

        # Initialize the AutoGen agent (optional, for backward compatibility)
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
            "model_type": self.model_type.value if self.model_type else None,
            "llm_provider": self.llm_provider.value if self.llm_provider else None
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

    # =========================================================================
    # LLM Integration Methods - Core Intelligence Layer
    # =========================================================================

    def _get_cache_key(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate cache key from prompt and system prompt"""
        content = f"{system_prompt or self.config.get('system_message', '')}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()

    def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Check if response is cached and still valid"""
        if not self.enable_caching:
            return None

        if cache_key in self._response_cache:
            cached = self._response_cache[cache_key]
            cache_age = time.time() - cached.get("timestamp", 0)
            if cache_age < self._cache_ttl_seconds:
                self.state["cache_hits"] += 1
                self.logger.debug(f"Cache hit for key {cache_key[:8]}...")
                return cached.get("response")
            else:
                # Cache expired, remove it
                del self._response_cache[cache_key]

        return None

    def _store_cache(self, cache_key: str, response: Dict[str, Any]):
        """Store response in cache"""
        if not self.enable_caching:
            return

        # Implement simple LRU by removing oldest if at capacity
        if len(self._response_cache) >= self._cache_max_size:
            oldest_key = min(
                self._response_cache.keys(),
                key=lambda k: self._response_cache[k].get("timestamp", 0)
            )
            del self._response_cache[oldest_key]

        self._response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }

    def _inject_application_context(self, prompt: str, max_context_tokens: int = 1500) -> str:
        """
        Inject application context into the prompt if available.

        This enables agents to have domain awareness similar to how a human
        QA engineer understands an application after onboarding.

        Args:
            prompt: The original user prompt
            max_context_tokens: Maximum tokens to use for context

        Returns:
            Enhanced prompt with application context prepended
        """
        if not self.application_context:
            return prompt

        try:
            # Get role-specific context
            context = self.application_context.get_context_for_agent(
                agent_role=self.role.value,
                max_tokens=max_context_tokens
            )

            if context:
                enhanced_prompt = f"""
{context}

---
YOUR TASK:
{prompt}
"""
                self.logger.debug(f"Injected application context ({len(context)} chars) into prompt")
                return enhanced_prompt

        except Exception as e:
            self.logger.warning(f"Failed to inject application context: {e}")

        return prompt

    def set_application_context(self, context: 'ApplicationContext') -> None:
        """
        Set or update the application context for this agent.

        Args:
            context: The ApplicationContext to use
        """
        self.application_context = context
        self.logger.info(f"Application context set: {context.app_name}")

    async def generate_llm_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: str = "text",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate response using configured LLM provider.

        This is the primary method for agents to get LLM-powered responses.
        It automatically handles:
        - Provider selection (Local AI -> OpenAI -> Anthropic)
        - Response caching
        - Retry logic with exponential backoff
        - Error handling and metrics tracking

        Args:
            prompt: The user prompt/question
            system_prompt: Optional system prompt (uses agent config if not provided)
            response_format: "text" or "json"
            temperature: Override default temperature
            max_tokens: Override default max tokens
            use_cache: Whether to use response caching

        Returns:
            Dict with:
                - success: bool
                - response: str or dict (parsed JSON if response_format="json")
                - provider: str (which LLM was used)
                - tokens: int (approximate token count)
                - cached: bool
                - error: str (if success=False)
        """
        self.state["llm_calls"] += 1
        effective_system_prompt = system_prompt or self.config.get("system_message", "")

        # Inject application context if available
        enhanced_prompt = self._inject_application_context(prompt)

        # Check cache first (use enhanced prompt for cache key)
        if use_cache and self.enable_caching:
            cache_key = self._get_cache_key(prompt, effective_system_prompt)
            cached_response = self._check_cache(cache_key)
            if cached_response:
                return {**cached_response, "cached": True}

        # Try providers in order of preference
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # 1. Try Local AI first (if available)
                if self.use_local_ai and self.local_ai_provider.is_available():
                    response = await self._call_local_ai(
                        enhanced_prompt, effective_system_prompt, temperature, max_tokens
                    )
                    if response.get("success"):
                        result = self._process_llm_response(response, "local_ai", response_format)
                        if use_cache and self.enable_caching:
                            self._store_cache(cache_key, result)
                        return result

                # 2. Try OpenAI
                if self._openai_client:
                    response = await self._call_openai(
                        enhanced_prompt, effective_system_prompt, temperature, max_tokens, response_format
                    )
                    if response.get("success"):
                        result = self._process_llm_response(response, "openai", response_format)
                        if use_cache and self.enable_caching:
                            self._store_cache(cache_key, result)
                        return result

                # 3. Try Anthropic
                if self._anthropic_client:
                    response = await self._call_anthropic(
                        enhanced_prompt, effective_system_prompt, temperature, max_tokens
                    )
                    if response.get("success"):
                        result = self._process_llm_response(response, "anthropic", response_format)
                        if use_cache and self.enable_caching:
                            self._store_cache(cache_key, result)
                        return result

                # No provider available
                raise RuntimeError("No LLM provider available. Configure OpenAI, Anthropic, or Local AI.")

            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)

        # All retries failed
        self.state["errors"] += 1
        return {
            "success": False,
            "error": f"All LLM providers failed after {self.max_retries} attempts. Last error: {last_error}",
            "cached": False
        }

    async def _call_local_ai(
        self,
        prompt: str,
        system_prompt: str,
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Call local AI (Ollama) provider"""
        try:
            result = await self.local_ai_provider.generate_response_async(
                prompt=prompt,
                model_type=self.model_type,
                system_prompt=system_prompt
            )
            return result
        except Exception as e:
            self.logger.error(f"Local AI call failed: {e}")
            return {"success": False, "error": str(e)}

    async def _call_openai(
        self,
        prompt: str,
        system_prompt: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
        response_format: str
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        if not self._openai_client:
            return {"success": False, "error": "OpenAI client not initialized"}

        try:
            llm_config = settings.get_llm_config(LLMProvider.OPENAI)
            model = llm_config.get("model", "gpt-4o")
            temp = temperature if temperature is not None else llm_config.get("temperature", 0.1)
            tokens = max_tokens if max_tokens is not None else llm_config.get("max_tokens", 4000)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            # Add JSON mode if requested
            kwargs = {}
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            response = await self._openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                **kwargs
            )

            content = response.choices[0].message.content
            usage = response.usage

            self.state["total_tokens"] += usage.total_tokens if usage else 0

            return {
                "success": True,
                "response": content,
                "tokens": usage.total_tokens if usage else 0,
                "model": model
            }

        except Exception as e:
            self.logger.error(f"OpenAI call failed: {e}")
            return {"success": False, "error": str(e)}

    async def _call_anthropic(
        self,
        prompt: str,
        system_prompt: str,
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Call Anthropic API"""
        if not self._anthropic_client:
            return {"success": False, "error": "Anthropic client not initialized"}

        try:
            llm_config = settings.get_llm_config(LLMProvider.ANTHROPIC)
            model = llm_config.get("model", "claude-3-5-sonnet-20241022")
            temp = temperature if temperature is not None else llm_config.get("temperature", 0.1)
            tokens = max_tokens if max_tokens is not None else llm_config.get("max_tokens", 4000)

            response = await self._anthropic_client.messages.create(
                model=model,
                max_tokens=tokens,
                temperature=temp,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            usage_tokens = response.usage.input_tokens + response.usage.output_tokens

            self.state["total_tokens"] += usage_tokens

            return {
                "success": True,
                "response": content,
                "tokens": usage_tokens,
                "model": model
            }

        except Exception as e:
            self.logger.error(f"Anthropic call failed: {e}")
            return {"success": False, "error": str(e)}

    def _process_llm_response(
        self,
        response: Dict[str, Any],
        provider: str,
        response_format: str
    ) -> Dict[str, Any]:
        """Process and format LLM response"""
        content = response.get("response", "")

        # Parse JSON if requested
        if response_format == "json" and isinstance(content, str):
            try:
                # Try to extract JSON from response
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = json.loads(content.strip())
            except json.JSONDecodeError:
                # Return as-is if JSON parsing fails
                self.logger.warning("Failed to parse JSON response, returning as text")

        return {
            "success": True,
            "response": content,
            "provider": provider,
            "tokens": response.get("tokens", 0),
            "model": response.get("model", "unknown"),
            "cached": False
        }

    def generate_llm_response_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: str = "text",
        **kwargs
    ) -> Dict[str, Any]:
        """Synchronous wrapper for generate_llm_response"""
        return asyncio.get_event_loop().run_until_complete(
            self.generate_llm_response(prompt, system_prompt, response_format, **kwargs)
        )

    # =========================================================================
    # End of LLM Integration Methods
    # =========================================================================

    # =========================================================================
    # Agent Message Handling - Phase 2 Collaboration
    # =========================================================================

    async def handle_message(self, message: 'AgentMessage') -> Optional['AgentMessage']:
        """
        Handle incoming messages from other agents.

        This is the primary entry point for agent-to-agent communication.
        Subclasses can override specific handlers for different message types.

        Args:
            message: The incoming AgentMessage

        Returns:
            Optional response message
        """
        from orchestrator.agent_protocol import MessageType, AgentMessage as AM

        self.logger.info(f"Received message from {message.sender_agent}: {message.message_type.value}")

        # Update activity timestamp
        self.state["last_activity"] = datetime.now()

        # Route to specific handlers based on message type
        handlers = {
            MessageType.TASK_REQUEST: self._handle_task_request,
            MessageType.REVIEW_REQUEST: self._handle_review_request,
            MessageType.REVIEW_FEEDBACK: self._handle_review_feedback,
            MessageType.REFINEMENT_REQUEST: self._handle_refinement_request,
            MessageType.STATUS_QUERY: self._handle_status_query,
            MessageType.HEALING_REQUEST: self._handle_healing_request,
        }

        handler = handlers.get(message.message_type)
        if handler:
            try:
                return await handler(message)
            except Exception as e:
                self.logger.error(f"Error handling message: {e}")
                self.state["errors"] += 1
                return message.create_response(
                    MessageType.ERROR_REPORT,
                    {"error": str(e), "original_message_id": message.id},
                    self.name
                )
        else:
            self.logger.warning(f"No handler for message type: {message.message_type.value}")
            return None

    async def _handle_task_request(self, message: 'AgentMessage') -> Optional['AgentMessage']:
        """Handle a task request from another agent"""
        from orchestrator.agent_protocol import MessageType

        task_data = message.payload.get("task_data", {})
        task_type = message.payload.get("task_type", "process")

        try:
            # Process the task using the agent's main task processor
            result = await self.process_task({
                "type": task_type,
                **task_data
            })

            self.state["tasks_completed"] += 1

            return message.create_response(
                MessageType.TASK_RESPONSE,
                {
                    "status": "completed",
                    "result": result
                },
                self.name
            )
        except Exception as e:
            self.state["errors"] += 1
            return message.create_response(
                MessageType.TASK_FAILED,
                {
                    "status": "failed",
                    "error": str(e)
                },
                self.name
            )

    async def _handle_review_request(self, message: 'AgentMessage') -> Optional['AgentMessage']:
        """Handle a review request - subclasses should override for specific behavior"""
        from orchestrator.agent_protocol import MessageType, ReviewFeedback

        # Default implementation - approve everything
        # Subclasses (like ReviewAgent) should override this
        items = message.payload.get("items", [])

        feedback = ReviewFeedback(
            approved=True,
            score=0.8,
            issues=[],
            suggestions=["Consider adding more assertions"],
            requires_changes=False
        )

        return message.create_response(
            MessageType.REVIEW_FEEDBACK,
            feedback.to_dict(),
            self.name
        )

    async def _handle_review_feedback(self, message: 'AgentMessage') -> Optional['AgentMessage']:
        """Handle review feedback - typically used to trigger refinement"""
        from orchestrator.agent_protocol import MessageType

        feedback = message.payload
        requires_changes = feedback.get("requires_changes", False)

        if requires_changes:
            # Trigger refinement based on feedback
            change_requests = feedback.get("change_requests", [])
            self.logger.info(f"Received {len(change_requests)} change requests")

            # Subclasses should implement actual refinement logic
            return message.create_response(
                MessageType.REFINEMENT_COMPLETE,
                {
                    "status": "refinement_pending",
                    "message": "Refinement logic should be implemented by subclass"
                },
                self.name
            )

        return None  # No response needed if approved

    async def _handle_refinement_request(self, message: 'AgentMessage') -> Optional['AgentMessage']:
        """Handle a request to refine previous work"""
        from orchestrator.agent_protocol import MessageType

        # Subclasses should override this with specific refinement logic
        original_work = message.payload.get("original_work", {})
        feedback = message.payload.get("feedback", {})

        return message.create_response(
            MessageType.REFINEMENT_COMPLETE,
            {
                "status": "completed",
                "refined_work": original_work,  # Default: return unchanged
                "changes_made": []
            },
            self.name
        )

    async def _handle_status_query(self, message: 'AgentMessage') -> Optional['AgentMessage']:
        """Handle a status query"""
        from orchestrator.agent_protocol import MessageType

        return message.create_response(
            MessageType.STATUS_RESPONSE,
            {
                "agent_name": self.name,
                "status": self.state.get("status", "unknown"),
                "metrics": self.get_metrics(),
                "capabilities": self.get_capabilities()
            },
            self.name
        )

    async def _handle_healing_request(self, message: 'AgentMessage') -> Optional['AgentMessage']:
        """Handle a self-healing request - SelfHealingAgent should override"""
        from orchestrator.agent_protocol import MessageType

        # Default: cannot heal, subclasses should override
        return message.create_response(
            MessageType.HEALING_FAILED,
            {
                "status": "not_supported",
                "message": f"{self.name} does not support self-healing"
            },
            self.name
        )

    async def send_to_agent(
        self,
        recipient_name: str,
        message_type: 'MessageType',
        payload: Dict[str, Any],
        wait_for_response: bool = True,
        message_bus: Optional['AgentMessageBus'] = None
    ) -> Optional['AgentMessage']:
        """
        Send a message to another agent via the message bus.

        Args:
            recipient_name: Name of the recipient agent
            message_type: Type of message to send
            payload: Message payload
            wait_for_response: Whether to wait for a response
            message_bus: Optional message bus (uses shared instance if not provided)

        Returns:
            Response message if wait_for_response is True
        """
        from orchestrator.agent_protocol import AgentMessage as AM

        message = AM(
            message_type=message_type,
            sender_agent=self.name,
            recipient_agent=recipient_name,
            payload=payload,
            requires_response=wait_for_response
        )

        if message_bus:
            return await message_bus.send_message(message, wait_for_response=wait_for_response)

        # If no message bus provided, log warning
        self.logger.warning("No message bus available for agent communication")
        return None

    # =========================================================================
    # End of Agent Message Handling
    # =========================================================================

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
        """Get agent performance metrics including LLM usage"""
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
            # LLM metrics
            "llm_calls": self.state.get("llm_calls", 0),
            "cache_hits": self.state.get("cache_hits", 0),
            "total_tokens": self.state.get("total_tokens", 0),
            "cache_hit_rate": (
                self.state.get("cache_hits", 0) /
                max(self.state.get("llm_calls", 0), 1)
            ),
            "llm_provider": self.state.get("llm_provider", "unknown"),
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

