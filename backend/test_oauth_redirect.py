#!/usr/bin/env python3
"""
Test script to verify OAuth callback redirect functionality.
"""

import asyncio
import sys
import os
import requests
from urllib.parse import urlencode

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_oauth_callback_redirect():
    """Test OAuth callback redirect functionality."""
    
    print("=== Testing OAuth Callback Redirect ===")
    
    # Test parameters that would come from Shopify
    test_params = {
        'shop': 'bizpredict.myshopify.com',
        'code': 'test_oauth_code_12345',
        'state': 'test_user:127.0.0.1',
        'hmac': 'test_hmac',
        'timestamp': '1234567890'
    }
    
    # Build the callback URL
    base_url = "http://localhost:8000/api/v1/shopify/oauth/callback"
    callback_url = f"{base_url}?{urlencode(test_params)}"
    
    print(f"Testing callback URL: {callback_url}")
    
    try:
        # Make request to callback endpoint (don't follow redirects)
        response = requests.get(callback_url, allow_redirects=False)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            print(f"✓ Redirect successful!")
            print(f"✓ Redirect URL: {redirect_url}")
            
            # Check if redirect URL contains expected parameters
            if 'localhost:3000/dashboard/shopify' in redirect_url:
                print("✓ Redirects to correct frontend dashboard")
                
                if 'success=' in redirect_url:
                    if 'success=true' in redirect_url:
                        print("✓ Success parameter detected")
                        if 'shop=' in redirect_url and 'store_id=' in redirect_url:
                            print("✓ Shop and store_id parameters included")
                        else:
                            print("⚠ Missing shop or store_id parameters")
                    else:
                        print("⚠ Error case - success=false detected")
                        if 'error=' in redirect_url:
                            print("✓ Error parameter included")
                else:
                    print("⚠ Missing success parameter")
            else:
                print("✗ Incorrect redirect destination")
        else:
            print(f"✗ Expected 302 redirect, got {response.status_code}")
            print(f"Response body: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to backend server")
        print("Make sure the backend server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False
    
    return True

def test_oauth_error_cases():
    """Test OAuth callback error handling."""
    
    print("\n=== Testing OAuth Error Cases ===")
    
    # Test case 1: Missing shop parameter
    print("\n1. Testing missing shop parameter...")
    test_params = {
        'code': 'test_oauth_code_12345',
        'state': 'test_user:127.0.0.1'
    }
    
    base_url = "http://localhost:8000/api/v1/shopify/oauth/callback"
    callback_url = f"{base_url}?{urlencode(test_params)}"
    
    try:
        response = requests.get(callback_url, allow_redirects=False)
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            if 'success=false' in redirect_url and 'error=' in redirect_url:
                print("✓ Error case handled correctly")
            else:
                print("⚠ Error case not handled properly")
        else:
            print(f"⚠ Expected redirect, got {response.status_code}")
    except Exception as e:
        print(f"✗ Error test failed: {e}")
    
    # Test case 2: Missing code parameter
    print("\n2. Testing missing code parameter...")
    test_params = {
        'shop': 'bizpredict.myshopify.com',
        'state': 'test_user:127.0.0.1'
    }
    
    callback_url = f"{base_url}?{urlencode(test_params)}"
    
    try:
        response = requests.get(callback_url, allow_redirects=False)
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            if 'success=false' in redirect_url and 'error=' in redirect_url:
                print("✓ Error case handled correctly")
            else:
                print("⚠ Error case not handled properly")
        else:
            print(f"⚠ Expected redirect, got {response.status_code}")
    except Exception as e:
        print(f"✗ Error test failed: {e}")

if __name__ == "__main__":
    print("OAuth Callback Redirect Test")
    print("=" * 50)
    
    # Test the redirect functionality
    success = test_oauth_callback_redirect()
    
    # Test error cases
    test_oauth_error_cases()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ OAuth callback redirect tests completed")
    else:
        print("✗ Some tests failed")
    
    print("\nTo test with a real OAuth flow:")
    print("1. Start the backend server: python main.py")
    print("2. Generate an OAuth URL: python generate_oauth_url.py")
    print("3. Visit the OAuth URL in your browser")
    print("4. After authorization, you should be redirected to the frontend dashboard")