import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseTestAgent

class PlanningAgent(BaseTestAgent):
    def __init__(self, **kwargs):
        super().__init__(
            role="planning",
            system_message="You are the Planning Agent...",
            **kwargs
        )

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._create_test_plan(task_data)

    async def _create_test_plan(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        requirements_json = task_data.get("requirements_json", {})
        test_files = task_data.get("test_files", [])
        
        # Extract test cases from requirements_json if available
        test_cases = []
        if requirements_json:
            # Check for test_cases directly in requirements_json
            if "test_cases" in requirements_json:
                test_cases = requirements_json["test_cases"]
            # Also check for test_requirements structure
            elif "test_requirements" in requirements_json:
                for req in requirements_json["test_requirements"]:
                    if "test_cases" in req:
                        test_cases.extend(req["test_cases"])
        
        # Log the correct count
        total_items = len(test_files) + len(test_cases)
        self.logger.info(f"Creating test plan for {len(test_files)} test files and {len(test_cases)} test cases from requirements")
        
        # Analyze each test file
        test_scenarios = []
        for test_file in test_files:
            scenario = await self._analyze_test_file(test_file)
            test_scenarios.append(scenario)
            
        # Analyze test cases from requirements_json - convert strings to test case objects
        for test_case in test_cases:
            if isinstance(test_case, str):
                # Convert string test case to proper test case object
                test_case_obj = {
                    "name": test_case.lower().replace(" ", "_"),
                    "description": test_case,
                    "priority": "High",
                    "steps": [test_case],
                    "expected_result": f"Successfully complete: {test_case}"
                }
                scenario = await self._analyze_test_case(test_case_obj)
            else:
                scenario = await self._analyze_test_case(test_case)
            test_scenarios.append(scenario)
        
        # Create comprehensive test plan
        test_plan = {
            "plan_id": f"plan_{datetime.now().strftime("%Y%m%d_%H%M%S")}",
            "test_scenarios": test_scenarios,
            "overall_risk_assessment": self._assess_overall_risk(test_scenarios),
            "resource_estimation": self._estimate_resources(test_scenarios),
            "execution_strategy": self._recommend_execution_strategy(test_scenarios),
            "quality_gates": self._define_quality_gates(test_scenarios)
        }

        return {
            "status": "success",
            "test_plan": test_plan,
        }
    
    async def _analyze_test_file(self, test_file: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single test file and create scenario details"""
        file_path = test_file.get("path", "")
        file_content = test_file.get("content", "")
        file_format = test_file.get("format", "txt")
        
        if file_format == "json":
            return self._analyze_json_test_file(file_content)
        else:
            return self._analyze_txt_test_file(file_content)
    
    async def _analyze_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single test case from requirements_json and create scenario details"""
        return {
            "name": test_case.get("name", "Unknown Test"),
            "description": test_case.get("description", ""),
            "priority": test_case.get("priority", "Medium"),
            "tags": [],
            "application": "Web Application",
            "test_steps": test_case.get("steps", []),
            "test_data": {},
            "environment": {"browser": "Chrome", "headless": True},
            "expected_result": test_case.get("expected_result", ""),
            "complexity": "Medium",
            "estimated_duration": "5 minutes",
            "dependencies": [],
            "risk_level": "Medium"
        }
    
    def _analyze_json_test_file(self, content: str) -> Dict[str, Any]:
        """Analyze JSON format test file"""
        try:
            test_data = json.loads(content)
            
            return {
                "name": test_data.get("testName", "Unknown Test"),
                "description": test_data.get("description", ""),
                "priority": test_data.get("priority", "Medium"),
                "tags": test_data.get("tags", []),
                "application": test_data.get("application", ""),
                "test_steps": test_data.get("testSteps", []),
                "test_data": test_data.get("testData", {}),
                "environment": test_data.get("environment", {}),
                "complexity_score": self._calculate_complexity(test_data),
                "estimated_duration_minutes": self._estimate_duration(test_data),
                "risk_factors": self._identify_risk_factors(test_data),
                "required_framework": self._recommend_framework(test_data),
            }
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON test file: {e}")
            return {"error": f"Invalid JSON format: {e}"}
    
    def _analyze_txt_test_file(self, content: str) -> Dict[str, Any]:
        """Analyze TXT format test file"""
        lines = content.strip().split("\n")
        
        # Parse the text file structure
        test_info = {
            "name": "Unknown Test",
            "description": "",
            "priority": "Medium",
            "tags": [],
            "application": "",
            "test_steps": [],
            "expected_results": [],
        }
        
        current_section = None
        step_counter = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if line.startswith("Test Name:") or line.startswith("Scenario:"):
                test_info["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("Target:") or line.startswith("Application:"):
                test_info["application"] = line.split(":", 1)[1].strip()
            elif line.startswith("Priority:"):
                test_info["priority"] = line.split(":", 1)[1].strip()
            elif line.startswith("Tags:"):
                tags_str = line.split(":", 1)[1].strip()
                test_info["tags"] = [tag.strip() for tag in tags_str.split(",")]
            elif line.startswith("Description:") or line.startswith("Objective:"):
                current_section = "description"
            elif line.startswith("Test Steps:"):
                current_section = "steps"
            elif line.startswith("Expected Results:"):
                current_section = "results"
            elif current_section == "description":
                test_info["description"] += line + " "
            elif current_section == "steps":
                if line[0].isdigit():
                    step_counter += 1
                    test_info["test_steps"].append({
                        "step": step_counter,
                        "action": line,
                        "expectedResult": ""
                    })
            elif current_section == "results":
                if line.startswith("-") or line.startswith("•"):
                    test_info["expected_results"].append(line[1:].strip())
        
        # Calculate additional metrics
        return {
            **test_info,
            "complexity_score": self._calculate_complexity_from_text(test_info),
            "estimated_duration_minutes": self._estimate_duration_from_text(test_info),
            "risk_factors": self._identify_risk_factors_from_text(test_info),
            "required_framework": self._recommend_framework_from_text(test_info),
        }
    
    def _calculate_complexity(self, test_data: Dict[str, Any]) -> float:
        """Calculate complexity score for a test"""
        score = 0.0
        
        # Base complexity from number of steps
        steps = test_data.get("testSteps", [])
        score += len(steps) * 0.1
        
        # Additional complexity factors
        if test_data.get("testData", {}):
            score += 0.2  # Data-driven tests are more complex
        
        if "authentication" in str(test_data).lower():
            score += 0.3  # Authentication adds complexity
        
        if "payment" in str(test_data).lower():
            score += 0.4  # Payment processing is complex
        
        # Normalize to 0-1 scale
        return min(score, 1.0)
    
    def _calculate_complexity_from_text(self, test_info: Dict[str, Any]) -> float:
        """Calculate complexity score from text-based test info"""
        score = 0.0
        
        # Base complexity from number of steps
        score += len(test_info.get("test_steps", [])) * 0.1
        
        # Text-based complexity analysis
        text_content = (test_info.get("description", "") + " " + 
                       " ".join([step.get("action", "") for step in test_info.get("test_steps", [])])).lower()
        
        complexity_keywords = {
            "login": 0.2, "authentication": 0.3, "payment": 0.4,
            "database": 0.3, "api": 0.2, "integration": 0.3,
            "upload": 0.2, "download": 0.2, "email": 0.2
        }
        
        for keyword, weight in complexity_keywords.items():
            if keyword in text_content:
                score += weight
        
        return min(score, 1.0)
    
    def _estimate_duration(self, test_data: Dict[str, Any]) -> int:
        """Estimate test duration in minutes"""
        base_duration = 5  # Base 5 minutes per test
        steps = test_data.get("testSteps", [])
        
        # Add time per step
        duration = base_duration + len(steps) * 2
        
        # Add time for complex operations
        text_content = str(test_data).lower()
        if "payment" in text_content:
            duration += 10
        if "upload" in text_content:
            duration += 5
        if "email" in text_content:
            duration += 5
        
        return duration
    
    def _estimate_duration_from_text(self, test_info: Dict[str, Any]) -> int:
        """Estimate duration from text-based test info"""
        base_duration = 5
        steps = len(test_info.get("test_steps", []))
        
        duration = base_duration + steps * 2
        
        # Analyze text for time-consuming operations
        text_content = (test_info.get("description", "") + " " + 
                       " ".join([step.get("action", "") for step in test_info.get("test_steps", [])])).lower()
        
        time_factors = {
            "payment": 10, "checkout": 8, "upload": 5, "download": 5,
            "email": 5, "verification": 3, "validation": 3
        }
        
        for factor, time_add in time_factors.items():
            if factor in text_content:
                duration += time_add
        
        return duration
    
    def _identify_risk_factors(self, test_data: Dict[str, Any]) -> List[str]:
        """Identify risk factors in the test"""
        risks = []
        text_content = str(test_data).lower()
        
        risk_keywords = {
            "payment": "Payment processing failure risk",
            "authentication": "Authentication security risk",
            "database": "Data consistency risk",
            "api": "API integration risk",
            "upload": "File upload security risk",
            "external": "External dependency risk"
        }
        
        for keyword, risk_desc in risk_keywords.items():
            if keyword in text_content:
                risks.append(risk_desc)
        
        return risks
    
    def _identify_risk_factors_from_text(self, test_info: Dict[str, Any]) -> List[str]:
        """Identify risk factors from text-based test info"""
        return self._identify_risk_factors(test_info)  # Same logic applies
    
    def _recommend_framework(self, test_data: Dict[str, Any]) -> str:
        """Recommend the best testing framework for this test"""
        text_content = str(test_data).lower()
        
        if "api" in text_content or "rest" in text_content:
            return "requests"
        elif "browser" in text_content or "ui" in text_content or "click" in text_content:
            return "playwright"
        else:
            return "playwright"  # Default to playwright for web testing
    
    def _recommend_framework_from_text(self, test_info: Dict[str, Any]) -> str:
        """Recommend framework from text-based test info"""
        return self._recommend_framework(test_info)  # Same logic applies
    
    def _assess_overall_risk(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall risk across all scenarios"""
        all_risks = []
        high_risk_count = 0
        
        for scenario in scenarios:
            risks = scenario.get("risk_factors", [])
            all_risks.extend(risks)
            
            if scenario.get("complexity_score", 0) > 0.7:
                high_risk_count += 1
        
        overall_risk = "low"
        if high_risk_count > len(scenarios) * 0.5:
            overall_risk = "high"
        elif high_risk_count > len(scenarios) * 0.25:
            overall_risk = "medium"
        
        return {
            "overall_risk": overall_risk,
            "high_risk_scenarios": high_risk_count,
            "common_risks": list(set(all_risks)),
            "mitigation_required": high_risk_count > 0
        }
    
    def _estimate_resources(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate resources needed for all scenarios"""
        total_duration = sum(s.get("estimated_duration_minutes", 0) for s in scenarios)
        total_hours = total_duration / 60
        
        # Add overhead for setup, review, and debugging
        overhead_factor = 1.5
        total_hours_with_overhead = total_hours * overhead_factor
        
        return {
            "total_scenarios": len(scenarios),
            "total_duration_minutes": total_duration,
            "total_hours": round(total_hours_with_overhead, 1),
            "estimated_team_size": max(1, len(scenarios) // 10),
            "parallel_execution_possible": len(scenarios) > 1,
            "resource_requirements": {
                "test_automation_engineer": 1,
                "qa_analyst": 1 if len(scenarios) > 5 else 0,
                "test_environment": 1
            }
        }
    
    def _recommend_execution_strategy(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Recommend execution strategy"""
        frameworks = [s.get("required_framework", "playwright") for s in scenarios]
        
        # Handle empty frameworks list
        if not frameworks:
            primary_framework = "playwright"  # Default framework
        else:
            primary_framework = max(set(frameworks), key=frameworks.count)
        
        return {
            "framework": primary_framework,
            "execution_mode": "parallel" if len(scenarios) > 3 else "sequential",
            "environment_requirements": ["test_environment", "test_data"],
            "prerequisites": ["framework_setup", "test_data_preparation"],
            "recommended_schedule": "continuous_integration"
        }
    
    def _define_quality_gates(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Define quality gates for the test execution"""
        return {
            "minimum_pass_rate": 95,
            "maximum_execution_time_minutes": sum(s.get("estimated_duration_minutes", 0) for s in scenarios) * 1.2,
            "required_coverage": {
                "functional": 100,
                "integration": 80,
                "ui": 90
            },
            "success_criteria": [
                "All critical tests must pass",
                "No new high-priority bugs introduced"
            ]
        }

