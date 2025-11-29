"""
Agent Data Contracts for AutoGen Test Automation Framework

This module defines standardized data structures (contracts) for communication
between agents. Using these contracts ensures consistent data flow and enables
proper context passing across the agent pipeline.

Pipeline Flow:
    Discovery -> Planning -> Test Creation -> Review -> Execution -> Reporting

Each agent produces output conforming to its contract, which becomes input
for downstream agents.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json


class Priority(str, Enum):
    """Priority levels for test scenarios and issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestFramework(str, Enum):
    """Supported test frameworks"""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    REQUESTS = "requests"
    HTTPX = "httpx"


class CoverageStatus(str, Enum):
    """Requirement coverage status"""
    COVERED = "covered"
    PARTIAL = "partial"
    NOT_COVERED = "not_covered"


# =============================================================================
# DISCOVERY AGENT CONTRACTS
# =============================================================================

@dataclass
class ElementSelector:
    """Standardized element selector information"""
    primary: str  # Primary selector to use
    fallbacks: List[str] = field(default_factory=list)  # Fallback selectors
    selector_type: str = "css"  # css, xpath, id, name, etc.
    confidence: float = 1.0  # How confident we are in this selector

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary": self.primary,
            "fallbacks": self.fallbacks,
            "selector_type": self.selector_type,
            "confidence": self.confidence
        }


@dataclass
class DiscoveredElement:
    """Information about a discovered page element"""
    element_id: str
    element_type: str  # button, input, link, form, etc.
    name: str
    text: Optional[str] = None
    selectors: ElementSelector = None
    attributes: Dict[str, str] = field(default_factory=dict)
    is_interactive: bool = True
    category: str = "general"  # login, navigation, form, action, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "element_type": self.element_type,
            "name": self.name,
            "text": self.text,
            "selectors": self.selectors.to_dict() if self.selectors else None,
            "attributes": self.attributes,
            "is_interactive": self.is_interactive,
            "category": self.category
        }


@dataclass
class DiscoveredPage:
    """Information about a discovered application page"""
    page_id: str
    name: str
    url: str
    title: Optional[str] = None
    elements: List[DiscoveredElement] = field(default_factory=list)
    screenshot_path: Optional[str] = None
    load_time_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_id": self.page_id,
            "name": self.name,
            "url": self.url,
            "title": self.title,
            "elements": [e.to_dict() for e in self.elements],
            "screenshot_path": self.screenshot_path,
            "load_time_ms": self.load_time_ms
        }


@dataclass
class DiscoveredWorkflow:
    """Information about a discovered user workflow"""
    workflow_id: str
    name: str
    description: str
    steps: List[str]
    involved_pages: List[str]  # Page IDs
    required_elements: List[str]  # Element IDs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "involved_pages": self.involved_pages,
            "required_elements": self.required_elements
        }


@dataclass
class DiscoveryResult:
    """
    Standard output from Discovery Agent.

    This is the contract that Planning Agent expects as input.
    """
    discovery_id: str
    application_url: str
    timestamp: datetime
    pages: List[DiscoveredPage] = field(default_factory=list)
    elements: Dict[str, List[DiscoveredElement]] = field(default_factory=dict)
    workflows: List[DiscoveredWorkflow] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "discovery_id": self.discovery_id,
            "application_url": self.application_url,
            "timestamp": self.timestamp.isoformat(),
            "pages": [p.to_dict() for p in self.pages],
            "elements": {k: [e.to_dict() for e in v] for k, v in self.elements.items()},
            "workflows": [w.to_dict() for w in self.workflows],
            "screenshots": self.screenshots,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiscoveryResult":
        """Create DiscoveryResult from dictionary"""
        return cls(
            discovery_id=data.get("discovery_id", ""),
            application_url=data.get("application_url", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            pages=[],  # Would need proper deserialization
            elements={},
            workflows=[],
            screenshots=data.get("screenshots", []),
            metadata=data.get("metadata", {})
        )


# =============================================================================
# PLANNING AGENT CONTRACTS
# =============================================================================

@dataclass
class TestStep:
    """A single test step"""
    step_number: int
    action: str
    expected_result: str
    target_element: Optional[str] = None  # Element ID reference
    test_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "action": self.action,
            "expected_result": self.expected_result,
            "target_element": self.target_element,
            "test_data": self.test_data
        }


