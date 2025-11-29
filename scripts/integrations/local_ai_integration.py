#!/usr/bin/env python3
"""
Local AI Model Integration for AutoGen Framework
Enables complete offline operation with Ollama-hosted models
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
    max_tokens: int = 2048
    timeout: int = 30

class LocalAIProvider:
    """
    Local AI Provider using Ollama for enterprise-grade AI inference
    Supports complete offline operation and data privacy
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = {}
        self.model_configs = self._initialize_model_configs()
        
    def _initialize_model_configs(self) -> Dict[ModelType, LocalModelConfig]:
        """Initialize optimized model configurations for different agent roles"""
        return {
            ModelType.CODE_GENERATION: LocalModelConfig(
                name="Test Creation Agent Model",
                model_type=ModelType.CODE_GENERATION,
                ollama_model="codellama:7b",
                temperature=0.3,  # Lower temperature for more deterministic code
                max_tokens=4096
            ),
            ModelType.GENERAL_INTELLIGENCE: LocalModelConfig(
                name="General Purpose Agent Model", 
                model_type=ModelType.GENERAL_INTELLIGENCE,
                ollama_model="mistral:7b",
                temperature=0.7,
                max_tokens=2048
            ),
            ModelType.PLANNING: LocalModelConfig(
                name="Planning Agent Model",
                model_type=ModelType.PLANNING,
                ollama_model="mistral:7b",
                temperature=0.5,  # Balanced for strategic thinking
                max_tokens=3072
            ),
            ModelType.REVIEW: LocalModelConfig(
                name="Review Agent Model",
                model_type=ModelType.REVIEW,
                ollama_model="mistral:7b",
                temperature=0.4,  # Lower for consistent reviews
                max_tokens=2048
            ),
            ModelType.EXECUTION: LocalModelConfig(
                name="Execution Agent Model",
                model_type=ModelType.EXECUTION,
                ollama_model="codellama:7b",
                temperature=0.2,  # Very low for precise execution
                max_tokens=1024
            ),
            ModelType.REPORTING: LocalModelConfig(
                name="Reporting Agent Model",
                model_type=ModelType.REPORTING,
                ollama_model="mistral:7b",
                temperature=0.6,  # Balanced for clear reporting
                max_tokens=3072
            )
        }
    
    async def check_ollama_status(self) -> bool:
        """Check if Ollama service is running and accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.available_models = {model['name']: model for model in data.get('models', [])}
                        logger.info(f"Ollama is running. Available models: {list(self.available_models.keys())}")
                        return True
                    return False
        except Exception as e:
            logger.error(f"Ollama service not accessible: {e}")
            return False
    
    def check_ollama_status_sync(self) -> bool:
        """Synchronous version of Ollama status check"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = {model['name']: model for model in data.get('models', [])}
                logger.info(f"Ollama is running. Available models: {list(self.available_models.keys())}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ollama service not accessible: {e}")
            return False
    
    async def generate_response(self, 
                              prompt: str, 
                              model_type: ModelType,
                              system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate AI response using local models
        
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
        
        # Check if required model is available
        if config.ollama_model not in self.available_models:
            logger.warning(f"Model {config.ollama_model} not available. Available: {list(self.available_models.keys())}")
            # Fallback to first available model
            if self.available_models:
                fallback_model = list(self.available_models.keys())[0]
                logger.info(f"Using fallback model: {fallback_model}")
                config.ollama_model = fallback_model
            else:
                raise RuntimeError("No models available in Ollama")
        
        # Prepare request payload
        payload = {
            "model": config.ollama_model,
            "prompt": prompt,
            "system": system_prompt or f"You are a specialized AI agent for {model_type.value}.",
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
                            "model": config.ollama_model,
                            "model_type": model_type.value,
                            "response_time": response_time,
                            "tokens_generated": len(result.get("response", "").split()),
                            "success": True,
                            "metadata": {
                                "temperature": config.temperature,
                                "max_tokens": config.max_tokens,
                                "actual_model": config.ollama_model
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
            logger.error(f"Timeout after {config.timeout}s for model {config.ollama_model}")
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
        """Synchronous version of generate_response"""
        config = self.model_configs.get(model_type)
        if not config:
            raise ValueError(f"No configuration found for model type: {model_type}")
        
        # Check if required model is available
        if config.ollama_model not in self.available_models:
            logger.warning(f"Model {config.ollama_model} not available. Available: {list(self.available_models.keys())}")
            # Fallback to first available model
            if self.available_models:
                fallback_model = list(self.available_models.keys())[0]
                logger.info(f"Using fallback model: {fallback_model}")
                config.ollama_model = fallback_model
            else:
                raise RuntimeError("No models available in Ollama")
        
        # Prepare request payload
        payload = {
            "model": config.ollama_model,
            "prompt": prompt,
            "system": system_prompt or f"You are a specialized AI agent for {model_type.value}.",
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
                    "model": config.ollama_model,
                    "model_type": model_type.value,
                    "response_time": response_time,
                    "tokens_generated": len(result.get("response", "").split()),
                    "success": True,
                    "metadata": {
                        "temperature": config.temperature,
                        "max_tokens": config.max_tokens,
                        "actual_model": config.ollama_model
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
            logger.error(f"Timeout after {config.timeout}s for model {config.ollama_model}")
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
    
    async def benchmark_models(self) -> Dict[str, Any]:
        """Benchmark all available models for performance comparison"""
        benchmark_prompt = "Write a simple Python function to add two numbers."
        results = {}
        
        for model_type in ModelType:
            logger.info(f"Benchmarking {model_type.value} model...")
            result = await self.generate_response(
                benchmark_prompt, 
                model_type,
                "You are a helpful coding assistant. Provide concise, accurate responses."
            )
            
            results[model_type.value] = {
                "model": result.get("model", "unknown"),
                "response_time": result.get("response_time", 0),
                "tokens_generated": result.get("tokens_generated", 0),
                "success": result.get("success", False),
                "response_length": len(result.get("response", "")),
                "tokens_per_second": result.get("tokens_generated", 0) / max(result.get("response_time", 1), 0.1)
            }
        
        return results

# Example usage and testing
async def main():
    """Test the local AI integration"""
    provider = LocalAIProvider()
    
    # Check Ollama status
    if not await provider.check_ollama_status():
        print("❌ Ollama service is not running. Please start Ollama first.")
        return
    
    print("✅ Ollama service is running!")
    print(f"Available models: {list(provider.available_models.keys())}")
    
    # Test model configurations
    print("\n📋 Model Configurations:")
    model_info = provider.get_all_model_info()
    for model_type, info in model_info.items():
        status = "✅ Available" if info.get("available") else "❌ Not Available"
        print(f"  {model_type}: {info.get('ollama_model')} - {status}")
    
    # Test code generation
    print("\n🧪 Testing Code Generation Agent:")
    code_result = await provider.generate_response(
        "Create a Python function to validate email addresses using regex.",
        ModelType.CODE_GENERATION,
        "You are an expert Python developer. Write clean, well-documented code."
    )
    
    if code_result["success"]:
        print(f"✅ Response generated in {code_result['response_time']:.2f}s")
        print(f"Model: {code_result['model']}")
        print(f"Response preview: {code_result['response'][:200]}...")
    else:
        print(f"❌ Error: {code_result.get('error')}")
    
    # Benchmark all models
    print("\n📊 Benchmarking Models:")
    benchmark_results = await provider.benchmark_models()
    for model_type, results in benchmark_results.items():
        if results["success"]:
            print(f"  {model_type}: {results['response_time']:.2f}s, {results['tokens_per_second']:.1f} tokens/sec")
        else:
            print(f"  {model_type}: ❌ Failed")

if __name__ == "__main__":
    asyncio.run(main())

