#!/usr/bin/env python3
"""
Create mock trend data for demo purposes
"""

import asyncio
import random
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.product import Product
from app.models.analytics import TrendAnalysis
from sqlalchemy.orm import Session

# Mock product data
MOCK_PRODUCTS = [
    {
        "sku_code": "DEMO-001",
        "product_title": "Wireless Bluetooth Headphones",
        "product_description": "Premium noise-cancelling wireless headphones with 30-hour battery life",
        "price": 199.99,
        "category": "Electronics",
        "brand": "TechPro",
        "shop_id": 1
    },
    {
        "sku_code": "DEMO-002", 
        "product_title": "Smart Fitness Tracker",
        "product_description": "Advanced fitness tracker with heart rate monitoring and GPS",
        "price": 149.99,
        "category": "Fitness",
        "brand": "FitTech",
        "shop_id": 1
    },
    {
        "sku_code": "DEMO-003",
        "product_title": "Organic Coffee Beans",
        "product_description": "Premium organic coffee beans from sustainable farms",
        "price": 24.99,
        "category": "Food & Beverage",
        "brand": "GreenBean",
        "shop_id": 1
    },
    {
        "sku_code": "DEMO-004",
        "product_title": "Yoga Mat Premium",
        "product_description": "Non-slip eco-friendly yoga mat with alignment guides",
        "price": 79.99,
        "category": "Fitness",
        "brand": "ZenFit",
        "shop_id": 1
    },
    {
        "sku_code": "DEMO-005",
        "product_title": "Smart Home Speaker",
        "product_description": "Voice-controlled smart speaker with premium sound quality",
        "price": 129.99,
        "category": "Electronics",
        "brand": "SmartHome",
        "shop_id": 1
    },
    {
        "sku_code": "DEMO-006",
        "product_title": "Skincare Serum Set",
        "product_description": "Anti-aging serum set with vitamin C and hyaluronic acid",
        "price": 89.99,
        "category": "Beauty",
        "brand": "GlowSkin",
        "shop_id": 1
    },
    {
        "sku_code": "DEMO-007",
        "product_title": "Gaming Mechanical Keyboard",
        "product_description": "RGB backlit mechanical keyboard for gaming enthusiasts",
        "price": 159.99,
        "category": "Electronics",
        "brand": "GamePro",
        "shop_id": 1
    },
    {
        "sku_code": "DEMO-008",
        "product_title": "Protein Powder Vanilla",
        "product_description": "Whey protein powder with natural vanilla flavor",
        "price": 49.99,
        "category": "Fitness",
        "brand": "ProteinMax",
        "shop_id": 1
    }
]

def generate_trend_label():
    """Generate random trend label based on weights"""
    labels = ["Hot", "Rising", "Steady", "Declining"]
    weights = [0.2, 0.3, 0.4, 0.1]  # Hot: 20%, Rising: 30%, Steady: 40%, Declining: 10%
    return random.choices(labels, weights=weights)[0]

def generate_trend_scores(label):
    """Generate realistic trend scores based on label"""
    if label == "Hot":
        google_trend = random.uniform(80, 100)
        social_score = random.uniform(85, 100)
        final_score = random.uniform(85, 100)
    elif label == "Rising":
        google_trend = random.uniform(60, 85)
        social_score = random.uniform(65, 90)
        final_score = random.uniform(65, 85)
    elif label == "Steady":
        google_trend = random.uniform(40, 70)
        social_score = random.uniform(45, 75)
        final_score = random.uniform(45, 70)
    else:  # Declining
        google_trend = random.uniform(10, 45)
        social_score = random.uniform(15, 50)
        final_score = random.uniform(15, 45)
    
    return google_trend, social_score, final_score

async def create_mock_data():
    """Create mock products and trend data"""
    print("🚀 Creating mock trend data for demo...")
    
    # Get database session
    db: Session = SessionLocal()
    
    try:
        # Clear existing demo data
        print("🧹 Clearing existing demo data...")
        db.query(TrendAnalysis).filter(TrendAnalysis.sku_code.like("DEMO-%")).delete()
        db.query(Product).filter(Product.sku_code.like("DEMO-%")).delete()
        db.commit()
        
        # Create mock products
        print("📦 Creating mock products...")
        for product_data in MOCK_PRODUCTS:
            product = Product(**product_data)
            db.add(product)
        
        db.commit()
        print(f"✅ Created {len(MOCK_PRODUCTS)} mock products")
        
        # Create trend analysis data for each product
        print("📊 Creating trend analysis data...")
        created_count = 0
        
        for product_data in MOCK_PRODUCTS:
            sku_code = product_data["sku_code"]
            label = generate_trend_label()
            google_trend, social_score, final_score = generate_trend_scores(label)
            
            # Create trend analysis record
            trend_analysis = TrendAnalysis(
                sku_code=sku_code,
                shop_id=1,
                google_trend_index=google_trend,
                social_score=social_score,
                final_score=final_score,
                label=label,
                analysis_data={
                    "google_trends": {
                        "interest_over_time": [
                            {"date": (datetime.now() - timedelta(days=i)).isoformat(), 
                             "value": max(0, google_trend + random.uniform(-10, 10))}
                            for i in range(30, 0, -1)
                        ],
                        "related_queries": [
                            f"{product_data['product_title'].lower()} review",
                            f"best {product_data['category'].lower()}",
                            f"{product_data['brand'].lower()} products"
                        ]
                    },
                    "social_media": {
                        "mentions": random.randint(50, 500),
                        "sentiment": "positive" if social_score > 60 else "neutral",
                        "engagement_rate": social_score / 100
                    },
                    "market_analysis": {
                        "competition_level": "medium" if final_score > 50 else "high",
                        "price_competitiveness": random.uniform(0.7, 1.3),
                        "demand_forecast": label.lower()
                    }
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(trend_analysis)
            created_count += 1
        
        db.commit()
        print(f"✅ Created {created_count} trend analysis records")
        
        # Print summary
        print("\n📈 TREND ANALYSIS SUMMARY:")
        trend_counts = db.query(TrendAnalysis.label, db.func.count(TrendAnalysis.id)).filter(
            TrendAnalysis.sku_code.like("DEMO-%")
        ).group_by(TrendAnalysis.label).all()
        
        for label, count in trend_counts:
            print(f"   🔥 {label}: {count} products")
        
        print(f"\n🎉 Mock trend data created successfully!")
        print(f"📊 Total products: {len(MOCK_PRODUCTS)}")
        print(f"📈 Total trend analyses: {created_count}")
        print(f"\n🚀 Ready for demo! Login with: jatinarora2689@gmail.com / Jazz@1552")
        
    except Exception as e:
        print(f"❌ Error creating mock data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_mock_data())