"""
Integrated Test Generator
=========================

This agent integrates all three-tier system capabilities to provide a unified
test generation experience. It combines enhanced discovery, intelligent flow
handling, step generation, and AutoGen collaboration into a single powerful agent.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import os

from .base_agent import BaseTestAgent
from .enhanced_discovery_agent import create_enhanced_discovery_agent
from .autogen_test_creation_agent import create_autogen_test_creation_agent
from config.settings import AgentRole
from utils.step_generator import create_step_generator
from utils.intelligent_flow_handler import create_intelligent_flow_handler


class IntegratedTestGenerator(BaseTestAgent):
    """
    Unified test generator that orchestrates all three-tier system capabilities
    """
    
    def __init__(self, **kwargs):
        system_message = """
You are the Integrated Test Generator, the master orchestrator of the three-tier test automation system. Your responsibilities include:

1. **System Orchestration**: Coordinate all components of the three-tier system
2. **Intelligent Workflow Management**: Manage complex test generation workflows
3. **Quality Assurance**: Ensure all generated artifacts meet quality standards
4. **Performance Optimization**: Optimize test generation and execution performance
5. **Adaptive Strategy**: Adapt testing strategies based on application characteristics
6. **Comprehensive Coverage**: Ensure comprehensive test coverage across all tiers
7. **Integration Management**: Manage integration between different system components
8. **Result Synthesis**: Synthesize results from multiple agents and components

**Three-Tier System Components**:
- Tier 1: Basic functionality and element discovery
- Tier 2: Intelligent flow analysis and business logic understanding
- Tier 3: Advanced scenarios, edge cases, and specialized testing

**Integrated Capabilities**:
- Enhanced application discovery and analysis
- Intelligent test flow generation
- Multi-agent collaborative test creation
- Comprehensive test strategy development
- Quality-driven test optimization
- Adaptive test maintenance and evolution

