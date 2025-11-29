# PostgreSQL Platform Troubleshooting Guide

## Issues Identified from Your Logs

### 1. PostgreSQL Audit Trigger Error ❌
**Error**: `record "new" has no field "customer_id"`

**Cause**: The audit trigger function tries to access `customer_id` field on tables that don't have it (like `subscription_plans`).

**Solution**: Use the fixed schema without problematic triggers.

### 2. Frontend SWR Dependency Missing ❌
**Error**: `Failed to resolve import "swr" from "src/hooks/useTests.js"`

**Cause**: The `swr` library wasn't installed in the frontend dependencies.

**Solution**: Install SWR and axios dependencies.

### 3. SystemD Commands Not Available ⚠️
**Error**: `systemctl: command not found`

**Cause**: Running on macOS which doesn't have systemctl.

**Solution**: Use platform-specific PostgreSQL management commands.

## Quick Fix Steps

### Step 1: Reset Database with Fixed Schema
```bash
cd /path/to/autogen-ai-test-automation
./reset-database.sh
```

### Step 2: Install Missing Frontend Dependencies
```bash
cd web-dashboard
npm install swr@2.2.4 axios@1.6.2
```

### Step 3: Start Platform with Fixed Script
```bash
./start-platform-fixed.sh
```

## Detailed Solutions

### PostgreSQL Setup Issues

#### Issue: Audit Trigger Errors
The original schema has audit triggers that assume all tables have a `customer_id` field, but some tables (like `subscription_plans`) don't.

**Fixed in**: `database/schema_fixed.sql`
- Removed problematic audit triggers
- Kept essential tables and security features
- Maintained data integrity without trigger conflicts

#### Issue: Row Level Security Blocking Inserts
RLS policies prevent initial data insertion during setup.

**Solution**: Temporarily disable RLS during setup:
```sql
ALTER TABLE customers DISABLE ROW LEVEL SECURITY;
ALTER TABLE customer_users DISABLE ROW LEVEL SECURITY;
-- ... other tables
```

### Frontend Dependency Issues

#### Issue: SWR Library Missing
The React hooks use SWR for data fetching but it's not installed.

**Solution**: Install SWR and axios:
```bash
npm install swr@2.2.4 axios@1.6.2
```

#### Issue: Port Conflicts
Vite tries multiple ports when 5173 is busy.

**Expected Behavior**: This is normal, Vite will find an available port.

### Platform-Specific Issues

#### macOS: No systemctl
**Error**: `systemctl: command not found`

**Solutions**:
- **Homebrew**: `brew services start postgresql`
- **Manual**: `pg_ctl -D /usr/local/var/postgres start`
- **Check Status**: `pg_isready`

#### Linux: PostgreSQL Not Running
**Solutions**:
- **SystemD**: `sudo systemctl start postgresql`
- **Service**: `sudo service postgresql start`
- **Manual**: `sudo -u postgres pg_ctl start -D /var/lib/postgresql/data`

#### Docker: PostgreSQL in Container
**Solution**:
```bash
docker run --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=test_automation_platform \
  -p 5432:5432 -d postgres:14
```

## Verification Steps

### 1. Check PostgreSQL Connection
```bash
pg_isready -h localhost -p 5432
```

### 2. Test Database Access
```bash
psql -h localhost -U app_user -d test_automation_platform -c "SELECT COUNT(*) FROM customers;"
```

### 3. Verify Backend API
```bash
curl http://localhost:8000/api/v1/health
```

### 4. Test Authentication
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

### 5. Check Frontend Access
Open: http://localhost:5173 (or the port shown in Vite output)

## Common Error Messages & Solutions

### Backend Errors

#### "psycopg2.OperationalError: could not connect to server"
**Cause**: PostgreSQL not running or wrong connection settings.
**Solution**: Start PostgreSQL and check connection parameters in `database_postgres.py`.

#### "relation does not exist"
**Cause**: Database schema not applied or tables missing.
**Solution**: Run `./reset-database.sh` to recreate schema.

#### "permission denied for table"
**Cause**: Database user lacks permissions.
**Solution**: Grant permissions with the reset script.

### Frontend Errors

#### "Failed to resolve import 'swr'"
**Cause**: SWR library not installed.
**Solution**: `npm install swr axios`

#### "Network Error" or "Failed to fetch"
**Cause**: Backend not running or CORS issues.
**Solution**: Ensure backend is running on port 8000.

#### "401 Unauthorized"
**Cause**: Authentication token expired or invalid.
**Solution**: Login again with demo credentials.

## Environment-Specific Setup

### Development Environment
```bash
# 1. Reset database
./reset-database.sh

# 2. Install dependencies
cd web-dashboard && npm install swr axios
cd ../api && pip install -r requirements.txt

# 3. Start platform
./start-platform-fixed.sh
```

### Production Environment
```bash
# 1. Use managed PostgreSQL service
# 2. Configure environment variables
# 3. Enable SSL and security features
# 4. Set up proper backup and monitoring
```

## Files Created to Fix Issues

1. **`database/schema_fixed.sql`** - PostgreSQL schema without problematic triggers
2. **`reset-database.sh`** - Complete database reset and setup script
3. **`start-platform-fixed.sh`** - Fixed startup script with proper error handling
4. **`TROUBLESHOOTING_GUIDE.md`** - This comprehensive guide

## Success Indicators

When everything is working correctly, you should see:

✅ **Backend**: 
- "🚀 API Server ready!" message
- Health endpoint returns `{"status":"healthy"}`
- Authentication works with demo credentials

✅ **Frontend**:
- Vite dev server starts without SWR errors
- Login page loads correctly
- Can authenticate and access dashboard

✅ **Database**:
- 16 tables created successfully
- Sample data inserted (demo customer, test suites)
- No RLS or trigger errors during operation

## Getting Help

If you continue to have issues:

1. **Check Logs**: Look for specific error messages in terminal output
2. **Verify Prerequisites**: Ensure PostgreSQL is running and accessible
3. **Test Components**: Test database, backend, and frontend separately
4. **Reset Everything**: Use `./reset-database.sh` for a clean start
5. **Check Ports**: Ensure ports 5173 and 8000 are available

## Contact Information

For additional support, check the project repository or create an issue with:
- Your operating system
- PostgreSQL version
- Complete error logs
- Steps you've already tried
