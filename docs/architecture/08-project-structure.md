# Project Structure & Organization

## Overview

The Retail AI Advisor follows a monorepo structure with clear separation between frontend, backend, and infrastructure components. This organization supports rapid development during the hackathon while maintaining scalability for future growth.

## Repository Structure

```
retail-ai-advisor/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── package.json                    # Root package.json for workspace management
├── 
├── frontend/                       # Next.js Frontend Application
│   ├── README.md
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── .env.local.example
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── logo.svg
│   │   └── images/
│   ├── src/
│   │   ├── app/                    # Next.js 14 App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── globals.css
│   │   │   ├── auth/
│   │   │   │   ├── login/
│   │   │   │   └── callback/
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── products/
│   │   │   │   ├── analytics/
│   │   │   │   └── settings/
│   │   │   └── api/                # API routes (if needed)
│   │   ├── components/             # Reusable UI Components
│   │   │   ├── ui/                 # Base UI components (shadcn/ui)
│   │   │   │   ├── button.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   └── index.ts
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Footer.tsx
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── AuthGuard.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── ProductTable.tsx
│   │   │   │   ├── AnalyticsCards.tsx
│   │   │   │   ├── VideoPlayer.tsx
│   │   │   │   └── SyncStatus.tsx
│   │   │   └── common/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       └── Modal.tsx
│   │   ├── hooks/                  # Custom React Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useProducts.ts
│   │   │   ├── useAnalytics.ts
│   │   │   └── useSupabase.ts
│   │   ├── lib/                    # Utility Libraries
│   │   │   ├── supabase.ts
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   ├── utils.ts
│   │   │   └── constants.ts
│   │   ├── store/                  # State Management (Zustand)
│   │   │   ├── authStore.ts
│   │   │   ├── productStore.ts
│   │   │   └── uiStore.ts
│   │   ├── types/                  # TypeScript Type Definitions
│   │   │   ├── auth.ts
│   │   │   ├── product.ts
│   │   │   ├── analytics.ts
│   │   │   └── api.ts
│   │   └── styles/                 # Global Styles
│   │       ├── globals.css
│   │       └── components.css
│   └── tests/                      # Frontend Tests
│       ├── __mocks__/
│       ├── components/
│       ├── hooks/
│       └── utils/
│
├── backend/                        # FastAPI Backend Application
│   ├── README.md
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── pyproject.toml
│   ├── main.py                     # FastAPI application entry point
│   ├── app/
│   │   ├── __init__.py
│   │   ├── core/                   # Core application configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   └── logging.py
│   │   ├── api/                    # API route definitions
│   │   │   ├── __init__.py
│   │   │   ├── deps.py             # Dependencies
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── products.py
│   │   │   │   ├── sync.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── video.py
│   │   │   │   └── upload.py
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── cors.py
│   │   │       └── rate_limit.py
│   │   ├── models/                 # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── product.py
│   │   │   ├── sync.py
│   │   │   ├── analytics.py
│   │   │   └── video.py
│   │   ├── services/               # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── product_service.py
│   │   │   ├── shopify_service.py
│   │   │   ├── competitor_service.py
│   │   │   ├── trends_service.py
│   │   │   ├── pricing_service.py
│   │   │   ├── video_service.py
│   │   │   └── cache_service.py
│   │   ├── integrations/           # External service integrations
│   │   │   ├── __init__.py
│   │   │   ├── shopify/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py
│   │   │   │   ├── oauth.py
│   │   │   │   └── sync.py
│   │   │   ├── zenrows/
│   │   │   │   ├── __init__.py
│   │   │   │   └── scraper.py
│   │   │   ├── google_trends/
│   │   │   │   ├── __init__.py
│   │   │   │   └── client.py
│   │   │   ├── apideck/
│   │   │   │   ├── __init__.py
│   │   │   │   └── client.py
│   │   │   ├── azure_openai/
│   │   │   │   ├── __init__.py
│   │   │   │   └── client.py
│   │   │   ├── elevenlabs/
│   │   │   │   ├── __init__.py
│   │   │   │   └── client.py
│   │   │   └── veed/
│   │   │       ├── __init__.py
│   │   │       └── client.py
│   │   ├── utils/                  # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── helpers.py
│   │   │   ├── validators.py
│   │   │   ├── formatters.py
│   │   │   └── exceptions.py
│   │   └── workers/                # Background job workers
│   │       ├── __init__.py
│   │       ├── sync_worker.py
│   │       ├── video_worker.py
│   │       └── pipeline_worker.py
│   └── tests/                      # Backend Tests
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_products.py
│       ├── test_sync.py
│       ├── test_integrations/
│       ├── test_services/
│       └── test_utils/
│
├── functions/                      # Azure Functions
│   ├── README.md
│   ├── requirements.txt
│   ├── function_app.py
│   ├── shared/                     # Shared code between functions
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── services.py
│   │   └── utils.py
│   ├── daily_pipeline/
│   │   ├── __init__.py
│   │   └── function.py
│   ├── video_generation/
│   │   ├── __init__.py
│   │   └── function.py
│   └── competitor_scraping/
│       ├── __init__.py
│       └── function.py
│
├── infrastructure/                 # Infrastructure as Code
│   ├── README.md
│   ├── main.bicep                  # Main Bicep template
│   ├── modules/                    # Bicep modules
│   │   ├── app-service.bicep
│   │   ├── static-web-app.bicep
│   │   ├── function-app.bicep
│   │   ├── storage.bicep
│   │   ├── key-vault.bicep
│   │   └── monitoring.bicep
│   ├── parameters/                 # Environment-specific parameters
│   │   ├── dev.json
│   │   ├── staging.json
│   │   └── prod.json
│   └── scripts/                    # Deployment scripts
│       ├── deploy.sh
│       └── setup-secrets.sh
│
├── docs/                          # Documentation
│   ├── README.md
│   ├── architecture/              # Architecture documentation
│   │   ├── README.md
│   │   ├── 01-system-architecture.md
│   │   ├── 02-database-schema.md
│   │   ├── 03-api-specifications.md
│   │   ├── 04-security-architecture.md
│   │   ├── 05-external-integrations.md
│   │   ├── 06-deployment-architecture.md
│   │   ├── 07-performance-optimization.md
│   │   ├── 08-project-structure.md
│   │   ├── 09-cicd-pipeline.md
│   │   └── 10-monitoring-error-handling.md
│   ├── api/                       # API documentation
│   │   ├── README.md
│   │   └── openapi.json
│   ├── deployment/                # Deployment guides
│   │   ├── README.md
│   │   ├── local-development.md
│   │   ├── azure-deployment.md
│   │   └── environment-setup.md
│   └── user-guides/               # User documentation
│       ├── README.md
│       ├── getting-started.md
│       └── troubleshooting.md
│
├── scripts/                       # Development and deployment scripts
│   ├── setup-dev.sh              # Local development setup
│   ├── build-docker.sh           # Docker build script
│   ├── run-tests.sh               # Test execution script
│   ├── deploy-staging.sh          # Staging deployment
│   └── deploy-prod.sh             # Production deployment
│
├── config/                        # Configuration files
│   ├── competitor_urls.json       # Competitor scraping configuration
│   ├── email_templates/           # Email templates
│   └── video_templates/           # Video generation templates
│
└── .github/                       # GitHub Actions workflows
    ├── workflows/
    │   ├── frontend.yml
    │   ├── backend.yml
    │   ├── functions.yml
    │   ├── infrastructure.yml
    │   └── tests.yml
    ├── ISSUE_TEMPLATE/
    └── PULL_REQUEST_TEMPLATE.md
```

