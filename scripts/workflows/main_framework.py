"""
Main AutoGen Test Automation Framework
Integrates all components into a unified system
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Add the framework to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings, AgentRole
from parsers.unified_parser import UnifiedTestFileParser
from orchestrator.workflow_orchestrator import WorkflowOrchestrator
from orchestrator.agent_coordinator import AgentCoordinator
from agents.planning_agent import PlanningAgent
from agents.test_creation_agent import TestCreationAgent
from agents.review_agent import ReviewAgent
from agents.execution_agent import ExecutionAgent
from agents.reporting_agent import ReportingAgent


class AutoGenTestFramework:
    """Main AutoGen Test Automation Framework"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the AutoGen Test Framework"""
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger("autogen.framework")
        
        # Configuration
        self.config = config or {}
        
        # Core components
        self.parser = UnifiedTestFileParser()
        self.orchestrator = WorkflowOrchestrator()
        self.coordinator = AgentCoordinator()
        
        # Agents
        self.agents = {}
        
        # Framework status
        self.is_initialized = False
        self.initialization_time = None
        
        self.logger.info("AutoGen Test Framework created")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('autogen_framework.log')
            ]
        )
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the framework and all agents"""
        
        self.logger.info("Initializing AutoGen Test Framework...")
        
        try:
            # Initialize agents
            await self._initialize_agents()
            
            # Register agents with orchestrator and coordinator
            self._register_agents()
            
            # Setup shared resources
            self._setup_shared_resources()
            
            # Mark as initialized
            self.is_initialized = True
            self.initialization_time = datetime.now()
            
            initialization_result = {
                "status": "success",
                "initialized_at": self.initialization_time.isoformat(),
                "agents_initialized": len(self.agents),
                "available_workflows": list(self.orchestrator.get_workflow_templates().keys()),
                "supported_file_formats": self.parser.get_supported_formats()
            }
            
            self.logger.info("AutoGen Test Framework initialized successfully")
            return initialization_result
            
        except Exception as e:
            self.logger.error(f"Failed to initialize framework: {e}")
            raise
    
    async def _initialize_agents(self):
        """Initialize all specialized agents"""
        
        self.logger.info("Initializing specialized agents...")
        
        # Initialize each agent
        self.agents[AgentRole.PLANNING] = PlanningAgent()
        self.agents[AgentRole.TEST_CREATION] = TestCreationAgent()
        self.agents[AgentRole.REVIEW] = ReviewAgent()
        self.agents[AgentRole.EXECUTION] = ExecutionAgent()
        self.agents[AgentRole.REPORTING] = ReportingAgent()
        
        # Initialize each agent
        for role, agent in self.agents.items():
            await agent.initialize()
            self.logger.info(f"Initialized {role.value} agent")
    
    def _register_agents(self):
        """Register agents with orchestrator and coordinator"""
        
        self.logger.info("Registering agents with orchestrator and coordinator...")
        
        for role, agent in self.agents.items():
            # Register with orchestrator
            self.orchestrator.register_agent(role, agent)
            
            # Register with coordinator
            self.coordinator.register_agent(role, agent)
            
            self.logger.debug(f"Registered {role.value} agent")
    
    def _setup_shared_resources(self):
        """Setup shared resources for agents"""
        
        # Add parser as shared resource
        self.coordinator.add_shared_resource("file_parser", self.parser)
        
        # Add configuration as shared resource
        self.coordinator.add_shared_resource("framework_config", self.config)
        
        # Add test data directory
        test_data_dir = self.config.get("test_data_directory", "./test_data")
        self.coordinator.add_shared_resource("test_data_directory", test_data_dir)
        
        self.logger.info("Setup shared resources")
    
    async def process_test_files(
        self,
        file_paths: List[str],
        workflow_template: str = "standard_test_automation",
        workflow_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process test files using the specified workflow"""
        
        if not self.is_initialized:
            raise RuntimeError("Framework not initialized. Call initialize() first.")
        
        if not file_paths:
            raise ValueError("No test files provided")
        
        # Generate workflow name if not provided
        if not workflow_name:
            workflow_name = f"Test Automation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.logger.info(f"Processing {len(file_paths)} test files with workflow: {workflow_template}")
        
        try:
            # Create workflow
            workflow_id = await self.orchestrator.create_workflow(
                workflow_name=workflow_name,
                test_files=file_paths,
                template_name=workflow_template,
                custom_config=self.config
            )
            
            # Execute workflow
            execution_result = await self.orchestrator.execute_workflow(workflow_id)
            
            # Get detailed workflow status
            workflow_status = self.orchestrator.get_workflow_status(workflow_id)
            
            result = {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "template_used": workflow_template,
                "execution_result": execution_result,
                "workflow_status": workflow_status,
                "processed_files": file_paths,
                "processing_completed_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Completed processing test files. Workflow: {workflow_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing test files: {e}")
            raise
    
    async def process_test_directory(
        self,
        directory_path: str,
        workflow_template: str = "standard_test_automation",
        recursive: bool = True
    ) -> Dict[str, Any]:
        """Process all test files in a directory"""
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        self.logger.info(f"Processing test directory: {directory_path}")
        
        # Find all test files
        parsed_files = self.parser.parse_directory(directory_path, recursive=recursive)
        
        if not parsed_files:
            raise ValueError(f"No valid test files found in directory: {directory_path}")
        
        # Extract file paths
        file_paths = [pf.file_path for pf in parsed_files]
        
        # Process using workflow
        workflow_name = f"Directory Processing - {os.path.basename(directory_path)}"
        
        result = await self.process_test_files(
            file_paths=file_paths,
            workflow_template=workflow_template,
            workflow_name=workflow_name
        )
        
        # Add directory-specific information
        result.update({
            "source_directory": directory_path,
            "recursive_search": recursive,
            "files_found": len(file_paths),
            "parsed_files_info": [
                {
                    "file_path": pf.file_path,
                    "format": pf.file_format,
                    "test_name": pf.test_name,
                    "steps_count": len(pf.test_steps),
                    "complexity": pf.metadata.get("complexity_analysis", {}).get("estimated_complexity", "unknown")
                }
                for pf in parsed_files
            ]
        })
        
        return result
    
    async def create_custom_workflow(
        self,
        template_name: str,
        template_config: Dict[str, Any]
    ) -> bool:
        """Create a custom workflow template"""
        
        if not self.is_initialized:
            raise RuntimeError("Framework not initialized. Call initialize() first.")
        
        success = self.orchestrator.create_custom_template(template_name, template_config)
        
        if success:
            self.logger.info(f"Created custom workflow template: {template_name}")
        else:
            self.logger.error(f"Failed to create custom workflow template: {template_name}")
        
        return success
    
    def get_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available workflow templates"""
        return self.orchestrator.get_workflow_templates()
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow"""
        return self.orchestrator.get_workflow_status(workflow_id)
    
    def list_workflows(self, include_history: bool = True) -> List[Dict[str, Any]]:
        """List all workflows"""
        return self.orchestrator.list_workflows(include_history=include_history)
    
    def get_framework_statistics(self) -> Dict[str, Any]:
        """Get comprehensive framework statistics"""
        
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        # Get statistics from components
        orchestrator_stats = self.orchestrator.get_execution_statistics()
        coordinator_stats = self.coordinator.get_coordination_metrics()
        parser_stats = self.parser.get_parsing_statistics()
        
        # Combine into comprehensive statistics
        framework_stats = {
            "framework_status": "initialized",
            "initialized_at": self.initialization_time.isoformat(),
            "uptime_seconds": (datetime.now() - self.initialization_time).total_seconds(),
            "agents_count": len(self.agents),
            "orchestrator_statistics": orchestrator_stats,
            "coordinator_statistics": coordinator_stats,
            "parser_statistics": parser_stats,
            "supported_formats": self.parser.get_supported_formats(),
            "available_templates": list(self.orchestrator.get_workflow_templates().keys())
        }
        
        return framework_stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "issues": []
        }
        
        try:
            # Check framework initialization
            if not self.is_initialized:
                health_status["overall_status"] = "unhealthy"
                health_status["issues"].append("Framework not initialized")
                return health_status
            
            # Check agents
            agent_health = {}
            for role, agent in self.agents.items():
                if hasattr(agent, 'health_check'):
                    agent_status = await agent.health_check()
                    agent_health[role.value] = agent_status
                else:
                    agent_health[role.value] = {"status": "unknown", "message": "No health check available"}
            
            health_status["components"]["agents"] = agent_health
            
            # Check coordinator
            coordinator_health = await self.coordinator.health_check()
            health_status["components"]["coordinator"] = coordinator_health
            
            if coordinator_health["status"] != "healthy":
                health_status["issues"].extend(coordinator_health.get("issues", []))
            
            # Check orchestrator
            orchestrator_stats = self.orchestrator.get_execution_statistics()
            health_status["components"]["orchestrator"] = {
                "status": "healthy",
                "active_workflows": orchestrator_stats.get("active_workflows", 0),
                "total_workflows": orchestrator_stats.get("total_workflows", 0)
            }
            
            # Check parser
            parser_stats = self.parser.get_parsing_statistics()
            health_status["components"]["parser"] = {
                "status": "healthy",
                "success_rate": parser_stats.get("success_rate", 0),
                "total_files_parsed": parser_stats.get("total_files_parsed", 0)
            }
            
            # Determine overall status
            if health_status["issues"]:
                health_status["overall_status"] = "warning"
            
            # Check for critical issues
            critical_issues = [issue for issue in health_status["issues"] if "unhealthy" in issue.lower()]
            if critical_issues:
                health_status["overall_status"] = "unhealthy"
            
        except Exception as e:
            health_status["overall_status"] = "unhealthy"
            health_status["issues"].append(f"Health check failed: {str(e)}")
            self.logger.error(f"Health check error: {e}")
        
        return health_status
    
    async def shutdown(self):
        """Shutdown the framework gracefully"""
        
        self.logger.info("Shutting down AutoGen Test Framework...")
        
        try:
            # Cancel active workflows
            active_workflows = self.orchestrator.list_workflows(include_history=False)
            for workflow in active_workflows:
                if workflow["is_active"]:
                    await self.orchestrator.cancel_workflow(workflow["id"])
            
            # Shutdown agents
            for role, agent in self.agents.items():
                if hasattr(agent, 'shutdown'):
                    await agent.shutdown()
                self.logger.debug(f"Shutdown {role.value} agent")
            
            # Clear registrations
            for role in self.agents.keys():
                self.coordinator.unregister_agent(role)
            
            # Clear resources
            self.coordinator.shared_resources.clear()
            self.coordinator.resource_locks.clear()
            
            self.is_initialized = False
            self.logger.info("AutoGen Test Framework shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise
    
    def generate_sample_files(self, output_directory: str) -> Dict[str, str]:
        """Generate sample test files for demonstration"""
        
        return self.parser.generate_sample_files(output_directory)
    
    async def validate_test_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Validate test files without executing workflows"""
        
        self.logger.info(f"Validating {len(file_paths)} test files")
        
        # Parse files
        parsed_files = []
        for file_path in file_paths:
            try:
                parsed_file = self.parser.parse_file(file_path)
                parsed_files.append(parsed_file)
            except Exception as e:
                self.logger.warning(f"Failed to parse {file_path}: {e}")
        
        # Validate parsed files
        validation_results = self.parser.validate_parsed_files(parsed_files)
        
        return {
            "validation_completed_at": datetime.now().isoformat(),
            "total_files": len(file_paths),
            "successfully_parsed": len(parsed_files),
            "validation_results": validation_results,
            "file_details": [
                {
                    "file_path": pf.file_path,
                    "format": pf.file_format,
                    "test_name": pf.test_name,
                    "valid": len(pf.parsing_errors) == 0,
                    "errors": pf.parsing_errors,
                    "complexity": pf.metadata.get("complexity_analysis", {}).get("estimated_complexity", "unknown")
                }
                for pf in parsed_files
            ]
        }


# Convenience functions for easy usage
async def create_framework(config: Optional[Dict[str, Any]] = None) -> AutoGenTestFramework:
    """Create and initialize an AutoGen Test Framework"""
    
    framework = AutoGenTestFramework(config)
    await framework.initialize()
    return framework


async def process_files(
    file_paths: List[str],
    workflow_template: str = "standard_test_automation",
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Quick function to process test files"""
    
    framework = await create_framework(config)
    
    try:
        result = await framework.process_test_files(file_paths, workflow_template)
        return result
    finally:
        await framework.shutdown()


async def process_directory(
    directory_path: str,
    workflow_template: str = "standard_test_automation",
    recursive: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Quick function to process a test directory"""
    
    framework = await create_framework(config)
    
    try:
        result = await framework.process_test_directory(directory_path, workflow_template, recursive)
        return result
    finally:
        await framework.shutdown()


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Main function for testing the framework"""
        
        print("AutoGen Test Automation Framework - Test Run")
        print("=" * 50)
        
        try:
            # Create framework
            framework = AutoGenTestFramework()
            
            # Initialize
            init_result = await framework.initialize()
            print(f"✅ Framework initialized: {init_result['status']}")
            print(f"   Agents: {init_result['agents_initialized']}")
            print(f"   Workflows: {len(init_result['available_workflows'])}")
            
            # Health check
            health = await framework.health_check()
            print(f"✅ Health check: {health['overall_status']}")
            
            # Generate sample files
            samples_dir = "./sample_test_files"
            os.makedirs(samples_dir, exist_ok=True)
            sample_files = framework.generate_sample_files(samples_dir)
            print(f"✅ Generated sample files: {list(sample_files.keys())}")
            
            # Validate sample files
            file_paths = list(sample_files.values())
            validation = await framework.validate_test_files(file_paths)
            print(f"✅ Validation completed: {validation['validation_results']['overall_status']}")
            
            # Get statistics
            stats = framework.get_framework_statistics()
            print(f"✅ Framework statistics collected")
            print(f"   Uptime: {stats['uptime_seconds']:.1f} seconds")
            
            # Shutdown
            await framework.shutdown()
            print("✅ Framework shutdown complete")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Run the test
    asyncio.run(main())

