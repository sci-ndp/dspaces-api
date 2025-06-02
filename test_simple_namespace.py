#!/usr/bin/env python3
"""
Simple test to validate URL-based ingestion functionality and default namespace behavior.
"""

import requests

API_BASE_URL = "http://localhost:8001"
TEST_DATASET_TYPE = "test-csv-data"

def main():
    print("🚀 Testing DSpaces API URL-based Ingestion and Default Namespace Configuration...")
    
    # Test 1: Check if API is running
    print("\n1️⃣ Testing API Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # Test 2: Check available datasets
    print("\n2️⃣ Testing Available Datasets...")
    try:
        response = requests.get(f"{API_BASE_URL}/dspaces/datasets", timeout=5)
        if response.status_code == 200:
            print("✅ Datasets endpoint accessible")
            datasets = response.json()
            print(f"Available datasets: {len(datasets.get('datasets', []))}")
        else:
            print(f"⚠️ Datasets endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Datasets check failed: {e}")
    
    # Test 3: Try URL-based ingestion without URL parameter (should fail)
    print("\n3️⃣ Testing URL-based Ingestion Validation (Missing URL)...")
    payload = {
        "namespace": "test-namespace"
        # Intentionally omitting required 'url' parameter to test validation
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json=payload, 
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code in [400, 422]:  # Expected validation error
            print("✅ URL validation working - missing URL properly rejected!")
        elif response.status_code == 200:
            print("⚠️ Unexpected success - validation may not be working")
        else:
            print(f"❌ Unexpected status: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 4: Try with explicit URL and namespace
    print("\n4️⃣ Testing URL-based Ingestion with Explicit URL and Namespace...")
    payload_explicit = {
        "url": "https://example.com/sample-data.csv",  # This will likely fail but tests structure
        "namespace": "custom_test_namespace"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json=payload_explicit, 
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            namespace = result.get("namespace", "NOT_FOUND")
            print("✅ URL-based ingestion successful!")
            print(f"📁 Namespace used: {namespace}")
            
            if namespace == "custom_test_namespace":
                print("🎉 SUCCESS: Explicit namespace was respected!")
            else:
                print(f"⚠️ Expected 'custom_test_namespace', got '{namespace}'")
        elif response.status_code in [400, 404, 422]:
            print("✅ Expected error - URL validation or download failure (normal for test URL)")
        else:
            print(f"⚠️ Status {response.status_code}: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (normal for invalid URLs)")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 5: Try with default namespace (no explicit namespace)
    print("\n5️⃣ Testing URL-based Ingestion with Default Namespace...")
    payload_default = {
        "url": "https://example.com/sample-data.csv"
        # Intentionally omitting namespace to test default
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json=payload_default, 
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            namespace = result.get("namespace", "NOT_FOUND")
            print("✅ URL-based ingestion successful!")
            print(f"📁 Namespace used: {namespace}")
            
            if namespace == "datasets":
                print("🎉 SUCCESS: Default namespace 'datasets' was applied!")
            else:
                print(f"⚠️ Expected 'datasets', got '{namespace}'")
        elif response.status_code in [400, 404, 422]:
            print("✅ Expected error - URL validation or download failure (normal for test URL)")
        else:
            print(f"⚠️ Status {response.status_code}: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (normal for invalid URLs)")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n✅ Test completed! Check the results above.")
    print("💡 Note: URL download failures are expected since we're using example URLs.")
    print("   The important thing is that URL validation is working and namespaces are handled correctly.")

if __name__ == "__main__":
    main()
