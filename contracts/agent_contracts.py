"""
Agent Contracts - Data Structures for Agent Communication
========================================================

This module defines the data contracts used for communication between agents
in the test automation pipeline. These contracts ensure type safety and
consistent data flow through:

    Discovery Agent -> Planning Agent -> Test Creation Agent -> Execution Agent

Key Contracts:
- DiscoveryResult: Output from discovery agent
- TestPlan: Output from planning agent
- GeneratedTest: Output from test creation agent
- ExecutionResult: Output from execution agent
- WorkflowContext: Shared context across the pipeline
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import uuid


class ElementType(str, Enum):
    """Types of discovered elements"""
    INPUT = "input"
    BUTTON = "button"
    LINK = "link"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FORM = "form"
    NAVIGATION = "navigation"
    IMAGE = "image"
    TEXT = "text"
    UNKNOWN = "unknown"


class TestPriority(str, Enum):
    """Test case priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExecutionStatus(str, Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class DiscoveredElement:
    """Represents a single discovered UI element"""
    element_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    element_type: ElementType = ElementType.UNKNOWN
    name: str = ""
    text: str = ""
    category: str = ""
    selectors: Dict[str, str] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_interactive: bool = True
    is_visible: bool = True
    page_url: str = ""

    def get_best_selector(self) -> Optional[str]:
        """Get the most reliable selector for this element"""
        # Priority order: id > name > css > class > text
        for key in ["id", "name", "css", "class", "text"]:
            if key in self.selectors and self.selectors[key]:
                return self.selectors[key]
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "element_type": self.element_type.value,
            "name": self.name,
            "text": self.text,
            "category": self.category,
            "selectors": self.selectors,
            "attributes": self.attributes,
            "is_interactive": self.is_interactive,
            "is_visible": self.is_visible,
            "page_url": self.page_url
        }


@dataclass
class DiscoveredPage:
    """Represents a discovered page in the application"""
    page_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    url: str = ""
    title: str = ""
    elements: List[DiscoveredElement] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    navigation_links: List[Dict[str, Any]] = field(default_factory=list)
    screenshot_path: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_id": self.page_id,
            "url": self.url,
            "title": self.title,
            "elements": [e.to_dict() if hasattr(e, 'to_dict') else e for e in self.elements],
            "forms": self.forms,
            "navigation_links": self.navigation_links,
            "screenshot_path": self.screenshot_path,
            "discovered_at": self.discovered_at.isoformat()
        }


@dataclass
class DiscoveryResult:
    """
    Output contract from the Discovery Agent.

    This is the primary input for the Planning Agent, containing
    all discovered application structure and elements.
    """
    discovery_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    base_url: str = ""
    discovered_pages: List[DiscoveredPage] = field(default_factory=list)
    discovered_elements: List[DiscoveredElement] = field(default_factory=list)
    user_workflows: List[Dict[str, Any]] = field(default_factory=list)
    discovery_method: str = "browser"  # "browser", "api", "mock"
    discovery_timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None

    def get_elements_by_type(self, element_type: ElementType) -> List[DiscoveredElement]:
        """Get all elements of a specific type"""
        return [e for e in self.discovered_elements if e.element_type == element_type]

    def get_element_by_name(self, name: str) -> Optional[DiscoveredElement]:
        """Find element by name"""
        for elem in self.discovered_elements:
            if elem.name.lower() == name.lower():
                return elem
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "discovery_id": self.discovery_id,
            "base_url": self.base_url,
            "discovered_pages": [p.to_dict() if hasattr(p, 'to_dict') else p for p in self.discovered_pages],
            "discovered_elements": [e.to_dict() if hasattr(e, 'to_dict') else e for e in self.discovered_elements],
            "user_workflows": self.user_workflows,
            "discovery_method": self.discovery_method,
            "discovery_timestamp": self.discovery_timestamp.isoformat(),
            "success": self.success,
            "error_message": self.error_message
        }


@dataclass
class TestStep:
    """Represents a single test step"""
    step_number: int
    action: str
    description: str = ""
    selector: Optional[str] = None
    input_data: Optional[str] = None
    expected_result: str = ""
    timeout_ms: int = 30000

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "action": self.action,
            "description": self.description,
            "selector": self.selector,
            "input_data": self.input_data,
            "expected_result": self.expected_result,
            "timeout_ms": self.timeout_ms
        }


