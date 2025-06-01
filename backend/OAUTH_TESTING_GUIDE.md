# Shopify OAuth Testing Guide

This guide provides step-by-step instructions to test the complete Shopify OAuth flow with fresh authorization codes.

## Overview

The OAuth flow consists of:
1. **Authorization URL Generation** - Create a URL to redirect users to Shopify for authorization
2. **User Authorization** - User visits the URL and grants permissions
3. **Callback Handling** - Shopify redirects back with an authorization code
4. **Token Exchange** - Exchange the code for an access token
5. **API Access** - Use the access token to make authenticated API calls

## Prerequisites

- Shopify Partner account with a public app created
- App configured with proper scopes and redirect URI
- Shopify client ID and secret in your `.env` file
- A test Shopify store (bizpredict.myshopify.com)

## Step 1: Generate OAuth Authorization URL

Run the OAuth URL generator:

```bash
python generate_oauth_url.py bizpredict.myshopify.com
```

This will output:
- Shop domain
- Client ID
- Required scopes
- Redirect URI
- State parameter
- **Complete OAuth URL**

## Step 2: Authorize the App

1. **Copy the OAuth URL** from the output above
2. **Open the URL in your browser**
3. **Log in to your Shopify store** if prompted
4. **Review the permissions** your app is requesting
5. **Click "Install app"** to authorize

## Step 3: Handle the Callback

After authorization, Shopify will redirect you to:
```
http://localhost:8000/api/v1/shopify/oauth/callback?shop=bizpredict.myshopify.com&code=FRESH_CODE_HERE&state=test_user:127.0.0.1&hmac=...&timestamp=...
```

**Copy the entire callback URL** from your browser's address bar.

## Step 4: Exchange Code for Access Token

Use the callback testing script:

```bash
python test_oauth_callback.py "PASTE_FULL_CALLBACK_URL_HERE"
```

Or if you just have the code:

```bash
python test_oauth_callback.py YOUR_FRESH_CODE bizpredict.myshopify.com
```

This will:
- Parse the callback parameters
- Exchange the authorization code for an access token
- Display the access token and scope
- Confirm successful OAuth completion

## Step 5: Test API Access (Optional)

Once you have an access token, you can test API calls:

```bash
curl -X GET \
  https://bizpredict.myshopify.com/admin/api/2024-07/products.json \
  -H 'X-Shopify-Access-Token: YOUR_ACCESS_TOKEN'
```

## Troubleshooting

### Common Issues

1. **"Invalid OAuth code"**
   - OAuth codes can only be used once
   - Generate a fresh OAuth URL and repeat the process

2. **"App not found"**
   - Verify your Shopify client ID is correct
   - Ensure your app is properly configured in the Partner Dashboard

3. **"Scope mismatch"**
   - Check that your app's configured scopes match the requested scopes

4. **"Redirect URI mismatch"**
   - Ensure your app's redirect URI matches exactly: `http://localhost:8000/api/v1/shopify/oauth/callback`

### Server Issues

If the FastAPI server endpoints are not working:

1. **Use the standalone scripts** (recommended for testing)
2. **Check server logs** for specific error messages
3. **Verify environment variables** are loaded correctly
4. **Restart the server** if needed

## Security Notes

- **State Parameter**: Always verify the state parameter matches what you sent
- **HMAC Verification**: In production, verify the HMAC signature
- **HTTPS**: Use HTTPS in production environments
- **Token Storage**: Store access tokens securely

## Files Created

- `generate_oauth_url.py` - Standalone OAuth URL generator
- `test_oauth_callback.py` - Callback handler and token exchange
- `OAUTH_TESTING_GUIDE.md` - This guide

## Next Steps

After successful OAuth testing:

1. **Fix the FastAPI server issues** (if needed)
2. **Implement proper callback handling** in your web application
3. **Add HMAC verification** for security
4. **Store access tokens** in your database
5. **Implement token refresh** logic
6. **Add error handling** for production use

## Example Complete Flow

```bash
# Step 1: Generate OAuth URL
python generate_oauth_url.py bizpredict.myshopify.com

# Step 2: Visit the OAuth URL in browser and authorize

# Step 3: Copy the callback URL from browser

# Step 4: Exchange code for token
python test_oauth_callback.py "http://localhost:8000/api/v1/shopify/oauth/callback?shop=bizpredict.myshopify.com&code=abc123&state=test_user:127.0.0.1"

# Step 5: Use the access token for API calls
curl -X GET https://bizpredict.myshopify.com/admin/api/2024-07/shop.json -H 'X-Shopify-Access-Token: YOUR_TOKEN'
```

This approach bypasses any server issues and provides a reliable way to test the OAuth flow with fresh credentials.