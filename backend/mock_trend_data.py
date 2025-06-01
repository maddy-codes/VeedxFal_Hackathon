"""
Extensive mock trend data for demo purposes
"""

from datetime import datetime

def get_mock_trending_products():
    """Return extensive mock trending products data"""
    return [
        # HOT PRODUCTS (12 items)
        {
            "sku_code": "HOT-001",
            "product_title": "Wireless Bluetooth Headphones Pro",
            "current_price": 299.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 95.2,
                "social_score": 92.8,
                "final_score": 94.0,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-002",
            "product_title": "AI-Powered Yoga Mat with Sensors",
            "current_price": 249.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 91.2,
                "social_score": 87.6,
                "final_score": 89.4,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-003",
            "product_title": "Smart Coffee Maker with App Control",
            "current_price": 189.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 88.7,
                "social_score": 85.3,
                "final_score": 87.0,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-004",
            "product_title": "Portable Electric Scooter",
            "current_price": 599.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 86.4,
                "social_score": 89.1,
                "final_score": 87.8,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-005",
            "product_title": "Wireless Charging Desk Lamp",
            "current_price": 79.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 84.2,
                "social_score": 81.7,
                "final_score": 83.0,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-006",
            "product_title": "Smart Water Bottle with Hydration Tracking",
            "current_price": 49.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 82.8,
                "social_score": 86.4,
                "final_score": 84.6,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-007",
            "product_title": "Eco-Friendly Bamboo Phone Case",
            "current_price": 24.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 81.5,
                "social_score": 88.2,
                "final_score": 84.9,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-008",
            "product_title": "Gaming Chair with RGB Lighting",
            "current_price": 399.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 80.3,
                "social_score": 83.7,
                "final_score": 82.0,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-009",
            "product_title": "Smart Home Security Camera 4K",
            "current_price": 159.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 79.8,
                "social_score": 82.1,
                "final_score": 81.0,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-010",
            "product_title": "Wireless Earbuds with Noise Cancellation",
            "current_price": 129.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 78.9,
                "social_score": 84.2,
                "final_score": 81.6,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-011",
            "product_title": "Smart Fitness Mirror",
            "current_price": 1299.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 77.6,
                "social_score": 85.8,
                "final_score": 81.7,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "HOT-012",
            "product_title": "Portable Solar Power Bank",
            "current_price": 89.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 76.4,
                "social_score": 79.3,
                "final_score": 77.9,
                "label": "Hot",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        
        # RISING PRODUCTS (18 items)
        {
            "sku_code": "RISE-001",
            "product_title": "Smart Thermostat with Voice Control",
            "current_price": 199.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 74.8,
                "social_score": 71.2,
                "final_score": 73.0,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-002",
            "product_title": "Electric Bike Conversion Kit",
            "current_price": 449.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 73.5,
                "social_score": 69.8,
                "final_score": 71.7,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-003",
            "product_title": "Smart Garden Indoor Growing System",
            "current_price": 179.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 72.1,
                "social_score": 75.4,
                "final_score": 73.8,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-004",
            "product_title": "Wireless Mechanical Gaming Keyboard",
            "current_price": 159.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 70.9,
                "social_score": 73.2,
                "final_score": 72.1,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-005",
            "product_title": "Smart Fitness Tracker with ECG",
            "current_price": 249.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 69.7,
                "social_score": 72.8,
                "final_score": 71.3,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-006",
            "product_title": "Portable Espresso Machine",
            "current_price": 129.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 68.4,
                "social_score": 71.6,
                "final_score": 70.0,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-007",
            "product_title": "Smart Door Lock with Fingerprint",
            "current_price": 199.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 67.2,
                "social_score": 70.4,
                "final_score": 68.8,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-008",
            "product_title": "Wireless Phone Charger Stand",
            "current_price": 39.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 66.8,
                "social_score": 69.2,
                "final_score": 68.0,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-009",
            "product_title": "Smart LED Strip Lights",
            "current_price": 49.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 65.5,
                "social_score": 68.7,
                "final_score": 67.1,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-010",
            "product_title": "Bluetooth Sleep Mask with Speakers",
            "current_price": 29.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 64.3,
                "social_score": 67.9,
                "final_score": 66.1,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-011",
            "product_title": "Smart Pet Feeder with Camera",
            "current_price": 149.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 63.1,
                "social_score": 66.8,
                "final_score": 65.0,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-012",
            "product_title": "Ergonomic Laptop Stand Adjustable",
            "current_price": 59.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 62.7,
                "social_score": 65.4,
                "final_score": 64.1,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-013",
            "product_title": "Smart Air Purifier with HEPA Filter",
            "current_price": 199.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 61.5,
                "social_score": 64.2,
                "final_score": 62.9,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-014",
            "product_title": "Wireless Gaming Mouse with RGB",
            "current_price": 79.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 60.8,
                "social_score": 63.5,
                "final_score": 62.2,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-015",
            "product_title": "Smart Bathroom Scale with Body Analysis",
            "current_price": 89.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 59.6,
                "social_score": 62.8,
                "final_score": 61.2,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-016",
            "product_title": "Portable Bluetooth Projector",
            "current_price": 299.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 58.4,
                "social_score": 61.7,
                "final_score": 60.1,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-017",
            "product_title": "Smart Plant Pot with Sensors",
            "current_price": 69.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 57.2,
                "social_score": 60.5,
                "final_score": 58.9,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "RISE-018",
            "product_title": "Wireless Car Charger Mount",
            "current_price": 34.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 56.8,
                "social_score": 59.3,
                "final_score": 58.1,
                "label": "Rising",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        
        # STEADY PRODUCTS (15 items)
        {
            "sku_code": "STEADY-001",
            "product_title": "Classic Leather Wallet",
            "current_price": 49.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 55.4,
                "social_score": 52.7,
                "final_score": 54.1,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-002",
            "product_title": "Stainless Steel Water Bottle",
            "current_price": 24.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 54.2,
                "social_score": 51.8,
                "final_score": 53.0,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-003",
            "product_title": "Organic Cotton T-Shirt",
            "current_price": 19.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 53.1,
                "social_score": 50.6,
                "final_score": 51.9,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-004",
            "product_title": "Ceramic Coffee Mug Set",
            "current_price": 29.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 52.8,
                "social_score": 49.4,
                "final_score": 51.1,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-005",
            "product_title": "Basic Phone Case Clear",
            "current_price": 12.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 51.6,
                "social_score": 48.2,
                "final_score": 49.9,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-006",
            "product_title": "Cotton Bed Sheets Set",
            "current_price": 79.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 50.4,
                "social_score": 47.8,
                "final_score": 49.1,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-007",
            "product_title": "Kitchen Knife Set",
            "current_price": 89.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 49.7,
                "social_score": 46.5,
                "final_score": 48.1,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-008",
            "product_title": "Reading Glasses Blue Light",
            "current_price": 39.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 48.5,
                "social_score": 45.3,
                "final_score": 46.9,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-009",
            "product_title": "Canvas Tote Bag",
            "current_price": 16.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 47.3,
                "social_score": 44.1,
                "final_score": 45.7,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-010",
            "product_title": "Desk Organizer Bamboo",
            "current_price": 34.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 46.8,
                "social_score": 43.7,
                "final_score": 45.3,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-011",
            "product_title": "Wall Clock Modern Design",
            "current_price": 42.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 45.6,
                "social_score": 42.4,
                "final_score": 44.0,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-012",
            "product_title": "Notebook Journal Leather",
            "current_price": 27.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 44.4,
                "social_score": 41.2,
                "final_score": 42.8,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-013",
            "product_title": "Picture Frame Set Wood",
            "current_price": 31.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 43.2,
                "social_score": 40.8,
                "final_score": 42.0,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-014",
            "product_title": "Candle Set Aromatherapy",
            "current_price": 24.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 42.7,
                "social_score": 39.5,
                "final_score": 41.1,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "STEADY-015",
            "product_title": "Kitchen Towel Set Cotton",
            "current_price": 18.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 41.5,
                "social_score": 38.3,
                "final_score": 39.9,
                "label": "Steady",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        
        # DECLINING PRODUCTS (5 items)
        {
            "sku_code": "DECLINE-001",
            "product_title": "DVD Player Basic Model",
            "current_price": 39.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 25.3,
                "social_score": 22.7,
                "final_score": 24.0,
                "label": "Declining",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "DECLINE-002",
            "product_title": "Wired Computer Mouse",
            "current_price": 14.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 28.1,
                "social_score": 24.5,
                "final_score": 26.3,
                "label": "Declining",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "DECLINE-003",
            "product_title": "Flip Phone Basic",
            "current_price": 49.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 21.8,
                "social_score": 19.4,
                "final_score": 20.6,
                "label": "Declining",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "DECLINE-004",
            "product_title": "CD Player Portable",
            "current_price": 29.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 18.5,
                "social_score": 16.2,
                "final_score": 17.4,
                "label": "Declining",
                "computed_at": datetime.utcnow().isoformat()
            }
        },
        {
            "sku_code": "DECLINE-005",
            "product_title": "Fax Machine Home Office",
            "current_price": 89.99,
            "image_url": None,
            "status": "active",
            "trend_data": {
                "google_trend_index": 15.2,
                "social_score": 13.8,
                "final_score": 14.5,
                "label": "Declining",
                "computed_at": datetime.utcnow().isoformat()
            }
        }
    ]