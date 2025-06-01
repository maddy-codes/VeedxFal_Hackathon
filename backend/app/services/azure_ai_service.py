"""
Azure AI service for generating business context and summaries.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status
from openai import AzureOpenAI

from app.core.config import settings
from app.core.database import get_supabase_client
from app.core.logging import get_logger, log_external_api_call, log_error, LoggerMixin


logger = get_logger(__name__)


class AzureAIService(LoggerMixin):
    """Service for Azure AI integration and business context generation."""
    
    def __init__(self):
        """Initialize Azure AI service."""
        self.supabase_client = get_supabase_client()
        self.api_key = settings.AZURE_OPENAI_API_KEY
        self.endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.api_version = settings.AZURE_OPENAI_API_VERSION
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT
        
        # Initialize Azure OpenAI client
        self.azure_client = None
        if self._is_azure_configured():
            try:
                self.azure_client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version=self.api_version,
                )
                logger.info("Azure OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI client: {e}")
                self.azure_client = None
        else:
            logger.warning("Azure OpenAI not configured, will use fallback")
    
    async def generate_business_summary(
        self,
        shop_id: int,
        business_data: Dict[str, Any],
        trend_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate business context summary using Azure AI.
        
        Args:
            shop_id: Store ID
            business_data: Business information and metrics
            trend_summary: Current trend analysis summary
            
        Returns:
            Generated business summary with insights
        """
        self.logger.info(
            "Generating business summary with Azure AI",
            shop_id=shop_id,
            business_data_keys=list(business_data.keys()),
            trend_summary_keys=list(trend_summary.keys())
        )
        
        try:
            # Prepare business context prompt
            prompt = self._create_business_context_prompt(business_data, trend_summary)
            
            # Check if Azure AI is properly configured
            if not self.azure_client:
                logger.warning("Azure AI not configured, using mock summary")
                return self._generate_mock_business_summary(business_data, trend_summary)
            
            # Call Azure OpenAI API
            summary = await self._call_azure_openai(prompt)
            
            # Parse and structure the response
            structured_summary = self._parse_ai_response(summary)
            
            # Add metadata
            structured_summary.update({
                "generated_at": datetime.utcnow().isoformat(),
                "shop_id": shop_id,
                "ai_provider": "azure_cognitive_services",
                "model": self.deployment_name,
                "data_sources": {
                    "business_metrics": bool(business_data.get("metrics")),
                    "product_data": bool(business_data.get("products")),
                    "trend_analysis": bool(trend_summary.get("summary")),
                    "sales_data": bool(business_data.get("sales"))
                }
            })
            
            self.logger.info(
                "Business summary generated successfully",
                shop_id=shop_id,
                summary_length=len(structured_summary.get("summary", "")),
                insights_count=len(structured_summary.get("insights", []))
            )
            
            return structured_summary
            
        except Exception as e:
            log_error(e, {
                "shop_id": shop_id,
                "service": "azure_ai",
                "operation": "generate_business_summary"
            })
            
            # Fallback to mock summary on error
            logger.warning(f"Azure AI failed, using mock summary: {e}")
            return self._generate_mock_business_summary(business_data, trend_summary)
    
    async def generate_business_summary_stream(
        self,
        shop_id: int,
        business_data: Dict[str, Any],
        trend_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate business context summary using Azure AI with streaming support.
        
        Args:
            shop_id: Store ID
            business_data: Business information and metrics
            trend_summary: Current trend analysis summary
            
        Returns:
            Generated business summary with insights (same as non-streaming)
        """
        # For now, use the same method as non-streaming
        # The streaming is handled at the API level
        return await self.generate_business_summary(shop_id, business_data, trend_summary)
    
    async def _call_azure_openai(self, prompt: str) -> str:
        """
        Call Azure OpenAI API using the Azure OpenAI SDK.
        
        Args:
            prompt: The prompt to send to Azure OpenAI
            
        Returns:
            AI-generated response text
        """
        if not self.azure_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Azure OpenAI client not initialized"
            )
        
        request_start_time = datetime.utcnow()
        
        try:
            # Prepare messages for Azure OpenAI
            messages = [
                {
                    "role": "system",
                    "content": "You are a business intelligence AI assistant specializing in e-commerce analytics and market insights. Provide clear, actionable business summaries based on the data provided. Always respond with valid JSON in the exact format requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Make the API call using Azure OpenAI SDK
            completion = self.azure_client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_completion_tokens=1500,
                stop=None,
                stream=True
            )
            
            request_duration = (datetime.utcnow() - request_start_time).total_seconds()
            
            # Log the successful API call
            log_external_api_call(
                service="azure_openai",
                endpoint="chat/completions",
                method="POST",
                status_code=200,
                duration=request_duration,
                model=self.deployment_name
            )
            
            # Handle streaming response
            response_content = ""
            for chunk in completion:
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                    response_content += chunk.choices[0].delta.content
            
            logger.info(
                "Azure OpenAI API call successful",
                model=self.deployment_name,
                duration=request_duration,
                response_length=len(response_content) if response_content else 0
            )
            
            return response_content
            
        except Exception as e:
            request_duration = (datetime.utcnow() - request_start_time).total_seconds()
            
            # Log the failed API call
            log_external_api_call(
                service="azure_openai",
                endpoint="chat/completions",
                method="POST",
                status_code=None,
                duration=request_duration,
                error_message=str(e),
                model=self.deployment_name
            )
            
            logger.error(f"Azure OpenAI API error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Azure OpenAI API error: {str(e)}"
            )
    
    def _create_business_context_prompt(
        self,
        business_data: Dict[str, Any],
        trend_summary: Dict[str, Any]
    ) -> str:
        """Create a comprehensive prompt for business context generation."""
        
        prompt = f"""
Analyze the following e-commerce business data and provide a comprehensive business summary:

BUSINESS OVERVIEW:
- Store Name: {business_data.get('store_name', 'E-commerce Store')}
- Industry: {business_data.get('industry', 'Retail')}
- Total Products: {trend_summary.get('total_products', 'N/A')}
- Business Type: {business_data.get('business_type', 'Online Retail')}

CURRENT PERFORMANCE METRICS:
- Revenue (Last 30 days): ${business_data.get('revenue_30d', 0):,.2f}
- Orders (Last 30 days): {business_data.get('orders_30d', 0)}
- Average Order Value: ${business_data.get('avg_order_value', 0):.2f}
- Conversion Rate: {business_data.get('conversion_rate', 0):.1f}%
- Customer Acquisition Cost: ${business_data.get('cac', 0):.2f}

PRODUCT TREND ANALYSIS:
- Hot Products: {trend_summary.get('summary', {}).get('Hot', 0)} ({trend_summary.get('percentages', {}).get('Hot', 0):.1f}%)
- Rising Products: {trend_summary.get('summary', {}).get('Rising', 0)} ({trend_summary.get('percentages', {}).get('Rising', 0):.1f}%)
- Steady Products: {trend_summary.get('summary', {}).get('Steady', 0)} ({trend_summary.get('percentages', {}).get('Steady', 0):.1f}%)
- Declining Products: {trend_summary.get('summary', {}).get('Declining', 0)} ({trend_summary.get('percentages', {}).get('Declining', 0):.1f}%)

AVERAGE TREND SCORES:
- Google Trends Index: {trend_summary.get('average_scores', {}).get('google_trend_index', 0):.1f}/100
- Social Score: {trend_summary.get('average_scores', {}).get('social_score', 0):.1f}/100
- Overall Trend Score: {trend_summary.get('average_scores', {}).get('final_score', 0):.1f}/100

TOP PERFORMING CATEGORIES:
{self._format_category_data(business_data.get('top_categories', []))}

INVENTORY STATUS:
- Low Stock Items: {business_data.get('low_stock_count', 0)}
- Out of Stock Items: {business_data.get('out_of_stock_count', 0)}
- Overstocked Items: {business_data.get('overstocked_count', 0)}

Please provide a business summary in the following JSON format:
{{
    "executive_summary": "2-3 sentence overview of current business performance",
    "key_insights": [
        "Insight 1 about trends and performance",
        "Insight 2 about opportunities",
        "Insight 3 about challenges or risks"
    ],
    "performance_highlights": [
        "Positive metric or achievement",
        "Another strong performance area"
    ],
    "areas_for_improvement": [
        "Area that needs attention",
        "Another improvement opportunity"
    ],
    "strategic_recommendations": [
        "Actionable recommendation 1",
        "Actionable recommendation 2",
        "Actionable recommendation 3"
    ],
    "market_outlook": "Brief assessment of market trends and future outlook",
    "priority_actions": [
        "Immediate action item 1",
        "Immediate action item 2"
    ]
}}

Focus on actionable insights and specific recommendations based on the data provided.
"""
        return prompt
    
    def _format_category_data(self, categories: List[Dict[str, Any]]) -> str:
        """Format category data for the prompt."""
        if not categories:
            return "- No category data available"
        
        formatted = []
        for i, category in enumerate(categories[:5], 1):
            formatted.append(
                f"- {category.get('name', 'Unknown')}: "
                f"${category.get('revenue', 0):,.2f} revenue, "
                f"{category.get('products', 0)} products"
            )
        
        return "\n".join(formatted)
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract structured data."""
        try:
            # Try to extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                parsed = json.loads(json_str)
                return parsed
            else:
                # Fallback: create structure from plain text
                return {
                    "executive_summary": response[:200] + "..." if len(response) > 200 else response,
                    "key_insights": [response],
                    "performance_highlights": [],
                    "areas_for_improvement": [],
                    "strategic_recommendations": [],
                    "market_outlook": "",
                    "priority_actions": []
                }
                
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            return {
                "executive_summary": response[:200] + "..." if len(response) > 200 else response,
                "key_insights": [response],
                "performance_highlights": [],
                "areas_for_improvement": [],
                "strategic_recommendations": [],
                "market_outlook": "",
                "priority_actions": []
            }
    
    def _generate_mock_business_summary(
        self,
        business_data: Dict[str, Any],
        trend_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a mock business summary for development/fallback."""
        
        total_products = trend_summary.get('total_products', 50)
        hot_products = trend_summary.get('summary', {}).get('Hot', 12)
        rising_products = trend_summary.get('summary', {}).get('Rising', 18)
        declining_products = trend_summary.get('summary', {}).get('Declining', 5)
        
        revenue = business_data.get('revenue_30d', 45000)
        orders = business_data.get('orders_30d', 180)
        
        return {
            "executive_summary": f"Your store is performing well with {total_products} products analyzed. {hot_products} products are trending hot, indicating strong market demand. Revenue of ${revenue:,.2f} from {orders} orders shows healthy business activity.",
            "key_insights": [
                f"{hot_products + rising_products} products ({((hot_products + rising_products) / total_products * 100):.1f}%) are showing positive trends",
                f"Average trend score of {trend_summary.get('average_scores', {}).get('final_score', 70.5):.1f}/100 indicates good market positioning",
                f"Only {declining_products} products are declining, suggesting strong product portfolio"
            ],
            "performance_highlights": [
                f"{hot_products} products are trending hot with high market demand",
                f"Strong Google Trends performance with {trend_summary.get('average_scores', {}).get('google_trend_index', 72.3):.1f}/100 average score",
                f"Healthy revenue of ${revenue:,.2f} in the last 30 days"
            ],
            "areas_for_improvement": [
                f"Monitor {declining_products} declining products for potential price adjustments",
                "Consider expanding inventory for hot trending products",
                "Optimize marketing for rising trend products to capitalize on momentum"
            ],
            "strategic_recommendations": [
                "Increase inventory levels for hot trending products to meet demand",
                "Implement dynamic pricing for products with high trend scores",
                "Focus marketing budget on rising trend products to accelerate growth",
                "Consider discontinuing or heavily discounting consistently declining products"
            ],
            "market_outlook": "Market trends show positive momentum with strong consumer interest in your product categories. The high percentage of hot and rising products indicates good market timing and product selection.",
            "priority_actions": [
                "Review inventory levels for hot trending products immediately",
                "Set up automated alerts for trend score changes",
                "Plan promotional campaigns for rising trend products"
            ],
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "mock_summary",
            "model": "fallback",
            "data_sources": {
                "business_metrics": bool(business_data.get("metrics")),
                "product_data": bool(business_data.get("products")),
                "trend_analysis": bool(trend_summary.get("summary")),
                "sales_data": bool(business_data.get("sales"))
            }
        }
    
    def _is_azure_configured(self) -> bool:
        """Check if Azure AI is properly configured."""
        return (
            self.api_key and 
            self.api_key != "placeholder" and
            self.endpoint and 
            self.endpoint != "placeholder"
        )
    
    async def get_business_data(self, shop_id: int) -> Dict[str, Any]:
        """
        Gather comprehensive business data for AI analysis.
        
        Args:
            shop_id: Store ID
            
        Returns:
            Comprehensive business data dictionary
        """
        try:
            # Get store information
            store_query = self.supabase_client.table("stores").select("*").eq("id", shop_id)
            store_result = store_query.execute()
            store_data = store_result.data[0] if store_result.data else {}
            
            # Get product count and categories
            products_query = self.supabase_client.table("products").select(
                "sku_code, product_title, current_price, inventory_level, status"
            ).eq("shop_id", shop_id)
            products_result = products_query.execute()
            products = products_result.data
            
            # Calculate business metrics (mock data for MVP)
            business_data = {
                "store_name": store_data.get("store_name", "Your Store"),
                "industry": "E-commerce Retail",
                "business_type": "Online Store",
                "total_products": len(products),
                "active_products": len([p for p in products if p.get("status") == "active"]),
                
                # Mock financial metrics (would come from real data in production)
                "revenue_30d": 45000.00,
                "orders_30d": 180,
                "avg_order_value": 250.00,
                "conversion_rate": 3.2,
                "cac": 25.50,
                
                # Inventory metrics
                "low_stock_count": len([p for p in products if p.get("inventory_level", 0) < 10]),
                "out_of_stock_count": len([p for p in products if p.get("inventory_level", 0) == 0]),
                "overstocked_count": len([p for p in products if p.get("inventory_level", 0) > 100]),
                
                # Mock category data
                "top_categories": [
                    {"name": "Electronics", "revenue": 18000, "products": 15},
                    {"name": "Clothing", "revenue": 12000, "products": 20},
                    {"name": "Home & Garden", "revenue": 8000, "products": 10},
                    {"name": "Sports", "revenue": 7000, "products": 8}
                ],
                
                "products": products
            }
            
            return business_data
            
        except Exception as e:
            log_error(e, {
                "shop_id": shop_id,
                "service": "azure_ai",
                "operation": "get_business_data"
            })
            
            # Return minimal mock data on error
            return {
                "store_name": "Your Store",
                "industry": "E-commerce",
                "business_type": "Online Store",
                "total_products": 50,
                "revenue_30d": 45000.00,
                "orders_30d": 180,
                "avg_order_value": 250.00,
                "conversion_rate": 3.2,
                "top_categories": []
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for Azure AI service.
        
        Returns:
            Health check status and details
        """
        health_status = {
            "service": "azure_ai",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # Check configuration
        if self._is_azure_configured():
            health_status["checks"]["configuration"] = "configured"
        else:
            health_status["checks"]["configuration"] = "not_configured"
            health_status["status"] = "degraded"
        
        # Test API connectivity (if configured)
        if self.azure_client:
            try:
                test_prompt = "Hello, this is a test. Please respond with 'Test successful'."
                response = await self._call_azure_openai(test_prompt)
                if response and "test" in response.lower():
                    health_status["checks"]["api_connectivity"] = "connected"
                else:
                    health_status["checks"]["api_connectivity"] = "connected_but_unexpected_response"
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["checks"]["api_connectivity"] = f"failed: {str(e)}"
                health_status["status"] = "degraded"
        else:
            health_status["checks"]["api_connectivity"] = "skipped_not_configured"
        
        return health_status