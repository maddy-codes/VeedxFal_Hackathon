# Retail AI Advisor

A comprehensive AI-powered retail analytics platform that provides intelligent insights, cost-plus pricing optimization, and video-based product analysis for retail businesses.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- Azure CLI (for deployment)
- Supabase account

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd application
   ```

2. **Backend Setup**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   pip install -r requirements.txt
   python main.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📋 Features

### Core Functionality
- **Product Insights Dashboard**: Real-time analytics and performance metrics
- **Cost-Plus Pricing Calculator**: AI-powered pricing optimization
- **Video Insights**: Automated video analysis and recommendations
- **Shopify Integration**: Complete store connection, product sync, and order management
- **Multi-Platform Integration**: Shopify, WooCommerce, and custom APIs
- **Advanced Analytics**: Trend analysis and predictive insights

### Shopify Integration Features
- **OAuth 2.0 Authentication**: Secure store connection with proper authorization
- **Real-time Product Sync**: Automatic synchronization of products and inventory
- **Order Management**: Complete order tracking and analytics
- **Webhook Processing**: Real-time updates for orders, products, and inventory
- **Multi-store Support**: Connect and manage multiple Shopify stores
- **Background Sync Jobs**: Efficient bulk data synchronization

### Technical Features
- **Authentication**: Secure JWT-based authentication with Supabase
- **Real-time Updates**: WebSocket connections for live data
- **Scalable Architecture**: Microservices with Docker containerization
- **Cloud-Ready**: Azure deployment with CI/CD pipelines
- **Monitoring**: Comprehensive logging and error tracking

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11, SQLAlchemy
- **Database**: PostgreSQL (Supabase)
- **Authentication**: Supabase Auth
- **Deployment**: Azure Static Web Apps + Azure App Service
- **Monitoring**: Sentry, Prometheus

### Color Palette
- **Primary**: #427F8C (Dark Teal)
- **Secondary**: #73B1BF (Medium Teal)
- **Accent**: #CECF2F (Light Blue/Cyan)
- **Background**: #F2F2F2 (Light Gray)
- **Text**: #0D0D0D (Black)

## 📚 Documentation

- [**Deployment Guide**](./DEPLOYMENT.md) - Complete deployment instructions
- [**API Documentation**](./API_DOCUMENTATION.md) - Backend API reference
- [**User Guide**](./USER_GUIDE.md) - End-user documentation
- [**Architecture Overview**](./ARCHITECTURE.md) - Technical architecture
- [**Demo Guide**](./DEMO_GUIDE.md) - Demo preparation and script

### Shopify Integration Documentation
- [**Shopify Setup Guide**](./docs/SHOPIFY_SETUP.md) - Complete Shopify integration setup
- [**Shopify API Documentation**](./docs/SHOPIFY_API.md) - Shopify API endpoints and usage
- [**Shopify User Guide**](./docs/SHOPIFY_USER_GUIDE.md) - End-user Shopify features guide

### Architecture Documentation
- [System Architecture](./docs/architecture/01-system-architecture.md)
- [Database Schema](./docs/architecture/02-database-schema.md)
- [API Specifications](./docs/architecture/03-api-specifications.md)
- [Security Architecture](./docs/architecture/04-security-architecture.md)
- [External Integrations](./docs/architecture/05-external-integrations.md)
- [Deployment Architecture](./docs/architecture/06-deployment-architecture.md)
- [Performance Optimization](./docs/architecture/07-performance-optimization.md)
- [Project Structure](./docs/architecture/08-project-structure.md)
- [CI/CD Pipeline](./docs/architecture/09-cicd-pipeline.md)
- [Monitoring & Error Handling](./docs/architecture/10-monitoring-error-handling.md)

## 🚀 Deployment

### Production Deployment
1. **Azure Setup**: Configure Azure resources
2. **Environment Variables**: Set production environment variables
3. **Database**: Set up Supabase production database
4. **CI/CD**: Configure GitHub Actions workflows
5. **Monitoring**: Set up Sentry and logging

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

### Environment Configuration
```bash
# Backend (.env)
ENVIRONMENT=production
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SECRET_KEY=...

# Shopify Integration
SHOPIFY_CLIENT_ID=your_shopify_client_id
SHOPIFY_CLIENT_SECRET=your_shopify_client_secret
SHOPIFY_API_VERSION=2024-07
SHOPIFY_SCOPES=read_products,read_inventory,read_orders,read_price_rules

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://your-api.azurewebsites.net
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Testing
```bash
cd frontend
npm test
npm run test:e2e
```

## 📊 Performance

### Benchmarks
- **API Response Time**: < 200ms (95th percentile)
- **Frontend Load Time**: < 2s (First Contentful Paint)
- **Database Queries**: < 100ms average
- **Concurrent Users**: 1000+ supported

### Monitoring
- **Uptime**: 99.9% SLA target
- **Error Rate**: < 0.1%
- **Response Time**: Real-time monitoring
- **Resource Usage**: CPU, Memory, Database metrics

## 🔒 Security

### Security Measures
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: TLS 1.3 in transit, AES-256 at rest
- **API Security**: Rate limiting, CORS, input validation
- **Infrastructure**: Azure security best practices

### Compliance
- **GDPR**: Data privacy and user rights
- **SOC 2**: Security controls and monitoring
- **PCI DSS**: Payment data security (if applicable)

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request
5. Code review and merge

### Code Standards
- **Python**: Black, isort, flake8, mypy
- **TypeScript**: ESLint, Prettier
- **Testing**: 80%+ code coverage
- **Documentation**: Comprehensive inline docs

## 📞 Support

### Getting Help
- **Documentation**: Check the docs/ directory
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Email**: support@retailaiadvisor.com

### Troubleshooting
See [USER_GUIDE.md](./USER_GUIDE.md) for common issues and solutions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Supabase**: Database and authentication
- **Azure**: Cloud infrastructure
- **OpenAI**: AI capabilities
- **VEED.io**: Video processing
- **Community**: Open source contributors

---

**Retail AI Advisor** - Empowering retail businesses with intelligent insights and AI-driven optimization.