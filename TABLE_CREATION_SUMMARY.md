# PostgreSQL Table Creation Summary

## Table Distribution Across SQL Files

### Tables in `database/schema_fixed.sql` (11 tables):
1. `subscription_plans` - Subscription and pricing management
2. `customers` - Customer organizations with security metadata  
3. `customer_users` - User accounts with enhanced authentication
4. `applications` - Application management with security controls
5. `application_credentials` - Encrypted credential storage
6. `encryption_keys` - Encryption key management
7. `audit_logs` - Comprehensive audit trails
8. `security_events` - Security monitoring and alerting
9. `data_access_logs` - Data access tracking for compliance
10. `test_creation_requests` - Test creation workflow tracking
11. `test_executions` - Test execution results and metrics

### Tables in `database/missing_tables_postgres.sql` (5 tables):
1. `test_suites` - Test suite organization and management
2. `test_cases` - Individual test cases within suites  
3. `test_executions` - **DUPLICATE** (also in schema_fixed.sql)
4. `agent_jobs` - AI agent job processing
5. `agent_job_activities` - Detailed agent activity tracking

## Issue Identified

### Duplicate Table: `test_executions`
The `test_executions` table is defined in **both** SQL files:
- `database/schema_fixed.sql` (line ~393)
- `database/missing_tables_postgres.sql` (line ~87)

This could cause conflicts when applying both schemas.

### RLS Timing Issue
The reset script was trying to disable RLS on `agent_jobs` before it was created, causing the error:
```
ALTER TABLE agent_jobs DISABLE ROW LEVEL SECURITY;
ERROR: relation "agent_jobs" does not exist
```

## Corrected Application Sequence

### Step 1: Apply Main Schema
```bash
sudo -u postgres psql -d test_automation_platform -f database/schema_fixed.sql
```
**Creates**: 11 core tables including `test_executions`

### Step 2: Apply Additional Tables  
```bash
sudo -u postgres psql -d test_automation_platform -f database/missing_tables_postgres.sql
```
**Creates**: 4 new tables (`test_suites`, `test_cases`, `agent_jobs`, `agent_job_activities`)
**Skips**: `test_executions` (already exists, uses IF NOT EXISTS)

### Step 3: Disable RLS (Fixed Order)
```bash
# First disable RLS on tables from schema_fixed.sql
ALTER TABLE customers DISABLE ROW LEVEL SECURITY;
ALTER TABLE customer_users DISABLE ROW LEVEL SECURITY;
ALTER TABLE applications DISABLE ROW LEVEL SECURITY;

# Then disable RLS on tables from missing_tables_postgres.sql
ALTER TABLE test_suites DISABLE ROW LEVEL SECURITY;
ALTER TABLE agent_jobs DISABLE ROW LEVEL SECURITY;
```

## Final Database Schema (15 unique tables)

After applying both files correctly, you'll have:

### Core Enterprise Tables (11):
- subscription_plans
- customers  
- customer_users
- applications
- application_credentials
- encryption_keys
- audit_logs
- security_events
- data_access_logs
- test_creation_requests
- test_executions

### Test Management Tables (4):
- test_suites
- test_cases  
- agent_jobs
- agent_job_activities

**Total: 15 tables** (not 16 as previously stated due to the duplicate)

## Verification Commands

### Check All Tables Created:
```bash
sudo -u postgres psql -d test_automation_platform -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
"
```

### Expected Output:
```
agent_job_activities
agent_jobs
applications
application_credentials
audit_logs
customers
customer_users
data_access_logs
encryption_keys
security_events
subscription_plans
test_cases
test_creation_requests
test_executions
test_suites
```

## Fixed Files

The `reset-database.sh` script has been updated to:
1. Apply schemas in correct order
2. Disable RLS only after tables exist
3. Handle the duplicate `test_executions` table gracefully
4. Provide better error handling and verification
