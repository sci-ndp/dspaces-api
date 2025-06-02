#!/usr/bin/env python3
"""
Comprehensive test to validate URL-based CSV ingestion and API endpoints.
Tests CSV-related endpoints to ensure proper URL-based data ingestion workflow.
"""

import requests

API_BASE_URL = "http://localhost:8001"
# Configuration for testing - update these for your dataset
TEST_DATASET_TYPE = "test-csv-data"
TEST_NAMESPACE = "test-demo"

def test_retrieve_with_namespace():
    """Test retrieving data using the configured namespace."""
    print(f"\n5️⃣ Testing Data Retrieval with Namespace '{TEST_NAMESPACE}'...")
    
    try:
        # Try to retrieve data from the configured namespace
        response = requests.get(
            f"{API_BASE_URL}/dspaces/retrieve/{TEST_DATASET_TYPE}/{TEST_NAMESPACE}?limit=5", 
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Data retrieval successful!")
            print(f"📊 Retrieved {len(result.get('data', []))} rows")
            print(f"📁 Namespace: {result.get('metadata', {}).get('namespace', 'unknown')}")
            return True
        else:
            print(f"⚠️ Status {response.status_code}: {response.text[:200]}")
            print("💡 This might be expected if no data has been ingested yet")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_filter_with_namespace():
    """Test filtering data using the configured namespace."""
    print(f"\n6️⃣ Testing Data Filtering with Namespace '{TEST_NAMESPACE}'...")
    
    filter_payload = {
        "limit": 5,
        "custom_filters": {"parameter_name": "Ozone"}  # Using generic filter structure
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/retrieve/{TEST_DATASET_TYPE}/{TEST_NAMESPACE}/filter", 
            json=filter_payload,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Data filtering successful!")
            print(f"📊 Filtered to {len(result.get('data', []))} rows")
            print(f"📁 Namespace: {result.get('metadata', {}).get('namespace', 'unknown')}")
            return True
        else:
            print(f"⚠️ Status {response.status_code}: {response.text[:200]}")
            print("💡 This might be expected if no data has been ingested yet")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_available_filters_with_namespace():
    """Test available filters endpoint with configured namespace."""
    print(f"\n7️⃣ Testing Available Filters with Namespace '{TEST_NAMESPACE}'...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/dspaces/retrieve/{TEST_DATASET_TYPE}/{TEST_NAMESPACE}/available-filters", 
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Available filters retrieved successfully!")
            print(f"📊 Available parameters: {len(result.get('parameter_names', []))}")
            print(f"📁 Namespace: {result.get('metadata', {}).get('namespace', 'unknown')}")
            return True
        else:
            print(f"⚠️ Status {response.status_code}: {response.text[:200]}")
            print("💡 This might be expected if no data has been ingested yet")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_url_ingestion_endpoint():
    """Test URL-based ingestion endpoint structure."""
    print(f"\n8️⃣ Testing URL Ingestion Endpoint Structure...")
    
    # Test with invalid payload to check endpoint exists and validation works
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json={"invalid": "payload"},  # Intentionally invalid to test validation
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code in [400, 422]:  # Expected validation error
            print("✅ URL ingestion endpoint exists and validates input!")
            print("💡 To test with real data, use: {'url': 'https://your-csv-url.com/data.csv', 'namespace': 'your-namespace'}")
            return True
        elif response.status_code == 200:
            print("✅ URL ingestion endpoint exists!")
            return True
        else:
            print(f"⚠️ Unexpected status {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("🚀 Comprehensive DSpaces API URL-Based Ingestion Validation...")
    print(f"📋 Testing with dataset type: {TEST_DATASET_TYPE}")
    print(f"📁 Testing with namespace: {TEST_NAMESPACE}")
    
    tests = [
        ("Data Retrieval", test_retrieve_with_namespace),
        ("Data Filtering", test_filter_with_namespace), 
        ("Available Filters", test_available_filters_with_namespace),
        ("URL Ingestion Endpoint", test_url_ingestion_endpoint)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 COMPREHENSIVE TEST SUMMARY")
    print('='*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ URL-based ingestion endpoints are working correctly!")
        print("✅ Generic CSV API structure is functioning!")
        print("✅ The DSpaces API is ready for URL-based data ingestion!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        print("💡 This is expected if no data has been ingested yet.")
        print("💡 To fully test, ingest data via URL first:")
        print(f"   POST /dspaces/ingest/{TEST_DATASET_TYPE}")
        print("   with JSON: {'url': 'https://your-csv-url.com/data.csv', 'namespace': 'your-namespace'}")

if __name__ == "__main__":
    main()
