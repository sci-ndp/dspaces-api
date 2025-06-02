#!/usr/bin/env python3
"""
Simple test script for the Salt Lake Data API client
"""

import os
import sys

# Add the current directory to the path to import our showcase module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from salt_lake_showcase import GenericCSVDataAPI


def test_api_client():
    """Test basic API client functionality."""
    print("🧪 Testing Generic CSV Data API Client")
    print("=" * 50)
    
    # Initialize API client
    api = GenericCSVDataAPI()
    
    # Test 1: Connection check
    print("\n1. Testing API connection...")
    if api.check_connection():
        print("   ✅ Connection test passed")
    else:
        print("   ❌ Connection test failed")
        print("   Make sure the API server is running on http://localhost:8001")
        return False
    
    # Test 2: Get available filters
    print("\n2. Testing available filters endpoint...")
    filters = api.get_available_filters()
    if filters:
        print("   ✅ Available filters retrieved successfully")
        print(f"   📊 Found {len(filters)} filter categories")
        for key in filters.keys():
            print(f"      • {key}")
    else:
        print("   ⚠️  Could not retrieve available filters")
        print("   This might indicate the data hasn't been ingested yet")
    
    # Test 3: Get sample data
    print("\n3. Testing sample data endpoint...")
    sample = api.get_sample_data(5)
    if sample and 'data' in sample:
        print("   ✅ Sample data retrieved successfully")
        print(f"   📊 Retrieved {len(sample['data'])} sample rows")
        if len(sample['data']) > 0:
            print(f"   📋 Sample columns: {list(sample['data'][0].keys())}")
    else:
        print("   ❌ Could not retrieve sample data")
        return False
    
    # Test 4: Basic data retrieval
    print("\n4. Testing basic data retrieval...")
    data = api.retrieve_data(limit=10)
    if data and 'data' in data:
        print("   ✅ Data retrieval successful")
        print(f"   📊 Retrieved {len(data['data'])} rows")
        if 'metadata' in data:
            metadata = data['metadata']
            print(f"   📈 Total rows available: {metadata.get('total_rows', 'unknown')}")
    else:
        print("   ❌ Could not retrieve data from DataSpaces")
        print("   This indicates the data hasn't been ingested into the namespace")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("The Generic CSV Data API client is working correctly.")
    print("You can now run the full showcase: python salt_lake_showcase.py")
    
    return True

if __name__ == "__main__":
    success = test_api_client()
    sys.exit(0 if success else 1)