@dataclass
class TestCase:
    """Represents a planned test case"""
    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    priority: TestPriority = TestPriority.MEDIUM
    test_type: str = "functional"  # functional, integration, ui, api
    steps: List[TestStep] = field(default_factory=list)
    expected_results: List[str] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    estimated_duration_minutes: int = 5
    required_framework: str = "playwright"
    uses_discovery_selectors: bool = False
    generated_from: str = "requirements"  # requirements, discovery, llm

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "test_type": self.test_type,
            "steps": [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.steps],
            "expected_results": self.expected_results,
            "preconditions": self.preconditions,
            "tags": self.tags,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "required_framework": self.required_framework,
            "uses_discovery_selectors": self.uses_discovery_selectors,
            "generated_from": self.generated_from
        }


@dataclass
class RiskAssessment:
    """Risk assessment for test plan"""
    overall_risk: RiskLevel = RiskLevel.MEDIUM
    high_risk_areas: List[str] = field(default_factory=list)
    risk_factors: List[Dict[str, Any]] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    confidence_score: float = 0.7

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_risk": self.overall_risk.value,
            "high_risk_areas": self.high_risk_areas,
            "risk_factors": self.risk_factors,
            "mitigation_strategies": self.mitigation_strategies,
            "confidence_score": self.confidence_score
        }


@dataclass
class TestPlan:
    """
    Output contract from the Planning Agent.

    This is the primary input for the Test Creation Agent, containing
    the test strategy, test cases, and risk assessment.
    """
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    requirements_summary: Dict[str, Any] = field(default_factory=dict)
    requirements_analysis: Dict[str, Any] = field(default_factory=dict)
    test_cases: List[TestCase] = field(default_factory=list)
    risk_assessment: RiskAssessment = field(default_factory=RiskAssessment)
    execution_strategy: Dict[str, Any] = field(default_factory=dict)
    quality_gates: Dict[str, Any] = field(default_factory=dict)
    estimated_hours: float = 8.0
    recommended_framework: str = "playwright"
    discovery_integrated: bool = False
    llm_powered: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "created_at": self.created_at.isoformat(),
            "requirements_summary": self.requirements_summary,
            "requirements_analysis": self.requirements_analysis,
            "test_cases": [tc.to_dict() if hasattr(tc, 'to_dict') else tc for tc in self.test_cases],
            "risk_assessment": self.risk_assessment.to_dict() if hasattr(self.risk_assessment, 'to_dict') else self.risk_assessment,
            "execution_strategy": self.execution_strategy,
            "quality_gates": self.quality_gates,
            "estimated_hours": self.estimated_hours,
            "recommended_framework": self.recommended_framework,
            "discovery_integrated": self.discovery_integrated,
            "llm_powered": self.llm_powered
        }


@dataclass
class GeneratedTest:
    """
    Output contract from the Test Creation Agent.

    Represents a generated test file with metadata.
    """
    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_path: str = ""
    file_name: str = ""
    framework: str = "playwright"
    test_type: str = "test"  # test, page_object, config, utility
    code_content: str = ""
    selectors_used: List[str] = field(default_factory=list)
    llm_generated: bool = False
    generation_method: str = "template"  # template, llm
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "framework": self.framework,
            "test_type": self.test_type,
            "selectors_used": self.selectors_used,
            "llm_generated": self.llm_generated,
            "generation_method": self.generation_method,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class TestExecutionResult:
    """Result of a single test execution"""
    test_id: str
    test_name: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    log_output: str = ""
    assertions_passed: int = 0
    assertions_failed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "screenshot_path": self.screenshot_path,
            "log_output": self.log_output,
            "assertions_passed": self.assertions_passed,
            "assertions_failed": self.assertions_failed
        }


