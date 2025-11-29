#!/usr/bin/env python3
"""
Complete Orchestrator for AutoGen Test Automation Framework
Coordinates all specialized agents in a complete test automation workflow
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Framework imports
from config.settings import settings, AgentRole
from models.local_ai_provider import LocalAIProvider
from parsers.unified_parser import UnifiedTestFileParser

# Agent imports
from agents.planning_agent import PlanningAgent
from agents.test_creation_agent import EnhancedTestCreationAgent as TestCreationAgent
from agents.review_agent import ReviewAgent
from agents.execution_agent import ExecutionAgent
from agents.reporting_agent import ReportingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompleteOrchestrator:
    """Complete orchestrator that coordinates all specialized agents"""
    
    def __init__(self):
        self.local_ai_provider = None
        self.agents = {}
        self.workflow_state = {
            "current_step": None,
            "completed_steps": [],
            "failed_steps": [],
            "workflow_data": {},
            "start_time": None,
            "end_time": None
        }
        
    async def initialize(self):
        """Initialize the orchestrator and all agents"""
        logger.info("🚀 Initializing Complete Test Automation Orchestrator")
        
        # Initialize local AI provider
        self.local_ai_provider = LocalAIProvider()
        
        if not self.local_ai_provider.is_available():
            logger.error("❌ Local AI provider not available")
            return False
            
        logger.info(f"✅ Local AI provider initialized with {len(self.local_ai_provider.available_models)} models")
        
        # Create all specialized agents
        await self._create_agents()
        
        logger.info("✅ Complete orchestrator initialized successfully")
        return True
        
    async def _create_agents(self):
        """Create all specialized agents"""
        logger.info("Creating specialized agents...")
        
        # Planning Agent
        self.agents["planning"] = PlanningAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        # Test Creation Agent
        self.agents["test_creation"] = TestCreationAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        # Review Agent
        self.agents["review"] = ReviewAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        # Execution Agent
        self.agents["execution"] = ExecutionAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        # Reporting Agent
        self.agents["reporting"] = ReportingAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        logger.info(f"✅ Created {len(self.agents)} specialized agents")
        
    async def execute_complete_workflow(self, input_files: List[str], workflow_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute complete test automation workflow"""
        logger.info("🔄 Starting Complete Test Automation Workflow")
        
        self.workflow_state["start_time"] = datetime.now()
        workflow_config = workflow_config or {}
        
        workflow_result = {
            "workflow_id": f"workflow_{int(time.time())}",
            "start_time": self.workflow_state["start_time"].isoformat(),
            "input_files": input_files,
            "steps": {},
            "final_results": {},
            "success": False
        }
        
        try:
            # Step 1: Parse Input Files
            logger.info("📄 Step 1: Parsing input files...")
            parse_result = await self._parse_input_files(input_files)
            workflow_result["steps"]["parse_files"] = parse_result
            self.workflow_state["workflow_data"]["parsed_files"] = parse_result
            
            # Step 2: Planning
            logger.info("🎯 Step 2: Creating test plan...")
            all_scenarios = []
            for parsed_file in parse_result.get("parsed_files", []):
                all_scenarios.extend(parsed_file.get("scenarios", []))
            
            planning_result = await self._execute_planning_step(all_scenarios)
            workflow_result["steps"]["planning"] = planning_result
            self.workflow_state["workflow_data"]["test_plan"] = planning_result
            
            # Step 3: Test Creation
            logger.info("⚙️ Step 3: Generating test code...")
            creation_result = await self._execute_test_creation_step(planning_result)
            workflow_result["steps"]["test_creation"] = creation_result
            self.workflow_state["workflow_data"]["generated_tests"] = creation_result
            
            # Step 4: Code Review
            logger.info("🔍 Step 4: Reviewing generated code...")
            review_result = await self._execute_review_step(creation_result)
            workflow_result["steps"]["review"] = review_result
            self.workflow_state["workflow_data"]["review_results"] = review_result
            
            # Step 5: Test Execution (if review passes)
            if review_result.get("overall_score", 0) >= workflow_config.get("min_review_score", 7.0):
                logger.info("⚡ Step 5: Executing tests...")
                execution_result = await self._execute_execution_step(creation_result, review_result)
                workflow_result["steps"]["execution"] = execution_result
                self.workflow_state["workflow_data"]["execution_results"] = execution_result
            else:
                logger.warning("⚠️ Skipping test execution due to low review score")
                workflow_result["steps"]["execution"] = {"status": "skipped", "reason": "Low review score"}
            
            # Step 6: Reporting
            logger.info("📊 Step 6: Generating comprehensive report...")
            reporting_result = await self._execute_reporting_step()
            workflow_result["steps"]["reporting"] = reporting_result
            self.workflow_state["workflow_data"]["final_report"] = reporting_result
            
            # Finalize workflow
            workflow_result["success"] = True
            workflow_result["final_results"] = self._extract_final_results()
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            workflow_result["error"] = str(e)
            workflow_result["success"] = False
        
        finally:
            self.workflow_state["end_time"] = datetime.now()
            workflow_result["end_time"] = self.workflow_state["end_time"].isoformat()
            workflow_result["total_duration"] = (self.workflow_state["end_time"] - self.workflow_state["start_time"]).total_seconds()
        
        # Save workflow results
        await self._save_workflow_results(workflow_result)
        
        logger.info(f"✅ Complete workflow finished - Success: {workflow_result['success']}")
        return workflow_result
        
    async def _parse_input_files(self, input_files: List[str]) -> Dict[str, Any]:
        """Parse input files using unified parser"""
        parser = UnifiedTestFileParser()
        parse_results = {
            "total_files": len(input_files),
            "parsed_files": [],
            "parsing_errors": [],
            "scenarios_extracted": 0
        }
        
        for file_path in input_files:
            try:
                if Path(file_path).exists():
                    parsed_file = await parser.parse_file(file_path)
                    parse_results["parsed_files"].append({
                        "file_path": file_path,
                        "scenarios": parsed_file.scenarios,
                        "metadata": parsed_file.metadata
                    })
                    parse_results["scenarios_extracted"] += len(parsed_file.scenarios)
                else:
                    parse_results["parsing_errors"].append(f"File not found: {file_path}")
            except Exception as e:
                parse_results["parsing_errors"].append(f"Error parsing {file_path}: {str(e)}")
        
        return parse_results
        
    async def _execute_planning_step(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute planning step"""
        planning_agent = self.agents["planning"]
        
        planning_task = {
            "type": "create_plan",
            "scenarios": scenarios,
            "requirements": {
                "test_frameworks": ["playwright", "selenium"],
                "coverage_requirements": ["ui", "api", "integration"],
                "quality_gates": {"min_coverage": 80, "max_execution_time": 300}
            }
        }
        
        return await planning_agent.process_task(planning_task)

        
    async def _execute_test_creation_step(self, planning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test creation step"""
        test_creation_agent = self.agents["test_creation"]
        
        # Extract test specifications from planning result
        test_scenarios = planning_result.get("test_scenarios", [])
        
        creation_task = {
            "type": "generate_tests",
            "test_scenarios": test_scenarios,
            "framework_preferences": ["playwright", "selenium"],
            "quality_requirements": {
                "include_error_handling": True,
                "include_logging": True,
                "include_assertions": True
            }
        }
        
        return await test_creation_agent.process_task(creation_task)
        
    async def _execute_review_step(self, creation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute review step"""
        review_agent = self.agents["review"]
        
        # Extract generated test files
        test_files = creation_result.get("test_files", [])
        generated_tests = creation_result.get("generated_tests", [])
        
        review_task = {
            "type": "review_code",
            "test_files": test_files,
            "generated_tests": generated_tests,
            "review_criteria": {
                "min_quality_score": 7.0,
                "check_error_handling": True,
                "check_test_coverage": True,
                "check_code_style": True
            }
        }
        
        return await review_agent.process_task(review_task)
        
    async def _execute_execution_step(self, creation_result: Dict[str, Any], review_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test execution step"""
        execution_agent = self.agents["execution"]
        
        # Extract test files for execution
        test_files = creation_result.get("test_files", [])
        
        execution_task = {
            "type": "execute_tests",
            "test_files": test_files,
            "execution_config": {
                "parallel_execution": True,
                "max_parallel_tests": 3,
                "timeout": 300,
                "retry_failed_tests": True,
                "generate_reports": True
            }
        }
        
        return await execution_agent.process_task(execution_task)
        
    async def _execute_reporting_step(self) -> Dict[str, Any]:
        """Execute reporting step"""
        reporting_agent = self.agents["reporting"]
        
        # Gather all workflow data for comprehensive reporting
        execution_data = self.workflow_state["workflow_data"].get("execution_results", {})
        review_data = self.workflow_state["workflow_data"].get("review_results", {})
        
        reporting_task = {
            "type": "generate_report",
            "execution_data": execution_data,
            "review_data": review_data,
            "workflow_data": self.workflow_state["workflow_data"],
            "report_config": {
                "include_executive_summary": True,
                "include_detailed_results": True,
                "include_recommendations": True,
                "generate_html": True,
                "generate_json": True
            }
        }
        
        return await reporting_agent.process_task(reporting_task)
        
    def _extract_final_results(self) -> Dict[str, Any]:
        """Extract final results from workflow"""
        workflow_data = self.workflow_state["workflow_data"]
        
        # Extract key metrics
        execution_results = workflow_data.get("execution_results", {})
        review_results = workflow_data.get("review_results", {})
        
        execution_summary = execution_results.get("summary", {})
        
        return {
            "test_execution_summary": {
                "total_tests": execution_summary.get("total_tests", 0),
                "passed_tests": execution_summary.get("passed", 0),
                "failed_tests": execution_summary.get("failed", 0),
                "success_rate": execution_summary.get("success_rate", 0),
                "execution_time": execution_summary.get("total_execution_time", 0)
            },
            "code_quality_summary": {
                "overall_score": review_results.get("overall_score", 0),
                "total_issues": len(review_results.get("reviews", [])),
                "recommendations": len(review_results.get("recommendations", []))
            },
            "workflow_summary": {
                "total_steps": len([step for step in self.workflow_state["completed_steps"]]),
                "successful_steps": len([step for step in self.workflow_state["completed_steps"] if step.get("success", False)]),
                "total_duration": (self.workflow_state["end_time"] - self.workflow_state["start_time"]).total_seconds() if self.workflow_state["end_time"] else 0
            },
            "deliverables": {
                "test_files": workflow_data.get("generated_tests", {}).get("test_files", []),
                "reports": workflow_data.get("final_report", {}).get("html_report_path", ""),
                "execution_results": workflow_data.get("execution_results", {}).get("results_path", "")
            }
        }
        
    async def _save_workflow_results(self, workflow_result: Dict[str, Any]):
        """Save workflow results to file"""
        results_filename = f"complete_workflow_results_{workflow_result['workflow_id']}.json"
        
        try:
            with open(results_filename, 'w') as f:
                json.dump(workflow_result, f, indent=2, default=str)
            logger.info(f"📁 Workflow results saved to: {results_filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save workflow results: {e}")
    
    async def execute_simple_workflow(self, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a simplified workflow for testing purposes"""
        logger.info("🔄 Starting Simple Test Workflow")
        
        workflow_result = {
            "workflow_type": "simple",
            "start_time": datetime.now().isoformat(),
            "steps": {},
            "success": False
        }
        
        try:
            # Step 1: Planning
            logger.info("🎯 Planning step...")
            planning_result = await self.agents["planning"].process_task({
                "type": "create_plan",
                "scenarios": test_scenarios
            })
            workflow_result["steps"]["planning"] = {"success": bool(planning_result), "result": planning_result}
            
            # Step 2: Test Creation
            logger.info("⚙️ Test creation step...")
            creation_result = await self.agents["test_creation"].process_task({
                "type": "generate_tests",
                "test_scenarios": test_scenarios
            })
            workflow_result["steps"]["test_creation"] = {"success": bool(creation_result), "result": creation_result}
            
            # Step 3: Review
            logger.info("🔍 Review step...")
            review_result = await self.agents["review"].process_task({
                "type": "review_code",
                "test_code": "# Sample test code for review\nimport pytest\n\ndef test_example():\n    assert True"
            })
            workflow_result["steps"]["review"] = {"success": bool(review_result), "result": review_result}
            
            # Step 4: Execution Setup
            logger.info("⚡ Execution setup step...")
            execution_result = await self.agents["execution"].process_task({
                "type": "setup_environment",
                "config": {"auto_install": False, "setup_browsers": False}
            })
            workflow_result["steps"]["execution"] = {"success": bool(execution_result), "result": execution_result}
            
            # Step 5: Reporting
            logger.info("📊 Reporting step...")
            reporting_result = await self.agents["reporting"].process_task({
                "type": "generate_report",
                "execution_data": {"summary": {"total_tests": 1, "success_rate": 100}},
                "review_data": review_result.get("review_results", {})
            })
            workflow_result["steps"]["reporting"] = {"success": bool(reporting_result), "result": reporting_result}
            
            workflow_result["success"] = True
            
        except Exception as e:
            logger.error(f"❌ Simple workflow failed: {e}")
            workflow_result["error"] = str(e)
        
        workflow_result["end_time"] = datetime.now().isoformat()
        logger.info(f"✅ Simple workflow completed - Success: {workflow_result['success']}")
        
        return workflow_result
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "current_step": self.workflow_state["current_step"],
            "completed_steps": len(self.workflow_state["completed_steps"]),
            "failed_steps": len(self.workflow_state["failed_steps"]),
            "start_time": self.workflow_state["start_time"].isoformat() if self.workflow_state["start_time"] else None,
            "agents_available": list(self.agents.keys()),
            "agents_status": {name: "ready" for name in self.agents.keys()}
        }


async def main():
    """Main function for testing the complete orchestrator"""
    orchestrator = CompleteOrchestrator()
    
    # Initialize orchestrator
    if not await orchestrator.initialize():
        logger.error("Failed to initialize orchestrator")
        return
    
    # Test simple workflow
    test_scenarios = [
        {
            "name": "Login Test",
            "description": "Test user login functionality",
            "test_steps": [
                "Navigate to login page",
                "Enter valid credentials",
                "Click login button",
                "Verify successful login"
            ],
            "expected_results": "User should be logged in successfully"
        }
    ]
    
    result = await orchestrator.execute_simple_workflow(test_scenarios)
    
    logger.info("🎉 Complete Orchestrator Test Completed!")
    logger.info(f"Workflow Success: {result['success']}")
    logger.info(f"Steps Completed: {len([s for s in result['steps'].values() if s['success']])}/{len(result['steps'])}")


if __name__ == "__main__":
    asyncio.run(main())

