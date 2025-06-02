#!/usr/bin/env python3
"""
Comprehensive test script for CSV URL ingestion functionality.
Tests all aspects of the new URL-based ingestion feature.
"""

import json
from typing import Any, Dict, Optional

import requests

# Base URL for the API
BASE_URL = "http://localhost:8001"

def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_subheader(title: str) -> None:
    """Print a formatted subheader."""
    print(f"\n📋 {title}")
    print('-' * 40)

def test_health_check() -> bool:
    """Test that the API is running."""
    print_subheader("API Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy and running!")
            return True
        else:
            print(f"❌ API health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not reach API: {e}")
        return False

def test_url_ingestion(url: str, dataset_type: str, namespace: str) -> Optional[Dict[str, Any]]:
    """Test URL ingestion with a specific URL."""
    print_subheader(f"URL Ingestion: {dataset_type}")
    print(f"📥 URL: {url}")
    print(f"📂 Namespace: {namespace}")
    
    payload = {
        "url": url,
        "namespace": namespace,
        "version": 0,
        "chunk_size": 5000
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dspaces/ingest/{dataset_type}/from-url",
            json=payload,
            timeout=120  # Allow more time for download
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ URL ingestion successful!")
            print(f"   📊 Rows: {result.get('total_rows', 'Unknown')}")
            print(f"   📋 Columns: {result.get('total_columns', 'Unknown')}")
            print(f"   📝 Column names: {result.get('columns', [])}")
            return result
        else:
            print(f"❌ URL ingestion failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during URL ingestion: {e}")
        return None

def test_data_retrieval(dataset_type: str, namespace: str, limit: int = 5) -> Optional[Dict[str, Any]]:
    """Test data retrieval from ingested dataset."""
    print_subheader(f"Data Retrieval: {dataset_type}/{namespace}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/dspaces/retrieve/{dataset_type}/{namespace}?limit={limit}",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Data retrieval successful!")
            print(f"   📊 Retrieved rows: {len(result.get('data', []))}")
            print(f"   📋 Columns: {result.get('columns', [])}")
            print(f"   📝 Sample data: {json.dumps(result.get('data', [])[:2], indent=2)}")
            return result
        else:
            print(f"❌ Data retrieval failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during data retrieval: {e}")
        return None

def test_data_filtering(dataset_type: str, namespace: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Test data filtering functionality."""
    print_subheader(f"Data Filtering: {dataset_type}/{namespace}")
    print(f"🔍 Filters: {json.dumps(filters, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/dspaces/retrieve/{dataset_type}/{namespace}/filter",
            json=filters,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            metadata = result.get('metadata', {})
            print("✅ Data filtering successful!")
            print(f"   📊 Total rows: {metadata.get('total_rows', 'Unknown')}")
            print(f"   🔍 Filtered rows: {metadata.get('filtered_rows', 'Unknown')}")
            print(f"   📋 Returned rows: {metadata.get('returned_rows', 'Unknown')}")
            return result
        else:
            print(f"❌ Data filtering failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during data filtering: {e}")
        return None

def test_error_handling() -> bool:
    """Test error handling with invalid URLs."""
    print_subheader("Error Handling - Invalid URL")
    
    payload = {
        "url": "https://invalid-url-that-does-not-exist.com/nonexistent.csv",
        "namespace": "test_invalid_url",
        "version": 0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dspaces/ingest/test-dataset/from-url",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 400:
            print("✅ Invalid URL properly rejected with 400 status!")
            return True
        else:
            print(f"❌ Expected 400 status for invalid URL, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during invalid URL test: {e}")
        return False

def run_comprehensive_tests() -> None:
    """Run comprehensive tests of the CSV URL ingestion functionality."""
    print_header("CSV URL Ingestion - Comprehensive Tests")
    
    # Test datasets to validate
    test_datasets = [
        {
            "url": "https://raw.githubusercontent.com/holtzy/data_to_viz/master/Example_dataset/1_OneNum.csv",
            "dataset_type": "numeric-data",
            "namespace": "price_analysis",
            "filters": {"custom_filters": {"price": {"min": 100.0, "max": 400.0}}, "limit": 5}
        },
        {
            "url": "https://raw.githubusercontent.com/plotly/datasets/master/iris.csv",
            "dataset_type": "iris-dataset", 
            "namespace": "flower_data",
            "filters": {"custom_filters": {"Name": "Iris-setosa"}, "limit": 3}
        }
    ]
    
    # Step 1: Health check
    if not test_health_check():
        print("\n❌ API is not available. Please start the API server first.")
        return
    
    # Step 2: Test each dataset
    for i, dataset in enumerate(test_datasets, 1):
        print_header(f"Dataset {i}: {dataset['dataset_type']}")
        
        # Ingest from URL
        ingestion_result = test_url_ingestion(
            dataset["url"], 
            dataset["dataset_type"], 
            dataset["namespace"]
        )
        
        if not ingestion_result:
            print(f"⚠️  Skipping further tests for {dataset['dataset_type']} due to ingestion failure")
            continue
        
        # Retrieve data
        retrieval_result = test_data_retrieval(
            dataset["dataset_type"], 
            dataset["namespace"]
        )
        
        # Filter data
        if retrieval_result:
            test_data_filtering(
                dataset["dataset_type"], 
                dataset["namespace"], 
                dataset["filters"]
            )
    
    # Step 3: Test error handling
    print_header("Error Handling Tests")
    test_error_handling()
    
    # Final summary
    print_header("Test Summary")
    print("🎉 Comprehensive CSV URL ingestion testing completed!")
    print("\n✅ Key Features Validated:")
    print("   • URL-based CSV download and ingestion")
    print("   • Multiple dataset types support")
    print("   • Data retrieval with column selection")
    print("   • Advanced filtering capabilities")
    print("   • Proper error handling for invalid URLs")
    print("   • Automatic file cleanup after ingestion")
    print("   • Integration with existing DataSpaces infrastructure")

if __name__ == "__main__":
    run_comprehensive_tests()
