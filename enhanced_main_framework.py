#!/usr/bin/env python3
"""
Enhanced AutoGen Test Automation Framework with Local AI Integration
Supports both external and local AI models for enterprise deployment
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

# Framework imports
from config.settings import settings, AgentRole
from models.local_ai_provider import LocalAIProvider, ModelType
from agents.base_agent import BaseTestAgent
from agents.planning_agent import PlanningAgent
from agents.test_creation_agent import TestCreationAgent
from parsers.unified_parser import UnifiedTestFileParser
from orchestrator.workflow_orchestrator import WorkflowOrchestrator
from orchestrator.agent_coordinator import AgentCoordinator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedAutoGenFramework:
    """
    Enhanced AutoGen Test Automation Framework
    
    Key Features:
    - Local AI model integration via Ollama
    - Multi-agent coordination with AutoGen
    - Plain English test scenario parsing (.txt/.json)
    - Enterprise-grade security and privacy
    - Hybrid deployment (local + external AI)
    """
    
    def __init__(self, use_local_ai: bool = True):
        """
        Initialize the enhanced framework
        
        Args:
            use_local_ai: Whether to use local AI models (default: True)
        """
        self.use_local_ai = use_local_ai
        self.local_ai_provider = None
        self.agents = {}
        self.orchestrator = None
        self.coordinator = None
        self.parser = UnifiedTestFileParser()
        
        # Framework state
        self.state = {
            "initialized": False,
            "local_ai_available": False,
            "agents_created": 0,
            "scenarios_processed": 0,
            "last_activity": datetime.now()
        }
        
        logger.info("Enhanced AutoGen Framework initialized")
    
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize the framework with all components
        
        Returns:
            Initialization status and configuration
        """
        logger.info("Initializing Enhanced AutoGen Framework...")
        
        # Initialize local AI provider if requested
        if self.use_local_ai:
            self.local_ai_provider = LocalAIProvider()
            self.state["local_ai_available"] = self.local_ai_provider.is_available()
            
            if self.state["local_ai_available"]:
                logger.info("✅ Local AI models available - Enterprise mode enabled")
            else:
                logger.warning("⚠️ Local AI models not available - Falling back to external LLMs")
        else:
            logger.info("Using external LLM providers only")
        
        # Create specialized agents
        await self._create_agents()
        
        # Initialize orchestration components
        self.orchestrator = WorkflowOrchestrator()
        self.coordinator = AgentCoordinator()
        
        # Register agents with coordinator
        for agent_name, agent in self.agents.items():
            self.coordinator.register_agent(agent_name, agent)
        
        self.state["initialized"] = True
        self.state["last_activity"] = datetime.now()
        
        initialization_report = {
            "status": "success",
            "local_ai_enabled": self.use_local_ai,
            "local_ai_available": self.state["local_ai_available"],
            "agents_created": len(self.agents),
            "agent_list": list(self.agents.keys()),
            "local_ai_models": self.local_ai_provider.get_all_model_info() if self.local_ai_provider else None,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Framework initialized successfully with {len(self.agents)} agents")
        return initialization_report
    
    async def _create_agents(self):
        """Create specialized agents with local AI integration"""
        logger.info("Creating specialized agents...")
        
        # Planning Agent - Strategic test planning and analysis
        self.agents["planning"] = PlanningAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        # Test Creation Agent - Generate test automation code
        self.agents["test_creation"] = TestCreationAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        # Review Agent - Code review and quality assurance
        self.agents["review"] = PlanningAgent(
            local_ai_provider=self.local_ai_provider,
            name="review_agent"
        )
        
        # Execution Agent - Test execution and monitoring
        self.agents["execution"] = TestCreationAgent(
            local_ai_provider=self.local_ai_provider,
            name="execution_agent"
        )
        
        # Reporting Agent - Generate comprehensive reports
        self.agents["reporting"] = PlanningAgent(
            local_ai_provider=self.local_ai_provider,
            name="reporting_agent"
        )
        
        self.state["agents_created"] = len(self.agents)
        logger.info(f"✅ Created {len(self.agents)} specialized agents")
    
    async def process_scenario_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a test scenario file (.txt or .json)
        
        Args:
            file_path: Path to the scenario file
            
        Returns:
            Processing results and generated tests
        """
        if not self.state["initialized"]:
            raise RuntimeError("Framework not initialized. Call initialize() first.")
        
        logger.info(f"Processing scenario file: {file_path}")
        
        try:
            # Parse the scenario file
            parsed_scenarios = self.parser.parse_file(file_path)
            
            if not parsed_scenarios["success"]:
                return {
                    "success": False,
                    "error": f"Failed to parse scenario file: {parsed_scenarios.get('error')}",
                    "file_path": file_path
                }
            
            results = []
            
            # Process each scenario
            for scenario in parsed_scenarios["scenarios"]:
                logger.info(f"Processing scenario: {scenario.get('name', 'Unnamed')}")
                
                # Create workflow for this scenario
                workflow_result = await self._create_scenario_workflow(scenario)
                results.append(workflow_result)
            
            self.state["scenarios_processed"] += len(parsed_scenarios["scenarios"])
            self.state["last_activity"] = datetime.now()
            
            return {
                "success": True,
                "file_path": file_path,
                "scenarios_processed": len(parsed_scenarios["scenarios"]),
                "results": results,
                "parsing_info": parsed_scenarios.get("parsing_info", {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing scenario file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _create_scenario_workflow(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and execute a workflow for a single scenario
        
        Args:
            scenario: Parsed scenario data
            
        Returns:
            Workflow execution results
        """
        scenario_name = scenario.get("name", "Unnamed Scenario")
        logger.info(f"Creating workflow for scenario: {scenario_name}")
        
        try:
            # Step 1: Planning Agent analyzes the scenario
            planning_prompt = f"""
            Analyze this test scenario and create a comprehensive test strategy:
            
            Scenario: {scenario_name}
            Description: {scenario.get('description', 'No description provided')}
            Test Steps: {json.dumps(scenario.get('test_steps', []), indent=2)}
            Target Application: {scenario.get('application', 'Not specified')}
            
            Provide:
            1. Test strategy and approach
            2. Risk assessment
            3. Required test data and setup
            4. Success criteria
            5. Potential challenges and mitigation
            """
            
            planning_result = await self._execute_agent_task("planning", planning_prompt)
            
            # Step 2: Test Creation Agent generates test code
            if planning_result["success"]:
                creation_prompt = f"""
                Based on this test strategy, generate complete test automation code:
                
                Test Strategy:
                {planning_result['response']}
                
                Original Scenario:
                {json.dumps(scenario, indent=2)}
                
                Generate:
                1. Complete test automation code (Python/Playwright)
                2. Test data setup
                3. Configuration files
                4. Documentation
                """
                
                creation_result = await self._execute_agent_task("test_creation", creation_prompt)
            else:
                creation_result = {"success": False, "error": "Planning failed"}
            
            # Step 3: Review Agent validates the generated code
            if creation_result["success"]:
                review_prompt = f"""
                Review this generated test code for quality and completeness:
                
                Generated Code:
                {creation_result['response']}
                
                Original Requirements:
                {json.dumps(scenario, indent=2)}
                
                Provide:
                1. Code quality assessment
                2. Completeness check
                3. Best practices compliance
                4. Improvement suggestions
                5. Approval/rejection recommendation
                """
                
                review_result = await self._execute_agent_task("review", review_prompt)
            else:
                review_result = {"success": False, "error": "Test creation failed"}
            
            # Compile workflow results
            workflow_result = {
                "scenario_name": scenario_name,
                "success": all([
                    planning_result["success"],
                    creation_result["success"],
                    review_result["success"]
                ]),
                "planning": planning_result,
                "test_creation": creation_result,
                "review": review_result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save artifacts if successful
            if workflow_result["success"]:
                await self._save_scenario_artifacts(scenario_name, workflow_result)
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"Error in scenario workflow for {scenario_name}: {e}")
            return {
                "scenario_name": scenario_name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_agent_task(self, agent_name: str, prompt: str) -> Dict[str, Any]:
        """
        Execute a task using a specific agent
        
        Args:
            agent_name: Name of the agent to use
            prompt: Task prompt
            
        Returns:
            Agent execution results
        """
        if agent_name not in self.agents:
            return {
                "success": False,
                "error": f"Agent {agent_name} not found"
            }
        
        agent = self.agents[agent_name]
        
        try:
            # Use local AI if available, otherwise fall back to AutoGen
            if agent.use_local_ai:
                result = agent.generate_local_ai_response(prompt)
                return result
            else:
                # Use AutoGen conversation (external LLM)
                # This would integrate with AutoGen's conversation system
                # For now, return a placeholder
                return {
                    "success": False,
                    "error": "External LLM integration not implemented in this demo",
                    "note": "In production, this would use AutoGen's conversation system"
                }
                
        except Exception as e:
            logger.error(f"Error executing task with agent {agent_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _save_scenario_artifacts(self, scenario_name: str, workflow_result: Dict[str, Any]):
        """Save generated artifacts for a scenario"""
        try:
            # Create output directory
            output_dir = f"./generated_tests/{scenario_name.replace(' ', '_').lower()}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save planning document
            if workflow_result["planning"]["success"]:
                planning_file = os.path.join(output_dir, "test_strategy.md")
                with open(planning_file, 'w') as f:
                    f.write(workflow_result["planning"]["response"])
            
            # Save generated test code
            if workflow_result["test_creation"]["success"]:
                test_file = os.path.join(output_dir, "test_automation.py")
                with open(test_file, 'w') as f:
                    f.write(workflow_result["test_creation"]["response"])
            
            # Save review report
            if workflow_result["review"]["success"]:
                review_file = os.path.join(output_dir, "code_review.md")
                with open(review_file, 'w') as f:
                    f.write(workflow_result["review"]["response"])
            
            # Save complete workflow results
            results_file = os.path.join(output_dir, "workflow_results.json")
            with open(results_file, 'w') as f:
                json.dump(workflow_result, f, indent=2, default=str)
            
            logger.info(f"✅ Saved artifacts for scenario: {scenario_name}")
            
        except Exception as e:
            logger.error(f"Error saving artifacts for {scenario_name}: {e}")
    
    def get_framework_status(self) -> Dict[str, Any]:
        """Get comprehensive framework status"""
        agent_statuses = {}
        for name, agent in self.agents.items():
            agent_statuses[name] = agent.get_local_ai_status()
        
        return {
            "framework_initialized": self.state["initialized"],
            "local_ai_enabled": self.use_local_ai,
            "local_ai_available": self.state["local_ai_available"],
            "agents_created": self.state["agents_created"],
            "scenarios_processed": self.state["scenarios_processed"],
            "last_activity": self.state["last_activity"].isoformat(),
            "agent_statuses": agent_statuses,
            "local_ai_provider_status": self.local_ai_provider.get_status_report() if self.local_ai_provider else None
        }
    
    async def run_demo(self):
        """Run a demonstration of the enhanced framework"""
        logger.info("🚀 Starting Enhanced AutoGen Framework Demo")
        
        # Initialize framework
        init_result = await self.initialize()
        print(f"\n📋 Initialization Result:")
        print(json.dumps(init_result, indent=2, default=str))
        
        # Check if we have sample scenario files
        sample_files = [
            "./test_samples/complete_shopping_workflow.txt",
            "./test_samples/simple_login_test.txt"
        ]
        
        for sample_file in sample_files:
            if os.path.exists(sample_file):
                logger.info(f"\n🧪 Processing sample scenario: {sample_file}")
                result = await self.process_scenario_file(sample_file)
                print(f"\n📊 Scenario Processing Result:")
                print(json.dumps(result, indent=2, default=str))
            else:
                logger.info(f"Sample file not found: {sample_file}")
        
        # Show final status
        status = self.get_framework_status()
        print(f"\n📈 Final Framework Status:")
        print(json.dumps(status, indent=2, default=str))
        
        logger.info("✅ Demo completed successfully!")

# Main execution
async def main():
    """Main function to run the enhanced framework"""
    framework = EnhancedAutoGenFramework(use_local_ai=True)
    await framework.run_demo()

if __name__ == "__main__":
    asyncio.run(main())