You provide the highest level of test automation intelligence by seamlessly integrating all system capabilities.
"""
        
        super().__init__(role=AgentRole.TEST_CREATION, system_message=system_message, **kwargs)
        
        # Initialize component agents
        self.discovery_agent = create_enhanced_discovery_agent(**kwargs)
        self.autogen_agent = create_autogen_test_creation_agent(**kwargs)
        self.step_generator = create_step_generator()
        self.flow_handler = create_intelligent_flow_handler()
        
        # Integration state
        self.current_workflow = None
        self.integration_results = {}
        self.quality_metrics = {}
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process integrated test generation task
        """
        try:
            task_type = task_data.get("type", "integrated_generation")
            
            if task_type == "integrated_generation":
                return await self._perform_integrated_generation(task_data)
            elif task_type == "comprehensive_analysis":
                return await self._perform_comprehensive_analysis(task_data)
            elif task_type == "adaptive_optimization":
                return await self._perform_adaptive_optimization(task_data)
            elif task_type == "quality_assessment":
                return await self._perform_quality_assessment(task_data)
            else:
                return {"error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Integrated test generation failed: {str(e)}")
            return {"error": str(e)}

    async def generate_comprehensive_tests(
        self,
        input_data: Dict[str, Any],
        discovery_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive tests using discovery results.

        This is the main entry point called by the API server.

        Args:
            input_data: Request input data containing url, app_name, test_types, etc.
            discovery_results: Results from the discovery agent containing discovered
                              elements, page structure, and application analysis.

        Returns:
            Dict[str, Any]: Generated test results including test files, coverage metrics,
                           and quality assessment.
        """
        try:
            self.logger.info("Starting comprehensive test generation")

            # Build task data from input_data and discovery_results
            task_data = {
                "type": "integrated_generation",
                "url": input_data.get("url"),
                "app_name": input_data.get("app_name", input_data.get("name", "application")),
                "test_types": input_data.get("test_types", ["functional", "e2e"]),
                "framework": input_data.get("framework", "pytest"),
                "discovery_results": discovery_results,
                "config": {
                    "headless": input_data.get("headless", True),
                    "browser": input_data.get("browser", "chromium"),
                    "output_format": input_data.get("output_format", "pytest"),
                    "enable_three_tier": True,
                    "enable_autogen": True,
                    "enable_intelligent_flows": True
                }
            }

            # Use existing integrated generation workflow
            result = await self._perform_integrated_generation(task_data)

            # Extract test files and metrics for API response
            tests = []
            if "generated_artifacts" in result:
                artifacts = result["generated_artifacts"]
                tests = artifacts.get("test_files", [])

            return {
                "status": "success" if "error" not in result else "error",
                "tests": tests,
                "total_tests": len(tests),
                "discovery_summary": result.get("discovery", {}).get("summary", {}),
                "quality_score": result.get("quality_metrics", {}).get("overall_score", 0),
                "coverage_metrics": result.get("quality_metrics", {}).get("coverage", {}),
                "generated_files": result.get("generated_artifacts", {}).get("files", []),
                "workflow_summary": result.get("summary", {}),
                "raw_results": result
            }

        except Exception as e:
            self.logger.error(f"Comprehensive test generation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "tests": [],
                "total_tests": 0
            }

    async def _perform_integrated_generation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete integrated test generation workflow
        """
        url = task_data.get("url")
        app_name = task_data.get("app_name", "application")
        generation_config = task_data.get("config", {})
        
        if not url:
            return {"error": "URL is required for integrated generation"}
        
        workflow_id = f"integrated_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_workflow = workflow_id
        
        workflow_results = {
            "workflow_id": workflow_id,
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "app_name": app_name,
            "phases": {},
            "final_artifacts": {},
            "quality_metrics": {},
            "recommendations": []
        }
        
        try:
            # Phase 1: Enhanced Discovery (skip if already provided)
            if task_data.get("discovery_results"):
                self.logger.info("Phase 1: Using provided discovery results (skipping re-discovery)")
                discovery_results = task_data["discovery_results"]
                workflow_results["phases"]["discovery"] = {
                    "status": "provided",
                    "results": discovery_results
                }
            else:
                self.logger.info("Phase 1: Enhanced Application Discovery")
                discovery_results = await self._execute_enhanced_discovery(url, generation_config)
                workflow_results["phases"]["discovery"] = discovery_results
            
            # Phase 2: Intelligent Flow Analysis
            self.logger.info("Phase 2: Intelligent Flow Analysis")
            flow_analysis = await self._execute_flow_analysis(discovery_results, generation_config)
            workflow_results["phases"]["flow_analysis"] = flow_analysis
            
            # Phase 3: Three-Tier Test Generation
            self.logger.info("Phase 3: Three-Tier Test Generation")
            test_generation = await self._execute_three_tier_generation(
                discovery_results, flow_analysis, generation_config
            )
            workflow_results["phases"]["test_generation"] = test_generation
            
            # Phase 4: AutoGen Collaboration (if enabled)
            if generation_config.get("enable_autogen", True):
                self.logger.info("Phase 4: AutoGen Collaborative Enhancement")
                autogen_results = await self._execute_autogen_collaboration(
                    discovery_results, test_generation, generation_config
                )
                workflow_results["phases"]["autogen_collaboration"] = autogen_results
            
            # Phase 5: Quality Assessment and Optimization
            self.logger.info("Phase 5: Quality Assessment and Optimization")
            quality_results = await self._execute_quality_assessment(workflow_results)
            workflow_results["phases"]["quality_assessment"] = quality_results
            
            # Phase 6: Final Artifact Generation
            self.logger.info("Phase 6: Final Artifact Generation")
            final_artifacts = await self._generate_final_artifacts(workflow_results, generation_config)
            workflow_results["final_artifacts"] = final_artifacts
            
            # Calculate overall quality metrics
            workflow_results["quality_metrics"] = self._calculate_overall_quality_metrics(workflow_results)
            
            # Generate recommendations
            workflow_results["recommendations"] = self._generate_workflow_recommendations(workflow_results)
            
            # Save workflow results
            output_file = self.save_work_artifact(
                f"integrated_workflow_{workflow_id}.json",
                json.dumps(workflow_results, indent=2, default=str)
            )
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "workflow_results": workflow_results,
                "output_file": output_file,
                "summary": self._create_workflow_summary(workflow_results)
            }
            
        except Exception as e:
            self.logger.error(f"Integrated workflow failed: {e}")
            workflow_results["error"] = str(e)
            workflow_results["status"] = "failed"
            return workflow_results
    
    async def _execute_enhanced_discovery(self, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute enhanced discovery phase
        """
        discovery_task = {
            "type": "enhanced_discovery",
            "url": url,
            "analysis_depth": config.get("discovery_depth", "comprehensive"),
            "headless": config.get("headless", True)
        }
        
        discovery_results = await self.discovery_agent.process_task(discovery_task)
        
        # Enhance results with additional analysis
        if discovery_results.get("status") == "success":
            discovery_data = discovery_results.get("discovery_results", {})
            
            # Add three-tier analysis
            discovery_data["three_tier_analysis"] = self._analyze_for_three_tier_generation(discovery_data)
            
            # Add complexity assessment
            discovery_data["complexity_assessment"] = self._assess_application_complexity(discovery_data)
            
            discovery_results["discovery_results"] = discovery_data
        
        return discovery_results
    
    async def _execute_flow_analysis(self, discovery_results: Dict[str, Any], 
                                   config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute intelligent flow analysis phase
        """
        if discovery_results.get("status") != "success":
            return {"error": "Discovery phase failed, cannot proceed with flow analysis"}
        
        discovery_data = discovery_results.get("discovery_results", {})
        
        # Analyze application flows
        flow_analysis = self.flow_handler.analyze_application_flows(discovery_data)
        
        # Generate intelligent flows
        requirements = {
            "default_timeout": config.get("default_timeout", 30),
            "include_performance_tests": config.get("include_performance_tests", False),
            "test_network_errors": config.get("test_network_errors", True),
            "complexity_level": config.get("complexity_level", "comprehensive")
        }
        
        intelligent_flows = self.flow_handler.generate_intelligent_flows(flow_analysis, requirements)
        
        return {
            "status": "success",
            "flow_analysis": flow_analysis,
            "intelligent_flows": [flow.__dict__ for flow in intelligent_flows],
            "flow_count": len(intelligent_flows),
            "analysis_summary": {
                "identified_flows": len(flow_analysis.get("identified_flows", [])),
                "critical_paths": len(flow_analysis.get("critical_paths", [])),
                "optimization_opportunities": len(flow_analysis.get("optimization_opportunities", [])),
                "risk_areas": len(flow_analysis.get("risk_areas", []))
            }
        }
    
    async def _execute_three_tier_generation(self, discovery_results: Dict[str, Any],
                                           flow_analysis: Dict[str, Any],
                                           config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute three-tier test generation phase
        """
        if discovery_results.get("status") != "success":
            return {"error": "Discovery phase failed, cannot proceed with test generation"}
        
        discovery_data = discovery_results.get("discovery_results", {})
        
        # Prepare requirements for three-tier generation
        requirements = {
            "flow_types": config.get("flow_types", ["user_journey", "business_workflows"]),
            "include_advanced_scenarios": config.get("include_advanced_scenarios", True),
            "complexity_level": config.get("complexity_level", "comprehensive"),
            "test_data_strategy": config.get("test_data_strategy", "json_based"),
            "framework_preferences": config.get("framework_preferences", ["playwright", "pytest"])
        }
        
        # Generate comprehensive test suite using three-tier approach
        test_suite = self.step_generator.generate_comprehensive_test_suite(
            discovery_data, requirements
        )
        
        # Enhance test suite with flow analysis results
        if flow_analysis.get("status") == "success":
            intelligent_flows = flow_analysis.get("intelligent_flows", [])
            test_suite["intelligent_flows_integration"] = self._integrate_intelligent_flows(
                test_suite, intelligent_flows
            )
        
        return {
            "status": "success",
            "test_suite": test_suite,
            "generation_method": "three_tier_integrated",
            "tier_distribution": {
                "tier1_tests": len(test_suite.get("tier1_basic_tests", [])),
                "tier2_tests": len(test_suite.get("tier2_flow_tests", [])),
                "tier3_tests": len(test_suite.get("tier3_advanced_tests", []))
            }
        }
    
    async def _execute_autogen_collaboration(self, discovery_results: Dict[str, Any],
                                           test_generation: Dict[str, Any],
                                           config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute AutoGen collaborative enhancement phase
        """
        if test_generation.get("status") != "success":
            return {"error": "Test generation phase failed, cannot proceed with AutoGen collaboration"}
        
        # Prepare AutoGen task
        autogen_task = {
            "type": "create_tests",
            "discovery_data": discovery_results.get("discovery_results", {}),
            "requirements": {
                "app_name": config.get("app_name", "application"),
                "base_url": config.get("url", ""),
                "test_types": config.get("test_types", ["functional", "integration"]),
                "quality_standards": config.get("quality_standards", "high"),
                "collaboration_mode": config.get("collaboration_mode", "comprehensive")
            }
        }
        
        # Execute AutoGen collaboration
        autogen_results = await self.autogen_agent.process_task(autogen_task)
        
        # Integrate AutoGen results with three-tier results
        if autogen_results.get("status") == "success":
            autogen_results["integration_with_three_tier"] = self._integrate_autogen_with_three_tier(
                test_generation, autogen_results
            )
        
        return autogen_results
    
    async def _execute_quality_assessment(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute quality assessment phase
        """
        quality_assessment = {
            "status": "success",
            "overall_quality_score": 0,
            "phase_quality_scores": {},
            "quality_issues": [],
            "improvement_recommendations": [],
            "compliance_check": {}
        }
        
        # Assess each phase quality
        phases = workflow_results.get("phases", {})
        
        for phase_name, phase_results in phases.items():
            phase_score = self._assess_phase_quality(phase_name, phase_results)
            quality_assessment["phase_quality_scores"][phase_name] = phase_score
        
        # Calculate overall quality score
        if quality_assessment["phase_quality_scores"]:
            quality_assessment["overall_quality_score"] = sum(
                quality_assessment["phase_quality_scores"].values()
            ) / len(quality_assessment["phase_quality_scores"])
        
        # Identify quality issues
        quality_assessment["quality_issues"] = self._identify_quality_issues(workflow_results)
        
        # Generate improvement recommendations
        quality_assessment["improvement_recommendations"] = self._generate_quality_improvements(
            workflow_results, quality_assessment
        )
        
        # Perform compliance check
        quality_assessment["compliance_check"] = self._perform_compliance_check(workflow_results)
        
        return quality_assessment
    
    async def _generate_final_artifacts(self, workflow_results: Dict[str, Any],
                                      config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final artifacts from workflow results
        """
        artifacts = {
            "test_files": [],
            "documentation": {},
            "configuration_files": [],
            "reports": {},
            "metadata": {}
        }
        
        # Generate test files from three-tier generation
        test_generation = workflow_results.get("phases", {}).get("test_generation", {})
        if test_generation.get("status") == "success":
            test_suite = test_generation.get("test_suite", {})
            artifacts["test_files"].extend(
                await self._generate_test_files_from_suite(test_suite, config)
            )
        
        # Add AutoGen generated tests if available
        autogen_results = workflow_results.get("phases", {}).get("autogen_collaboration", {})
        if autogen_results.get("status") == "success":
            autogen_files = autogen_results.get("test_files", [])
            artifacts["test_files"].extend(autogen_files)
        
        # Generate documentation
        artifacts["documentation"] = await self._generate_documentation(workflow_results, config)
        
        # Generate configuration files
        artifacts["configuration_files"] = self._generate_configuration_files(workflow_results, config)
        
        # Generate reports
        artifacts["reports"] = self._generate_workflow_reports(workflow_results)
        
        # Generate metadata
        artifacts["metadata"] = self._generate_artifacts_metadata(workflow_results, artifacts)
        
        return artifacts
    
    def _analyze_for_three_tier_generation(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze discovery data for three-tier generation suitability
        """
        analysis = {
            "tier1_opportunities": [],
            "tier2_opportunities": [],
            "tier3_opportunities": [],
            "complexity_indicators": {},
            "generation_strategy": "balanced"
        }
        
        # Analyze for Tier 1 opportunities (basic functionality)
        page_analysis = discovery_data.get("page_analysis", {})
        interactive_elements = page_analysis.get("interactive_elements", {})
        
        if interactive_elements.get("buttons"):
            analysis["tier1_opportunities"].append("button_interactions")
        if interactive_elements.get("inputs"):
            analysis["tier1_opportunities"].append("form_interactions")
        if interactive_elements.get("links"):
            analysis["tier1_opportunities"].append("navigation_testing")
        
        # Analyze for Tier 2 opportunities (intelligent flows)
        user_journeys = discovery_data.get("user_journeys", {})
        if user_journeys.get("primary_flows"):
            analysis["tier2_opportunities"].extend(["user_journey_testing", "workflow_testing"])
        
        business_logic = discovery_data.get("business_logic", {})
        if business_logic.get("validation_rules"):
            analysis["tier2_opportunities"].append("business_logic_testing")
        
        # Analyze for Tier 3 opportunities (advanced scenarios)
        technical_analysis = discovery_data.get("technical_analysis", {})
        if technical_analysis.get("api_endpoints"):
            analysis["tier3_opportunities"].append("api_integration_testing")
        if technical_analysis.get("security_indicators"):
            analysis["tier3_opportunities"].append("security_testing")
        if technical_analysis.get("performance_characteristics"):
            analysis["tier3_opportunities"].append("performance_testing")
        
        # Determine generation strategy
        total_opportunities = (len(analysis["tier1_opportunities"]) +
                             len(analysis["tier2_opportunities"]) +
                             len(analysis["tier3_opportunities"]))
        
        if total_opportunities > 15:
            analysis["generation_strategy"] = "comprehensive"
        elif total_opportunities > 8:
            analysis["generation_strategy"] = "balanced"
        else:
            analysis["generation_strategy"] = "focused"
        
        return analysis
    
    def _assess_application_complexity(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess application complexity for test generation planning
        """
        complexity = {
            "overall_complexity": "medium",
            "complexity_factors": {},
            "complexity_score": 0,
            "testing_implications": []
        }
        
        score = 0
        
        # UI complexity
        page_analysis = discovery_data.get("page_analysis", {})
        interactive_elements = page_analysis.get("interactive_elements", {})
        total_elements = sum(len(elements) for elements in interactive_elements.values())
        
        if total_elements > 50:
            score += 3
            complexity["complexity_factors"]["ui_complexity"] = "high"
        elif total_elements > 20:
            score += 2
            complexity["complexity_factors"]["ui_complexity"] = "medium"
        else:
            score += 1
            complexity["complexity_factors"]["ui_complexity"] = "low"
        
        # Business logic complexity
        business_logic = discovery_data.get("business_logic", {})
        validation_rules = business_logic.get("validation_rules", {})
        
        if len(validation_rules) > 10:
            score += 3
            complexity["complexity_factors"]["business_logic"] = "high"
        elif len(validation_rules) > 5:
            score += 2
            complexity["complexity_factors"]["business_logic"] = "medium"
        else:
            score += 1
            complexity["complexity_factors"]["business_logic"] = "low"
        
        # Technical complexity
        technical_analysis = discovery_data.get("technical_analysis", {})
        api_count = len(technical_analysis.get("api_endpoints", []))
        
        if api_count > 20:
            score += 3
            complexity["complexity_factors"]["technical_complexity"] = "high"
        elif api_count > 10:
            score += 2
            complexity["complexity_factors"]["technical_complexity"] = "medium"
        else:
            score += 1
            complexity["complexity_factors"]["technical_complexity"] = "low"
        
        # Determine overall complexity
        complexity["complexity_score"] = score
        
        if score >= 8:
            complexity["overall_complexity"] = "high"
            complexity["testing_implications"] = [
                "Requires comprehensive test coverage",
                "Multiple test environments needed",
                "Extended test execution time",
                "Advanced debugging capabilities required"
            ]
        elif score >= 5:
            complexity["overall_complexity"] = "medium"
            complexity["testing_implications"] = [
                "Balanced test approach needed",
                "Standard test environments sufficient",
                "Moderate test execution time",
                "Standard debugging capabilities"
            ]
        else:
            complexity["overall_complexity"] = "low"
            complexity["testing_implications"] = [
                "Basic test coverage sufficient",
                "Single test environment adequate",
                "Fast test execution",
                "Simple debugging requirements"
            ]
        
        return complexity
    
    def _integrate_intelligent_flows(self, test_suite: Dict[str, Any], 
                                   intelligent_flows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Integrate intelligent flows with three-tier test suite
        """
        integration = {
            "integrated_flows": 0,
            "flow_mappings": {},
            "enhancement_summary": {}
        }
        
        # Map intelligent flows to test tiers
        for flow in intelligent_flows:
            flow_name = flow.get("name", "")
            flow_category = flow.get("category", "")
            
            # Determine appropriate tier for the flow
            if flow_category in ["smoke", "regression"]:
                target_tier = "tier1_basic_tests"
            elif flow_category in ["integration", "end_to_end"]:
                target_tier = "tier2_flow_tests"
            else:
                target_tier = "tier3_advanced_tests"
            
            integration["flow_mappings"][flow_name] = target_tier
            integration["integrated_flows"] += 1
        
        integration["enhancement_summary"] = {
            "total_flows_integrated": integration["integrated_flows"],
            "tier1_enhancements": len([f for f in integration["flow_mappings"].values() if f == "tier1_basic_tests"]),
            "tier2_enhancements": len([f for f in integration["flow_mappings"].values() if f == "tier2_flow_tests"]),
            "tier3_enhancements": len([f for f in integration["flow_mappings"].values() if f == "tier3_advanced_tests"])
        }
        
        return integration
    
    def _integrate_autogen_with_three_tier(self, test_generation: Dict[str, Any],
                                         autogen_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate AutoGen results with three-tier generation
        """
        integration = {
            "integration_strategy": "complementary",
            "combined_test_count": 0,
            "quality_enhancement": {},
            "coverage_improvement": {}
        }
        
        # Count tests from both sources
        three_tier_suite = test_generation.get("test_suite", {})
        three_tier_count = (len(three_tier_suite.get("tier1_basic_tests", [])) +
                           len(three_tier_suite.get("tier2_flow_tests", [])) +
                           len(three_tier_suite.get("tier3_advanced_tests", [])))
        
        autogen_count = len(autogen_results.get("test_files", []))
        
        integration["combined_test_count"] = three_tier_count + autogen_count
        
        # Assess quality enhancement
        integration["quality_enhancement"] = {
            "three_tier_contribution": "Systematic coverage and structure",
            "autogen_contribution": "Advanced code quality and collaboration insights",
            "synergy_benefits": [
                "Comprehensive coverage with high code quality",
                "Structured approach with intelligent optimizations",
                "Maintainable architecture with advanced features"
            ]
        }
        
        return integration
    
    def _assess_phase_quality(self, phase_name: str, phase_results: Dict[str, Any]) -> float:
        """
        Assess quality of a specific phase
        """
        if phase_results.get("status") != "success":
            return 0.0
        
        base_score = 70.0  # Base score for successful completion
        
        # Phase-specific quality assessment
        if phase_name == "discovery":
            discovery_data = phase_results.get("discovery_results", {})
            if discovery_data.get("application_profile"):
                base_score += 10.0
            if discovery_data.get("intelligent_flows"):
                base_score += 10.0
            if discovery_data.get("testing_recommendations"):
                base_score += 10.0
        
        elif phase_name == "flow_analysis":
            flow_count = phase_results.get("flow_count", 0)
            if flow_count > 5:
                base_score += 15.0
            elif flow_count > 2:
                base_score += 10.0
            else:
                base_score += 5.0
        
        elif phase_name == "test_generation":
            tier_distribution = phase_results.get("tier_distribution", {})
            total_tests = sum(tier_distribution.values())
            if total_tests > 10:
                base_score += 15.0
            elif total_tests > 5:
                base_score += 10.0
            else:
                base_score += 5.0
        
        elif phase_name == "autogen_collaboration":
            if phase_results.get("generation_method") == "autogen_collaboration":
                base_score += 15.0
            else:
                base_score += 5.0  # Fallback method used
        
        return min(100.0, base_score)
    
    def _identify_quality_issues(self, workflow_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify quality issues in the workflow
        """
        issues = []
        
        phases = workflow_results.get("phases", {})
        
        # Check for failed phases
        for phase_name, phase_results in phases.items():
            if phase_results.get("status") != "success":
                issues.append({
                    "type": "phase_failure",
                    "phase": phase_name,
                    "severity": "high",
                    "description": f"Phase {phase_name} failed to complete successfully",
                    "error": phase_results.get("error", "Unknown error")
                })
        
        # Check for low test coverage
        test_generation = phases.get("test_generation", {})
        if test_generation.get("status") == "success":
            tier_distribution = test_generation.get("tier_distribution", {})
            total_tests = sum(tier_distribution.values())
            
            if total_tests < 5:
                issues.append({
                    "type": "low_coverage",
                    "severity": "medium",
                    "description": f"Low test count: only {total_tests} tests generated",
                    "recommendation": "Consider expanding test scenarios or adjusting generation parameters"
                })
        
        # Check for missing AutoGen collaboration
        if "autogen_collaboration" not in phases:
            issues.append({
                "type": "missing_enhancement",
                "severity": "low",
                "description": "AutoGen collaboration was not executed",
                "recommendation": "Enable AutoGen collaboration for enhanced test quality"
            })
        
        return issues
    
    def _generate_quality_improvements(self, workflow_results: Dict[str, Any],
                                     quality_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate quality improvement recommendations
        """
        improvements = []
        
        overall_score = quality_assessment.get("overall_quality_score", 0)
        
        if overall_score < 80:
            improvements.append({
                "type": "overall_quality",
                "priority": "high",
                "description": "Overall workflow quality is below optimal threshold",
                "actions": [
                    "Review failed phases and address issues",
                    "Increase test coverage and complexity",
                    "Enable all available enhancement features",
                    "Validate configuration parameters"
                ]
            })
        
        # Phase-specific improvements
        phase_scores = quality_assessment.get("phase_quality_scores", {})
        for phase_name, score in phase_scores.items():
            if score < 70:
                improvements.append({
                    "type": "phase_improvement",
                    "phase": phase_name,
                    "priority": "medium",
                    "description": f"Phase {phase_name} quality can be improved",
                    "current_score": score,
                    "target_score": 85,
                    "actions": self._get_phase_improvement_actions(phase_name)
                })
        
        return improvements
    
    def _get_phase_improvement_actions(self, phase_name: str) -> List[str]:
        """
        Get improvement actions for a specific phase
        """
        actions_map = {
            "discovery": [
                "Increase analysis depth",
                "Enable comprehensive discovery features",
                "Verify application accessibility",
                "Check for dynamic content handling"
            ],
            "flow_analysis": [
                "Expand flow identification criteria",
                "Include more business scenarios",
                "Enhance risk assessment",
                "Add performance flow analysis"
            ],
            "test_generation": [
                "Increase test complexity levels",
                "Add more test tiers",
                "Include edge case scenarios",
                "Enhance data-driven testing"
            ],
            "autogen_collaboration": [
                "Enable AutoGen if disabled",
                "Increase collaboration rounds",
                "Add more specialized agents",
                "Improve prompt engineering"
            ]
        }
        
        return actions_map.get(phase_name, ["Review phase configuration and parameters"])
    
    def _perform_compliance_check(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform compliance check against testing standards
        """
        compliance = {
            "overall_compliance": "partial",
            "standards_checked": [],
            "compliance_scores": {},
            "violations": [],
            "recommendations": []
        }
        
        # Check test coverage standards
        test_generation = workflow_results.get("phases", {}).get("test_generation", {})
        if test_generation.get("status") == "success":
            tier_distribution = test_generation.get("tier_distribution", {})
            
            # Basic coverage check
            if tier_distribution.get("tier1_tests", 0) > 0:
                compliance["compliance_scores"]["basic_coverage"] = 100
            else:
                compliance["compliance_scores"]["basic_coverage"] = 0
                compliance["violations"].append("Missing basic functionality tests")
            
            # Advanced coverage check
            if tier_distribution.get("tier3_tests", 0) > 0:
                compliance["compliance_scores"]["advanced_coverage"] = 100
            else:
                compliance["compliance_scores"]["advanced_coverage"] = 50
                compliance["recommendations"].append("Consider adding advanced test scenarios")
        
        # Check documentation standards
        final_artifacts = workflow_results.get("final_artifacts", {})
        if final_artifacts.get("documentation"):
            compliance["compliance_scores"]["documentation"] = 100
        else:
            compliance["compliance_scores"]["documentation"] = 0
            compliance["violations"].append("Missing test documentation")
        
        # Calculate overall compliance
        if compliance["compliance_scores"]:
            avg_score = sum(compliance["compliance_scores"].values()) / len(compliance["compliance_scores"])
            if avg_score >= 90:
                compliance["overall_compliance"] = "full"
            elif avg_score >= 70:
                compliance["overall_compliance"] = "substantial"
            else:
                compliance["overall_compliance"] = "partial"
        
        compliance["standards_checked"] = list(compliance["compliance_scores"].keys())
        
        return compliance
    
    async def _generate_test_files_from_suite(self, test_suite: Dict[str, Any],
                                            config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate actual test files from test suite
        """
        test_files = []
        app_name = config.get("app_name", "application")
        
        # Generate files for each tier
        for tier_name, tier_tests in test_suite.items():
            if tier_name.startswith("tier") and isinstance(tier_tests, list):
                for i, test_flow in enumerate(tier_tests):
                    filename = f"test_{app_name}_{tier_name}_{i+1}.py"
                    content = self._generate_test_file_content(test_flow, app_name, config)
                    
                    test_files.append({
                        "filename": filename,
                        "content": content,
                        "tier": tier_name,
                        "description": getattr(test_flow, 'description', f"{tier_name} test {i+1}"),
                        "generator": "integrated_three_tier"
                    })
        
        return test_files
    
    def _generate_test_file_content(self, test_flow, app_name: str, config: Dict[str, Any]) -> str:
        """
        Generate content for a test file
        """
        base_url = config.get("url", "https://example.com")
        
        content = f'''"""
Test file for {app_name}
Generated by Integrated Test Generator
Flow: {getattr(test_flow, 'name', 'unknown')}
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class Test{getattr(test_flow, 'name', 'Unknown').replace('_', '').title()}:
    """Test class for {getattr(test_flow, 'description', 'test flow')}"""
    
    @pytest.fixture
    async def browser_setup(self):
        """Setup browser for testing"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            yield page
            
            await context.close()
            await browser.close()
    
    async def test_{getattr(test_flow, 'name', 'unknown')}(self, browser_setup):
        """
        Test: {getattr(test_flow, 'description', 'Test flow')}
        """
        page = browser_setup
        
        try:
            # Navigate to application
            await page.goto("{base_url}")
            
            # Basic verification
            assert await page.title(), "Page should have a title"
            
            # TODO: Implement specific test steps based on flow
            
        except Exception as e:
            pytest.fail(f"Test failed: {{str(e)}}")
'''
        
        return content
    
    async def _generate_documentation(self, workflow_results: Dict[str, Any],
                                    config: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate comprehensive documentation
        """
        documentation = {}
        
        # Generate README
        documentation["README.md"] = self._generate_readme(workflow_results, config)
        
        # Generate test strategy document
        documentation["TEST_STRATEGY.md"] = self._generate_test_strategy_doc(workflow_results)
        
        # Generate setup instructions
        documentation["SETUP_INSTRUCTIONS.md"] = self._generate_setup_instructions(workflow_results, config)
        
        # Generate API documentation if applicable
        if self._has_api_tests(workflow_results):
            documentation["API_TESTING.md"] = self._generate_api_testing_doc(workflow_results)
        
        return documentation
    
    def _generate_readme(self, workflow_results: Dict[str, Any], config: Dict[str, Any]) -> str:
        """
        Generate README documentation
        """
        app_name = config.get("app_name", "Application")
        
        readme = f"""# {app_name} Test Suite

Generated by Integrated Test Generator - Three-Tier System

## Overview

This test suite was automatically generated using the three-tier test automation system, providing comprehensive coverage across multiple testing levels.

## Test Structure

### Tier 1: Basic Functionality Tests
- Element interaction testing
- Basic form validation
- Navigation testing

### Tier 2: Intelligent Flow Tests
- User journey testing
- Business workflow validation
- Integration scenarios

### Tier 3: Advanced Scenario Tests
- Edge case testing
- Performance validation
- Security testing

## Generated Artifacts

"""
        
        # Add artifact information
        final_artifacts = workflow_results.get("final_artifacts", {})
        test_files = final_artifacts.get("test_files", [])
        
        readme += f"- **Test Files**: {len(test_files)} generated\n"
        readme += f"- **Documentation**: {len(final_artifacts.get('documentation', {}))} files\n"
        readme += f"- **Configuration**: {len(final_artifacts.get('configuration_files', []))} files\n"
        
        readme += """
## Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific tier tests
pytest tests/ -k "tier1" -v
pytest tests/ -k "tier2" -v
pytest tests/ -k "tier3" -v
```

## Quality Metrics

"""
        
        # Add quality metrics
        quality_metrics = workflow_results.get("quality_metrics", {})
        readme += f"- **Overall Quality Score**: {quality_metrics.get('overall_score', 'N/A')}\n"
        readme += f"- **Test Coverage**: {quality_metrics.get('coverage_estimate', 'N/A')}\n"
        readme += f"- **Complexity Level**: {quality_metrics.get('complexity_level', 'N/A')}\n"
        
        return readme
    
    def _generate_test_strategy_doc(self, workflow_results: Dict[str, Any]) -> str:
        """
        Generate test strategy documentation
        """
        return """# Test Strategy Document

## Testing Approach

This document outlines the comprehensive testing strategy implemented by the three-tier system.

### Three-Tier Architecture

1. **Tier 1 - Basic Functionality**
   - Validates core application features
   - Tests individual components
   - Ensures basic user interactions work

2. **Tier 2 - Intelligent Flows**
   - Tests complete user journeys
   - Validates business logic
   - Ensures workflow integrity

3. **Tier 3 - Advanced Scenarios**
   - Tests edge cases and error conditions
   - Performance and security validation
   - Integration testing with external systems

### Quality Assurance

- Automated test generation with quality checks
- Multi-agent collaboration for enhanced coverage
- Continuous improvement based on execution results

### Maintenance Strategy

- Regular test suite updates based on application changes
- Performance monitoring and optimization
- Documentation updates and knowledge sharing
"""
    
    def _generate_setup_instructions(self, workflow_results: Dict[str, Any], config: Dict[str, Any]) -> str:
        """
        Generate setup instructions
        """
        return """# Setup Instructions

## Prerequisites

- Python 3.8 or higher
- Node.js (for Playwright)
- Git

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

## Configuration

1. Copy the configuration template:
```bash
cp config.template.json config.json
```

2. Update configuration with your application details:
- Base URL
- Authentication credentials (if needed)
- Environment-specific settings

## Running Tests

### Basic Execution
```bash
pytest tests/ -v
```

### With HTML Report
```bash
pytest tests/ --html=report.html --self-contained-html
```

### Parallel Execution
```bash
pytest tests/ -n auto
```

## Troubleshooting

- Ensure all dependencies are installed
- Check browser compatibility
- Verify application accessibility
- Review test configuration
"""
    
    def _generate_configuration_files(self, workflow_results: Dict[str, Any], 
                                    config: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate configuration files
        """
        config_files = []
        
        # Generate pytest.ini
        config_files.append({
            "filename": "pytest.ini",
            "content": """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    tier1: Basic functionality tests
    tier2: Intelligent flow tests
    tier3: Advanced scenario tests
    smoke: Smoke tests
    regression: Regression tests
    integration: Integration tests
"""
        })
        
        # Generate requirements.txt
        config_files.append({
            "filename": "requirements.txt",
            "content": """pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-html>=3.1.0
pytest-xdist>=3.0.0
playwright>=1.30.0
requests>=2.28.0
"""
        })
        
        # Generate application-specific config
        app_config = {
            "base_url": config.get("url", "https://example.com"),
            "timeout": config.get("default_timeout", 30),
            "headless": config.get("headless", True),
            "browser": "chromium",
            "viewport": {"width": 1920, "height": 1080}
        }
        
        config_files.append({
            "filename": "test_config.json",
            "content": json.dumps(app_config, indent=2)
        })
        
        return config_files
    
    def _generate_workflow_reports(self, workflow_results: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate workflow reports
        """
        reports = {}
        
        # Generate execution summary
        reports["execution_summary.json"] = json.dumps({
            "workflow_id": workflow_results.get("workflow_id"),
            "timestamp": workflow_results.get("timestamp"),
            "phases_completed": len(workflow_results.get("phases", {})),
            "overall_status": "success" if not workflow_results.get("error") else "failed",
            "quality_metrics": workflow_results.get("quality_metrics", {}),
            "recommendations": workflow_results.get("recommendations", [])
        }, indent=2)
        
        # Generate detailed phase report
        phase_report = {
            "phases": {},
            "summary": {
                "total_phases": len(workflow_results.get("phases", {})),
                "successful_phases": 0,
                "failed_phases": 0
            }
        }
        
        for phase_name, phase_results in workflow_results.get("phases", {}).items():
            phase_report["phases"][phase_name] = {
                "status": phase_results.get("status"),
                "duration": phase_results.get("duration", "unknown"),
                "key_metrics": self._extract_phase_metrics(phase_name, phase_results)
            }
            
            if phase_results.get("status") == "success":
                phase_report["summary"]["successful_phases"] += 1
            else:
                phase_report["summary"]["failed_phases"] += 1
        
        reports["phase_report.json"] = json.dumps(phase_report, indent=2)
        
        return reports
    
    def _extract_phase_metrics(self, phase_name: str, phase_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key metrics from phase results
        """
        metrics = {}
        
        if phase_name == "discovery":
            discovery_data = phase_results.get("discovery_results", {})
            metrics = {
                "pages_analyzed": 1,  # Currently single page
                "elements_discovered": len(discovery_data.get("page_analysis", {}).get("interactive_elements", {})),
                "flows_identified": len(discovery_data.get("user_journeys", {}).get("primary_flows", []))
            }
        
        elif phase_name == "flow_analysis":
            metrics = {
                "flows_analyzed": phase_results.get("flow_count", 0),
                "critical_paths": len(phase_results.get("flow_analysis", {}).get("critical_paths", [])),
                "optimization_opportunities": len(phase_results.get("flow_analysis", {}).get("optimization_opportunities", []))
            }
        
        elif phase_name == "test_generation":
            tier_distribution = phase_results.get("tier_distribution", {})
            metrics = {
                "total_tests_generated": sum(tier_distribution.values()),
                "tier_distribution": tier_distribution
            }
        
        elif phase_name == "autogen_collaboration":
            metrics = {
                "test_files_generated": len(phase_results.get("test_files", [])),
                "collaboration_method": phase_results.get("generation_method", "unknown")
            }
        
        return metrics
    
    def _generate_artifacts_metadata(self, workflow_results: Dict[str, Any], 
                                   artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate metadata for all artifacts
        """
        metadata = {
            "generation_timestamp": datetime.now().isoformat(),
            "workflow_id": workflow_results.get("workflow_id"),
            "generator_version": "integrated_test_generator_v1.0",
            "artifacts_summary": {
                "test_files": len(artifacts.get("test_files", [])),
                "documentation_files": len(artifacts.get("documentation", {})),
                "configuration_files": len(artifacts.get("configuration_files", [])),
                "report_files": len(artifacts.get("reports", {}))
            },
            "quality_indicators": workflow_results.get("quality_metrics", {}),
            "generation_parameters": {
                "three_tier_enabled": True,
                "autogen_enabled": "autogen_collaboration" in workflow_results.get("phases", {}),
                "quality_assessment_enabled": True
            }
        }
        
        return metadata
    
    def _calculate_overall_quality_metrics(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall quality metrics for the workflow
        """
        metrics = {
            "overall_score": 0,
            "coverage_estimate": "unknown",
            "complexity_level": "medium",
            "maintainability_score": 0,
            "reliability_score": 0
        }
        
        # Calculate overall score from phase quality
        quality_assessment = workflow_results.get("phases", {}).get("quality_assessment", {})
        if quality_assessment.get("status") == "success":
            metrics["overall_score"] = quality_assessment.get("overall_quality_score", 0)
        
        # Estimate coverage based on test generation
        test_generation = workflow_results.get("phases", {}).get("test_generation", {})
        if test_generation.get("status") == "success":
            tier_distribution = test_generation.get("tier_distribution", {})
            total_tests = sum(tier_distribution.values())
            
            if total_tests >= 15:
                metrics["coverage_estimate"] = "high"
            elif total_tests >= 8:
                metrics["coverage_estimate"] = "medium"
            else:
                metrics["coverage_estimate"] = "low"
        
        # Assess complexity level
        discovery_results = workflow_results.get("phases", {}).get("discovery", {})
        if discovery_results.get("status") == "success":
            complexity_assessment = discovery_results.get("discovery_results", {}).get("complexity_assessment", {})
            metrics["complexity_level"] = complexity_assessment.get("overall_complexity", "medium")
        
        # Calculate maintainability score
        final_artifacts = workflow_results.get("final_artifacts", {})
        documentation_count = len(final_artifacts.get("documentation", {}))
        config_count = len(final_artifacts.get("configuration_files", []))
        
        maintainability = 60  # Base score
        maintainability += min(20, documentation_count * 5)  # Documentation bonus
        maintainability += min(20, config_count * 10)  # Configuration bonus
        
        metrics["maintainability_score"] = maintainability
        
        # Calculate reliability score based on successful phases
        phases = workflow_results.get("phases", {})
        successful_phases = sum(1 for phase in phases.values() if phase.get("status") == "success")
        total_phases = len(phases)
        
        if total_phases > 0:
            metrics["reliability_score"] = (successful_phases / total_phases) * 100
        
        return metrics
    
    def _generate_workflow_recommendations(self, workflow_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on workflow results
        """
        recommendations = []
        
        # Quality-based recommendations
        quality_metrics = workflow_results.get("quality_metrics", {})
        overall_score = quality_metrics.get("overall_score", 0)
        
        if overall_score < 80:
            recommendations.append({
                "type": "quality_improvement",
                "priority": "high",
                "title": "Improve Overall Quality",
                "description": f"Current quality score ({overall_score:.1f}) is below recommended threshold (80+)",
                "actions": [
                    "Review and address quality issues identified in assessment",
                    "Enable all available enhancement features",
                    "Increase test coverage and complexity",
                    "Validate configuration parameters"
                ]
            })
        
        # Coverage-based recommendations
        coverage_estimate = quality_metrics.get("coverage_estimate", "unknown")
        if coverage_estimate == "low":
            recommendations.append({
                "type": "coverage_enhancement",
                "priority": "medium",
                "title": "Increase Test Coverage",
                "description": "Current test coverage is estimated to be low",
                "actions": [
                    "Add more test scenarios to each tier",
                    "Include edge case testing",
                    "Expand business logic validation",
                    "Add integration test scenarios"
                ]
            })
        
        # AutoGen recommendations
        phases = workflow_results.get("phases", {})
        if "autogen_collaboration" not in phases:
            recommendations.append({
                "type": "feature_enhancement",
                "priority": "low",
                "title": "Enable AutoGen Collaboration",
                "description": "AutoGen collaboration can enhance test quality and coverage",
                "actions": [
                    "Install AutoGen dependencies",
                    "Configure OpenAI API access",
                    "Enable AutoGen in generation configuration",
                    "Review and optimize collaboration prompts"
                ]
            })
        
        # Maintenance recommendations
        recommendations.append({
            "type": "maintenance",
            "priority": "low",
            "title": "Establish Maintenance Practices",
            "description": "Implement regular maintenance practices for sustained quality",
            "actions": [
                "Schedule regular test suite reviews",
                "Monitor test execution performance",
                "Update tests based on application changes",
                "Maintain documentation and configuration"
            ]
        })
        
        return recommendations
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this agent provides"""
        return [
            "integrated_test_generation",
            "three_tier_orchestration",
            "workflow_management",
            "quality_assurance",
            "comprehensive_analysis",
            "adaptive_optimization",
            "artifact_generation",
            "performance_monitoring"
        ]
    
    def _create_workflow_summary(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive workflow summary
        """
        summary = {
            "workflow_id": workflow_results.get("workflow_id"),
            "status": "success" if not workflow_results.get("error") else "failed",
            "execution_time": "unknown",  # Would be calculated from actual execution
            "phases_completed": len(workflow_results.get("phases", {})),
            "artifacts_generated": {},
            "quality_summary": {},
            "key_achievements": [],
            "next_steps": []
        }
        
        # Summarize artifacts
        final_artifacts = workflow_results.get("final_artifacts", {})
        summary["artifacts_generated"] = {
            "test_files": len(final_artifacts.get("test_files", [])),
            "documentation": len(final_artifacts.get("documentation", {})),
            "configuration": len(final_artifacts.get("configuration_files", [])),
            "reports": len(final_artifacts.get("reports", {}))
        }
        
        # Summarize quality
        quality_metrics = workflow_results.get("quality_metrics", {})
        summary["quality_summary"] = {
            "overall_score": quality_metrics.get("overall_score", 0),
            "coverage_level": quality_metrics.get("coverage_estimate", "unknown"),
            "complexity_handled": quality_metrics.get("complexity_level", "medium"),
            "maintainability": quality_metrics.get("maintainability_score", 0)
        }
        
        # Key achievements
        phases = workflow_results.get("phases", {})
        if phases.get("discovery", {}).get("status") == "success":
            summary["key_achievements"].append("Comprehensive application discovery completed")
        
        if phases.get("test_generation", {}).get("status") == "success":
            tier_dist = phases["test_generation"].get("tier_distribution", {})
            total_tests = sum(tier_dist.values())
            summary["key_achievements"].append(f"Generated {total_tests} tests across three tiers")
        
        if phases.get("autogen_collaboration", {}).get("status") == "success":
            summary["key_achievements"].append("Enhanced tests with AutoGen collaboration")
        
        # Next steps
        recommendations = workflow_results.get("recommendations", [])
        high_priority_recs = [rec for rec in recommendations if rec.get("priority") == "high"]
        
        if high_priority_recs:
            summary["next_steps"].append("Address high-priority quality improvements")
        
        summary["next_steps"].extend([
            "Execute generated test suite",
            "Review and customize tests as needed",
            "Integrate with CI/CD pipeline",
            "Establish maintenance schedule"
        ])
        
        return summary
    
    def _has_api_tests(self, workflow_results: Dict[str, Any]) -> bool:
        """
        Check if the workflow includes API testing
        """
        discovery_results = workflow_results.get("phases", {}).get("discovery", {})
        if discovery_results.get("status") == "success":
            discovery_data = discovery_results.get("discovery_results", {})
            technical_analysis = discovery_data.get("technical_analysis", {})
            api_endpoints = technical_analysis.get("api_endpoints", [])
            return len(api_endpoints) > 0
        
        return False
    
    def _generate_api_testing_doc(self, workflow_results: Dict[str, Any]) -> str:
        """
        Generate API testing documentation
        """
        return """# API Testing Documentation

## Overview

This document describes the API testing approach and implementation for the discovered API endpoints.

## Discovered Endpoints

The following API endpoints were identified during discovery:

- [List would be populated with actual discovered endpoints]

## Testing Strategy

### API Test Categories

1. **Functional Testing**
   - Request/response validation
   - Data integrity checks
   - Business logic validation

2. **Integration Testing**
   - End-to-end workflow testing
   - Data flow validation
   - System integration checks

3. **Performance Testing**
   - Response time validation
   - Load testing scenarios
   - Scalability assessment

4. **Security Testing**
   - Authentication validation
   - Authorization checks
   - Input validation testing

## Implementation

API tests are integrated into the three-tier system:

- **Tier 2**: Business workflow API testing
- **Tier 3**: Advanced API scenarios and edge cases

## Execution

```bash
# Run API tests specifically
pytest tests/ -k "api" -v

# Run with API performance monitoring
pytest tests/ -k "api" --api-monitoring -v
```
"""


def create_integrated_test_generator(**kwargs) -> IntegratedTestGenerator:
    """Factory function to create an integrated test generator"""
    return IntegratedTestGenerator(**kwargs)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_integrated_generation():
        generator = create_integrated_test_generator()
        
        task_data = {
            "type": "integrated_generation",
            "url": "https://example.com",
            "app_name": "example_app",
            "config": {
                "discovery_depth": "comprehensive",
                "enable_autogen": True,
                "include_performance_tests": True,
                "complexity_level": "high"
            }
        }
        
        result = await generator.process_task(task_data)
        print(f"Integrated generation completed: {result.get('status')}")
        
        if result.get("summary"):
            summary = result["summary"]
            print(f"Phases completed: {summary.get('phases_completed')}")
            print(f"Artifacts generated: {summary.get('artifacts_generated')}")
            print(f"Quality score: {summary.get('quality_summary', {}).get('overall_score')}")
    
    asyncio.run(test_integrated_generation())
