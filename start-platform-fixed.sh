#!/bin/bash

echo "🚀 Starting AI Test Automation Platform (Fixed Version)..."

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

# Start backend server
echo "🔧 Starting backend server..."
cd ../api
python3 main_postgres.py &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Test backend health
echo "🔍 Testing backend health..."
if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend may still be starting..."
fi

# Start frontend server
echo "🎨 Starting frontend server..."
cd ../web-dashboard
npm run dev &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

echo ""
echo "🎉 AI Test Automation Platform is running!"
echo ""
echo "📱 Frontend: http://localhost:5173 (or next available port)"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🗄️  Database: PostgreSQL"
echo ""
echo "👤 Demo Login:"
echo "   Username: demo"
echo "   Password: demo123"
echo ""
echo "🔧 Troubleshooting:"
echo "   - If frontend shows SWR errors, run: cd web-dashboard && npm install swr axios"
echo "   - If backend shows database errors, check PostgreSQL connection"
echo "   - Check logs above for any specific error messages"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait for interrupt
wait
