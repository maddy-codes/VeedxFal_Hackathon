# OAuth Token Exchange Debug Guide

## Quick Start for Debugging

### 1. Enable Detailed Logging

To see all the enhanced OAuth logging, you need to set the log level to INFO:

**Option A: Environment Variable**
```bash
export LOG_LEVEL=INFO
```

**Option B: Update .env file**
```bash
echo "LOG_LEVEL=INFO" >> .env
```

**Option C: Temporary for testing**
```bash
LOG_LEVEL=INFO python main.py
```

### 2. Test the Enhanced Logging

Run the logging test script to verify everything works:

```bash
cd backend
python test_enhanced_logging.py
```

You should see output like:
```
=== TESTING OAUTH TOKEN EXCHANGE ===
✓ Input validation passed
=== PREPARING TOKEN EXCHANGE REQUEST ===
✓ Request prepared successfully
=== OAUTH TOKEN EXCHANGE TEST COMPLETED ===
```

### 3. Monitor OAuth Flow

When testing the actual OAuth flow, watch for these log sections:

#### In the OAuth Callback (`/api/v1/shopify/oauth/callback`):
```
=== OAUTH CALLBACK RECEIVED ===
=== EXTRACTING USER ID FROM STATE ===
=== CALLING TOKEN EXCHANGE SERVICE ===
=== TOKEN EXCHANGE COMPLETED ===
=== OAUTH CALLBACK PROCESSING COMPLETED SUCCESSFULLY ===
```

#### In the Token Exchange Service (`exchange_oauth_code`):
```
=== STARTING OAUTH TOKEN EXCHANGE ===
=== PREPARING TOKEN EXCHANGE REQUEST ===
=== SENDING TOKEN EXCHANGE REQUEST ===
=== RECEIVED TOKEN EXCHANGE RESPONSE ===
=== EXTRACTING ACCESS TOKEN ===
=== VERIFYING SHOP ACCESS ===
=== CREATING STORE DATA ===
=== SAVING TO DATABASE ===
=== OAUTH TOKEN EXCHANGE COMPLETED SUCCESSFULLY ===
```

## Common Failure Points and Debugging

### 1. Input Validation Failures

**Look for:**
```
VALIDATION ERROR: shop_domain is empty or None
VALIDATION ERROR: OAuth code is empty or None
CONFIGURATION ERROR: Shopify OAuth credentials not configured
```

**Debug steps:**
- Check that `SHOPIFY_CLIENT_ID` and `SHOPIFY_CLIENT_SECRET` are set
- Verify the OAuth callback URL parameters
- Ensure the shop domain is properly formatted

### 2. HTTP Request Failures

**Look for:**
```
=== HTTP STATUS ERROR ===
=== HTTP REQUEST ERROR ===
Response status: 400/401/403/500
```

**Debug steps:**
- Check the exact URL being called
- Verify the request payload structure
- Check Shopify API credentials
- Verify network connectivity

### 3. Token Extraction Failures

**Look for:**
```
❌ No access token in response
TOKEN EXTRACTION FAILED
Available response keys: [...]
```

**Debug steps:**
- Check the Shopify response structure
- Verify OAuth code validity
- Check if the OAuth app is properly configured in Shopify

### 4. Shop Verification Failures

**Look for:**
```
=== SHOP ACCESS VERIFICATION FAILED ===
Failed to verify shop access
```

**Debug steps:**
- Verify the access token is valid
- Check if the shop domain is correct
- Ensure the OAuth scopes are sufficient

### 5. Database Failures

**Look for:**
```
=== DATABASE ERROR ===
Database error while saving store
❌ No data returned from database upsert
```

**Debug steps:**
- Check database connectivity
- Verify Supabase credentials
- Check the `shopify_stores` table schema
- Verify user permissions

## Testing OAuth Flow End-to-End

### 1. Generate OAuth URL
```bash
cd backend
python generate_oauth_url.py
```

### 2. Test OAuth Callback
```bash
cd backend
python test_oauth_callback.py
```

### 3. Monitor Logs
Watch the console output for the detailed logging sections mentioned above.

## Log Level Configuration

The application uses different log levels:

- **INFO**: Detailed flow information (what you want for debugging)
- **WARNING**: Non-critical issues and warnings
- **ERROR**: Actual errors and failures

### Current Log Level Settings

Check your current log level:
```bash
grep LOG_LEVEL .env
```

### Recommended Settings for Debugging

**Development:**
```bash
LOG_LEVEL=INFO
ENVIRONMENT=development
DEBUG=true
```

**Production:**
```bash
LOG_LEVEL=WARNING
ENVIRONMENT=production
DEBUG=false
```

## Interpreting the Logs

### Success Indicators
- ✓ symbols indicate successful operations
- Section completion messages
- "COMPLETED SUCCESSFULLY" messages

### Failure Indicators
- ❌ symbols indicate failures
- "ERROR" or "FAILED" in section headers
- Exception tracebacks

### Security Events
- IP mismatch warnings
- Invalid state parameter errors
- Missing user ID errors

## Advanced Debugging

### 1. Enable Detailed HTTP Logging

For even more detailed HTTP request/response logging, you can temporarily modify the log level for httpx:

```python
import logging
logging.getLogger("httpx").setLevel(logging.DEBUG)
```

### 2. Database Query Logging

To see database queries, enable SQLAlchemy logging:

```python
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

### 3. Custom Debug Points

You can add temporary debug logging at any point:

```python
logger.info(f"DEBUG: Variable value = {variable}")
logger.info(f"DEBUG: Object state = {obj.__dict__}")
```

## Common Issues and Solutions

### Issue: No logs appearing
**Solution:** Check log level is set to INFO or DEBUG

### Issue: Logs are too verbose
**Solution:** Set log level to WARNING for production

### Issue: Missing OAuth credentials
**Solution:** Verify .env file has SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET

### Issue: Database connection errors
**Solution:** Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY

### Issue: Invalid OAuth code
**Solution:** Check if the OAuth URL generation and callback URL match

## Getting Help

If you're still having issues after reviewing the logs:

1. **Capture the full log output** from the OAuth flow
2. **Identify the exact section** where the failure occurs
3. **Note any error codes** or HTTP status codes
4. **Check the parameter values** being logged
5. **Verify your environment configuration**

The enhanced logging should provide enough detail to identify exactly where and why the OAuth token exchange is failing.