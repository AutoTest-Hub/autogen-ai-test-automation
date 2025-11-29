#!/bin/bash

echo "🚀 Starting AI Test Automation Platform..."

# Check if Python dependencies are installed
echo "📦 Installing Python dependencies..."
cd api
pip3 install fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt] 2>/dev/null

# Initialize database
echo "🗄️ Initializing database..."
if [ ! -f "test_automation.db" ]; then
    sqlite3 test_automation.db < ../database/sqlite_schema.sql
    echo "✅ Database initialized with sample data"
else
    echo "✅ Database already exists"
fi

# Start backend server
echo "🔧 Starting backend server..."
python3 main_fixed.py &
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
echo "🎉 Platform is starting up!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "👤 Demo Login:"
echo "   Username: demo"
echo "   Password: demo123"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for interrupt
trap "echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
