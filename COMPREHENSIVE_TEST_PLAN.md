# Comprehensive Test Plan: AI Test Automation Platform
## Hybrid Architecture & Agent Functionality Validation

**Test Plan Version:** 1.0  
**Date:** September 26, 2025  
**Scope:** Complete E2E validation of hybrid file + database architecture with agent functionality  

---

## 🎯 Test Objectives

### Primary Objectives
1. **Validate Hybrid Architecture**: Verify files are generated AND metadata is stored in database
2. **Verify Agent Functionality**: Confirm each agent produces actual, meaningful output
3. **Test Complete Workflow**: End-to-end user journey from login to test execution
4. **Validate File Quality**: Ensure generated Playwright tests are executable and well-structured

### Success Criteria
- ✅ All 4 agents complete successfully with real outputs
- ✅ Test files generated with proper Playwright syntax
- ✅ Database metadata stored correctly with file paths
- ✅ Generated tests are executable (even if they fail due to template logic)
- ✅ UI workflow functions without errors

---

## 📋 Test Environment Setup

### Prerequisites
```bash
# 1. Platform Dependencies
cd /home/ubuntu/autogen-ai-test-automation
sudo systemctl start postgresql
pip3 install pytest playwright

# 2. Storage Configuration
export STORAGE_TYPE=local
export STORAGE_BASE_PATH=/opt/test-automation-platform/data

# 3. Database Verification
sudo -u postgres psql -d test_automation_platform -c "SELECT COUNT(*) FROM test_cases;"
```

