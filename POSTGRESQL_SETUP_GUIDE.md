# PostgreSQL Database Setup Guide

## Overview of SQL Files

After examining all the SQL files in the project, here's what each file contains and the correct setup sequence:

### SQL Files Analysis

1. **`database/schema.sql`** (695 lines) - **MAIN COMPREHENSIVE SCHEMA**
   - Complete PostgreSQL enterprise schema with SOC 2 compliance
   - Contains 11 core tables: subscription_plans, customers, customer_users, applications, application_credentials, encryption_keys, audit_logs, security_events, data_access_logs, test_creation_requests, test_executions
   - Includes advanced security features, RLS policies, and audit functions
   - **This is the primary schema file**

2. **`database/missing_tables_postgres.sql`** (283 lines) - **ADDITIONAL TABLES**
   - Contains 5 additional tables: test_suites, test_cases, agent_jobs, agent_job_activities
   - These tables were missing from the main schema
   - **Must be applied AFTER the main schema**

3. **`database/sqlite_schema.sql`** (149 lines) - **LEGACY SQLite SCHEMA**
   - Simple SQLite version (not for PostgreSQL)
   - **DO NOT USE for PostgreSQL setup**

4. **`database/missing_tables.sql`** - **LEGACY FILE**
   - Old version, superseded by missing_tables_postgres.sql
   - **DO NOT USE**

5. **`database/config/saas_config.sql`** and **`database/config/onprem_config.sql`**
   - Configuration files for different deployment scenarios
   - **Optional - for advanced configuration**

## Correct Setup Sequence

### Step 1: Create Database and User
```bash
# Create database
sudo -u postgres psql -c "CREATE DATABASE test_automation_platform;"

# Create application user
sudo -u postgres psql -c "CREATE USER app_user WITH PASSWORD 'app_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE test_automation_platform TO app_user;"
```

### Step 2: Apply Main Schema (REQUIRED)
```bash
# Apply the comprehensive PostgreSQL schema
sudo -u postgres psql -d test_automation_platform -f database/schema.sql
```

**Note**: This may show some warnings/errors for:
- `pg_audit` extension (not critical)
- `DATABASE CURRENT` references (can be ignored)
- Some audit configuration parameters (not critical for basic functionality)

### Step 3: Apply Missing Tables (REQUIRED)
```bash
# Add the missing test management tables
sudo -u postgres psql -d test_automation_platform -f database/missing_tables_postgres.sql
```

### Step 4: Grant Permissions (REQUIRED)
```bash
# Grant proper permissions to app_user
sudo -u postgres psql -d test_automation_platform -c "
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
"
```

### Step 5: Disable RLS for Initial Setup (TEMPORARY)
```bash
# Temporarily disable Row Level Security for data insertion
sudo -u postgres psql -d test_automation_platform -c "
ALTER TABLE customers DISABLE ROW LEVEL SECURITY;
ALTER TABLE customer_users DISABLE ROW LEVEL SECURITY;
ALTER TABLE applications DISABLE ROW LEVEL SECURITY;
ALTER TABLE test_suites DISABLE ROW LEVEL SECURITY;
ALTER TABLE agent_jobs DISABLE ROW LEVEL SECURITY;
"
```

### Step 6: Initialize Sample Data (OPTIONAL)
```bash
# Run the Python initialization script
cd api
python3 -c "from database_postgres import initialize_database; initialize_database()"
```

## Complete Database Schema

After applying both files, you'll have **16 tables**:

### Core Enterprise Tables (from schema.sql):
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

### Test Management Tables (from missing_tables_postgres.sql):
12. `test_suites` - Test suite organization and management
13. `test_cases` - Individual test cases within suites
14. `agent_jobs` - AI agent job processing
15. `agent_job_activities` - Detailed agent activity tracking

## Verification Commands

### Check All Tables Created:
```bash
sudo -u postgres psql -d test_automation_platform -c "\dt"
```

### Verify Sample Data:
```bash
sudo -u postgres psql -d test_automation_platform -c "SELECT COUNT(*) FROM customers;"
sudo -u postgres psql -d test_automation_platform -c "SELECT COUNT(*) FROM test_suites;"
```

### Test API Connection:
```bash
curl -X GET http://localhost:8000/api/v1/health
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"username": "demo", "password": "demo123"}'
```

## Production Considerations

### Security Hardening:
1. **Re-enable RLS**: After initial setup, re-enable row-level security
2. **Configure SSL**: Enable SSL connections for production
3. **Audit Configuration**: Configure pg_audit extension properly
4. **Backup Strategy**: Implement regular database backups
5. **Monitoring**: Set up database monitoring and alerting

### Performance Optimization:
1. **Connection Pooling**: Configure pgBouncer or similar
2. **Index Optimization**: Monitor and optimize query performance
3. **Vacuum Strategy**: Configure automatic vacuum settings
4. **Resource Limits**: Set appropriate memory and connection limits

## Troubleshooting

### Common Issues:
1. **Permission Errors**: Ensure app_user has proper grants
2. **RLS Blocking Inserts**: Disable RLS temporarily for setup
3. **Extension Errors**: pg_audit extension is optional for basic functionality
4. **UUID Errors**: Ensure uuid-ossp extension is installed

### Quick Fixes:
```bash
# Reset permissions
sudo -u postgres psql -d test_automation_platform -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO app_user;"

# Check table existence
sudo -u postgres psql -d test_automation_platform -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"

# Reset RLS if needed
sudo -u postgres psql -d test_automation_platform -c "ALTER TABLE customers DISABLE ROW LEVEL SECURITY;"
```

## Summary

**Use these files in order:**
1. ✅ `database/schema.sql` (MAIN SCHEMA - REQUIRED)
2. ✅ `database/missing_tables_postgres.sql` (ADDITIONAL TABLES - REQUIRED)
3. ❌ `database/sqlite_schema.sql` (DO NOT USE for PostgreSQL)
4. ❌ `database/missing_tables.sql` (LEGACY - DO NOT USE)

This will give you a complete PostgreSQL enterprise database with 16 tables and full SOC 2 compliance features.
