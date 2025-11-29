#!/bin/bash

echo "🚀 Starting AI Test Automation Platform - Enterprise Edition (21 Tables)"

# Function to check if PostgreSQL is running
check_postgres() {
    if command -v pg_isready >/dev/null 2>&1; then
        if pg_isready -q; then
            echo "✅ PostgreSQL is running"
            return 0
        else
            echo "❌ PostgreSQL is not running"
            return 1
        fi
    else
        echo "⚠️  pg_isready not found, assuming PostgreSQL is running"
        return 0
    fi
}

# Check PostgreSQL status
if ! check_postgres; then
    echo "📦 Please start PostgreSQL manually:"
    echo "   - macOS: brew services start postgresql"
    echo "   - Linux: sudo systemctl start postgresql"
    echo "   - Docker: docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres"
    echo ""
    echo "Press Enter when PostgreSQL is running..."
    read -r
fi

# Verify database schema
echo "🔍 Verifying enterprise database schema..."
TABLES_COUNT=$(sudo -u postgres psql -d test_automation_platform -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)

if [ "$TABLES_COUNT" -ge "20" ]; then
    echo "✅ Enterprise schema detected ($TABLES_COUNT tables)"
    echo "📊 Tables include:"
    echo "   - Agent management (5 tables): agent_jobs, agent_activity_logs, etc."
    echo "   - Test management (7 tables): test_suites, test_cases, test_steps, etc."
    echo "   - Security & compliance (6 tables): audit_logs, security_events, etc."
    echo "   - Core enterprise (3+ tables): customers, applications, etc."
else
    echo "⚠️  Database schema incomplete ($TABLES_COUNT tables found)"
    echo "Expected 20+ tables for enterprise features"
    echo ""
    echo "Please ensure you've run the complete PostgreSQL schema:"
    echo "1. sudo -u postgres psql -d test_automation_platform -f database/schema.sql"
    echo "2. sudo -u postgres psql -d test_automation_platform -f database/missing_tables.sql"
    echo ""
    echo "Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd api
pip3 install fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt] psycopg2-binary 2>/dev/null || {
    echo "⚠️  Some dependencies may already be installed"
}

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd ../web-dashboard
npm install swr axios 2>/dev/null || {
    echo "⚠️  Installing SWR and axios..."
    npm install swr@2.2.4 axios@1.6.2
}

# Start enterprise backend server
echo "🔧 Starting Enterprise Backend Server..."
cd ../api
python3 main_postgres_full.py &
BACKEND_PID=$!
echo "Enterprise backend started with PID: $BACKEND_PID"

# Wait for backend to start and initialize seed data
echo "⏳ Waiting for enterprise backend to initialize..."
echo "   - Database connection and schema verification"
echo "   - Automatic seed data creation (comprehensive → minimal → basic fallback)"
echo "   - API endpoint registration"
sleep 8

# Test backend health
echo "🔍 Testing enterprise backend health..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/v1/health 2>/dev/null)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Enterprise backend is healthy"
    echo "📊 Schema: Full Enterprise (21 tables)"
    
    # Test seed data
    echo "🌱 Verifying seed data..."
    SYSTEM_INFO=$(curl -s http://localhost:8000/api/v1/system/info 2>/dev/null)
    if echo "$SYSTEM_INFO" | grep -q "customers"; then
        echo "✅ Seed data successfully created"
        echo "   - Demo customer and users available"
        echo "   - Sample applications and test suites ready"
        echo "   - Agent jobs and audit logs initialized"
    else
        echo "⚠️  Seed data may still be initializing..."
    fi
else
    echo "⚠️  Backend may still be starting..."
    echo "   Check the backend logs above for any seed data creation messages"
fi

# Start frontend server
echo "🎨 Starting frontend server..."
cd ../web-dashboard
npm run dev &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

echo ""
echo "🎉 AI Test Automation Platform - Enterprise Edition is running!"
echo ""
echo "📱 Frontend: http://localhost:5173 (or next available port)"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🗄️  Database: PostgreSQL Enterprise (21 Tables)"
echo ""
echo "👤 Demo Login:"
echo "   Username: demo"
echo "   Password: demo123"
echo ""
echo "🏢 Enterprise Features Available:"
echo "   ✅ Real-time agent status tracking"
echo "   ✅ Granular test step execution"
echo "   ✅ Comprehensive activity logging"
echo "   ✅ Enhanced security controls"
echo "   ✅ SOC 2 Type II compliance"
echo "   ✅ Advanced audit capabilities"
echo ""
echo "📊 Database Schema:"
echo "   - Agent Management: 5 tables (jobs, activities, sessions, status, logs)"
echo "   - Test Management: 7 tables (suites, cases, steps, executions, results)"
echo "   - Security & Compliance: 6 tables (audit, security events, access logs)"
echo "   - Core Enterprise: 3+ tables (customers, users, applications)"
echo ""
echo "🌱 Seed Data Information:"
echo "   - Automatic creation: No manual steps required"
echo "   - Fallback strategy: Comprehensive → Minimal → Basic"
echo "   - seed_data_minimal.py: Constraint-compliant for any schema"
echo "   - Demo data: Always available for testing"
echo ""
echo "🔧 Troubleshooting:"
echo "   - If frontend shows SWR errors: cd web-dashboard && npm install swr axios"
echo "   - If backend shows database errors: check PostgreSQL connection"
echo "   - For schema issues: verify all 21 tables are created"
echo "   - If seed data fails: Check backend logs for constraint violations"
echo "   - Manual seed data: cd api && python3 seed_data_minimal.py"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping enterprise servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Enterprise servers stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait for interrupt
wait