@dataclass
class TestCase:
    """A complete test case definition"""
    test_id: str
    name: str
    description: str
    priority: Priority
    test_type: str  # functional, security, performance, etc.
    steps: List[TestStep]
    expected_results: List[str]
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    estimated_duration_minutes: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "test_type": self.test_type,
            "steps": [s.to_dict() for s in self.steps],
            "expected_results": self.expected_results,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "tags": self.tags,
            "estimated_duration_minutes": self.estimated_duration_minutes
        }


@dataclass
class RiskAssessment:
    """Risk assessment for the test plan"""
    overall_risk_level: str
    risk_score: float
    key_risks: List[Dict[str, Any]]
    mitigation_strategies: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_risk_level": self.overall_risk_level,
            "risk_score": self.risk_score,
            "key_risks": self.key_risks,
            "mitigation_strategies": self.mitigation_strategies
        }


@dataclass
class TestPlan:
    """
    Standard output from Planning Agent.

    This is the contract that Test Creation Agent expects as input.
    """
    plan_id: str
    name: str
    description: str
    created_at: datetime
    test_cases: List[TestCase]
    priority_order: List[str]  # Test IDs in priority order
    risk_assessment: RiskAssessment
    recommended_framework: TestFramework
    estimated_duration_minutes: int
    discovery_reference: Optional[str] = None  # Discovery ID this plan is based on
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "test_cases": [tc.to_dict() for tc in self.test_cases],
            "priority_order": self.priority_order,
            "risk_assessment": self.risk_assessment.to_dict(),
            "recommended_framework": self.recommended_framework.value,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "discovery_reference": self.discovery_reference,
            "metadata": self.metadata
        }


# =============================================================================
# TEST CREATION AGENT CONTRACTS
# =============================================================================

@dataclass
class GeneratedTestFile:
    """A generated test file"""
    file_id: str
    file_path: str
    file_name: str
    content: str
    framework: TestFramework
    test_cases_covered: List[str]  # Test case IDs
    selectors_used: List[str]  # Element selectors used
    llm_generated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_id": self.file_id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "content": self.content,
            "framework": self.framework.value,
            "test_cases_covered": self.test_cases_covered,
            "selectors_used": self.selectors_used,
            "llm_generated": self.llm_generated
        }


@dataclass
class GeneratedTest:
    """
    Standard output from Test Creation Agent.

    This is the contract that Review Agent expects as input.
    """
    generation_id: str
    created_at: datetime
    test_files: List[GeneratedTestFile]
    page_objects: List[GeneratedTestFile]
    config_files: List[GeneratedTestFile]
    framework: TestFramework
    plan_reference: str  # Test Plan ID this was generated from
    discovery_reference: Optional[str] = None
    requirements_covered: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generation_id": self.generation_id,
            "created_at": self.created_at.isoformat(),
            "test_files": [tf.to_dict() for tf in self.test_files],
            "page_objects": [po.to_dict() for po in self.page_objects],
            "config_files": [cf.to_dict() for cf in self.config_files],
            "framework": self.framework.value,
            "plan_reference": self.plan_reference,
            "discovery_reference": self.discovery_reference,
            "requirements_covered": self.requirements_covered,
            "metadata": self.metadata
        }


# =============================================================================
# REVIEW AGENT CONTRACTS
# =============================================================================

@dataclass
class ReviewIssue:
    """An issue found during code review"""
    issue_id: str
    severity: Priority
    category: str  # logic, assertion, security, style, performance
    description: str
    file_path: str
    line_hint: Optional[str] = None
    suggested_fix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "severity": self.severity.value,
            "category": self.category,
            "description": self.description,
            "file_path": self.file_path,
            "line_hint": self.line_hint,
            "suggested_fix": self.suggested_fix
        }


@dataclass
class RequirementCoverage:
    """Coverage status for a requirement"""
    requirement_id: str
    coverage_status: CoverageStatus
    covering_tests: List[str]  # Test file IDs
    gaps: List[str]
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "coverage_status": self.coverage_status.value,
            "covering_tests": self.covering_tests,
            "gaps": self.gaps,
            "confidence": self.confidence
        }


