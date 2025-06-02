#!/usr/bin/env python3
"""
Test script for the new CSV URL ingestion functionality.
"""

import json

import requests

# Base URL for the API
BASE_URL = "http://localhost:8001"

def test_health_check():
    """Test that the API is running."""
    print("🏥 Testing API health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy!")
            return True
        else:
            print(f"❌ API health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not reach API: {e}")
        return False

def test_csv_url_ingestion():
    """Test the new CSV URL ingestion endpoint."""
    print("\n📥 Testing CSV URL ingestion...")
    
    # Use a public CSV file for testing
    test_url = "https://raw.githubusercontent.com/holtzy/data_to_viz/master/Example_dataset/1_OneNum.csv"
    
    payload = {
        "url": test_url,
        "namespace": "test_url_ingestion",
        "version": 0,
        "chunk_size": 1000,
        "filename": "test_data.csv"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dspaces/ingest/test-dataset/from-url",
            json=payload,
            timeout=60  # Allow more time for download and ingestion
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CSV URL ingestion successful!")
            print(f"   📊 Rows: {result.get('total_rows', 'Unknown')}")
            print(f"   📋 Columns: {result.get('total_columns', 'Unknown')}")
            print(f"   📂 Namespace: {result.get('namespace', 'Unknown')}")
            return True
        else:
            print(f"❌ CSV URL ingestion failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during CSV URL ingestion: {e}")
        return False

def test_invalid_url():
    """Test handling of invalid URLs."""
    print("\n🚫 Testing invalid URL handling...")
    
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
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Invalid URL properly rejected!")
            return True
        else:
            print(f"❌ Expected 400 status for invalid URL, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during invalid URL test: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing CSV URL Ingestion Functionality")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ API is not available. Please start the API server first.")
        return
    
    # Test 2: Valid CSV URL ingestion
    test_csv_url_ingestion()
    
    # Test 3: Invalid URL handling
    test_invalid_url()
    
    print("\n" + "=" * 50)
    print("🎯 CSV URL ingestion testing complete!")

if __name__ == "__main__":
    main()
