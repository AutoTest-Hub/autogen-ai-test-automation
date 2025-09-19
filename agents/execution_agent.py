#!/usr/bin/env python3
"""
Execution Agent for AutoGen Test Automation Framework
Responsible for executing tests and managing test runs
"""

import json
import os
import subprocess
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from agents.base_agent import BaseTestAgent
from config.settings import AgentRole, TestFramework


class ExecutionAgent(BaseTestAgent):
    """Agent responsible for executing tests and managing test runs"""
    
    def __init__(self, **kwargs):
        system_message = """
You are the Execution Agent, an expert in test execution and test environment management. Your responsibilities include:

1. **Test Execution**: Execute test suites and individual tests across different frameworks
2. **Environment Management**: Set up and manage test environments and dependencies
3. **Parallel Execution**: Coordinate parallel test execution for efficiency
4. **Result Collection**: Collect and process test execution results
5. **Error Handling**: Handle test failures and execution errors gracefully
6. **Resource Management**: Manage test resources, browsers, and cleanup

**Key Capabilities**:
- Execute Playwright, Selenium, and API tests
- Manage test environments and dependencies
- Coordinate parallel test execution
- Monitor test execution progress
- Collect detailed execution results
- Handle test failures and retries
- Generate execution reports

**Execution Strategies**:
- Sequential execution for stability
- Parallel execution for speed
- Distributed execution for scale
- Retry mechanisms for reliability
- Resource optimization
- Environment isolation

**Output Format**: Always provide structured execution results with:
- Execution status and summary
- Detailed test results
- Performance metrics
- Error details and logs
- Resource usage statistics
- Recommendations for optimization
"""
        
        super().__init__(
            role=AgentRole.EXECUTION,
            system_message=system_message,
            **kwargs
        )
        
        # Register execution functions
        self.register_function(
            func=self._execute_suite,
            description="Execute a complete test suite"
        )
        
        self.register_function(
            func=self._execute_tests,
            description="Execute a single test file"
        )
        
        self.register_function(
            func=self._setup_environment,
            description="Set up test environment and dependencies"
        )
        
        self.register_function(
            func=self._monitor_progress,
            description="Monitor test execution progress"
        )
        
        self.register_function(
            func=self._collect_test_results,
            description="Collect and process test execution results"
        )
        
        # Execution state tracking
        self.execution_state = {
            "current_execution": None,
            "running_tests": [],
            "completed_tests": [],
            "failed_tests": [],
            "execution_start_time": None,
            "total_tests": 0
        }
        
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "execute_test_suite",
            "execute_single_test",
            "setup_test_environment",
            "monitor_execution",
            "collect_results"
        ]
        
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process execution task"""
        try:
            self.update_state("processing")
            
            task_type = task_data.get("task_type", task_data.get("type", "execute_tests"))
            
            if task_type == "execute_tests":
                result = await self._execute_tests(task_data)
            elif task_type == "execute_suite":
                result = await self._execute_suite(task_data)
            elif task_type == "setup_environment":
                result = await self._setup_environment(task_data)
            elif task_type == "monitor_progress":
                result = await self._monitor_progress(task_data)
            elif task_type == "collect_results":
                result = await self._collect_test_results(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.update_state("completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing execution task: {e}")
            self.update_state("error")
            raise
    
    async def _execute_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tests based on task data"""
        # Handle both old format (test_files) and new format (review_results)
        test_files = task_data.get("test_files", [])
        test_suite_path = task_data.get("test_suite_path", "")
        execution_config = task_data.get("execution_config", {})
        review_results = task_data.get("review_results", {})
        headless = task_data.get("headless", True)  # Extract headless parameter
        
        # Add headless to execution config
        execution_config["headless"] = headless
        
        # Extract test files from review_results if available
        if review_results and not test_files:
            # Look for generated_test_files
            generated_files = review_results.get("generated_test_files", [])
            if generated_files:
                test_files = generated_files
            else:
                # Look for login_test or other test files
                if review_results.get("login_test"):
                    test_files.append(review_results["login_test"])
        
        # If still no test files, look for all test files in tests directory
        if not test_files:
            tests_dir = Path("tests")
            if tests_dir.exists():
                test_files = [str(f) for f in tests_dir.glob("test_*.py") if f.is_file()]
        
        self.logger.info(f"Executing tests: {len(test_files)} files")
        
        # Initialize execution state
        self.execution_state["execution_start_time"] = datetime.now()
        self.execution_state["total_tests"] = len(test_files)
        self.execution_state["running_tests"] = []
        self.execution_state["completed_tests"] = []
        self.execution_state["failed_tests"] = []
        
        execution_results = {
            "execution_id": f"exec_{int(time.time())}",
            "start_time": self.execution_state["execution_start_time"].isoformat(),
            "test_results": [],
            "summary": {},
            "performance_metrics": {},
            "errors": []
        }
        
        # Set up test environment
        env_setup = await self._setup_test_environment({})
        if not env_setup.get("success", False):
            execution_results["errors"].append("Failed to set up test environment")
            return execution_results
        
        # Execute tests
        if test_suite_path and os.path.exists(test_suite_path):
            # Execute test suite
            suite_result = await self._execute_test_suite_file(test_suite_path, execution_config)
            execution_results["test_results"].append(suite_result)
        else:
            # Execute individual test files
            for test_file in test_files:
                if os.path.exists(test_file):
                    test_result = await self._execute_single_test_file(test_file, execution_config)
                    execution_results["test_results"].append(test_result)
                else:
                    self.logger.warning(f"Test file not found: {test_file}")
                    execution_results["errors"].append(f"Test file not found: {test_file}")
        
        # Calculate summary and metrics
        execution_results["end_time"] = datetime.now().isoformat()
        execution_results["summary"] = self._calculate_execution_summary(execution_results["test_results"])
        execution_results["performance_metrics"] = self._calculate_performance_metrics(execution_results)
        
        # Save execution results
        results_filename = f"execution_results_{execution_results['execution_id']}.json"
        results_path = self.save_work_artifact(results_filename, json.dumps(execution_results, indent=2))
        
        return {
            "execution_results": execution_results,
            "results_path": results_path,
            "summary": execution_results["summary"],
            "success": execution_results["summary"].get("success_rate", 0) > 0,
            "test_files": test_files
        }
    
    async def _execute_test_suite_file(self, suite_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a test suite file"""
        self.logger.info(f"Executing test suite: {suite_path}")
        
        result = {
            "test_file": suite_path,
            "test_type": "suite",
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "output": "",
            "errors": [],
            "metrics": {}
        }
        
        try:
            # Determine execution command based on file type
            if suite_path.endswith('.py'):
                # Python test suite
                cmd = ["python", suite_path]
                if config.get("verbose", False):
                    cmd.append("-v")
            else:
                result["errors"].append(f"Unsupported test suite type: {suite_path}")
                result["status"] = "failed"
                return result
            
            # Execute the test suite
            start_time = time.time()
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="."  # Always run from project root directory
            )
            
            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time
            
            result["end_time"] = datetime.now().isoformat()
            result["execution_time"] = execution_time
            result["return_code"] = process.returncode
            result["output"] = stdout.decode('utf-8') if stdout else ""
            result["stderr"] = stderr.decode('utf-8') if stderr else ""
            
            # Determine status based on return code
            if process.returncode == 0:
                result["status"] = "passed"
                self.execution_state["completed_tests"].append(suite_path)
            else:
                result["status"] = "failed"
                result["errors"].append(f"Test suite failed with return code: {process.returncode}")
                self.execution_state["failed_tests"].append(suite_path)
            
            # Extract metrics from output
            result["metrics"] = self._extract_test_metrics(result["output"])
            
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"Execution error: {str(e)}")
            result["end_time"] = datetime.now().isoformat()
            self.execution_state["failed_tests"].append(suite_path)
        
        return result
    
    async def _execute_single_test_file(self, test_file: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test file"""
        self.logger.info(f"Executing test file: {test_file}")
        
        result = {
            "test_file": test_file,
            "test_type": "single",
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "output": "",
            "errors": [],
            "metrics": {}
        }
        
        try:
            # Determine execution command based on file type and framework
            cmd = self._build_execution_command(test_file, config)
            
            if not cmd:
                result["errors"].append(f"Unable to determine execution command for: {test_file}")
                result["status"] = "failed"
                return result
            
            # Execute the test
            start_time = time.time()
            
            # Set up environment variables for test configuration
            env = os.environ.copy()
            headless = config.get("headless", True)
            env["PYTEST_HEADLESS"] = "true" if headless else "false"
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=".",  # Always run from project root directory
                env=env
            )
            
            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time
            
            result["end_time"] = datetime.now().isoformat()
            result["execution_time"] = execution_time
            result["return_code"] = process.returncode
            result["output"] = stdout.decode('utf-8') if stdout else ""
            result["stderr"] = stderr.decode('utf-8') if stderr else ""
            
            # Determine status based on return code and output
            if process.returncode == 0:
                result["status"] = "passed"
                self.execution_state["completed_tests"].append(test_file)
            else:
                result["status"] = "failed"
                result["errors"].append(f"Test failed with return code: {process.returncode}")
                self.execution_state["failed_tests"].append(test_file)
            
            # Extract metrics from output
            result["metrics"] = self._extract_test_metrics(result["output"])
            
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"Execution error: {str(e)}")
            result["end_time"] = datetime.now().isoformat()
            self.execution_state["failed_tests"].append(test_file)
        
        return result
    
    def _build_execution_command(self, test_file: str, config: Dict[str, Any]) -> List[str]:
        """Build execution command based on test file type"""
        file_path = Path(test_file)
        
        if file_path.suffix == '.py':
            # Python test file
            if 'pytest' in open(test_file).read():
                # Pytest-based test
                cmd = ["python", "-m", "pytest", test_file]
                if config.get("verbose", False):
                    cmd.append("-v")
                if config.get("html_report", False):
                    cmd.extend(["--html", f"report_{file_path.stem}.html"])
                
                # Set headless mode via environment variable for conftest.py to read
                # This way conftest.py can configure the browser appropriately
            else:
                # Regular Python test
                cmd = ["python", test_file]
        elif file_path.suffix == '.js':
            # JavaScript test file
            if 'jest' in config.get("framework", ""):
                cmd = ["npm", "run", "test", test_file]
            else:
                cmd = ["node", test_file]
        else:
            # Unknown file type
            return []
        
        return cmd
    
    def _extract_test_metrics(self, output: str) -> Dict[str, Any]:
        """Extract test metrics from execution output"""
        metrics = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "assertions": 0,
            "coverage": 0
        }
        
        # Parse pytest output
        if "passed" in output or "failed" in output:
            lines = output.split('\n')
            for line in lines:
                if "passed" in line and "failed" in line:
                    # Parse summary line like "5 passed, 2 failed"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            metrics["tests_passed"] = int(parts[i-1])
                        elif part == "failed" and i > 0:
                            metrics["tests_failed"] = int(parts[i-1])
                        elif part == "skipped" and i > 0:
                            metrics["tests_skipped"] = int(parts[i-1])
        
        metrics["tests_run"] = metrics["tests_passed"] + metrics["tests_failed"] + metrics["tests_skipped"]
        
        return metrics
    
    async def _setup_test_environment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set up test environment and dependencies"""
        self.logger.info("Setting up test environment")
        
        setup_result = {
            "success": True,
            "steps_completed": [],
            "errors": [],
            "environment_info": {}
        }
        
        try:
            # Check Python environment
            python_version = await self._check_python_version()
            setup_result["environment_info"]["python_version"] = python_version
            setup_result["steps_completed"].append("Python version check")
            
            # Check required packages
            required_packages = ["pytest", "playwright", "selenium", "requests"]
            package_status = await self._check_packages(required_packages)
            setup_result["environment_info"]["packages"] = package_status
            setup_result["steps_completed"].append("Package availability check")
            
            # Install missing packages if needed
            missing_packages = [pkg for pkg, status in package_status.items() if not status]
            if missing_packages and config.get("auto_install", False):
                install_result = await self._install_packages(missing_packages)
                if install_result["success"]:
                    setup_result["steps_completed"].append("Missing packages installed")
                else:
                    setup_result["errors"].extend(install_result["errors"])
            
            # Set up browser drivers if needed
            if config.get("setup_browsers", True):
                browser_setup = await self._setup_browser_drivers()
                setup_result["environment_info"]["browsers"] = browser_setup
                setup_result["steps_completed"].append("Browser drivers setup")
            
            # Create work directories
            work_dirs = ["./work_dir", "./test_results", "./screenshots", "./reports"]
            for work_dir in work_dirs:
                os.makedirs(work_dir, exist_ok=True)
            setup_result["steps_completed"].append("Work directories created")
            
        except Exception as e:
            setup_result["success"] = False
            setup_result["errors"].append(f"Environment setup error: {str(e)}")
        
        return setup_result
    
    async def _check_python_version(self) -> str:
        """Check Python version"""
        try:
            process = await asyncio.create_subprocess_exec(
                "python", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return stdout.decode('utf-8').strip()
        except Exception:
            return "Unknown"
    
    async def _check_packages(self, packages: List[str]) -> Dict[str, bool]:
        """Check if required packages are installed"""
        package_status = {}
        
        for package in packages:
            try:
                process = await asyncio.create_subprocess_exec(
                    "python", "-c", f"import {package}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                package_status[package] = process.returncode == 0
            except Exception:
                package_status[package] = False
        
        return package_status
    
    async def _install_packages(self, packages: List[str]) -> Dict[str, Any]:
        """Install missing packages"""
        install_result = {
            "success": True,
            "installed": [],
            "errors": []
        }
        
        for package in packages:
            try:
                process = await asyncio.create_subprocess_exec(
                    "pip", "install", package,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    install_result["installed"].append(package)
                else:
                    install_result["errors"].append(f"Failed to install {package}: {stderr.decode('utf-8')}")
                    install_result["success"] = False
            except Exception as e:
                install_result["errors"].append(f"Error installing {package}: {str(e)}")
                install_result["success"] = False
        
        return install_result
    
    async def _setup_browser_drivers(self) -> Dict[str, Any]:
        """Set up browser drivers for Selenium/Playwright"""
        browser_setup = {
            "playwright": False,
            "selenium": False,
            "errors": []
        }
        
        try:
            # Install Playwright browsers
            process = await asyncio.create_subprocess_exec(
                "python", "-m", "playwright", "install",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                browser_setup["playwright"] = True
            else:
                browser_setup["errors"].append(f"Playwright setup failed: {stderr.decode('utf-8')}")
        except Exception as e:
            browser_setup["errors"].append(f"Playwright setup error: {str(e)}")
        
        return browser_setup
    
    def _calculate_execution_summary(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate execution summary from test results"""
        if not test_results:
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "success_rate": 0,
                "total_execution_time": 0
            }
        
        total_tests = len(test_results)
        passed = len([r for r in test_results if r.get("status") == "passed"])
        failed = len([r for r in test_results if r.get("status") == "failed"])
        errors = len([r for r in test_results if r.get("status") == "error"])
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        total_execution_time = sum(r.get("execution_time", 0) for r in test_results)
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": round(success_rate, 2),
            "total_execution_time": round(total_execution_time, 2)
        }
    
    def _calculate_performance_metrics(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        test_results = execution_results.get("test_results", [])
        
        if not test_results:
            return {}
        
        execution_times = [r.get("execution_time", 0) for r in test_results if r.get("execution_time")]
        
        return {
            "average_execution_time": round(sum(execution_times) / len(execution_times), 2) if execution_times else 0,
            "fastest_test": round(min(execution_times), 2) if execution_times else 0,
            "slowest_test": round(max(execution_times), 2) if execution_times else 0,
            "total_execution_time": round(sum(execution_times), 2),
            "tests_per_minute": round(len(test_results) / (sum(execution_times) / 60), 2) if sum(execution_times) > 0 else 0
        }
    
    async def _execute_suite(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a test suite"""
        return await self._execute_tests(task_data)
    
    async def _setup_environment(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up test environment"""
        return await self._setup_test_environment(task_data.get("config", {}))
    
    async def _monitor_progress(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor execution progress"""
        return {
            "execution_state": self.execution_state,
            "progress_percentage": self._calculate_progress_percentage(),
            "estimated_completion": self._estimate_completion_time()
        }
    
    def _calculate_progress_percentage(self) -> float:
        """Calculate execution progress percentage"""
        total = self.execution_state.get("total_tests", 0)
        completed = len(self.execution_state.get("completed_tests", []))
        failed = len(self.execution_state.get("failed_tests", []))
        
        if total == 0:
            return 0
        
        return round(((completed + failed) / total) * 100, 2)
    
    def _estimate_completion_time(self) -> Optional[str]:
        """Estimate completion time based on current progress"""
        start_time = self.execution_state.get("execution_start_time")
        if not start_time:
            return None
        
        elapsed = (datetime.now() - start_time).total_seconds()
        progress = self._calculate_progress_percentage()
        
        if progress == 0:
            return None
        
        estimated_total_time = elapsed / (progress / 100)
        remaining_time = estimated_total_time - elapsed
        
        completion_time = datetime.now() + timedelta(seconds=remaining_time)
        return completion_time.isoformat()
    
    async def _collect_test_results(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and process test results"""
        results_dir = task_data.get("results_dir", "./test_results")
        
        collected_results = {
            "collection_time": datetime.now().isoformat(),
            "results_found": [],
            "summary": {},
            "errors": []
        }
        
        try:
            if os.path.exists(results_dir):
                for file in os.listdir(results_dir):
                    if file.endswith('.json') or file.endswith('.xml') or file.endswith('.html'):
                        file_path = os.path.join(results_dir, file)
                        collected_results["results_found"].append(file_path)
            
            collected_results["summary"] = {
                "total_result_files": len(collected_results["results_found"]),
                "collection_successful": True
            }
            
        except Exception as e:
            collected_results["errors"].append(f"Error collecting results: {str(e)}")
            collected_results["summary"]["collection_successful"] = False
        
        return collected_results


if __name__ == "__main__":
    # Example usage
    import asyncio
    from models.local_ai_provider import LocalAIProvider
    
    async def test_execution_agent():
        provider = LocalAIProvider()
        agent = ExecutionAgent(local_ai_provider=provider)
        
        # Test environment setup
        result = await agent.process_task({
            "type": "setup_environment",
            "config": {
                "auto_install": False,
                "setup_browsers": True
            }
        })
        
        print("Environment Setup Result:", result)
    
    # Run test
    # asyncio.run(test_execution_agent())

