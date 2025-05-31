# System Architecture Overview

## High-Level Architecture

The Retail AI Advisor follows a modern microservices architecture pattern with clear separation of concerns, designed for rapid MVP development while maintaining scalability for future growth.

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Next.js Dashboard<br/>React 18 + TypeScript]
        AUTH[Supabase Auth<br/>Email/Password]
    end
    
    subgraph "API Gateway Layer"
        API[FastAPI Backend<br/>Python 3.11.8]
        RATE[Rate Limiting<br/>& Security]
    end
    
    subgraph "Data Processing Layer"
        SYNC[Data Sync Service<br/>Shopify Integration]
        SCRAPE[Competitor Scraping<br/>ZenRows Service]
        TRENDS[Trends Analysis<br/>Google Trends + Social]
        PRICING[Pricing Engine<br/>AI Recommendations]
        VIDEO[Video Generation<br/>AI Pipeline]
    end
    
    subgraph "External Services"
        SHOPIFY[Shopify API<br/>OAuth 2.0]
        ZENROWS[ZenRows<br/>Web Scraping]
        GTRENDS[Google Trends<br/>pytrends]
        APIDECK[API Deck<br/>Accounting Data]
        OPENAI[Azure OpenAI<br/>GPT-4 Turbo]
        ELEVEN[ElevenLabs<br/>Text-to-Speech]
        VEED[VEED.io<br/>Video Generation]
    end
    
    subgraph "Data Layer"
        DB[(Supabase PostgreSQL<br/>Row Level Security)]
        BLOB[Azure Blob Storage<br/>Videos & Files]
        VAULT[Azure Key Vault<br/>Secrets Management]
    end
    
    subgraph "Infrastructure Layer"
        STATIC[Azure Static Web Apps<br/>Frontend Hosting]
        APPSERVICE[Azure App Service<br/>Backend API]
        FUNCTIONS[Azure Functions<br/>Background Jobs]
        MONITOR[Azure Monitor<br/>Application Insights]
    end
    
    UI --> AUTH
    UI --> API
    API --> RATE
    RATE --> SYNC
    RATE --> SCRAPE
    RATE --> TRENDS
    RATE --> PRICING
    RATE --> VIDEO
    
    SYNC --> SHOPIFY
    SCRAPE --> ZENROWS
    TRENDS --> GTRENDS
    PRICING --> APIDECK
    VIDEO --> OPENAI
    VIDEO --> ELEVEN
    VIDEO --> VEED
    
    API --> DB
    VIDEO --> BLOB
    API --> VAULT
    
    UI -.-> STATIC
    API -.-> APPSERVICE
    SYNC -.-> FUNCTIONS
    SCRAPE -.-> FUNCTIONS
    TRENDS -.-> FUNCTIONS
    VIDEO -.-> FUNCTIONS
    
    API --> MONITOR
    FUNCTIONS --> MONITOR
```

## Component Architecture

### Frontend Components

```mermaid
graph TB
    subgraph "Next.js Application"
        APP[App Router<br/>Next.js 14.2.3]
        PAGES[Page Components]
        COMPONENTS[Reusable Components]
        HOOKS[Custom Hooks]
        STORE[Zustand State Management]
    end
    
    subgraph "UI Components"
        DASHBOARD[Dashboard Layout]
        PRODUCTS[Product Table]
        FILTERS[Search & Filters]
        VIDEO[Video Player]
        AUTH_UI[Auth Components]
    end
    
    subgraph "Data Layer"
        QUERY[React Query<br/>Data Fetching]
        SUPABASE_CLIENT[Supabase Client<br/>Real-time Updates]
    end
    
    APP --> PAGES
    PAGES --> COMPONENTS
    COMPONENTS --> HOOKS
    HOOKS --> STORE
    
    PAGES --> DASHBOARD
    DASHBOARD --> PRODUCTS
    DASHBOARD --> FILTERS
    DASHBOARD --> VIDEO
    DASHBOARD --> AUTH_UI
    
    COMPONENTS --> QUERY
    QUERY --> SUPABASE_CLIENT
