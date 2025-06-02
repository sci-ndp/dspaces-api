# DSpaces CSV API - Complete Guide

This comprehensive guide covers everything you need to work with the DSpaces CSV API, from basic setup to advanced integration patterns.

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Quick Reference](#-quick-reference)
- [Working with CSV Data](#-working-with-csv-data)
- [Programming Language Examples](#-programming-language-examples)
- [Common Workflows](#-common-workflows)
- [Integration Examples](#-integration-examples)
- [Best Practices](#-best-practices)
- [Advanced Use Cases](#-advanced-use-cases)
- [Troubleshooting](#-troubleshooting)

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- curl or HTTP client
- Basic understanding of REST APIs and JSON

### Quick Setup

1. **Clone and start the services:**
   ```bash
   git clone <repository>
   cd dspaces-api
   docker-compose up -d
   ```

2. **Verify the API is running:**
   ```bash
   curl http://localhost:8001/health
   # Expected: {"status": "healthy", "message": "DSpaces API is running"}
   ```

3. **Access interactive documentation:**
   ```
   http://localhost:8001/docs
   ```

## 📚 Quick Reference

### Complete API Documentation

**For comprehensive endpoint documentation, request/response schemas, and interactive testing:**

**➡️ [http://localhost:8001/docs](http://localhost:8001/docs) - FastAPI Auto-Generated Swagger UI**

The Swagger UI provides:
- ✅ Complete endpoint specifications
- ✅ Request/response models with validation
- ✅ Interactive API testing interface
- ✅ Real-time parameter documentation
- ✅ Authentication requirements
- ✅ HTTP status codes and error responses

### Endpoint Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | API health check |
| `/dspaces/ingest/{dataset_type}/from-url` | POST | **Ingest CSV datasets from URL** |
| `/dspaces/retrieve/{dataset_type}/{namespace}` | GET | Retrieve full datasets |
| `/dspaces/ingest/{dataset_type}/sample` | GET | Preview CSV samples |
| `/dspaces/retrieve/{dataset_type}/{namespace}/filter` | GET/POST | Filter data with criteria |
| `/dspaces/retrieve/{dataset_type}/{namespace}/aggregate` | POST | Statistical aggregations |
| `/dspaces/retrieve/{dataset_type}/{namespace}/available-filters` | GET | Discover filter options |

### Getting Started Checklist

1. **Check API Status**: `GET /health`
2. **Preview Your Data**: `GET /dspaces/ingest/{dataset_type}/sample`
3. **Ingest Data**: `POST /dspaces/ingest/{dataset_type}`
4. **Explore Filters**: `GET /dspaces/retrieve/{dataset_type}/{namespace}/available-filters`
5. **Query Data**: Use filter and aggregate endpoints

## 📊 Working with CSV Data

### Data Lifecycle

1. **Preview** → 2. **Ingest** → 3. **Explore** → 4. **Filter** → 5. **Analyze**

### 1. Preview Your Data

Before ingesting, preview your CSV structure:

```bash
# Get sample data and column information
curl "http://localhost:8001/dspaces/ingest/csv/sample?rows=5"
```

**Response shows:**
- Column names and data types
- Sample values
- File size and row count
- Data quality indicators

### 2. Ingest Your Dataset

Download and ingest CSV files directly from any accessible URL:

```bash
curl -X POST "http://localhost:8001/dspaces/ingest/{dataset_type}/from-url" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://example.com/data.csv",
       "namespace": "my_dataset",
       "version": 0,
       "chunk_size": 10000,
       "filename": "custom_name.csv"
     }'
```

**URL Ingestion Features:**
- 🌐 Download from any public URL
- ✅ Automatic CSV validation
- 🧹 Automatic file cleanup
- ⚡ Streaming downloads for large files
- 🛡️ Robust error handling
- 📊 Progress tracking

**Key parameters:**
- `url`: Direct link to the CSV file
- `namespace`: Unique identifier for your dataset
- `version`: Version number for dataset revisions
- `chunk_size`: Processing batch size (adjust for performance)
- `filename`: Optional custom filename for the download

**Real-world examples:**
```bash
# Ingest from GitHub
curl -X POST "http://localhost:8001/dspaces/ingest/research-data/from-url" \
     -d '{"url": "https://raw.githubusercontent.com/user/repo/data.csv", "namespace": "github_data"}'

# Ingest from data repository
curl -X POST "http://localhost:8001/dspaces/ingest/public-datasets/from-url" \
     -d '{"url": "https://data.gov/dataset.csv", "namespace": "government_data"}'

# Ingest with custom settings
curl -X POST "http://localhost:8001/dspaces/ingest/sales-analytics/from-url" \
     -d '{
       "url": "https://company.com/sales_q4.csv",
       "namespace": "q4_analysis", 
       "chunk_size": 5000,
       "filename": "q4_sales_data.csv"
     }'
```

### 3. Explore Your Data

Retrieve data with basic controls:

```bash
# Get first 100 rows
curl "http://localhost:8001/dspaces/retrieve/csv/my_dataset?limit=100"

# Get specific columns
curl "http://localhost:8001/dspaces/retrieve/csv/my_dataset?columns=Date,Value,Category&limit=50"

# Pagination
curl "http://localhost:8001/dspaces/retrieve/csv/my_dataset?limit=100&offset=200"
```

### 4. Filter Your Data

#### Simple Filtering (GET)
```bash
# Date range
curl "http://localhost:8001/dspaces/retrieve/csv/my_dataset/filter?date_from=2023-01-01&date_to=2023-12-31"

# Numeric range
curl "http://localhost:8001/dspaces/retrieve/csv/my_dataset/filter?measurement_min=25.0&measurement_max=75.0"

# Geographic bounds
curl "http://localhost:8001/dspaces/retrieve/csv/my_dataset/filter?lat_min=40.0&lat_max=41.0&lng_min=-112.0&lng_max=-111.0"
```

#### Advanced Filtering (POST)
```bash
curl -X POST "http://localhost:8001/dspaces/retrieve/csv/my_dataset/filter" \
     -H "Content-Type: application/json" \
     -d '{
       "date_from": "2023-06-01",
       "date_to": "2023-08-31",
       "measurement_min": 25.0,
       "custom_filters": {
         "Category": "Premium",
         "Region": "West Coast"
       },
       "columns": ["Date", "Value", "Category", "Region"],
       "limit": 500
     }'
```

### 5. Analyze Your Data

Perform statistical aggregations:

```bash
curl -X POST "http://localhost:8001/dspaces/retrieve/csv/my_dataset/aggregate" \
     -H "Content-Type: application/json" \
     -d '{
       "group_by": ["Category", "Region"],
       "aggregations": ["mean", "count", "std"],
       "aggregation_column": "Value",
       "date_from": "2023-01-01"
     }'
```

## 💻 Programming Language Examples

### Python with requests

```python
import requests
import json

base_url = "http://localhost:8001"

# Health check
response = requests.get(f"{base_url}/health")
print(response.json())

# 🆕 Ingest data from URL
url_ingest_data = {
    "url": "https://raw.githubusercontent.com/plotly/datasets/master/iris.csv",
    "namespace": "iris_analysis",
    "version": 1,
    "chunk_size": 1000,
    "filename": "iris_dataset.csv"
}
response = requests.post(f"{base_url}/dspaces/ingest/research-data/from-url", json=url_ingest_data)
result = response.json()
print(f"Ingested {result['total_rows']} rows")

# 🆕 Ingest data from URL
url_ingest_data = {
    "url": "https://raw.githubusercontent.com/plotly/datasets/master/iris.csv",
    "namespace": "iris_analysis",
    "version": 1,
    "chunk_size": 1000,
    "filename": "iris_dataset.csv"
}
response = requests.post(f"{base_url}/dspaces/ingest/research-data/from-url", json=url_ingest_data)
result = response.json()
print(f"URL Ingestion: {result['message']} - {result['total_rows']} rows, {result['total_columns']} columns")

# Filter data
filter_data = {
    "date_from": "2023-01-01",
    "date_to": "2023-12-31",
    "measurement_min": 1000.0,
    "custom_filters": {
        "Region": "North America"
    },
    "limit": 100
}
response = requests.post(f"{base_url}/dspaces/retrieve/csv/sales_data/filter", json=filter_data)
filtered_data = response.json()
print(f"Found {len(filtered_data['data'])} records")

# Aggregate data
agg_data = {
    "group_by": ["Region", "Product_Category"],
    "aggregations": ["sum", "mean", "count"],
    "aggregation_column": "Revenue"
}
response = requests.post(f"{base_url}/dspaces/retrieve/csv/sales_data/aggregate", json=agg_data)
aggregated = response.json()
print(f"Created {len(aggregated['data'])} aggregate groups")
```

### Python with pandas integration

```python
import requests
import pandas as pd
from typing import Dict, List, Optional

class DSpacesClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
    
    def health_check(self) -> Dict:
        """Check API health status"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def ingest_csv_from_url(self, dataset_type: str, url: str, namespace: str, 
                           version: int = 0, chunk_size: int = 10000, 
                           filename: Optional[str] = None) -> Dict:
        """Ingest CSV data directly from URL"""
        payload = {
            "namespace": namespace,
            "version": version,
            "chunk_size": chunk_size
        }
        response = requests.post(f"{self.base_url}/dspaces/ingest/csv", json=payload)
        response.raise_for_status()
        return response.json()
    
    def ingest_csv_from_url(self, dataset_type: str, url: str, namespace: str, 
                           version: int = 0, chunk_size: int = 10000, 
                           filename: Optional[str] = None) -> Dict:
        """🆕 Ingest CSV data directly from URL"""
        payload = {
            "url": url,
            "namespace": namespace,
            "version": version,
            "chunk_size": chunk_size
        }
        if filename:
            payload["filename"] = filename
            
        response = requests.post(f"{self.base_url}/dspaces/ingest/{dataset_type}/from-url", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_data(self, namespace: str, limit: Optional[int] = None, 
                 columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Retrieve data as pandas DataFrame"""
        params = {}
        if limit:
            params['limit'] = limit
        if columns:
            params['columns'] = ','.join(columns)
        
        response = requests.get(f"{self.base_url}/dspaces/retrieve/csv/{namespace}", params=params)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data['data'])
    
    def filter_data(self, namespace: str, filters: Dict) -> pd.DataFrame:
        """Filter data and return as DataFrame"""
        response = requests.post(f"{self.base_url}/dspaces/retrieve/csv/{namespace}/filter", json=filters)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data['data'])
    
    def aggregate_data(self, namespace: str, group_by: List[str], 
                      aggregations: List[str], aggregation_column: str = "Sample_Measurement") -> pd.DataFrame:
        """Perform aggregation and return as DataFrame"""
        payload = {
            "group_by": group_by,
            "aggregations": aggregations,
            "aggregation_column": aggregation_column
        }
        response = requests.post(f"{self.base_url}/dspaces/retrieve/csv/{namespace}/aggregate", json=payload)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data['data'])

# Usage examples
client = DSpacesClient()

# Check health
health = client.health_check()
print(f"API Status: {health['status']}")

# Ingest data from file
result = client.ingest_csv("analysis_dataset")
print(f"Ingested {result['total_rows']} rows")

# 🆕 Ingest data from URL
url_result = client.ingest_csv_from_url(
    dataset_type="research-data",
    url="https://raw.githubusercontent.com/plotly/datasets/master/iris.csv",
    namespace="iris_ml_analysis",
    chunk_size=1000,
    filename="iris_research.csv"
)
print(f"URL Ingestion: {url_result['message']} - {url_result['total_rows']} rows")

# Get the URL-ingested data
iris_df = client.get_data("iris_ml_analysis", limit=150)
print(f"Iris dataset shape: {iris_df.shape}")
print(iris_df.head())

# Get filtered data
filters = {
    "date_from": "2023-01-01",
    "measurement_min": 25.0,
    "limit": 1000
}
df = client.filter_data("analysis_dataset", filters)
print(f"Retrieved {len(df)} filtered records")

# Perform aggregation
agg_df = client.aggregate_data(
    "analysis_dataset", 
    group_by=["Category"], 
    aggregations=["mean", "count"]
)
print(f"Generated {len(agg_df)} aggregate groups")
```

## 🔄 Common Workflows

### 1. 🔍 Data Exploration Workflow

**Scenario**: You have a new CSV dataset and want to understand its structure before analysis.

```bash
# Step 1: Preview the data structure
curl "http://localhost:8001/dspaces/ingest/csv/sample?rows=10"

# Step 2: Ingest with appropriate namespace
curl -X POST "http://localhost:8001/dspaces/ingest/csv" \
     -H "Content-Type: application/json" \
     -d '{"namespace": "exploration_2024", "chunk_size": 10000}'

# Step 3: Discover available filters
curl "http://localhost:8001/dspaces/retrieve/csv/exploration_2024/available-filters"

# Step 4: Get a sample of the ingested data
curl "http://localhost:8001/dspaces/retrieve/csv/exploration_2024?limit=50"
```

### 2. 📊 Time Series Analysis Workflow

**Scenario**: Analyzing environmental sensor data over time periods.

```bash
# Get monthly aggregations for trend analysis
curl -X POST "http://localhost:8001/dspaces/retrieve/csv/sensors/aggregate" \
     -H "Content-Type: application/json" \
     -d '{
       "group_by": ["Month", "Sensor_Type"],
       "aggregations": ["mean", "std", "count"],
       "aggregation_column": "Temperature",
       "date_from": "2023-01-01",
       "date_to": "2023-12-31"
     }'

# Filter for anomalous readings (outside normal range)
curl -X POST "http://localhost:8001/dspaces/retrieve/csv/sensors/filter" \
     -H "Content-Type: application/json" \
     -d '{
       "measurement_min": 100.0,
       "date_from": "2023-01-01",
       "columns": ["Date", "Time", "Sensor_ID", "Temperature", "Location"],
       "limit": 1000
     }'
```

### 3. 🌍 Geographic Analysis Workflow

**Scenario**: Analyzing spatial data within specific geographic boundaries.

```bash
# Filter data within city boundaries
curl -X POST "http://localhost:8001/dspaces/retrieve/csv/air_quality/filter" \
     -H "Content-Type: application/json" \
     -d '{
       "lat_min": 40.7589,
       "lat_max": 40.7789,
       "lng_min": -111.9083,
       "lng_max": -111.8683,
       "parameter_names": ["Nitrogen dioxide (NO2)", "Ozone"],
       "date_from": "2023-06-01",
       "date_to": "2023-08-31"
     }'

# Get statistics by geographic zones
curl -X POST "http://localhost:8001/dspaces/retrieve/csv/air_quality/aggregate" \
     -H "Content-Type: application/json" \
     -d '{
       "group_by": ["County Name", "Parameter Name"],
       "aggregations": ["mean", "max", "count"],
       "aggregation_column": "Sample_Measurement",
       "lat_min": 40.0,
       "lat_max": 41.0,
       "lng_min": -112.0,
       "lng_max": -111.0
     }'
```

### 4. 🌐 URL Ingestion Workflow (🆕 NEW!)

**Scenario**: Ingesting CSV datasets directly from web URLs without manual downloads.

```bash
# Step 1: Ingest from GitHub repository
curl -X POST "http://localhost:8001/dspaces/ingest/research-data/from-url" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://raw.githubusercontent.com/plotly/datasets/master/iris.csv",
       "namespace": "iris_analysis",
       "version": 1,
       "chunk_size": 1000
     }'

# Step 2: Verify ingestion and explore structure
curl "http://localhost:8001/dspaces/retrieve/research-data/iris_analysis?limit=10"

# Step 3: Discover available filters for the new dataset
curl "http://localhost:8001/dspaces/retrieve/research-data/iris_analysis/available-filters"

# Step 4: Filter by species and measurements
curl -X POST "http://localhost:8001/dspaces/retrieve/research-data/iris_analysis/filter" \
     -H "Content-Type: application/json" \
     -d '{
       "custom_filters": {
         "species": "setosa",
         "sepal_length": {"min": 4.0, "max": 6.0}
       },
       "limit": 50
     }'

# Step 5: Aggregate by species
curl -X POST "http://localhost:8001/dspaces/retrieve/research-data/iris_analysis/aggregate" \
     -H "Content-Type: application/json" \
     -d '{
       "group_by": ["species"],
       "aggregations": ["mean", "std", "count"],
       "aggregation_column": "sepal_length"
     }'
```

**URL Ingestion Benefits:**
- 🚀 No manual file downloads required
- 🔄 Easy integration with data pipelines
- 📊 Automatic CSV validation and processing
- 🧹 Temporary file cleanup handled automatically
- ⚡ Streaming downloads for large datasets

**Supported URL Sources:**
- GitHub raw file URLs
- Data repository URLs (data.gov, etc.)
- Cloud storage public URLs
- API endpoints returning CSV data
- Direct file download links

### 5. 🔄 Data Pipeline Integration

**Scenario**: Automating data processing in a scheduled pipeline.

```bash
#!/bin/bash
# daily_processing.sh

# Set variables
DATASET_TYPE="daily_sales"
NAMESPACE="sales_$(date +%Y_%m)"
BASE_URL="http://localhost:8001"

# Check API health
if ! curl -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo "❌ API not available"
    exit 1
fi

# Ingest new data
echo "📥 Ingesting daily sales data..."
INGEST_RESPONSE=$(curl -s -X POST "$BASE_URL/dspaces/ingest/$DATASET_TYPE" \
     -H "Content-Type: application/json" \
     -d "{\"namespace\": \"$NAMESPACE\", \"version\": $(date +%Y%m%d)}")

# Check if ingestion was successful
if [[ $(echo "$INGEST_RESPONSE" | jq -r '.success') == "true" ]]; then
    echo "✅ Ingestion successful"
    
    # Generate daily report
    echo "📊 Generating daily summary..."
    curl -X POST "$BASE_URL/dspaces/retrieve/$DATASET_TYPE/$NAMESPACE/aggregate" \
         -H "Content-Type: application/json" \
         -d '{
           "group_by": ["Product_Category", "Sales_Rep"],
           "aggregations": ["sum", "mean", "count"],
           "aggregation_column": "Revenue",
           "date_from": "'$(date -d yesterday +%Y-%m-%d)'",
           "date_to": "'$(date +%Y-%m-%d)'"
         }' > daily_sales_report.json
    
    echo "✅ Report generated: daily_sales_report.json"
else
    echo "❌ Ingestion failed"
    exit 1
fi
```

## 🔧 Integration Examples

### Python Integration with pandas

```python
import requests
import pandas as pd
from typing import Dict, List, Optional

class DSpacesCSVClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        
    def ingest_dataframe(self, df: pd.DataFrame, namespace: str, dataset_type: str = "csv") -> Dict:
        """Save DataFrame to temporary CSV and ingest into DSpaces"""
        # Save to temporary CSV
        temp_file = f"/tmp/{namespace}_data.csv"
        df.to_csv(temp_file, index=False)
        
        # Ingest via API
        response = requests.post(
            f"{self.base_url}/dspaces/ingest/{dataset_type}",
            json={"namespace": namespace, "version": 0}
        )
        return response.json()
    
    def ingest_from_url(self, url: str, namespace: str, dataset_type: str = "csv", 
                       chunk_size: int = 10000, filename: Optional[str] = None) -> Dict:
        """Ingest CSV data directly from a URL"""
        payload = {
            "url": url,
            "namespace": namespace,
            "version": 0,
            "chunk_size": chunk_size
        }
        if filename:
            payload["filename"] = filename
            
        response = requests.post(
            f"{self.base_url}/dspaces/ingest/{dataset_type}/from-url",
            json=payload
        )
        return response.json()
    
    def query_to_dataframe(self, dataset_type: str, namespace: str, 
                          filters: Optional[Dict] = None, limit: int = 10000) -> pd.DataFrame:
        """Retrieve filtered data as pandas DataFrame"""
        if filters:
            response = requests.post(
                f"{self.base_url}/dspaces/retrieve/{dataset_type}/{namespace}/filter",
                json={**filters, "limit": limit}
            )
        else:
            response = requests.get(
                f"{self.base_url}/dspaces/retrieve/{dataset_type}/{namespace}",
                params={"limit": limit}
            )
        
        data = response.json()
        return pd.DataFrame(data.get("data", []))
    
    def aggregate_data(self, dataset_type: str, namespace: str, 
                      group_by: List[str], aggregations: List[str],
                      filters: Optional[Dict] = None) -> pd.DataFrame:
        """Get aggregated data as DataFrame"""
        request_data = {
            "group_by": group_by,
            "aggregations": aggregations
        }
        if filters:
            request_data.update(filters)
            
        response = requests.post(
            f"{self.base_url}/dspaces/retrieve/{dataset_type}/{namespace}/aggregate",
            json=request_data
        )
        
        data = response.json()
        return pd.DataFrame(data.get("data", []))

# Usage example
client = DSpacesCSVClient()

# 🆕 Ingest data directly from URL
url_result = client.ingest_from_url(
    url="https://raw.githubusercontent.com/plotly/datasets/master/iris.csv",
    namespace="iris_analysis",
    dataset_type="research-data",
    chunk_size=1000,
    filename="iris_dataset.csv"
)
print(f"URL Ingestion: {url_result['message']} - {url_result['total_rows']} rows")

# Filter and analyze air quality data
air_quality_df = client.query_to_dataframe(
    dataset_type="csv",
    namespace="air_quality_utah",
    filters={
        "date_from": "2023-06-01",
        "date_to": "2023-08-31",
        "parameter_names": ["Ozone", "Nitrogen dioxide (NO2)"],
        "measurement_min": 25.0
    }
)

# Get monthly statistics
monthly_stats = client.aggregate_data(
    dataset_type="csv",
    namespace="air_quality_utah",
    group_by=["Parameter Name", "Date Local"],
    aggregations=["mean", "max", "count"],
    filters={"date_from": "2023-01-01", "date_to": "2023-12-31"}
)

print(f"Retrieved {len(air_quality_df)} filtered records")
print(f"Monthly aggregations: {len(monthly_stats)} groups")
```

## 🎯 Best Practices

### 1. 🚀 Performance Optimization

**Use Pagination for Large Datasets**
```bash
# Instead of loading all data at once
curl "http://localhost:8001/dspaces/retrieve/csv/large_dataset"

# Use pagination
curl "http://localhost:8001/dspaces/retrieve/csv/large_dataset?limit=1000&offset=0"
curl "http://localhost:8001/dspaces/retrieve/csv/large_dataset?limit=1000&offset=1000"
```

**Select Only Required Columns**
```bash
# Instead of all columns
curl "http://localhost:8001/dspaces/retrieve/csv/dataset/namespace"

# Select specific columns
curl "http://localhost:8001/dspaces/retrieve/csv/dataset/namespace?columns=Date,Value,Category"
```

**Use Aggregation for Analytics**
```bash
# Instead of processing raw data client-side
curl "http://localhost:8001/dspaces/retrieve/csv/sales/namespace?limit=100000"

# Get server-side aggregations
curl -X POST "http://localhost:8001/dspaces/retrieve/csv/sales/namespace/aggregate" \
     -d '{"group_by": ["Region"], "aggregations": ["sum", "mean"]}'
```

### 2. 🔒 Error Handling

**Implement Robust Error Handling**
```python
import requests
from typing import Dict, Optional

def safe_api_call(url: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict:
    """Make API call with comprehensive error handling"""
    try:
        if method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, params=data, timeout=30)
        
        response.raise_for_status()
        return {"success": True, "data": response.json()}
        
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "API server unavailable"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timeout"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP error: {e.response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}

# Usage
result = safe_api_call(
    "http://localhost:8001/dspaces/retrieve/csv/data/filter",
    method="POST",
    data={"date_from": "2023-01-01", "limit": 1000}
)

if result["success"]:
    data = result["data"]["data"]
    print(f"Retrieved {len(data)} records")
else:
    print(f"Error: {result['error']}")
```

### 3. 📊 Data Quality Checks

**Validate Data Before Analysis**
```bash
# Check data structure first
curl "http://localhost:8001/dspaces/ingest/csv/sample?rows=5"

# Verify ingestion success
INGEST_RESULT=$(curl -X POST "http://localhost:8001/dspaces/ingest/csv" \
                     -H "Content-Type: application/json" \
                     -d '{"namespace": "validation_test"}')

# Check if all columns were ingested successfully
echo "$INGEST_RESULT" | jq '.stored_objects | to_entries[] | select(.value.status != "success")'
```

### 4. Data Validation

```python
def validate_filter_request(filters):
    """Validate filter parameters before sending request"""
    
    # Date validation
    if 'date_from' in filters or 'date_to' in filters:
        from datetime import datetime
        try:
            if 'date_from' in filters:
                datetime.strptime(filters['date_from'], '%Y-%m-%d')
            if 'date_to' in filters:
                datetime.strptime(filters['date_to'], '%Y-%m-%d')
        except ValueError:
            raise ValueError("Dates must be in YYYY-MM-DD format")
    
    # Numeric validation
    numeric_fields = ['measurement_min', 'measurement_max', 'lat_min', 'lat_max', 'lng_min', 'lng_max']
    for field in numeric_fields:
        if field in filters and not isinstance(filters[field], (int, float)):
            raise ValueError(f"{field} must be a number")
    
    # Geographic bounds validation
    if 'lat_min' in filters and (filters['lat_min'] < -90 or filters['lat_min'] > 90):
        raise ValueError("lat_min must be between -90 and 90")
    if 'lat_max' in filters and (filters['lat_max'] < -90 or filters['lat_max'] > 90):
        raise ValueError("lat_max must be between -90 and 90")
    if 'lng_min' in filters and (filters['lng_min'] < -180 or filters['lng_min'] > 180):
        raise ValueError("lng_min must be between -180 and 180")
    if 'lng_max' in filters and (filters['lng_max'] < -180 or filters['lng_max'] > 180):
        raise ValueError("lng_max must be between -180 and 180")
    
    return True
```

## 🛠 Advanced Use Cases

### Real-time Data Pipeline

```python
import time
import pandas as pd

def create_data_pipeline(namespace, processing_func, interval=60):
    """Process data updates in real-time"""
    client = DSpacesClient()
    last_processed = None
    
    while True:
        try:
            # Get latest data
            if last_processed:
                filters = {"date_from": last_processed.isoformat()}
                new_data = client.filter_data(namespace, filters)
            else:
                new_data = client.get_data(namespace, limit=1000)
            
            if not new_data.empty:
                # Process new data
                processed = processing_func(new_data)
                print(f"Processed {len(processed)} new records")
                
                # Update timestamp
                if 'Date Local' in new_data.columns:
                    last_processed = pd.to_datetime(new_data['Date Local']).max()
            
            time.sleep(interval)
            
        except Exception as e:
            print(f"Pipeline error: {e}")
            time.sleep(interval)

def my_processing_function(df):
    """Example processing function"""
    # Calculate moving averages, detect anomalies, etc.
    df['moving_avg'] = df['Sample_Measurement'].rolling(window=5).mean()
    df['anomaly'] = abs(df['Sample_Measurement'] - df['moving_avg']) > 2 * df['Sample_Measurement'].std()
    return df

# Start pipeline
create_data_pipeline("sensor_data", my_processing_function)
```

### Multi-Dataset Analysis

```python
def compare_datasets(namespaces, filters=None):
    """Compare multiple datasets with same structure"""
    client = DSpacesClient()
    results = {}
    
    for namespace in namespaces:
        try:
            if filters:
                data = client.filter_data(namespace, filters)
            else:
                data = client.get_data(namespace)
            
            # Calculate basic statistics
            stats = {
                'count': len(data),
                'mean_measurement': data['Sample_Measurement'].mean() if 'Sample_Measurement' in data.columns else None,
                'date_range': {
                    'start': data['Date Local'].min() if 'Date Local' in data.columns else None,
                    'end': data['Date Local'].max() if 'Date Local' in data.columns else None
                }
            }
            results[namespace] = stats
            
        except Exception as e:
            print(f"Error processing {namespace}: {e}")
            results[namespace] = {'error': str(e)}
    
    return results

# Compare air quality data from different regions
datasets = ["air_quality_utah", "air_quality_california", "air_quality_texas"]
comparison = compare_datasets(datasets, {"date_from": "2023-01-01"})
```

### Automated Reporting

```python
def generate_monthly_report(namespace, year, month):
    """Generate automated monthly data report"""
    client = DSpacesClient()
    
    # Define date range
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year+1}-01-01"
    else:
        end_date = f"{year}-{month+1:02d}-01"
    
    # Get monthly aggregations
    monthly_agg = client.aggregate_data(
        namespace,
        group_by=["Parameter Name"],
        aggregations=["mean", "min", "max", "count"],
        aggregation_column="Sample_Measurement"
    )
    
    # Get daily trends
    daily_filters = {
        "date_from": start_date,
        "date_to": end_date
    }
    daily_agg = client.aggregate_data(
        namespace,
        group_by=["Date Local", "Parameter Name"],
        aggregations=["mean"],
        aggregation_column="Sample_Measurement"
    )
    
    # Generate report
    report = {
        "period": f"{year}-{month:02d}",
        "summary": {
            "total_measurements": monthly_agg['Sample_Measurement_count'].sum(),
            "parameters_monitored": len(monthly_agg),
            "avg_daily_measurements": monthly_agg['Sample_Measurement_count'].sum() / 30
        },
        "by_parameter": monthly_agg.to_dict('records'),
        "daily_trends": daily_agg.to_dict('records')
    }
    
    return report

# Generate report for December 2023
december_report = generate_monthly_report("air_quality", 2023, 12)
```

## 🐛 Troubleshooting

### Common Issues and Solutions

**1. Large Dataset Timeouts**
```bash
# Problem: Request times out for large datasets
# Solution: Use smaller chunks and pagination

# ❌ This might timeout
curl "http://localhost:8001/dspaces/retrieve/csv/huge_dataset/namespace"

# ✅ Use pagination instead
curl "http://localhost:8001/dspaces/retrieve/csv/huge_dataset/namespace?limit=1000"
```

**2. Memory Issues During Ingestion**
```bash
# Problem: Large CSV files cause memory errors
# Solution: Use smaller chunk_size

# ❌ Default chunk size might be too large
curl -X POST "http://localhost:8001/dspaces/ingest/csv" \
     -d '{"namespace": "large_file"}'

# ✅ Use smaller chunks
curl -X POST "http://localhost:8001/dspaces/ingest/csv" \
     -d '{"namespace": "large_file", "chunk_size": 1000}'
```

**3. Filter Not Finding Data**
```bash
# Problem: Filters return empty results
# Solution: Check available filter values first

# ✅ Check what values are available
curl "http://localhost:8001/dspaces/retrieve/csv/dataset/namespace/available-filters"

# Then use exact values from the response
curl -X POST "http://localhost:8001/dspaces/retrieve/csv/dataset/namespace/filter" \
     -d '{"parameter_names": ["Exact Parameter Name From Available Filters"]}'
```

**4. Performance Issues with Complex Filters**
```bash
# Problem: Complex filters are slow
# Solution: Apply most selective filters first

# ❌ This processes many records before filtering
{
  "custom_filters": {"category": "A"},
  "measurement_min": 50,
  "date_from": "2023-01-01"
}

# ✅ Apply date filter first (most selective)
{
  "date_from": "2023-12-01",
  "measurement_min": 50,
  "custom_filters": {"category": "A"}
}
```

**5. Connection Errors**
```python
# Check if API is running
try:
    response = requests.get("http://localhost:8001/health", timeout=5)
    print("API is running")
except requests.exceptions.ConnectionError:
    print("API is not accessible. Check if Docker containers are running:")
    print("docker-compose ps")
```

**6. Empty Results**
```python
# Check available filters first
filters_response = requests.get(f"{base_url}/dspaces/retrieve/csv/{namespace}/available-filters")
available_filters = filters_response.json()
print("Available date range:", available_filters.get('date_range'))
print("Available parameters:", available_filters.get('parameter_names'))
```

**7. Performance Issues**
```python
# Monitor response times
import time

start_time = time.time()
response = requests.get(f"{base_url}/dspaces/retrieve/csv/{namespace}?limit=1000")
end_time = time.time()

print(f"Request took {end_time - start_time:.2f} seconds")
if end_time - start_time > 5:
    print("Consider using smaller limits or adding filters")
```

**8. Memory Issues with Large Datasets**
```python
# Use streaming for large datasets
def stream_large_dataset(namespace, chunk_size=1000):
    offset = 0
    while True:
        response = requests.get(f"{base_url}/dspaces/retrieve/csv/{namespace}",
                              params={"limit": chunk_size, "offset": offset})
        data = response.json()['data']
        if not data:
            break
        
        # Process chunk immediately
        yield pd.DataFrame(data)
        offset += chunk_size

# Process in chunks
for chunk_df in stream_large_dataset("large_dataset"):
    # Process each chunk
    processed = process_chunk(chunk_df)
    save_results(processed)
```

### Monitoring and Observability

**Health Checks**
```bash
# Basic health check
curl "http://localhost:8001/health"

# Check specific namespace exists
curl "http://localhost:8001/dspaces/retrieve/csv/my_namespace/available-filters"
```

**Performance Monitoring**
```python
import time
import requests

def monitor_api_performance(endpoint: str, data: dict = None) -> dict:
    """Monitor API call performance"""
    start_time = time.time()
    
    try:
        if data:
            response = requests.post(endpoint, json=data)
        else:
            response = requests.get(endpoint)
        
        end_time = time.time()
        
        return {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "response_time_ms": round((end_time - start_time) * 1000, 2),
            "success": response.status_code == 200,
            "data_size": len(response.content) if response.content else 0
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "error": str(e),
            "success": False
        }

# Monitor key endpoints
endpoints = [
    ("http://localhost:8001/health", None),
    ("http://localhost:8001/dspaces/retrieve/csv/test/available-filters", None),
    ("http://localhost:8001/dspaces/retrieve/csv/test/filter", {"limit": 100})
]

for endpoint, data in endpoints:
    result = monitor_api_performance(endpoint, data)
    print(f"⏱️  {result['endpoint']}: {result.get('response_time_ms', 'ERROR')}ms")
```

**Debug Mode**

```python
import logging
import requests

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Log all requests
def debug_request(method, url, **kwargs):
    print(f"Making {method} request to {url}")
    if 'json' in kwargs:
        print(f"Request body: {kwargs['json']}")
    
    response = getattr(requests, method.lower())(url, **kwargs)
    
    print(f"Response status: {response.status_code}")
    print(f"Response time: {response.elapsed.total_seconds():.2f}s")
    
    if response.status_code >= 400:
        print(f"Error response: {response.text}")
    
    return response

# Use debug_request instead of requests.get/post
response = debug_request('GET', f"{base_url}/dspaces/retrieve/csv/my_dataset")
```

---

This comprehensive guide provides everything you need to effectively work with the DSpaces CSV API, from basic operations to advanced integration patterns and troubleshooting.
