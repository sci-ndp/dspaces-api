#!/usr/bin/env python3
"""
Demonstration of the Generic CSV API usage.
Shows both backward compatibility and new features.
"""


# Assuming we're using the API models directly for demonstration
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.models.dspaces_model import (
    CSVDatasetAggregateRequest,
    CSVDatasetFilterRequest,
    SaltLakeAggregateRequest,  # Backward compatibility
    SaltLakeFilterRequest,  # Backward compatibility
)


def demo_backward_compatibility():
    """Demonstrate that existing Salt Lake County code still works."""
    
    print("🔄 Backward Compatibility Demo")
    print("=" * 50)
    
    # Existing Salt Lake County filter request (unchanged)
    old_filter = SaltLakeFilterRequest(
        date_from="2016-01-01",
        date_to="2016-12-31",
        parameter_names=["Ozone"],
        state_codes=["49"],  # Utah
        measurement_min=0.0,
        measurement_max=0.1,
        limit=100
    )
    
    print("✅ Old Salt Lake Filter Request:")
    print(f"   Date Range: {old_filter.date_from} to {old_filter.date_to}")
    print(f"   Parameters: {old_filter.parameter_names}")
    print(f"   State Codes: {old_filter.state_codes}")
    print(f"   Measurement Range: {old_filter.measurement_min} - {old_filter.measurement_max}")
    
    # Existing Salt Lake County aggregate request (unchanged)
    old_aggregate = SaltLakeAggregateRequest(
        group_by=["Parameter Name", "County Code"],
        aggregations=["mean", "max", "min", "count"],
        parameter_names=["Ozone", "PM2.5"]
    )
    
    print("\n✅ Old Salt Lake Aggregate Request:")
    print(f"   Group By: {old_aggregate.group_by}")
    print(f"   Aggregations: {old_aggregate.aggregations}")
    print(f"   Parameters: {old_aggregate.parameter_names}")
    
    print("\n📡 API Calls (still work exactly the same):")
    print("   POST /retrieve/salt-lake-county/my_namespace/filter")
    print("   POST /retrieve/salt-lake-county/my_namespace/aggregate")
    
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
        "POST /ingest/salt-lake-county              # Backward compatible",
        "POST /ingest/air-quality                   # New dataset type",
        "POST /ingest/weather-stations              # Another dataset",
        "",
        "GET  /retrieve/salt-lake-county/ns/filter  # Backward compatible", 
        "POST /retrieve/air-quality/ns/filter       # New generic filtering",
        "POST /retrieve/weather-stations/ns/filter  # Works with any dataset",
        "",
        "POST /retrieve/salt-lake-county/ns/aggregate  # Backward compatible",
        "POST /retrieve/air-quality/ns/aggregate       # New generic aggregation", 
        "POST /retrieve/environmental-data/ns/aggregate # Configurable agg column",
        "",
        "GET  /ingest/salt-lake-county/sample          # Backward compatible",
        "GET  /ingest/air-quality/sample               # New dataset sample",
        "GET  /ingest/weather-stations/sample          # Any dataset sample"
    ]
    
    for endpoint in endpoints:
        if endpoint:
            print(f"   {endpoint}")
        else:
            print()

def demo_migration_path():
    """Show how to migrate from old API to new API."""
    
    print("\n📈 Migration Path from Old to New API")
    print("=" * 50)
    
    print("🔄 STEP 1: No changes needed - Backward compatibility")
    print("   Your existing Salt Lake County code works unchanged!")
    print()
    
    print("🆕 STEP 2: Optionally adopt new features when beneficial")
    print()
    
    # Show equivalent old vs new
    print("   Old Salt Lake specific approach:")
    old_way = """
   filter_request = SaltLakeFilterRequest(
       parameter_names=["Ozone"],
       state_codes=["49"], 
       county_codes=["035"],
       measurement_min=0.0,
       measurement_max=0.1
   )
   # POST /retrieve/salt-lake-county/my_ns/filter
   """
    print(old_way)
    
    print("   New generic approach (more flexible):")
    new_way = """
   filter_request = CSVDatasetFilterRequest(
       custom_filters={
           "Parameter Name": ["Ozone", "PM2.5"],    # Multiple parameters
           "State Code": "49",
           "County Code": ["035", "049"],            # Multiple counties  
           "Sample Measurement": {"min": 0.0, "max": 0.1},
           "Elevation": {"min": 1000, "max": 2000"} # New filter types!
       }
   )
   # POST /retrieve/salt-lake-county/my_ns/filter  (same endpoint)
   # POST /retrieve/air-quality/my_ns/filter       (new dataset types)
   """
    print(new_way)
    
    print("🎯 STEP 3: Adopt new dataset types when expanding")
    expansion_example = """
   # Add air quality data from other states
   POST /ingest/air-quality
   POST /retrieve/air-quality/california_data/filter
   
   # Add weather monitoring  
   POST /ingest/weather-stations
   POST /retrieve/weather-stations/noaa_data/aggregate
   
   # Add environmental sensors
   POST /ingest/environmental-monitoring  
   POST /retrieve/environmental-monitoring/sensor_net/filter
   """
    print(expansion_example)

if __name__ == "__main__":
    print("🚀 Generic CSV API Demonstration")
    print("=" * 60)
    print("Showing backward compatibility + powerful new features")
    print("=" * 60)
    
    try:
        demo_backward_compatibility()
        demo_new_generic_features() 
        demo_api_endpoints()
        demo_migration_path()
        
        print("\n" + "=" * 60)
        print("✅ Generic CSV API Successfully Demonstrated!")
        print("\n🎉 Key Benefits:")
        print("   • 100% backward compatible with existing Salt Lake County code")
        print("   • Flexible custom filters support multiple data types")  
        print("   • Configurable aggregation columns (not hardcoded)")
        print("   • Support for unlimited dataset types")
        print("   • Clean, extensible architecture")
        print("   • Zero breaking changes for existing users")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)
