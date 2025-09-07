"""
Unified Test File Parser for AutoGen Test Automation Framework
Handles both .txt and .json file formats with automatic format detection
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from .txt_parser import TxtTestFileParser, ParsedTestFile
from .json_parser import JsonTestFileParser


class UnifiedTestFileParser:
    """Unified parser that handles multiple test file formats"""
    
    def __init__(self):
        self.logger = logging.getLogger("parser.unified")
        
        # Initialize format-specific parsers
        self.txt_parser = TxtTestFileParser()
        self.json_parser = JsonTestFileParser()
        
        # Format detection mappings
        self.format_parsers = {
            ".txt": self.txt_parser,
            ".text": self.txt_parser,
            ".json": self.json_parser
        }
        
        # Statistics tracking
        self.parsing_stats = {
            "total_files_parsed": 0,
            "successful_parses": 0,
            "failed_parses": 0,
            "formats_processed": {},
            "errors_encountered": []
        }
    
    def parse_file(self, file_path: str) -> ParsedTestFile:
        """Parse a test file automatically detecting its format"""
        self.logger.info(f"Parsing file: {file_path}")
        
        try:
            # Update statistics
            self.parsing_stats["total_files_parsed"] += 1
            
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Detect file format
            file_format = self._detect_file_format(file_path)
            
            # Read file content
            content = self._read_file_content(file_path)
            
            # Get appropriate parser
            parser = self._get_parser_for_format(file_format)
            
            # Parse the file
            parsed_file = parser.parse_file(file_path, content)
            
            # Update statistics
            self._update_parsing_stats(file_format, True)
            
            # Enhance with unified metadata
            self._enhance_parsed_file(parsed_file, file_format)
            
            self.logger.info(f"Successfully parsed {file_format} file: {file_path}")
            return parsed_file
            
        except Exception as e:
            error_msg = f"Failed to parse file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            
            # Update statistics
            self._update_parsing_stats("unknown", False, error_msg)
            
            # Return error parsed file
            return self._create_error_parsed_file(file_path, error_msg)
    
    def parse_multiple_files(self, file_paths: List[str]) -> List[ParsedTestFile]:
        """Parse multiple test files"""
        self.logger.info(f"Parsing {len(file_paths)} files")
        
        parsed_files = []
        
        for file_path in file_paths:
            try:
                parsed_file = self.parse_file(file_path)
                parsed_files.append(parsed_file)
            except Exception as e:
                self.logger.error(f"Error parsing file {file_path}: {e}")
                # Continue with other files
                continue
        
        self.logger.info(f"Successfully parsed {len(parsed_files)} out of {len(file_paths)} files")
        return parsed_files
    
    def parse_directory(self, directory_path: str, recursive: bool = True) -> List[ParsedTestFile]:
        """Parse all test files in a directory"""
        self.logger.info(f"Parsing directory: {directory_path} (recursive: {recursive})")
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find all test files
        test_files = self._find_test_files(directory_path, recursive)
        
        if not test_files:
            self.logger.warning(f"No test files found in directory: {directory_path}")
            return []
        
        # Parse all found files
        return self.parse_multiple_files(test_files)
    
    def _detect_file_format(self, file_path: str) -> str:
        """Detect file format based on extension and content"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension in self.format_parsers:
            return file_extension
        
        # Try to detect format from content if extension is unknown
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content_sample = f.read(100).strip()
            
            # Check if it looks like JSON
            if content_sample.startswith('{') and '"' in content_sample:
                return ".json"
            
            # Default to text format
            return ".txt"
            
        except Exception as e:
            self.logger.warning(f"Could not detect format for {file_path}: {e}")
            return ".txt"  # Default fallback
    
    def _read_file_content(self, file_path: str) -> str:
        """Read file content with proper encoding handling"""
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                self.logger.debug(f"Successfully read file {file_path} with encoding {encoding}")
                return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.error(f"Error reading file {file_path} with encoding {encoding}: {e}")
                continue
        
        raise ValueError(f"Could not read file {file_path} with any supported encoding")
    
    def _get_parser_for_format(self, file_format: str) -> Union[TxtTestFileParser, JsonTestFileParser]:
        """Get the appropriate parser for the file format"""
        parser = self.format_parsers.get(file_format)
        
        if not parser:
            self.logger.warning(f"No parser found for format {file_format}, using TXT parser as fallback")
            return self.txt_parser
        
        return parser
    
    def _enhance_parsed_file(self, parsed_file: ParsedTestFile, detected_format: str):
        """Enhance parsed file with unified metadata"""
        if not hasattr(parsed_file, 'metadata') or parsed_file.metadata is None:
            parsed_file.metadata = {}
        
        # Add unified parser metadata
        parsed_file.metadata.update({
            "parsed_by": "UnifiedTestFileParser",
            "detected_format": detected_format,
            "parser_version": "1.0.0",
            "file_size_bytes": self._get_file_size(parsed_file.file_path),
            "parsing_timestamp": parsed_file.parsed_at.isoformat()
        })
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
    
    def _update_parsing_stats(self, file_format: str, success: bool, error_msg: str = None):
        """Update parsing statistics"""
        if success:
            self.parsing_stats["successful_parses"] += 1
        else:
            self.parsing_stats["failed_parses"] += 1
            if error_msg:
                self.parsing_stats["errors_encountered"].append(error_msg)
        
        # Update format statistics
        if file_format not in self.parsing_stats["formats_processed"]:
            self.parsing_stats["formats_processed"][file_format] = {"success": 0, "failed": 0}
        
        if success:
            self.parsing_stats["formats_processed"][file_format]["success"] += 1
        else:
            self.parsing_stats["formats_processed"][file_format]["failed"] += 1
    
    def _create_error_parsed_file(self, file_path: str, error_msg: str) -> ParsedTestFile:
        """Create a ParsedTestFile object for error cases"""
        from datetime import datetime
        
        return ParsedTestFile(
            file_path=file_path,
            file_format="error",
            test_name="Parse Error",
            description=f"Failed to parse file: {error_msg}",
            priority="High",
            tags=["parse_error", "unified_parser"],
            application_url="",
            test_steps=[],
            expected_results=[],
            test_data={},
            environment={},
            metadata={
                "parse_failed": True,
                "error_message": error_msg,
                "parsed_by": "UnifiedTestFileParser"
            },
            parsing_errors=[error_msg],
            parsed_at=datetime.now()
        )
    
    def _find_test_files(self, directory_path: str, recursive: bool) -> List[str]:
        """Find all test files in a directory"""
        test_files = []
        supported_extensions = set()
        
        # Collect all supported extensions
        for parser in [self.txt_parser, self.json_parser]:
            supported_extensions.update(parser.get_supported_formats())
        
        if recursive:
            # Recursively search for test files
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if any(file.lower().endswith(ext) for ext in supported_extensions):
                        test_files.append(file_path)
        else:
            # Search only in the specified directory
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in supported_extensions):
                    test_files.append(file_path)
        
        return sorted(test_files)
    
    def validate_parsed_files(self, parsed_files: List[ParsedTestFile]) -> Dict[str, Any]:
        """Validate multiple parsed files and return comprehensive results"""
        validation_results = {
            "total_files": len(parsed_files),
            "valid_files": 0,
            "invalid_files": 0,
            "files_with_warnings": 0,
            "files_with_suggestions": 0,
            "overall_status": "unknown",
            "detailed_results": [],
            "summary": {
                "common_errors": {},
                "common_warnings": {},
                "format_distribution": {},
                "complexity_distribution": {"low": 0, "medium": 0, "high": 0}
            }
        }
        
        for parsed_file in parsed_files:
            # Get format-specific validator
            if parsed_file.file_format == "txt":
                file_validation = self.txt_parser.validate_parsed_file(parsed_file)
            elif parsed_file.file_format == "json":
                file_validation = self.json_parser.validate_parsed_file(parsed_file)
            else:
                file_validation = {"is_valid": False, "errors": ["Unknown format"], "warnings": [], "suggestions": []}
            
            # Update counters
            if file_validation["is_valid"]:
                validation_results["valid_files"] += 1
            else:
                validation_results["invalid_files"] += 1
            
            if file_validation.get("warnings"):
                validation_results["files_with_warnings"] += 1
            
            if file_validation.get("suggestions"):
                validation_results["files_with_suggestions"] += 1
            
            # Track format distribution
            format_key = parsed_file.file_format
            validation_results["summary"]["format_distribution"][format_key] = \
                validation_results["summary"]["format_distribution"].get(format_key, 0) + 1
            
            # Track complexity distribution
            complexity = parsed_file.metadata.get("complexity_analysis", {}).get("estimated_complexity", "unknown")
            if complexity in validation_results["summary"]["complexity_distribution"]:
                validation_results["summary"]["complexity_distribution"][complexity] += 1
            
            # Collect common errors and warnings
            for error in file_validation.get("errors", []):
                validation_results["summary"]["common_errors"][error] = \
                    validation_results["summary"]["common_errors"].get(error, 0) + 1
            
            for warning in file_validation.get("warnings", []):
                validation_results["summary"]["common_warnings"][warning] = \
                    validation_results["summary"]["common_warnings"].get(warning, 0) + 1
            
            # Add detailed result
            validation_results["detailed_results"].append({
                "file_path": parsed_file.file_path,
                "file_format": parsed_file.file_format,
                "test_name": parsed_file.test_name,
                "is_valid": file_validation["is_valid"],
                "errors": file_validation.get("errors", []),
                "warnings": file_validation.get("warnings", []),
                "suggestions": file_validation.get("suggestions", [])
            })
        
        # Determine overall status
        if validation_results["invalid_files"] == 0:
            validation_results["overall_status"] = "all_valid"
        elif validation_results["valid_files"] == 0:
            validation_results["overall_status"] = "all_invalid"
        else:
            validation_results["overall_status"] = "mixed"
        
        return validation_results
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive parsing statistics"""
        stats = self.parsing_stats.copy()
        
        # Calculate success rate
        total_parsed = stats["successful_parses"] + stats["failed_parses"]
        if total_parsed > 0:
            stats["success_rate"] = round(stats["successful_parses"] / total_parsed * 100, 2)
        else:
            stats["success_rate"] = 0.0
        
        return stats
    
    def reset_statistics(self):
        """Reset parsing statistics"""
        self.parsing_stats = {
            "total_files_parsed": 0,
            "successful_parses": 0,
            "failed_parses": 0,
            "formats_processed": {},
            "errors_encountered": []
        }
        self.logger.info("Parsing statistics reset")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of all supported file formats"""
        supported_formats = set()
        for parser in [self.txt_parser, self.json_parser]:
            supported_formats.update(parser.get_supported_formats())
        return sorted(list(supported_formats))
    
    def generate_sample_files(self, output_directory: str) -> Dict[str, str]:
        """Generate sample test files in different formats"""
        os.makedirs(output_directory, exist_ok=True)
        
        generated_files = {}
        
        # Generate TXT sample
        txt_content = '''Test Name: Sample Login Test
Target: https://www.advantageonlineshopping.com/#/
Priority: High
Tags: authentication, login, security

Description:
Test the user login functionality with valid credentials to ensure proper authentication flow

Test Steps:
1. Navigate to the Advantage Online Shopping website
2. Click on the user account icon to access login
3. Enter username "helios" and password "Password123"
4. Click the login button
5. Verify successful login and user dashboard display

Expected Results:
- User successfully logs in
- Dashboard displays user information
- Navigation shows logged-in state
- No error messages are displayed

Test Data:
username: helios
password: Password123

Environment:
browser: chrome
headless: false
timeout: 30000
'''
        
        txt_file_path = os.path.join(output_directory, "sample_login_test.txt")
        with open(txt_file_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        generated_files["txt"] = txt_file_path
        
        # Generate JSON sample
        json_sample = self.json_parser.generate_json_template("Sample Login Test")
        json_sample.update({
            "testName": "Sample Login Test",
            "description": "Test the user login functionality with valid credentials",
            "application": "https://www.advantageonlineshopping.com/#/",
            "testSteps": [
                {
                    "step": 1,
                    "action": "Navigate to the Advantage Online Shopping website",
                    "expectedResult": "Website loads successfully",
                    "timeout": 30000
                },
                {
                    "step": 2,
                    "action": "Click on the user account icon",
                    "expectedResult": "Login form is displayed",
                    "selector": "[data-testid='user-icon']"
                },
                {
                    "step": 3,
                    "action": "Enter username and password",
                    "expectedResult": "Credentials are entered correctly",
                    "data": {
                        "username": "helios",
                        "password": "Password123"
                    }
                }
            ],
            "testData": {
                "credentials": {
                    "username": "helios",
                    "password": "Password123"
                }
            }
        })
        
        json_file_path = os.path.join(output_directory, "sample_login_test.json")
        import json
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_sample, f, indent=2)
        generated_files["json"] = json_file_path
        
        self.logger.info(f"Generated sample files in {output_directory}")
        return generated_files
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the unified parser"""
        return {
            "name": "Unified Test File Parser",
            "version": "1.0.0",
            "description": "Unified parser supporting multiple test file formats with automatic detection",
            "supported_formats": self.get_supported_formats(),
            "features": [
                "Automatic format detection",
                "Multiple file parsing",
                "Directory parsing (recursive)",
                "Comprehensive validation",
                "Statistics tracking",
                "Error handling and recovery",
                "Sample file generation"
            ],
            "sub_parsers": {
                "txt": self.txt_parser.get_parser_info(),
                "json": self.json_parser.get_parser_info()
            },
            "statistics": self.get_parsing_statistics()
        }

