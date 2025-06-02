#!/usr/bin/env python3
"""
Test script to verify static dataset ingestion has been completely removed
and only URL-based ingestion is supported.
"""

import requests
import json
import time
import sys

# API base URL
BASE_URL = "http://localhost:8001"

def test_static_endpoint_removed():
    """Test that the static ingestion endpoint no longer exists"""
    print("🧪 Testing static ingestion endpoint removal...")
    
    # Try to access the removed static endpoint
    static_endpoint = f"{BASE_URL}/dspaces/ingest/test-dataset"
    
    try:
        response = requests.post(
            static_endpoint,
            json={
                "namespace": "test_namespace",
                "version": 0,
                "chunk_size": 1000
            },
            timeout=10
        )
        
        # The endpoint should not exist (404) or method not allowed (405)
        if response.status_code in [404, 405]:
            print("✅ Static ingestion endpoint correctly removed")
            return True
        else:
            print(f"❌ Static endpoint still exists with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Cannot connect to API server - is it running?")
        return None
    except Exception as e:
        print(f"❌ Error testing static endpoint: {e}")
        return False

def test_url_endpoint_exists():
    """Test that URL-based ingestion endpoint still exists"""
    print("🧪 Testing URL ingestion endpoint availability...")
    
    # Test the URL endpoint exists (should get 422 for missing URL, not 404)
    url_endpoint = f"{BASE_URL}/dspaces/ingest/test-dataset/from-url"
    
    try:
        response = requests.post(
            url_endpoint,
            json={
                "namespace": "test_namespace", 
                "version": 0
                # Missing required "url" field should cause 422
            },
            timeout=10
        )
        
        if response.status_code == 422:
            print("✅ URL ingestion endpoint exists and validates input")
            return True
        elif response.status_code == 404:
            print("❌ URL ingestion endpoint not found")
            return False
        else:
            print(f"⚠️  URL endpoint returned unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return True  # Endpoint exists, just different validation
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Cannot connect to API server - is it running?")
        return None
    except Exception as e:
        print(f"❌ Error testing URL endpoint: {e}")
        return False

def test_api_health():
    """Test API health endpoint"""
    print("🧪 Testing API health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Cannot connect to API server")
        return None
    except Exception as e:
        print(f"❌ Error checking API health: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting static dataset removal verification tests...\n")
    
    results = []
    
    # Test API health first
    health_result = test_api_health()
    results.append(("API Health", health_result))
    
    if health_result is None:
        print("\n❌ Cannot connect to API server. Please ensure it's running on localhost:8001")
        print("To start the server: cd /home/jaytau/Programming/dspaces-hackathon/dspaces-api && ./start.sh")
        return 1
    
    print()
    
    # Test static endpoint removal
    static_result = test_static_endpoint_removed()
    results.append(("Static Endpoint Removed", static_result))
    
    print()
    
    # Test URL endpoint exists
    url_result = test_url_endpoint_exists()
    results.append(("URL Endpoint Available", url_result))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
            all_passed = False
        else:
            status = "⚠️  SKIP"
            all_passed = False
            
        print(f"{test_name:.<30} {status}")
    
    print("="*50)
    
    if all_passed:
        print("🎉 All tests passed! Static dataset support successfully removed.")
        print("✨ The API now only supports URL-based CSV ingestion.")
        return 0
    else:
        print("❌ Some tests failed. Please review the results above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
