#!/bin/bash

# Retail AI Advisor - Project Setup Script
# This script initializes the entire project including frontend and backend

set -e  # Exit on any error

echo "🚀 Starting Retail AI Advisor Setup..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] && [ ! -d "frontend" ] && [ ! -d "backend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Checking system requirements..."

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js version 18+ is required. Current version: $(node --version)"
    exit 1
fi

print_success "Node.js $(node --version) found"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
print_success "Python $(python3 --version) found"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm and try again."
    exit 1
fi

print_success "npm $(npm --version) found"

# Check pip
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    print_error "pip is not installed. Please install pip and try again."
    exit 1
fi

print_success "pip found"

echo ""
print_status "Setting up Frontend (Next.js)..."
echo "=================================="

# Navigate to frontend directory
cd frontend

# Install frontend dependencies
print_status "Installing frontend dependencies..."
if npm install; then
    print_success "Frontend dependencies installed successfully"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    print_status "Creating frontend environment file..."
    cat > .env.local << EOF
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Retail AI Advisor
NEXT_PUBLIC_APP_VERSION=1.0.0
EOF
    print_success "Frontend .env.local created"
else
    print_warning "Frontend .env.local already exists"
fi

# Go back to root
cd ..

echo ""
print_status "Setting up Backend (FastAPI)..."
echo "================================="

# Navigate to backend directory
cd backend

# Install Python dependencies
print_status "Installing Python dependencies..."
if python3 -m pip install -r requirements-minimal.txt; then
    print_success "Core Python dependencies installed"
else
    print_error "Failed to install Python dependencies"
    exit 1
fi

# Install additional required packages
print_status "Installing additional required packages..."
python3 -m pip install databases==0.9.0 email-validator

# Create .env if it doesn't exist (copy from .env.example)
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_status "Creating backend environment file from example..."
        cp .env.example .env
        print_success "Backend .env created from .env.example"
    else
        print_status "Creating backend environment file..."
        cat > .env << EOF
# Environment Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database Configuration (using SQLite for testing)
DATABASE_URL=sqlite:///./test.db
SUPABASE_URL=https://xiessgdymqqyqmbbzxca.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpZXNzZ2R5bXFxeXFtYmJ6eGNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg2ODMyMTcsImV4cCI6MjA2NDI1OTIxN30.yyYP7TnZdkBOF_zMD5IYiBc0JmCB4YERhT59PDraa6g
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpZXNzZ2R5bXFxeXFtYmJ6eGNhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODY4MzIxNywiZXhwIjoyMDY0MjU5MjE3fQ.teMNmkkDi2CB_qHUoVYYuX2yMTErWLYSGzXv5q9TjUk

# Security
SECRET_KEY=test-super-secret-key-for-development-only
JWT_SECRET_KEY=test-jwt-secret-key-for-development
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Redis Configuration (optional for testing)
REDIS_URL=redis://localhost:6379/0

# External API Keys (mock for testing)
SHOPIFY_CLIENT_ID=test-shopify-client-id
SHOPIFY_CLIENT_SECRET=test-shopify-client-secret
ZENROWS_API_KEY=test-zenrows-api-key
APIDECK_API_KEY=test-apideck-api-key
AZURE_OPENAI_API_KEY=test-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://test-openai.openai.azure.com/
ELEVENLABS_API_KEY=test-elevenlabs-key
VEED_API_KEY=test-veed-api-key
EOF
        print_success "Backend .env created"
    fi
else
    print_warning "Backend .env already exists"
fi

# Go back to root
cd ..

echo ""
print_status "Creating startup scripts..."
echo "============================"

# Create start script for development
cat > start-dev.sh << 'EOF'
#!/bin/bash

# Development startup script for Retail AI Advisor

echo "🚀 Starting Retail AI Advisor in Development Mode..."

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Frontend stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting backend server..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Services started successfully!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for background processes
wait
EOF

chmod +x start-dev.sh

# Create production build script
cat > build.sh << 'EOF'
#!/bin/bash

# Production build script for Retail AI Advisor

echo "🏗️  Building Retail AI Advisor for Production..."

# Build frontend
echo "Building frontend..."
cd frontend
npm run build
if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful"
else
    echo "❌ Frontend build failed"
    exit 1
fi
cd ..

# Prepare backend
echo "Preparing backend..."
cd backend
# Create production requirements if needed
if [ ! -f "requirements-prod.txt" ]; then
    cp requirements-minimal.txt requirements-prod.txt
    echo "databases==0.9.0" >> requirements-prod.txt
    echo "email-validator" >> requirements-prod.txt
fi
cd ..

echo "✅ Build completed successfully!"
echo "📦 Frontend build: ./frontend/.next"
echo "🐍 Backend ready: ./backend"
EOF

chmod +x build.sh

# Create health check script
cat > health-check.sh << 'EOF'
#!/bin/bash

# Health check script for Retail AI Advisor

echo "🔍 Checking Retail AI Advisor Health..."

# Check backend
echo "Checking backend (http://localhost:8000/health)..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
    BACKEND_STATUS=$(curl -s http://localhost:8000/health | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "unknown")
    echo "   Status: $BACKEND_STATUS"
else
    echo "❌ Backend is not responding"
fi

# Check frontend
echo "Checking frontend (http://localhost:3000)..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "Health check completed."
EOF

chmod +x health-check.sh

print_success "Startup scripts created:"
print_success "  - start-dev.sh: Start both frontend and backend in development mode"
print_success "  - build.sh: Build for production"
print_success "  - health-check.sh: Check if services are running"

echo ""
print_status "Final setup steps..."
echo "===================="

# Create a simple README for quick start
cat > QUICK_START.md << 'EOF'
# Quick Start Guide

## Prerequisites
- Node.js 18+
- Python 3.11+
- npm
- pip

## Setup (First Time)
```bash
chmod +x setup.sh
./setup.sh
```

## Development
```bash
# Start both frontend and backend
./start-dev.sh

# Or start individually:
# Backend only
cd backend && python3 main.py

# Frontend only (in another terminal)
cd frontend && npm run dev
```

## URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Health Check
```bash
./health-check.sh
```

## Production Build
```bash
./build.sh
```

## Troubleshooting
- Make sure ports 3000 and 8000 are available
- Check that all dependencies are installed
- Verify Python and Node.js versions meet requirements
EOF

print_success "QUICK_START.md created"

echo ""
echo "🎉 Setup Complete!"
echo "=================="
print_success "Retail AI Advisor has been set up successfully!"
echo ""
echo "📋 Next Steps:"
echo "   1. Run './start-dev.sh' to start both frontend and backend"
echo "   2. Open http://localhost:3000 in your browser"
echo "   3. Check API docs at http://localhost:8000/docs"
echo ""
echo "📚 Additional Commands:"
echo "   - ./health-check.sh - Check if services are running"
echo "   - ./build.sh - Build for production"
echo "   - See QUICK_START.md for more details"
echo ""
print_warning "Note: This setup uses simplified authentication for demo purposes."
print_warning "For production, configure proper authentication and external services."