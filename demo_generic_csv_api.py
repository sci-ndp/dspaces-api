#!/usr/bin/env python3
"""
Demonstration of the Generic CSV API usage.
Shows URL-based data ingestion and flexible filtering features.
"""


# Assuming we're using the API models directly for demonstration
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.models.dspaces_model import (
    CSVDatasetAggregateRequest,
    CSVDatasetFilterRequest,
)


def demo_generic_csv_functionality():
    """Demonstrate the Generic CSV API functionality."""
    
    print("🔄 Generic CSV API Demo")
    print("=" * 50)
    
    # Generic CSV filter request using URL-ingested data
    filter_request = CSVDatasetFilterRequest(
        date_from="2016-01-01",
        date_to="2016-12-31",
        custom_filters={
            "Parameter Name": ["Ozone"],
            "State Code": "49",  # Utah
            "Sample Measurement": {"min": 0.0, "max": 0.1}
        },
        limit=100
    )
    
    print("✅ Generic CSV Filter Request:")
    print(f"   Date Range: {filter_request.date_from} to {filter_request.date_to}")
    print(f"   Custom Filters: {filter_request.custom_filters}")
    print(f"   Limit: {filter_request.limit}")
    
    # Generic CSV aggregate request
    aggregate_request = CSVDatasetAggregateRequest(
        group_by=["Parameter Name", "County Code"],
        aggregations=["mean", "max", "min", "count"],
        custom_filters={"Parameter Name": ["Ozone", "PM2.5"]},
        aggregation_column="Sample Measurement"
    )
    
    print("\n✅ Old Salt Lake Aggregate Request:")
    print(f"   Group By: {old_aggregate.group_by}")
    
    print(f"   Aggregations: {aggregate_request.aggregations}")
    print(f"   Custom Filters: {aggregate_request.custom_filters}")
    print(f"   Aggregation Column: {aggregate_request.aggregation_column}")
    
    print("\n📡 Generic API Calls (URL-based datasets only):")
    print("   POST /retrieve/{dataset_type}/my_namespace/filter")
    print("   POST /retrieve/{dataset_type}/my_namespace/aggregate")
    
def demo_new_generic_features():
    """Demonstrate the new generic CSV API features."""
    
    print("\n\n🆕 New Generic API Features Demo")
    print("=" * 50)
    
    # 1. Custom Filters - Much more flexible than before
    print("1️⃣ Custom Filters (New Feature)")
    
    air_quality_filter = CSVDatasetFilterRequest(
        custom_filters={
            # Single value filter
            "State Code": "06",  # California
            
            # Multiple value filter  
            "Parameter Name": ["Ozone", "PM2.5", "NO2"],
            
            # Range filter for numeric data
            "Sample Measurement": {"min": 0.0, "max": 50.0},
            
            # Geographic range filter
            "Latitude": {"min": 34.0, "max": 37.0},
            "Longitude": {"min": -122.0, "max": -118.0},
            
            # Site-specific filter
            "Site Num": ["1", "5", "10"]
        },
        date_from="2016-06-01",
        date_to="2016-08-31",
        limit=500
    )
    
    print(f"   ✨ Custom Filters: {len(air_quality_filter.custom_filters)} different filter types")
    for key, value in air_quality_filter.custom_filters.items():
        if isinstance(value, dict):
            print(f"      📊 {key}: Range {value['min']} to {value['max']}")
        elif isinstance(value, list):
            print(f"      📋 {key}: {len(value)} values {value[:2]}{'...' if len(value) > 2 else ''}")
        else:
            print(f"      🎯 {key}: {value}")
    
    # 2. Configurable Aggregation Column
    print("\n2️⃣ Configurable Aggregation Column (New Feature)")
    
    weather_aggregate = CSVDatasetAggregateRequest(
        group_by=["Station ID", "Month"],
        aggregations=["mean", "min", "max", "std"],
        aggregation_column="Temperature",  # Not hardcoded to "Sample Measurement"!
        custom_filters={
            "Region": ["North", "Central"],
            "Temperature": {"min": -10.0, "max": 40.0}
        }
    )
    
    print(f"   🌡️  Aggregation Column: '{weather_aggregate.aggregation_column}'")
    print(f"   📊 Group By: {weather_aggregate.group_by}")
    print(f"   🧮 Aggregations: {weather_aggregate.aggregations}")
    print(f"   🔍 Custom Filters: {len(weather_aggregate.custom_filters)} filters applied")
    
    # 3. Multiple Dataset Types
    print("\n3️⃣ Multiple Dataset Types (New Feature)")
    
    dataset_examples = [
        {
            "type": "air-quality",
            "description": "EPA Air Quality monitoring data",
            "sample_filters": {"Parameter Name": ["Ozone", "PM2.5"], "State Code": "06"}
        },
        {
            "type": "weather-stations", 
            "description": "National Weather Service station data",
            "sample_filters": {"Station Type": ["ASOS", "AWOS"], "Temperature": {"min": 0, "max": 35}}
        },
        {
            "type": "environmental-monitoring",
            "description": "Multi-parameter environmental sensor data", 
            "sample_filters": {"Sensor Type": ["Water Quality", "Soil"], "Location": "Urban"}
        },
        {
            "type": "traffic-sensors",
            "description": "Traffic volume and speed monitoring",
            "sample_filters": {"Highway": ["I-80", "US-101"], "Volume": {"min": 1000, "max": 50000}}
        }
    ]
    
    for i, dataset in enumerate(dataset_examples, 1):
        print(f"   {i}. {dataset['type']}")
        print(f"      📝 {dataset['description']}")
        print(f"      🔗 POST /ingest/{dataset['type']}")
        print(f"      🔗 POST /retrieve/{dataset['type']}/my_namespace/filter")
        print(f"      🔗 POST /retrieve/{dataset['type']}/my_namespace/aggregate")
        
        # Show sample request for this dataset type
        sample_request = CSVDatasetFilterRequest(
            custom_filters=dataset['sample_filters'],
            limit=100
        )
        print(f"      🎯 Sample filters: {sample_request.custom_filters}")
        print()

