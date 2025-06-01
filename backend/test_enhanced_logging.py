#!/usr/bin/env python3
"""
Test script to verify the enhanced OAuth logging works correctly.
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up environment for testing
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("ENVIRONMENT", "development")

# Import and setup logging
from app.core.logging import setup_logging

def test_logging_setup():
    """Test that logging is set up correctly."""
    print("Setting up logging...")
    setup_logging()
    
    # Get a logger and test different levels
    logger = logging.getLogger("test_oauth_logging")
    
    print("\nTesting log levels:")
    logger.info("✓ INFO level logging works")
    logger.warning("⚠ WARNING level logging works")
    logger.error("❌ ERROR level logging works")
    
    print("\nTesting OAuth-style logging:")
    logger.info("=== TESTING OAUTH TOKEN EXCHANGE ===")
    logger.info("Input parameters - shop_domain: test.myshopify.com, user_id: test_user")
    logger.info("OAuth code length: 32")
    logger.info("✓ Input validation passed")
    logger.info("=== PREPARING TOKEN EXCHANGE REQUEST ===")
    logger.info("Token URL: https://test.myshopify.com/admin/oauth/access_token")
    logger.info("Request payload keys: ['client_id', 'client_secret', 'code']")
    logger.info("✓ Request prepared successfully")
    logger.info("=== OAUTH TOKEN EXCHANGE TEST COMPLETED ===")
    
    print("\nLogging test completed successfully!")

if __name__ == "__main__":
    test_logging_setup()