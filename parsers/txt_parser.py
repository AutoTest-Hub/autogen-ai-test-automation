"""
TXT File Parser for AutoGen Test Automation Framework
Parses natural language test descriptions from .txt files
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestStep:
    """Represents a single test step"""
    step_number: int
    action: str
    expected_result: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ParsedTestFile:
    """Represents a parsed test file"""
    file_path: str
    file_format: str
    test_name: str
    description: str
    priority: str
    tags: List[str]
    application_url: str
    test_steps: List[TestStep]
    expected_results: List[str]
    test_data: Dict[str, Any]
    environment: Dict[str, Any]
    metadata: Dict[str, Any]
    parsing_errors: List[str]
    parsed_at: datetime


class TxtTestFileParser:
    """Parser for .txt format test files with natural language descriptions"""
    
    def __init__(self):
        self.logger = logging.getLogger("parser.txt")
        
        # Regex patterns for parsing different sections
        self.section_patterns = {
            "test_name": [
                r"^(?:Test Name|Scenario|Test Case):\s*(.+)$",
                r"^# (.+)$"  # Markdown-style header
            ],
            "target_url": [
                r"^(?:Target|Application|URL|Website):\s*(.+)$",
                r"^(?:Base URL|App URL):\s*(.+)$"
            ],
            "priority": [
                r"^Priority:\s*(.+)$",
                r"^(?:Importance|Severity):\s*(.+)$"
            ],
            "tags": [
                r"^Tags:\s*(.+)$",
                r"^(?:Categories|Labels):\s*(.+)$"
            ],
            "description_start": [
                r"^(?:Description|Objective|Purpose|Summary):\s*$",
                r"^(?:Test Description|Overview):\s*$"
            ],
            "steps_start": [
                r"^(?:Test Steps|Steps|Procedure|Actions):\s*$",
                r"^(?:Execution Steps|Test Procedure):\s*$"
            ],
            "results_start": [
                r"^(?:Expected Results|Expected Outcome|Verification):\s*$",
                r"^(?:Success Criteria|Acceptance Criteria):\s*$"
            ],
            "data_start": [
                r"^(?:Test Data|Data|Test Inputs):\s*$",
                r"^(?:Input Data|Test Values):\s*$"
            ],
            "environment_start": [
                r"^(?:Environment|Test Environment|Setup):\s*$",
                r"^(?:Configuration|Settings):\s*$"
            ]
        }
        
        # Step number patterns
        self.step_patterns = [
            r"^(\d+)\.?\s+(.+)$",  # "1. Action" or "1 Action"
            r"^Step\s+(\d+):\s*(.+)$",  # "Step 1: Action"
            r"^(\d+)\)\s+(.+)$",  # "1) Action"
            r"^-\s+(.+)$",  # "- Action" (bullet points)
            r"^\*\s+(.+)$",  # "* Action" (asterisk bullets)
            r"^•\s+(.+)$"  # "• Action" (bullet character)
        ]
    
    def parse_file(self, file_path: str, content: str) -> ParsedTestFile:
        """Parse a .txt test file and return structured data"""
        self.logger.info(f"Parsing TXT file: {file_path}")
        
        parsing_errors = []
        
        try:
            # Initialize parsed data with defaults
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
            
            # Split content into lines for processing
            lines = content.strip().split('\n')
            
            # Parse the file line by line
            current_section = None
            description_lines = []
            step_counter = 0
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                try:
                    # Check for section headers
                    section_found = self._identify_section(line)
                    if section_found:
                        current_section = section_found
                        continue
                    
                    # Check for direct field matches (like "Test Name: ...")
                    field_match = self._extract_field_value(line)
                    if field_match:
                        field_name, field_value = field_match
                        if field_name == "test_name":
                            parsed_data["test_name"] = field_value
                        elif field_name == "target_url":
                            parsed_data["application_url"] = field_value
                        elif field_name == "priority":
                            parsed_data["priority"] = field_value.title()
                        elif field_name == "tags":
                            parsed_data["tags"] = [tag.strip() for tag in field_value.split(",")]
                        continue
                    
                    # Process content based on current section
                    if current_section == "description":
                        description_lines.append(line)
                    elif current_section == "steps":
                        step = self._parse_test_step(line, step_counter)
                        if step:
                            parsed_data["test_steps"].append(step)
                            step_counter += 1
                    elif current_section == "results":
                        result = self._parse_expected_result(line)
                        if result:
                            parsed_data["expected_results"].append(result)
                    elif current_section == "data":
                        data_item = self._parse_test_data(line)
                        if data_item:
                            parsed_data["test_data"].update(data_item)
                    elif current_section == "environment":
                        env_item = self._parse_environment_setting(line)
                        if env_item:
                            parsed_data["environment"].update(env_item)
                
                except Exception as e:
                    error_msg = f"Error parsing line {line_num}: {line} - {str(e)}"
                    parsing_errors.append(error_msg)
                    self.logger.warning(error_msg)
            
            # Join description lines
            if description_lines:
                parsed_data["description"] = " ".join(description_lines).strip()
            
            # Add metadata
            parsed_data["metadata"] = {
                "total_lines": len(lines),
                "total_steps": len(parsed_data["test_steps"]),
                "has_test_data": bool(parsed_data["test_data"]),
                "has_environment_config": bool(parsed_data["environment"]),
                "complexity_indicators": self._analyze_complexity(parsed_data)
            }
            
            # Create and return ParsedTestFile object
            return ParsedTestFile(
                file_path=file_path,
                file_format="txt",
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
            
        except Exception as e:
            error_msg = f"Critical error parsing file {file_path}: {str(e)}"
            parsing_errors.append(error_msg)
            self.logger.error(error_msg)
            
            # Return minimal parsed file with error information
            return ParsedTestFile(
                file_path=file_path,
                file_format="txt",
                test_name="Parse Error",
                description=f"Failed to parse file: {str(e)}",
                priority="High",
                tags=["parse_error"],
                application_url="",
                test_steps=[],
                expected_results=[],
                test_data={},
                environment={},
                metadata={"parse_failed": True},
                parsing_errors=parsing_errors,
                parsed_at=datetime.now()
            )
    
    def _identify_section(self, line: str) -> Optional[str]:
        """Identify which section a line represents"""
        for section, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    return section.replace("_start", "")
        return None
    
    def _extract_field_value(self, line: str) -> Optional[tuple]:
        """Extract field name and value from a line like 'Field: Value'"""
        for field_name, patterns in self.section_patterns.items():
            if field_name.endswith("_start"):
                continue
            
            for pattern in patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    return field_name, match.group(1).strip()
        return None
    
    def _parse_test_step(self, line: str, current_counter: int) -> Optional[TestStep]:
        """Parse a test step from a line"""
        for pattern in self.step_patterns:
            match = re.match(pattern, line)
            if match:
                if len(match.groups()) == 2:
                    # Numbered step
                    step_num = int(match.group(1))
                    action = match.group(2).strip()
                elif len(match.groups()) == 1:
                    # Bullet point step
                    step_num = current_counter + 1
                    action = match.group(1).strip()
                else:
                    continue
                
                return TestStep(
                    step_number=step_num,
                    action=action,
                    expected_result=None,
                    notes=None
                )
        return None
    
    def _parse_expected_result(self, line: str) -> Optional[str]:
        """Parse an expected result from a line"""
        # Remove common bullet point markers
        result_patterns = [
            r"^-\s+(.+)$",
            r"^\*\s+(.+)$",
            r"^•\s+(.+)$",
            r"^(\d+)\.?\s+(.+)$",
            r"^(.+)$"  # Fallback for plain text
        ]
        
        for pattern in result_patterns:
            match = re.match(pattern, line)
            if match:
                if len(match.groups()) == 2:
                    return match.group(2).strip()
                else:
                    return match.group(1).strip()
        
        return line.strip() if line.strip() else None
    
    def _parse_test_data(self, line: str) -> Optional[Dict[str, str]]:
        """Parse test data from a line"""
        # Look for key-value pairs
        data_patterns = [
            r"^(.+?):\s*(.+)$",  # "key: value"
            r"^(.+?)\s*=\s*(.+)$",  # "key = value"
            r"^-\s*(.+?):\s*(.+)$",  # "- key: value"
        ]
        
        for pattern in data_patterns:
            match = re.match(pattern, line)
            if match:
                key = match.group(1).strip().lower().replace(" ", "_")
                value = match.group(2).strip()
                return {key: value}
        
        return None
    
    def _parse_environment_setting(self, line: str) -> Optional[Dict[str, str]]:
        """Parse environment setting from a line"""
        # Same logic as test data parsing
        return self._parse_test_data(line)
    
    def _analyze_complexity(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze complexity indicators in the parsed data"""
        complexity_indicators = {
            "step_count": len(parsed_data["test_steps"]),
            "has_authentication": False,
            "has_data_input": False,
            "has_file_operations": False,
            "has_api_calls": False,
            "has_database_operations": False,
            "estimated_complexity": "low"
        }
        
        # Analyze test content for complexity indicators
        all_text = (
            parsed_data["description"] + " " +
            " ".join([step.action for step in parsed_data["test_steps"]]) + " " +
            " ".join(parsed_data["expected_results"])
        ).lower()
        
        # Check for complexity keywords
        complexity_keywords = {
            "has_authentication": ["login", "sign in", "authenticate", "password", "username"],
            "has_data_input": ["enter", "input", "type", "fill", "form", "data"],
            "has_file_operations": ["upload", "download", "file", "attachment", "import", "export"],
            "has_api_calls": ["api", "rest", "endpoint", "request", "response", "json"],
            "has_database_operations": ["database", "db", "sql", "query", "record", "table"]
        }
        
        for indicator, keywords in complexity_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                complexity_indicators[indicator] = True
        
        # Calculate estimated complexity
        complexity_score = 0
        complexity_score += min(complexity_indicators["step_count"] * 0.1, 0.5)
        
        for key, value in complexity_indicators.items():
            if key.startswith("has_") and value:
                complexity_score += 0.15
        
        if complexity_score < 0.3:
            complexity_indicators["estimated_complexity"] = "low"
        elif complexity_score < 0.7:
            complexity_indicators["estimated_complexity"] = "medium"
        else:
            complexity_indicators["estimated_complexity"] = "high"
        
        complexity_indicators["complexity_score"] = round(complexity_score, 2)
        
        return complexity_indicators
    
    def validate_parsed_file(self, parsed_file: ParsedTestFile) -> Dict[str, Any]:
        """Validate a parsed test file and return validation results"""
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # Check for required fields
        if not parsed_file.test_name or parsed_file.test_name == "Unknown Test":
            validation_results["errors"].append("Test name is missing or invalid")
            validation_results["is_valid"] = False
        
        if not parsed_file.test_steps:
            validation_results["errors"].append("No test steps found")
            validation_results["is_valid"] = False
        
        if not parsed_file.application_url:
            validation_results["warnings"].append("Application URL is missing")
        
        # Check for best practices
        if len(parsed_file.test_steps) > 20:
            validation_results["warnings"].append("Test has many steps - consider breaking into smaller tests")
        
        if not parsed_file.description:
            validation_results["suggestions"].append("Add a test description for better documentation")
        
        if not parsed_file.expected_results:
            validation_results["suggestions"].append("Add expected results for better validation")
        
        if not parsed_file.tags:
            validation_results["suggestions"].append("Add tags for better test organization")
        
        # Check for parsing errors
        if parsed_file.parsing_errors:
            validation_results["warnings"].extend(parsed_file.parsing_errors)
        
        return validation_results
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return [".txt", ".text"]
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get information about this parser"""
        return {
            "name": "TXT Test File Parser",
            "version": "1.0.0",
            "description": "Parses natural language test descriptions from .txt files",
            "supported_formats": self.get_supported_formats(),
            "features": [
                "Natural language parsing",
                "Flexible section detection",
                "Step numbering support",
                "Complexity analysis",
                "Validation and suggestions"
            ]
        }

