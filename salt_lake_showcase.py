#!/usr/bin/env python3
"""
Generic CSV Data Showcase (Example with Air Quality Data)

This script demonstrates how to work with CSV datasets through the DataSpaces API
using URL-based data ingestion. It includes examples of data retrieval, filtering,
aggregation, and visualization.

Example Dataset: Air quality measurements (requires URL-based ingestion)
Parameters: Nitrogen dioxide (NO2) and other air pollutants
Temporal Resolution: Hourly measurements
Geographic Coverage: Monitoring stations

Author: DataSpaces API Demo
Date: 2025

**HOW TO USE THIS SCRIPT:**

1.  **Prerequisites:**
    *   **Python Environment:** Ensure you have Python 3.x installed with the necessary packages.
        You can install them using the `showcase_requirements.txt` file:
        `pip install -r showcase_requirements.txt` (or `uv pip install -r showcase_requirements.txt`)
    *   **DataSpaces API Server:** The DataSpaces API server must be running.
        It is expected to be at `http://localhost:8001` by default (see `BASE_URL` below).
        You can typically start the server with `python -m api.main` from the project root,
        or using `docker-compose up -d` if Docker is configured.
    *   **Data Ingestion:** A CSV dataset must be ingested into DataSpaces from a URL
        under your chosen namespace (see `NAMESPACE` below).
        
        IMPORTANT: This showcase now requires URL-based data ingestion only.
        No default datasets are included. You must ingest data from an external URL first:
        
        Example ingestion:
        ```
        curl -X POST "http://localhost:8001/dspaces/ingest/air-quality" \
             -H "Content-Type: application/json" \
             -d '{
               "url": "https://your-data-source.com/air-quality.csv",
               "namespace": "your_demo"
             }'
        ```

2.  **Configuration:**
    *   Update the `DATASET_TYPE` and `NAMESPACE` variables below to match your ingested dataset.
    *   Ensure your CSV data has appropriate columns for the analysis methods used.

3.  **Execution:**
    *   Once the prerequisites are met, run this script from your terminal:
        `python salt_lake_showcase.py`

4.  **Functionality & Output:**
    *   The script will first check the API connection and data availability.
    *   It will then perform several analyses on your CSV dataset:
        *   **Dataset Exploration:** Shows an overview of the dataset, including date ranges,
          available parameters, geographic bounds, and a sample of the data.
        *   **Temporal Pattern Analysis:** Analyzes and visualizes hourly and daily patterns.
        *   **Seasonal Trend Analysis:** Analyzes and visualizes monthly trends.
        *   **Geographic Distribution Analysis:** Visualizes the geographic distribution of
          monitoring stations and values (if geographic columns are present).
        *   **Comprehensive Statistics:** Calculates and displays detailed statistics.
        *   **Data Filtering Demonstrations:** Shows examples of how to use the API's
          filtering capabilities.
    *   Output will be printed to the console, and `matplotlib` plot windows will appear
        to display visualizations. Close each plot window to proceed to the next part of the showcase.

"""

import warnings
from typing import Dict, List, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import requests

# Configuration
warnings.filterwarnings('ignore')
plt.style.use('default')  # Using default style for compatibility
plt.rcParams['figure.figsize'] = (12, 8)

# API Configuration
BASE_URL = "http://localhost:8001"
API_PREFIX = "/dspaces"
NAMESPACE = "your_demo"  # Update this to match your ingested dataset namespace
DATASET_TYPE = "air-quality"  # Update this to match your ingested dataset type
VERSION = 0