def demo_api_endpoints():
    """Show the new flexible API endpoint patterns."""
    
    print("4️⃣ New Flexible API Endpoints")
    print("   📍 Pattern: /retrieve/{dataset_type}/{namespace}/{operation}")
    print()
    
    endpoints = [
        "POST /ingest/{dataset_type}                  # Generic ingestion",
        "POST /ingest/air-quality                   # New dataset type",
        "POST /ingest/weather-stations              # Another dataset",
        "",
        "GET  /retrieve/{dataset_type}/{namespace}/filter  # Generic filtering", 
        "POST /retrieve/air-quality/ns/filter       # New generic filtering",
        "POST /retrieve/weather-stations/ns/filter  # Works with any dataset",
        "",
        "POST /retrieve/{dataset_type}/{namespace}/aggregate  # Generic aggregation",
        "POST /retrieve/air-quality/ns/aggregate       # New generic aggregation", 
        "POST /retrieve/environmental-data/ns/aggregate # Configurable agg column",
        "",
        "GET  /ingest/{dataset_type}/sample          # Generic sample data",
        "GET  /ingest/air-quality/sample               # New dataset sample",
        "GET  /ingest/weather-stations/sample          # Any dataset sample"
    ]
    
    for endpoint in endpoints:
        if endpoint:
            print(f"   {endpoint}")
        else:
            print()

def demo_migration_path():
    """Show how to use the generic CSV API with URL-based datasets."""
    
    print("\n📈 URL-Based Dataset Usage")
    print("=" * 50)
    
    print("🔄 STEP 1: Ingest data from URLs only")
    print("   All datasets must be ingested from external URLs!")
    print()
    
    print("🆕 STEP 2: Use generic CSV API for all operations")
    print()
    
    # Show the URL-based approach
    print("   URL-based data ingestion:")
    url_ingestion = """
   # First ingest data from URL
   POST /ingest/{dataset_type}
   {
       "url": "https://example.com/data.csv",
       "namespace": "my_namespace"
   }
   """
    print(url_ingestion)
    
    print("   Generic filtering approach:")
    new_way = """
   filter_request = CSVDatasetFilterRequest(
       custom_filters={
           "Parameter Name": ["Ozone", "PM2.5"],    # Multiple parameters
           "State Code": "49",
           "County Code": ["035", "049"],            # Multiple counties  
           "Sample Measurement": {"min": 0.0, "max": 0.1},
           "Elevation": {"min": 1000, "max": 2000"} # Flexible filter types
       }
   )
   # POST /retrieve/{dataset_type}/my_namespace/filter
   """
    print(new_way)
    
    print("🎯 STEP 3: Support multiple dataset types from URLs")
    expansion_example = """
   # Add air quality data from external source
   POST /ingest/air-quality
   POST /retrieve/air-quality/california_data/filter
   
   # Add weather monitoring from URL
   POST /ingest/weather-stations
   POST /retrieve/weather-stations/noaa_data/aggregate
   
   # Add environmental sensors from URL
   POST /ingest/environmental-monitoring  
   POST /retrieve/environmental-monitoring/sensor_net/filter
   """
    print(expansion_example)

if __name__ == "__main__":
    print("🚀 Generic CSV API Demonstration")
    print("=" * 60)
    print("URL-based data ingestion with flexible filtering")
    print("=" * 60)
    
    try:
        demo_generic_csv_functionality()
        demo_new_generic_features() 
        demo_api_endpoints()
        demo_migration_path()
        
        print("\n" + "=" * 60)
        print("✅ Generic CSV API Successfully Demonstrated!")
        print("\n🎉 Key Benefits:")
        print("   • URL-based data ingestion only (no default datasets)")
        print("   • Flexible custom filters support multiple data types")  
        print("   • Configurable aggregation columns (not hardcoded)")
        print("   • Support for unlimited dataset types from URLs")
        print("   • Clean, extensible architecture")
        print("   • No embedded or default datasets")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)
