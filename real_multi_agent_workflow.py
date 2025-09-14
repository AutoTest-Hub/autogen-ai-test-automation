#!/usr/bin/env python3
"""
Real Multi-Agent Workflow
===================
This script implements a real multi-agent workflow using all six agents.
"""

import os
import sys
import json
import logging
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import agents
from agents.planning_agent import PlanningAgent
from agents.real_browser_discovery_agent_compatible import RealBrowserDiscoveryAgent
from agents.test_creation_agent import EnhancedTestCreationAgent
from agents.review_agent import ReviewAgent
from agents.execution_agent import ExecutionAgent
from agents.reporting_agent import ReportingAgent

class RealMultiAgentWorkflow:
    """
    Real Multi-Agent Workflow
    
    This class orchestrates the workflow between all six agents in the AI test automation framework.
    """
    
    def __init__(self):
        """Initialize the real multi-agent workflow"""
        # Create agents
        logger.info("Initializing agents...")
        self.planning_agent = PlanningAgent()
        self.discovery_agent = RealBrowserDiscoveryAgent()
        self.test_creation_agent = EnhancedTestCreationAgent()
        self.review_agent = ReviewAgent()
        self.execution_agent = ExecutionAgent()
        self.reporting_agent = ReportingAgent()
        
        # Create directories
        self.work_dir = Path("work_dir")
        self.reports_dir = Path("reports")
        self.screenshots_dir = Path("screenshots")
        self.tests_dir = Path("tests")
        self.pages_dir = Path("pages")
        
        for directory in [self.work_dir, self.reports_dir, self.screenshots_dir, self.tests_dir, self.pages_dir]:
            directory.mkdir(exist_ok=True)
    
    async def run_workflow(self, application_url: str, application_name: str) -> Dict[str, Any]:
        """
        Run the complete workflow
        
        Args:
            application_url: URL of the application to test
            application_name: Name of the application
            
        Returns:
            Dict[str, Any]: Workflow results
        """
        logger.info(f"Starting workflow for {application_name} at {application_url}")
        
        # Step 1: Planning
        logger.info("Step 1: Planning")
        test_plan = await self._run_planning_agent(application_url, application_name)
        
        # Step 2: Discovery
        logger.info("Step 2: Discovery")
        discovery_results = await self._run_discovery_agent(application_url)
        
        # Step 3: Test Creation
        logger.info("Step 3: Test Creation")
        test_creation_results = await self._run_test_creation_agent(test_plan, discovery_results)
        
        # Step 4: Review
        logger.info("Step 4: Review")
        review_results = await self._run_review_agent(test_creation_results)
        
        # Step 5: Execution
        logger.info("Step 5: Execution")
        execution_results = await self._run_execution_agent(test_creation_results)
        
        # Step 6: Reporting
        logger.info("Step 6: Reporting")
        report = await self._run_reporting_agent(execution_results)
        
        # Return workflow results
        workflow_results = {
            "application_name": application_name,
            "application_url": application_url,
            "test_plan": test_plan,
            "discovery_results": discovery_results,
            "test_creation_results": test_creation_results,
            "review_results": review_results,
            "execution_results": execution_results,
            "report": report
        }
        
        logger.info("Workflow completed successfully")
        return workflow_results
    
    async def _run_planning_agent(self, application_url: str, application_name: str) -> Dict[str, Any]:
        """Run the planning agent"""
        logger.info(f"Running planning agent for {application_name}")
        
        # Create test requirements
        requirements = {
            "application_name": application_name,
            "application_url": application_url,
            "test_scope": "basic functionality",
            "priority_features": ["login", "navigation", "search"]
        }
        
        # Create task data for planning agent
        task_data = {
            "type": "create_plan",
            "requirements": requirements,
            "test_files": [
                {
                    "path": f"{application_name.lower()}_requirements.txt",
                    "content": f"Test requirements for {application_name}\n\n"
                              f"1. Test login functionality\n"
                              f"2. Test navigation through main sections\n"
                              f"3. Test search functionality\n",
                    "format": "txt"
                }
            ]
        }
        
        # Process task with planning agent
        try:
            result = await self.planning_agent.process_task(task_data)
            
            # Save test plan
            test_plan = result.get("test_plan", {})
            test_plan_path = self.work_dir / f"test_plan_{application_name.lower().replace(' ', '_')}.json"
            with open(test_plan_path, 'w') as f:
                json.dump(test_plan, f, indent=2)
            
            logger.info(f"Test plan created: {test_plan_path}")
            
            return test_plan
            
        except Exception as e:
            logger.error(f"Planning agent failed: {str(e)}")
            return {"error": str(e)}
    
    async def _run_discovery_agent(self, application_url: str) -> Dict[str, Any]:
        """Run the discovery agent"""
        logger.info(f"Running discovery agent for {application_url}")
        
        try:
            # Discover elements on the application
            discovery_results = await self.discovery_agent.discover_elements(application_url)
            
            # Save discovery results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            discovery_results_path = self.work_dir / f"discovery_results_{timestamp}.json"
            with open(discovery_results_path, 'w') as f:
                json.dump(discovery_results, f, indent=2)
            
            logger.info(f"Discovery results created: {discovery_results_path}")
            
            return discovery_results
            
        except Exception as e:
            logger.error(f"Discovery agent failed: {str(e)}")
            return {"error": str(e)}
    
    async def _run_test_creation_agent(self, test_plan: Dict[str, Any], discovery_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run the test creation agent"""
        logger.info("Running test creation agent")
        
        try:
            # Create task data for test creation agent
            task_data = {
                "task_type": "generate_tests",
                "test_plan": test_plan,
                "application_data": {
                    "base_url": discovery_results.get("application_url", ""),
                    "discovered_pages": discovery_results.get("pages", []),
                    "discovered_elements": discovery_results.get("elements", {}),
                    "user_workflows": discovery_results.get("workflows", [])
                }
            }
            
            # Process task with test creation agent
            result = await self.test_creation_agent.process_task(task_data)
            
            # Save test creation results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_creation_results_path = self.work_dir / f"test_creation_results_{timestamp}.json"
            with open(test_creation_results_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Test creation results created: {test_creation_results_path}")
            
            # Copy generated files to proper directories
            generated_files = result.get("generated_files", [])
            for file_info in generated_files:
                file_path = file_info.get("path", "")
                file_type = file_info.get("type", "")
                file_name = file_info.get("name", "")
                
                if file_path and os.path.exists(file_path):
                    if file_type == "test":
                        dest_path = self.tests_dir / file_name
                    elif file_type == "page_object":
                        dest_path = self.pages_dir / file_name
                    else:
                        dest_path = Path(file_name)
                    
                    # Copy file
                    with open(file_path, 'r') as src_file:
                        content = src_file.read()
                        with open(dest_path, 'w') as dest_file:
                            dest_file.write(content)
                    
                    logger.info(f"Copied {file_type} file to {dest_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Test creation agent failed: {str(e)}")
            return {"error": str(e)}
    
    async def _run_review_agent(self, test_creation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run the review agent"""
        logger.info("Running review agent")
        
        try:
            # Get generated files
            generated_files = test_creation_results.get("generated_files", [])
            
            # Create task data for review agent
            task_data = {
                "task_type": "review_tests",
                "generated_files": generated_files
            }
            
            # Process task with review agent
            result = await self.review_agent.process_task(task_data)
            
            # Save review results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            review_results_path = self.work_dir / f"review_results_{timestamp}.json"
            with open(review_results_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Review results created: {review_results_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Review agent failed: {str(e)}")
            return {"error": str(e)}
    
    async def _run_execution_agent(self, test_creation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run the execution agent"""
        logger.info("Running execution agent")
        
        try:
            # Get test files
            test_files = []
            for file_info in test_creation_results.get("generated_files", []):
                if file_info.get("type") == "test":
                    test_files.append(file_info.get("path"))
            
            # Create task data for execution agent
            task_data = {
                "task_type": "execute_tests",
                "test_files": test_files,
                "framework": test_creation_results.get("framework", "playwright"),
                "headless": True
            }
            
            # Process task with execution agent
            result = await self.execution_agent.process_task(task_data)
            
            # Save execution results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            execution_results_path = self.work_dir / f"execution_results_{timestamp}.json"
            with open(execution_results_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Execution results created: {execution_results_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Execution agent failed: {str(e)}")
            return {"error": str(e)}
    
    async def _run_reporting_agent(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run the reporting agent"""
        logger.info("Running reporting agent")
        
        try:
            # Create task data for reporting agent
            task_data = {
                "task_type": "generate_report",
                "execution_results": execution_results
            }
            
            # Process task with reporting agent
            result = await self.reporting_agent.process_task(task_data)
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.reports_dir / f"test_report_{timestamp}.html"
            
            if "report_content" in result:
                with open(report_path, 'w') as f:
                    f.write(result["report_content"])
                
                logger.info(f"Report created: {report_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Reporting agent failed: {str(e)}")
            return {"error": str(e)}

async def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Real Multi-Agent Workflow")
    parser.add_argument("--url", "-u", required=True, help="URL of the application to test")
    parser.add_argument("--name", "-n", required=True, help="Name of the application")
    args = parser.parse_args()
    
    # Create workflow
    workflow = RealMultiAgentWorkflow()
    
    # Run workflow
    workflow_results = await workflow.run_workflow(args.url, args.name)
    
    # Print workflow results
    print("\nWorkflow Results:")
    print(f"Application: {args.name} ({args.url})")
    print("\nTest Plan:")
    print(f"- Scenarios: {len(workflow_results['test_plan'].get('test_scenarios', []))}")
    
    print("\nDiscovery Results:")
    print(f"- Pages: {len(workflow_results['discovery_results'].get('pages', []))}")
    print(f"- Elements: {len(workflow_results['discovery_results'].get('elements', {}))}")
    
    print("\nTest Creation Results:")
    print(f"- Generated Files: {len(workflow_results['test_creation_results'].get('generated_files', []))}")
    print(f"- Framework: {workflow_results['test_creation_results'].get('framework', 'unknown')}")
    
    print("\nExecution Results:")
    print(f"- Status: {workflow_results['execution_results'].get('status', 'unknown')}")
    print(f"- Total Tests: {workflow_results['execution_results'].get('total_tests', 0)}")
    print(f"- Passed Tests: {workflow_results['execution_results'].get('passed_tests', 0)}")
    print(f"- Failed Tests: {workflow_results['execution_results'].get('failed_tests', 0)}")
    
    print("\nReport:")
    print(f"- Report File: {workflow_results['report'].get('report_file', 'unknown')}")
    
    print("\nWorkflow completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())

