# Database Setup and Migration Guide

## 📁 Database Files Overview

### **Core Schema Files:**
- `schema.sql` - Main PostgreSQL enterprise schema (21 tables)
- `missing_tables_postgres.sql` - Additional tables for test management
- `schema_fixed.sql` - Simplified schema without audit triggers

### **Migration Files:**
- `database_updates.sql` - **LATEST** - Schema updates for agent processing fixes

### **Legacy Files:**
- `sqlite_schema.sql` - Legacy SQLite schema (not used)
- `missing_tables.sql` - Old version (superseded)

## 🚀 **Setup Instructions**

### **For New Installation:**
```bash
# 1. Create database and user
sudo -u postgres psql -c "CREATE DATABASE test_automation_platform;"
sudo -u postgres psql -c "CREATE USER app_user WITH PASSWORD 'app_password';"

# 2. Apply main schema
sudo -u postgres psql -d test_automation_platform -f database/schema.sql

# 3. Apply additional tables
sudo -u postgres psql -d test_automation_platform -f database/missing_tables_postgres.sql

# 4. Apply latest updates
sudo -u postgres psql -d test_automation_platform -f database/database_updates.sql

# 5. Grant permissions
sudo -u postgres psql -d test_automation_platform -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;"
```

### **For Existing Installation (Migration):**
```bash
# Apply only the latest updates
sudo -u postgres psql -d test_automation_platform -f database/database_updates.sql
```

## 🔧 **What database_updates.sql Fixes:**

### **Schema Issues:**
- ✅ Adds missing `customer_id` column to `test_cases`
- ✅ Adds `test_steps` JSONB column for storing test steps
- ✅ Ensures `test_type` column exists (not `type`)
- ✅ Adds progress tracking columns to agent tables

### **Data Integrity:**
- ✅ Updates existing test cases with proper customer_id
- ✅ Cleans up orphaned agent activities
- ✅ Removes old pending jobs that cause conflicts

### **Permissions:**
- ✅ Grants proper access to app_user
- ✅ Ensures sequence permissions for auto-increment

## 🎯 **Verification Commands:**

```bash
# Check if updates applied correctly
sudo -u postgres psql -d test_automation_platform -c "
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('test_cases', 'agent_jobs', 'agent_job_activities')
ORDER BY table_name, column_name;"

# Count existing data
sudo -u postgres psql -d test_automation_platform -c "
SELECT 'customers' as table_name, COUNT(*) as count FROM customers
UNION ALL
SELECT 'test_cases', COUNT(*) FROM test_cases
UNION ALL  
SELECT 'agent_jobs', COUNT(*) FROM agent_jobs;"
```

## 🚨 **Troubleshooting:**

### **Permission Errors:**
```bash
sudo -u postgres psql -d test_automation_platform -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;"
```

### **Column Already Exists:**
The update script uses `IF NOT EXISTS` checks, so it's safe to run multiple times.

### **Foreign Key Violations:**
The script ensures customer_id references are properly set before creating constraints.