```

### Backend Services Architecture

```mermaid
graph TB
    subgraph "FastAPI Application"
        MAIN[Main Application<br/>FastAPI Instance]
        ROUTERS[API Routers]
        MIDDLEWARE[Security Middleware]
        DEPS[Dependencies]
    end
    
    subgraph "Business Logic"
        SHOPIFY_SERVICE[Shopify Service<br/>OAuth & Data Sync]
        COMPETITOR_SERVICE[Competitor Service<br/>Price Scraping]
        TRENDS_SERVICE[Trends Service<br/>Market Analysis]
        PRICING_SERVICE[Pricing Service<br/>Recommendations]
        VIDEO_SERVICE[Video Service<br/>AI Generation]
    end
    
    subgraph "Data Access Layer"
        SUPABASE_ORM[Supabase Client<br/>Database Operations]
        BLOB_CLIENT[Azure Blob Client<br/>File Operations]
        VAULT_CLIENT[Key Vault Client<br/>Secrets Access]
    end
    
    MAIN --> ROUTERS
    MAIN --> MIDDLEWARE
    ROUTERS --> DEPS
    
    ROUTERS --> SHOPIFY_SERVICE
    ROUTERS --> COMPETITOR_SERVICE
    ROUTERS --> TRENDS_SERVICE
    ROUTERS --> PRICING_SERVICE
    ROUTERS --> VIDEO_SERVICE
    
    SHOPIFY_SERVICE --> SUPABASE_ORM
    COMPETITOR_SERVICE --> SUPABASE_ORM
    TRENDS_SERVICE --> SUPABASE_ORM
    PRICING_SERVICE --> SUPABASE_ORM
    VIDEO_SERVICE --> SUPABASE_ORM
    VIDEO_SERVICE --> BLOB_CLIENT
    
    SUPABASE_ORM --> VAULT_CLIENT
```

## Data Flow Architecture

### Daily Data Processing Pipeline

```mermaid
sequenceDiagram
    participant CRON as Azure Functions<br/>Daily Cron (02:00 AM)
    participant API as FastAPI Backend
    participant SHOPIFY as Shopify API
    participant ZENROWS as ZenRows API
    participant GTRENDS as Google Trends
    participant APIDECK as API Deck
    participant DB as Supabase DB
    participant AI as AI Services
    participant BLOB as Azure Blob
    
    CRON->>API: Trigger Daily Sync
    
    Note over API,SHOPIFY: 1. Shopify Data Sync
    API->>SHOPIFY: Fetch Products & Sales
    SHOPIFY-->>API: Product/Sales Data
    API->>DB: Upsert Products & Sales
    
    Note over API,APIDECK: 2. Accounting Cost Update
    API->>APIDECK: Fetch Cost Prices
    APIDECK-->>API: Cost Data by SKU
    API->>DB: Update Product Costs
    
    Note over API,ZENROWS: 3. Competitor Pricing
    API->>ZENROWS: Scrape Competitor URLs
    ZENROWS-->>API: Competitor Prices
    API->>DB: Update Competitor Prices
    
    Note over API,GTRENDS: 4. Market Trends
    API->>GTRENDS: Fetch Trend Data
    GTRENDS-->>API: Trend Scores
    API->>DB: Update Trend Insights
    
    Note over API,DB: 5. Pricing Engine
    API->>DB: Calculate Recommendations
    API->>DB: Store Recommended Prices
    
    Note over API,AI: 6. Video Generation
    API->>AI: Generate Insights Script
    AI-->>API: Video Script
    API->>AI: Create Video
    AI-->>API: Video URL
    API->>BLOB: Store Video
    API->>DB: Update Video Reference
    
    CRON-->>API: Pipeline Complete