## Frontend Architecture (Next.js 14)

### App Router Structure
```typescript
// src/app/layout.tsx - Root layout
import { Inter } from 'next/font/google';
import { Providers } from '@/components/providers';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}

// src/app/dashboard/layout.tsx - Dashboard layout
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { AuthGuard } from '@/components/auth/AuthGuard';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto p-6">
            {children}
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
```

### Component Organization
```typescript
// src/components/ui/index.ts - UI component exports
export { Button } from './button';
export { Input } from './input';
export { Table } from './table';
export { Card } from './card';
export { Modal } from './modal';

// src/components/dashboard/ProductTable.tsx - Feature component
import { Table, Button } from '@/components/ui';
import { useProducts } from '@/hooks/useProducts';
import { Product } from '@/types/product';

interface ProductTableProps {
  shopId: number;
  filters?: ProductFilters;
}

export function ProductTable({ shopId, filters }: ProductTableProps) {
  const { products, isLoading, error } = useProducts({ shopId, filters });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <Table>
      {/* Table implementation */}
    </Table>
  );
}
```

### State Management Structure
```typescript
// src/store/authStore.ts - Zustand store
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      
      login: async (email: string, password: string) => {
        // Login implementation
      },
      
      logout: () => {
        set({ user: null, isAuthenticated: false });
      },
      
      refreshToken: async () => {
        // Token refresh implementation
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
```

## Backend Architecture (FastAPI)

