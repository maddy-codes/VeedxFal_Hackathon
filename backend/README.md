# Retail AI Advisor Backend

AI-powered retail analytics and pricing optimization backend built with FastAPI.

## Features

- **Authentication**: Supabase Auth integration with JWT tokens
- **Product Management**: CRUD operations for products with advanced filtering
- **Data Synchronization**: Shopify integration and CSV upload fallback
- **Analytics**: Comprehensive dashboard analytics and business insights
- **AI Video Generation**: Automated video creation with Azure OpenAI, ElevenLabs, and VEED.io
- **External Integrations**: ZenRows, Google Trends, API Deck, and more
- **Security**: Row Level Security, rate limiting, and comprehensive logging
- **Performance**: Async operations, caching, and optimized database queries

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL via Supabase
- **Authentication**: Supabase Auth
- **Caching**: Redis
- **Background Jobs**: Celery (planned)
- **Monitoring**: Structured logging with Sentry
- **Deployment**: Docker + Azure App Service

## Project Structure

```
backend/
├── app/
│   ├── api/                    # API routes and middleware
│   │   ├── middleware/         # Authentication, rate limiting
│   │   ├── v1/                 # API v1 endpoints
│   │   └── deps.py             # FastAPI dependencies
│   ├── core/                   # Core application modules
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database connection
│   │   ├── security.py         # Authentication & authorization
│   │   └── logging.py          # Structured logging
│   ├── models/                 # Pydantic models
│   │   ├── auth.py             # Authentication models
│   │   ├── product.py          # Product models
│   │   ├── sync.py             # Synchronization models
│   │   ├── analytics.py        # Analytics models
│   │   └── video.py            # Video generation models
│   ├── services/               # Business logic services
│   ├── integrations/           # External service integrations
│   ├── utils/                  # Utility functions
│   └── workers/                # Background job workers
├── tests/                      # Test suite
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
└── README.md                   # This file
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/auth/stores/current` - Get current user's store
- `POST /api/v1/auth/stores/shopify/connect` - Connect Shopify store

### Products
- `GET /api/v1/products` - Get products with filtering and pagination
- `GET /api/v1/products/{sku_code}` - Get product by SKU
- `POST /api/v1/products` - Create product
- `PUT /api/v1/products/{sku_code}` - Update product
- `DELETE /api/v1/products/{sku_code}` - Delete product

### Data Synchronization
- `POST /api/v1/sync/shopify` - Trigger Shopify data sync
- `GET /api/v1/sync/status` - Get sync status
- `POST /api/v1/sync/competitor-prices` - Update competitor prices
- `POST /api/v1/sync/trends` - Update trend data

### Analytics
- `GET /api/v1/analytics/dashboard` - Get dashboard analytics
- `GET /api/v1/analytics/insights` - Get business insights for AI video

### Video Generation
- `POST /api/v1/video/generate` - Generate AI video
- `GET /api/v1/video/status/{job_id}` - Get video generation status
- `GET /api/v1/video/latest` - Get latest videos
- `POST /api/v1/video/{video_id}/view` - Record video view

### File Upload
- `POST /api/v1/upload/csv/products` - Upload products CSV
- `POST /api/v1/upload/csv/sales` - Upload sales CSV

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (via Supabase)
- Redis
- Docker (optional)

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/retail_ai_advisor
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Security
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# External APIs
SHOPIFY_CLIENT_ID=your-shopify-client-id
SHOPIFY_CLIENT_SECRET=your-shopify-client-secret
ZENROWS_API_KEY=your-zenrows-api-key
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
ELEVENLABS_API_KEY=your-elevenlabs-key
VEED_API_KEY=your-veed-api-key

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Set up database:**
   - Create Supabase project
   - Run database migrations (SQL from docs/architecture/02-database-schema.md)

3. **Start Redis:**
   ```bash
   redis-server
   ```

4. **Run the application:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Development

1. **Build and run with Docker:**
   ```bash
   docker build -t retail-ai-advisor-backend .
   docker run -p 8000:8000 --env-file .env retail-ai-advisor-backend
   ```

2. **Or use Docker Compose (if available):**
   ```bash
   docker-compose up --build
   ```

## Database Schema

The application uses 6 core tables:

- **stores**: Multi-tenant store management
- **products**: Product catalog with SKU management
- **sales**: Historical sales transactions
- **competitor_prices**: Competitor pricing data
- **trend_insights**: Market trend analysis
- **recommended_prices**: AI-generated pricing recommendations

See `docs/architecture/02-database-schema.md` for complete schema.

## Security

- **Authentication**: Supabase Auth with JWT tokens
- **Authorization**: Row Level Security (RLS) for multi-tenant isolation
- **Rate Limiting**: Redis-based distributed rate limiting
- **Input Validation**: Pydantic models with comprehensive validation
- **Secrets Management**: Azure Key Vault integration (production)
- **CORS**: Configurable CORS origins
- **Security Headers**: Comprehensive security middleware

## Performance

- **Async Operations**: Full async/await support
- **Connection Pooling**: Optimized database connections
- **Caching**: Redis caching for frequently accessed data
- **Query Optimization**: Indexed queries and efficient joins
- **Background Jobs**: Celery for long-running tasks
- **Rate Limiting**: Prevents API abuse

## Monitoring & Logging

- **Structured Logging**: JSON logs with contextual information
- **Error Tracking**: Sentry integration for error monitoring
- **Performance Metrics**: Prometheus metrics (planned)
- **Health Checks**: Comprehensive health check endpoints
- **Business Events**: Detailed business event logging

## External Integrations

### Shopify
- OAuth 2.0 authentication
- Product and sales data synchronization
- Webhook support for real-time updates

### ZenRows
- Competitor price scraping
- Rate limiting and retry logic
- Error handling and fallbacks

### Google Trends
- Market trend analysis
- Batch processing for efficiency
- Trend scoring algorithms

### AI Services
- **Azure OpenAI**: Script generation for videos
- **ElevenLabs**: Text-to-speech conversion
- **VEED.io**: Video composition and generation

### API Deck
- Accounting system integration
- Cost price synchronization
- Multi-platform support

## Testing

Run tests with:

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=app tests/
```

## Deployment

### Azure App Service

1. **Build Docker image:**
   ```bash
   docker build -t retail-ai-advisor-backend .
   ```

2. **Push to Azure Container Registry:**
   ```bash
   az acr build --registry myregistry --image retail-ai-advisor-backend .
   ```

3. **Deploy to App Service:**
   ```bash
   az webapp create --resource-group mygroup --plan myplan --name myapp --deployment-container-image-name myregistry.azurecr.io/retail-ai-advisor-backend:latest
   ```

### Environment Configuration

Set environment variables in Azure App Service:
- Use Azure Key Vault for secrets
- Configure connection strings
- Set up monitoring and logging

## API Documentation

- **OpenAPI Spec**: Available at `/openapi.json`
- **Swagger UI**: Available at `/docs` (development only)
- **ReDoc**: Available at `/redoc` (development only)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run linting and tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.