### Test Data
- **Application**: E-commerce Demo (https://demo.opencart.com)
- **User**: demo / demo123
- **Test Type**: Functional testing
- **Expected Scenarios**: 7-8 test scenarios

---

## 🧪 Test Cases

### TC001: Platform Startup & Health Check
**Objective**: Verify platform starts correctly and all services are accessible

| Step | Action | Expected Result | Validation Method |
|------|--------|----------------|-------------------|
| 1 | Start platform with `./start-platform-enterprise.sh` | Platform starts without errors | Check process status |
| 2 | Wait 30 seconds for startup | Frontend accessible at localhost:5173 | `curl -s http://localhost:5173 \| grep "AI Test Automation"` |
| 3 | Check backend health | Backend responds at localhost:8000 | `curl -s http://localhost:8000/health` |
| 4 | Verify database connection | Database accessible | `sudo -u postgres psql -d test_automation_platform -c "SELECT 1;"` |

**Pass Criteria**: All services respond correctly within 30 seconds

---

### TC002: User Authentication
**Objective**: Verify login functionality works correctly

| Step | Action | Expected Result | Validation Method |
|------|--------|----------------|-------------------|
| 1 | Navigate to http://localhost:5173 | Login page displays | Visual verification |
| 2 | Click "Admin Demo" button | Demo credentials populated | Check form fields |
| 3 | Enter username: "demo" | Username field populated | Visual verification |
| 4 | Enter password: "demo123" | Password field populated | Visual verification |
| 5 | Click "Sign In" button | Login successful, dashboard loads | Check for dashboard elements |
| 6 | Verify user session | User authenticated | Check for logout option |

**Pass Criteria**: Successful login with access to dashboard

---

### TC003: Test Creation Initiation
**Objective**: Verify test creation workflow starts correctly

| Step | Action | Expected Result | Validation Method |
|------|--------|----------------|-------------------|
| 1 | Click "Create Tests" button | Test creation page loads | Check page title/content |
| 2 | Select "E-commerce Demo" scenario | Scenario details populate | Verify form fields filled |
| 3 | Review application details | URL, features, flows displayed | Visual verification |
| 4 | Click "Create Tests" button | Success message appears | Check for "Test creation started successfully!" |
| 5 | Verify agent status panel | Agent activity monitor visible | Check for 4 agents listed |

**Pass Criteria**: Test creation initiated with success message and agent monitor visible

---

### TC004: Discovery Agent Validation
**Objective**: Verify Discovery Agent finds meaningful test scenarios

| Step | Action | Expected Result | Validation Method |
|------|--------|----------------|-------------------|
| 1 | Monitor agent activity panel | Discovery Agent status updates | Watch for status changes |
| 2 | Wait for Discovery completion | Agent shows "completed" status | Visual verification |
| 3 | Check backend logs | Discovery activities logged | `grep -i "discovery" platform_logs` |
| 4 | Verify scenario count | 7-8 scenarios discovered | Check activity messages |
| 5 | Validate scenario quality | Scenarios relate to e-commerce features | Review scenario names |

**Pass Criteria**: Discovery Agent completes and finds 7-8 relevant e-commerce scenarios

---

### TC005: Test Generation Agent Validation
**Objective**: Verify Test Generation Agent creates meaningful test cases

| Step | Action | Expected Result | Validation Method |
|------|--------|----------------|-------------------|
| 1 | Monitor Test Generation Agent | Agent status updates to "running" | Visual verification |
| 2 | Wait for generation completion | Agent shows "completed" status | Visual verification |
| 3 | Check backend logs | Generation activities logged | `grep -i "generation" platform_logs` |
| 4 | Verify test case count | 7-8 test cases generated | Check activity messages |
| 5 | Validate test case structure | Test cases have names, descriptions, steps | Review logged data |

**Pass Criteria**: Test Generation Agent completes and creates 7-8 structured test cases

---

### TC006: Code Generation Agent Validation
**Objective**: Verify Code Generation Agent creates actual Playwright test files

| Step | Action | Expected Result | Validation Method |
|------|--------|----------------|-------------------|
| 1 | Monitor Code Generation Agent | Agent status updates to "running" | Visual verification |
| 2 | Wait for code generation completion | Agent shows "completed" status | Visual verification |
| 3 | Check file system for generated files | Test files created in customer directory | `find /opt/test-automation-platform/data -name "test_*.py"` |
| 4 | Verify file count | 7-8 test files + conftest.py | Count files in directory |
| 5 | Check file content quality | Files contain Playwright imports and test functions | `grep -l "from playwright" /path/to/files/*.py` |
| 6 | Verify file structure | Proper Python syntax and test structure | `python3 -m py_compile test_file.py` |

**Pass Criteria**: 7-8 valid Playwright test files generated with proper syntax

---

### TC007: Validation Agent Verification
**Objective**: Verify Validation Agent performs quality checks

| Step | Action | Expected Result | Validation Method |
|------|--------|----------------|-------------------|
| 1 | Monitor Validation Agent | Agent status updates to "running" | Visual verification |
| 2 | Wait for validation completion | Agent shows "completed" status | Visual verification |
| 3 | Check validation activities | Validation steps logged | Check backend logs |
| 4 | Verify test suite status | Test suite marked as "completed" | Check database or UI |
| 5 | Confirm final status | All agents show "completed" | Visual verification |

**Pass Criteria**: Validation Agent completes and test suite is marked as completed

---

### TC008: Database Storage Verification
**Objective**: Verify hybrid architecture stores metadata correctly

| Step | Action | Expected Result | Validation Method |
|------|--------|----------------|-------------------|
| 1 | Check test_cases table | Test case records exist | `sudo -u postgres psql -d test_automation_platform -c "SELECT COUNT(*) FROM test_cases WHERE created_at > NOW() - INTERVAL '1 hour';"` |
| 2 | Verify file paths stored | test_file_path column populated | `sudo -u postgres psql -d test_automation_platform -c "SELECT name, test_file_path FROM test_cases WHERE test_file_path IS NOT NULL LIMIT 5;"` |
| 3 | Check metadata completeness | All required fields populated | Verify generation_model, file_size_bytes, etc. |
| 4 | Validate customer isolation | Records associated with correct customer | Check customer_id field |
| 5 | Verify test suite association | Test cases linked to test suite | Check test_suite_id field |

**Pass Criteria**: Test case metadata stored correctly with file paths and complete information

---

### TC009: File Execution Validation
**Objective**: Verify generated test files are executable

| Step | Action | Expected Result | Validation Method |
|------|--------|----------------|-------------------|
| 1 | Navigate to test directory | Directory contains test files | `cd /opt/test-automation-platform/data/customers/.../tests/` |
| 2 | Install test dependencies | pytest and playwright available | `pip3 list \| grep -E "(pytest\|playwright)"` |
| 3 | Run syntax check | Files have valid Python syntax | `python3 -m py_compile test_*.py` |
| 4 | Execute one test file | Test runs (may fail but executes) | `python3 -m pytest test_checkout_process.py -v --tb=short` |
| 5 | Check test structure | Test function exists and runs | Verify pytest recognizes test |
| 6 | Verify Playwright integration | Playwright imports and Page parameter work | Check for browser automation |

**Pass Criteria**: Test files are syntactically correct and executable with pytest

---

### TC010: End-to-End Workflow Validation
**Objective**: Verify complete user workflow from start to finish

| Step | Action | Expected Result | Validation Method |
|------|--------|----------------|-------------------|
| 1 | Complete full workflow | All previous test cases pass | Run TC001-TC009 in sequence |
| 2 | Verify file-database consistency | File paths in DB match actual files | Cross-reference database and filesystem |
| 3 | Check agent completion times | All agents complete within reasonable time | Monitor timestamps |
| 4 | Validate user experience | UI remains responsive throughout | No errors or timeouts |
| 5 | Confirm hybrid architecture | Both files AND database populated | Verify both storage layers |

**Pass Criteria**: Complete workflow executes successfully with hybrid storage working

---

## 📊 Test Execution Tracking

### Test Results Template
```
Test Case: TC00X
Date: YYYY-MM-DD
Time: HH:MM
Tester: [Name]
Environment: [Local/Staging/Production]

Results:
- Step 1: [PASS/FAIL] - [Notes]
- Step 2: [PASS/FAIL] - [Notes]
- Step 3: [PASS/FAIL] - [Notes]
...

Overall Result: [PASS/FAIL]
Issues Found: [List any issues]
Screenshots: [Attach if applicable]
Logs: [Reference log files]
```

### Key Metrics to Track
1. **Agent Performance**
   - Discovery scenarios found: ___/8
   - Test cases generated: ___/8
   - Files created: ___/8
   - Validation completion: [Y/N]

2. **File Quality**
   - Syntactically correct: ___/8
   - Executable with pytest: ___/8
   - Contains Playwright code: ___/8
   - Has test functions: ___/8

3. **Database Storage**
   - Test cases in database: ___
   - File paths stored: ___/8
   - Metadata complete: [Y/N]
   - Customer isolation: [Y/N]

4. **Performance**
   - Platform startup time: ___ seconds
   - Total workflow time: ___ minutes
   - Agent processing time: ___ minutes
   - File generation time: ___ seconds

---

## 🚨 Known Issues & Workarounds

### Issue 1: Database Connection
**Problem**: RLS policy may prevent test case insertion  
**Workaround**: Verify app_user has app_read_write role  
**Command**: `sudo -u postgres psql -d test_automation_platform -c "GRANT app_read_write TO app_user;"`

### Issue 2: Template Test Logic
**Problem**: Generated tests contain TODO comments and may fail  
**Expected**: This is normal - tests should execute but may fail on assertions  
**Validation**: Focus on syntax correctness and execution, not test results

### Issue 3: File Permissions
**Problem**: Generated files may have incorrect permissions  
**Workaround**: Check file ownership and permissions  
**Command**: `ls -la /opt/test-automation-platform/data/customers/*/test_suites/*/tests/`

---

## 📈 Success Metrics

### Minimum Viable Success
- ✅ Platform starts and UI accessible
- ✅ Test creation workflow completes
- ✅ At least 5 test files generated
- ✅ Files are syntactically correct
- ✅ Basic database storage working

### Full Success
- ✅ All 4 agents complete successfully
- ✅ 7-8 high-quality test files generated
- ✅ Complete database metadata storage
- ✅ Files executable with pytest
- ✅ Hybrid architecture fully functional

### Excellence
- ✅ All tests pass within 5 minutes
- ✅ Generated code quality score > 80%
- ✅ Zero syntax errors
- ✅ Complete audit trail in database
- ✅ Ready for production deployment

---

## 🔄 Test Execution Schedule

### Phase 1: Infrastructure (30 minutes)
- TC001: Platform Startup
- TC002: User Authentication
- Environment validation

### Phase 2: Core Workflow (45 minutes)
- TC003: Test Creation Initiation
- TC004-TC007: Agent Validation (all 4 agents)
- Real-time monitoring

### Phase 3: Validation (30 minutes)
- TC008: Database Storage Verification
- TC009: File Execution Validation
- TC010: End-to-End Workflow

### Phase 4: Documentation (15 minutes)
- Results compilation
- Issue documentation
- Recommendations

**Total Estimated Time: 2 hours**

---

## 📝 Test Report Template

```markdown
# Test Execution Report
**Date**: [Date]
**Tester**: [Name]
**Environment**: [Environment]
**Platform Version**: [Version]

## Executive Summary
[Overall results and key findings]

## Test Results Summary
| Test Case | Status | Duration | Issues |
|-----------|--------|----------|--------|
| TC001 | PASS/FAIL | XX min | [Issues] |
| TC002 | PASS/FAIL | XX min | [Issues] |
| ... | ... | ... | ... |

## Key Metrics
- Files Generated: X/8
- Database Records: X
- Execution Success Rate: X%
- Total Test Time: X minutes

## Issues Found
1. [Issue description]
2. [Issue description]

## Recommendations
1. [Recommendation]
2. [Recommendation]

## Conclusion
[Final assessment and next steps]
```

This comprehensive test plan provides exact steps, validation methods, and success criteria for thoroughly testing the hybrid architecture and agent functionality.
