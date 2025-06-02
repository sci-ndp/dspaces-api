#!/usr/bin/env python3
"""
Script to demonstrate URL-based CSV data ingestion into DataSpaces
"""

import requests


def ingest_csv_data_from_url():
    """Ingest CSV data into DataSpaces using URL-based ingestion."""
    
    api_url = "http://localhost:8001"
    
    # Example configuration - UPDATE THESE VALUES
    dataset_type = "air-quality"  # Change this to your dataset type
    namespace = "demo_namespace"   # Change this to your namespace
    csv_url = "https://example.com/data.csv"  # CHANGE THIS to your actual CSV URL
    
    ingest_endpoint = f"{api_url}/dspaces/ingest/{dataset_type}"
    
    # Request payload for URL-based ingestion
    ingest_request = {
        "url": csv_url,
        "namespace": namespace,
        "version": 0,
        "chunk_size": 10000
    }
    
    print("🔄 Starting URL-based CSV data ingestion...")
    print(f"API URL: {api_url}")
    print(f"Dataset Type: {dataset_type}")
    print(f"CSV URL: {csv_url}")
    print(f"Namespace: {namespace}")
    print(f"Version: {ingest_request['version']}")
    print("-" * 50)
    
    if csv_url == "https://example.com/data.csv":
        print("❌ ERROR: You must update the csv_url variable with a real CSV file URL!")
        print("Edit this script and change the csv_url variable to point to your actual CSV data.")
        return False
    
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
            
            print("\n🎉 CSV data is now available in DataSpaces!")
            print("You can now run the showcase: python salt_lake_showcase.py")
            print("(Make sure to update the DATASET_TYPE and NAMESPACE variables in that script)")
            
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
    success = ingest_csv_data_from_url()
    exit(0 if success else 1)
