# DSpaces CSV API Developer Guide

Complete developer guide for integrating with the DSpaces CSV API, including code examples, best practices, and troubleshooting.

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

---

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

Store your CSV data in DSpaces:

```bash
curl -X POST "http://localhost:8001/dspaces/ingest/csv" \
     -H "Content-Type: application/json" \
     -d '{
       "namespace": "my_dataset",
       "version": 0,
       "chunk_size": 10000
     }'
```

**Key parameters:**
- `namespace`: Unique identifier for your dataset
- `version`: Version number for dataset revisions
- `chunk_size`: Processing batch size (adjust for performance)

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

---

## 💻 Programming Language Examples

### Python with requests

```python
import requests
import json

base_url = "http://localhost:8001"

# Health check
response = requests.get(f"{base_url}/health")
print(response.json())

# Ingest data
ingest_data = {
    "namespace": "sales_data",
    "version": 0
}
response = requests.post(f"{base_url}/dspaces/ingest/csv", json=ingest_data)
result = response.json()
print(f"Ingested {result['total_rows']} rows")

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

### JavaScript/Node.js with fetch

```javascript
const baseUrl = "http://localhost:8001";

// Health check
async function checkHealth() {
    const response = await fetch(`${baseUrl}/health`);
    const data = await response.json();
    console.log(data);
}

// Ingest data
async function ingestData() {
    const ingestPayload = {
        namespace: "sensor_data",
        version: 0,
        chunk_size: 5000
    };
    
    const response = await fetch(`${baseUrl}/dspaces/ingest/csv`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ingestPayload)
    });
    
    const result = await response.json();
    console.log(`Ingested ${result.total_rows} rows across ${result.total_columns} columns`);
}

// Filter data
async function filterData() {
    const filterPayload = {
        date_from: "2023-01-01",
        measurement_min: 20.0,
        measurement_max: 80.0,
        lat_min: 40.0,
        lat_max: 41.0,
        lng_min: -112.0,
        lng_max: -111.0,
        limit: 200
    };
    
    const response = await fetch(`${baseUrl}/dspaces/retrieve/csv/sensor_data/filter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filterPayload)
    });
    
    const data = await response.json();
    console.log(`Filtered to ${data.metadata.filtered_records} records`);
    return data.data;
}

// Aggregate data
async function aggregateData() {
    const aggPayload = {
        group_by: ["Sensor_Type", "Location"],
        aggregations: ["mean", "min", "max"],
        aggregation_column: "Temperature",
        date_from: "2023-12-01"
    };
    
    const response = await fetch(`${baseUrl}/dspaces/retrieve/csv/sensor_data/aggregate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(aggPayload)
    });
    
    const data = await response.json();
    console.log(`Created ${data.metadata.total_groups} aggregate groups`);
    return data.data;
}
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
    
    def ingest_csv(self, namespace: str, version: int = 0, chunk_size: int = 10000) -> Dict:
        """Ingest CSV data into DSpaces"""
        payload = {
            "namespace": namespace,
            "version": version,
            "chunk_size": chunk_size
        }
        response = requests.post(f"{self.base_url}/dspaces/ingest/csv", json=payload)
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

# Usage example
client = DSpacesClient()

# Check health
health = client.health_check()
print(f"API Status: {health['status']}")

# Ingest data
result = client.ingest_csv("analysis_dataset")
print(f"Ingested {result['total_rows']} rows")

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

---

## 🔧 Best Practices

### Performance Optimization

1. **Use pagination for large datasets:**
   ```python
   def get_all_data(namespace, chunk_size=1000):
       all_data = []
       offset = 0
       while True:
           response = requests.get(f"{base_url}/dspaces/retrieve/csv/{namespace}",
                                 params={"limit": chunk_size, "offset": offset})
           data = response.json()['data']
           if not data:
               break
           all_data.extend(data)
           offset += chunk_size
       return all_data
   ```

2. **Select only needed columns:**
   ```python
   # Instead of retrieving all columns
   all_data = client.get_data("large_dataset")
   
   # Select specific columns
   subset = client.get_data("large_dataset", columns=["Date", "Value", "Category"])
   ```

3. **Use server-side filtering:**
   ```python
   # Filter on server (efficient)
   filtered = client.filter_data("dataset", {"measurement_min": 50.0})
   
   # Don't filter after retrieval (inefficient)
   all_data = client.get_data("dataset")
   filtered = all_data[all_data['measurement'] >= 50.0]
   ```

4. **Aggregate when possible:**
   ```python
   # Get aggregated statistics (efficient)
   monthly_stats = client.aggregate_data("dataset", 
                                       group_by=["Month"], 
                                       aggregations=["mean", "count"])
   
   # Don't aggregate raw data locally (inefficient for large datasets)
   raw_data = client.get_data("dataset")
   monthly_stats = raw_data.groupby('Month').agg({'Value': ['mean', 'count']})
   ```

### Error Handling

```python
import requests
from requests.exceptions import RequestException

def safe_api_call(url, method='GET', **kwargs):
    try:
        if method.upper() == 'POST':
            response = requests.post(url, **kwargs)
        else:
            response = requests.get(url, **kwargs)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print(f"Data not found: {e}")
        elif response.status_code == 400:
            print(f"Bad request: {e}")
        elif response.status_code == 422:
            print(f"Validation error: {e}")
        else:
            print(f"HTTP error: {e}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
result = safe_api_call(f"{base_url}/dspaces/retrieve/csv/my_dataset")
if result:
    print(f"Retrieved {len(result['data'])} records")
```

### Data Validation

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

---

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

---

## 🐛 Troubleshooting

### Common Issues and Solutions

1. **Connection Errors**
   ```python
   # Check if API is running
   try:
       response = requests.get("http://localhost:8001/health", timeout=5)
       print("API is running")
   except requests.exceptions.ConnectionError:
       print("API is not accessible. Check if Docker containers are running:")
       print("docker-compose ps")
   ```

2. **Empty Results**
   ```python
   # Check available filters first
   filters_response = requests.get(f"{base_url}/dspaces/retrieve/csv/{namespace}/available-filters")
   available_filters = filters_response.json()
   print("Available date range:", available_filters.get('date_range'))
   print("Available parameters:", available_filters.get('parameter_names'))
   ```

3. **Performance Issues**
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

4. **Memory Issues with Large Datasets**
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

### Debug Mode

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

This developer guide provides comprehensive examples and best practices for effectively using the DSpaces CSV API in production applications.
