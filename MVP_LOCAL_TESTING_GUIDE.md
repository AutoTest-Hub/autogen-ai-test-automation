# 🧪 MVP Hybrid Architecture - Local Testing Guide

## 📋 Prerequisites

### Required Software:
```bash
# PostgreSQL 14+
sudo apt update
sudo apt install postgresql postgresql-contrib

# Python 3.11+
python3 --version  # Should be 3.11+

# Node.js 18+
node --version     # Should be 18+
npm --version
```

### Required Python Packages:
```bash
pip3 install fastapi uvicorn psycopg2-binary python-multipart python-jose[cryptography] passlib[bcrypt] pytest playwright
playwright install
```

---

## 🚀 Step-by-Step Testing Instructions

### Step 1: Database Setup
```bash
# 1. Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 2. Create database and user
sudo -u postgres psql -c "CREATE DATABASE test_automation_platform;"
sudo -u postgres psql -c "CREATE USER app_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE test_automation_platform TO app_user;"

# 3. Apply database schema
cd /path/to/your/autogen-ai-test-automation
sudo -u postgres psql -d test_automation_platform -f database/schema.sql

# 4. Apply file storage migration
sudo -u postgres psql -d test_automation_platform -f database/mvp_file_storage_migration.sql
```

### Step 2: Environment Configuration
```bash
# 1. Set environment variables for local testing
export STORAGE_TYPE=local
export DATABASE_URL="postgresql://app_user:secure_password@localhost:5432/test_automation_platform"
export LOCAL_STORAGE_PATH="/opt/test-automation-platform/data"

# 2. Create local storage directory
sudo mkdir -p /opt/test-automation-platform/data
sudo chown -R $USER:$USER /opt/test-automation-platform/data
```

### Step 3: Start the Platform
```bash
# Option A: Use the provided startup script
chmod +x start-platform-enterprise.sh
STORAGE_TYPE=local ./start-platform-enterprise.sh

# Option B: Manual startup (for debugging)
# Terminal 1 - Backend API
cd api
python3 main_postgres_full.py

# Terminal 2 - Frontend (new terminal)
cd web-dashboard
npm install
npm run dev
```

### Step 4: Access and Test the Platform
```bash
# 1. Open browser and navigate to:
http://localhost:5173

# 2. Login with demo credentials:
Username: demo
Password: demo123
```

---

## 🧪 Test Cases to Execute

### Test Case 1: Authentication & Navigation
**Steps:**
1. Navigate to `http://localhost:5173`
2. Click "Admin Demo"
3. Enter credentials: `demo` / `demo123`
4. Click "Sign In"
5. Verify successful login and dashboard access

**Expected Result:** ✅ Successful login, dashboard displays

---

### Test Case 2: Test Creation (File Storage)
**Steps:**
1. Click "Create Tests" in sidebar
2. Click "E-commerce Demo" 
3. Scroll down and click "Create Tests"
4. Wait for "Test creation started successfully!" message
5. Monitor agent activity panel

**Expected Result:** 
- ✅ Success message appears
- ✅ Agent status updates show progress
- ✅ All 4 agents complete successfully

---

### Test Case 3: File Generation Verification
**Steps:**
```bash
# 1. Check if test files were created
find /opt/test-automation-platform/data -name "*.py" -type f

# 2. Verify file structure
ls -la /opt/test-automation-platform/data/customers/*/test_suites/*/tests/

# 3. Check file content
cat /opt/test-automation-platform/data/customers/*/test_suites/*/tests/test_*.py
```

**Expected Result:**
- ✅ 7+ Playwright test files created
- ✅ `conftest.py` configuration file exists
- ✅ Files contain valid Python/Playwright syntax

---

### Test Case 4: Database Storage Verification
**Steps:**
```bash
# 1. Check test suites in database
sudo -u postgres psql -d test_automation_platform -c "
SELECT COUNT(*) as total_suites, 
       COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_suites
FROM test_suites;"

# 2. Check test cases with file paths
sudo -u postgres psql -d test_automation_platform -c "
SELECT name, test_file_path, status 
FROM test_cases 
WHERE test_file_path IS NOT NULL 
LIMIT 5;"
```

**Expected Result:**
- ✅ Multiple test suites with 'completed' status
- ✅ Test cases with valid file paths
- ✅ File paths point to actual generated files

---

### Test Case 5: Test Execution
**Steps:**
```bash
# 1. Navigate to generated test directory
cd /opt/test-automation-platform/data/customers/*/test_suites/*/tests/

# 2. Install pytest if not already installed
pip3 install pytest playwright

# 3. Run a single test file
pytest test_checkout_process.py -v

# 4. Check test results
echo $?  # Should be 0 for success, non-zero for failure
```

