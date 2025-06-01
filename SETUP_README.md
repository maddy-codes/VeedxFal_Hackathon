# Retail AI Advisor - Setup Guide

This guide provides multiple ways to set up and run the Retail AI Advisor application.

## Prerequisites

- **Node.js 18+** (for frontend)
- **Python 3.11+** (for backend)
- **npm** (comes with Node.js)
- **pip** (comes with Python)

## Quick Setup Options

### Option 1: Simple Setup (Recommended)
```bash
chmod +x setup-simple.sh
./setup-simple.sh
```

This script:
- Installs dependencies one by one with better error handling
- Creates necessary environment files
- Provides simple start/stop scripts
- More resilient to dependency conflicts

### Option 2: Full Setup
```bash
chmod +x setup.sh
./setup.sh
```

This script:
- Comprehensive system checks
- Installs all dependencies at once
- Creates multiple utility scripts
- More features but may encounter dependency issues

## Starting the Application

### After Simple Setup:
```bash
./start.sh
```

### After Full Setup:
```bash
./start-dev.sh
```

### Manual Startup:
```bash
# Terminal 1 - Backend
cd backend
python3 main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Application URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

## Stopping the Application

### After Simple Setup:
```bash
./stop.sh
```

### Manual Stop:
```bash
# Kill processes
pkill -f "python3 main.py"
pkill -f "npm run dev"
```

## Project Structure

```
├── frontend/           # Next.js React application
├── backend/           # FastAPI Python application
├── docs/             # Documentation
├── setup.sh          # Full setup script
├── setup-simple.sh   # Simple setup script
├── start.sh          # Simple start script (created by setup-simple.sh)
├── stop.sh           # Simple stop script (created by setup-simple.sh)
├── start-dev.sh      # Development start script (created by setup.sh)
├── build.sh          # Production build script (created by setup.sh)
└── health-check.sh   # Health check script (created by setup.sh)
```

## Environment Files

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Retail AI Advisor
NEXT_PUBLIC_APP_VERSION=1.0.0

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### Backend (.env)
```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=test-super-secret-key-for-development-only
JWT_SECRET_KEY=test-jwt-secret-key-for-development
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Shopify Integration (Optional - for Shopify features)
SHOPIFY_CLIENT_ID=your_shopify_client_id
SHOPIFY_CLIENT_SECRET=your_shopify_client_secret
SHOPIFY_API_VERSION=2024-07
SHOPIFY_SCOPES=read_products,read_inventory,read_orders,read_price_rules
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the ports
   lsof -i :3000  # Frontend
   lsof -i :8000  # Backend
   
   # Kill processes if needed
   ./stop.sh
   ```

2. **Python Dependencies Issues**
   ```bash
   # Try installing dependencies manually
   cd backend
   pip3 install fastapi uvicorn sqlalchemy databases
   ```

3. **Node.js Dependencies Issues**
   ```bash
   # Clear npm cache and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Permission Issues**
   ```bash
   # Make scripts executable
   chmod +x *.sh
   ```

### Dependency Conflicts

If you encounter dependency conflicts:

1. **Use Simple Setup**: The `setup-simple.sh` script is more resilient
2. **Virtual Environment**: Consider using Python virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements-minimal.txt
   ```

3. **Node Version**: Ensure you're using Node.js 18+
   ```bash
   node --version
   npm --version
   ```

## Development Notes

- The application uses **SQLite** for development (no external database required)
- **Authentication** is simplified for demo purposes
- **CORS** is configured to allow frontend-backend communication
- **Hot reload** is enabled for both frontend and backend in development mode

## Shopify Integration Setup

To enable Shopify integration features:

### 1. Database Migration

Run the Shopify migration to create required tables:

```bash
cd backend
python run_shopify_migration.py
```

### 2. Shopify App Configuration

1. Create a Shopify Partner account at [partners.shopify.com](https://partners.shopify.com)
2. Create a new app in your Partner Dashboard
3. Configure OAuth redirect URLs:
   - Development: `http://localhost:3000/dashboard/shopify/callback`
   - Production: `https://your-domain.com/dashboard/shopify/callback`
4. Set required scopes: `read_products,read_inventory,read_orders,read_price_rules`
5. Note your Client ID and Client Secret

### 3. Environment Configuration

Add Shopify credentials to your `.env` files:

**Backend (.env)**:
```bash
SHOPIFY_CLIENT_ID=your_shopify_client_id
SHOPIFY_CLIENT_SECRET=your_shopify_client_secret
SHOPIFY_API_VERSION=2024-07
SHOPIFY_SCOPES=read_products,read_inventory,read_orders,read_price_rules
```

### 4. Test Shopify Integration

1. Start the application
2. Navigate to `/dashboard/shopify`
3. Connect a development store
4. Test product synchronization

For detailed Shopify setup instructions, see [docs/SHOPIFY_SETUP.md](./docs/SHOPIFY_SETUP.md).

## Production Deployment

For production deployment:

1. Run the build script (if using full setup):
   ```bash
   ./build.sh
   ```

2. Set production environment variables
3. Use a production database (PostgreSQL recommended)
4. Configure proper authentication and security settings
5. Set up reverse proxy (nginx recommended)
6. Configure Shopify webhooks for production URLs

## Getting Help

- Check the logs in the terminal where you started the services
- Visit http://localhost:8000/docs for API documentation
- Ensure all prerequisites are installed and up to date
- Try the simple setup if the full setup fails

## Features

- **Frontend**: Modern React/Next.js interface
- **Backend**: FastAPI with automatic API documentation
- **Database**: SQLite for development, PostgreSQL-ready for production
- **Authentication**: JWT-based authentication system
- **Real-time**: WebSocket support for real-time updates
- **API Documentation**: Automatic Swagger/OpenAPI documentation