### Application Structure
```python
# main.py - FastAPI application entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, products, sync, analytics, video
from app.core.logging import setup_logging

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Retail AI Advisor API",
    description="AI-powered retail analytics and pricing optimization",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(sync.router, prefix="/api/v1/sync", tags=["sync"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(video.router, prefix="/api/v1/video", tags=["video"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

### Service Layer Structure
```python
# app/services/product_service.py
from typing import List, Optional
from app.models.product import Product, ProductCreate, ProductUpdate
from app.core.database import get_db
from app.utils.exceptions import ProductNotFoundError

class ProductService:
    def __init__(self, db_client):
        self.db = db_client
    
    async def get_products(
        self, 
        shop_id: int, 
        page: int = 1, 
        limit: int = 20,
        search: Optional[str] = None
    ) -> List[Product]:
        """Get products with pagination and search"""
        # Implementation here
        pass
    
    async def get_product_by_sku(self, shop_id: int, sku_code: str) -> Product:
        """Get single product by SKU"""
        # Implementation here
        pass
    
    async def create_product(self, shop_id: int, product_data: ProductCreate) -> Product:
        """Create new product"""
        # Implementation here
        pass
    
    async def update_product(
        self, 
        shop_id: int, 
        sku_code: str, 
        product_data: ProductUpdate
    ) -> Product:
        """Update existing product"""
        # Implementation here
        pass
    
    async def delete_product(self, shop_id: int, sku_code: str) -> bool:
        """Delete product"""
        # Implementation here
        pass
```

### Integration Layer Structure
```python
# app/integrations/shopify/client.py
from typing import Dict, List, Optional
import httpx
from app.core.config import settings
from app.utils.exceptions import ShopifyAPIError

class ShopifyClient:
    def __init__(self, shop_domain: str, access_token: str):
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.base_url = f"https://{shop_domain}/admin/api/2024-07"
        self.client = httpx.AsyncClient(
            headers={"X-Shopify-Access-Token": access_token},
            timeout=30.0
        )
    
    async def get_products(self, limit: int = 250, page_info: str = None) -> Dict:
        """Get products from Shopify"""
        params = {"limit": limit}
        if page_info:
            params["page_info"] = page_info
        
        try:
            response = await self.client.get(f"{self.base_url}/products.json", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ShopifyAPIError(f"Failed to fetch products: {e}")
    
    async def get_orders(self, limit: int = 250, created_at_min: str = None) -> Dict:
        """Get orders from Shopify"""
        # Implementation here
        pass
```

## Configuration Management

### Environment Configuration
```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Retail AI Advisor"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Database settings
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # External API settings
    SHOPIFY_CLIENT_ID: str
    SHOPIFY_CLIENT_SECRET: str
    ZENROWS_API_KEY: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    ELEVENLABS_API_KEY: str
    VEED_API_KEY: str
    
    # Azure settings
    AZURE_KEY_VAULT_URL: Optional[str] = None
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    
    # Security settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Performance settings
    DB_POOL_SIZE: int = 10
    CACHE_TTL: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Docker Configuration
```dockerfile
# backend/Dockerfile
FROM python:3.11.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Development Workflow

### Local Development Setup
```bash
#!/bin/bash
# scripts/setup-dev.sh

echo "Setting up Retail AI Advisor development environment..."

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }

# Setup frontend
echo "Setting up frontend..."
cd frontend
npm install
cp .env.local.example .env.local
echo "Please update frontend/.env.local with your configuration"

# Setup backend
echo "Setting up backend..."
cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
echo "Please update backend/.env with your configuration"

# Setup database
echo "Starting local services..."
cd ..
docker-compose up -d redis

echo "Development environment setup complete!"
echo "Next steps:"
echo "1. Update configuration files with your API keys"
echo "2. Run 'npm run dev' in the frontend directory"
echo "3. Run 'uvicorn main:app --reload' in the backend directory"
```

### Package.json Workspace Configuration
```json
{
  "name": "retail-ai-advisor",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "frontend"
  ],
  "scripts": {
    "dev": "concurrently \"npm run dev:frontend\" \"npm run dev:backend\"",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:backend": "cd backend && uvicorn main:app --reload",
    "build": "npm run build:frontend",
    "build:frontend": "cd frontend && npm run build",
    "test": "npm run test:frontend && npm run test:backend",
    "test:frontend": "cd frontend && npm run test",
    "test:backend": "cd backend && pytest",
    "lint": "npm run lint:frontend && npm run lint:backend",
    "lint:frontend": "cd frontend && npm run lint",
    "lint:backend": "cd backend && flake8 .",
    "docker:build": "./scripts/build-docker.sh",
    "docker:up": "docker-compose up -d",
    "docker:down": "docker-compose down"
  },
  "devDependencies": {
    "concurrently": "^8.2.0"
  }
}
```

---

**Next**: [CI/CD Pipeline](./09-cicd-pipeline.md)
