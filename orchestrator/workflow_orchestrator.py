"""
Workflow Orchestrator for AutoGen Test Automation Framework
Manages complex multi-agent workflows and coordination

Key Features:
- Workflow step execution with dependency management
- Review-refinement loops for iterative test improvement
- Self-healing integration for automatic test repair
- Message-based agent coordination via AgentMessageBus
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import uuid

from config.settings import settings, AgentRole
from parsers.unified_parser import UnifiedTestFileParser, ParsedTestFile

# Import message protocol for agent communication
from .agent_protocol import (
    AgentMessageBus,
    AgentMessage,
    MessageType,
    MessagePriority,
    ReviewFeedback,
    HealingRequest,
    create_review_request,
    create_review_feedback,
    create_healing_request,
    create_task_request,
    create_status_update,
)


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepStatus(str, Enum):
    """Individual workflow step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Represents a single workflow step"""
    id: str
    name: str
    agent_role: AgentRole
    task_type: str
    dependencies: List[str]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    status: WorkflowStepStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowExecution:
    """Represents a complete workflow execution"""
    id: str
    name: str
    description: str
    test_files: List[str]
    steps: List[WorkflowStep]
    status: WorkflowStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration: Optional[timedelta] = None
    success_rate: float = 0.0
    metadata: Dict[str, Any] = None


class WorkflowOrchestrator:
    """Orchestrates complex multi-agent workflows for test automation"""

    def __init__(self):
        self.logger = logging.getLogger("orchestrator.workflow")
        self.parser = UnifiedTestFileParser()

        # Workflow management
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.workflow_history: List[WorkflowExecution] = []

        # Agent management
        self.available_agents: Dict[AgentRole, Any] = {}
        self.agent_workloads: Dict[AgentRole, int] = {}

        # Message bus for agent communication
        self.message_bus = AgentMessageBus()

        # Review-refinement configuration
        self.review_config = {
            "min_approval_score": 7.0,  # Minimum score (1-10) to pass review
            "max_refinement_iterations": 3,  # Maximum refinement attempts
            "require_all_issues_resolved": False,  # Must all issues be resolved
            "auto_approve_score": 9.0,  # Score to auto-approve without changes
        }

        # Self-healing configuration
        self.healing_config = {
            "enabled": True,
            "max_healing_attempts": 3,
            "auto_heal_selector_errors": True,
            "auto_heal_timeout_errors": True,
        }

        # Workflow templates
        self.workflow_templates = self._initialize_workflow_templates()

        # Execution statistics
        self.execution_stats = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_duration": 0.0,
            "agent_utilization": {},
            "refinement_stats": {
                "total_refinements": 0,
                "successful_refinements": 0,
                "average_iterations": 0.0,
            },
            "healing_stats": {
                "total_healing_requests": 0,
                "successful_heals": 0,
                "selector_fixes": 0,
                "timeout_fixes": 0,
            },
        }
    
    def _initialize_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined workflow templates"""
        return {
            "standard_test_automation": {
                "name": "Standard Test Automation Workflow",
                "description": "Complete test automation workflow from planning to reporting",
                "steps": [
                    {
                        "id": "parse_requirements",
                        "name": "Parse Test Requirements",
                        "agent_role": AgentRole.ORCHESTRATOR,
                        "task_type": "parse_files",
                        "dependencies": []
                    },
                    {
                        "id": "create_test_plan",
                        "name": "Create Test Plan",
                        "agent_role": AgentRole.PLANNING,
                        "task_type": "create_plan",
                        "dependencies": ["parse_requirements"]
                    },
                    {
                        "id": "generate_tests",
                        "name": "Generate Test Code",
                        "agent_role": AgentRole.TEST_CREATION,
                        "task_type": "generate_tests",
                        "dependencies": ["create_test_plan"]
                    },
                    {
                        "id": "review_tests",
                        "name": "Review Generated Tests",
                        "agent_role": AgentRole.REVIEW,
                        "task_type": "review_code",
                        "dependencies": ["generate_tests"]
                    },
                    {
                        "id": "execute_tests",
                        "name": "Execute Tests",
                        "agent_role": AgentRole.EXECUTION,
                        "task_type": "execute_tests",
                        "dependencies": ["review_tests"]
                    },
                    {
                        "id": "generate_report",
                        "name": "Generate Test Report",
                        "agent_role": AgentRole.REPORTING,
                        "task_type": "generate_report",
                        "dependencies": ["execute_tests"]
                    }
                ]
            },
            "quick_test_generation": {
                "name": "Quick Test Generation Workflow",
                "description": "Rapid test generation without full review cycle",
                "steps": [
                    {
                        "id": "parse_requirements",
                        "name": "Parse Test Requirements",
                        "agent_role": AgentRole.ORCHESTRATOR,
                        "task_type": "parse_files",
                        "dependencies": []
                    },
                    {
                        "id": "generate_tests",
                        "name": "Generate Test Code",
                        "agent_role": AgentRole.TEST_CREATION,
                        "task_type": "generate_tests",
                        "dependencies": ["parse_requirements"]
                    },
                    {
                        "id": "execute_tests",
                        "name": "Execute Tests",
                        "agent_role": AgentRole.EXECUTION,
                        "task_type": "execute_tests",
                        "dependencies": ["generate_tests"]
                    }
                ]
            },
            "comprehensive_quality_analysis": {
                "name": "Comprehensive Quality Analysis Workflow",
                "description": "Deep quality analysis with strategic insights",
                "steps": [
                    {
                        "id": "parse_requirements",
                        "name": "Parse Test Requirements",
                        "agent_role": AgentRole.ORCHESTRATOR,
                        "task_type": "parse_files",
                        "dependencies": []
                    },
                    {
                        "id": "analyze_requirements",
                        "name": "Analyze Requirements",
                        "agent_role": AgentRole.PLANNING,
                        "task_type": "analyze_requirements",
                        "dependencies": ["parse_requirements"]
                    },
                    {
                        "id": "create_comprehensive_plan",
                        "name": "Create Comprehensive Test Plan",
                        "agent_role": AgentRole.PLANNING,
                        "task_type": "create_plan",
                        "dependencies": ["analyze_requirements"]
                    },
                    {
                        "id": "generate_tests",
                        "name": "Generate Test Code",
                        "agent_role": AgentRole.TEST_CREATION,
                        "task_type": "generate_tests",
                        "dependencies": ["create_comprehensive_plan"]
                    },
                    {
                        "id": "comprehensive_review",
                        "name": "Comprehensive Code Review",
                        "agent_role": AgentRole.REVIEW,
                        "task_type": "comprehensive_review",
                        "dependencies": ["generate_tests"]
                    },
                    {
                        "id": "execute_tests",
                        "name": "Execute Tests",
                        "agent_role": AgentRole.EXECUTION,
                        "task_type": "execute_tests",
                        "dependencies": ["comprehensive_review"]
                    },
                    {
                        "id": "quality_analysis",
                        "name": "Quality Analysis",
                        "agent_role": AgentRole.REPORTING,
                        "task_type": "quality_analysis",
                        "dependencies": ["execute_tests"]
                    },
                    {
                        "id": "strategic_insights",
                        "name": "Generate Strategic Insights",
                        "agent_role": AgentRole.REPORTING,
                        "task_type": "strategic_insights",
                        "dependencies": ["quality_analysis"]
                    }
                ]
            },
            "iterative_test_generation": {
                "name": "Iterative Test Generation with Review-Refinement",
                "description": "AI-powered test generation with iterative review and refinement loops",
                "steps": [
                    {
                        "id": "discover_application",
                        "name": "Discover Application Elements",
                        "agent_role": AgentRole.DISCOVERY,
                        "task_type": "discover_elements",
                        "dependencies": []
                    },
                    {
                        "id": "analyze_and_plan",
                        "name": "Analyze and Create Test Plan",
                        "agent_role": AgentRole.PLANNING,
                        "task_type": "create_plan_with_discovery",
                        "dependencies": ["discover_application"]
                    },
                    {
                        "id": "generate_tests",
                        "name": "Generate Test Code",
                        "agent_role": AgentRole.TEST_CREATION,
                        "task_type": "generate_tests",
                        "dependencies": ["analyze_and_plan"]
                    },
                    {
                        "id": "review_and_refine",
                        "name": "Review and Refine Tests",
                        "agent_role": AgentRole.ORCHESTRATOR,
                        "task_type": "review_refinement_loop",
                        "dependencies": ["generate_tests"]
                    },
                    {
                        "id": "execute_tests",
                        "name": "Execute Tests with Self-Healing",
                        "agent_role": AgentRole.EXECUTION,
                        "task_type": "execute_with_healing",
                        "dependencies": ["review_and_refine"]
                    },
                    {
                        "id": "generate_report",
                        "name": "Generate Comprehensive Report",
                        "agent_role": AgentRole.REPORTING,
                        "task_type": "generate_report",
                        "dependencies": ["execute_tests"]
                    }
                ],
                "config": {
                    "enable_refinement_loop": True,
                    "enable_self_healing": True,
                    "max_refinement_iterations": 3,
                    "min_approval_score": 7.0
                }
            }
        }
    
    async def create_workflow(
        self,
        workflow_name: str,
        test_files: List[str],
        template_name: str = "standard_test_automation",
        custom_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new workflow execution"""
        
        workflow_id = str(uuid.uuid4())
        
        self.logger.info(f"Creating workflow {workflow_id}: {workflow_name}")
        
        try:
            # Get workflow template
            template = self.workflow_templates.get(template_name)
            if not template:
                raise ValueError(f"Unknown workflow template: {template_name}")
            
            # Create workflow steps
            steps = []
            for step_template in template["steps"]:
                step = WorkflowStep(
                    id=step_template["id"],
                    name=step_template["name"],
                    agent_role=AgentRole(step_template["agent_role"]),
                    task_type=step_template["task_type"],
                    dependencies=step_template["dependencies"],
                    input_data={},
                    output_data={},
                    status=WorkflowStepStatus.PENDING,
                    max_retries=custom_config.get("max_retries", 3) if custom_config else 3
                )
                steps.append(step)
            
            # Create workflow execution
            workflow = WorkflowExecution(
                id=workflow_id,
                name=workflow_name,
                description=template["description"],
                test_files=test_files,
                steps=steps,
                status=WorkflowStatus.PENDING,
                created_at=datetime.now(),
                metadata=custom_config or {}
            )
            
            # Store workflow
            self.active_workflows[workflow_id] = workflow
            
            self.logger.info(f"Created workflow {workflow_id} with {len(steps)} steps")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Error creating workflow: {e}")
            raise
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow"""
        
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        
        self.logger.info(f"Starting execution of workflow {workflow_id}: {workflow.name}")
        
        try:
            # Update workflow status
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.now()
            
            # Execute workflow steps
            execution_result = await self._execute_workflow_steps(workflow)
            
            # Update final status
            if execution_result["success"]:
                workflow.status = WorkflowStatus.COMPLETED
                workflow.success_rate = execution_result["success_rate"]
            else:
                workflow.status = WorkflowStatus.FAILED
            
            workflow.completed_at = datetime.now()
            workflow.total_duration = workflow.completed_at - workflow.started_at
            
            # Move to history
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            # Update statistics
            self._update_execution_stats(workflow)
            
            self.logger.info(f"Completed workflow {workflow_id} with status {workflow.status}")
            
            return {
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "success_rate": workflow.success_rate,
                "duration": workflow.total_duration.total_seconds() if workflow.total_duration else 0,
                "results": execution_result
            }
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            if workflow.started_at:
                workflow.total_duration = workflow.completed_at - workflow.started_at
            
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
            raise
    
    async def _execute_workflow_steps(self, workflow: WorkflowExecution) -> Dict[str, Any]:
        """Execute all steps in a workflow"""
        
        completed_steps = set()
        failed_steps = set()
        step_results = {}
        
        # Create dependency graph
        dependency_graph = {step.id: step.dependencies for step in workflow.steps}
        step_map = {step.id: step for step in workflow.steps}
        
        while len(completed_steps) + len(failed_steps) < len(workflow.steps):
            # Find steps ready to execute
            ready_steps = []
            for step in workflow.steps:
                if (step.id not in completed_steps and 
                    step.id not in failed_steps and
                    step.status == WorkflowStepStatus.PENDING and
                    all(dep in completed_steps for dep in step.dependencies)):
                    ready_steps.append(step)
            
            if not ready_steps:
                # Check if we're stuck due to failed dependencies
                remaining_steps = [s for s in workflow.steps 
                                 if s.id not in completed_steps and s.id not in failed_steps]
                if remaining_steps:
                    self.logger.warning(f"Workflow stuck - {len(remaining_steps)} steps cannot execute due to failed dependencies")
                    for step in remaining_steps:
                        step.status = WorkflowStepStatus.SKIPPED
                        failed_steps.add(step.id)
                break
            
            # Execute ready steps (can be parallel)
            step_tasks = []
            for step in ready_steps:
                task = self._execute_workflow_step(step, step_results)
                step_tasks.append(task)
            
            # Wait for all ready steps to complete
            results = await asyncio.gather(*step_tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                step = ready_steps[i]
                if isinstance(result, Exception):
                    self.logger.error(f"Step {step.id} failed: {result}")
                    step.status = WorkflowStepStatus.FAILED
                    step.error_message = str(result)
                    failed_steps.add(step.id)
                else:
                    step.status = WorkflowStepStatus.COMPLETED
                    step.output_data = result
                    step_results[step.id] = result
                    completed_steps.add(step.id)
        
        # Calculate success metrics
        total_steps = len(workflow.steps)
        successful_steps = len(completed_steps)
        success_rate = successful_steps / total_steps if total_steps > 0 else 0
        
        return {
            "success": len(failed_steps) == 0,
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "failed_steps": len(failed_steps),
            "success_rate": success_rate,
            "step_results": step_results,
            "completed_steps": list(completed_steps),
            "failed_steps": list(failed_steps)
        }
    
    async def _execute_workflow_step(self, step: WorkflowStep, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        
        self.logger.info(f"Executing step {step.id}: {step.name}")
        
        step.status = WorkflowStepStatus.RUNNING
        step.started_at = datetime.now()
        
        try:
            # Prepare input data
            input_data = step.input_data.copy()
            
            # Add results from dependency steps
            for dep_id in step.dependencies:
                if dep_id in previous_results:
                    input_data[f"{dep_id}_result"] = previous_results[dep_id]
            
            # Get appropriate agent
            agent = self.available_agents.get(step.agent_role)
            if not agent:
                raise ValueError(f"No agent available for role {step.agent_role}")
            
            # Execute the step based on task type
            if step.task_type == "parse_files":
                result = await self._execute_parse_files_task(input_data)
            elif step.task_type == "create_plan":
                result = await agent.process_task({
                    "type": "create_plan",
                    **input_data
                })
            elif step.task_type == "generate_tests":
                result = await agent.process_task({
                    "type": "generate_tests",
                    **input_data
                })
            elif step.task_type == "review_code":
                result = await agent.process_task({
                    "type": "review_code",
                    **input_data
                })
            elif step.task_type == "execute_tests":
                result = await agent.process_task({
                    "type": "execute_tests",
                    **input_data
                })
            elif step.task_type == "generate_report":
                result = await agent.process_task({
                    "type": "generate_report",
                    **input_data
                })
            elif step.task_type == "review_refinement_loop":
                # Special handling for review-refinement loop
                result = await self._execute_review_refinement_loop(input_data)
            elif step.task_type == "execute_with_healing":
                # Special handling for execution with self-healing
                result = await self._execute_with_self_healing(input_data)
            elif step.task_type == "discover_elements":
                result = await agent.process_task({
                    "type": "discover",
                    **input_data
                })
            elif step.task_type == "create_plan_with_discovery":
                result = await agent.process_task({
                    "type": "create_plan",
                    "use_discovery_data": True,
                    **input_data
                })
            else:
                result = await agent.process_task({
                    "type": step.task_type,
                    **input_data
                })
            
            step.completed_at = datetime.now()
            
            self.logger.info(f"Completed step {step.id} successfully")
            return result
            
        except Exception as e:
            step.completed_at = datetime.now()
            step.error_message = str(e)
            
            # Retry logic
            if step.retry_count < step.max_retries:
                step.retry_count += 1
                self.logger.warning(f"Step {step.id} failed, retrying ({step.retry_count}/{step.max_retries})")
                await asyncio.sleep(2 ** step.retry_count)  # Exponential backoff
                return await self._execute_workflow_step(step, previous_results)
            
            self.logger.error(f"Step {step.id} failed after {step.retry_count} retries: {e}")
            raise
    
    async def _execute_parse_files_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file parsing task"""
        
        # This is handled by the orchestrator itself
        test_files = input_data.get("test_files", [])
        
        if not test_files:
            # Get test files from workflow
            workflow_id = input_data.get("workflow_id")
            if workflow_id and workflow_id in self.active_workflows:
                test_files = self.active_workflows[workflow_id].test_files
        
        if not test_files:
            raise ValueError("No test files provided for parsing")
        
        # Parse all test files
        parsed_files = []
        for file_path in test_files:
            try:
                parsed_file = self.parser.parse_file(file_path)
                parsed_files.append(parsed_file)
            except Exception as e:
                self.logger.warning(f"Failed to parse file {file_path}: {e}")
        
        if not parsed_files:
            raise ValueError("No files were successfully parsed")
        
        # Validate parsed files
        validation_results = self.parser.validate_parsed_files(parsed_files)
        
        return {
            "status": "success",
            "parsed_files": parsed_files,
            "validation_results": validation_results,
            "total_files": len(test_files),
            "successfully_parsed": len(parsed_files)
        }

    # ==========================================
    # Review-Refinement Loop Implementation
    # ==========================================

    async def _execute_review_refinement_loop(
        self, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the review-refinement loop for iterative test improvement.

        This method:
        1. Sends generated tests to ReviewAgent for review
        2. If review score < threshold, sends feedback to TestCreationAgent
        3. TestCreationAgent refines tests based on feedback
        4. Loop continues until approval or max iterations reached

        Args:
            input_data: Contains generated tests and discovery data

        Returns:
            Final approved tests with review history
        """
        self.logger.info("Starting review-refinement loop")

        # Get configuration
        min_score = self.review_config["min_approval_score"]
        max_iterations = self.review_config["max_refinement_iterations"]
        auto_approve_score = self.review_config["auto_approve_score"]

        # Extract test data from previous step
        generated_tests = input_data.get("generate_tests_result", {})
        discovery_data = input_data.get("discover_application_result", {})
        test_plan = input_data.get("analyze_and_plan_result", {})

        # Track refinement history
        refinement_history = []
        current_tests = generated_tests
        iteration = 0
        approved = False

        while iteration < max_iterations and not approved:
            iteration += 1
            self.logger.info(f"Review-refinement iteration {iteration}/{max_iterations}")

            # Step 1: Send tests to review agent
            review_result = await self._request_review(current_tests, iteration)

            review_score = review_result.get("overall_score", 0)
            issues = review_result.get("review_results", {}).get("reviews", [{}])[0].get("issues", [])
            recommendations = review_result.get("review_results", {}).get("recommendations", [])

            self.logger.info(f"Review score: {review_score}/10, Issues: {len(issues)}")

            # Record this iteration
            refinement_history.append({
                "iteration": iteration,
                "review_score": review_score,
                "issues_count": len(issues),
                "issues": issues,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat(),
            })

            # Step 2: Check if approved
            if review_score >= auto_approve_score:
                self.logger.info(f"Tests auto-approved with score {review_score}")
                approved = True
                break
            elif review_score >= min_score and len(issues) == 0:
                self.logger.info(f"Tests approved with score {review_score}")
                approved = True
                break
            elif iteration >= max_iterations:
                self.logger.warning(
                    f"Max refinement iterations reached. Final score: {review_score}"
                )
                break

            # Step 3: Request refinement from TestCreationAgent
            self.logger.info(f"Requesting refinement based on {len(issues)} issues")

            refinement_feedback = ReviewFeedback(
                approved=False,
                score=review_score / 10.0,  # Normalize to 0-1
                issues=[{"description": issue} for issue in issues],
                suggestions=recommendations,
                requires_changes=True,
                change_requests=[
                    {"type": "fix_issue", "details": issue} for issue in issues
                ],
                review_notes=f"Iteration {iteration}: Score {review_score}/10. Please address the identified issues.",
            )

            current_tests = await self._request_refinement(
                current_tests=current_tests,
                feedback=refinement_feedback,
                discovery_data=discovery_data,
                test_plan=test_plan,
                iteration=iteration,
            )

        # Update statistics
        self.execution_stats["refinement_stats"]["total_refinements"] += 1
        if approved:
            self.execution_stats["refinement_stats"]["successful_refinements"] += 1

        # Update average iterations
        current_avg = self.execution_stats["refinement_stats"]["average_iterations"]
        total = self.execution_stats["refinement_stats"]["total_refinements"]
        self.execution_stats["refinement_stats"]["average_iterations"] = (
            (current_avg * (total - 1) + iteration) / total
        )

        return {
            "status": "approved" if approved else "max_iterations_reached",
            "final_tests": current_tests,
            "final_score": refinement_history[-1]["review_score"] if refinement_history else 0,
            "total_iterations": iteration,
            "refinement_history": refinement_history,
            "approved": approved,
        }

    async def _request_review(
        self, tests: Dict[str, Any], iteration: int
    ) -> Dict[str, Any]:
        """
        Request a review from the ReviewAgent.

        Uses message bus for structured communication if available,
        falls back to direct agent call.
        """
        review_agent = self.available_agents.get(AgentRole.REVIEW)
        if not review_agent:
            raise ValueError("No review agent available")

        # Prepare test files for review
        test_files = tests.get("generated_test_files", [])
        test_code = tests.get("test_code", "")

        # Create review request message
        review_message = create_review_request(
            sender="orchestrator",
            recipient="review_agent",
            items_to_review=[
                {
                    "type": "test_code",
                    "files": test_files,
                    "code": test_code,
                    "iteration": iteration,
                }
            ],
            review_type="test_code_review",
            context={"iteration": iteration, "source": "refinement_loop"},
        )

        # Try message bus first
        if "review_agent" in self.message_bus.message_handlers:
            response = await self.message_bus.send_message(
                review_message, wait_for_response=True, timeout=60.0
            )
            if response and response.payload:
                return response.payload

        # Fallback to direct agent call
        return await review_agent.process_task({
            "type": "review_code",
            "test_files": test_files,
            "test_code": test_code,
            "iteration": iteration,
        })

    async def _request_refinement(
        self,
        current_tests: Dict[str, Any],
        feedback: ReviewFeedback,
        discovery_data: Dict[str, Any],
        test_plan: Dict[str, Any],
        iteration: int,
    ) -> Dict[str, Any]:
        """
        Request test refinement from TestCreationAgent based on review feedback.
        """
        test_creation_agent = self.available_agents.get(AgentRole.TEST_CREATION)
        if not test_creation_agent:
            raise ValueError("No test creation agent available")

        # Create refinement request
        refinement_request = create_task_request(
            sender="orchestrator",
            recipient="test_creation_agent",
            task_type="refine_tests",
            task_data={
                "current_tests": current_tests,
                "feedback": feedback.to_dict(),
                "discovery_data": discovery_data,
                "test_plan": test_plan,
                "iteration": iteration,
            },
            priority=MessagePriority.HIGH,
        )

        # Try message bus first
        if "test_creation_agent" in self.message_bus.message_handlers:
            response = await self.message_bus.send_message(
                refinement_request, wait_for_response=True, timeout=120.0
            )
            if response and response.payload:
                return response.payload.get("refined_tests", current_tests)

        # Fallback to direct agent call
        result = await test_creation_agent.process_task({
            "type": "refine_tests",
            "current_tests": current_tests,
            "feedback": feedback.to_dict(),
            "discovery_data": discovery_data,
            "test_plan": test_plan,
            "iteration": iteration,
        })

        return result.get("refined_tests", result)

    # ==========================================
    # Self-Healing Execution Implementation
    # ==========================================

    async def _execute_with_self_healing(
        self, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tests with automatic self-healing for failures.

        This method:
        1. Executes tests via ExecutionAgent
        2. On selector/timeout failures, invokes SelfHealingAgent
        3. SelfHealingAgent fixes the test using discovery data
        4. Re-executes the fixed test
        5. Continues until all tests pass or max attempts reached

        Args:
            input_data: Contains approved tests and discovery data

        Returns:
            Execution results with healing history
        """
        if not self.healing_config["enabled"]:
            # Self-healing disabled, run normal execution
            return await self._execute_tests_normal(input_data)

        self.logger.info("Starting test execution with self-healing")

        # Get agents
        execution_agent = self.available_agents.get(AgentRole.EXECUTION)
        healing_agent = self.available_agents.get(AgentRole.SELF_HEALING)

        if not execution_agent:
            raise ValueError("No execution agent available")

        # Extract test data
        approved_tests = input_data.get("review_and_refine_result", {})
        final_tests = approved_tests.get("final_tests", {})
        discovery_data = input_data.get("discover_application_result", {})

        max_attempts = self.healing_config["max_healing_attempts"]
        healing_history = []
        execution_results = []

        # Get list of test files to execute
        test_files = final_tests.get("generated_test_files", [])

        for test_file in test_files:
            attempt = 0
            test_passed = False
            current_test = test_file

            while attempt < max_attempts and not test_passed:
                attempt += 1
                self.logger.info(f"Executing test {test_file}, attempt {attempt}/{max_attempts}")

                # Execute the test
                result = await execution_agent.process_task({
                    "type": "execute_single_test",
                    "test_file": current_test,
                    "attempt": attempt,
                })

                execution_results.append({
                    "test_file": current_test,
                    "attempt": attempt,
                    "result": result,
                })

                if result.get("status") == "passed":
                    test_passed = True
                    self.logger.info(f"Test {test_file} passed on attempt {attempt}")
                    break

                # Check if we can heal this error
                error_type = result.get("error_type", "")
                error_message = result.get("error_message", "")

                can_heal = self._can_heal_error(error_type)

                if not can_heal or not healing_agent or attempt >= max_attempts:
                    self.logger.warning(
                        f"Cannot heal error for {test_file}: {error_type}"
                    )
                    break

                # Request healing
                self.logger.info(f"Requesting healing for {test_file}: {error_type}")

                healing_request = HealingRequest(
                    test_file_path=current_test,
                    error_type=error_type,
                    error_message=error_message,
                    stack_trace=result.get("stack_trace", ""),
                    failed_selector=result.get("failed_selector"),
                    discovery_data=discovery_data,
                    max_attempts=max_attempts,
                    current_attempt=attempt,
                )

                healing_result = await self._request_healing(healing_request)

                healing_history.append({
                    "test_file": test_file,
                    "attempt": attempt,
                    "error_type": error_type,
                    "healing_result": healing_result,
                    "timestamp": datetime.now().isoformat(),
                })

                if healing_result.get("status") == "healed":
                    current_test = healing_result.get("healed_test_file", current_test)
                    self._update_healing_stats(error_type, success=True)
                else:
                    self._update_healing_stats(error_type, success=False)
                    break

        # Calculate final results
        total_tests = len(test_files)
        passed_tests = sum(
            1 for r in execution_results
            if r["result"].get("status") == "passed"
        )

        return {
            "status": "completed",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "execution_results": execution_results,
            "healing_history": healing_history,
            "healing_attempts": len(healing_history),
        }

    def _can_heal_error(self, error_type: str) -> bool:
        """Check if an error type can be healed automatically."""
        healable_selector_errors = [
            "element_not_found",
            "selector_timeout",
            "stale_element",
            "element_not_visible",
            "element_not_interactable",
        ]
        healable_timeout_errors = [
            "timeout",
            "navigation_timeout",
            "wait_timeout",
        ]

        error_lower = error_type.lower()

        if self.healing_config["auto_heal_selector_errors"]:
            if any(err in error_lower for err in healable_selector_errors):
                return True

        if self.healing_config["auto_heal_timeout_errors"]:
            if any(err in error_lower for err in healable_timeout_errors):
                return True

        return False

    async def _request_healing(
        self, healing_request: HealingRequest
    ) -> Dict[str, Any]:
        """
        Request test healing from SelfHealingAgent.
        """
        healing_agent = self.available_agents.get(AgentRole.SELF_HEALING)
        if not healing_agent:
            return {"status": "no_healing_agent", "healed": False}

        # Create healing message
        healing_message = create_healing_request(
            sender="orchestrator",
            recipient="self_healing_agent",
            request=healing_request,
        )

        # Try message bus first
        if "self_healing_agent" in self.message_bus.message_handlers:
            response = await self.message_bus.send_message(
                healing_message, wait_for_response=True, timeout=60.0
            )
            if response and response.payload:
                return response.payload

        # Fallback to direct agent call
        return await healing_agent.process_task({
            "type": "heal_test",
            **healing_request.to_dict(),
        })

    async def _execute_tests_normal(
        self, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute tests without self-healing (fallback)."""
        execution_agent = self.available_agents.get(AgentRole.EXECUTION)
        if not execution_agent:
            raise ValueError("No execution agent available")

        approved_tests = input_data.get("review_and_refine_result", {})
        final_tests = approved_tests.get("final_tests", {})

        return await execution_agent.process_task({
            "type": "execute_tests",
            "test_files": final_tests.get("generated_test_files", []),
        })

    def _update_healing_stats(self, error_type: str, success: bool):
        """Update healing statistics."""
        stats = self.execution_stats["healing_stats"]
        stats["total_healing_requests"] += 1

        if success:
            stats["successful_heals"] += 1

        error_lower = error_type.lower()
        if "selector" in error_lower or "element" in error_lower:
            stats["selector_fixes"] += 1 if success else 0
        elif "timeout" in error_lower:
            stats["timeout_fixes"] += 1 if success else 0

    # ==========================================
    # Agent Registration with Message Bus
    # ==========================================

    def register_agent(self, agent_role: AgentRole, agent_instance: Any):
        """Register an agent for workflow execution and message bus communication."""
        self.available_agents[agent_role] = agent_instance
        self.agent_workloads[agent_role] = 0

        # Register with message bus if agent has handle_message method
        agent_name = self._get_agent_bus_name(agent_role)
        if hasattr(agent_instance, "handle_message"):
            self.message_bus.register_agent(agent_name, agent_instance.handle_message)
            self.logger.info(f"Registered agent {agent_name} with message bus")

        self.logger.info(f"Registered agent for role {agent_role}")

    def _get_agent_bus_name(self, agent_role: AgentRole) -> str:
        """Get the message bus name for an agent role."""
        role_to_name = {
            AgentRole.DISCOVERY: "discovery_agent",
            AgentRole.PLANNING: "planning_agent",
            AgentRole.TEST_CREATION: "test_creation_agent",
            AgentRole.REVIEW: "review_agent",
            AgentRole.EXECUTION: "execution_agent",
            AgentRole.SELF_HEALING: "self_healing_agent",
            AgentRole.REPORTING: "reporting_agent",
            AgentRole.ORCHESTRATOR: "orchestrator",
        }
        return role_to_name.get(agent_role, f"{agent_role.value}_agent")

    def unregister_agent(self, agent_role: AgentRole):
        """Unregister an agent from workflow execution and message bus."""
        if agent_role in self.available_agents:
            agent_name = self._get_agent_bus_name(agent_role)
            self.message_bus.unregister_agent(agent_name)
            del self.available_agents[agent_role]
            del self.agent_workloads[agent_role]
            self.logger.info(f"Unregistered agent for role {agent_role}")
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow"""
        
        # Check active workflows
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
        else:
            # Check workflow history
            workflow = next((w for w in self.workflow_history if w.id == workflow_id), None)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
        
        # Calculate progress
        total_steps = len(workflow.steps)
        completed_steps = sum(1 for step in workflow.steps if step.status == WorkflowStepStatus.COMPLETED)
        failed_steps = sum(1 for step in workflow.steps if step.status == WorkflowStepStatus.FAILED)
        
        progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "progress": round(progress, 1),
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "duration": workflow.total_duration.total_seconds() if workflow.total_duration else None,
            "success_rate": workflow.success_rate,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "status": step.status.value,
                    "agent_role": step.agent_role.value,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "error_message": step.error_message,
                    "retry_count": step.retry_count
                }
                for step in workflow.steps
            ]
        }
    
    def list_workflows(self, include_history: bool = True) -> List[Dict[str, Any]]:
        """List all workflows"""
        
        workflows = []
        
        # Add active workflows
        for workflow in self.active_workflows.values():
            workflows.append({
                "id": workflow.id,
                "name": workflow.name,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "is_active": True
            })
        
        # Add historical workflows if requested
        if include_history:
            for workflow in self.workflow_history:
                workflows.append({
                    "id": workflow.id,
                    "name": workflow.name,
                    "status": workflow.status.value,
                    "created_at": workflow.created_at.isoformat(),
                    "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                    "duration": workflow.total_duration.total_seconds() if workflow.total_duration else None,
                    "success_rate": workflow.success_rate,
                    "is_active": False
                })
        
        return sorted(workflows, key=lambda x: x["created_at"], reverse=True)
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        
        stats = self.execution_stats.copy()
        
        # Calculate additional metrics
        if stats["total_workflows"] > 0:
            stats["failure_rate"] = (stats["failed_workflows"] / stats["total_workflows"]) * 100
            stats["success_rate"] = (stats["successful_workflows"] / stats["total_workflows"]) * 100
        else:
            stats["failure_rate"] = 0
            stats["success_rate"] = 0
        
        # Add current active workflows
        stats["active_workflows"] = len(self.active_workflows)
        
        # Add agent availability
        stats["available_agents"] = list(self.available_agents.keys())
        stats["agent_workloads"] = self.agent_workloads.copy()
        
        return stats
    
    def _update_execution_stats(self, workflow: WorkflowExecution):
        """Update execution statistics"""
        
        self.execution_stats["total_workflows"] += 1
        
        if workflow.status == WorkflowStatus.COMPLETED:
            self.execution_stats["successful_workflows"] += 1
        else:
            self.execution_stats["failed_workflows"] += 1
        
        # Update average duration
        if workflow.total_duration:
            current_avg = self.execution_stats["average_duration"]
            total_workflows = self.execution_stats["total_workflows"]
            new_duration = workflow.total_duration.total_seconds()
            
            self.execution_stats["average_duration"] = (
                (current_avg * (total_workflows - 1) + new_duration) / total_workflows
            )
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        
        if workflow_id not in self.active_workflows:
            return False
        
        workflow = self.active_workflows[workflow_id]
        
        if workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.now()
            if workflow.started_at:
                workflow.total_duration = workflow.completed_at - workflow.started_at
            
            # Move to history
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            self.logger.info(f"Cancelled workflow {workflow_id}")
            return True
        
        return False
    
    def get_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available workflow templates"""
        return self.workflow_templates.copy()
    
    def create_custom_template(self, template_name: str, template_config: Dict[str, Any]) -> bool:
        """Create a custom workflow template"""
        
        try:
            # Validate template structure
            required_fields = ["name", "description", "steps"]
            if not all(field in template_config for field in required_fields):
                raise ValueError(f"Template must contain: {required_fields}")
            
            # Validate steps
            for step in template_config["steps"]:
                required_step_fields = ["id", "name", "agent_role", "task_type", "dependencies"]
                if not all(field in step for field in required_step_fields):
                    raise ValueError(f"Each step must contain: {required_step_fields}")
            
            self.workflow_templates[template_name] = template_config
            self.logger.info(f"Created custom workflow template: {template_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating custom template: {e}")
            return False