```

### Real-time User Interaction Flow

```mermaid
sequenceDiagram
    participant USER as User Browser
    participant NEXT as Next.js Frontend
    participant AUTH as Supabase Auth
    participant API as FastAPI Backend
    participant DB as Supabase DB
    participant BLOB as Azure Blob
    
    USER->>NEXT: Access Dashboard
    NEXT->>AUTH: Check Authentication
    AUTH-->>NEXT: JWT Token
    
    NEXT->>API: Fetch Dashboard Data
    API->>DB: Query Products & Insights
    DB-->>API: Product Data
    API-->>NEXT: Dashboard Response
    NEXT-->>USER: Render Dashboard
    
    USER->>NEXT: Request Video Playback
    NEXT->>API: Get Video URL
    API->>DB: Query Latest Video
    DB-->>API: Video Reference
    API->>BLOB: Get Video URL
    BLOB-->>API: Signed URL
    API-->>NEXT: Video URL
    NEXT-->>USER: Stream Video
    
    USER->>NEXT: Filter Products
    NEXT->>API: Filter Request
    API->>DB: Filtered Query
    DB-->>API: Filtered Results
    API-->>NEXT: Updated Data
    NEXT-->>USER: Updated Table
```

## Service Communication Patterns

### Synchronous Communication
- **Frontend ↔ Backend**: REST API calls with JWT authentication
- **Backend ↔ Database**: Direct SQL queries via Supabase client
- **Backend ↔ External APIs**: HTTP requests with retry logic

### Asynchronous Communication
- **Background Jobs**: Azure Functions triggered by timer or queue
- **File Processing**: Event-driven blob storage operations
- **Real-time Updates**: Supabase real-time subscriptions (future enhancement)

## Error Handling & Resilience Patterns

### Circuit Breaker Pattern
```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open : Failure Threshold Exceeded
    Open --> HalfOpen : Timeout Elapsed
    HalfOpen --> Closed : Success
    HalfOpen --> Open : Failure
    
    Closed : Normal Operation<br/>Requests Pass Through
    Open : Fail Fast<br/>Return Cached/Default Data
    HalfOpen : Test Recovery<br/>Limited Requests
```

### Retry Strategy
- **Exponential Backoff**: 1s, 2s, 4s, 8s intervals
- **Maximum Retries**: 3 attempts for external APIs
- **Jitter**: Random delay to prevent thundering herd
- **Circuit Breaker**: Fail fast after threshold

## Security Architecture Layers

### Defense in Depth
1. **Network Security**: Azure Virtual Network, NSGs
2. **Application Security**: JWT tokens, CORS, rate limiting
3. **Data Security**: Row Level Security, encryption at rest
4. **Secret Management**: Azure Key Vault integration
5. **Monitoring**: Application Insights, security alerts

## Scalability Considerations

### Horizontal Scaling
- **Frontend**: CDN distribution, multiple regions
- **Backend**: Load balancer with multiple App Service instances
- **Database**: Read replicas, connection pooling
- **Functions**: Consumption plan auto-scaling

### Vertical Scaling
- **App Service**: Scale up to higher SKUs
- **Database**: Increase compute and storage
- **Blob Storage**: Premium tier for higher IOPS

### Caching Strategy
- **Browser Cache**: Static assets, API responses
- **CDN Cache**: Global content distribution
- **Application Cache**: Redis for session data
- **Database Cache**: Query result caching

## Performance Optimization

### Frontend Optimization
- **Code Splitting**: Route-based lazy loading
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: Webpack bundle analyzer
- **Prefetching**: Link prefetching for navigation

### Backend Optimization
- **Database Indexing**: Strategic index placement
- **Query Optimization**: Efficient SQL queries
- **Connection Pooling**: Supabase connection management
- **Async Processing**: Background job queues

### Infrastructure Optimization
- **Auto-scaling**: Demand-based resource allocation
- **Load Balancing**: Traffic distribution
- **Monitoring**: Performance metrics and alerts
- **Cost Optimization**: Reserved instances, spot pricing

---

**Next**: [Database Schema Design](./02-database-schema.md)