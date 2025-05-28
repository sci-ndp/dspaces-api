#!/usr/bin/env python3
"""
Script to ingest Salt Lake County data into DataSpaces
"""

import requests


def ingest_salt_lake_data():
    """Ingest the Salt Lake County data into DataSpaces using the API."""
    
    api_url = "http://localhost:8001"
    ingest_endpoint = f"{api_url}/dspaces/ingest/salt-lake-county"
    
    # Request payload
    ingest_request = {
        "namespace": "salt_lake_demo",
        "version": 0,
        "chunk_size": 10000
    }
    
    print("🔄 Starting Salt Lake County data ingestion...")
    print(f"API URL: {api_url}")
    print(f"Namespace: {ingest_request['namespace']}")
    print(f"Version: {ingest_request['version']}")
    print("-" * 50)
    
    try:
        # Make the ingestion request
        response = requests.post(
            ingest_endpoint,
            json=ingest_request,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minutes timeout for large data ingestion
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Data ingestion successful!")
            print(f"📁 File: {result['file_path']}")
            print(f"📊 Total rows: {result['total_rows']:,}")
            print(f"📈 Total columns: {result['total_columns']}")
            print(f"🏷️  Namespace: {result['namespace']}")
            print(f"🔢 Version: {result['version']}")
            
            # Show column summary
            stored_objects = result['stored_objects']
            successful_columns = len([col for col, info in stored_objects.items() if 'error' not in info])
            failed_columns = len([col for col, info in stored_objects.items() if 'error' in info])
            
            print(f"✅ Successfully stored: {successful_columns} columns")
            if failed_columns > 0:
                print(f"❌ Failed to store: {failed_columns} columns")
                for col, info in stored_objects.items():
                    if 'error' in info:
                        print(f"   • {col}: {info['error']}")
            
            print("\n📋 Sample of stored columns:")
            for i, (col, info) in enumerate(list(stored_objects.items())[:5]):
                if 'error' not in info:
                    data_type = info.get('data_type', 'unknown')
                    num_elements = info.get('num_elements', 'unknown')
                    print(f"   {i+1}. {col} ({data_type}) - {num_elements} elements")
            
            if len(stored_objects) > 5:
                print(f"   ... and {len(stored_objects) - 5} more columns")
            
            print("\n🎉 Salt Lake County data is now available in DataSpaces!")
            print("You can now run the showcase: python salt_lake_showcase.py")
            
            return True
            
        else:
            print(f"❌ Ingestion failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("Make sure the DataSpaces API is running on http://localhost:8001")
        print("You can start it with: docker-compose up -d")
        return False
        
    except requests.exceptions.Timeout:
        print("⏰ Request timed out. The data ingestion might still be in progress.")
        print("Please check the API logs or try the test script later.")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error during ingestion: {str(e)}")
        return False

if __name__ == "__main__":
    success = ingest_salt_lake_data()
    exit(0 if success else 1)
