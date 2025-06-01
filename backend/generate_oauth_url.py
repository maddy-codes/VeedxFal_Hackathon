#!/usr/bin/env python3
"""
Standalone OAuth URL generator for Shopify integration testing.
This bypasses any server issues and generates a working OAuth URL.
"""

import os
import sys
from urllib.parse import urlencode

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generate_shopify_oauth_url(shop_domain: str, redirect_uri: str = None):
    """Generate Shopify OAuth authorization URL."""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get Shopify credentials from environment
    client_id = os.getenv('SHOPIFY_CLIENT_ID')
    if not client_id:
        return {"error": "SHOPIFY_CLIENT_ID not found in environment variables"}
    
    # Default scopes
    scopes = ["read_products", "read_inventory", "read_orders", "read_price_rules"]
    
    # Generate state parameter for security
    state = f"test_user:127.0.0.1"
    
    # Set default redirect URI
    final_redirect_uri = redirect_uri or "http://localhost:8000/api/v1/shopify/oauth/callback"
    
    # Build OAuth parameters
    params = {
        "client_id": client_id,
        "scope": ",".join(scopes),
        "redirect_uri": final_redirect_uri,
        "state": state
    }
    
    # Generate OAuth URL
    oauth_url = f"https://{shop_domain}/admin/oauth/authorize?{urlencode(params)}"
    
    return {
        "oauth_url": oauth_url,
        "state": state,
        "shop_domain": shop_domain,
        "redirect_uri": final_redirect_uri,
        "client_id": client_id,
        "scopes": scopes
    }

def main():
    """Main function for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python generate_oauth_url.py <shop_domain> [redirect_uri]")
        print("Example: python generate_oauth_url.py bizpredict.myshopify.com")
        sys.exit(1)
    
    shop_domain = sys.argv[1]
    redirect_uri = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = generate_shopify_oauth_url(shop_domain, redirect_uri)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("SHOPIFY OAUTH AUTHORIZATION URL GENERATED")
    print("="*80)
    print(f"Shop Domain: {result['shop_domain']}")
    print(f"Client ID: {result['client_id']}")
    print(f"Scopes: {', '.join(result['scopes'])}")
    print(f"Redirect URI: {result['redirect_uri']}")
    print(f"State: {result['state']}")
    print("\nOAuth URL:")
    print(result['oauth_url'])
    print("\n" + "="*80)
    print("INSTRUCTIONS:")
    print("1. Copy the OAuth URL above")
    print("2. Open it in your browser")
    print("3. Log in to your Shopify store if needed")
    print("4. Click 'Install app' to authorize")
    print("5. You'll be redirected back with a fresh OAuth code")
    print("6. Use that code to test the callback endpoint")
    print("="*80)

if __name__ == "__main__":
    main()