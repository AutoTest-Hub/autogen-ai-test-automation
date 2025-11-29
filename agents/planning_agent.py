"""
Planning Agent for AutoGen Test Automation Framework
Responsible for analyzing requirements and creating comprehensive test strategies
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseTestAgent
from config.settings import AgentRole
from models.local_ai_provider import ModelType


class PlanningAgent(BaseTestAgent):
    """Agent responsible for test planning and strategy creation"""
    
    def __init__(self, **kwargs):
        system_message = """
You are the Planning Agent, an expert in test strategy and planning. Your responsibilities include:

1. **Requirement Analysis**: Analyze test requirements from .txt and .json files
2. **Test Strategy Creation**: Develop comprehensive test plans and strategies
3. **Risk Assessment**: Identify potential risks and mitigation strategies
4. **Test Prioritization**: Prioritize test cases based on business impact and risk
5. **Resource Planning**: Estimate effort, time, and resources needed
6. **Quality Gates Definition**: Define success criteria and quality gates

**Key Capabilities**:
- Parse and understand test requirements in natural language
- Create detailed test plans with scenarios, data, and dependencies
- Assess complexity and risk levels for different test scenarios
- Recommend optimal testing approaches and frameworks
- Define comprehensive acceptance criteria

**Output Format**: Always provide structured JSON responses with clear sections for:
- Test objectives and scope
- Test scenarios and cases
- Risk assessment and mitigation
- Resource requirements and timeline
- Success criteria and quality gates

