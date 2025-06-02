#!/usr/bin/env python3
"""
Demonstration script showing URL-based ingestion and default namespace feature.
This shows how the API now requires URLs and provides default namespace functionality.
"""

import json
import requests

API_BASE_URL = "http://localhost:8001"
TEST_DATASET_TYPE = "test-csv-data"

def demo_url_based_ingestion_and_default_namespace():
    """Demonstrate URL-based ingestion and default namespace functionality."""
    
    print("🚀 DSpaces CSV API - URL-based Ingestion & Default Namespace Demo")
    print("="*70)
    
    print("\n📋 SCENARIO: User wants to ingest CSV data from URL without specifying namespace")
    print("Current behavior: ✅ URL is required, namespace defaults to 'datasets'")
    
    # Demo 1: Minimal payload with URL (new behavior)
    print("\n1️⃣ DEMO: URL-based Ingestion with Default Namespace")
    print("-" * 50)
    
    minimal_payload = {
        "url": "https://example.com/sample-data.csv"
        # Notice: NO namespace specified - will use default!
    }
    
    print("Request payload:")
    print(json.dumps(minimal_payload, indent=2))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json=minimal_payload, 
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            namespace_used = result.get("namespace", "unknown")
            
            print("\n✅ SUCCESS!")
            print(f"📁 Namespace automatically assigned: '{namespace_used}'")
            print(f"📊 Data stored: {result.get('total_rows', 0):,} rows, {result.get('total_columns', 0)} columns")
        elif response.status_code in [400, 404, 422]:
            print("\n⚠️ Expected error - URL validation or download failure")
            print("   (This is normal for demo URLs that don't exist)")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"\n❌ Unexpected error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out (normal for invalid URLs)")
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
    
    # Demo 2: Explicit namespace (user choice respected)
    print("\n\n2️⃣ DEMO: URL-based Ingestion with Explicit Namespace")
    print("-" * 50)
    
    explicit_payload = {
        "url": "https://example.com/sample-data.csv",
        "namespace": "my_custom_namespace"
    }
    
    print("Request payload:")
    print(json.dumps(explicit_payload, indent=2))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json=explicit_payload, 
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            namespace_used = result.get("namespace", "unknown")
            
            print("\n✅ SUCCESS!")
            print(f"📁 Namespace used: '{namespace_used}'")
            
            if namespace_used == "my_custom_namespace":
                print("🎉 User's explicit namespace was respected!")
            else:
                print(f"⚠️ Expected 'my_custom_namespace', but got '{namespace_used}'")
                
            print(f"📊 Data stored: {result.get('total_rows', 0):,} rows, {result.get('total_columns', 0)} columns")
        elif response.status_code in [400, 404, 422]:
            print("\n⚠️ Expected error - URL validation or download failure")
            print("   (This is normal for demo URLs that don't exist)")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"\n❌ Unexpected error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out (normal for invalid URLs)")
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
    
    # Demo 3: Show validation (missing URL)
    print("\n\n3️⃣ DEMO: Validation - Missing URL (Should Fail)")
    print("-" * 50)
    
    invalid_payload = {
        "namespace": "test_namespace"
        # Missing required 'url' field
    }
    
    print("Request payload:")
    print(json.dumps(invalid_payload, indent=2))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dspaces/ingest/{TEST_DATASET_TYPE}", 
            json=invalid_payload, 
            timeout=5
        )
        
        if response.status_code in [400, 422]:
            print("\n✅ SUCCESS! Validation working correctly")
            print("   API properly rejected request missing URL")
            print(f"   Response: {response.text[:100]}...")
        elif response.status_code == 200:
            print("\n❌ PROBLEM! Request succeeded without URL")
            print("   This suggests validation is not working correctly")
        else:
            print(f"\n⚠️ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
    
    # Demo 4: Check retrieved data
    print("\n\n4️⃣ DEMO: Retrieving Ingested Data")
    print("-" * 50)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/dspaces/retrieve/{TEST_DATASET_TYPE}/datasets?limit=3", 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Data retrieval successful!")
            print(f"📊 Retrieved {len(data.get('data', []))} sample rows")
            
            if data.get('data'):
                print("\nSample data:")
                for i, row in enumerate(data['data'][:2], 1):
                    print(f"  Row {i}: {str(row)[:80]}...")
            else:
                print("ℹ️ No data available (expected if ingestion failed due to demo URLs)")
        elif response.status_code == 404:
            print("\n⚠️ No data found in default namespace")
            print("   This is expected if ingestion failed due to demo URLs")
        else:
            print(f"\n⚠️ Data retrieval failed: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Data retrieval failed: {e}")
    
    # Summary
    print("\n\n" + "="*70)
    print("📋 SUMMARY")
    print("="*70)
    print("✅ URL-based ingestion: All data must come from external URLs")
    print("✅ Default namespace: When not specified, uses 'datasets'")
    print("✅ Explicit namespace: User choice is respected when provided")
    print("✅ Validation: Missing URLs are properly rejected")
    print("📝 Note: Demo URLs may fail - this tests structure, not actual data")

if __name__ == "__main__":
    demo_url_based_ingestion_and_default_namespace()
