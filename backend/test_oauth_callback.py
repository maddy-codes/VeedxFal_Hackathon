#!/usr/bin/env python3
"""
Test script to handle OAuth callback and exchange code for access token.
"""

import os
import sys
import json
import httpx
from urllib.parse import parse_qs, urlparse

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def exchange_oauth_code(shop_domain: str, code: str):
    """Exchange OAuth authorization code for access token."""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('SHOPIFY_CLIENT_ID')
    client_secret = os.getenv('SHOPIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        return {"error": "Shopify credentials not found in environment variables"}
    
    # Prepare token exchange request
    token_url = f"https://{shop_domain}/admin/oauth/access_token"
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"Exchanging OAuth code for access token...")
            print(f"Token URL: {token_url}")
            print(f"Shop Domain: {shop_domain}")
            print(f"Code: {code}")
            
            response = await client.post(token_url, json=token_data)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                token_response = response.json()
                print(f"Token Response: {json.dumps(token_response, indent=2)}")
                
                return {
                    "success": True,
                    "access_token": token_response.get("access_token"),
                    "scope": token_response.get("scope"),
                    "shop_domain": shop_domain,
                    "message": "OAuth token exchange successful!"
                }
            else:
                error_text = response.text
                print(f"Error Response: {error_text}")
                return {
                    "error": f"Token exchange failed with status {response.status_code}: {error_text}"
                }
                
        except Exception as e:
            print(f"Exception during token exchange: {e}")
            return {"error": f"Token exchange failed: {str(e)}"}

def parse_callback_url(callback_url: str):
    """Parse callback URL to extract parameters."""
    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)
    
    return {
        "shop": params.get('shop', [None])[0],
        "code": params.get('code', [None])[0],
        "state": params.get('state', [None])[0],
        "hmac": params.get('hmac', [None])[0],
        "timestamp": params.get('timestamp', [None])[0]
    }

async def main():
    """Main function for testing OAuth callback."""
    if len(sys.argv) < 2:
        print("Usage: python test_oauth_callback.py <callback_url_or_code> [shop_domain]")
        print("Example 1: python test_oauth_callback.py 'http://localhost:8000/api/v1/shopify/oauth/callback?shop=bizpredict.myshopify.com&code=abc123&state=test_user:127.0.0.1'")
        print("Example 2: python test_oauth_callback.py abc123 bizpredict.myshopify.com")
        sys.exit(1)
    
    input_param = sys.argv[1]
    
    # Check if input is a full callback URL or just a code
    if input_param.startswith('http'):
        # Parse callback URL
        params = parse_callback_url(input_param)
        shop_domain = params['shop']
        code = params['code']
        state = params['state']
        
        print("="*80)
        print("PARSING CALLBACK URL")
        print("="*80)
        print(f"Shop: {shop_domain}")
        print(f"Code: {code}")
        print(f"State: {state}")
        print(f"HMAC: {params['hmac']}")
        print(f"Timestamp: {params['timestamp']}")
        print()
        
    else:
        # Treat as code with shop domain
        code = input_param
        shop_domain = sys.argv[2] if len(sys.argv) > 2 else "bizpredict.myshopify.com"
        
        print("="*80)
        print("USING PROVIDED CODE AND SHOP DOMAIN")
        print("="*80)
        print(f"Shop: {shop_domain}")
        print(f"Code: {code}")
        print()
    
    if not code or not shop_domain:
        print("Error: Missing code or shop domain")
        sys.exit(1)
    
    # Exchange code for access token
    print("="*80)
    print("EXCHANGING OAUTH CODE FOR ACCESS TOKEN")
    print("="*80)
    
    result = await exchange_oauth_code(shop_domain, code)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    else:
        print("="*80)
        print("SUCCESS! OAUTH TOKEN EXCHANGE COMPLETED")
        print("="*80)
        print(f"Shop Domain: {result['shop_domain']}")
        print(f"Access Token: {result['access_token']}")
        print(f"Scope: {result['scope']}")
        print(f"Message: {result['message']}")
        print("="*80)
        print("You can now use this access token to make API calls to Shopify!")
        print("="*80)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())