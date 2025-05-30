# DSpaces CSV API - Workflows & Integration Guide

This document provides practical workflows, integration patterns, and real-world examples for the DSpaces CSV API. For detailed endpoint specifications, request/response schemas, and parameter documentation, visit the **auto-generated API documentation** at:

**📚 [http://localhost:8001/docs](http://localhost:8001/docs) - Interactive Swagger UI**

## Overview

The DSpaces CSV API enables you to:
- Ingest CSV datasets into DataSpaces for distributed storage
- Retrieve and filter data with advanced criteria
- Perform statistical aggregations across large datasets
- Preview data before ingestion

## Common Workflows

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

### 4. 🔄 Data Pipeline Integration

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

## Integration Examples

### 1. Python Integration with pandas

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

### 2. JavaScript/Node.js Integration

```javascript
class DSpacesCSVAPI {
    constructor(baseURL = 'http://localhost:8001') {
        this.baseURL = baseURL;
    }

    async healthCheck() {
        const response = await fetch(`${this.baseURL}/health`);
        return response.json();
    }

    async ingestCSV(datasetType, namespace, options = {}) {
        const defaultOptions = {
            version: 0,
            chunk_size: 10000
        };
        
        const response = await fetch(`${this.baseURL}/dspaces/ingest/${datasetType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                namespace,
                ...defaultOptions,
                ...options
            })
        });
        
        return response.json();
    }

    async queryData(datasetType, namespace, options = {}) {
        const params = new URLSearchParams();
        
        Object.entries(options).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                params.append(key, value.toString());
            }
        });

        const response = await fetch(
            `${this.baseURL}/dspaces/retrieve/${datasetType}/${namespace}?${params}`
        );
        return response.json();
    }

    async filterData(datasetType, namespace, filters) {
        const response = await fetch(
            `${this.baseURL}/dspaces/retrieve/${datasetType}/${namespace}/filter`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(filters)
            }
        );
        return response.json();
    }

    async aggregateData(datasetType, namespace, aggregationConfig) {
        const response = await fetch(
            `${this.baseURL}/dspaces/retrieve/${datasetType}/${namespace}/aggregate`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(aggregationConfig)
            }
        );
        return response.json();
    }

    async getAvailableFilters(datasetType, namespace) {
        const response = await fetch(
            `${this.baseURL}/dspaces/retrieve/${datasetType}/${namespace}/available-filters`
        );
        return response.json();
    }
}

// Usage example
const api = new DSpacesCSVAPI();

async function analyzeAirQuality() {
    try {
        // Check API health
        const health = await api.healthCheck();
        console.log('API Status:', health.status);

        // Get available filters
        const filters = await api.getAvailableFilters('csv', 'air_quality');
        console.log('Available parameters:', filters.parameter_names);

        // Query summer ozone data
        const summerOzone = await api.filterData('csv', 'air_quality', {
            date_from: '2023-06-01',
            date_to: '2023-08-31',
            parameter_names: ['Ozone'],
            measurement_min: 50.0,
            limit: 1000
        });

        console.log(`Found ${summerOzone.data.length} high ozone readings`);

        // Get monthly statistics
        const monthlyStats = await api.aggregateData('csv', 'air_quality', {
            group_by: ['Parameter Name', 'Month'],
            aggregations: ['mean', 'max', 'count'],
            aggregation_column: 'Sample_Measurement',
            date_from: '2023-01-01',
            date_to: '2023-12-31'
        });

        console.log('Monthly statistics:', monthlyStats.data);

    } catch (error) {
        console.error('Analysis failed:', error);
    }
}

analyzeAirQuality();
```

### 3. React Component Example

```jsx
import React, { useState, useEffect } from 'react';

const AirQualityDashboard = () => {
    const [data, setData] = useState([]);
    const [filters, setFilters] = useState({
        date_from: '2023-01-01',
        date_to: '2023-12-31',
        parameter_names: ['Ozone'],
        limit: 100
    });
    const [loading, setLoading] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        try {
            const response = await fetch(
                'http://localhost:8001/dspaces/retrieve/csv/air_quality/filter',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(filters)
                }
            );
            const result = await response.json();
            setData(result.data || []);
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [filters]);

    const updateFilter = (key, value) => {
        setFilters(prev => ({
            ...prev,
            [key]: value
        }));
    };

    return (
        <div className="air-quality-dashboard">
            <h2>Air Quality Data Analysis</h2>
            
            <div className="filters">
                <input
                    type="date"
                    value={filters.date_from}
                    onChange={(e) => updateFilter('date_from', e.target.value)}
                />
                <input
                    type="date"
                    value={filters.date_to}
                    onChange={(e) => updateFilter('date_to', e.target.value)}
                />
                <select
                    value={filters.parameter_names[0]}
                    onChange={(e) => updateFilter('parameter_names', [e.target.value])}
                >
                    <option value="Ozone">Ozone</option>
                    <option value="Nitrogen dioxide (NO2)">NO2</option>
                    <option value="PM2.5">PM2.5</option>
                </select>
            </div>

            {loading ? (
                <div>Loading data...</div>
            ) : (
                <div className="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Parameter</th>
                                <th>Measurement</th>
                                <th>Location</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((row, index) => (
                                <tr key={index}>
                                    <td>{row['Date Local']}</td>
                                    <td>{row['Parameter Name']}</td>
                                    <td>{row['Sample Measurement']}</td>
                                    <td>{row['County Name']}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <div className="pagination">
                        {data.length >= filters.limit && (
                            <button onClick={() => updateFilter('limit', filters.limit + 100)}>
                                Load More
                            </button>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default AirQualityDashboard;
```

## Best Practices

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

## Troubleshooting

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

## Monitoring and Observability

### Health Checks
```bash
# Basic health check
curl "http://localhost:8001/health"

# Check specific namespace exists
curl "http://localhost:8001/dspaces/retrieve/csv/my_namespace/available-filters"
```

### Performance Monitoring
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

This workflow and integration guide provides practical patterns for effectively using the DSpaces CSV API in real-world applications, complementing the detailed technical specifications available in the auto-generated Swagger documentation.