Be thorough, analytical, and strategic in your planning approach.
"""
        
        super().__init__(
            role=AgentRole.PLANNING,
            system_message=system_message,
            **kwargs
        )
        
        # Register planning-specific functions
        self._register_planning_functions()
    
    def _register_planning_functions(self):
        """Register planning-specific functions"""
        
        def analyze_requirements(requirements_text: str) -> Dict[str, Any]:
            """Analyze test requirements and extract key information"""
            # This would be implemented with more sophisticated NLP
            return {
                "requirements_analyzed": True,
                "complexity_score": 0.7,
                "estimated_effort_hours": 8,
                "risk_level": "medium"
            }
        
        def create_test_matrix(scenarios: List[str]) -> Dict[str, Any]:
            """Create a test coverage matrix"""
            return {
                "matrix_created": True,
                "total_scenarios": len(scenarios),
                "coverage_percentage": 85
            }
        
        def assess_risk(test_plan: Dict[str, Any]) -> Dict[str, Any]:
            """Assess risks in the test plan"""
            return {
                "risk_assessment_complete": True,
                "high_risk_areas": ["authentication", "payment_processing"],
                "mitigation_strategies": ["additional_validation", "error_handling"]
            }
        
        # Register functions with the agent
        self.register_function(analyze_requirements, "Analyze test requirements and extract key information")
        self.register_function(create_test_matrix, "Create a comprehensive test coverage matrix")
        self.register_function(assess_risk, "Assess risks and create mitigation strategies")
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process planning tasks"""
        try:
            self.update_state("processing", current_task="planning")
            
            task_type = task_data.get("type", "create_plan")
            
            if task_type == "create_plan":
                result = await self._create_test_plan(task_data)
            elif task_type == "analyze_requirements":
                result = await self._analyze_requirements(task_data)
            elif task_type == "assess_risk":
                result = await self._assess_risk(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.state["tasks_completed"] += 1
            self.update_state("completed")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing planning task: {e}")
            self.state["errors"] += 1
            self.update_state("error", error_message=str(e))
            raise
    
    async def _create_test_plan(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive test plan using LLM analysis"""
        requirements = task_data.get("requirements", {})
        discovery_results = task_data.get("discovery_results", {})
        url = task_data.get("url", "")
        name = task_data.get("name", "")
        
        self.logger.info(f"Creating test plan for {name} at {url}")
        
        # Prepare context for the LLM
        discovery_summary = "No elements discovered yet."
        if discovery_results and "elements" in discovery_results:
            elements = discovery_results["elements"]
            total_elements = discovery_results.get("total_elements", 0)
            discovery_summary = f"Discovered {total_elements} elements.\n"
            
            # Summarize inputs
            if "inputs" in elements:
                inputs = [f"{el.get('type')} (id={el.get('id')}, name={el.get('name')})" for el in elements["inputs"][:10]]
                discovery_summary += f"Inputs: {', '.join(inputs)}\n"
            
            # Summarize buttons
            if "buttons" in elements:
                buttons = [f"{el.get('text')} (id={el.get('id')})" for el in elements["buttons"][:10]]
                discovery_summary += f"Buttons: {', '.join(buttons)}\n"
                
            # Summarize links
            if "links" in elements:
                links = [f"{el.get('text')} (href={el.get('href')})" for el in elements["links"][:10]]
                discovery_summary += f"Links: {', '.join(links)}\n"

        prompt = f"""
        Create a comprehensive test plan for the application "{name}" at {url}.
        
        Requirements:
        {requirements}
        
        Discovered Application Structure:
        {discovery_summary}
        
        Based on the discovered elements and requirements, generate a JSON test plan with the following structure:
        {{
            "test_scenarios": [
                {{
                    "name": "Scenario Name",
                    "description": "Description",
                    "priority": "High/Medium/Low",
                    "test_steps": [
                        {{
                            "step": 1,
                            "action": "Action description (referencing specific discovered elements if possible)",
                            "expectedResult": "Expected result"
                        }}
                    ],
                    "risk_factors": ["Risk 1", "Risk 2"],
                    "estimated_duration_minutes": 5,
                    "required_framework": "playwright"
                }}
            ],
            "risk_assessment": {{
                "overall_risk": "High/Medium/Low",
                "high_risk_scenarios": 0,
                "mitigation_strategies": ["Strategy 1"]
            }},
            "execution_strategy": {{
                "framework": "playwright",
                "execution_mode": "sequential/parallel"
            }}
        }}
        
        Return ONLY valid JSON.
        """
        
        try:
            # Call the Local AI Provider
            response = await self.local_ai_provider.generate_response_async(
                prompt=prompt,
                model_type=ModelType.PLANNING,
                system_prompt="You are an expert QA Test Planner. Analyze the application structure and requirements to create a detailed, executable test plan."
            )
            
            if response.get("success"):
                llm_output = response.get("response", "")
                # Clean up potential markdown code blocks
                if "```json" in llm_output:
                    llm_output = llm_output.split("```json")[1].split("```")[0].strip()
                elif "```" in llm_output:
                    llm_output = llm_output.split("```")[1].split("```")[0].strip()
                
                try:
                    test_plan = json.loads(llm_output)
                    
                    # Add metadata
                    test_plan["plan_id"] = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    test_plan["created_at"] = datetime.now().isoformat()
                    test_plan["url"] = url
                    test_plan["name"] = name
                    
                    # Save the test plan
                    plan_file = self.save_work_artifact(
                        f"test_plan_{test_plan['plan_id']}.json",
                        test_plan,
                        "json"
                    )
                    
                    return {
                        "status": "success",
                        "test_plan": test_plan,
                        "plan_file": plan_file,
                        "source": "llm"
                    }
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse LLM response as JSON: {e}")
                    self.logger.debug(f"Raw response: {llm_output}")
                    # Fallback to default/mock plan if JSON parsing fails
            
            # Fallback if LLM fails
            self.logger.warning("LLM generation failed or returned invalid JSON, falling back to heuristic planning")
            return await self._create_heuristic_test_plan(task_data)
            
        except Exception as e:
            self.logger.error(f"Error in AI planning: {e}")
            return await self._create_heuristic_test_plan(task_data)

    async def _create_heuristic_test_plan(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback method using the original heuristic logic"""
        requirements = task_data.get("requirements", {})
        test_files = task_data.get("test_files", [])
        
        # Analyze each test file
        test_scenarios = []
        for test_file in test_files:
            scenario = await self._analyze_test_file(test_file)
            test_scenarios.append(scenario)
            
        # If no test files, create a default login scenario based on discovery
        if not test_scenarios:
             test_scenarios.append({
                "name": "Login Test",
                "description": "Verify login functionality",
                "priority": "High",
                "test_steps": [
                    {"step": 1, "action": "Navigate to login page", "expectedResult": "Login page loaded"},
                    {"step": 2, "action": "Enter credentials", "expectedResult": "Credentials entered"},
                    {"step": 3, "action": "Click login", "expectedResult": "Dashboard loaded"}
                ],
                "required_framework": "playwright"
             })
        
        # Create comprehensive test plan
        test_plan = {
            "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "requirements_summary": requirements,
            "test_scenarios": test_scenarios,
            "risk_assessment": self._assess_overall_risk(test_scenarios),
            "resource_estimation": self._estimate_resources(test_scenarios),
            "execution_strategy": self._recommend_execution_strategy(test_scenarios),
            "quality_gates": self._define_quality_gates(test_scenarios),
            "timeline": self._create_timeline(test_scenarios),
        }
        
        # Save the test plan
        plan_file = self.save_work_artifact(
            f"test_plan_{test_plan['plan_id']}.json",
            test_plan,
            "json"
        )
        
        return {
            "status": "success",
            "test_plan": test_plan,
            "plan_file": plan_file,
            "summary": {
                "total_scenarios": len(test_scenarios),
                "estimated_hours": test_plan["resource_estimation"]["total_hours"],
                "risk_level": test_plan["risk_assessment"]["overall_risk"],
                "recommended_framework": test_plan["execution_strategy"]["framework"]
            }
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
        lines = content.strip().split('\n')
        
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
                "All critical tests pass",
                "No high-severity defects",
                "Performance within acceptable limits"
            ],
            "failure_criteria": [
                "Critical test failures",
                "Security vulnerabilities detected",
                "Performance degradation > 20%"
            ]
        }
    
    def _create_timeline(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create execution timeline"""
        total_duration = sum(s.get("estimated_duration_minutes", 0) for s in scenarios)
        
        return {
            "phases": {
                "setup": {"duration_minutes": 30, "description": "Environment and framework setup"},
                "execution": {"duration_minutes": total_duration, "description": "Test execution"},
                "analysis": {"duration_minutes": 60, "description": "Results analysis and reporting"},
                "cleanup": {"duration_minutes": 15, "description": "Environment cleanup"}
            },
            "total_duration_minutes": total_duration + 105,  # Including overhead
            "estimated_completion": "Based on parallel execution capabilities"
        }
    
    async def _analyze_requirements(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements in detail using LLM intelligence"""
        requirements = task_data.get("requirements", "")
        discovery_data = task_data.get("discovery_data", {})

        # Use LLM for intelligent analysis
        result = await self._analyze_requirements_with_llm(requirements, discovery_data)

        return {
            "status": "completed",
            "analysis": result
        }

    async def _assess_risk(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks for specific scenarios using LLM intelligence"""
        test_plan = task_data.get("test_plan", {})
        scenarios = task_data.get("scenarios", [])

        # Use LLM for intelligent risk assessment
        result = await self._assess_risk_with_llm(test_plan, scenarios)

        return {
            "status": "completed",
            "risks": result
        }

    # =========================================================================
    # LLM-POWERED INTELLIGENT METHODS
    # =========================================================================

    async def _analyze_requirements_with_llm(
        self,
        requirements: str,
        discovery_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to intelligently analyze requirements and discovery data.

        This method leverages the LLM to:
        - Understand the semantic meaning of requirements
        - Map requirements to discovered application elements
        - Identify test scenarios that should be covered
        - Provide intelligent complexity and risk assessment
        """
        # Build context from discovery data
        pages_info = discovery_data.get("pages", [])
        elements_info = discovery_data.get("elements", {})
        workflows_info = discovery_data.get("workflows", [])

        prompt = f"""
Analyze the following test requirements and application discovery data to create a comprehensive test analysis.

## Requirements:
{requirements if requirements else "No specific requirements provided. Analyze based on discovered application structure."}

## Discovered Application Structure:
### Pages Found: {len(pages_info)}
{json.dumps(pages_info[:5], indent=2) if pages_info else "No pages discovered yet"}

### Interactive Elements:
{json.dumps(dict(list(elements_info.items())[:3]), indent=2) if isinstance(elements_info, dict) else "No elements discovered yet"}

### Identified Workflows:
{json.dumps(workflows_info[:3], indent=2) if workflows_info else "No workflows identified yet"}

## Analysis Required:
Provide a detailed analysis in JSON format with the following structure:
{{
    "requirement_summary": "Brief summary of the testing requirements",
    "test_scenarios": [
        {{
            "name": "Scenario name",
            "description": "What this scenario tests",
            "priority": "High/Medium/Low",
            "type": "functional/integration/e2e/security/performance",
            "steps": ["Step 1", "Step 2", ...],
            "expected_results": ["Result 1", "Result 2", ...]
        }}
    ],
    "coverage_analysis": {{
        "covered_areas": ["List of areas that will be tested"],
        "gaps": ["List of potential testing gaps"],
        "recommendations": ["Recommendations for additional coverage"]
    }},
    "complexity_assessment": {{
        "overall_complexity": "Low/Medium/High",
        "complexity_score": 1-10,
        "reasoning": "Why this complexity level"
    }},
    "risk_factors": [
        {{
            "risk": "Description of risk",
            "likelihood": "Low/Medium/High",
            "impact": "Low/Medium/High",
            "mitigation": "How to mitigate"
        }}
    ],
    "recommended_approach": {{
        "framework": "playwright/selenium/api",
        "execution_strategy": "sequential/parallel",
        "estimated_effort_hours": number,
        "reasoning": "Why this approach"
    }}
}}

Be thorough and specific. Base your analysis on the actual discovered application structure when available.
"""

        try:
            response = await self.generate_llm_response(
                prompt=prompt,
                response_format="json",
                temperature=0.3  # Lower temperature for more deterministic analysis
            )

            if response.get("success") and response.get("json_parse_success"):
                return response.get("parsed_json", {})
            elif response.get("success"):
                # If JSON parsing failed, return the raw response with a note
                return {
                    "raw_analysis": response.get("response", ""),
                    "parse_error": "Could not parse as JSON",
                    "requirement_summary": "Analysis completed but structured parsing failed"
                }
            else:
                self.logger.warning(f"LLM analysis failed: {response.get('error')}")
                # Fall back to basic analysis
                return self._fallback_requirement_analysis(requirements, discovery_data)

        except Exception as e:
            self.logger.error(f"Error in LLM requirement analysis: {e}")
            return self._fallback_requirement_analysis(requirements, discovery_data)

    def _fallback_requirement_analysis(
        self,
        requirements: str,
        discovery_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback analysis when LLM is unavailable"""
        return {
            "requirement_summary": "Basic analysis (LLM unavailable)",
            "test_scenarios": [],
            "coverage_analysis": {
                "covered_areas": [],
                "gaps": ["Full analysis requires LLM"],
                "recommendations": ["Enable LLM for intelligent analysis"]
            },
            "complexity_assessment": {
                "overall_complexity": "Unknown",
                "complexity_score": 5,
                "reasoning": "Unable to perform intelligent analysis"
            },
            "risk_factors": [],
            "recommended_approach": {
                "framework": "playwright",
                "execution_strategy": "sequential",
                "estimated_effort_hours": 8,
                "reasoning": "Default recommendation"
            }
        }

    async def _assess_risk_with_llm(
        self,
        test_plan: Dict[str, Any],
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use LLM to intelligently assess risks in the test plan.
        """
        prompt = f"""
Analyze the following test plan and scenarios to provide a comprehensive risk assessment.

## Test Plan Summary:
{json.dumps(test_plan, indent=2, default=str)[:2000]}

## Test Scenarios:
{json.dumps(scenarios[:10], indent=2, default=str) if scenarios else "No scenarios provided"}

## Risk Assessment Required:
Provide a detailed risk assessment in JSON format:
{{
    "overall_risk_level": "Low/Medium/High/Critical",
    "risk_score": 1-10,
    "key_risks": [
        {{
            "risk_id": "RISK-001",
            "category": "security/performance/functional/data/integration",
            "description": "Detailed description of the risk",
            "likelihood": "Low/Medium/High",
            "impact": "Low/Medium/High/Critical",
            "affected_scenarios": ["Scenario names affected"],
            "mitigation_strategy": "How to mitigate this risk",
            "contingency_plan": "What to do if risk materializes"
        }}
    ],
    "risk_matrix": {{
        "high_priority": ["Risks requiring immediate attention"],
        "medium_priority": ["Risks to monitor closely"],
        "low_priority": ["Risks with minimal impact"]
    }},
    "recommendations": [
        "Specific recommendations to reduce overall risk"
    ],
    "confidence_level": "How confident is this assessment (Low/Medium/High)"
}}

Consider common testing risks including:
- Security vulnerabilities
- Performance bottlenecks
- Data integrity issues
- Integration failures
- Environment dependencies
- Test data quality
"""

        try:
            response = await self.generate_llm_response(
                prompt=prompt,
                response_format="json",
                temperature=0.3
            )

            if response.get("success") and response.get("json_parse_success"):
                return response.get("parsed_json", {})
            elif response.get("success"):
                return {
                    "raw_assessment": response.get("response", ""),
                    "overall_risk_level": "Unknown",
                    "risk_score": 5
                }
            else:
                return self._fallback_risk_assessment(test_plan, scenarios)

        except Exception as e:
            self.logger.error(f"Error in LLM risk assessment: {e}")
            return self._fallback_risk_assessment(test_plan, scenarios)

    def _fallback_risk_assessment(
        self,
        test_plan: Dict[str, Any],
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback risk assessment when LLM is unavailable"""
        return {
            "overall_risk_level": "Medium",
            "risk_score": 5,
            "key_risks": [
                {
                    "risk_id": "RISK-001",
                    "category": "general",
                    "description": "Unable to perform intelligent risk assessment",
                    "likelihood": "Medium",
                    "impact": "Medium",
                    "mitigation_strategy": "Enable LLM for detailed analysis"
                }
            ],
            "recommendations": ["Enable LLM for comprehensive risk assessment"],
            "confidence_level": "Low"
        }

    async def _generate_test_strategy_with_llm(
        self,
        requirements: str,
        discovery_data: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use LLM to generate an intelligent test strategy.
        """
        prompt = f"""
Create a comprehensive test strategy based on the following inputs.

## Requirements:
{requirements if requirements else "General application testing"}

## Application Discovery Data:
Pages: {len(discovery_data.get('pages', []))}
Elements: {len(discovery_data.get('elements', {}))}
Workflows: {len(discovery_data.get('workflows', []))}

## Constraints:
{json.dumps(constraints, indent=2) if constraints else "No specific constraints"}

## Generate Test Strategy:
Provide a detailed test strategy in JSON format:
{{
    "strategy_name": "Name for this strategy",
    "objectives": ["Primary testing objectives"],
    "scope": {{
        "in_scope": ["What will be tested"],
        "out_of_scope": ["What will not be tested"],
        "assumptions": ["Key assumptions"]
    }},
    "test_levels": [
        {{
            "level": "unit/integration/system/e2e",
            "coverage_target": percentage,
            "approach": "Description of approach"
        }}
    ],
    "test_types": [
        {{
            "type": "functional/security/performance/usability",
            "priority": "High/Medium/Low",
            "techniques": ["Testing techniques to use"]
        }}
    ],
    "execution_plan": {{
        "phases": ["Phase descriptions"],
        "parallelization": "How tests can be parallelized",
        "environment_requirements": ["Required environments"]
    }},
    "success_criteria": {{
        "pass_rate": percentage,
        "coverage_threshold": percentage,
        "performance_targets": {{}}
    }},
    "resource_requirements": {{
        "estimated_hours": number,
        "team_skills": ["Required skills"],
        "tools": ["Required tools"]
    }}
}}
"""

        try:
            response = await self.generate_llm_response(
                prompt=prompt,
                response_format="json",
                temperature=0.4
            )

            if response.get("success") and response.get("json_parse_success"):
                return response.get("parsed_json", {})
            else:
                return {
                    "strategy_name": "Default Strategy",
                    "objectives": ["Basic test coverage"],
                    "execution_plan": {"phases": ["Setup", "Execute", "Report"]}
                }

        except Exception as e:
            self.logger.error(f"Error generating test strategy: {e}")
            return {"error": str(e)}

    def get_capabilities(self) -> List[str]:
        """Get planning agent capabilities"""
        return [
            "requirement_analysis",
            "test_strategy_creation",
            "risk_assessment",
            "resource_estimation",
            "timeline_planning",
            "quality_gates_definition",
            "framework_recommendation",
            "complexity_analysis"
        ]