@dataclass
class ExecutionReport:
    """
    Output contract from the Execution Agent.

    Contains results of test execution run.
    """
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    execution_start: datetime = field(default_factory=datetime.now)
    execution_end: Optional[datetime] = None
    test_results: List[TestExecutionResult] = field(default_factory=list)
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    pass_rate: float = 0.0
    total_duration_seconds: float = 0.0

    def calculate_metrics(self):
        """Calculate summary metrics from test results"""
        self.total_tests = len(self.test_results)
        self.passed = sum(1 for r in self.test_results if r.status == ExecutionStatus.PASSED)
        self.failed = sum(1 for r in self.test_results if r.status == ExecutionStatus.FAILED)
        self.skipped = sum(1 for r in self.test_results if r.status == ExecutionStatus.SKIPPED)
        self.errors = sum(1 for r in self.test_results if r.status == ExecutionStatus.ERROR)
        self.pass_rate = (self.passed / max(self.total_tests, 1)) * 100
        self.total_duration_seconds = sum(r.duration_seconds for r in self.test_results)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "execution_start": self.execution_start.isoformat(),
            "execution_end": self.execution_end.isoformat() if self.execution_end else None,
            "test_results": [r.to_dict() for r in self.test_results],
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "errors": self.errors,
            "pass_rate": self.pass_rate,
            "total_duration_seconds": self.total_duration_seconds
        }


@dataclass
class WorkflowContext:
    """
    Shared context that flows through the entire pipeline.

    This is the master context object that accumulates results
    from each stage of the workflow.
    """
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    # Input
    application_url: str = ""
    requirements: str = ""
    requirements_files: List[str] = field(default_factory=list)

    # Stage outputs
    discovery_result: Optional[DiscoveryResult] = None
    test_plan: Optional[TestPlan] = None
    generated_tests: List[GeneratedTest] = field(default_factory=list)
    execution_report: Optional[ExecutionReport] = None

    # Metadata
    current_stage: str = "initialized"
    stages_completed: List[str] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    llm_calls_made: int = 0
    total_tokens_used: int = 0

    def advance_stage(self, new_stage: str):
        """Advance to the next workflow stage"""
        self.stages_completed.append(self.current_stage)
        self.current_stage = new_stage

    def add_error(self, stage: str, error: str):
        """Record an error"""
        self.errors.append({
            "stage": stage,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "created_at": self.created_at.isoformat(),
            "application_url": self.application_url,
            "requirements": self.requirements,
            "requirements_files": self.requirements_files,
            "discovery_result": self.discovery_result.to_dict() if self.discovery_result else None,
            "test_plan": self.test_plan.to_dict() if self.test_plan else None,
            "generated_tests": [t.to_dict() for t in self.generated_tests],
            "execution_report": self.execution_report.to_dict() if self.execution_report else None,
            "current_stage": self.current_stage,
            "stages_completed": self.stages_completed,
            "errors": self.errors,
            "llm_calls_made": self.llm_calls_made,
            "total_tokens_used": self.total_tokens_used
        }


# Factory functions for creating contracts from dict data

def create_discovery_result(data: Dict[str, Any]) -> DiscoveryResult:
    """Create DiscoveryResult from dictionary data"""
    return DiscoveryResult(
        discovery_id=data.get("discovery_id", str(uuid.uuid4())),
        base_url=data.get("base_url", ""),
        discovered_pages=data.get("discovered_pages", []),
        discovered_elements=data.get("discovered_elements", []),
        user_workflows=data.get("user_workflows", []),
        discovery_method=data.get("discovery_method", "browser"),
        success=data.get("success", True),
        error_message=data.get("error_message")
    )


def create_test_plan(data: Dict[str, Any]) -> TestPlan:
    """Create TestPlan from dictionary data"""
    return TestPlan(
        plan_id=data.get("plan_id", str(uuid.uuid4())),
        requirements_summary=data.get("requirements_summary", {}),
        requirements_analysis=data.get("requirements_analysis", {}),
        test_cases=data.get("test_cases", []),
        execution_strategy=data.get("execution_strategy", {}),
        quality_gates=data.get("quality_gates", {}),
        estimated_hours=data.get("estimated_hours", 8.0),
        recommended_framework=data.get("recommended_framework", "playwright"),
        discovery_integrated=data.get("discovery_integrated", False),
        llm_powered=data.get("llm_powered", False)
    )


def create_workflow_context(
    workflow_id: Optional[str] = None,
    application_url: str = "",
    requirements: str = ""
) -> WorkflowContext:
    """Create a new WorkflowContext"""
    return WorkflowContext(
        workflow_id=workflow_id or str(uuid.uuid4()),
        application_url=application_url,
        requirements=requirements
    )
