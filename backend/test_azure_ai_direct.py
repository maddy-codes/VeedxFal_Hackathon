#!/usr/bin/env python3
"""
Direct test of Azure AI service without authentication.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.azure_ai_service import AzureAIService
from app.services.trend_analysis_service import TrendAnalysisService

async def test_azure_ai_service():
    """Test Azure AI service directly."""
    print("=" * 60)
    print("AZURE AI SERVICE DIRECT TEST")
    print("=" * 60)
    
    try:
        # Initialize services
        ai_service = AzureAIService()
        trend_service = TrendAnalysisService()
        
        print("✅ Services initialized successfully")
        
        # Test Azure AI health check
        print("\nTesting Azure AI health check...")
        health = await ai_service.health_check()
        print(f"Health Status: {health}")
        
        # Test business data gathering
        print("\nTesting business data gathering...")
        business_data = await ai_service.get_business_data(shop_id=1)
        print(f"Business Data Keys: {list(business_data.keys())}")
        print(f"Store Name: {business_data.get('store_name')}")
        print(f"Total Products: {business_data.get('total_products')}")
        
        # Test trend summary (mock data)
        print("\nTesting trend summary...")
        trend_summary = {
            "shop_id": 1,
            "total_products": 50,
            "summary": {
                "Hot": 12,
                "Rising": 18,
                "Steady": 15,
                "Declining": 5
            },
            "percentages": {
                "Hot": 24.0,
                "Rising": 36.0,
                "Steady": 30.0,
                "Declining": 10.0
            },
            "average_scores": {
                "google_trend_index": 72.3,
                "social_score": 68.7,
                "final_score": 70.5
            }
        }
        
        # Test business summary generation
        print("\nTesting business summary generation...")
        summary = await ai_service.generate_business_summary(
            shop_id=1,
            business_data=business_data,
            trend_summary=trend_summary
        )
        
        print("✅ Business summary generated successfully!")
        print(f"Summary Keys: {list(summary.keys())}")
        print(f"Executive Summary: {summary.get('executive_summary', '')[:100]}...")
        print(f"Key Insights Count: {len(summary.get('key_insights', []))}")
        print(f"AI Provider: {summary.get('ai_provider')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_trend_analysis_service():
    """Test trend analysis service directly."""
    print("\n" + "=" * 60)
    print("TREND ANALYSIS SERVICE DIRECT TEST")
    print("=" * 60)
    
    try:
        # Initialize service
        trend_service = TrendAnalysisService()
        print("✅ Trend service initialized successfully")
        
        # Test health check
        print("\nTesting trend service health check...")
        health = await trend_service.health_check()
        print(f"Health Status: {health}")
        
        # Test trend insights (should return mock data)
        print("\nTesting trend insights...")
        insights = await trend_service.get_trend_insights(
            shop_id=1,
            max_age_hours=24
        )
        print(f"Insights Count: {len(insights)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all direct tests."""
    results = []
    
    # Test Azure AI service
    results.append(await test_azure_ai_service())
    
    # Test trend analysis service
    results.append(await test_trend_analysis_service())
    
    print("\n" + "=" * 60)
    print("DIRECT TEST SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("✅ All direct tests passed!")
    else:
        print("❌ Some direct tests failed.")
        
    print(f"Passed: {sum(results)}/{len(results)}")

if __name__ == "__main__":
    asyncio.run(main())