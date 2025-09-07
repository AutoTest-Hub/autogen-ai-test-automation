#!/usr/bin/env python3
"""
Reporting Agent for AutoGen Test Automation Framework
Responsible for generating comprehensive test reports and analytics
"""

import json
import os
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import base64

from .base_agent import BaseTestAgent
from config.settings import AgentRole, TestFramework


class ReportingAgent(BaseTestAgent):
    """Agent responsible for generating test reports and analytics"""
    
    def __init__(self, **kwargs):
        system_message = """
You are the Reporting Agent, an expert in test reporting and analytics. Your responsibilities include:

1. **Report Generation**: Generate comprehensive test reports in multiple formats
2. **Data Analysis**: Analyze test execution data and identify trends
3. **Visualization**: Create charts, graphs, and visual representations of test data
4. **Metrics Calculation**: Calculate key testing metrics and KPIs
5. **Trend Analysis**: Identify patterns and trends in test results over time
6. **Stakeholder Communication**: Create reports tailored for different audiences

**Key Capabilities**:
- Generate HTML, PDF, and JSON reports
- Create executive summaries and detailed technical reports
- Analyze test execution trends and patterns
- Calculate quality metrics and KPIs
- Generate visual charts and graphs
- Create dashboard-style reports
- Export data in various formats

**Report Types**:
- Execution Summary Reports
- Detailed Test Results Reports
- Quality Metrics Reports
- Trend Analysis Reports
- Performance Reports
- Coverage Reports
- Executive Dashboards

**Output Format**: Always provide structured reports with:
- Executive summary
- Detailed findings
- Visual representations
- Key metrics and KPIs
- Recommendations and insights
- Historical comparisons
"""
        
        super().__init__(
            role=AgentRole.REPORTING,
            system_message=system_message,
            **kwargs
        )
        
        # Register reporting functions
        self.register_function(
            func=self._create_execution_report,
            description="Generate test execution report"
        )
        
        self.register_function(
            func=self._create_quality_report,
            description="Generate quality metrics report"
        )
        
        self.register_function(
            func=self._create_trend_analysis,
            description="Generate trend analysis report"
        )
        
        self.register_function(
            func=self._create_dashboard,
            description="Generate executive dashboard"
        )
        
        self.register_function(
            func=self._export_test_data,
            description="Export test data in various formats"
        )
        
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "generate_execution_report",
            "generate_quality_report",
            "generate_trend_analysis",
            "generate_dashboard",
            "export_data"
        ]
        
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process reporting task"""
        try:
            self.update_state("processing")
            
            task_type = task_data.get("type", "generate_report")
            
            if task_type == "generate_report":
                result = await self._generate_report(task_data)
            elif task_type == "execution_report":
                result = await self._create_execution_report(task_data)
            elif task_type == "quality_report":
                result = await self._create_quality_report(task_data)
            elif task_type == "trend_analysis":
                result = await self._create_trend_analysis(task_data)
            elif task_type == "dashboard":
                result = await self._create_dashboard(task_data)
            elif task_type == "export_data":
                result = await self._export_test_data(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.update_state("completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing reporting task: {e}")
            self.update_state("error")
            raise
    
    async def _generate_report(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        execution_data = task_data.get("execution_data", {})
        review_data = task_data.get("review_data", {})
        report_config = task_data.get("report_config", {})
        
        self.logger.info("Generating comprehensive test report")
        
        report = {
            "report_id": f"report_{int(time.time())}",
            "generated_at": datetime.now().isoformat(),
            "report_type": "comprehensive",
            "executive_summary": {},
            "test_execution": {},
            "quality_analysis": {},
            "recommendations": [],
            "appendices": {}
        }
        
        # Generate executive summary
        report["executive_summary"] = self._generate_executive_summary(execution_data, review_data)
        
        # Generate test execution section
        report["test_execution"] = self._generate_execution_section(execution_data)
        
        # Generate quality analysis section
        report["quality_analysis"] = self._generate_quality_section(review_data)
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(execution_data, review_data)
        
        # Generate appendices
        report["appendices"] = self._generate_appendices(execution_data, review_data)
        
        # Create HTML report
        html_report = self._create_html_report(report)
        html_filename = f"test_report_{report['report_id']}.html"
        html_path = self.save_work_artifact(html_filename, html_report)
        
        # Create JSON report
        json_filename = f"test_report_{report['report_id']}.json"
        json_path = self.save_work_artifact(json_filename, json.dumps(report, indent=2))
        
        return {
            "report": report,
            "html_report_path": html_path,
            "json_report_path": json_path,
            "report_id": report["report_id"]
        }
    
    def _generate_executive_summary(self, execution_data: Dict[str, Any], review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        summary = execution_data.get("summary", {})
        
        return {
            "test_execution_overview": {
                "total_tests": summary.get("total_tests", 0),
                "success_rate": summary.get("success_rate", 0),
                "execution_time": summary.get("total_execution_time", 0),
                "status": "PASSED" if summary.get("success_rate", 0) >= 80 else "FAILED"
            },
            "quality_overview": {
                "code_quality_score": review_data.get("overall_score", 0),
                "issues_found": len(review_data.get("reviews", [])),
                "recommendations_count": len(review_data.get("recommendations", []))
            },
            "key_findings": self._extract_key_findings(execution_data, review_data),
            "risk_assessment": self._assess_risks(execution_data, review_data)
        }
    
    def _generate_execution_section(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test execution section"""
        return {
            "summary": execution_data.get("summary", {}),
            "performance_metrics": execution_data.get("performance_metrics", {}),
            "test_results": execution_data.get("test_results", []),
            "environment_info": execution_data.get("environment_info", {}),
            "execution_timeline": self._create_execution_timeline(execution_data)
        }
    
    def _generate_quality_section(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quality analysis section"""
        return {
            "overall_score": review_data.get("overall_score", 0),
            "quality_metrics": self._calculate_quality_metrics(review_data),
            "code_reviews": review_data.get("reviews", []),
            "issue_analysis": self._analyze_issues(review_data),
            "improvement_areas": self._identify_improvement_areas(review_data)
        }
    
    def _generate_recommendations(self, execution_data: Dict[str, Any], review_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on data analysis"""
        recommendations = []
        
        # Execution-based recommendations
        summary = execution_data.get("summary", {})
        if summary.get("success_rate", 0) < 80:
            recommendations.append({
                "category": "Test Reliability",
                "priority": "High",
                "recommendation": "Improve test reliability - success rate is below 80%",
                "action_items": [
                    "Review and fix failing tests",
                    "Improve test data management",
                    "Enhance error handling"
                ]
            })
        
        # Performance-based recommendations
        performance = execution_data.get("performance_metrics", {})
        if performance.get("average_execution_time", 0) > 60:
            recommendations.append({
                "category": "Performance",
                "priority": "Medium",
                "recommendation": "Optimize test execution time",
                "action_items": [
                    "Implement parallel execution",
                    "Optimize test setup and teardown",
                    "Review slow-running tests"
                ]
            })
        
        # Quality-based recommendations
        if review_data.get("overall_score", 0) < 7:
            recommendations.append({
                "category": "Code Quality",
                "priority": "High",
                "recommendation": "Improve code quality and maintainability",
                "action_items": [
                    "Address code review findings",
                    "Implement coding standards",
                    "Add comprehensive documentation"
                ]
            })
        
        return recommendations
    
    def _generate_appendices(self, execution_data: Dict[str, Any], review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report appendices"""
        return {
            "detailed_test_results": execution_data.get("test_results", []),
            "environment_details": execution_data.get("environment_info", {}),
            "code_review_details": review_data.get("reviews", []),
            "raw_data": {
                "execution_data": execution_data,
                "review_data": review_data
            }
        }
    
    def _create_html_report(self, report: Dict[str, Any]) -> str:
        """Create HTML report"""
        html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoGen Test Automation Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007acc;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            border-left: 4px solid #007acc;
            background-color: #f9f9f9;
        }}
        .section h2 {{
            color: #007acc;
            margin-top: 0;
            font-size: 1.8em;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007acc;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .status-passed {{
            color: #28a745;
        }}
        .status-failed {{
            color: #dc3545;
        }}
        .recommendations {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }}
        .recommendation {{
            margin-bottom: 15px;
            padding: 10px;
            background-color: white;
            border-radius: 5px;
        }}
        .priority-high {{
            border-left: 4px solid #dc3545;
        }}
        .priority-medium {{
            border-left: 4px solid #ffc107;
        }}
        .priority-low {{
            border-left: 4px solid #28a745;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007acc;
            color: white;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AutoGen Test Automation Report</h1>
            <p>Generated on {generated_at}</p>
            <p>Report ID: {report_id}</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value {status_class}">{total_tests}</div>
                    <div class="metric-label">Total Tests</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value {status_class}">{success_rate}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{execution_time}s</div>
                    <div class="metric-label">Execution Time</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{quality_score}</div>
                    <div class="metric-label">Quality Score</div>
                </div>
            </div>
            
            <h3>Overall Status: <span class="{status_class}">{overall_status}</span></h3>
            
            <h3>Key Findings</h3>
            <ul>
                {key_findings}
            </ul>
        </div>
        
        <div class="section">
            <h2>Test Execution Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test File</th>
                        <th>Status</th>
                        <th>Execution Time</th>
                        <th>Tests Run</th>
                    </tr>
                </thead>
                <tbody>
                    {test_results_table}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            <div class="recommendations">
                {recommendations_html}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by AutoGen Test Automation Framework</p>
            <p>Report generated at {generated_at}</p>
        </div>
    </div>
</body>
</html>
'''
        
        # Extract data for template
        exec_summary = report.get("executive_summary", {})
        test_overview = exec_summary.get("test_execution_overview", {})
        quality_overview = exec_summary.get("quality_overview", {})
        
        # Format data
        total_tests = test_overview.get("total_tests", 0)
        success_rate = test_overview.get("success_rate", 0)
        execution_time = test_overview.get("execution_time", 0)
        quality_score = quality_overview.get("code_quality_score", 0)
        overall_status = test_overview.get("status", "UNKNOWN")
        
        status_class = "status-passed" if overall_status == "PASSED" else "status-failed"
        
        # Format key findings
        key_findings = exec_summary.get("key_findings", [])
        key_findings_html = "".join([f"<li>{finding}</li>" for finding in key_findings])
        
        # Format test results table
        test_results = report.get("test_execution", {}).get("test_results", [])
        test_results_rows = []
        for result in test_results:
            status_class_row = "status-passed" if result.get("status") == "passed" else "status-failed"
            test_results_rows.append(f'''
                <tr>
                    <td>{result.get("test_file", "Unknown")}</td>
                    <td><span class="{status_class_row}">{result.get("status", "Unknown").upper()}</span></td>
                    <td>{result.get("execution_time", 0):.2f}s</td>
                    <td>{result.get("metrics", {}).get("tests_run", 0)}</td>
                </tr>
            ''')
        test_results_table = "".join(test_results_rows)
        
        # Format recommendations
        recommendations = report.get("recommendations", [])
        recommendations_html = ""
        for rec in recommendations:
            priority_class = f"priority-{rec.get('priority', 'medium').lower()}"
            action_items = "".join([f"<li>{item}</li>" for item in rec.get("action_items", [])])
            recommendations_html += f'''
                <div class="recommendation {priority_class}">
                    <h4>{rec.get("category", "General")} - {rec.get("priority", "Medium")} Priority</h4>
                    <p>{rec.get("recommendation", "")}</p>
                    <ul>{action_items}</ul>
                </div>
            '''
        
        # Fill template
        return html_template.format(
            generated_at=report.get("generated_at", ""),
            report_id=report.get("report_id", ""),
            total_tests=total_tests,
            success_rate=success_rate,
            execution_time=execution_time,
            quality_score=quality_score,
            overall_status=overall_status,
            status_class=status_class,
            key_findings=key_findings_html,
            test_results_table=test_results_table,
            recommendations_html=recommendations_html
        )
    
    def _extract_key_findings(self, execution_data: Dict[str, Any], review_data: Dict[str, Any]) -> List[str]:
        """Extract key findings from data"""
        findings = []
        
        summary = execution_data.get("summary", {})
        success_rate = summary.get("success_rate", 0)
        
        if success_rate >= 90:
            findings.append("Excellent test execution with high success rate")
        elif success_rate >= 80:
            findings.append("Good test execution with acceptable success rate")
        else:
            findings.append("Test execution needs improvement - low success rate")
        
        # Quality findings
        quality_score = review_data.get("overall_score", 0)
        if quality_score >= 8:
            findings.append("High code quality maintained")
        elif quality_score >= 6:
            findings.append("Acceptable code quality with room for improvement")
        else:
            findings.append("Code quality needs significant improvement")
        
        # Performance findings
        performance = execution_data.get("performance_metrics", {})
        avg_time = performance.get("average_execution_time", 0)
        if avg_time > 60:
            findings.append("Test execution time is high - consider optimization")
        
        return findings
    
    def _assess_risks(self, execution_data: Dict[str, Any], review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks based on test data"""
        risks = {
            "overall_risk": "LOW",
            "risk_factors": []
        }
        
        summary = execution_data.get("summary", {})
        success_rate = summary.get("success_rate", 0)
        
        if success_rate < 70:
            risks["overall_risk"] = "HIGH"
            risks["risk_factors"].append("Low test success rate indicates potential quality issues")
        elif success_rate < 85:
            risks["overall_risk"] = "MEDIUM"
            risks["risk_factors"].append("Moderate test success rate requires attention")
        
        quality_score = review_data.get("overall_score", 0)
        if quality_score < 6:
            risks["overall_risk"] = "HIGH"
            risks["risk_factors"].append("Low code quality score indicates maintainability risks")
        
        return risks
    
    def _create_execution_timeline(self, execution_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create execution timeline"""
        timeline = []
        test_results = execution_data.get("test_results", [])
        
        for result in test_results:
            timeline.append({
                "test_name": result.get("test_file", "Unknown"),
                "start_time": result.get("start_time", ""),
                "end_time": result.get("end_time", ""),
                "duration": result.get("execution_time", 0),
                "status": result.get("status", "unknown")
            })
        
        return timeline
    
    def _calculate_quality_metrics(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality metrics"""
        reviews = review_data.get("reviews", [])
        
        if not reviews:
            return {}
        
        total_issues = sum(len(review.get("issues", [])) for review in reviews)
        total_strengths = sum(len(review.get("strengths", [])) for review in reviews)
        
        return {
            "average_score": review_data.get("overall_score", 0),
            "total_issues": total_issues,
            "total_strengths": total_strengths,
            "issues_per_file": round(total_issues / len(reviews), 2) if reviews else 0,
            "quality_trend": "improving" if review_data.get("overall_score", 0) > 7 else "needs_attention"
        }
    
    def _analyze_issues(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze issues found in reviews"""
        reviews = review_data.get("reviews", [])
        all_issues = []
        
        for review in reviews:
            all_issues.extend(review.get("issues", []))
        
        # Categorize issues
        issue_categories = {
            "error_handling": 0,
            "documentation": 0,
            "testing": 0,
            "performance": 0,
            "security": 0,
            "other": 0
        }
        
        for issue in all_issues:
            issue_lower = issue.lower()
            if "error" in issue_lower or "exception" in issue_lower:
                issue_categories["error_handling"] += 1
            elif "documentation" in issue_lower or "comment" in issue_lower:
                issue_categories["documentation"] += 1
            elif "test" in issue_lower or "assert" in issue_lower:
                issue_categories["testing"] += 1
            elif "performance" in issue_lower or "slow" in issue_lower:
                issue_categories["performance"] += 1
            elif "security" in issue_lower:
                issue_categories["security"] += 1
            else:
                issue_categories["other"] += 1
        
        return {
            "total_issues": len(all_issues),
            "issue_categories": issue_categories,
            "most_common_category": max(issue_categories, key=issue_categories.get)
        }
    
    def _identify_improvement_areas(self, review_data: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement"""
        areas = []
        issue_analysis = self._analyze_issues(review_data)
        categories = issue_analysis.get("issue_categories", {})
        
        for category, count in categories.items():
            if count > 0:
                areas.append(f"{category.replace('_', ' ').title()}: {count} issues found")
        
        return areas
    
    async def _create_execution_report(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution-focused report"""
        return await self._generate_report(task_data)
    
    async def _create_quality_report(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create quality-focused report"""
        return await self._generate_report(task_data)
    
    async def _create_trend_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create trend analysis report"""
        historical_data = task_data.get("historical_data", [])
        
        trend_analysis = {
            "analysis_period": f"{len(historical_data)} executions",
            "trends": {},
            "insights": [],
            "predictions": {}
        }
        
        if historical_data:
            # Analyze success rate trend
            success_rates = [data.get("summary", {}).get("success_rate", 0) for data in historical_data]
            trend_analysis["trends"]["success_rate"] = {
                "current": success_rates[-1] if success_rates else 0,
                "average": sum(success_rates) / len(success_rates) if success_rates else 0,
                "trend": "improving" if len(success_rates) > 1 and success_rates[-1] > success_rates[0] else "declining"
            }
            
            # Analyze execution time trend
            exec_times = [data.get("performance_metrics", {}).get("total_execution_time", 0) for data in historical_data]
            trend_analysis["trends"]["execution_time"] = {
                "current": exec_times[-1] if exec_times else 0,
                "average": sum(exec_times) / len(exec_times) if exec_times else 0,
                "trend": "improving" if len(exec_times) > 1 and exec_times[-1] < exec_times[0] else "declining"
            }
        
        return trend_analysis
    
    async def _create_dashboard(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive dashboard"""
        dashboard = {
            "dashboard_type": "executive",
            "widgets": [],
            "kpis": {},
            "alerts": []
        }
        
        # Add KPI widgets
        execution_data = task_data.get("execution_data", {})
        summary = execution_data.get("summary", {})
        
        dashboard["kpis"] = {
            "test_success_rate": summary.get("success_rate", 0),
            "total_tests_executed": summary.get("total_tests", 0),
            "average_execution_time": execution_data.get("performance_metrics", {}).get("average_execution_time", 0),
            "quality_score": task_data.get("review_data", {}).get("overall_score", 0)
        }
        
        # Add alerts for critical issues
        if summary.get("success_rate", 0) < 80:
            dashboard["alerts"].append({
                "level": "critical",
                "message": "Test success rate is below 80%",
                "action": "Review and fix failing tests"
            })
        
        return dashboard
    
    async def _export_test_data(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export test data in various formats"""
        export_format = task_data.get("format", "json")
        data = task_data.get("data", {})
        
        export_result = {
            "format": export_format,
            "exported_files": [],
            "success": True
        }
        
        try:
            if export_format == "json":
                filename = f"test_data_export_{int(time.time())}.json"
                file_path = self.save_work_artifact(filename, json.dumps(data, indent=2))
                export_result["exported_files"].append(file_path)
            
            elif export_format == "csv":
                # Convert data to CSV format (simplified)
                csv_content = self._convert_to_csv(data)
                filename = f"test_data_export_{int(time.time())}.csv"
                file_path = self.save_work_artifact(filename, csv_content)
                export_result["exported_files"].append(file_path)
            
        except Exception as e:
            export_result["success"] = False
            export_result["error"] = str(e)
        
        return export_result
    
    def _convert_to_csv(self, data: Dict[str, Any]) -> str:
        """Convert data to CSV format"""
        # Simplified CSV conversion
        csv_lines = ["Field,Value"]
        
        def flatten_dict(d, prefix=""):
            for key, value in d.items():
                if isinstance(value, dict):
                    yield from flatten_dict(value, f"{prefix}{key}.")
                else:
                    yield f"{prefix}{key},{value}"
        
        csv_lines.extend(flatten_dict(data))
        return "\n".join(csv_lines)


if __name__ == "__main__":
    # Example usage
    import asyncio
    from models.local_ai_provider import LocalAIProvider
    
    async def test_reporting_agent():
        provider = LocalAIProvider()
        agent = ReportingAgent(local_ai_provider=provider)
        
        # Test report generation
        sample_execution_data = {
            "summary": {
                "total_tests": 10,
                "success_rate": 85.0,
                "total_execution_time": 45.2
            },
            "performance_metrics": {
                "average_execution_time": 4.52
            },
            "test_results": [
                {
                    "test_file": "test_login.py",
                    "status": "passed",
                    "execution_time": 3.2,
                    "metrics": {"tests_run": 3}
                }
            ]
        }
        
        sample_review_data = {
            "overall_score": 8.5,
            "reviews": [
                {
                    "filename": "test_login.py",
                    "score": 8.5,
                    "issues": ["Missing error handling"],
                    "strengths": ["Good test structure"]
                }
            ]
        }
        
        result = await agent.process_task({
            "type": "generate_report",
            "execution_data": sample_execution_data,
            "review_data": sample_review_data
        })
        
        print("Report Generation Result:", result)
    
    # Run test
    # asyncio.run(test_reporting_agent())

