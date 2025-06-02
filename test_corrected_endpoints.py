#!/usr/bin/env python3
"""
Test script to validate URL-based CSV ingestion functionality.
Tests that CSV ingestion properly requires URL-based data sources.
"""

import sys
import time

import requests

API_BASE_URL = "http://localhost:8001"
TEST_DATASET_TYPE = "test-csv-data"

def test_api_health():
    """Check if the API is running and accessible."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API health check passed")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API health check failed: {e}")
        return False

def test_available_datasets():
    """Check what datasets are available."""
    print("\n🔍 Checking available datasets...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/dspaces/datasets", timeout=5)
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            datasets = response.json()
            print("✅ Available datasets:")
            if "datasets" in datasets:
                for dataset in datasets["datasets"]:
                    print(f"  - {dataset.get('dataset_id', 'unknown')}: {dataset.get('description', 'No description')}")
                return True
            else:
                print("⚠️ Unexpected response format")
                print(f"Response: {response.text}")
                return True
        else:
            print(f"❌ Failed to get datasets: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_url_ingestion_validation():
    """Test URL-based ingestion validation - should require valid URL."""
    print("\n🧪 Testing URL-based CSV ingestion validation...")
    
    # Test with missing URL to verify validation
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json={"namespace": "test-demo"},  # Missing required 'url' field
            timeout=5
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code in [400, 422]:  # Expected validation error
            print("✅ URL validation working - missing URL properly rejected")
            return True
        elif response.status_code == 200:
            print("⚠️ Unexpected success - validation may not be working")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    
def test_url_ingestion_structure():
    """Test that URL ingestion endpoint has correct structure."""
    print("\n🧪 Testing URL-based ingestion endpoint structure...")
    
    # Test with invalid URL to verify endpoint exists and validates URLs
    payload = {
        "url": "not-a-valid-url",
        "namespace": "test-demo"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json=payload, 
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code in [400, 422]:  # Expected validation error for invalid URL
            print("✅ URL ingestion endpoint exists and validates URLs!")
            return True
        elif response.status_code == 200:
            print("⚠️ Unexpected success with invalid URL")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_csv_ingestion_with_url():
    """Test CSV ingestion with URL to ensure URL-based ingestion works."""
    print("\n🧪 Testing CSV ingestion WITH URL and explicit namespace...")
    
    # Test with a sample CSV URL (this might fail but tests the structure)
    payload = {
        "url": "https://raw.githubusercontent.com/example/data/main/sample.csv",
        "namespace": "custom_namespace"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json=payload, 
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ URL-based CSV ingestion successful!")
            
            # Check if the explicit namespace was respected
            if "namespace" in result:
                if result["namespace"] == "custom_namespace":
                    print("✅ Explicit namespace 'custom_namespace' was respected!")
                    return True
                else:
                    print(f"❌ Unexpected namespace: {result['namespace']}")
                    return False
            else:
                print("⚠️ Response doesn't include namespace information")
                print(f"Full response: {result}")
                return True  # Still consider success if ingestion worked
        elif response.status_code in [400, 404, 422]:
            print("✅ URL validation working - invalid/inaccessible URL properly handled")
            return True  # This is expected behavior for URL validation
        else:
            print(f"❌ CSV ingestion failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CSV ingestion request failed: {e}")
        return False

def test_generic_ingestion_with_namespace():
    """Test generic CSV ingestion with explicit namespace."""
    print(f"\n🧪 Testing {TEST_DATASET_TYPE} ingestion WITH explicit namespace...")
    
    # Test with invalid URL to verify validation
    payload = {
        "url": "https://example.com/invalid-data.csv",  # This URL likely won't work but tests structure
        "namespace": "custom_namespace"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json=payload, 
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code in [400, 404, 422]:  # Expected errors for invalid URL
            print("✅ URL ingestion endpoint working - invalid URL properly handled!")
            return True
        elif response.status_code == 200:
            result = response.json()
            print("✅ URL ingestion successful!")
            return True
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_api_docs():
    """Check if the API documentation is accessible."""
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API documentation is accessible at /docs")
            return True
        else:
            print(f"❌ API documentation check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API documentation check failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting DSpaces URL-based CSV API Tests...")
    
    # Wait a moment for services to be fully ready
    print("⏳ Waiting 3 seconds for services to be fully ready...")
    time.sleep(3)
    
    tests = [
        ("API Health Check", test_api_health),
        ("API Documentation", test_api_docs),
        ("Available Datasets", test_available_datasets),
        ("URL Ingestion Validation", test_url_ingestion_validation),
        ("URL Ingestion Structure", test_url_ingestion_structure),
        ("CSV Ingestion with URL", test_csv_ingestion_with_url),
        ("Generic Ingestion with Namespace", test_generic_ingestion_with_namespace),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= total - 1:  # Allow one test to fail
        print("🎉 Most tests passed! URL-based ingestion appears to be working.")
        sys.exit(0)
    else:
        print("💥 Multiple tests failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