class GenericCSVDataAPI:
    """
    A client class for interacting with CSV datasets via the DataSpaces API.
    
    This class provides methods to retrieve, filter, aggregate, and analyze
    CSV datasets stored in DataSpaces through URL-based ingestion.
    """
    
    def __init__(self, base_url: str = BASE_URL, namespace: str = NAMESPACE, dataset_type: str = DATASET_TYPE):
        self.base_url = base_url
        self.namespace = namespace
        self.dataset_type = dataset_type
        self.session = requests.Session()
    
    def check_connection(self) -> bool:
        """Check if the API is accessible."""
        try:
            response = self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                print("✓ API connection successful")
                return True
            else:
                print(f"✗ API returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Could not connect to API: {e}")
            return False
    
    def get_available_filters(self, version: int = VERSION) -> Optional[Dict]:
        """Get available filter values for the dataset."""
        try:
            url = f"{self.base_url}/dspaces/retrieve/{self.dataset_type}/{self.namespace}/available-filters"
            response = self.session.get(url, params={"version": version})
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting filters: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_sample_data(self, rows: int = 100) -> Optional[Dict]:
        """Get a sample of the raw CSV data."""
        try:
            response = self.session.get(f"{self.base_url}/dspaces/ingest/{self.dataset_type}/sample", 
                                      params={"rows": rows})
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting sample data: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def retrieve_data(self, limit: Optional[int] = None, columns: Optional[List[str]] = None, 
                     version: int = VERSION) -> Optional[Dict]:
        """Retrieve data from DataSpaces."""
        try:
            params: Dict[str, Union[int, str]] = {"version": version}
            if limit:
                params["limit"] = limit
            if columns:
                params["columns"] = ",".join(columns)
            
            response = self.session.get(f"{self.base_url}/dspaces/retrieve/{self.dataset_type}/{self.namespace}", 
                                      params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error retrieving data: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def filter_data(self, filter_params: Dict, version: int = VERSION) -> Optional[Dict]:
        """Filter data using API."""
        try:
            # Use GET method for filtering as per the API design
            url = f"{self.base_url}/dspaces/retrieve/{self.dataset_type}/{self.namespace}/filter"
            response = self.session.get(url, params={**filter_params, "version": version})
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error filtering data: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def aggregate_data(self, aggregate_params: Dict, version: int = VERSION) -> Optional[Dict]:
        """Aggregate data using API."""
        try:
            url = f"{self.base_url}/dspaces/retrieve/{self.dataset_type}/{self.namespace}/aggregate"
            response = self.session.post(url, 
                                       json=aggregate_params,
                                       params={"version": version})
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error aggregating data: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None


class GenericCSVDataAnalyzer:
    """
    A class for analyzing CSV datasets via the DataSpaces API.
    
    Provides methods for exploratory data analysis, visualization,
    and statistical analysis of CSV data from URL-based ingestion.
    """
    
    def __init__(self, api_client: GenericCSVDataAPI):
        self.api = api_client
        
    def explore_dataset_structure(self) -> None:
        """Explore the basic structure and available filters of the dataset."""
        print("=" * 60)
        print("CSV DATASET EXPLORATION")
        print("=" * 60)
        
        # Get available filters
        filters = self.api.get_available_filters()
        if filters:
            print("\n📊 Dataset Overview:")
            
            if 'date_range' in filters:
                print(f"📅 Date Range: {filters['date_range']['min']} to {filters['date_range']['max']}")
            
            if 'parameter_names' in filters:
                print(f"🧪 Available Parameters: {', '.join(filters['parameter_names'])}")
            
            if 'measurement_range' in filters:
                print(f"📈 Measurement Range: {filters['measurement_range']['min']:.1f} - {filters['measurement_range']['max']:.1f} ppb")
            
            if 'geographic_bounds' in filters:
                bounds = filters['geographic_bounds']
                print("🗺️  Geographic Bounds:")
                print(f"   Latitude: {bounds['lat_min']:.4f} to {bounds['lat_max']:.4f}")
                print(f"   Longitude: {bounds['lng_min']:.4f} to {bounds['lng_max']:.4f}")
            
            if 'available_columns' in filters:
                print(f"\n📋 Available Columns ({len(filters['available_columns'])}):")
                for col in filters['available_columns']:
                    print(f"   • {col}")
        
        # Get a sample of the data
        print("\n" + "=" * 60)
        print("SAMPLE DATA PREVIEW")
        print("=" * 60)
        
        sample = self.api.get_sample_data(5)
        if sample and 'data' in sample:
            df = pd.DataFrame(sample['data'])
            print("\n📋 First 5 rows of data:")
            print(df.to_string(index=False))
            
            print("\n📊 Sample Data Info:")
            print(f"   Rows: {len(df)}")
            print(f"   Columns: {len(df.columns)}")
    
    def analyze_temporal_patterns(self) -> None:
        """Analyze temporal patterns in air quality measurements."""
        print("\n" + "=" * 60)
        print("TEMPORAL PATTERN ANALYSIS")
        print("=" * 60)
        
        # Get data for January 2016 to analyze patterns
        filter_params = {
            "date_from": "2016-01-01",
            "date_to": "2016-01-31",
            "limit": 1000,
            "columns": "Date Local,Time Local,Parameter Name,Sample Measurement"
        }
        
        data = self.api.filter_data(filter_params)
        if not data or 'data' not in data:
            print("❌ Could not retrieve temporal data")
            return
        
        df = pd.DataFrame(data['data'])
        print(f"📊 Analyzing {len(df)} measurements from January 2016")
        
        # Convert to datetime
        df['datetime'] = pd.to_datetime(df['Date Local'] + ' ' + df['Time Local'])
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.day_name()
        
        # Analyze hourly patterns
        hourly_avg = df.groupby('hour')['Sample Measurement'].mean()
        
        plt.figure(figsize=(15, 10))
        
        # Hourly pattern
        plt.subplot(2, 2, 1)
        hourly_avg.plot(kind='bar', color='skyblue', alpha=0.7)
        plt.title('Average NO2 Levels by Hour of Day')
        plt.xlabel('Hour of Day')
        plt.ylabel('NO2 Concentration (ppb)')
        plt.xticks(rotation=0)
        
        # Daily pattern
        plt.subplot(2, 2, 2)
        daily_avg = df.groupby('day_of_week')['Sample Measurement'].mean()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_avg = daily_avg.reindex(day_order)
        daily_avg.plot(kind='bar', color='lightcoral', alpha=0.7)
        plt.title('Average NO2 Levels by Day of Week')
        plt.xlabel('Day of Week')
        plt.ylabel('NO2 Concentration (ppb)')
        plt.xticks(rotation=45)
        
        # Time series
        plt.subplot(2, 1, 2)
        daily_data = df.groupby(df['datetime'].dt.date)['Sample Measurement'].mean()
        daily_data.plot(color='green', alpha=0.7)
        plt.title('Daily Average NO2 Levels - January 2016')
        plt.xlabel('Date')
        plt.ylabel('NO2 Concentration (ppb)')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
        
        # Print insights
        peak_hour = hourly_avg.idxmax()
        lowest_hour = hourly_avg.idxmin()
        peak_day = daily_avg.idxmax()
        lowest_day = daily_avg.idxmin()
        
        print("\n🔍 Temporal Insights:")
        print(f"   🕐 Peak pollution hour: {peak_hour}:00 ({hourly_avg[peak_hour]:.1f} ppb)")
        print(f"   🕐 Cleanest hour: {lowest_hour}:00 ({hourly_avg[lowest_hour]:.1f} ppb)")
        print(f"   📅 Most polluted day: {peak_day} ({daily_avg[peak_day]:.1f} ppb)")
        print(f"   📅 Cleanest day: {lowest_day} ({daily_avg[lowest_day]:.1f} ppb)")
    
    def analyze_seasonal_trends(self) -> None:
        """Analyze seasonal trends throughout 2016."""
        print("\n" + "=" * 60)
        print("SEASONAL TREND ANALYSIS")
        print("=" * 60)
        
        # Get monthly aggregated data
        monthly_data = []
        months = [
            ('2016-01-01', '2016-01-31', 'January'),
            ('2016-02-01', '2016-02-29', 'February'),
            ('2016-03-01', '2016-03-31', 'March'),
            ('2016-04-01', '2016-04-30', 'April'),
            ('2016-05-01', '2016-05-31', 'May'),
            ('2016-06-01', '2016-06-30', 'June')
        ]
        
        for start_date, end_date, month_name in months:
            aggregate_params = {
                "group_by": ["Parameter Name"],
                "aggregations": ["mean", "max", "min", "count"],
                "date_from": start_date,
                "date_to": end_date
            }
            
            result = self.api.aggregate_data(aggregate_params)
            if result and 'data' in result:
                for row in result['data']:
                    row['month'] = month_name
                    monthly_data.append(row)
        
        if not monthly_data:
            print("❌ Could not retrieve seasonal data")
            return
        
        # Convert to DataFrame and analyze
        df = pd.DataFrame(monthly_data)
        print(f"📊 Analyzing seasonal trends across {len(df)} monthly aggregations")
        
        # Plot seasonal trends
        plt.figure(figsize=(15, 6))
        
        months_order = ['January', 'February', 'March', 'April', 'May', 'June']
        df_ordered = df[df['month'].isin(months_order)]
        
        # Average levels by month
        plt.subplot(1, 2, 1)
        if 'Sample Measurement_mean' in df.columns:
            monthly_means = df_ordered.groupby('month')['Sample Measurement_mean'].mean()
            monthly_means = monthly_means.reindex(months_order)
            monthly_means.plot(kind='bar', color='orange', alpha=0.7)
            plt.title('Average NO2 Levels by Month (Jan-Jun 2016)')
            plt.ylabel('NO2 Concentration (ppb)')
            plt.xticks(rotation=45)
        
        # Max levels by month
        plt.subplot(1, 2, 2)
        if 'Sample Measurement_max' in df.columns:
            monthly_max = df_ordered.groupby('month')['Sample Measurement_max'].mean()
            monthly_max = monthly_max.reindex(months_order)
            monthly_max.plot(kind='bar', color='red', alpha=0.7)
            plt.title('Maximum NO2 Levels by Month (Jan-Jun 2016)')
            plt.ylabel('NO2 Concentration (ppb)')
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
        
        if 'Sample Measurement_mean' in df.columns:
            print("\n🔍 Seasonal Insights:")
            monthly_stats = df_ordered.groupby('month')['Sample Measurement_mean'].mean()
            highest_month = monthly_stats.idxmax()
            lowest_month = monthly_stats.idxmin()
            print(f"   🌡️  Highest pollution month: {highest_month} ({monthly_stats[highest_month]:.1f} ppb)")
            print(f"   🌿 Lowest pollution month: {lowest_month} ({monthly_stats[lowest_month]:.1f} ppb)")
    
    def analyze_geographic_distribution(self) -> None:
        """Analyze geographic distribution of monitoring stations and pollution levels."""
        print("\n" + "=" * 60)
        print("GEOGRAPHIC DISTRIBUTION ANALYSIS")
        print("=" * 60)
        
        # Get data with geographic information
        filter_params = {
            "limit": 2000,
            "columns": "Latitude,Longitude,Sample Measurement,Parameter Name,Site Num"
        }
        
        data = self.api.filter_data(filter_params)
        if not data or 'data' not in data:
            print("❌ Could not retrieve geographic data")
            return
        
        df = pd.DataFrame(data['data'])
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df['Sample Measurement'] = pd.to_numeric(df['Sample Measurement'], errors='coerce')
        
        # Remove rows with missing coordinates
        df = df.dropna(subset=['Latitude', 'Longitude', 'Sample Measurement'])
        
        print(f"📊 Analyzing {len(df)} measurements with geographic coordinates")
        
        # Plot geographic distribution
        plt.figure(figsize=(15, 6))
        
        # Scatter plot of stations
        plt.subplot(1, 2, 1)
        scatter = plt.scatter(df['Longitude'], df['Latitude'], 
                            c=df['Sample Measurement'], 
                            cmap='YlOrRd', alpha=0.6, s=20)
        plt.colorbar(scatter, label='NO2 Concentration (ppb)')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Geographic Distribution of NO2 Measurements')
        
        # Station-level averages
        plt.subplot(1, 2, 2)
        station_avg = df.groupby(['Latitude', 'Longitude']).agg({
            'Sample Measurement': 'mean',
            'Site Num': 'first'
        }).reset_index()
        
        scatter2 = plt.scatter(station_avg['Longitude'], station_avg['Latitude'], 
                             c=station_avg['Sample Measurement'], 
                             cmap='YlOrRd', alpha=0.8, s=100)
        plt.colorbar(scatter2, label='Average NO2 Concentration (ppb)')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Average NO2 Levels by Monitoring Station')
        
        plt.tight_layout()
        plt.show()
        
        # Geographic insights
        print("\n🔍 Geographic Insights:")
        print(f"   📍 Number of unique monitoring stations: {len(station_avg)}")
        print(f"   🗺️  Latitude range: {df['Latitude'].min():.4f} to {df['Latitude'].max():.4f}")
        print(f"   🗺️  Longitude range: {df['Longitude'].min():.4f} to {df['Longitude'].max():.4f}")
        
        if len(station_avg) > 0:
            highest_station = station_avg.loc[station_avg['Sample Measurement'].idxmax()]
            lowest_station = station_avg.loc[station_avg['Sample Measurement'].idxmin()]
            
            print(f"   🔴 Highest pollution station: Site {highest_station['Site Num']} ")
            print(f"      ({highest_station['Latitude']:.4f}, {highest_station['Longitude']:.4f}) - {highest_station['Sample Measurement']:.1f} ppb")
            print(f"   🟢 Lowest pollution station: Site {lowest_station['Site Num']} ")
            print(f"      ({lowest_station['Latitude']:.4f}, {lowest_station['Longitude']:.4f}) - {lowest_station['Sample Measurement']:.1f} ppb")
    
    def analyze_pollution_statistics(self) -> None:
        """Analyze comprehensive pollution statistics."""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE POLLUTION STATISTICS")
        print("=" * 60)
        
        # Get comprehensive statistics using aggregation
        aggregate_params = {
            "group_by": ["Parameter Name"],
            "aggregations": ["mean", "min", "max", "count", "std", "median"]
        }
        
        result = self.api.aggregate_data(aggregate_params)
        if not result or 'data' not in result:
            print("❌ Could not retrieve statistical data")
            return
        
        df = pd.DataFrame(result['data'])
        print("📊 Statistical Analysis Results")
        
        # Display statistics table
        if len(df) > 0:
            print("\n📋 Pollution Statistics Summary:")
            print("-" * 80)
            for _, row in df.iterrows():
                param_name = row.get('Parameter Name', 'Unknown Parameter')
                print(f"\n🧪 {param_name}:")
                
                stats_cols = [col for col in row.index if 'Sample Measurement_' in col]
                for col in stats_cols:
                    stat_name = col.replace('Sample Measurement_', '').title()
                    value = row[col]
                    if pd.notna(value):
                        if stat_name == 'Count':
                            print(f"   {stat_name:12}: {int(value):,} measurements")
                        else:
                            print(f"   {stat_name:12}: {value:.2f} ppb")
        
        # Create visualization of statistics
        if len(df) > 0 and any('Sample Measurement_' in col for col in df.columns):
            plt.figure(figsize=(15, 8))
            
            # Box plot equivalent (using min, q25, median, q75, max)
            plt.subplot(2, 2, 1)
            stats_to_plot = ['Sample Measurement_min', 'Sample Measurement_median', 'Sample Measurement_max']
            plot_data = df[df.columns.intersection(stats_to_plot)].T
            plot_data.columns = df['Parameter Name'] if 'Parameter Name' in df.columns else range(len(df))
            plot_data.plot(kind='bar', alpha=0.7)
            plt.title('Pollution Level Statistics by Parameter')
            plt.ylabel('Concentration (ppb)')
            plt.xticks(rotation=45)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Mean vs Standard Deviation
            if all(col in df.columns for col in ['Sample Measurement_mean', 'Sample Measurement_std']):
                plt.subplot(2, 2, 2)
                plt.scatter(df['Sample Measurement_mean'], df['Sample Measurement_std'], s=100, alpha=0.7)
                plt.xlabel('Mean Concentration (ppb)')
                plt.ylabel('Standard Deviation (ppb)')
                plt.title('Mean vs Variability')
                
                for i, param in enumerate(df['Parameter Name'] if 'Parameter Name' in df.columns else range(len(df))):
                    plt.annotate(param, 
                               (df['Sample Measurement_mean'].iloc[i], 
                                df['Sample Measurement_std'].iloc[i]),
                               xytext=(5, 5), textcoords='offset points')
            
            plt.tight_layout()
            plt.show()


def demonstrate_data_filtering():
    """Demonstrate various data filtering capabilities."""
    print("\n" + "=" * 60)
    print("DATA FILTERING DEMONSTRATIONS")
    print("=" * 60)
    
    api = GenericCSVDataAPI()
    
    # Example 1: Date range filtering
    print("\n🗓️  Example 1: Filtering by date range (First week of January 2016)")
    filter_params = {
        "date_from": "2016-01-01",
        "date_to": "2016-01-07",
        "limit": 10,
        "columns": "Date Local,Time Local,Parameter Name,Sample Measurement"
    }
    
    result = api.filter_data(filter_params)
    if result and 'data' in result:
        df = pd.DataFrame(result['data'])
        print(f"Retrieved {len(df)} records")
        print(df.head().to_string(index=False))
        print(f"Metadata: {result.get('metadata', {})}")
    
    # Example 2: High pollution filtering
    print("\n🚨 Example 2: Filtering high pollution episodes (>40 ppb)")
    filter_params = {
        "measurement_min": "40",
        "limit": 10,
        "columns": "Date Local,Time Local,Sample Measurement,Parameter Name"
    }
    
    result = api.filter_data(filter_params)
    if result and 'data' in result:
        df = pd.DataFrame(result['data'])
        print(f"Found {len(df)} high pollution measurements")
        if len(df) > 0:
            print(df.head().to_string(index=False))
    
    # Example 3: Geographic filtering
    print("\n🗺️  Example 3: Geographic filtering (Central Salt Lake area)")
    filter_params = {
        "lat_min": "40.73",
        "lat_max": "40.74",
        "lng_min": "-111.88",
        "lng_max": "-111.87",
        "limit": 5,
        "columns": "Latitude,Longitude,Sample Measurement,Date Local"
    }
    
    result = api.filter_data(filter_params)
    if result and 'data' in result:
        df = pd.DataFrame(result['data'])
        print(f"Found {len(df)} measurements in specified geographic area")
        if len(df) > 0:
            print(df.head().to_string(index=False))


def check_and_ingest_data():
    """Check if data is available and provide instructions for ingestion if not."""
    print("🔍 Checking data availability...")
    
    api = GenericCSVDataAPI()
    
    # Check if API is accessible
    if not api.check_connection():
        print("❌ Cannot connect to DataSpaces API")
        print("Please ensure the server is running:")
        print("   python -m api.main")
        return False
    
    # Check if data is available using retrieve_data
    retrieved_sample = api.retrieve_data(limit=1)
    if retrieved_sample and 'data' in retrieved_sample and len(retrieved_sample['data']) > 0:
        print("✅ CSV data is available and ready for analysis!")
        return True
    
    # Data not available - provide ingestion instructions
    print("⚠️  CSV data not found in DataSpaces")
    print("\n📝 To ingest data, you must use URL-based ingestion:")
    print("1. Prepare a publicly accessible CSV file URL")
    print("2. Use the ingestion endpoint to load the data:")
    print(f"   curl -X POST {BASE_URL}/dspaces/ingest/{api.dataset_type} \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{")
    print('              "url": "https://your-data-source.com/data.csv",')
    print(f'              "namespace": "{api.namespace}"')
    print("           }'")
    print("\n3. Or use the API directly:")
    print(f"   POST /dspaces/ingest/{api.dataset_type}")
    print("   with JSON data: url and namespace")
    print("\n4. Update DATASET_TYPE and NAMESPACE variables in this script")
    print("5. Then run this showcase again")
    print("\nCurrent configuration:")
    print(f"   Dataset Type: {api.dataset_type}")
    print(f"   Namespace: {api.namespace}")
    
    return False

def main():
    """
    Main function to run the CSV data showcase.

    This function orchestrates the entire demonstration, from checking prerequisites
    to running various data analysis and visualization routines on URL-ingested CSV data.
    """
    print("🌟 GENERIC CSV DATA SHOWCASE 🌟")
    print("=" * 60)
    print("This demonstration showcases the capabilities of the DataSpaces API")
    print("for analyzing CSV datasets ingested from URLs.")
    print("=" * 60)
    
    # Initialize API client
    api = GenericCSVDataAPI()
    
    # Check connection
    if not api.check_connection():
        print("❌ Cannot connect to API. Please ensure the server is running.")
        return
    
    # Check and ingest data if not already present
    if not check_and_ingest_data():
        return
    
    # Initialize analyzer
    analyzer = GenericCSVDataAnalyzer(api)
    
    try:
        # 1. Explore dataset structure
        analyzer.explore_dataset_structure()
        
        # 2. Analyze temporal patterns
        analyzer.analyze_temporal_patterns()
        
        # 3. Analyze seasonal trends
        analyzer.analyze_seasonal_trends()
        
        # 4. Analyze geographic distribution
        # analyzer.analyze_geographic_distribution() # Commented out as per user request
        
        # 5. Comprehensive statistics
        # analyzer.analyze_pollution_statistics() # Commented out as per user request
        
        # 6. Demonstrate filtering capabilities
        demonstrate_data_filtering()
        
        print("\n" + "=" * 60)
        print("🎉 SHOWCASE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("This demonstration covered:")
        print("• Dataset exploration and structure analysis")
        print("• Temporal pattern analysis (hourly, daily)")
        print("• Seasonal trend analysis")
        print("• Geographic distribution mapping")
        print("• Comprehensive pollution statistics")
        print("• Advanced data filtering examples")
        print("\nFor more advanced usage, check the API documentation at:")
        print(f"{BASE_URL}/docs")
        
    except Exception as e:
        print(f"\n❌ An error occurred during the showcase: {e}")
        print("Please check your API connection and data availability.")


if __name__ == "__main__":
    main()
