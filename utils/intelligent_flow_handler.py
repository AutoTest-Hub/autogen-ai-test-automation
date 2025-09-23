"""
Intelligent Flow Handler
========================

This module provides smart test flow generation and management capabilities.
It analyzes application behavior, user interactions, and business logic to
create intelligent test flows that adapt to different scenarios.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class FlowPriority(Enum):
    """Priority levels for test flows"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class FlowCategory(Enum):
    """Categories of test flows"""
    SMOKE = "smoke"
    REGRESSION = "regression"
    INTEGRATION = "integration"
    E2E = "end_to_end"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class FlowCondition:
    """Represents a condition that must be met for flow execution"""
    condition_type: str
    element: str
    expected_value: Any
    operator: str = "equals"
    timeout: int = 10


@dataclass
class FlowStep:
    """Enhanced flow step with intelligent features"""
    action: str
    target: str
    value: Optional[str] = None
    description: str = ""
    wait_condition: Optional[FlowCondition] = None
    retry_count: int = 3
    timeout: int = 30
    screenshot: bool = False
    validation: Optional[Dict[str, Any]] = None


@dataclass
class IntelligentFlow:
    """Represents an intelligent test flow with adaptive capabilities"""
    id: str
    name: str
    description: str
    category: FlowCategory
    priority: FlowPriority
    steps: List[FlowStep]
    preconditions: List[FlowCondition]
    postconditions: List[FlowCondition]
    tags: List[str]
    estimated_duration: int
    success_criteria: Dict[str, Any]
    failure_recovery: List[FlowStep]
    created_at: str
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class IntelligentFlowHandler:
    """
    Handles intelligent test flow generation, optimization, and execution planning
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.flow_templates = self._load_flow_templates()
        self.business_rules = self._load_business_rules()
        self.optimization_strategies = self._load_optimization_strategies()
    
    def _load_flow_templates(self) -> Dict[str, Any]:
        """Load predefined flow templates for common scenarios"""
        return {
            "user_authentication": {
                "steps": [
                    {"action": "navigate", "target": "login_page"},
                    {"action": "fill", "target": "username_field", "value": "{username}"},
                    {"action": "fill", "target": "password_field", "value": "{password}"},
                    {"action": "click", "target": "login_button"},
                    {"action": "verify", "target": "dashboard", "validation": {"visible": True}}
                ],
                "category": FlowCategory.SMOKE,
                "priority": FlowPriority.CRITICAL
            },
            "product_search": {
                "steps": [
                    {"action": "navigate", "target": "search_page"},
                    {"action": "fill", "target": "search_input", "value": "{search_term}"},
                    {"action": "click", "target": "search_button"},
                    {"action": "verify", "target": "search_results", "validation": {"count": ">0"}}
                ],
                "category": FlowCategory.REGRESSION,
                "priority": FlowPriority.HIGH
            },
            "form_submission": {
                "steps": [
                    {"action": "navigate", "target": "form_page"},
                    {"action": "fill_form", "target": "main_form", "value": "{form_data}"},
                    {"action": "click", "target": "submit_button"},
                    {"action": "verify", "target": "success_message", "validation": {"visible": True}}
                ],
                "category": FlowCategory.INTEGRATION,
                "priority": FlowPriority.MEDIUM
            },
            "data_export": {
                "steps": [
                    {"action": "navigate", "target": "reports_page"},
                    {"action": "select", "target": "date_range", "value": "{date_range}"},
                    {"action": "click", "target": "export_button"},
                    {"action": "wait", "target": "download_complete", "timeout": 60},
                    {"action": "verify", "target": "downloaded_file", "validation": {"exists": True}}
                ],
                "category": FlowCategory.E2E,
                "priority": FlowPriority.MEDIUM
            }
        }
    
    def _load_business_rules(self) -> Dict[str, Any]:
        """Load business rules that affect flow generation"""
        return {
            "authentication_required": {
                "applies_to": ["protected_pages", "user_actions"],
                "prerequisite_flow": "user_authentication"
            },
            "data_validation": {
                "applies_to": ["form_submission", "data_entry"],
                "validation_rules": ["required_fields", "format_validation", "business_logic"]
            },
            "workflow_dependencies": {
                "order_processing": ["inventory_check", "payment_validation", "shipping_calculation"],
                "user_management": ["role_validation", "permission_check", "audit_logging"]
            },
            "error_handling": {
                "network_errors": {"retry_count": 3, "backoff_strategy": "exponential"},
                "validation_errors": {"capture_screenshot": True, "log_details": True},
                "system_errors": {"escalate": True, "notify_team": True}
            }
        }
    
    def _load_optimization_strategies(self) -> Dict[str, Any]:
        """Load strategies for flow optimization"""
        return {
            "parallel_execution": {
                "independent_flows": True,
                "max_parallel": 5,
                "resource_constraints": ["browser_instances", "network_bandwidth"]
            },
            "data_driven": {
                "parameterization": True,
                "test_data_sources": ["csv", "json", "database"],
                "data_variation_strategies": ["boundary_values", "equivalence_classes"]
            },
            "smart_waiting": {
                "dynamic_waits": True,
                "element_visibility": True,
                "ajax_completion": True,
                "custom_conditions": True
            },
            "failure_recovery": {
                "auto_retry": True,
                "alternative_paths": True,
                "graceful_degradation": True
            }
        }
    
    def analyze_application_flows(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze discovered application data to identify potential test flows
        """
        analysis = {
            "identified_flows": [],
            "flow_dependencies": {},
            "critical_paths": [],
            "optimization_opportunities": [],
            "risk_areas": []
        }
        
        # Identify flows based on discovered elements and interactions
        pages = discovery_data.get("pages", {})
        interactions = discovery_data.get("interactions", {})
        
        for page_name, page_data in pages.items():
            # Analyze page for potential flows
            page_flows = self._analyze_page_flows(page_name, page_data)
            analysis["identified_flows"].extend(page_flows)
        
        # Identify flow dependencies
        analysis["flow_dependencies"] = self._identify_flow_dependencies(
            analysis["identified_flows"], interactions
        )
        
        # Identify critical paths
        analysis["critical_paths"] = self._identify_critical_paths(
            analysis["identified_flows"], discovery_data.get("business_context", {})
        )
        
        # Find optimization opportunities
        analysis["optimization_opportunities"] = self._find_optimization_opportunities(
            analysis["identified_flows"]
        )
        
        # Identify risk areas
        analysis["risk_areas"] = self._identify_risk_areas(
            discovery_data, analysis["identified_flows"]
        )
        
        return analysis
    
    def generate_intelligent_flows(self, 
                                 analysis_data: Dict[str, Any],
                                 requirements: Dict[str, Any]) -> List[IntelligentFlow]:
        """
        Generate intelligent test flows based on analysis and requirements
        """
        flows = []
        
        # Generate flows for identified scenarios
        for flow_info in analysis_data.get("identified_flows", []):
            flow = self._create_intelligent_flow(flow_info, requirements)
            if flow:
                flows.append(flow)
        
        # Generate critical path flows
        for critical_path in analysis_data.get("critical_paths", []):
            flow = self._create_critical_path_flow(critical_path, requirements)
            if flow:
                flows.append(flow)
        
        # Generate error handling flows
        error_flows = self._generate_error_handling_flows(analysis_data, requirements)
        flows.extend(error_flows)
        
        # Generate performance test flows if required
        if requirements.get("include_performance_tests", False):
            perf_flows = self._generate_performance_flows(analysis_data, requirements)
            flows.extend(perf_flows)
        
        # Optimize flow execution order
        flows = self._optimize_flow_execution_order(flows)
        
        return flows
    
    def _analyze_page_flows(self, page_name: str, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a single page to identify potential flows"""
        flows = []
        
        # Check for common flow patterns
        elements = page_data.get("elements", [])
        
        # Login flow detection
        if self._has_login_elements(elements):
            flows.append({
                "name": f"{page_name}_login",
                "type": "authentication",
                "page": page_name,
                "elements": self._extract_login_elements(elements),
                "priority": FlowPriority.CRITICAL
            })
        
        # Form submission flow detection
        forms = [e for e in elements if e.get("tag") == "form"]
        for form in forms:
            flows.append({
                "name": f"{page_name}_form_submission",
                "type": "form_interaction",
                "page": page_name,
                "form_data": form,
                "priority": FlowPriority.HIGH
            })
        
        # Navigation flow detection
        nav_elements = [e for e in elements if e.get("type") in ["link", "button"] and "nav" in e.get("class", "")]
        if nav_elements:
            flows.append({
                "name": f"{page_name}_navigation",
                "type": "navigation",
                "page": page_name,
                "nav_elements": nav_elements,
                "priority": FlowPriority.MEDIUM
            })
        
        return flows
    
    def _create_intelligent_flow(self, flow_info: Dict[str, Any], requirements: Dict[str, Any]) -> Optional[IntelligentFlow]:
        """Create an intelligent flow from flow information"""
        flow_type = flow_info.get("type")
        
        if flow_type not in self.flow_templates:
            return None
        
        template = self.flow_templates[flow_type]
        
        # Create flow steps from template
        steps = []
        for step_template in template["steps"]:
            step = FlowStep(
                action=step_template["action"],
                target=step_template["target"],
                value=step_template.get("value"),
                description=f"{step_template['action'].title()} {step_template['target']}",
                validation=step_template.get("validation"),
                timeout=requirements.get("default_timeout", 30)
            )
            steps.append(step)
        
        # Create preconditions and postconditions
        preconditions = self._create_preconditions(flow_info, requirements)
        postconditions = self._create_postconditions(flow_info, requirements)
        
        # Create failure recovery steps
        failure_recovery = self._create_failure_recovery_steps(flow_info)
        
        flow = IntelligentFlow(
            id=f"flow_{flow_info['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=flow_info["name"],
            description=f"Intelligent flow for {flow_info['type']} on {flow_info.get('page', 'unknown page')}",
            category=template.get("category", FlowCategory.REGRESSION),
            priority=flow_info.get("priority", FlowPriority.MEDIUM),
            steps=steps,
            preconditions=preconditions,
            postconditions=postconditions,
            tags=[flow_type, flow_info.get("page", ""), "intelligent"],
            estimated_duration=len(steps) * 15,  # 15 seconds per step estimate
            success_criteria={"all_steps_passed": True, "no_errors": True},
            failure_recovery=failure_recovery,
            created_at=datetime.now().isoformat()
        )
        
        return flow
    
    def _has_login_elements(self, elements: List[Dict[str, Any]]) -> bool:
        """Check if page has login elements"""
        has_username = any("username" in e.get("name", "").lower() or 
                          "email" in e.get("name", "").lower() for e in elements)
        has_password = any("password" in e.get("name", "").lower() for e in elements)
        has_submit = any(e.get("type") == "submit" or 
                        "login" in e.get("text", "").lower() for e in elements)
        
        return has_username and has_password and has_submit
    
    def _extract_login_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, str]:
        """Extract login-related elements"""
        login_elements = {}
        
        for element in elements:
            name = element.get("name", "").lower()
            if "username" in name or "email" in name:
                login_elements["username"] = element.get("selector", "")
            elif "password" in name:
                login_elements["password"] = element.get("selector", "")
            elif element.get("type") == "submit" or "login" in element.get("text", "").lower():
                login_elements["submit"] = element.get("selector", "")
        
        return login_elements
    
    def _identify_flow_dependencies(self, flows: List[Dict[str, Any]], 
                                  interactions: Dict[str, Any]) -> Dict[str, List[str]]:
        """Identify dependencies between flows"""
        dependencies = {}
        
        for flow in flows:
            flow_name = flow["name"]
            deps = []
            
            # Authentication dependency
            if flow["type"] != "authentication" and self._requires_authentication(flow):
                auth_flows = [f["name"] for f in flows if f["type"] == "authentication"]
                deps.extend(auth_flows)
            
            # Data dependency
            if self._requires_data_setup(flow):
                setup_flows = [f["name"] for f in flows if "setup" in f["name"].lower()]
                deps.extend(setup_flows)
            
            dependencies[flow_name] = deps
        
        return dependencies
    
    def _identify_critical_paths(self, flows: List[Dict[str, Any]], 
                               business_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify critical business paths"""
        critical_paths = []
        
        # Business-critical flows
        critical_keywords = business_context.get("critical_keywords", 
                                                ["login", "payment", "checkout", "order"])
        
        for flow in flows:
            for keyword in critical_keywords:
                if keyword in flow["name"].lower():
                    critical_paths.append({
                        "flow_name": flow["name"],
                        "criticality": "high",
                        "business_impact": f"Critical {keyword} functionality"
                    })
                    break
        
        return critical_paths
    
    def _find_optimization_opportunities(self, flows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find opportunities to optimize flow execution"""
        opportunities = []
        
        # Parallel execution opportunities
        independent_flows = []
        for flow in flows:
            if not self._has_dependencies(flow, flows):
                independent_flows.append(flow["name"])
        
        if len(independent_flows) > 1:
            opportunities.append({
                "type": "parallel_execution",
                "flows": independent_flows,
                "potential_time_saving": "50-70%"
            })
        
        # Data-driven opportunities
        similar_flows = self._find_similar_flows(flows)
        if similar_flows:
            opportunities.append({
                "type": "data_driven_testing",
                "flows": similar_flows,
                "potential_maintenance_reduction": "60-80%"
            })
        
        return opportunities
    
    def _identify_risk_areas(self, discovery_data: Dict[str, Any], 
                           flows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential risk areas in the application"""
        risks = []
        
        # Complex forms
        complex_forms = discovery_data.get("complex_forms", [])
        if complex_forms:
            risks.append({
                "type": "complex_form_validation",
                "description": "Forms with many fields may have validation issues",
                "affected_flows": [f["name"] for f in flows if f["type"] == "form_interaction"],
                "mitigation": "Implement comprehensive field validation tests"
            })
        
        # Dynamic content
        if discovery_data.get("has_dynamic_content", False):
            risks.append({
                "type": "dynamic_content_timing",
                "description": "Dynamic content may cause timing issues",
                "affected_flows": [f["name"] for f in flows],
                "mitigation": "Implement smart waiting strategies"
            })
        
        return risks
    
    def _create_preconditions(self, flow_info: Dict[str, Any], 
                            requirements: Dict[str, Any]) -> List[FlowCondition]:
        """Create preconditions for a flow"""
        preconditions = []
        
        # Authentication precondition
        if self._requires_authentication(flow_info):
            preconditions.append(FlowCondition(
                condition_type="authentication",
                element="user_session",
                expected_value="authenticated",
                operator="equals"
            ))
        
        # Page availability precondition
        preconditions.append(FlowCondition(
            condition_type="page_availability",
            element="page_status",
            expected_value="loaded",
            operator="equals"
        ))
        
        return preconditions
    
    def _create_postconditions(self, flow_info: Dict[str, Any], 
                             requirements: Dict[str, Any]) -> List[FlowCondition]:
        """Create postconditions for a flow"""
        postconditions = []
        
        # Success indication
        postconditions.append(FlowCondition(
            condition_type="success_indicator",
            element="flow_result",
            expected_value="success",
            operator="equals"
        ))
        
        # No error messages
        postconditions.append(FlowCondition(
            condition_type="error_absence",
            element="error_messages",
            expected_value=0,
            operator="equals"
        ))
        
        return postconditions
    
    def _create_failure_recovery_steps(self, flow_info: Dict[str, Any]) -> List[FlowStep]:
        """Create failure recovery steps"""
        recovery_steps = [
            FlowStep(
                action="screenshot",
                target="current_page",
                description="Capture screenshot for debugging"
            ),
            FlowStep(
                action="log_error",
                target="error_details",
                description="Log detailed error information"
            ),
            FlowStep(
                action="refresh_page",
                target="current_page",
                description="Attempt page refresh"
            )
        ]
        
        return recovery_steps
    
    def _requires_authentication(self, flow_info: Dict[str, Any]) -> bool:
        """Check if flow requires authentication"""
        auth_required_types = ["form_interaction", "data_modification", "user_action"]
        return flow_info.get("type") in auth_required_types
    
    def _requires_data_setup(self, flow_info: Dict[str, Any]) -> bool:
        """Check if flow requires data setup"""
        data_required_types = ["data_modification", "reporting", "search"]
        return flow_info.get("type") in data_required_types
    
    def _has_dependencies(self, flow: Dict[str, Any], all_flows: List[Dict[str, Any]]) -> bool:
        """Check if flow has dependencies on other flows"""
        return self._requires_authentication(flow) or self._requires_data_setup(flow)
    
    def _find_similar_flows(self, flows: List[Dict[str, Any]]) -> List[str]:
        """Find flows that are similar and could be data-driven"""
        similar_groups = {}
        
        for flow in flows:
            flow_type = flow.get("type", "unknown")
            if flow_type not in similar_groups:
                similar_groups[flow_type] = []
            similar_groups[flow_type].append(flow["name"])
        
        # Return groups with more than one flow
        similar_flows = []
        for group, flow_names in similar_groups.items():
            if len(flow_names) > 1:
                similar_flows.extend(flow_names)
        
        return similar_flows
    
    def _create_critical_path_flow(self, critical_path: Dict[str, Any], 
                                 requirements: Dict[str, Any]) -> Optional[IntelligentFlow]:
        """Create a flow for a critical path"""
        # This would create specialized flows for critical business paths
        # Implementation would depend on specific critical path requirements
        return None
    
    def _generate_error_handling_flows(self, analysis_data: Dict[str, Any], 
                                     requirements: Dict[str, Any]) -> List[IntelligentFlow]:
        """Generate flows specifically for error handling scenarios"""
        error_flows = []
        
        # Network error handling
        if requirements.get("test_network_errors", False):
            error_flows.append(self._create_network_error_flow())
        
        # Validation error handling
        if requirements.get("test_validation_errors", False):
            error_flows.append(self._create_validation_error_flow())
        
        return [flow for flow in error_flows if flow is not None]
    
    def _generate_performance_flows(self, analysis_data: Dict[str, Any], 
                                  requirements: Dict[str, Any]) -> List[IntelligentFlow]:
        """Generate performance testing flows"""
        perf_flows = []
        
        # Load testing flow
        if requirements.get("include_load_tests", False):
            perf_flows.append(self._create_load_test_flow())
        
        return [flow for flow in perf_flows if flow is not None]
    
    def _optimize_flow_execution_order(self, flows: List[IntelligentFlow]) -> List[IntelligentFlow]:
        """Optimize the order of flow execution"""
        # Sort by priority first, then by dependencies
        return sorted(flows, key=lambda f: (f.priority.value, len(f.preconditions)))
    
    def _create_network_error_flow(self) -> Optional[IntelligentFlow]:
        """Create a flow to test network error handling"""
        # Implementation for network error testing
        return None
    
    def _create_validation_error_flow(self) -> Optional[IntelligentFlow]:
        """Create a flow to test validation error handling"""
        # Implementation for validation error testing
        return None
    
    def _create_load_test_flow(self) -> Optional[IntelligentFlow]:
        """Create a flow for load testing"""
        # Implementation for load testing
        return None
    
    def export_flows_to_json(self, flows: List[IntelligentFlow], filepath: str) -> bool:
        """Export flows to JSON file"""
        try:
            flows_data = [asdict(flow) for flow in flows]
            with open(filepath, 'w') as f:
                json.dump(flows_data, f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Failed to export flows: {e}")
            return False
    
    def import_flows_from_json(self, filepath: str) -> List[IntelligentFlow]:
        """Import flows from JSON file"""
        try:
            with open(filepath, 'r') as f:
                flows_data = json.load(f)
            
            flows = []
            for flow_data in flows_data:
                # Convert back to dataclass instances
                flow = IntelligentFlow(**flow_data)
                flows.append(flow)
            
            return flows
        except Exception as e:
            self.logger.error(f"Failed to import flows: {e}")
            return []


def create_intelligent_flow_handler() -> IntelligentFlowHandler:
    """Factory function to create an intelligent flow handler"""
    return IntelligentFlowHandler()


# Example usage
if __name__ == "__main__":
    handler = create_intelligent_flow_handler()
    
    # Example discovery data
    discovery_data = {
        "pages": {
            "login": {
                "elements": [
                    {"name": "username", "type": "input", "selector": "#username"},
                    {"name": "password", "type": "input", "selector": "#password"},
                    {"type": "submit", "text": "Login", "selector": "#login-btn"}
                ]
            }
        },
        "business_context": {
            "critical_keywords": ["login", "checkout", "payment"]
        }
    }
    
    # Analyze application flows
    analysis = handler.analyze_application_flows(discovery_data)
    
    # Generate intelligent flows
    requirements = {
        "default_timeout": 30,
        "include_performance_tests": False,
        "test_network_errors": True
    }
    
    flows = handler.generate_intelligent_flows(analysis, requirements)
    
    print(f"Generated {len(flows)} intelligent flows")
    for flow in flows:
        print(f"- {flow.name} ({flow.category.value}, Priority: {flow.priority.value})")
