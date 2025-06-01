# Shopify Integration Deployment Checklist

This checklist ensures a successful deployment of the Shopify integration to production environments.

## Pre-Deployment Checklist

### 1. Shopify App Configuration

- [ ] **Shopify Partner Account**: Created and verified
- [ ] **Shopify App**: Created in Partner Dashboard
- [ ] **App Type**: Selected (Public/Custom) based on requirements
- [ ] **OAuth URLs**: Configured for production domain
  - [ ] App URL: `https://your-domain.com`
  - [ ] Redirect URL: `https://your-domain.com/api/v1/shopify/oauth/callback`
- [ ] **Scopes**: Configured with required permissions
  - [ ] `read_products`
  - [ ] `read_inventory`
  - [ ] `read_orders`
  - [ ] `read_price_rules`
- [ ] **Webhook URLs**: Configured for production endpoints
  - [ ] Orders create: `https://your-domain.com/api/v1/shopify/webhooks/orders_create`
  - [ ] Orders update: `https://your-domain.com/api/v1/shopify/webhooks/orders_update`
  - [ ] Products create: `https://your-domain.com/api/v1/shopify/webhooks/products_create`
  - [ ] Products update: `https://your-domain.com/api/v1/shopify/webhooks/products_update`
  - [ ] App uninstalled: `https://your-domain.com/api/v1/shopify/webhooks/app_uninstalled`
- [ ] **Webhook Secret**: Generated and configured

### 2. Database Setup

- [ ] **Production Database**: PostgreSQL instance ready
- [ ] **Database Migration**: Shopify tables created
  ```bash
  python run_shopify_migration.py
  ```
- [ ] **Database Permissions**: Application user has required permissions
- [ ] **Connection Pooling**: Configured for production load
- [ ] **Backup Strategy**: Database backup plan in place
- [ ] **Monitoring**: Database monitoring configured

### 3. Environment Configuration

#### Backend Environment Variables

- [ ] **Core Settings**:
  - [ ] `ENVIRONMENT=production`
  - [ ] `DEBUG=false`
  - [ ] `SECRET_KEY` (secure, unique)
  - [ ] `JWT_SECRET_KEY` (secure, unique)

- [ ] **Database**:
  - [ ] `DATABASE_URL` (production PostgreSQL)
  - [ ] `SUPABASE_URL` (if using Supabase)
  - [ ] `SUPABASE_SERVICE_ROLE_KEY` (if using Supabase)

- [ ] **Shopify Integration**:
  - [ ] `SHOPIFY_CLIENT_ID`
  - [ ] `SHOPIFY_CLIENT_SECRET`
  - [ ] `SHOPIFY_API_VERSION=2024-07`
  - [ ] `SHOPIFY_SCOPES=read_products,read_inventory,read_orders,read_price_rules`
  - [ ] `SHOPIFY_WEBHOOK_SECRET`

- [ ] **Application URLs**:
  - [ ] `FRONTEND_URL` (production frontend URL)
  - [ ] `BACKEND_URL` (production backend URL)
  - [ ] `ALLOWED_ORIGINS` (production domains only)

#### Frontend Environment Variables

- [ ] **API Configuration**:
  - [ ] `NEXT_PUBLIC_API_URL` (production backend URL)

