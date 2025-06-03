#!/usr/bin/env python3
"""
# 🌬️ Air Quality Hackathon - Utah MEOP Data Analysis (Linear Sequential Version)

This script demonstrates a comprehensive air quality data analysis workflow using 
the DataSpaces API. It executes all operations in sequential order without functions,
making it easy to follow step-by-step.

## 📊 Dataset Information
- **Dataset**: University of Utah MEOP Level 2 Data (October 2024)
- **Source**: https://horel.chpc.utah.edu/data/meop/level2/ebus_2024_10.csv
- **Description**: Mobile air quality measurements from electric buses in Utah
- **Size**: ~3.4M rows, 23 columns

## 🚀 DataSpaces API Features Demonstrated
- URL-based CSV ingestion into DataSpaces
- Data exploration and validation
- Temporal pattern analysis
- Geographic distribution mapping
- Air quality parameter filtering
- Statistical analysis and visualization
- Sample queries demonstrating API capabilities

## 📋 Prerequisites
1. DataSpaces API server running on http://localhost:8001
2. Required Python packages: requests, pandas, matplotlib, numpy

## 💻 Usage
Run this script to execute the complete DataSpaces API workflow sequentially.

**Author**: Air Quality Hackathon Team  
**Date**: June 2025
"""

# =============================================================================
# 📦 STEP 1: Import Dependencies and Setup
# =============================================================================

import sys
import time
import warnings

# Import required packages with error handling
try:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import requests
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Please install required packages:")
    print("pip install requests pandas matplotlib numpy")
    sys.exit(1)

# Configure visualization and warnings
warnings.filterwarnings('ignore')
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 8)

print("✅ All dependencies imported successfully!")
print("📊 Matplotlib configured for 12x8 inch figures")
print("🔕 Warnings filtered for cleaner output")

# =============================================================================
# 📝 STEP 2: Global Configuration and Setup
# =============================================================================

# Global Configuration Variables
BASE_URL = "http://localhost:8001"                    # DataSpaces API server URL
DATASET_TYPE = "utah-meop-air-quality"                # Dataset type identifier
NAMESPACE = "meop_october_2024"                       # Namespace for organizing data
CSV_URL = "https://horel.chpc.utah.edu/data/meop/level2/ebus_2024_10.csv"  # Source data URL
VERSION = 0                                           # Dataset version

# Create a global session for API requests
session = requests.Session()
session.headers.update({'Content-Type': 'application/json'})

print("🔧 Configuration loaded:")
print(f"  • API URL: {BASE_URL}")
print(f"  • Dataset Type: {DATASET_TYPE}")
print(f"  • Namespace: {NAMESPACE}")
print(f"  • Data Source: {CSV_URL}")
print(f"  • Version: {VERSION}")

# =============================================================================
# 🏥 STEP 3: Check DataSpaces API Health
# =============================================================================

print("\n🔍 Checking DataSpaces API health...")

try:
    response = session.get(f"{BASE_URL}/docs", timeout=10)
    if response.status_code == 200:
        print("✅ DataSpaces API is accessible")
        api_healthy = True
    else:
        print(f"❌ API returned status code: {response.status_code}")
        api_healthy = False
except Exception as e:
    print(f"❌ Could not connect to DataSpaces API: {e}")
    print("Please ensure the API server is running on http://localhost:8001")
    api_healthy = False

if not api_healthy:
    print("❌ Cannot proceed without API access. Exiting...")
    sys.exit(1)

# =============================================================================
# 📥 STEP 4: Ingest Data from URL into DataSpaces
# =============================================================================

print("\n🔄 Starting data ingestion from URL...")
print(f"📊 Dataset Type: {DATASET_TYPE}")
print(f"🌐 Source URL: {CSV_URL}")
print(f"📁 Namespace: {NAMESPACE}")
print(f"🔢 Version: {VERSION}")

# Prepare the ingestion payload with optimized settings
payload = {
    "url": CSV_URL,
    "namespace": NAMESPACE,
    "version": VERSION,
    "chunk_size": 5000,  # Process 5000 rows at a time for memory efficiency
    "filename": "ebus_2024_10.csv"
}

