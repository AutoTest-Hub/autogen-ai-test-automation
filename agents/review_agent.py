#!/usr/bin/env python3
"""
Review Agent for AutoGen Test Automation Framework
Responsible for reviewing and validating generated test automation code
"""

import json
import os
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseTestAgent
from config.settings import AgentRole, TestFramework


class ReviewAgent(BaseTestAgent):
    """Agent responsible for reviewing and validating test automation code"""
    
    def __init__(self, **kwargs):
        system_message = """
You are the Review Agent, an expert in test automation code review and quality assurance. Your responsibilities include:

1. **Code Review**: Review generated test automation code for quality, correctness, and best practices
2. **Test Validation**: Validate test scenarios for completeness and coverage
3. **Quality Assessment**: Assess code quality, maintainability, and reliability
4. **Best Practices**: Ensure adherence to testing best practices and coding standards
5. **Risk Analysis**: Identify potential issues, risks, and improvement opportunities
6. **Recommendations**: Provide actionable feedback and improvement suggestions

**Key Capabilities**:
- Review Playwright, Selenium, and API test code
- Validate test scenario coverage and completeness
- Assess code quality and maintainability
- Identify potential bugs and issues
- Recommend improvements and optimizations
- Ensure compliance with testing standards

**Review Criteria**:
- Code correctness and functionality
- Test coverage and completeness
- Error handling and robustness
- Code readability and maintainability
- Performance and efficiency
- Security considerations
- Compliance with best practices

**Output Format**: Always provide structured review feedback with:
- Overall quality score (1-10)
- Detailed findings and issues
- Specific recommendations
- Priority levels for improvements
- Code quality metrics
"""
        
        super().__init__(
            role=AgentRole.REVIEW,
            system_message=system_message,
            **kwargs
        )
        
        # Register review functions
        self.register_function(
            func=self._review_tests,
            description="Review and validate test automation code"
        )
        
        self.register_function(
            func=self._validate_scenarios,
            description="Validate test scenarios for completeness and coverage"
        )
        
        self.register_function(
            func=self._assess_quality,
            description="Assess code quality and provide improvement recommendations"
        )
        
        self.register_function(
            func=self._analyze_coverage,
            description="Analyze test coverage and identify gaps"
        )
        
        self.register_function(
            func=self._generate_report,
            description="Generate comprehensive review report"
        )
        
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "review_test_code",
            "validate_test_scenarios", 
            "assess_code_quality",
            "analyze_test_coverage",
            "generate_review_report"
        ]
        
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process review task"""
        try:
            self.update_state("processing")
            
            task_type = task_data.get("task_type", task_data.get("type", "review_code"))
            
            if task_type == "review_tests" or task_type == "review_code":
                result = await self._review_tests(task_data)
            elif task_type == "validate_scenarios":
                result = await self._validate_scenarios(task_data)
            elif task_type == "assess_quality":
                result = await self._assess_quality(task_data)
            elif task_type == "analyze_coverage":
                result = await self._analyze_coverage(task_data)
            elif task_type == "generate_report":
                result = await self._generate_report(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.update_state("completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing review task: {e}")
            self.update_state("error")
            raise
    
    async def _review_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review generated test code"""
        # Handle both old format (test_files) and new format (created_tests)
        test_files = task_data.get("test_files", [])
        test_code = task_data.get("test_code", "")
        created_tests = task_data.get("created_tests", {})
        
        # Extract test files from created_tests if available
        if created_tests and not test_files:
            generated_files = created_tests.get("generated_test_files", [])
            if generated_files:
                test_files = generated_files
            else:
                # Look for login_test or other test files
                if created_tests.get("login_test"):
                    test_files.append(created_tests["login_test"])
        
        self.logger.info(f"Reviewing {len(test_files)} test files")
        
        review_results = {
            "overall_score": 0,
            "reviews": [],
            "summary": {},
            "recommendations": []
        }
        
        # Review each test file or code snippet
        if test_files:
            for test_file in test_files:
                file_review = await self._review_single_file(test_file)
                review_results["reviews"].append(file_review)
        elif test_code:
            code_review = await self._review_code_snippet(test_code)
            review_results["reviews"].append(code_review)
        else:
            # If no test files found, create a default review
            self.logger.warning("No test files found to review")
            review_results["reviews"].append({
                "filename": "no_tests_found",
                "score": 0,
                "issues": ["No test files were provided for review"],
                "recommendations": ["Ensure test files are generated before review"],
                "metrics": {"total_lines": 0}
            })
        
        # Calculate overall score and generate summary
        review_results["overall_score"] = self._calculate_overall_score(review_results["reviews"])
        review_results["summary"] = self._generate_review_summary(review_results["reviews"])
        review_results["recommendations"] = self._generate_recommendations(review_results["reviews"])
        
        # Save review report
        report_filename = f"review_report_{int(time.time())}.json"
        report_path = self.save_work_artifact(report_filename, json.dumps(review_results, indent=2))
        
        return {
            "review_results": review_results,
            "report_path": report_path,
            "overall_score": review_results["overall_score"],
            "total_files_reviewed": len(review_results["reviews"])
        }
    
    async def _review_single_file(self, test_file: str) -> Dict[str, Any]:
        """Review a single test file"""
        try:
            # Read test file content
            if os.path.exists(test_file):
                with open(test_file, 'r') as f:
                    content = f.read()
            else:
                content = test_file  # Assume it's the content itself
            
            return await self._review_code_snippet(content, filename=os.path.basename(test_file))
            
        except Exception as e:
            self.logger.error(f"Error reviewing file {test_file}: {e}")
            return {
                "filename": test_file,
                "score": 0,
                "issues": [f"Failed to review file: {e}"],
                "recommendations": ["Fix file access issues"]
            }
    
    async def _review_code_snippet(self, code: str, filename: str = "code_snippet") -> Dict[str, Any]:
        """Review a code snippet"""
        review = {
            "filename": filename,
            "score": 8,  # Default good score
            "issues": [],
            "strengths": [],
            "recommendations": [],
            "metrics": {}
        }
        
        # Basic code quality checks
        lines = code.split('\n')
        review["metrics"]["total_lines"] = len(lines)
        review["metrics"]["non_empty_lines"] = len([line for line in lines if line.strip()])
        
        # Check for common issues
        issues = []
        strengths = []
        recommendations = []
        
        # Check for imports
        if "import" in code:
            strengths.append("Proper imports are present")
        else:
            issues.append("Missing import statements")
            recommendations.append("Add necessary import statements")
        
        # Check for error handling
        if "try:" in code and "except" in code:
            strengths.append("Error handling is implemented")
        else:
            issues.append("Limited error handling")
            recommendations.append("Add comprehensive error handling")
        
        # Check for logging
        if "logging" in code or "log" in code:
            strengths.append("Logging is implemented")
        else:
            issues.append("No logging found")
            recommendations.append("Add logging for better debugging")
        
        # Check for assertions
        if "assert" in code or "expect" in code:
            strengths.append("Test assertions are present")
        else:
            issues.append("Missing test assertions")
            recommendations.append("Add proper test assertions")
        
        # Check for async/await patterns
        if "async def" in code and "await" in code:
            strengths.append("Proper async/await usage")
        
        # Check for documentation
        if '"""' in code or "'''" in code:
            strengths.append("Code documentation is present")
        else:
            issues.append("Limited code documentation")
            recommendations.append("Add comprehensive code documentation")
        
        # Calculate score based on findings
        score = 10
        score -= len(issues) * 0.5
        score = max(1, min(10, score))
        
        review["score"] = score
        review["issues"] = issues
        review["strengths"] = strengths
        review["recommendations"] = recommendations
        
        return review
    
    async def _validate_scenarios(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate test scenarios"""
        scenarios = task_data.get("scenarios", [])
        
        validation_results = {
            "total_scenarios": len(scenarios),
            "valid_scenarios": 0,
            "invalid_scenarios": 0,
            "scenario_reviews": [],
            "coverage_gaps": [],
            "recommendations": []
        }
        
        for i, scenario in enumerate(scenarios):
            scenario_review = self._validate_single_scenario(scenario, i)
            validation_results["scenario_reviews"].append(scenario_review)
            
            if scenario_review["is_valid"]:
                validation_results["valid_scenarios"] += 1
            else:
                validation_results["invalid_scenarios"] += 1
        
        # Analyze coverage gaps
        validation_results["coverage_gaps"] = self._identify_coverage_gaps(scenarios)
        validation_results["recommendations"] = self._generate_scenario_recommendations(validation_results)
        
        return validation_results
    
    def _validate_single_scenario(self, scenario: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate a single test scenario"""
        review = {
            "scenario_index": index,
            "scenario_name": scenario.get("name", f"Scenario {index}"),
            "is_valid": True,
            "issues": [],
            "strengths": [],
            "completeness_score": 0
        }
        
        required_fields = ["name", "description", "test_steps"]
        optional_fields = ["priority", "expected_results", "test_data"]
        
        # Check required fields
        missing_required = [field for field in required_fields if field not in scenario]
        if missing_required:
            review["issues"].extend([f"Missing required field: {field}" for field in missing_required])
            review["is_valid"] = False
        
        # Check test steps
        test_steps = scenario.get("test_steps", [])
        if not test_steps:
            review["issues"].append("No test steps defined")
            review["is_valid"] = False
        elif len(test_steps) < 2:
            review["issues"].append("Insufficient test steps (minimum 2 required)")
        else:
            review["strengths"].append(f"Good test step coverage ({len(test_steps)} steps)")
        
        # Check for expected results
        if "expected_results" in scenario:
            review["strengths"].append("Expected results are defined")
        else:
            review["issues"].append("Missing expected results")
        
        # Calculate completeness score
        total_fields = len(required_fields) + len(optional_fields)
        present_fields = len([field for field in required_fields + optional_fields if field in scenario])
        review["completeness_score"] = (present_fields / total_fields) * 100
        
        return review
    
    def _identify_coverage_gaps(self, scenarios: List[Dict[str, Any]]) -> List[str]:
        """Identify test coverage gaps"""
        gaps = []
        
        # Check for common test types
        scenario_names = [s.get("name", "").lower() for s in scenarios]
        scenario_descriptions = [s.get("description", "").lower() for s in scenarios]
        all_text = " ".join(scenario_names + scenario_descriptions)
        
        # Common test coverage areas
        coverage_areas = {
            "login": ["login", "authentication", "signin"],
            "navigation": ["navigate", "menu", "link", "page"],
            "form_submission": ["form", "submit", "input", "field"],
            "error_handling": ["error", "invalid", "failure", "exception"],
            "security": ["security", "permission", "access", "unauthorized"],
            "performance": ["performance", "load", "speed", "timeout"],
            "mobile": ["mobile", "responsive", "touch", "device"]
        }
        
        for area, keywords in coverage_areas.items():
            if not any(keyword in all_text for keyword in keywords):
                gaps.append(f"Missing {area.replace('_', ' ')} test coverage")
        
        return gaps
    
    def _generate_scenario_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for scenario improvements"""
        recommendations = []
        
        if validation_results["invalid_scenarios"] > 0:
            recommendations.append("Fix invalid scenarios before proceeding with test generation")
        
        if validation_results["coverage_gaps"]:
            recommendations.append("Address identified coverage gaps to improve test completeness")
        
        avg_completeness = sum(r["completeness_score"] for r in validation_results["scenario_reviews"]) / len(validation_results["scenario_reviews"]) if validation_results["scenario_reviews"] else 0
        
        if avg_completeness < 70:
            recommendations.append("Improve scenario completeness by adding missing fields and details")
        
        return recommendations
    
    async def _assess_quality(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall code quality"""
        # This would integrate with the review functionality
        return await self._review_tests(task_data)
    
    async def _analyze_coverage(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test coverage"""
        scenarios = task_data.get("scenarios", [])
        test_files = task_data.get("test_files", [])
        
        coverage_analysis = {
            "scenario_coverage": len(scenarios),
            "test_file_coverage": len(test_files),
            "coverage_areas": {},
            "recommendations": []
        }
        
        # Analyze different types of coverage
        if scenarios:
            coverage_analysis["coverage_areas"] = self._analyze_scenario_coverage(scenarios)
        
        return coverage_analysis
    
    def _analyze_scenario_coverage(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze coverage across different areas"""
        coverage = {
            "functional": 0,
            "ui": 0,
            "api": 0,
            "integration": 0,
            "error_handling": 0,
            "security": 0,
            "performance": 0
        }
        
        for scenario in scenarios:
            text = f"{scenario.get('name', '')} {scenario.get('description', '')}".lower()
            
            if any(keyword in text for keyword in ["function", "feature", "business"]):
                coverage["functional"] += 1
            if any(keyword in text for keyword in ["ui", "interface", "click", "form"]):
                coverage["ui"] += 1
            if any(keyword in text for keyword in ["api", "endpoint", "request", "response"]):
                coverage["api"] += 1
            if any(keyword in text for keyword in ["integration", "workflow", "end-to-end"]):
                coverage["integration"] += 1
            if any(keyword in text for keyword in ["error", "invalid", "failure"]):
                coverage["error_handling"] += 1
            if any(keyword in text for keyword in ["security", "permission", "access"]):
                coverage["security"] += 1
            if any(keyword in text for keyword in ["performance", "load", "speed"]):
                coverage["performance"] += 1
        
        return coverage
    
    async def _generate_report(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive review report"""
        # This would combine all review results into a comprehensive report
        review_data = task_data.get("review_data", {})
        
        report = {
            "report_type": "comprehensive_review",
            "generated_at": datetime.now().isoformat(),
            "summary": review_data.get("summary", {}),
            "detailed_findings": review_data.get("reviews", []),
            "recommendations": review_data.get("recommendations", []),
            "metrics": self._calculate_quality_metrics(review_data)
        }
        
        # Save comprehensive report
        report_filename = f"comprehensive_review_report_{int(time.time())}.json"
        report_path = self.save_work_artifact(report_filename, json.dumps(report, indent=2))
        
        return {
            "report": report,
            "report_path": report_path
        }
    
    def _calculate_overall_score(self, reviews: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score"""
        if not reviews:
            return 0
        
        total_score = sum(review.get("score", 0) for review in reviews)
        return round(total_score / len(reviews), 2)
    
    def _generate_review_summary(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate review summary"""
        if not reviews:
            return {}
        
        total_issues = sum(len(review.get("issues", [])) for review in reviews)
        total_strengths = sum(len(review.get("strengths", [])) for review in reviews)
        
        return {
            "total_files_reviewed": len(reviews),
            "average_score": self._calculate_overall_score(reviews),
            "total_issues_found": total_issues,
            "total_strengths_identified": total_strengths,
            "files_needing_improvement": len([r for r in reviews if r.get("score", 0) < 7])
        }
    
    def _generate_recommendations(self, reviews: List[Dict[str, Any]]) -> List[str]:
        """Generate overall recommendations"""
        all_recommendations = []
        for review in reviews:
            all_recommendations.extend(review.get("recommendations", []))
        
        # Remove duplicates and prioritize
        unique_recommendations = list(set(all_recommendations))
        return unique_recommendations[:10]  # Top 10 recommendations
    
    def _calculate_quality_metrics(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality metrics"""
        reviews = review_data.get("reviews", [])
        
        if not reviews:
            return {}
        
        return {
            "code_quality_score": self._calculate_overall_score(reviews),
            "maintainability_index": min(10, sum(r.get("score", 0) for r in reviews) / len(reviews)),
            "test_coverage_score": len(reviews) * 2,  # Simple metric
            "reliability_score": max(1, 10 - sum(len(r.get("issues", [])) for r in reviews) / len(reviews))
        }


# Helper functions for code analysis
def analyze_code_complexity(code: str) -> Dict[str, Any]:
    """Analyze code complexity metrics"""
    lines = code.split('\n')
    
    return {
        "total_lines": len(lines),
        "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
        "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
        "function_count": code.count('def '),
        "class_count": code.count('class '),
        "complexity_score": min(10, max(1, 10 - (code.count('if ') + code.count('for ') + code.count('while ')) / 10))
    }


def check_security_issues(code: str) -> List[str]:
    """Check for potential security issues"""
    issues = []
    
    # Basic security checks
    if "eval(" in code:
        issues.append("Potential security risk: eval() usage")
    
    if "exec(" in code:
        issues.append("Potential security risk: exec() usage")
    
    if "shell=True" in code:
        issues.append("Potential security risk: shell=True in subprocess")
    
    if "password" in code.lower() and "=" in code:
        issues.append("Potential security risk: hardcoded password")

    return issues


# =============================================================================
# LLM-POWERED INTELLIGENT REVIEW METHODS
# =============================================================================

class IntelligentReviewMixin:
    """Mixin class providing LLM-powered review capabilities"""

    async def review_with_llm(
        self,
        code: str,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use LLM to perform semantic code review.

        This method goes beyond string matching to actually understand:
        - Whether the test validates the requirement
        - If assertions are meaningful and complete
        - If the test flow makes logical sense
        - Missing edge cases and error scenarios
        """
        import json

        prompt = f"""
Perform a comprehensive code review of the following test code against the requirements.

## Test Code:
```python
{code}
```

## Original Requirements:
{json.dumps(requirements, indent=2, default=str)}

## Additional Context:
{json.dumps(context, indent=2, default=str) if context else "None provided"}

## Review Criteria:
Analyze the code and provide detailed feedback on:

1. **Requirement Coverage** (1-10): Does the test actually verify the requirement?
2. **Assertion Quality** (1-10): Are the assertions meaningful and complete?
3. **Logic Flow** (1-10): Does the test flow make logical sense?
4. **Error Handling** (1-10): Are error scenarios properly handled?
5. **Maintainability** (1-10): Is the code readable and maintainable?
6. **Security** (1-10): Are there any security concerns?

Provide your review in JSON format:
{{
    "overall_score": 1-10,
    "requirement_verified": true/false,
    "requirement_coverage_explanation": "Detailed explanation",
    "scores": {{
        "requirement_coverage": 1-10,
        "assertion_quality": 1-10,
        "logic_flow": 1-10,
        "error_handling": 1-10,
        "maintainability": 1-10,
        "security": 1-10
    }},
    "issues": [
        {{
            "severity": "critical/major/minor/suggestion",
            "category": "logic/assertion/security/style/performance",
            "description": "Description of the issue",
            "line_hint": "approximate location or context",
            "suggested_fix": "How to fix it"
        }}
    ],
    "strengths": ["List of things done well"],
    "missing_scenarios": ["Edge cases or scenarios not covered"],
    "improvement_suggestions": [
        {{
            "priority": "high/medium/low",
            "suggestion": "What to improve",
            "code_example": "Example code if applicable"
        }}
    ],
    "overall_assessment": "Summary paragraph of the review"
}}
"""

        try:
            response = await self.generate_llm_response(
                prompt=prompt,
                response_format="json",
                temperature=0.3
            )

            if response.get("success") and response.get("json_parse_success"):
                return {
                    "status": "success",
                    "review": response.get("parsed_json", {}),
                    "llm_powered": True
                }
            elif response.get("success"):
                return {
                    "status": "partial",
                    "raw_review": response.get("response", ""),
                    "llm_powered": True,
                    "parse_error": "Could not parse structured response"
                }
            else:
                return await self._fallback_code_review(code)

        except Exception as e:
            logging.error(f"LLM review failed: {e}")
            return await self._fallback_code_review(code)

    async def _fallback_code_review(self, code: str) -> Dict[str, Any]:
        """Fallback to basic review when LLM is unavailable"""
        return {
            "status": "fallback",
            "llm_powered": False,
            "review": await self._review_code_snippet(code),
            "note": "LLM unavailable - using basic heuristic review"
        }

    async def validate_requirement_coverage_with_llm(
        self,
        test_code: str,
        requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use LLM to validate if test code covers all requirements.
        """
        import json

        prompt = f"""
Analyze if the following test code adequately covers the specified requirements.

## Test Code:
```python
{test_code}
```

## Requirements to Verify:
{json.dumps(requirements, indent=2, default=str)}

## Analysis Required:
For each requirement, determine:
1. Is it covered by the test? (yes/partial/no)
2. Which test assertions verify it?
3. What's missing for complete coverage?

Return JSON:
{{
    "overall_coverage_percentage": 0-100,
    "requirements_analysis": [
        {{
            "requirement_id": "ID or description",
            "coverage_status": "covered/partial/not_covered",
            "covering_assertions": ["List of assertions that cover this"],
            "gaps": ["What's missing"],
            "confidence": "high/medium/low"
        }}
    ],
    "uncovered_requirements": ["List of requirements not covered"],
    "recommendations": ["How to improve coverage"]
}}
"""

        try:
            response = await self.generate_llm_response(
                prompt=prompt,
                response_format="json",
                temperature=0.2
            )

            if response.get("success") and response.get("json_parse_success"):
                return response.get("parsed_json", {})
            return {
                "overall_coverage_percentage": 0,
                "requirements_analysis": [],
                "error": "Could not perform LLM analysis"
            }

        except Exception as e:
            logging.error(f"Requirement coverage validation failed: {e}")
            return {"error": str(e)}

    async def suggest_improvements_with_llm(
        self,
        code: str,
        review_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to generate specific code improvements.
        """
        import json

        prompt = f"""
Based on the code review results, generate specific code improvements.

## Original Code:
```python
{code}
```

## Review Results:
{json.dumps(review_results, indent=2, default=str)}

## Generate Improvements:
For each issue found, provide specific code fixes.

Return JSON array:
[
    {{
        "issue": "What issue this addresses",
        "priority": "critical/high/medium/low",
        "original_code": "The problematic code snippet",
        "improved_code": "The fixed code snippet",
        "explanation": "Why this improvement helps"
    }}
]
"""

        try:
            response = await self.generate_llm_response(
                prompt=prompt,
                response_format="json",
                temperature=0.3
            )

            if response.get("success") and response.get("json_parse_success"):
                improvements = response.get("parsed_json", [])
                if isinstance(improvements, list):
                    return improvements
            return []

        except Exception as e:
            logging.error(f"Improvement suggestion failed: {e}")
            return []


# Extend ReviewAgent with LLM capabilities
ReviewAgent.review_with_llm = IntelligentReviewMixin.review_with_llm
ReviewAgent.validate_requirement_coverage_with_llm = IntelligentReviewMixin.validate_requirement_coverage_with_llm
ReviewAgent.suggest_improvements_with_llm = IntelligentReviewMixin.suggest_improvements_with_llm
ReviewAgent._fallback_code_review = IntelligentReviewMixin._fallback_code_review


if __name__ == "__main__":
    # Example usage
    import asyncio
    from models.local_ai_provider import LocalAIProvider
    
    async def test_review_agent():
        provider = LocalAIProvider()
        agent = ReviewAgent(local_ai_provider=provider)
        
        # Test code review
        test_code = '''
import pytest
from playwright.async_api import async_playwright

async def test_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        await page.click("#login")
        await browser.close()
'''
        
        result = await agent.process_task({
            "type": "review_code",
            "test_code": test_code
        })
        
        print("Review Result:", result)
    
    # Run test
    # asyncio.run(test_review_agent())