- [ ] **Supabase**:
  - [ ] `NEXT_PUBLIC_SUPABASE_URL`
  - [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`

- [ ] **App Configuration**:
  - [ ] `NEXT_PUBLIC_APP_NAME=Retail AI Advisor`
  - [ ] `NEXT_PUBLIC_APP_VERSION`
  - [ ] `NODE_ENV=production`

### 4. Security Configuration

- [ ] **SSL Certificates**: Valid SSL certificates installed
- [ ] **HTTPS Enforcement**: All traffic redirected to HTTPS
- [ ] **CORS Configuration**: Restricted to production domains
- [ ] **Rate Limiting**: Configured and tested
- [ ] **Input Validation**: All endpoints validate input
- [ ] **Error Handling**: No sensitive data in error responses
- [ ] **Webhook Verification**: HMAC signature verification enabled
- [ ] **Database Security**: Row Level Security (RLS) enabled

### 5. Infrastructure Setup

- [ ] **Server Resources**: Adequate CPU, memory, and storage
- [ ] **Load Balancer**: Configured if using multiple instances
- [ ] **CDN**: Configured for static assets
- [ ] **Monitoring**: Application and infrastructure monitoring
- [ ] **Logging**: Centralized logging configured
- [ ] **Backup**: Automated backup strategy
- [ ] **Disaster Recovery**: Recovery plan documented

## Deployment Process

### 1. Backend Deployment

- [ ] **Code Deployment**: Latest code deployed to production
- [ ] **Dependencies**: All Python packages installed
  ```bash
  pip install -r requirements.txt
  ```
- [ ] **Database Migration**: Run migration if not already done
  ```bash
  python run_shopify_migration.py
  ```
- [ ] **Environment Variables**: All variables configured
- [ ] **Service Start**: Backend service started and running
- [ ] **Health Check**: Backend health endpoint responding
  ```bash
  curl https://your-backend-domain.com/health
  ```

### 2. Frontend Deployment

- [ ] **Build Process**: Frontend built for production
  ```bash
  npm run build
  ```
- [ ] **Static Assets**: Deployed to CDN or static hosting
- [ ] **Environment Variables**: Production variables configured
- [ ] **Service Start**: Frontend service started
- [ ] **Health Check**: Frontend loading correctly
  ```bash
  curl https://your-frontend-domain.com
  ```

### 3. Integration Testing

- [ ] **API Endpoints**: All Shopify endpoints responding
  - [ ] `GET /api/v1/shopify/stores`
  - [ ] `POST /api/v1/shopify/oauth/authorize`
  - [ ] `POST /api/v1/shopify/oauth/callback`
- [ ] **Database Connectivity**: Backend can connect to database
- [ ] **Shopify API**: Backend can communicate with Shopify API
- [ ] **Webhook Endpoints**: All webhook URLs accessible
- [ ] **Frontend Integration**: Frontend can call backend APIs

## Post-Deployment Testing

### 1. OAuth Flow Testing

- [ ] **Development Store**: Create test development store
- [ ] **OAuth URL Generation**: Test OAuth URL generation
- [ ] **Authorization Flow**: Complete full OAuth flow
- [ ] **Store Connection**: Verify store appears in connected stores
- [ ] **Token Storage**: Verify access token stored securely

### 2. Product Sync Testing

- [ ] **Initial Sync**: Test initial product synchronization
- [ ] **Sync Status**: Verify sync job status tracking
- [ ] **Data Accuracy**: Compare synced data with Shopify
- [ ] **Error Handling**: Test sync with invalid data
- [ ] **Performance**: Verify sync performance with large catalogs

### 3. Webhook Testing

- [ ] **Webhook Registration**: Verify webhooks registered in Shopify
- [ ] **Order Events**: Test order creation/update webhooks
- [ ] **Product Events**: Test product creation/update webhooks
- [ ] **Signature Verification**: Verify HMAC signature validation
- [ ] **Error Handling**: Test webhook error scenarios

### 4. User Interface Testing

- [ ] **Store Connection**: Test store connection UI
- [ ] **Store Dashboard**: Verify store statistics display
- [ ] **Sync Controls**: Test manual sync triggers
- [ ] **Error Messages**: Verify user-friendly error messages
- [ ] **Responsive Design**: Test on different screen sizes

## Monitoring and Maintenance

### 1. Monitoring Setup

- [ ] **Application Monitoring**: APM tools configured
- [ ] **Error Tracking**: Sentry or similar error tracking
- [ ] **Performance Monitoring**: Response time and throughput
- [ ] **Database Monitoring**: Query performance and connections
- [ ] **Infrastructure Monitoring**: Server resources and uptime
- [ ] **Business Metrics**: Store connections and sync success rates

### 2. Alerting Configuration

- [ ] **Error Rate Alerts**: High error rate notifications
- [ ] **Performance Alerts**: Slow response time alerts
- [ ] **Database Alerts**: Connection and performance issues
- [ ] **Webhook Alerts**: Failed webhook processing
- [ ] **Sync Alerts**: Failed synchronization jobs
- [ ] **Security Alerts**: Suspicious activity detection

### 3. Maintenance Procedures

- [ ] **Regular Backups**: Automated database backups
- [ ] **Log Rotation**: Log file management
- [ ] **Security Updates**: Regular dependency updates
- [ ] **Performance Optimization**: Regular performance reviews
- [ ] **Capacity Planning**: Resource usage monitoring
- [ ] **Documentation Updates**: Keep documentation current

## Rollback Plan

### 1. Rollback Triggers

- [ ] **Critical Errors**: High error rates or system failures
- [ ] **Performance Issues**: Unacceptable response times
- [ ] **Data Corruption**: Database integrity issues
- [ ] **Security Breaches**: Security vulnerabilities discovered

### 2. Rollback Procedure

- [ ] **Code Rollback**: Revert to previous stable version
- [ ] **Database Rollback**: Restore from backup if needed
- [ ] **Configuration Rollback**: Revert environment variables
- [ ] **DNS Rollback**: Point traffic to previous version
- [ ] **Monitoring**: Verify rollback success
- [ ] **Communication**: Notify stakeholders of rollback

## Sign-off

### Technical Team

- [ ] **Backend Developer**: Deployment verified
- [ ] **Frontend Developer**: UI/UX verified
- [ ] **DevOps Engineer**: Infrastructure verified
- [ ] **QA Engineer**: Testing completed
- [ ] **Security Engineer**: Security review completed

### Business Team

- [ ] **Product Manager**: Features verified
- [ ] **Business Stakeholder**: Requirements met
- [ ] **Support Team**: Documentation reviewed

### Final Approval

- [ ] **Technical Lead**: Technical approval
- [ ] **Project Manager**: Project approval
- [ ] **Release Manager**: Release approval

---

**Deployment Date**: _______________

**Deployed By**: _______________

**Approved By**: _______________

**Notes**: 
_________________________________
_________________________________
_________________________________

This checklist ensures a comprehensive and successful deployment of the Shopify integration. Complete each item before proceeding to the next phase.