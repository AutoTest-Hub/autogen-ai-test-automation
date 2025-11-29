"""
Three-Tier Step Generation System
=================================

This module implements a sophisticated three-tier approach to test step generation:
1. Tier 1: Basic action identification and element discovery
2. Tier 2: Intelligent flow analysis and context understanding  
3. Tier 3: Advanced test scenario generation with edge cases

The system provides intelligent test flow generation with adaptive strategies
based on application complexity and user requirements.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class StepComplexity(Enum):
    """Defines the complexity levels for test steps"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class FlowType(Enum):
    """Defines different types of test flows"""
    LINEAR = "linear"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    PARALLEL = "parallel"


@dataclass
class TestStep:
    """Represents a single test step with metadata"""
    action: str
    element: str
    value: Optional[str] = None
    description: str = ""
    complexity: StepComplexity = StepComplexity.BASIC
    prerequisites: List[str] = None
    expected_outcome: str = ""
    error_handling: str = ""
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []


@dataclass
class TestFlow:
    """Represents a complete test flow with multiple steps"""
    name: str
    description: str
    steps: List[TestStep]
    flow_type: FlowType = FlowType.LINEAR
    priority: int = 1
    estimated_duration: int = 30  # seconds
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ThreeTierStepGenerator:
    """
    Three-tier step generation system that creates intelligent test flows
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tier1_patterns = self._load_tier1_patterns()
        self.tier2_flows = self._load_tier2_flows()
        self.tier3_scenarios = self._load_tier3_scenarios()
    
    def _load_tier1_patterns(self) -> Dict[str, Any]:
        """Load basic action patterns for Tier 1"""
        return {
            "login": {
                "elements": ["username", "password", "login_button"],
                "actions": ["fill", "fill", "click"],
                "validations": ["page_title", "user_menu", "dashboard"]
            },
            "navigation": {
                "elements": ["menu_item", "submenu", "page_content"],
                "actions": ["click", "hover", "verify"],
                "validations": ["url_change", "content_visible", "breadcrumb"]
            },
            "form_submission": {
                "elements": ["input_fields", "dropdown", "submit_button"],
                "actions": ["fill", "select", "click"],
                "validations": ["success_message", "data_saved", "redirect"]
            },
            "search": {
                "elements": ["search_box", "search_button", "results"],
                "actions": ["fill", "click", "verify"],
                "validations": ["results_displayed", "result_count", "relevance"]
            }
        }
    
    def _load_tier2_flows(self) -> Dict[str, Any]:
        """Load intelligent flow patterns for Tier 2"""
        return {
            "user_journey": {
                "login_to_dashboard": ["login", "verify_dashboard", "check_notifications"],
                "product_purchase": ["search_product", "add_to_cart", "checkout", "payment"],
                "profile_management": ["login", "navigate_profile", "update_info", "save_changes"]
            },
            "business_workflows": {
                "employee_onboarding": ["create_user", "assign_role", "send_invitation", "verify_access"],
                "order_processing": ["receive_order", "validate_inventory", "process_payment", "ship_order"],
                "report_generation": ["select_criteria", "generate_report", "export_data", "email_report"]
            },
            "error_scenarios": {
                "invalid_login": ["enter_invalid_credentials", "verify_error_message", "retry_login"],
                "network_failure": ["simulate_network_error", "verify_error_handling", "retry_mechanism"],
                "data_validation": ["enter_invalid_data", "verify_validation_messages", "correct_data"]
            }
        }
    
    def _load_tier3_scenarios(self) -> Dict[str, Any]:
        """Load advanced scenario patterns for Tier 3"""
        return {
            "edge_cases": {
                "boundary_testing": ["min_values", "max_values", "null_values", "special_characters"],
                "concurrent_users": ["multiple_sessions", "resource_contention", "data_consistency"],
                "performance_limits": ["large_datasets", "slow_network", "memory_constraints"]
            },
            "security_testing": {
                "authentication": ["brute_force", "session_hijacking", "password_policies"],
                "authorization": ["privilege_escalation", "access_control", "data_exposure"],
                "input_validation": ["sql_injection", "xss_attacks", "csrf_protection"]
            },
            "integration_scenarios": {
                "api_integration": ["external_api_calls", "data_synchronization", "error_propagation"],
                "database_operations": ["crud_operations", "transaction_handling", "data_integrity"],
                "third_party_services": ["payment_gateways", "email_services", "cloud_storage"]
            }
        }
    
    def generate_tier1_steps(self, action_type: str, elements: List[Dict]) -> List[TestStep]:
        """
        Tier 1: Generate basic test steps from discovered elements
        """
        steps = []
        
        if action_type not in self.tier1_patterns:
            self.logger.warning(f"Unknown action type: {action_type}")
            return steps
        
        pattern = self.tier1_patterns[action_type]
        
        for i, element in enumerate(elements):
            if i < len(pattern["actions"]):
                action = pattern["actions"][i]
                step = TestStep(
                    action=action,
                    element=element.get("selector", ""),
                    value=element.get("value", ""),
                    description=f"{action.title()} {element.get('type', 'element')}",
                    complexity=StepComplexity.BASIC
                )
                steps.append(step)
        
        return steps
    
    def generate_tier2_flow(self, flow_name: str, context: Dict[str, Any]) -> TestFlow:
        """
        Tier 2: Generate intelligent test flows with context awareness
        """
        if flow_name not in self.tier2_flows:
            # Create a generic flow
            return self._create_generic_flow(flow_name, context)
        
        flow_pattern = self.tier2_flows[flow_name]
        steps = []
        
        for step_name in flow_pattern:
            step = TestStep(
                action=self._infer_action_from_name(step_name),
                element=self._infer_element_from_context(step_name, context),
                description=step_name.replace("_", " ").title(),
                complexity=StepComplexity.INTERMEDIATE
            )
            steps.append(step)
        
        return TestFlow(
            name=flow_name,
            description=f"Intelligent flow for {flow_name.replace('_', ' ')}",
            steps=steps,
            flow_type=FlowType.LINEAR,
            priority=2
        )
    
    def generate_tier3_scenario(self, scenario_type: str, requirements: Dict[str, Any]) -> List[TestFlow]:
        """
        Tier 3: Generate advanced test scenarios with edge cases
        """
        scenarios = []
        
        if scenario_type not in self.tier3_scenarios:
            return scenarios
        
        scenario_patterns = self.tier3_scenarios[scenario_type]
        
        for pattern_name, pattern_steps in scenario_patterns.items():
            steps = []
            for step_name in pattern_steps:
                step = TestStep(
                    action=self._infer_advanced_action(step_name),
                    element=self._infer_advanced_element(step_name, requirements),
                    description=step_name.replace("_", " ").title(),
                    complexity=StepComplexity.ADVANCED,
                    error_handling=self._generate_error_handling(step_name)
                )
                steps.append(step)
            
            flow = TestFlow(
                name=f"{scenario_type}_{pattern_name}",
                description=f"Advanced {pattern_name.replace('_', ' ')} scenario",
                steps=steps,
                flow_type=FlowType.CONDITIONAL,
                priority=3,
                tags=[scenario_type, "advanced", "edge_case"]
            )
            scenarios.append(flow)
        
        return scenarios
    
    def generate_comprehensive_test_suite(self, 
                                        discovery_data: Dict[str, Any],
                                        requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive test suite using all three tiers
        """
        test_suite = {
            "tier1_basic_tests": [],
            "tier2_flow_tests": [],
            "tier3_advanced_tests": [],
            "metadata": {
                "generation_strategy": "three_tier",
                "total_flows": 0,
                "complexity_distribution": {},
                "estimated_duration": 0
            }
        }
        
        # Tier 1: Basic functionality tests
        for action_type in ["login", "navigation", "form_submission", "search"]:
            if action_type in discovery_data.get("actions", {}):
                elements = discovery_data["actions"][action_type].get("elements", [])
                steps = self.generate_tier1_steps(action_type, elements)
                if steps:
                    flow = TestFlow(
                        name=f"basic_{action_type}",
                        description=f"Basic {action_type} functionality",
                        steps=steps,
                        priority=1
                    )
                    test_suite["tier1_basic_tests"].append(flow)
        
        # Tier 2: Intelligent flows
        flow_types = requirements.get("flow_types", ["user_journey", "business_workflows"])
        for flow_category in flow_types:
            if flow_category in self.tier2_flows:
                for flow_name in self.tier2_flows[flow_category]:
                    flow = self.generate_tier2_flow(flow_name, discovery_data)
                    test_suite["tier2_flow_tests"].append(flow)
        
        # Tier 3: Advanced scenarios
        if requirements.get("include_advanced_scenarios", True):
            for scenario_type in ["edge_cases", "security_testing", "integration_scenarios"]:
                scenarios = self.generate_tier3_scenario(scenario_type, requirements)
                test_suite["tier3_advanced_tests"].extend(scenarios)
        
        # Calculate metadata
        all_flows = (test_suite["tier1_basic_tests"] + 
                    test_suite["tier2_flow_tests"] + 
                    test_suite["tier3_advanced_tests"])
        
        test_suite["metadata"]["total_flows"] = len(all_flows)
        test_suite["metadata"]["estimated_duration"] = sum(flow.estimated_duration for flow in all_flows)
        
        # Complexity distribution
        complexity_count = {"basic": 0, "intermediate": 0, "advanced": 0}
        for flow in all_flows:
            for step in flow.steps:
                complexity_count[step.complexity.value] += 1
        
        test_suite["metadata"]["complexity_distribution"] = complexity_count
        
        return test_suite
    
    def _create_generic_flow(self, flow_name: str, context: Dict[str, Any]) -> TestFlow:
        """Create a generic flow when specific pattern is not found"""
        steps = [
            TestStep(
                action="navigate",
                element="page",
                description=f"Navigate to {flow_name} page",
                complexity=StepComplexity.BASIC
            ),
            TestStep(
                action="verify",
                element="content",
                description=f"Verify {flow_name} content is loaded",
                complexity=StepComplexity.BASIC
            )
        ]
        
        return TestFlow(
            name=flow_name,
            description=f"Generic flow for {flow_name}",
            steps=steps,
            priority=1
        )
    
    def _infer_action_from_name(self, step_name: str) -> str:
        """Infer action type from step name"""
        action_mapping = {
            "login": "fill_and_submit",
            "verify": "assert",
            "navigate": "click",
            "search": "fill_and_click",
            "create": "fill_form",
            "update": "modify_form",
            "delete": "click_and_confirm"
        }
        
        for keyword, action in action_mapping.items():
            if keyword in step_name.lower():
                return action
        
        return "interact"
    
    def _infer_element_from_context(self, step_name: str, context: Dict[str, Any]) -> str:
        """Infer element selector from context"""
        # This would be enhanced with actual element discovery data
        element_mapping = {
            "login": "input[type='text'], input[type='password'], button[type='submit']",
            "dashboard": ".dashboard, #main-content",
            "profile": ".profile, .user-info",
            "search": "input[type='search'], .search-box"
        }
        
        for keyword, selector in element_mapping.items():
            if keyword in step_name.lower():
                return selector
        
        return ".generic-element"
    
    def _infer_advanced_action(self, step_name: str) -> str:
        """Infer advanced action types for Tier 3"""
        advanced_actions = {
            "brute_force": "security_test",
            "injection": "vulnerability_test",
            "performance": "load_test",
            "concurrent": "parallel_test",
            "boundary": "edge_case_test"
        }
        
        for keyword, action in advanced_actions.items():
            if keyword in step_name.lower():
                return action
        
        return "advanced_test"
    
    def _infer_advanced_element(self, step_name: str, requirements: Dict[str, Any]) -> str:
        """Infer element for advanced testing scenarios"""
        # This would be enhanced with security and performance testing selectors
        return f"[data-test='{step_name}']"
    
    def _generate_error_handling(self, step_name: str) -> str:
        """Generate error handling strategy for advanced steps"""
        error_strategies = {
            "security": "Log security violation and continue with next test",
            "performance": "Record performance metrics and validate against thresholds",
            "integration": "Verify error propagation and system recovery",
            "boundary": "Validate error messages and system stability"
        }
        
        for keyword, strategy in error_strategies.items():
            if keyword in step_name.lower():
                return strategy
        
        return "Log error and continue test execution"


def create_step_generator() -> ThreeTierStepGenerator:
    """Factory function to create a step generator instance"""
    return ThreeTierStepGenerator()


# Example usage and testing
if __name__ == "__main__":
    generator = create_step_generator()
    
    # Example discovery data
    discovery_data = {
        "actions": {
            "login": {
                "elements": [
                    {"selector": "#username", "type": "input", "value": ""},
                    {"selector": "#password", "type": "input", "value": ""},
                    {"selector": "#login-btn", "type": "button", "value": ""}
                ]
            }
        }
    }
    
    # Example requirements
    requirements = {
        "flow_types": ["user_journey"],
        "include_advanced_scenarios": True,
        "complexity_level": "comprehensive"
    }
    
    # Generate comprehensive test suite
    test_suite = generator.generate_comprehensive_test_suite(discovery_data, requirements)
    
    print("Generated Test Suite:")
    print(f"Total Flows: {test_suite['metadata']['total_flows']}")
    print(f"Estimated Duration: {test_suite['metadata']['estimated_duration']} seconds")
    print(f"Complexity Distribution: {test_suite['metadata']['complexity_distribution']}")
