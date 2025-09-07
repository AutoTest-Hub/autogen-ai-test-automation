"""
JSON File Parser for AutoGen Test Automation Framework
Parses structured test descriptions from .json files
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Try to import jsonschema, fallback to simple validator
try:
    from jsonschema import validate, ValidationError, Draft7Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    # Fallback to simple validator if jsonschema is not available
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from simple_json_validator import validate, ValidationError
    JSONSCHEMA_AVAILABLE = False
    
    # Mock Draft7Validator for compatibility
    class Draft7Validator:
        def __init__(self, schema):
            self.schema = schema
        
        def iter_errors(self, instance):
            return []

from .txt_parser import TestStep, ParsedTestFile


class JsonTestFileParser:
    """Parser for .json format test files with structured data"""
    
    def __init__(self):
        self.logger = logging.getLogger("parser.json")
        
        # JSON schema for test file validation
        self.test_file_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "testName": {"type": "string", "minLength": 1},
                "description": {"type": "string"},
                "priority": {
                    "type": "string",
                    "enum": ["Low", "Medium", "High", "Critical"]
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "application": {"type": "string", "format": "uri"},
                "testSteps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step": {"type": "integer", "minimum": 1},
                            "action": {"type": "string", "minLength": 1},
                            "expectedResult": {"type": "string"},
                            "data": {"type": "object"},
                            "timeout": {"type": "integer", "minimum": 1000},
                            "screenshot": {"type": "boolean"},
                            "notes": {"type": "string"}
                        },
                        "required": ["step", "action"],
                        "additionalProperties": True
                    },
                    "minItems": 1
                },
                "expectedResults": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "testData": {
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "properties": {
                                "username": {"type": "string"},
                                "password": {"type": "string"}
                            }
                        },
                        "testInputs": {"type": "object"},
                        "expectedOutputs": {"type": "object"}
                    },
                    "additionalProperties": True
                },
                "environment": {
                    "type": "object",
                    "properties": {
                        "browser": {
                            "type": "string",
                            "enum": ["chrome", "firefox", "safari", "edge", "chromium"]
                        },
                        "headless": {"type": "boolean"},
                        "timeout": {"type": "integer", "minimum": 1000},
                        "viewport": {
                            "type": "object",
                            "properties": {
                                "width": {"type": "integer", "minimum": 1},
                                "height": {"type": "integer", "minimum": 1}
                            }
                        },
                        "baseUrl": {"type": "string", "format": "uri"},
                        "apiBaseUrl": {"type": "string", "format": "uri"}
                    },
                    "additionalProperties": True
                },
                "configuration": {
                    "type": "object",
                    "properties": {
                        "framework": {
                            "type": "string",
                            "enum": ["playwright", "selenium", "requests", "httpx", "auto"]
                        },
                        "parallel": {"type": "boolean"},
                        "retries": {"type": "integer", "minimum": 0},
                        "reportFormat": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["html", "json", "xml", "junit"]
                            }
                        }
                    },
                    "additionalProperties": True
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "author": {"type": "string"},
                        "created": {"type": "string", "format": "date-time"},
                        "lastModified": {"type": "string", "format": "date-time"},
                        "version": {"type": "string"},
                        "requirements": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "additionalProperties": True
                }
            },
            "required": ["testName", "testSteps"],
            "additionalProperties": True
        }
    
    def parse_file(self, file_path: str, content: str) -> ParsedTestFile:
        """Parse a .json test file and return structured data"""
        self.logger.info(f"Parsing JSON file: {file_path}")
        
        parsing_errors = []
        
        try:
            # Parse JSON content
            json_data = json.loads(content)
            
            # Validate against schema
            validation_errors = self._validate_json_schema(json_data)
            if validation_errors:
                parsing_errors.extend(validation_errors)
            
            # Extract and normalize data
            parsed_data = self._extract_test_data(json_data, parsing_errors)
            
            # Create and return ParsedTestFile object
            return ParsedTestFile(
                file_path=file_path,
                file_format="json",
                test_name=parsed_data["test_name"],
                description=parsed_data["description"],
                priority=parsed_data["priority"],
                tags=parsed_data["tags"],
                application_url=parsed_data["application_url"],
                test_steps=parsed_data["test_steps"],
                expected_results=parsed_data["expected_results"],
                test_data=parsed_data["test_data"],
                environment=parsed_data["environment"],
                metadata=parsed_data["metadata"],
                parsing_errors=parsing_errors,
                parsed_at=datetime.now()
            )
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format in {file_path}: {str(e)}"
            parsing_errors.append(error_msg)
            self.logger.error(error_msg)
            
            return self._create_error_parsed_file(file_path, error_msg, parsing_errors)
            
        except Exception as e:
            error_msg = f"Critical error parsing JSON file {file_path}: {str(e)}"
            parsing_errors.append(error_msg)
            self.logger.error(error_msg)
            
            return self._create_error_parsed_file(file_path, error_msg, parsing_errors)
    
    def _validate_json_schema(self, json_data: Dict[str, Any]) -> List[str]:
        """Validate JSON data against schema and return validation errors"""
        validation_errors = []
        
        try:
            validator = Draft7Validator(self.test_file_schema)
            errors = sorted(validator.iter_errors(json_data), key=lambda e: e.path)
            
            for error in errors:
                error_path = " -> ".join([str(p) for p in error.path])
                error_msg = f"Schema validation error at '{error_path}': {error.message}"
                validation_errors.append(error_msg)
                self.logger.warning(error_msg)
                
        except Exception as e:
            error_msg = f"Schema validation failed: {str(e)}"
            validation_errors.append(error_msg)
            self.logger.error(error_msg)
        
        return validation_errors
    
    def _extract_test_data(self, json_data: Dict[str, Any], parsing_errors: List[str]) -> Dict[str, Any]:
        """Extract and normalize test data from JSON"""
        
        # Initialize with defaults
        parsed_data = {
            "test_name": "Unknown Test",
            "description": "",
            "priority": "Medium",
            "tags": [],
            "application_url": "",
            "test_steps": [],
            "expected_results": [],
            "test_data": {},
            "environment": {},
            "metadata": {}
        }
        
        try:
            # Extract basic information
            parsed_data["test_name"] = json_data.get("testName", "Unknown Test")
            parsed_data["description"] = json_data.get("description", "")
            parsed_data["priority"] = json_data.get("priority", "Medium")
            parsed_data["tags"] = json_data.get("tags", [])
            parsed_data["application_url"] = json_data.get("application", "")
            
            # Extract test steps
            test_steps_data = json_data.get("testSteps", [])
            parsed_data["test_steps"] = self._parse_test_steps(test_steps_data, parsing_errors)
            
            # Extract expected results
            parsed_data["expected_results"] = json_data.get("expectedResults", [])
            
            # Extract test data
            parsed_data["test_data"] = self._normalize_test_data(json_data.get("testData", {}))
            
            # Extract environment configuration
            parsed_data["environment"] = self._normalize_environment(json_data.get("environment", {}))
            
            # Extract and enhance metadata
            metadata = json_data.get("metadata", {})
            metadata.update({
                "original_format": "json",
                "total_steps": len(parsed_data["test_steps"]),
                "has_test_data": bool(parsed_data["test_data"]),
                "has_environment_config": bool(parsed_data["environment"]),
                "complexity_analysis": self._analyze_json_complexity(json_data),
                "configuration": json_data.get("configuration", {})
            })
            parsed_data["metadata"] = metadata
            
        except Exception as e:
            error_msg = f"Error extracting test data: {str(e)}"
            parsing_errors.append(error_msg)
            self.logger.error(error_msg)
        
        return parsed_data
    
    def _parse_test_steps(self, test_steps_data: List[Dict[str, Any]], parsing_errors: List[str]) -> List[TestStep]:
        """Parse test steps from JSON data"""
        test_steps = []
        
        for i, step_data in enumerate(test_steps_data):
            try:
                step = TestStep(
                    step_number=step_data.get("step", i + 1),
                    action=step_data.get("action", ""),
                    expected_result=step_data.get("expectedResult"),
                    notes=step_data.get("notes")
                )
                
                # Add additional JSON-specific attributes
                if hasattr(step, '__dict__'):
                    step.__dict__.update({
                        "data": step_data.get("data", {}),
                        "timeout": step_data.get("timeout"),
                        "screenshot": step_data.get("screenshot", False),
                        "selector": step_data.get("selector"),
                        "wait_condition": step_data.get("waitCondition")
                    })
                
                test_steps.append(step)
                
            except Exception as e:
                error_msg = f"Error parsing test step {i + 1}: {str(e)}"
                parsing_errors.append(error_msg)
                self.logger.warning(error_msg)
        
        return test_steps
    
    def _normalize_test_data(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize test data structure"""
        normalized = {}
        
        # Handle credentials
        if "credentials" in test_data:
            normalized["credentials"] = test_data["credentials"]
        
        # Handle test inputs
        if "testInputs" in test_data:
            normalized["test_inputs"] = test_data["testInputs"]
        
        # Handle expected outputs
        if "expectedOutputs" in test_data:
            normalized["expected_outputs"] = test_data["expectedOutputs"]
        
        # Include any additional data
        for key, value in test_data.items():
            if key not in ["credentials", "testInputs", "expectedOutputs"]:
                normalized[key] = value
        
        return normalized
    
    def _normalize_environment(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize environment configuration"""
        normalized = {}
        
        # Browser settings
        if "browser" in environment:
            normalized["browser"] = environment["browser"]
        
        if "headless" in environment:
            normalized["headless"] = environment["headless"]
        
        if "timeout" in environment:
            normalized["timeout"] = environment["timeout"]
        
        # Viewport settings
        if "viewport" in environment:
            normalized["viewport"] = environment["viewport"]
        
        # URL settings
        if "baseUrl" in environment:
            normalized["base_url"] = environment["baseUrl"]
        
        if "apiBaseUrl" in environment:
            normalized["api_base_url"] = environment["apiBaseUrl"]
        
        # Include any additional environment settings
        for key, value in environment.items():
            if key not in ["browser", "headless", "timeout", "viewport", "baseUrl", "apiBaseUrl"]:
                normalized[key] = value
        
        return normalized
    
    def _analyze_json_complexity(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze complexity indicators in JSON test data"""
        complexity_analysis = {
            "step_count": len(json_data.get("testSteps", [])),
            "has_test_data": bool(json_data.get("testData", {})),
            "has_environment_config": bool(json_data.get("environment", {})),
            "has_configuration": bool(json_data.get("configuration", {})),
            "has_metadata": bool(json_data.get("metadata", {})),
            "complexity_indicators": {},
            "estimated_complexity": "low"
        }
        
        # Analyze test content for complexity indicators
        all_text = json.dumps(json_data).lower()
        
        complexity_keywords = {
            "authentication": ["login", "sign in", "authenticate", "password", "username", "credentials"],
            "data_operations": ["create", "update", "delete", "modify", "save", "submit"],
            "file_operations": ["upload", "download", "file", "attachment", "import", "export"],
            "api_integration": ["api", "rest", "endpoint", "request", "response", "json", "xml"],
            "database_operations": ["database", "db", "sql", "query", "record", "table"],
            "payment_processing": ["payment", "checkout", "purchase", "billing", "credit card"],
            "multi_step_workflows": ["workflow", "process", "sequence", "chain", "pipeline"]
        }
        
        for category, keywords in complexity_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                complexity_analysis["complexity_indicators"][category] = True
        
        # Calculate complexity score
        complexity_score = 0
        complexity_score += min(complexity_analysis["step_count"] * 0.05, 0.3)
        complexity_score += len(complexity_analysis["complexity_indicators"]) * 0.1
        
        if complexity_analysis["has_test_data"]:
            complexity_score += 0.1
        if complexity_analysis["has_environment_config"]:
            complexity_score += 0.05
        
        # Determine complexity level
        if complexity_score < 0.3:
            complexity_analysis["estimated_complexity"] = "low"
        elif complexity_score < 0.7:
            complexity_analysis["estimated_complexity"] = "medium"
        else:
            complexity_analysis["estimated_complexity"] = "high"
        
        complexity_analysis["complexity_score"] = round(complexity_score, 2)
        
        return complexity_analysis
    
    def _create_error_parsed_file(self, file_path: str, error_msg: str, parsing_errors: List[str]) -> ParsedTestFile:
        """Create a ParsedTestFile object for error cases"""
        return ParsedTestFile(
            file_path=file_path,
            file_format="json",
            test_name="Parse Error",
            description=f"Failed to parse JSON file: {error_msg}",
            priority="High",
            tags=["parse_error"],
            application_url="",
            test_steps=[],
            expected_results=[],
            test_data={},
            environment={},
            metadata={"parse_failed": True, "error_message": error_msg},
            parsing_errors=parsing_errors,
            parsed_at=datetime.now()
        )
    
    def validate_parsed_file(self, parsed_file: ParsedTestFile) -> Dict[str, Any]:
        """Validate a parsed JSON test file and return validation results"""
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": [],
            "schema_compliance": True
        }
        
        # Check for required fields
        if not parsed_file.test_name or parsed_file.test_name == "Unknown Test":
            validation_results["errors"].append("Test name is missing or invalid")
            validation_results["is_valid"] = False
        
        if not parsed_file.test_steps:
            validation_results["errors"].append("No test steps found")
            validation_results["is_valid"] = False
        
        # Check step numbering
        step_numbers = [step.step_number for step in parsed_file.test_steps]
        if len(set(step_numbers)) != len(step_numbers):
            validation_results["warnings"].append("Duplicate step numbers found")
        
        expected_numbers = list(range(1, len(parsed_file.test_steps) + 1))
        if step_numbers != expected_numbers:
            validation_results["warnings"].append("Step numbers are not sequential")
        
        # Check for best practices
        if len(parsed_file.test_steps) > 25:
            validation_results["warnings"].append("Test has many steps - consider breaking into smaller tests")
        
        if not parsed_file.description:
            validation_results["suggestions"].append("Add a test description for better documentation")
        
        if not parsed_file.expected_results:
            validation_results["suggestions"].append("Add expected results for comprehensive validation")
        
        if not parsed_file.tags:
            validation_results["suggestions"].append("Add tags for better test organization and filtering")
        
        # Check environment configuration
        if not parsed_file.environment:
            validation_results["suggestions"].append("Consider adding environment configuration for consistent execution")
        
        # Check for parsing errors
        if parsed_file.parsing_errors:
            validation_results["warnings"].extend(parsed_file.parsing_errors)
            validation_results["schema_compliance"] = False
        
        return validation_results
    
    def generate_json_template(self, test_name: str = "Sample Test") -> Dict[str, Any]:
        """Generate a JSON template for creating new test files"""
        return {
            "testName": test_name,
            "description": "Description of what this test validates",
            "priority": "Medium",
            "tags": ["sample", "template"],
            "application": "https://example.com",
            "testSteps": [
                {
                    "step": 1,
                    "action": "Navigate to the application homepage",
                    "expectedResult": "Homepage loads successfully",
                    "timeout": 30000,
                    "screenshot": True
                },
                {
                    "step": 2,
                    "action": "Click on the login button",
                    "expectedResult": "Login form is displayed",
                    "selector": "button[data-testid='login']",
                    "timeout": 10000
                }
            ],
            "expectedResults": [
                "User successfully completes the workflow",
                "All data is saved correctly",
                "No errors are displayed"
            ],
            "testData": {
                "credentials": {
                    "username": "testuser",
                    "password": "testpass"
                },
                "testInputs": {
                    "sampleField": "sample value"
                }
            },
            "environment": {
                "browser": "chromium",
                "headless": False,
                "timeout": 30000,
                "viewport": {
                    "width": 1920,
                    "height": 1080
                },
                "baseUrl": "https://example.com"
            },
            "configuration": {
                "framework": "playwright",
                "parallel": False,
                "retries": 3,
                "reportFormat": ["html", "json"]
            },
            "metadata": {
                "author": "Test Automation Team",
                "created": datetime.now().isoformat(),
                "version": "1.0.0",
                "requirements": ["User authentication", "Data validation"]
            }
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return [".json"]
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get information about this parser"""
        return {
            "name": "JSON Test File Parser",
            "version": "1.0.0",
            "description": "Parses structured test descriptions from .json files",
            "supported_formats": self.get_supported_formats(),
            "features": [
                "JSON schema validation",
                "Structured data parsing",
                "Complex test step support",
                "Environment configuration",
                "Metadata management",
                "Template generation"
            ],
            "schema_version": "1.0"
        }

