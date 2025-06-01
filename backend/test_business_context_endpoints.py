#!/usr/bin/env python3
"""
Test script to verify business context endpoints are working.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
SHOP_ID = 1
TOKEN = "test-token"  # Mock token for testing

def test_business_context_endpoint():
    """Test the regular business context endpoint."""
    print("Testing business context endpoint...")
    
    url = f"{BASE_URL}/api/v1/trend-analysis/business-context/{SHOP_ID}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Business context endpoint working!")
            print(f"Shop ID: {data.get('shop_id')}")
            print(f"Business Summary Keys: {list(data.get('business_summary', {}).keys())}")
            print(f"Business Data: {data.get('business_data', {})}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_business_context_stream_endpoint():
    """Test the streaming business context endpoint."""
    print("\nTesting business context streaming endpoint...")
    
    url = f"{BASE_URL}/api/v1/trend-analysis/business-context-stream/{SHOP_ID}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "text/event-stream"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Streaming endpoint accessible!")
            
            # Read first few chunks
            chunk_count = 0
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        print(f"Chunk {chunk_count}: {data.get('type', 'unknown')} - {data.get('message', '')[:50]}...")
                        chunk_count += 1
                        
                        if data.get('type') == 'complete':
                            print("✅ Streaming completed successfully!")
                            return True
                        elif data.get('type') == 'error':
                            print(f"❌ Streaming error: {data.get('message')}")
                            return False
                            
                        if chunk_count >= 10:  # Limit for testing
                            print("✅ Streaming working (stopped after 10 chunks)")
                            return True
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Failed to parse chunk: {e}")
                        
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_trend_summary_endpoint():
    """Test the trend summary endpoint."""
    print("\nTesting trend summary endpoint...")
    
    url = f"{BASE_URL}/api/v1/trend-analysis/insights/{SHOP_ID}/summary"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Trend summary endpoint working!")
            print(f"Total Products: {data.get('total_products')}")
            print(f"Summary: {data.get('summary', {})}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_server_health():
    """Test if the server is running."""
    print("Testing server health...")
    
    url = f"{BASE_URL}/api/v1/trend-analysis/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running!")
            print(f"Health Status: {data}")
            return True
        else:
            print(f"❌ Server error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("BUSINESS CONTEXT ENDPOINTS TEST")
    print("=" * 60)
    
    # Test server health first
    if not test_server_health():
        print("\n❌ Server is not running. Please start the backend server first.")
        print("Run: cd backend && python main.py")
        return
    
    # Test endpoints
    results = []
    results.append(test_trend_summary_endpoint())
    results.append(test_business_context_endpoint())
    results.append(test_business_context_stream_endpoint())
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("✅ All tests passed! Business context endpoints are working.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        
    print(f"Passed: {sum(results)}/{len(results)}")

if __name__ == "__main__":
    main()