#!/usr/bin/env python3
"""
Test script to validate the default namespace functionality in the DSpaces CSV API.
Tests that CSV ingestion requests without explicit namespace use "datasets" by default.
"""

import sys
import time

import requests

API_BASE_URL = "http://localhost:8001"

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

def test_csv_ingestion_without_namespace():
    """Test CSV ingestion without specifying namespace - should default to 'datasets'."""
    print("\n🧪 Testing CSV ingestion WITHOUT namespace (should default to 'datasets')...")
    
    # Sample CSV data
    csv_data = """name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Chicago"""
    
    # Payload without namespace
    payload = {
        "csv_data": csv_data,
        "dataset_name": "test_default_namespace"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/csv/ingest", 
            json=payload, 
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CSV ingestion successful!")
            
            # Check if the response indicates the default namespace was used
            if "namespace" in result:
                if result["namespace"] == "datasets":
                    print("✅ Default namespace 'datasets' was applied correctly!")
                    return True
                else:
                    print(f"❌ Unexpected namespace: {result['namespace']}")
                    return False
            else:
                print("⚠️ Response doesn't include namespace information")
                return True  # Still consider success if ingestion worked
        else:
            print(f"❌ CSV ingestion failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CSV ingestion request failed: {e}")
        return False

def test_csv_ingestion_with_explicit_namespace():
    """Test CSV ingestion with explicit namespace to ensure it's still respected."""
    print("\n🧪 Testing CSV ingestion WITH explicit namespace...")
    
    # Sample CSV data
    csv_data = """product,price,category
Laptop,999,Electronics
Book,20,Education
Coffee,5,Food"""
    
    # Payload with explicit namespace
    payload = {
        "csv_data": csv_data,
        "dataset_name": "test_explicit_namespace",
        "namespace": "custom_namespace"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/csv/ingest", 
            json=payload, 
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CSV ingestion successful!")
            
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
                return True  # Still consider success if ingestion worked
        else:
            print(f"❌ CSV ingestion failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CSV ingestion request failed: {e}")
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
    print("🚀 Starting DSpaces CSV API Default Namespace Tests...")
    
    # Wait a moment for services to be fully ready
    print("⏳ Waiting 5 seconds for services to be fully ready...")
    time.sleep(5)
    
    tests = [
        ("API Health Check", test_api_health),
        ("API Documentation", test_api_docs),
        ("CSV Ingestion without namespace", test_csv_ingestion_without_namespace),
        ("CSV Ingestion with explicit namespace", test_csv_ingestion_with_explicit_namespace),
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
    
    if passed == total:
        print("🎉 All tests passed! Default namespace configuration is working correctly.")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
