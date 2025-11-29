#!/usr/bin/env python3
"""
Simple JSON validator to replace jsonschema dependency
Provides basic validation for test scenario JSON files
"""

import json
from typing import Dict, Any, List, Optional, Union

class SimpleJsonValidator:
    """Simple JSON validator for test scenarios"""
    
    def __init__(self):
        self.test_scenario_schema = {
            "required_fields": ["testName", "testSteps"],
            "optional_fields": ["description", "priority", "tags", "application", "testType", "environment", "testData", "configuration"],
            "field_types": {
                "testName": str,
                "description": str,
                "priority": str,
                "tags": list,
                "application": str,
                "testType": str,
                "testSteps": list,
                "environment": dict,
                "testData": dict,
                "configuration": dict
            }
        }
    
    def validate_test_scenario(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a test scenario JSON object"""
        errors = []
        warnings = []
        
        # Check required fields
        for field in self.test_scenario_schema["required_fields"]:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check field types
        for field, expected_type in self.test_scenario_schema["field_types"].items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    errors.append(f"Field '{field}' should be of type {expected_type.__name__}, got {type(data[field]).__name__}")
        
        # Validate test steps structure
        if "testSteps" in data and isinstance(data["testSteps"], list):
            for i, step in enumerate(data["testSteps"]):
                if not isinstance(step, dict):
                    errors.append(f"Test step {i+1} should be an object")
                    continue
                
                if "step" not in step:
                    warnings.append(f"Test step {i+1} missing 'step' number")
                
                if "action" not in step and "description" not in step:
                    errors.append(f"Test step {i+1} missing 'action' or 'description'")
        
        # Validate environment structure if present
        if "environment" in data and isinstance(data["environment"], dict):
            env = data["environment"]
            if "timeout" in env and not isinstance(env["timeout"], (int, float)):
                errors.append("Environment timeout should be a number")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_json_file(self, file_path: str) -> Dict[str, Any]:
        """Validate a JSON test scenario file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            validation_result = self.validate_test_scenario(data)
            validation_result["file_path"] = file_path
            validation_result["parsed_data"] = data
            
            return validation_result
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "errors": [f"Invalid JSON format: {str(e)}"],
                "warnings": [],
                "file_path": file_path
            }
        except FileNotFoundError:
            return {
                "valid": False,
                "errors": [f"File not found: {file_path}"],
                "warnings": [],
                "file_path": file_path
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "file_path": file_path
            }

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Simple schema validation function to replace jsonschema.validate"""
    validator = SimpleJsonValidator()
    result = validator.validate_test_scenario(data)
    return result["valid"]

# Compatibility function for existing code
def validate(instance: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Compatibility function that raises exception on validation failure"""
    validator = SimpleJsonValidator()
    result = validator.validate_test_scenario(instance)
    
    if not result["valid"]:
        error_msg = "; ".join(result["errors"])
        raise ValueError(f"Validation failed: {error_msg}")

class ValidationError(Exception):
    """Custom validation error for compatibility"""
    pass

