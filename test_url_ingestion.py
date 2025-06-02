#!/usr/bin/env python3
"""
Test URL-based CSV ingestion functionality 
"""

import requests
import json
import sys

# Base URL for API
BASE_URL = "http://localhost:8001"

# Test dataset URL - Iris dataset from GitHub (small and reliable)
TEST_URL = "https://raw.githubusercontent.com/plotly/datasets/master/iris.csv"

def test_url_ingestion():
    """Test the URL-based ingestion endpoint"""
    print("🧪 Testing URL-based ingestion...")
    
    # Prepare the request payload
    payload = {
        "url": TEST_URL,
        "namespace": "iris_test",
        "version": 1,
        "chunk_size": 1000,
        "filename": "iris_dataset.csv"
    }
    
    try:
        # Make the POST request to ingest from URL
        response = requests.post(
            f"{BASE_URL}/dspaces/ingest/test-dataset/from-url",
            json=payload,
            timeout=30  # Allow sufficient time for download and ingestion
        )
        
        # Check if successful
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully ingested dataset from URL")
            print(f"  - Total rows: {result.get('total_rows')}")
            print(f"  - Total columns: {result.get('total_columns')}")
            print(f"  - Columns: {', '.join(result.get('columns', []))}")
            print(f"  - Namespace: {result.get('namespace')}")
            return True, result
        else:
            print(f"❌ Failed to ingest from URL: Status code {response.status_code}")
            print(f"  - Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error during URL ingestion: {e}")
        return False, None

def test_data_retrieval(namespace):
    """Test retrieving the ingested data"""
    print("\n🧪 Testing data retrieval for ingested dataset...")
    
    try:
        # Make the GET request to retrieve the data
        response = requests.get(
            f"{BASE_URL}/dspaces/retrieve/test-dataset/{namespace}",
            timeout=20
        )
        
        # Check if successful
        if response.status_code == 200:
            result = response.json()
            row_count = len(result.get('data', []))
            print(f"✅ Successfully retrieved dataset")
            print(f"  - Retrieved {row_count} rows")
            return True, result
        else:
            print(f"❌ Failed to retrieve data: Status code {response.status_code}")
            print(f"  - Response: {response.text}")
            return False, None
    
    except Exception as e:
        print(f"❌ Error during data retrieval: {e}")
        return False, None

def main():
    """Run all the URL ingestion tests"""
    print("🚀 Starting URL-based ingestion tests...\n")
    
    # Test URL-based ingestion
    ingestion_success, ingestion_result = test_url_ingestion()
    
    if not ingestion_success:
        print("\n❌ URL ingestion test failed, cannot continue")
        return 1
    
    # Get the namespace from the ingestion result
    namespace = ingestion_result.get('namespace')
    
    # Test retrieving the ingested data
    retrieval_success, _ = test_data_retrieval(namespace)
    
    # Print summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    print(f"URL-based Ingestion........ {'✅ PASS' if ingestion_success else '❌ FAIL'}")
    print(f"Data Retrieval............. {'✅ PASS' if retrieval_success else '❌ FAIL'}")
    print("="*50)
    
    if ingestion_success and retrieval_success:
        print("🎉 All URL-based ingestion tests passed!")
        print("✨ The API correctly supports URL-based CSV ingestion.")
        return 0
    else:
        print("❌ Some tests failed. Please review the results above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
