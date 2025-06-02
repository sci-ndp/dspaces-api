import json
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class Interval(BaseModel):
    start: int = Field(title="the lower bound of a range", ge=-1)
    span: int = Field(title="the size of a range", ge=0)

class BoundingBox(BaseModel):
    bounds: list[Interval]

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class DSObject(BaseModel):
    name: str
    namespace: Optional[str] = None
    version: int
    bounds: list[Interval]

class RequestList(BaseModel):
    requests: list[DSObject] = []

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    
class DSRegHandle(BaseModel):
    namespace: str
    parameters: dict

class CSVIngestionRequest(BaseModel):
    namespace: str = Field(default="datasets", title="Namespace", description="The namespace to store the CSV data under")
    version: int = Field(default=0, title="Version", description="Version number for the stored objects", ge=0)
    chunk_size: int = Field(default=10000, title="Chunk Size", description="Number of rows to process at once", gt=0)

class CSVIngestionResponse(BaseModel):
    file_path: str
    total_rows: int
    total_columns: int
    columns: list[str]
    namespace: str
    version: int
    stored_objects: dict
    success: bool
    message: str

# Generic CSV Dataset Models

class CSVDatasetFilterRequest(BaseModel):
    """Generic filter request model for CSV datasets"""
    
    # Date/Time filters
    date_from: Optional[date] = Field(default=None, description="Start date (YYYY-MM-DD)")
    date_to: Optional[date] = Field(default=None, description="End date (YYYY-MM-DD)")
    time_from: Optional[str] = Field(default=None, description="Start time (HH:MM format)")
    time_to: Optional[str] = Field(default=None, description="End time (HH:MM format)")
    
    # Numeric filters
    measurement_min: Optional[float] = Field(default=None, description="Minimum sample measurement value")
    measurement_max: Optional[float] = Field(default=None, description="Maximum sample measurement value")
    
    # Geographic filters
    lat_min: Optional[float] = Field(default=None, description="Minimum latitude", ge=-90, le=90)
    lat_max: Optional[float] = Field(default=None, description="Maximum latitude", ge=-90, le=90)
    lng_min: Optional[float] = Field(default=None, description="Minimum longitude", ge=-180, le=180)
    lng_max: Optional[float] = Field(default=None, description="Maximum longitude", ge=-180, le=180)
    
    # Categorical filters
    parameter_names: Optional[List[str]] = Field(default=None, description="List of parameter names to include")
    state_codes: Optional[List[str]] = Field(default=None, description="List of state codes to include")
    county_codes: Optional[List[str]] = Field(default=None, description="List of county codes to include")
    site_nums: Optional[List[str]] = Field(default=None, description="List of site numbers to include")
    parameter_codes: Optional[List[str]] = Field(default=None, description="List of parameter codes to include")
    
    # Generic categorical filters for any column
    custom_filters: Optional[dict] = Field(default=None, description="Custom filters for any column as key-value pairs")
    
    # Result controls
    limit: Optional[int] = Field(default=None, description="Maximum number of rows to return", ge=1)
    columns: Optional[List[str]] = Field(default=None, description="Specific columns to return")

class CSVDatasetFilterResponse(BaseModel):
    """Response model for filtered CSV dataset data"""
    
    data: List[dict] = Field(description="Filtered data records")
    metadata: dict = Field(description="Metadata about the filtered results")
    filter_summary: dict = Field(description="Summary of applied filters")
    
class CSVDatasetAggregateRequest(BaseModel):
    """Request model for aggregated CSV dataset data"""
    
    # Inherit filters from CSVDatasetFilterRequest
    date_from: Optional[date] = Field(default=None, description="Start date (YYYY-MM-DD)")
    date_to: Optional[date] = Field(default=None, description="End date (YYYY-MM-DD)")
    parameter_names: Optional[List[str]] = Field(default=None, description="List of parameter names to include")
    lat_min: Optional[float] = Field(default=None, description="Minimum latitude", ge=-90, le=90)
    lat_max: Optional[float] = Field(default=None, description="Maximum latitude", ge=-90, le=90)
    lng_min: Optional[float] = Field(default=None, description="Minimum longitude", ge=-180, le=180)
    lng_max: Optional[float] = Field(default=None, description="Maximum longitude", ge=-180, le=180)
    
    # Custom filters
    custom_filters: Optional[dict] = Field(default=None, description="Custom filters for any column as key-value pairs")
    
    # Aggregation options
    group_by: List[str] = Field(description="Fields to group by (e.g., ['Parameter Name', 'Date Local'])")
    aggregations: List[str] = Field(
        default=["mean", "min", "max", "count"],
        description="Aggregation functions to apply to measurement columns"
    )
    aggregation_column: Optional[str] = Field(
        default="Sample_Measurement", 
        description="Column to apply aggregation functions to"
    )
    
class CSVDatasetAggregateResponse(BaseModel):
    """Response model for aggregated CSV dataset data"""
    
    data: List[dict] = Field(description="Aggregated data records")
    metadata: dict = Field(description="Metadata about the aggregation")
    group_by: List[str] = Field(description="Fields used for grouping")
    aggregations: List[str] = Field(description="Aggregation functions applied")

class DatasetInfo(BaseModel):
    """Information about a single dataset"""
    
    dataset_id: str = Field(description="Unique dataset identifier/key")
    description: str = Field(description="Human-readable description of the dataset")
    file_path: str = Field(description="Path to the CSV file")
    file_exists: bool = Field(description="Whether the file exists on disk")
    file_size_bytes: Optional[int] = Field(default=None, description="File size in bytes")
    sample_endpoint: str = Field(description="URL to get sample data")

class DatasetListResponse(BaseModel):
    """Response model for listing all available datasets"""
    
    datasets: List[DatasetInfo] = Field(description="List of available datasets")
    total_datasets: int = Field(description="Total number of available datasets")
    api_endpoints: dict = Field(description="Related API endpoints for working with datasets")

# Request model for ingesting CSV data from a URL
class CSVIngestionFromURLRequest(BaseModel):
    """Request model for ingesting CSV data from a URL"""
    
    url: str = Field(title="CSV URL", description="URL to download the CSV file from")
    namespace: str = Field(default="datasets", title="Namespace", description="The namespace to store the CSV data under")
    version: int = Field(default=0, title="Version", description="Version number for the stored objects", ge=0)
    chunk_size: int = Field(default=10000, title="Chunk Size", description="Number of rows to process at once", gt=0)
    filename: Optional[str] = Field(default=None, title="Filename", description="Optional custom filename for the downloaded file (will be auto-generated if not provided)")