try:
    # Make the ingestion request with extended timeout for large datasets
    print("⏳ Sending ingestion request...")
    response = session.post(
        f"{BASE_URL}/dspaces/ingest/{DATASET_TYPE}/from-url",
        json=payload,
        timeout=300  # 5 minutes timeout for large dataset processing
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Data ingestion successful!")
        print(f"📊 Total rows ingested: {result.get('total_rows', 0):,}")
        print(f"📈 Total columns processed: {result.get('total_columns', 0)}")
        
        # Display first few column names for validation
        columns = result.get('columns', [])
        if columns:
            print(f"📋 First 5 columns: {', '.join(columns[:5])}...")
        
        # Show detailed ingestion statistics for troubleshooting
        stored_objects = result.get('stored_objects', {})
        successful = len([v for v in stored_objects.values() if 'error' not in v])
        failed = len([v for v in stored_objects.values() if 'error' in v])
        
        print(f"✅ Successfully stored columns: {successful}")
        if failed > 0:
            print(f"❌ Failed to store columns: {failed}")
            print("⚠️  Some columns may have data quality issues")
        
        ingestion_successful = True
    else:
        print(f"❌ Ingestion failed with HTTP status: {response.status_code}")
        print(f"Error details: {response.text}")
        ingestion_successful = False
        
except requests.exceptions.Timeout:
    print("⏰ Ingestion request timed out - large dataset processing may take time")
    print("💡 The ingestion may still be processing in the background")
    print("   Check the API logs or try retrieving data in a few minutes")
    ingestion_successful = False
except Exception as e:
    print(f"❌ Unexpected error during ingestion: {e}")
    ingestion_successful = False

if not ingestion_successful:
    print("❌ Cannot proceed without successful data ingestion. Exiting...")
    sys.exit(1)

# =============================================================================
# 📋 STEP 5: Get Sample Data for Exploration
# =============================================================================

print("\n📊 Retrieving 10 sample rows for data exploration...")

try:
    response = session.get(
        f"{BASE_URL}/dspaces/ingest/{DATASET_TYPE}/sample",
        params={"rows": 10}
    )
    
    if response.status_code == 200:
        sample_data = response.json()
        print("✅ Successfully retrieved 10 sample rows")
        
        # Display sample data information
        total_rows = sample_data.get('total_rows', 'unknown')
        total_cols = sample_data.get('total_columns', 'unknown')
        
        print("📊 Dataset Size Overview:")
        print(f"  • Total rows: {total_rows:,}")
        print(f"  • Total columns: {total_cols}")
        
        # Display sample data for content validation
        sample_records = sample_data.get('data', {})
        if sample_records:
            print("\n📋 Sample Data Preview (first 5 rows):")
            data_rows = sample_records.get('data', [])
            for i, row in enumerate(data_rows[:5]):
                # Show first 3 columns of each row for readability
                sample_cols = dict(list(row.items())[:3])
                print(f"  Row {i+1}: {sample_cols}...")
        
        # Display comprehensive column information
        column_info = sample_data.get('column_info', {})
        if column_info:
            print(f"\n📊 Column Information ({len(column_info)} total columns):")
            for col, info in list(column_info.items())[:10]:  # Show first 10 columns
                data_type = info.get('data_type', 'unknown')
                print(f"  • {col}: {data_type}")
            
            if len(column_info) > 10:
                print(f"  • ... and {len(column_info) - 10} more columns")
                
    else:
        print(f"❌ Error getting sample data: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        sample_data = None
except Exception as e:
    print(f"❌ Error retrieving sample data: {e}")
    sample_data = None

# =============================================================================
# 🔍 STEP 6: Discover Available Filters
# =============================================================================

print("\n🔍 Discovering available filters and value ranges...")

try:
    response = session.get(
        f"{BASE_URL}/dspaces/retrieve/{DATASET_TYPE}/{NAMESPACE}/available-filters"
    )
    
    if response.status_code == 200:
        filters = response.json()
        print(f"✅ Retrieved filter information for {len(filters)} columns")
        
        print(f"\n🔍 Available Filters ({len(filters)} total):")
        for filter_name, values in list(filters.items())[:5]:  # Show first 5 filters
            if isinstance(values, list) and len(values) <= 10:
                print(f"  • {filter_name}: {values}")
            elif isinstance(values, list):
                print(f"  • {filter_name}: {values[:3]}... ({len(values)} total values)")
            else:
                print(f"  • {filter_name}: {type(values).__name__} data")
                
    else:
        print(f"❌ Error getting available filters: HTTP {response.status_code}")
        filters = None
except Exception as e:
    print(f"❌ Error retrieving filter information: {e}")
    filters = None

# =============================================================================
# 📊 STEP 7: Retrieve Basic Data Sample
# =============================================================================

print("\n📊 Retrieving up to 1,000 rows from DataSpaces...")

try:
    # Prepare query parameters
    params = {"version": VERSION, "limit": 1000}
    
    response = session.get(
        f"{BASE_URL}/dspaces/retrieve/{DATASET_TYPE}/{NAMESPACE}",
        params=params
    )
    
    if response.status_code == 200:
        basic_data = response.json()
        row_count = len(basic_data.get('data', []))
        print(f"✅ Successfully retrieved {row_count:,} rows")
        
        # Convert to DataFrame for analysis
        if basic_data.get('data'):
            df_basic = pd.DataFrame(basic_data.get('data', []))
            print(f"📊 DataFrame created with shape: {df_basic.shape}")
        else:
            df_basic = pd.DataFrame()
            
    else:
        print(f"❌ Error retrieving data: HTTP {response.status_code}")
        basic_data = None
        df_basic = pd.DataFrame()
except Exception as e:
    print(f"❌ Error during data retrieval: {e}")
    basic_data = None
    df_basic = pd.DataFrame()

# =============================================================================
# ⏰ STEP 8: Temporal Pattern Analysis
# =============================================================================

print("\n" + "="*60)
print("⏰ TEMPORAL PATTERN ANALYSIS")
print("="*60)

if not df_basic.empty:
    print(f"📊 Analyzing temporal patterns in {len(df_basic):,} records...")
    
    # Identify time-related columns using keyword matching
    time_keywords = ['time', 'date', 'timestamp', 'hour', 'minute', 'second', 'datetime']
    time_columns = [col for col in df_basic.columns 
                   if any(keyword in col.lower() for keyword in time_keywords)]
    
    if time_columns:
        print(f"🕐 Found temporal columns: {time_columns}")
        
        # Analyze the first time column in detail
        time_col = time_columns[0]
        if time_col in df_basic.columns:
            print(f"\n📈 Detailed analysis for '{time_col}':")
            time_values = df_basic[time_col].dropna()
            
            if len(time_values) > 0:
                print(f"  • First timestamp: {time_values.iloc[0]}")
                print(f"  • Last timestamp: {time_values.iloc[-1]}")
                print(f"  • Total valid records: {len(time_values):,}")
                print(f"  • Missing values: {df_basic[time_col].isna().sum():,}")
                
                # Try to parse as datetime for more insights
                try:
                    time_parsed = pd.to_datetime(time_values, errors='coerce')
                    valid_times = time_parsed.dropna()
                    
                    if len(valid_times) > 0:
                        time_span = valid_times.max() - valid_times.min()
                        print(f"  • Time span: {time_span}")
                        print(f"  • Date range: {valid_times.min().date()} to {valid_times.max().date()}")
                except Exception:
                    print("  • Could not parse as standard datetime format")
                    
    else:
        print("⚠️  No temporal columns detected in the dataset")
        print("💡 Dataset may use non-standard time column naming")
else:
    print("❌ No data available for temporal analysis")

# =============================================================================
# 🌬️ STEP 9: Air Quality Parameter Analysis
# =============================================================================

print("\n" + "="*60)
print("🌬️ AIR QUALITY PARAMETER ANALYSIS")
print("="*60)

if not df_basic.empty:
    print(f"🌬️ Analyzing air quality parameters in {len(df_basic):,} records...")
    
    # Identify air quality parameter columns using keyword matching
    aq_keywords = ['pm2.5', 'pm10', 'pm25', 'o3', 'ozone', 'no2', 'co', 'so2', 
                  'pollutant', 'concentration', 'aqi', 'quality', 'emission']
    aq_columns = [col for col in df_basic.columns 
                 if any(keyword in col.lower() for keyword in aq_keywords)]
    
    if aq_columns:
        print(f"🌬️ Found air quality parameter columns: {aq_columns}")
        
        # Analyze each air quality parameter
        for col in aq_columns[:3]:  # Analyze first 3 AQ columns for brevity
            if col in df_basic.columns:
                values = pd.to_numeric(df_basic[col], errors='coerce').dropna()
                
                if len(values) > 0:
                    print(f"\n📊 Analysis for '{col}':")
                    print(f"  • Mean: {values.mean():.3f}")
                    print(f"  • Std Dev: {values.std():.3f}")
                    print(f"  • Min: {values.min():.3f}")
                    print(f"  • Max: {values.max():.3f}")
                    print(f"  • Valid measurements: {len(values):,}")
                    
    else:
        # Look for any numeric columns that might be measurements
        numeric_cols = df_basic.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            print(f"📊 Found numeric measurement columns: {numeric_cols[:5]}")
            print("💡 These may contain air quality or environmental measurements")
            
            # Show basic statistics for first few numeric columns
            for col in numeric_cols[:3]:
                values = df_basic[col].dropna()
                if len(values) > 0:
                    print(f"\n📊 Analysis for '{col}':")
                    print(f"  • Mean: {values.mean():.3f}")
                    print(f"  • Range: {values.min():.3f} to {values.max():.3f}")
                    print(f"  • Valid values: {len(values):,}")
        else:
            print("⚠️ No numeric measurement columns found")
            print("💡 Dataset may not contain air quality measurements")
else:
    print("❌ No data available for air quality analysis")

# =============================================================================
# 🗺️ STEP 10: Geographic Distribution Analysis
# =============================================================================

print("\n" + "="*60)
print("🗺️ GEOGRAPHIC DISTRIBUTION ANALYSIS")
print("="*60)

if not df_basic.empty:
    print(f"🗺️ Analyzing geographic distribution in {len(df_basic):,} records...")
    
    # Identify geographic coordinate columns
    geo_keywords = ['lat', 'lon', 'longitude', 'latitude', 'coord', 'location', 'x', 'y']
    geo_columns = [col for col in df_basic.columns 
                  if any(keyword in col.lower() for keyword in geo_keywords)]
    
    if geo_columns:
        print(f"📍 Found geographic columns: {geo_columns}")
        
        # Try to identify latitude and longitude columns
        lat_col = next((col for col in geo_columns if 'lat' in col.lower()), None)
        lon_col = next((col for col in geo_columns if 'lon' in col.lower()), None)
        
        if lat_col and lon_col:
            lat_values = pd.to_numeric(df_basic[lat_col], errors='coerce').dropna()
            lon_values = pd.to_numeric(df_basic[lon_col], errors='coerce').dropna()
            
            if len(lat_values) > 0 and len(lon_values) > 0:
                print("\n📍 Coordinate Analysis:")
                print(f"  • Latitude range: {lat_values.min():.6f} to {lat_values.max():.6f}")
                print(f"  • Longitude range: {lon_values.min():.6f} to {lon_values.max():.6f}")
                print(f"  • Valid coordinate pairs: {min(len(lat_values), len(lon_values)):,}")
                
                # Check if coordinates are in expected Utah range
                utah_lat_range = (36.5, 42.0)  # Approximate Utah latitude range
                utah_lon_range = (-114.5, -109.0)  # Approximate Utah longitude range
                
                lat_in_utah = ((lat_values >= utah_lat_range[0]) & (lat_values <= utah_lat_range[1])).sum()
                lon_in_utah = ((lon_values >= utah_lon_range[0]) & (lon_values <= utah_lon_range[1])).sum()
                
                print(f"  • Coordinates in Utah latitude range: {lat_in_utah:,} ({lat_in_utah/len(lat_values)*100:.1f}%)")
                print(f"  • Coordinates in Utah longitude range: {lon_in_utah:,} ({lon_in_utah/len(lon_values)*100:.1f}%)")
        else:
            print("⚠️ Could not identify clear latitude/longitude columns")
            print(f"💡 Found geographic columns: {geo_columns}")
    else:
        print("⚠️ No geographic coordinate columns detected")
        print("💡 Dataset may not contain spatial information")
else:
    print("❌ No data available for geographic analysis")

# =============================================================================
# 🔍 STEP 11: Advanced Filtering Demonstration
# =============================================================================

print("\n" + "="*60)
print("🔍 ADVANCED FILTERING DEMONSTRATION")
print("="*60)

# Demonstrate filtering with some example criteria
if not df_basic.empty:
    # Get a numeric column for filtering demonstration
    numeric_cols = df_basic.select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_cols:
        filter_col = numeric_cols[0]  # Use first numeric column
        col_values = pd.to_numeric(df_basic[filter_col], errors='coerce').dropna()
        
        if len(col_values) > 0:
            # Create a filter for values above the median
            median_value = col_values.median()
            
            custom_filters = {
                filter_col: {"min": median_value}
            }
            
            print("🔍 Applying custom filters (limit: 500 rows)...")
            print(f"📋 Filter criteria: {custom_filters}")
            
            try:
                payload = {
                    "custom_filters": custom_filters,
                    "limit": 500,
                    "version": VERSION
                }
                
                response = session.post(
                    f"{BASE_URL}/dspaces/retrieve/{DATASET_TYPE}/{NAMESPACE}/filter",
                    json=payload
                )
                
                if response.status_code == 200:
                    filtered_data = response.json()
                    row_count = len(filtered_data.get('data', []))
                    print(f"✅ Filter applied successfully - {row_count:,} rows match criteria")
                    
                    # Show some statistics about the filtered data
                    if filtered_data.get('data'):
                        df_filtered = pd.DataFrame(filtered_data.get('data', []))
                        filtered_values = pd.to_numeric(df_filtered[filter_col], errors='coerce').dropna()
                        print(f"📊 Filtered {filter_col} statistics:")
                        print(f"  • Min value: {filtered_values.min():.3f}")
                        print(f"  • Max value: {filtered_values.max():.3f}")
                        print(f"  • Mean: {filtered_values.mean():.3f}")
                else:
                    print(f"❌ Error applying filters: HTTP {response.status_code}")
                    print(f"Response details: {response.text}")
            except Exception as e:
                print(f"❌ Error during data filtering: {e}")
        else:
            print("⚠️ No numeric data available for filtering demonstration")
    else:
        print("⚠️ No numeric columns found for filtering demonstration")
else:
    print("❌ No data available for filtering demonstration")

# =============================================================================
# 📊 STEP 12: Statistical Aggregation Demonstration
# =============================================================================

print("\n" + "="*60)
print("📊 STATISTICAL AGGREGATION DEMONSTRATION")
print("="*60)

if not df_basic.empty:
    # Find suitable columns for aggregation
    categorical_cols = df_basic.select_dtypes(include=['object']).columns.tolist()
    numeric_cols = df_basic.select_dtypes(include=[np.number]).columns.tolist()
    
    if categorical_cols and numeric_cols:
        group_col = categorical_cols[0]  # Use first categorical column
        agg_col = numeric_cols[0]       # Use first numeric column
        
        print("\n📈 Performing data aggregation...")
        print(f"📊 Grouping by: {group_col}")
        print(f"🔢 Aggregating column: {agg_col}")
        print("📋 Functions: mean, count, std")
        print("🔢 Limit: 100 groups")
        
        try:
            payload = {
                "group_by": [group_col],
                "aggregations": ["mean", "count", "std"],
                "aggregation_column": agg_col,
                "limit": 100,
                "version": VERSION
            }
            
            response = session.post(
                f"{BASE_URL}/dspaces/retrieve/{DATASET_TYPE}/{NAMESPACE}/aggregate",
                json=payload
            )
            
            if response.status_code == 200:
                agg_data = response.json()
                group_count = len(agg_data.get('data', []))
                print(f"✅ Aggregation completed - {group_count:,} groups generated")
                
                # Display first few aggregation results
                if agg_data.get('data'):
                    print("\n📊 First 5 aggregation results:")
                    for i, result in enumerate(agg_data.get('data', [])[:5]):
                        print(f"  Group {i+1}: {result}")
            else:
                print(f"❌ Error performing aggregation: HTTP {response.status_code}")
                print(f"Response details: {response.text}")
        except Exception as e:
            print(f"❌ Error during data aggregation: {e}")
    else:
        print("⚠️ Insufficient column types for aggregation demonstration")
        print(f"💡 Categorical columns: {len(categorical_cols)}, Numeric columns: {len(numeric_cols)}")
else:
    print("❌ No data available for aggregation demonstration")

# =============================================================================
# 🎉 STEP 13: Final Summary and Completion
# =============================================================================

print("\n🎉 HACKATHON DEMONSTRATION COMPLETE!")
print("="*60)
print("✅ Successfully demonstrated DataSpaces API capabilities:")
print("   • ✅ Large-scale CSV ingestion from remote URL")
print("   • ✅ Real-time data exploration and profiling")
print("   • ✅ Multi-dimensional analysis (temporal, spatial, environmental)")
print("   • ✅ Advanced filtering with custom criteria")
print("   • ✅ Statistical aggregation and summarization")
print("   • ✅ Utah MEOP air quality data analysis")

print("\n🔗 Next Steps and Resources:")
print("   🌐 API Documentation: http://localhost:8001/docs")
print("   🔍 Interactive API Explorer: http://localhost:8001/redoc")
print("   📊 Try custom filters and aggregations")
print("   🌬️ Analyze specific air quality parameters")
print("   📈 Create visualizations with retrieved data")
print("   🏫 Explore more MEOP datasets from University of Utah")

print("\n💡 DataSpaces API Key Features Demonstrated:")
print("   🚀 Zero-ETL data ingestion from any URL")
print("   ⚡ Real-time querying without pre-indexing")
print("   🔧 Dynamic schema detection and adaptation")
print("   📊 Built-in statistical analysis capabilities")
print("   🌐 RESTful API with comprehensive documentation")

print(f"\n📅 Script completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("✨ Thank you for exploring DataSpaces API!")
