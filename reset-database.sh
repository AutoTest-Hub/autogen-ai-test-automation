#!/bin/bash

echo "🔄 Resetting PostgreSQL Database..."

# Drop and recreate database
echo "📦 Recreating database..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS test_automation_platform;" 2>/dev/null
sudo -u postgres psql -c "CREATE DATABASE test_automation_platform;"

# Create user if not exists
echo "👤 Setting up database user..."
sudo -u postgres psql -c "DROP USER IF EXISTS app_user;" 2>/dev/null
sudo -u postgres psql -c "CREATE USER app_user WITH PASSWORD 'app_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE test_automation_platform TO app_user;"

# Apply fixed schema (without problematic triggers)
echo "📋 Applying fixed schema..."
sudo -u postgres psql -d test_automation_platform -f database/schema_fixed.sql

# Apply additional tables
echo "📋 Adding test management tables..."
sudo -u postgres psql -d test_automation_platform -f database/missing_tables_postgres.sql

# Grant all permissions
echo "🔐 Setting up permissions..."
sudo -u postgres psql -d test_automation_platform -c "
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
"

# Disable RLS for initial setup (after all tables are created)
echo "🔓 Disabling Row Level Security for setup..."
sudo -u postgres psql -d test_automation_platform -c "
-- Disable RLS on tables from schema_fixed.sql
ALTER TABLE customers DISABLE ROW LEVEL SECURITY;
ALTER TABLE customer_users DISABLE ROW LEVEL SECURITY;
ALTER TABLE applications DISABLE ROW LEVEL SECURITY;
" 2>/dev/null

sudo -u postgres psql -d test_automation_platform -c "
-- Disable RLS on tables from missing_tables_postgres.sql
ALTER TABLE test_suites DISABLE ROW LEVEL SECURITY;
ALTER TABLE agent_jobs DISABLE ROW LEVEL SECURITY;
" 2>/dev/null

# Initialize sample data
echo "📊 Initializing sample data..."
cd api
python3 -c "
from database_postgres import initialize_database
try:
    initialize_database()
    print('✅ Sample data initialized successfully')
except Exception as e:
    print(f'⚠️  Sample data initialization: {e}')
"

echo ""
echo "✅ Database reset complete!"
echo ""
echo "📊 Database Status:"
sudo -u postgres psql -d test_automation_platform -c "
SELECT 
    schemaname,
    tablename,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = tablename) as columns
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
"

echo ""
echo "🎯 Next Steps:"
echo "1. Run: ./start-platform-fixed.sh"
echo "2. Open: http://localhost:8000/docs (API documentation)"
echo "3. Login with: username=demo, password=demo123"
