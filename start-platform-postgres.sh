#!/bin/bash

echo "🚀 Starting AI Test Automation Platform with PostgreSQL..."

# Check if PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo "📦 Starting PostgreSQL service..."
    sudo systemctl start postgresql
fi

# Check if Python dependencies are installed
echo "📦 Installing Python dependencies..."
cd api
sudo pip3 install fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt] psycopg2-binary 2>/dev/null

# Start backend server with PostgreSQL
echo "🔧 Starting PostgreSQL backend server..."
python3 main_postgres.py &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend server
echo "🎨 Starting frontend server..."
cd ../web-dashboard
npm install 2>/dev/null
npm run dev &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

echo ""
echo "🎉 AI Test Automation Platform is running!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🗄️  Database: PostgreSQL (Enterprise)"
echo ""
echo "👤 Demo Login:"
echo "   Username: demo"
echo "   Password: demo123"
echo ""
echo "🏢 Enterprise Features:"
echo "   ✅ SOC 2 Type II Compliance"
echo "   ✅ Advanced Security Controls"
echo "   ✅ Comprehensive Audit Logging"
echo "   ✅ Row-Level Security Policies"
echo "   ✅ Encryption Key Management"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for interrupt
trap "echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
