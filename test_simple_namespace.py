#!/usr/bin/env python3
"""
Simple test to validate the default namespace functionality.
"""

import requests

API_BASE_URL = "http://localhost:8001"

def main():
    print("🚀 Testing DSpaces API Default Namespace Configuration...")
    
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
    
    # Test 3: Try Salt Lake ingestion without namespace
    print("\n3️⃣ Testing Salt Lake Ingestion (Default Namespace)...")
    payload = {
        "version": 0,
        "chunk_size": 1000
        # Intentionally omitting namespace to test default
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/salt-lake-county", 
            json=payload, 
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            namespace = result.get("namespace", "NOT_FOUND")
            print("✅ Ingestion successful!")
            print(f"📁 Namespace used: {namespace}")
            
            if namespace == "datasets":
                print("🎉 SUCCESS: Default namespace 'datasets' was applied!")
            else:
                print(f"⚠️ Expected 'datasets', got '{namespace}'")
                
        elif response.status_code == 400:
            error_detail = response.json().get("detail", response.text)
            print(f"⚠️ Request failed (expected): {error_detail}")
        else:
            print(f"❌ Unexpected status: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (normal for large data)")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 4: Try with explicit namespace
    print("\n4️⃣ Testing Salt Lake Ingestion (Explicit Namespace)...")
    payload_explicit = {
        "namespace": "custom_test_namespace",
        "version": 0,
        "chunk_size": 1000
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/salt-lake-county", 
            json=payload_explicit, 
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            namespace = result.get("namespace", "NOT_FOUND")
            print("✅ Ingestion successful!")
            print(f"📁 Namespace used: {namespace}")
            
            if namespace == "custom_test_namespace":
                print("🎉 SUCCESS: Explicit namespace was respected!")
            else:
                print(f"⚠️ Expected 'custom_test_namespace', got '{namespace}'")
                
        else:
            print(f"⚠️ Status {response.status_code}: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (normal for large data)")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n✅ Test completed! Check the results above.")

if __name__ == "__main__":
    main()
