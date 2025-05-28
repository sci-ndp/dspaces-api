# Salt Lake City Air Quality Data Showcase

This Python script demonstrates how to work with the Salt Lake County air quality dataset through the DataSpaces API. It showcases various data analysis capabilities including filtering, aggregation, and visualization.

## Dataset Information

The dataset contains hourly air quality measurements from monitoring stations in Salt Lake County, Utah for the year 2016, including:

- **Nitrogen dioxide (NO2)** measurements in parts per billion (ppb)
- **Temporal data**: Date and time of measurements
- **Geographic data**: Latitude and longitude coordinates
- **Metadata**: State codes, county codes, site numbers, measurement methods

## Features Demonstrated

### 1. Dataset Exploration
- Overview of available data and filters
- Sample data preview
- Column information and data structure

### 2. Temporal Analysis
- Hourly pollution patterns
- Daily trends (weekday vs weekend)
- Time series visualization

### 3. Seasonal Trends
- Monthly pollution levels
- Seasonal variation analysis
- Comparative statistics

### 4. Geographic Analysis
- Monitoring station locations
- Geographic distribution of pollution levels
- Station-level pollution mapping

### 5. Statistical Analysis
- Comprehensive pollution statistics
- Mean, median, min, max, standard deviation
- Data visualization and insights

### 6. Data Filtering Examples
- Date range filtering
- High pollution episode detection
- Geographic area filtering
- Custom parameter selection

## Prerequisites

1. **DataSpaces API Server**: The API server must be running on `http://localhost:8000`
2. **Data Ingestion**: Salt Lake County data must be ingested into namespace `salt_lake_demo`
3. **Python Dependencies**: Install required packages

## Installation

1. Install Python dependencies:
```bash
pip install -r showcase_requirements.txt
```

2. Ensure the DataSpaces API is running:
```bash
# Start the API server (from the main directory)
python -m api.main
```

3. Verify data is ingested:
```bash
# Check if data is available
curl http://localhost:8000/retrieve/salt-lake-county/salt_lake_demo?limit=1
```

## Usage

### Basic Usage
```bash
python salt_lake_showcase.py
```

### What the Script Does

1. **Connection Check**: Verifies API connectivity
2. **Data Exploration**: Shows dataset structure and available filters
3. **Temporal Analysis**: Analyzes hourly and daily pollution patterns
4. **Seasonal Analysis**: Examines monthly trends (Jan-Jun 2016)
5. **Geographic Analysis**: Maps monitoring stations and pollution levels
6. **Statistical Summary**: Provides comprehensive pollution statistics
7. **Filtering Examples**: Demonstrates various data filtering capabilities

### Expected Output

The script will generate:
- Console output with detailed analysis results
- Multiple matplotlib visualizations showing:
  - Hourly pollution patterns
  - Daily trends
  - Seasonal variations
  - Geographic distribution maps
  - Statistical summaries

## API Endpoints Used

The showcase demonstrates the following DataSpaces API endpoints:

- `GET /retrieve/salt-lake-county/{namespace}/available-filters` - Get available filter options
- `GET /ingest/salt-lake-county/sample` - Get sample data
- `GET /retrieve/salt-lake-county/{namespace}` - Retrieve data with basic filtering
- `GET /retrieve/salt-lake-county/{namespace}/filter` - Advanced data filtering
- `POST /retrieve/salt-lake-county/{namespace}/aggregate` - Data aggregation

## Customization

### Modify Analysis Parameters

You can customize the analysis by modifying the configuration variables at the top of the script:

```python
# API Configuration
BASE_URL = "http://localhost:8000"  # Change if API is on different host/port
NAMESPACE = "salt_lake_demo"        # Change to your namespace
VERSION = 0                         # Change to use different data version
```

### Add Custom Analyses

The script is structured with separate classes for API interaction (`SaltLakeDataAPI`) and analysis (`SaltLakeDataAnalyzer`), making it easy to add custom analysis methods.

### Extend Filtering Examples

Add new filtering examples in the `demonstrate_data_filtering()` function:

```python
def demonstrate_data_filtering():
    api = SaltLakeDataAPI()
    
    # Your custom filter example
    filter_params = {
        "date_from": "2016-06-01",
        "date_to": "2016-06-30",
        "measurement_min": "30",
        "limit": 100
    }
    
    result = api.filter_data(filter_params)
    # Process results...
```

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure the DataSpaces API server is running
   - Check the BASE_URL configuration
   - Verify firewall settings

2. **No Data Returned**
   - Verify data has been ingested into the specified namespace
   - Check that the namespace name is correct
   - Ensure data version exists

3. **Import Errors**
   - Install required dependencies: `pip install -r showcase_requirements.txt`
   - Check Python version compatibility (3.7+)

4. **Visualization Issues**
   - Ensure matplotlib backend is properly configured
   - For headless environments, add: `plt.switch_backend('Agg')`

### Debug Mode

For debugging, you can modify the script to print detailed API responses:

```python
# Add this to see raw API responses
import json

def debug_print(response):
    print(json.dumps(response, indent=2))
```

## Data Source

The Salt Lake County air quality data is sourced from the EPA's Air Quality System (AQS) database, containing measurements from regulatory monitoring stations throughout Salt Lake County, Utah.

## License

This showcase script is provided as an example for working with DataSpaces API and air quality data analysis.