**Expected Result:**
- ✅ Test executes without syntax errors
- ✅ Playwright launches successfully
- ⚠️ Test may fail on assertions (expected - template logic)

---

### Test Case 6: API Verification
**Steps:**
```bash
# 1. Test backend API directly
curl -s http://localhost:8000/health

# 2. Check test suites API (requires authentication)
# Note: This will return 401 without proper token, which is expected
curl -s http://localhost:8000/api/v1/tests

# 3. Check backend logs for successful data retrieval
tail -f api/logs/app.log | grep "Query returned"
```

**Expected Result:**
- ✅ Health endpoint returns success
- ✅ Backend logs show "Query returned 54 test suites" or similar
- ✅ API endpoints are responsive

---

## 🔍 Troubleshooting

### Issue: Database Connection Error
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep test_automation_platform

# Test connection
psql -h localhost -U app_user -d test_automation_platform -c "SELECT 1;"
```

### Issue: Permission Denied on Storage Directory
```bash
# Fix permissions
sudo chown -R $USER:$USER /opt/test-automation-platform/data
chmod -R 755 /opt/test-automation-platform/data
```

### Issue: Frontend Not Loading
```bash
# Check if Node.js dependencies are installed
cd web-dashboard
npm install

# Check if backend is running
curl http://localhost:8000/health
```

### Issue: No Test Files Generated
```bash
# Check backend logs
tail -f api/logs/app.log

# Check storage configuration
echo $STORAGE_TYPE
echo $LOCAL_STORAGE_PATH

# Verify agent processor is working
grep "Code Generation Agent" api/logs/app.log
```

### Issue: RLS Policy Errors
```bash
# Check if RLS policies are properly configured
sudo -u postgres psql -d test_automation_platform -c "
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'test_suites';"

# Temporarily disable RLS for testing (if needed)
sudo -u postgres psql -d test_automation_platform -c "
ALTER TABLE test_suites DISABLE ROW LEVEL SECURITY;"
```

---

## 📊 Success Criteria

### ✅ **Hybrid Architecture Working:**
- [ ] Database stores test suite metadata
- [ ] Files generated in local storage
- [ ] Test cases have file_path references
- [ ] All 4 agents complete successfully

### ✅ **File Storage Working:**
- [ ] Playwright test files created
- [ ] Files are syntactically correct
- [ ] Directory structure follows customer/suite pattern
- [ ] Files are executable with pytest

### ✅ **Database Integration Working:**
- [ ] Test suites appear in database
- [ ] Test cases linked to file paths
- [ ] Customer isolation maintained
- [ ] Audit logs created

### ✅ **Agent Processing Working:**
- [ ] Discovery Agent finds test scenarios
- [ ] Test Generation Agent creates test cases
- [ ] Code Generation Agent produces Playwright files
- [ ] Validation Agent completes quality checks

---

## 🚨 Known Issues

1. **UI Display Issue:** Backend returns data correctly (54 test suites), but frontend may not display them due to a rendering issue (API working, UI needs fix)

2. **Template Test Logic:** Generated tests use placeholder logic and will fail on actual execution (expected behavior for MVP)

3. **RLS Policy Warnings:** Some configuration parameter warnings in logs (non-blocking, doesn't affect functionality)

4. **Dashboard Stats:** May show errors due to configuration parameter issues (doesn't affect core functionality)

---

## 📈 Expected Performance

### **File Generation:**
- **Time**: 30-60 seconds for complete test suite
- **Output**: 7+ Playwright test files per suite
- **Size**: ~2-5KB per test file

### **Database Operations:**
- **Test Suite Creation**: < 1 second
- **Test Case Metadata**: < 500ms per case
- **File Path Tracking**: Immediate

### **Agent Processing:**
- **Discovery Agent**: 5-10 seconds
- **Test Generation**: 10-15 seconds  
- **Code Generation**: 15-20 seconds
- **Validation**: 5-10 seconds

---

## 📞 Support

If you encounter issues:

1. **Check logs:** `tail -f api/logs/app.log`
2. **Verify database:** Use the SQL queries provided above
3. **Check file permissions:** Ensure storage directory is writable
4. **Test API directly:** `curl http://localhost:8000/api/v1/tests`
5. **Monitor agent processing:** Look for agent completion messages in logs

## 🎯 Quick Validation Commands

```bash
# One-liner to check if everything is working
echo "=== PLATFORM STATUS ===" && \
curl -s http://localhost:8000/health && \
echo -e "\n=== FILE COUNT ===" && \
find /opt/test-automation-platform/data -name "*.py" | wc -l && \
echo "=== DATABASE COUNT ===" && \
sudo -u postgres psql -d test_automation_platform -c "SELECT COUNT(*) FROM test_suites;" -t
```

The MVP hybrid architecture should work end-to-end with these steps! 🚀