@dataclass
class ReviewResult:
    """
    Standard output from Review Agent.

    This is the contract that Execution Agent expects as input.
    """
    review_id: str
    created_at: datetime
    overall_score: float  # 1-10
    issues: List[ReviewIssue]
    strengths: List[str]
    requirement_coverage: List[RequirementCoverage]
    overall_coverage_percentage: float
    ready_for_execution: bool
    recommendations: List[str]
    generation_reference: str  # Generated Test ID this review is for
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "review_id": self.review_id,
            "created_at": self.created_at.isoformat(),
            "overall_score": self.overall_score,
            "issues": [i.to_dict() for i in self.issues],
            "strengths": self.strengths,
            "requirement_coverage": [rc.to_dict() for rc in self.requirement_coverage],
            "overall_coverage_percentage": self.overall_coverage_percentage,
            "ready_for_execution": self.ready_for_execution,
            "recommendations": self.recommendations,
            "generation_reference": self.generation_reference,
            "metadata": self.metadata
        }


# =============================================================================
# EXECUTION AGENT CONTRACTS
# =============================================================================

@dataclass
class TestResult:
    """Result of a single test execution"""
    test_id: str
    test_name: str
    status: str  # passed, failed, skipped, error
    duration_ms: int
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "screenshots": self.screenshots,
            "logs": self.logs
        }


@dataclass
class ExecutionResult:
    """
    Standard output from Execution Agent.

    This is the contract that Reporting Agent expects as input.
    """
    execution_id: str
    started_at: datetime
    completed_at: datetime
    test_results: List[TestResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    success_rate: float
    total_duration_ms: int
    environment: Dict[str, str]
    review_reference: str  # Review ID this execution is based on
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "test_results": [tr.to_dict() for tr in self.test_results],
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "success_rate": self.success_rate,
            "total_duration_ms": self.total_duration_ms,
            "environment": self.environment,
            "review_reference": self.review_reference,
            "metadata": self.metadata
        }


# =============================================================================
# WORKFLOW CONTEXT
# =============================================================================

@dataclass
class WorkflowContext:
    """
    Accumulated context passed through the agent pipeline.

    This context grows as it passes through each agent, accumulating
    results from all previous stages.
    """
    workflow_id: str
    started_at: datetime
    current_stage: str

    # Results from each stage (optional until that stage completes)
    discovery_result: Optional[DiscoveryResult] = None
    test_plan: Optional[TestPlan] = None
    generated_tests: Optional[GeneratedTest] = None
    review_result: Optional[ReviewResult] = None
    execution_result: Optional[ExecutionResult] = None

    # Cross-cutting concerns
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "started_at": self.started_at.isoformat(),
            "current_stage": self.current_stage,
            "discovery_result": self.discovery_result.to_dict() if self.discovery_result else None,
            "test_plan": self.test_plan.to_dict() if self.test_plan else None,
            "generated_tests": self.generated_tests.to_dict() if self.generated_tests else None,
            "review_result": self.review_result.to_dict() if self.review_result else None,
            "execution_result": self.execution_result.to_dict() if self.execution_result else None,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata
        }

    def add_error(self, stage: str, error: str, details: Optional[Dict] = None):
        """Add an error to the context"""
        self.errors.append({
            "stage": stage,
            "error": error,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def add_warning(self, warning: str):
        """Add a warning to the context"""
        self.warnings.append(warning)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_workflow_context(workflow_id: str) -> WorkflowContext:
    """Create a new workflow context"""
    return WorkflowContext(
        workflow_id=workflow_id,
        started_at=datetime.now(),
        current_stage="initialized"
    )


def serialize_contract(contract) -> str:
    """Serialize a contract to JSON string"""
    return json.dumps(contract.to_dict(), indent=2, default=str)


def validate_discovery_result(data: Dict[str, Any]) -> bool:
    """Validate that data conforms to DiscoveryResult contract"""
    required_fields = ["discovery_id", "application_url", "timestamp"]
    return all(field in data for field in required_fields)


def validate_test_plan(data: Dict[str, Any]) -> bool:
    """Validate that data conforms to TestPlan contract"""
    required_fields = ["plan_id", "name", "test_cases", "recommended_framework"]
    return all(field in data for field in required_fields)


def validate_generated_test(data: Dict[str, Any]) -> bool:
    """Validate that data conforms to GeneratedTest contract"""
    required_fields = ["generation_id", "test_files", "framework"]
    return all(field in data for field in required_fields)


def validate_review_result(data: Dict[str, Any]) -> bool:
    """Validate that data conforms to ReviewResult contract"""
    required_fields = ["review_id", "overall_score", "ready_for_execution"]
    return all(field in data for field in required_fields)


def validate_execution_result(data: Dict[str, Any]) -> bool:
    """Validate that data conforms to ExecutionResult contract"""
    required_fields = ["execution_id", "test_results", "success_rate"]
    return all(field in data for field in required_fields)
