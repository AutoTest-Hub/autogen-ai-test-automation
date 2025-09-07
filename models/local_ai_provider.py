#!/usr/bin/env python3
"""
Local AI Provider for AutoGen Framework
Integrates with Ollama for enterprise-grade local AI inference
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
import aiohttp
import requests
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Specialized model types for different agent roles"""
    CODE_GENERATION = "code_generation"
    GENERAL_INTELLIGENCE = "general_intelligence"
    PLANNING = "planning"
    REVIEW = "review"
    EXECUTION = "execution"
    REPORTING = "reporting"

@dataclass
class LocalModelConfig:
    """Configuration for local AI models"""
    name: str
    model_type: ModelType
    ollama_model: str
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 1024
    timeout: int = 30

class LocalAIProvider:
    """
    Local AI Provider using Ollama for enterprise-grade AI inference
    Supports complete offline operation and data privacy
    
    This class integrates with the AutoGen framework to provide:
    - Local AI model hosting via Ollama
    - Specialized models for different agent types
    - Complete data privacy (no external API calls)
    - Enterprise-grade security and compliance
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = {}
        self.model_configs = self._initialize_model_configs()
        self._check_service_status()
        
    def _initialize_model_configs(self) -> Dict[ModelType, LocalModelConfig]:
        """Initialize optimized model configurations for different agent roles"""
        return {
            ModelType.CODE_GENERATION: LocalModelConfig(
                name="Test Creation Agent Model",
                model_type=ModelType.CODE_GENERATION,
                ollama_model="phi3:mini",  # Optimized for code generation
                temperature=0.3,  # Lower temperature for deterministic code
                max_tokens=2048
            ),
            ModelType.GENERAL_INTELLIGENCE: LocalModelConfig(
                name="General Purpose Agent Model", 
                model_type=ModelType.GENERAL_INTELLIGENCE,
                ollama_model="tinyllama:latest",  # Fast and efficient
                temperature=0.7,
                max_tokens=1024
            ),
            ModelType.PLANNING: LocalModelConfig(
                name="Planning Agent Model",
                model_type=ModelType.PLANNING,
                ollama_model="phi3:mini",  # Good for strategic thinking
                temperature=0.5,
                max_tokens=1536
            ),
            ModelType.REVIEW: LocalModelConfig(
                name="Review Agent Model",
                model_type=ModelType.REVIEW,
                ollama_model="phi3:mini",  # Good for analysis
                temperature=0.4,
                max_tokens=1536
            ),
            ModelType.EXECUTION: LocalModelConfig(
                name="Execution Agent Model",
                model_type=ModelType.EXECUTION,
                ollama_model="tinyllama:latest",  # Fast execution
                temperature=0.2,
                max_tokens=512
            ),
            ModelType.REPORTING: LocalModelConfig(
                name="Reporting Agent Model",
                model_type=ModelType.REPORTING,
                ollama_model="phi3:mini",  # Good for reports
                temperature=0.6,
                max_tokens=2048
            )
        }
    
    def _check_service_status(self) -> bool:
        """Check if Ollama service is running and update available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = {model['name']: model for model in data.get('models', [])}
                logger.info(f"Ollama service is running. Available models: {list(self.available_models.keys())}")
                return True
            else:
                logger.warning(f"Ollama service returned status {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"Ollama service not accessible: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if local AI service is available"""
        return len(self.available_models) > 0
    
    def get_fallback_model(self) -> Optional[str]:
        """Get the smallest available model as fallback"""
        if "tinyllama:latest" in self.available_models:
            return "tinyllama:latest"
        elif self.available_models:
            return list(self.available_models.keys())[0]
        return None
    
    async def generate_response_async(self, 
                                    prompt: str, 
                                    model_type: ModelType,
                                    system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate AI response using local models (async version)
        
        Args:
            prompt: User prompt for the AI model
            model_type: Type of model to use based on agent role
            system_prompt: Optional system prompt for context
            
        Returns:
            Dictionary containing response and metadata
        """
        config = self.model_configs.get(model_type)
        if not config:
            raise ValueError(f"No configuration found for model type: {model_type}")
        
        # Check if required model is available, use fallback if needed
        model_to_use = config.ollama_model
        if model_to_use not in self.available_models:
            fallback = self.get_fallback_model()
            if fallback:
                logger.warning(f"Model {model_to_use} not available, using fallback: {fallback}")
                model_to_use = fallback
            else:
                raise RuntimeError("No models available in Ollama")
        
        # Prepare request payload
        payload = {
            "model": model_to_use,
            "prompt": prompt,
            "system": system_prompt or f"You are a specialized AI agent for {model_type.value}. Be concise and accurate.",
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens
            },
            "stream": False
        }
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=config.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_time = time.time() - start_time
                        
                        return {
                            "response": result.get("response", ""),
                            "model": model_to_use,
                            "model_type": model_type.value,
                            "response_time": response_time,
                            "tokens_generated": len(result.get("response", "").split()),
                            "success": True,
                            "metadata": {
                                "temperature": config.temperature,
                                "max_tokens": config.max_tokens,
                                "actual_model": model_to_use,
                                "requested_model": config.ollama_model
                            }
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status} - {error_text}")
                        return {
                            "response": "",
                            "error": f"API error: {response.status}",
                            "success": False
                        }
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout after {config.timeout}s for model {model_to_use}")
            return {
                "response": "",
                "error": "Request timeout",
                "success": False
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "",
                "error": str(e),
                "success": False
            }
    
    def generate_response_sync(self, 
                              prompt: str, 
                              model_type: ModelType,
                              system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate AI response using local models (sync version)
        
        This is the main method used by AutoGen agents for AI inference
        """
        config = self.model_configs.get(model_type)
        if not config:
            raise ValueError(f"No configuration found for model type: {model_type}")
        
        # Check if required model is available, use fallback if needed
        model_to_use = config.ollama_model
        if model_to_use not in self.available_models:
            fallback = self.get_fallback_model()
            if fallback:
                logger.warning(f"Model {model_to_use} not available, using fallback: {fallback}")
                model_to_use = fallback
            else:
                raise RuntimeError("No models available in Ollama")
        
        # Prepare request payload
        payload = {
            "model": model_to_use,
            "prompt": prompt,
            "system": system_prompt or f"You are a specialized AI agent for {model_type.value}. Be concise and accurate.",
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens
            },
            "stream": False
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                response_time = time.time() - start_time
                
                return {
                    "response": result.get("response", ""),
                    "model": model_to_use,
                    "model_type": model_type.value,
                    "response_time": response_time,
                    "tokens_generated": len(result.get("response", "").split()),
                    "success": True,
                    "metadata": {
                        "temperature": config.temperature,
                        "max_tokens": config.max_tokens,
                        "actual_model": model_to_use,
                        "requested_model": config.ollama_model
                    }
                }
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return {
                    "response": "",
                    "error": f"API error: {response.status_code}",
                    "success": False
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout after {config.timeout}s for model {model_to_use}")
            return {
                "response": "",
                "error": "Request timeout",
                "success": False
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "",
                "error": str(e),
                "success": False
            }
    
    def get_model_info(self, model_type: ModelType) -> Dict[str, Any]:
        """Get information about a specific model configuration"""
        config = self.model_configs.get(model_type)
        if not config:
            return {}
        
        return {
            "name": config.name,
            "model_type": config.model_type.value,
            "ollama_model": config.ollama_model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "available": config.ollama_model in self.available_models
        }
    
    def get_all_model_info(self) -> Dict[str, Any]:
        """Get information about all configured models"""
        return {
            model_type.value: self.get_model_info(model_type)
            for model_type in ModelType
        }
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report of local AI service"""
        return {
            "service_available": self.is_available(),
            "base_url": self.base_url,
            "available_models": list(self.available_models.keys()),
            "configured_models": len(self.model_configs),
            "fallback_model": self.get_fallback_model(),
            "model_configurations": self.get_all_model_info()
        }

