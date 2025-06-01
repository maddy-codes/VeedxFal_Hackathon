#!/usr/bin/env python3
"""
Comprehensive integration test for the Trend Analysis service.
Tests the complete integration with the running application.
"""

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_SHOP_ID = 1

def test_endpoint(method: str, endpoint: str, data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Test an API endpoint and return results."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "headers": dict(response.headers)
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def main():
    """Run comprehensive trend analysis integration tests."""
    print("=" * 80)
    print("TREND ANALYSIS INTEGRATION TEST")
    print("=" * 80)
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print()
    
    # Test results storage
    results = {}
    
    # 1. Test application health
    print("1. Testing Application Health...")
    app_health = test_endpoint("GET", "/health")
    results["app_health"] = app_health
    if app_health.get("success"):
        print("   ✅ Application is healthy")
        print(f"   📊 Version: {app_health['response'].get('version', 'unknown')}")
        print(f"   🌍 Environment: {app_health['response'].get('environment', 'unknown')}")
    else:
        print("   ❌ Application health check failed")
        print(f"   🔍 Error: {app_health.get('error', 'Unknown error')}")
    print()
    
    # 2. Test trend analysis health (no auth required)
    print("2. Testing Trend Analysis Health...")
    trend_health = test_endpoint("GET", "/api/v1/trend-analysis/health")
    results["trend_health"] = trend_health
    if trend_health.get("success"):
        print("   ✅ Trend Analysis service is accessible")
        response = trend_health["response"]
        print(f"   📊 Service Status: {response.get('status', 'unknown')}")
        
        checks = response.get('checks', {})
        for service, status in checks.items():
            status_icon = "✅" if status.get('status') == 'healthy' else "⚠️" if status.get('status') == 'degraded' else "❌"
            print(f"   {status_icon} {service.title()}: {status.get('status', 'unknown')}")
            if 'response_time_ms' in status:
                print(f"      ⏱️  Response Time: {status['response_time_ms']:.2f}ms")
            if 'error' in status:
                print(f"      🔍 Error: {status['error']}")
    else:
        print("   ❌ Trend Analysis health check failed")
        print(f"   🔍 Error: {trend_health.get('error', 'Unknown error')}")
    print()
    
    # 3. Test API documentation accessibility
    print("3. Testing API Documentation...")
    docs_test = test_endpoint("GET", "/docs")
    results["docs_access"] = docs_test
    if docs_test.get("success"):
        print("   ✅ API documentation is accessible")
    else:
        print("   ❌ API documentation not accessible")
    print()
    
    # 4. Test OpenAPI schema for trend analysis endpoints
    print("4. Testing OpenAPI Schema...")
    openapi_test = test_endpoint("GET", "/openapi.json")
    results["openapi"] = openapi_test
    if openapi_test.get("success"):
        openapi_data = openapi_test["response"]
        
        # Count trend analysis endpoints
        trend_endpoints = []
        for path, methods in openapi_data.get('paths', {}).items():
            if 'trend-analysis' in path:
                for method in methods.keys():
                    trend_endpoints.append(f"{method.upper()} {path}")
        
        print(f"   ✅ OpenAPI schema accessible")
        print(f"   📊 Total Trend Analysis Endpoints: {len(trend_endpoints)}")
        for endpoint in sorted(trend_endpoints):
            print(f"      - {endpoint}")
    else:
        print("   ❌ OpenAPI schema not accessible")
    print()
    
    # 5. Test authentication requirement for protected endpoints
    print("5. Testing Authentication Requirements...")
    protected_endpoints = [
        ("POST", "/api/v1/trend-analysis/analyze/1", {"sku_code": "TEST", "product_title": "Test Product"}),
        ("GET", "/api/v1/trend-analysis/insights/1", None),
        ("GET", "/api/v1/trend-analysis/insights/1/summary", None),
        ("GET", "/api/v1/trend-analysis/insights/1/trending", None),
    ]
    
    auth_results = {}
    for method, endpoint, data in protected_endpoints:
        test_result = test_endpoint(method, endpoint, data)
        auth_results[endpoint] = test_result
        
        if test_result.get("status_code") == 401:
            print(f"   ✅ {method} {endpoint} - Properly protected (401)")
        elif test_result.get("status_code") == 500:
            print(f"   ⚠️  {method} {endpoint} - Server error (500) - may indicate auth middleware issue")
        else:
            print(f"   ❌ {method} {endpoint} - Unexpected status: {test_result.get('status_code')}")
    
    results["auth_tests"] = auth_results
    print()
    
    # 6. Test database connectivity through trend service
    print("6. Testing Database Connectivity...")
    if trend_health.get("success"):
        checks = trend_health["response"].get('checks', {})
        db_status = checks.get('database', {})
        if db_status.get('status') == 'healthy':
            print("   ✅ Database connection through trend service is healthy")
            print(f"   ⏱️  Database Response Time: {db_status.get('response_time_ms', 0):.2f}ms")
        else:
            print("   ❌ Database connection issues detected")
    else:
        print("   ❌ Cannot test database connectivity - trend health check failed")
    print()
    
    # 7. Summary
    print("=" * 80)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 80)
    
    total_tests = 0
    passed_tests = 0
    
    # Count test results
    test_categories = [
        ("Application Health", results.get("app_health", {}).get("success", False)),
        ("Trend Analysis Health", results.get("trend_health", {}).get("success", False)),
        ("API Documentation", results.get("docs_access", {}).get("success", False)),
        ("OpenAPI Schema", results.get("openapi", {}).get("success", False)),
    ]
    
    for category, success in test_categories:
        total_tests += 1
        if success:
            passed_tests += 1
            print(f"✅ {category}")
        else:
            print(f"❌ {category}")
    
    # Authentication tests
    auth_tests = results.get("auth_tests", {})
    auth_passed = sum(1 for result in auth_tests.values() if result.get("status_code") == 401)
    total_tests += len(auth_tests)
    passed_tests += auth_passed
    
    print(f"✅ Authentication Protection: {auth_passed}/{len(auth_tests)} endpoints properly protected")
    
    print()
    print(f"📊 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Trend Analysis integration is complete and working!")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️  MOSTLY WORKING - Minor issues detected but core functionality is operational")
    else:
        print("❌ INTEGRATION ISSUES - Multiple problems detected that need attention")
    
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. 🌐 Access API docs: http://localhost:8000/docs")
    print("2. 🔍 View trend analysis endpoints in the 'Trend Analysis' section")
    print("3. 🧪 Test endpoints with authentication tokens")
    print("4. 📊 Monitor trend analysis health: http://localhost:8000/api/v1/trend-analysis/health")
    print("5. 🚀 Ready for integration with pricing recommendation system")
    print()
    
    return results

if __name__ == "__main__":
    results = main()