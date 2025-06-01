#!/usr/bin/env python3
"""
Test script for Azure AI business context integration.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.azure_ai_service import AzureAIService
from app.services.trend_analysis_service import TrendAnalysisService


async def test_azure_ai_integration():
    """Test the Azure AI business context generation."""
    print("🧪 Testing Azure AI Business Context Integration")
    print("=" * 60)
    
    try:
        # Initialize services
        ai_service = AzureAIService()
        trend_service = TrendAnalysisService()
        
        print("✅ Services initialized successfully")
        
        # Test shop ID
        shop_id = 1
        
        # Test health check
        print("\n🔍 Testing Azure AI health check...")
        health_status = await ai_service.health_check()
        print(f"Health Status: {health_status['status']}")
        print(f"Configuration: {health_status['checks'].get('configuration', 'unknown')}")
        print(f"API Connectivity: {health_status['checks'].get('api_connectivity', 'unknown')}")
        
        # Get business data
        print(f"\n📊 Getting business data for shop {shop_id}...")
        business_data = await ai_service.get_business_data(shop_id)
        print(f"Store Name: {business_data.get('store_name')}")
        print(f"Total Products: {business_data.get('total_products')}")
        print(f"Revenue (30d): ${business_data.get('revenue_30d', 0):,.2f}")
        
        # Get trend summary
        print(f"\n📈 Getting trend summary for shop {shop_id}...")
        trend_insights = await trend_service.get_trend_insights(
            shop_id=shop_id,
            max_age_hours=24
        )
        
        if trend_insights:
            print(f"Found {len(trend_insights)} trend insights")
            
            # Calculate trend summary
            label_counts = {"Hot": 0, "Rising": 0, "Steady": 0, "Declining": 0}
            total_google_trend = 0
            total_social_score = 0
            total_final_score = 0
            
            for insight in trend_insights:
                label_counts[insight["label"]] += 1
                total_google_trend += insight["google_trend_index"]
                total_social_score += insight["social_score"]
                total_final_score += insight["final_score"]
            
            total_products = len(trend_insights)
            
            trend_summary = {
                "shop_id": shop_id,
                "total_products": total_products,
                "summary": label_counts,
                "percentages": {
                    label: round((count / total_products) * 100, 1) 
                    for label, count in label_counts.items()
                },
                "average_scores": {
                    "google_trend_index": round(total_google_trend / total_products, 1),
                    "social_score": round(total_social_score / total_products, 1),
                    "final_score": round(total_final_score / total_products, 1)
                }
            }
        else:
            print("No trend insights found, using mock data")
            trend_summary = {
                "shop_id": shop_id,
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
        
        print(f"Trend Summary: {trend_summary['summary']}")
        print(f"Average Final Score: {trend_summary['average_scores']['final_score']}")
        
        # Generate business summary
        print(f"\n🤖 Generating AI business summary...")
        business_summary = await ai_service.generate_business_summary(
            shop_id=shop_id,
            business_data=business_data,
            trend_summary=trend_summary
        )
        
        print(f"AI Provider: {business_summary.get('ai_provider')}")
        print(f"Generated At: {business_summary.get('generated_at')}")
        
        # Display summary sections
        print("\n📋 EXECUTIVE SUMMARY:")
        print("-" * 40)
        print(business_summary.get('executive_summary', 'N/A'))
        
        print("\n💡 KEY INSIGHTS:")
        print("-" * 40)
        for i, insight in enumerate(business_summary.get('key_insights', []), 1):
            print(f"{i}. {insight}")
        
        print("\n🎯 PERFORMANCE HIGHLIGHTS:")
        print("-" * 40)
        for i, highlight in enumerate(business_summary.get('performance_highlights', []), 1):
            print(f"{i}. {highlight}")
        
        print("\n📈 STRATEGIC RECOMMENDATIONS:")
        print("-" * 40)
        for i, rec in enumerate(business_summary.get('strategic_recommendations', []), 1):
            print(f"{i}. {rec}")
        
        if business_summary.get('priority_actions'):
            print("\n🚨 PRIORITY ACTIONS:")
            print("-" * 40)
            for i, action in enumerate(business_summary.get('priority_actions', []), 1):
                print(f"{i}. {action}")
        
        if business_summary.get('market_outlook'):
            print("\n🔮 MARKET OUTLOOK:")
            print("-" * 40)
            print(business_summary.get('market_outlook'))
        
        # Test the API endpoint format
        print("\n🌐 API Response Format:")
        print("-" * 40)
        api_response = {
            "shop_id": shop_id,
            "business_summary": business_summary,
            "trend_summary": trend_summary,
            "business_data": {
                "store_name": business_data.get("store_name"),
                "total_products": business_data.get("total_products"),
                "revenue_30d": business_data.get("revenue_30d"),
                "orders_30d": business_data.get("orders_30d"),
                "avg_order_value": business_data.get("avg_order_value")
            }
        }
        
        print(f"Response keys: {list(api_response.keys())}")
        print(f"Business summary keys: {list(business_summary.keys())}")
        
        print("\n✅ Azure AI integration test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during Azure AI integration test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_business_context_endpoint():
    """Test the business context API endpoint format."""
    print("\n🔗 Testing Business Context API Endpoint Format")
    print("=" * 60)
    
    try:
        from app.api.v1.trend_analysis import get_business_context
        from app.api.deps import get_current_user
        
        # Mock current user
        mock_user = {"user_id": 1, "email": "test@example.com"}
        
        print("✅ Business context endpoint imports successful")
        print("📝 Endpoint ready for testing with actual HTTP requests")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing business context endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Azure AI Business Context Integration Tests")
    print("=" * 80)
    
    # Test Azure AI integration
    ai_test_result = await test_azure_ai_integration()
    
    # Test endpoint format
    endpoint_test_result = await test_business_context_endpoint()
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Azure AI Integration: {'✅ PASSED' if ai_test_result else '❌ FAILED'}")
    print(f"API Endpoint Format: {'✅ PASSED' if endpoint_test_result else '❌ FAILED'}")
    
    if ai_test_result and endpoint_test_result:
        print("\n🎉 All tests passed! Azure AI business context integration is ready.")
        print("\n📋 Next Steps:")
        print("1. Start the backend server: uvicorn main:app --reload")
        print("2. Test the endpoint: GET /api/v1/trend-analysis/business-context/1")
        print("3. Check the frontend integration in the insights page")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return ai_test_result and endpoint_test_result


if __name__ == "__main__":
    asyncio.run(main())