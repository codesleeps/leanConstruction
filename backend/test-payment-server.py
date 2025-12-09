#!/usr/bin/env python3
"""
Test script for the payment-only server
This script tests all the payment endpoints without requiring the ML modules
"""

import requests
import json
import time
import subprocess
import sys
import os
from threading import Thread

def start_server():
    """Start the payment-only server in a subprocess"""
    try:
        # Change to app directory and start server
        os.chdir('app')
        process = subprocess.Popen([
            sys.executable, 'payments_only.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def wait_for_server(url="http://localhost:8000", timeout=30):
    """Wait for server to be ready"""
    print("⏳ Waiting for server to start...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    
    print("❌ Server failed to start within timeout")
    return False

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_create_subscription():
    """Test subscription creation"""
    try:
        payload = {
            "price_id": "price_test_123",
            "customer_id": "cus_test_123"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/payments/create-subscription",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Create subscription passed")
            print(f"   Client secret: {data.get('client_secret')}")
            print(f"   Subscription ID: {data.get('subscription_id')}")
            return True
        else:
            print(f"❌ Create subscription failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Create subscription error: {e}")
        return False

def test_subscription_status():
    """Test subscription status"""
    try:
        response = requests.get("http://localhost:8000/api/v1/payments/subscription-status/cus_test_123")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Subscription status passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Customer ID: {data.get('customer_id')}")
            return True
        else:
            print(f"❌ Subscription status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Subscription status error: {e}")
        return False

def test_confirm_subscription():
    """Test subscription confirmation"""
    try:
        payload = {
            "payment_method_id": "pm_test_123",
            "customer_id": "cus_test_123",
            "client_secret": "pi_test_123_secret"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/payments/confirm-subscription",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Confirm subscription passed")
            print(f"   Success: {data.get('success')}")
            print(f"   Plan: {data.get('subscription', {}).get('plan', {}).get('name')}")
            return True
        else:
            print(f"❌ Confirm subscription failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Confirm subscription error: {e}")
        return False

def test_cancel_subscription():
    """Test subscription cancellation"""
    try:
        payload = {
            "subscription_id": "sub_test_123"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/payments/cancel-subscription",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Cancel subscription passed")
            print(f"   Success: {data.get('success')}")
            return True
        else:
            print(f"❌ Cancel subscription failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cancel subscription error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Payment-Only Server")
    print("=" * 40)
    
    # Start server
    server_process = start_server()
    if not server_process:
        return False
    
    try:
        # Wait for server to be ready
        if not wait_for_server():
            return False
        
        # Run tests
        print("\n📋 Running Tests:")
        print("-" * 20)
        
        tests = [
            test_health_endpoint,
            test_create_subscription,
            test_subscription_status,
            test_confirm_subscription,
            test_cancel_subscription
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()
        
        # Summary
        print("=" * 40)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Payment-only server is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the server logs for details.")
            return False
            
    finally:
        # Clean up
        print("\n🧹 Shutting down server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped.")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)