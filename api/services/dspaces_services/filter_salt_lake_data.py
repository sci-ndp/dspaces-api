"""
Service for filtering Salt Lake County dataset stored in DataSpaces.
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd  # type: ignore

from api.models.dspaces_model import SaltLakeAggregateRequest, SaltLakeFilterRequest
from api.services.dspaces_services.ingest_csv_data import retrieve_csv_from_dspaces

logger = logging.getLogger(__name__)

def _clean_column_name(col_name: str) -> str:
    """Clean column name for DataSpaces storage by removing special characters."""
    return (col_name.replace(" ", "_")
                    .replace("(", "")
                    .replace(")", "")
                    .replace("/", "_")
                    .replace("-", "_"))

def _normalize_column_name(col_name: str) -> str:
    """Normalize column name to cleaned format for internal use."""
    return _clean_column_name(col_name)

def _map_column_names_in_dataframe(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """Map column names in DataFrame to support both original and cleaned names."""
    # Create a copy to avoid modifying the original
    mapped_df = df.copy()
    
    # For each column in the mapping, check if we need to find it by alternative name
    for original_name, cleaned_name in column_mapping.items():
        if original_name not in mapped_df.columns and cleaned_name in mapped_df.columns:
            # If original name not found but cleaned name exists, we're good
            continue
        elif cleaned_name not in mapped_df.columns and original_name in mapped_df.columns:
            # If cleaned name not found but original exists, rename it
            mapped_df = mapped_df.rename(columns={original_name: cleaned_name})
    
    return mapped_df

def _create_column_mapping() -> Dict[str, str]:
    """Create mapping from common original column names to cleaned names."""
    common_columns = {
        "State Code": "State_Code",
        "County Code": "County_Code", 
        "Site Num": "Site_Num",
        "Parameter Code": "Parameter_Code",
        "Parameter Name": "Parameter_Name",
        "Sample Measurement": "Sample_Measurement",
        "Units of Measure": "Units_of_Measure",
        "Date Local": "Date_Local",
        "Time Local": "Time_Local",
        "Date GMT": "Date_GMT",
        "Time GMT": "Time_GMT",
        "Qualifier": "Qualifier",
        "Method Type": "Method_Type",
        "Method Code": "Method_Code",
        "Method Name": "Method_Name",
        "State Name": "State_Name",
        "County Name": "County_Name",
        "Date of Last Change": "Date_of_Last_Change"
    }
    return common_columns

def _normalize_filter_request_columns(filter_request: SaltLakeFilterRequest) -> SaltLakeFilterRequest:
    """Normalize column names in filter request to cleaned format."""
    # Create a copy of the filter request
    normalized_request = SaltLakeFilterRequest(
        date_from=filter_request.date_from,
        date_to=filter_request.date_to,
        time_from=filter_request.time_from,
        time_to=filter_request.time_to,
        measurement_min=filter_request.measurement_min,
        measurement_max=filter_request.measurement_max,
        lat_min=filter_request.lat_min,
        lat_max=filter_request.lat_max,
        lng_min=filter_request.lng_min,
        lng_max=filter_request.lng_max,
        parameter_names=filter_request.parameter_names,
        state_codes=filter_request.state_codes,
        county_codes=filter_request.county_codes,
        site_nums=filter_request.site_nums,
        parameter_codes=filter_request.parameter_codes,
        limit=filter_request.limit,
        columns=None  # Will be set below
    )
    
    # Normalize column names if specified
    if filter_request.columns:
        normalized_columns = [_normalize_column_name(col) for col in filter_request.columns]
        normalized_request.columns = normalized_columns
    
    return normalized_request

def filter_salt_lake_data(
    namespace: str,
    filter_request: SaltLakeFilterRequest,
    version: int = 0
) -> Dict[str, Any]:
    """
    Filter Salt Lake County data based on the provided criteria.
    
    Args:
        namespace: The namespace where the Salt Lake data is stored
        filter_request: The filtering criteria
        version: Version of the data to retrieve
        
    Returns:
        Dict containing filtered data and metadata
    """
    logger.info(f"Filtering Salt Lake data in namespace: {namespace}")
    
    # Step 1: Normalize filter request column names
    normalized_request = _normalize_filter_request_columns(filter_request)
    
    # Step 2: Retrieve the full dataset from DataSpaces
    try:
        # Get only the columns we need for filtering plus any requested columns
        required_columns = _get_required_columns(normalized_request)
        df = retrieve_csv_from_dspaces(
            namespace=namespace,
            version=version,
            columns=required_columns
        )
        
        if df.empty:
            return {
                "data": [],
                "metadata": {
                    "total_rows": 0,
                    "filtered_rows": 0,
                    "columns": [],
                    "namespace": namespace,
                    "version": version
                },
                "filter_summary": _create_filter_summary(filter_request)
            }
            
        original_row_count = len(df)
        logger.info(f"Retrieved {original_row_count} rows from DataSpaces")
        
        # Step 2.5: Ensure column names are properly mapped for filtering
        column_mapping = _create_column_mapping()
        df = _map_column_names_in_dataframe(df, column_mapping)
        
    except Exception as e:
        logger.error(f"Failed to retrieve data from DataSpaces: {str(e)}")
        raise ValueError(f"Failed to retrieve data: {str(e)}")
    
    # Step 3: Apply filters (using normalized request)
    filtered_df = _apply_filters(df, normalized_request)
    filtered_row_count = len(filtered_df)
    
    logger.info(f"Filtered from {original_row_count} to {filtered_row_count} rows")
    
    # Step 4: Apply column selection if specified
    if normalized_request.columns:
        available_columns = [col for col in normalized_request.columns if col in filtered_df.columns]
        if available_columns:
            filtered_df = filtered_df[available_columns]
        else:
            logger.warning(f"None of the requested columns found: {normalized_request.columns}")
            
        # Map back to original column names for response if user requested original names
        if filter_request.columns:
            rename_dict = {}
            for orig_col, cleaned_col in zip(filter_request.columns, normalized_request.columns):
                if cleaned_col in filtered_df.columns and orig_col != cleaned_col:
                    rename_dict[cleaned_col] = orig_col
            if rename_dict:
                filtered_df = filtered_df.rename(columns=rename_dict)
    
    # Step 4: Apply row limit if specified
    if filter_request.limit:
        filtered_df = filtered_df.head(filter_request.limit)
    
    # Step 5: Convert to response format
    return {
        "data": filtered_df.to_dict(orient="records"),
        "metadata": {
            "total_rows": original_row_count,
            "filtered_rows": filtered_row_count,
            "returned_rows": len(filtered_df),
            "columns": list(filtered_df.columns),
            "namespace": namespace,
            "version": version
        },
        "filter_summary": _create_filter_summary(filter_request)
    }

def aggregate_salt_lake_data(
    namespace: str,
    aggregate_request: SaltLakeAggregateRequest,
    version: int = 0
) -> Dict[str, Any]:
    """
    Aggregate Salt Lake County data based on the provided criteria.
    
    Args:
        namespace: The namespace where the Salt Lake data is stored
        aggregate_request: The aggregation criteria
        version: Version of the data to retrieve
        
    Returns:
        Dict containing aggregated data and metadata
    """
    logger.info(f"Aggregating Salt Lake data in namespace: {namespace}")
    
    # Step 1: Create a filter request from aggregate request
    filter_request = SaltLakeFilterRequest(
        date_from=aggregate_request.date_from,
        date_to=aggregate_request.date_to,
        parameter_names=aggregate_request.parameter_names,
        lat_min=aggregate_request.lat_min,
        lat_max=aggregate_request.lat_max,
        lng_min=aggregate_request.lng_min,
        lng_max=aggregate_request.lng_max
    )
    
    # Step 2: Get required columns for aggregation (normalize group_by columns)
    normalized_group_by = [_normalize_column_name(col) for col in aggregate_request.group_by]
    required_columns = normalized_group_by + ["Sample_Measurement"]  # Use underscore version
    additional_required = _get_required_columns(filter_request)
    if additional_required:
        required_columns.extend(additional_required)
    filter_request.columns = required_columns
    
    # Step 3: Get filtered data
    filtered_result = filter_salt_lake_data(namespace, filter_request, version)
    df = pd.DataFrame(filtered_result["data"])
    
    if df.empty:
        return {
            "data": [],
            "metadata": {
                "total_rows": 0,
                "aggregated_groups": 0,
                "namespace": namespace,
                "version": version
            },
            "group_by": aggregate_request.group_by,
            "aggregations": aggregate_request.aggregations
        }
    
    # Step 4: Perform aggregation
    try:
        # Find the correct column name for Sample Measurement (could be with or without underscore)
        measurement_col = None
        for col in df.columns:
            if "sample" in col.lower() and "measurement" in col.lower():
                measurement_col = col
                break
        
        if measurement_col is None:
            raise ValueError("Sample Measurement column not found in retrieved data")
        
        logger.info(f"Using measurement column: {measurement_col}")
        
        # Convert Sample Measurement to numeric
        df[measurement_col] = pd.to_numeric(df[measurement_col], errors='coerce')
        
        # Group by specified columns (use normalized names)
        grouped = df.groupby(normalized_group_by)
        
        # Apply aggregations
        agg_dict = {}
        for agg_func in aggregate_request.aggregations:
            if agg_func == "mean":
                agg_dict[f"Sample Measurement_{agg_func}"] = grouped[measurement_col].mean()
            elif agg_func == "min":
                agg_dict[f"Sample Measurement_{agg_func}"] = grouped[measurement_col].min()
            elif agg_func == "max":
                agg_dict[f"Sample Measurement_{agg_func}"] = grouped[measurement_col].max()
            elif agg_func == "count":
                agg_dict[f"Sample Measurement_{agg_func}"] = grouped[measurement_col].count()
            elif agg_func == "std":
                agg_dict[f"Sample Measurement_{agg_func}"] = grouped[measurement_col].std()
            elif agg_func == "median":
                agg_dict[f"Sample Measurement_{agg_func}"] = grouped[measurement_col].median()
        
        # Combine results
        result_df = pd.DataFrame(agg_dict).reset_index()
        
        # Map back to original column names if they were different
        if aggregate_request.group_by != normalized_group_by:
            rename_dict = {norm_col: orig_col for orig_col, norm_col in zip(aggregate_request.group_by, normalized_group_by)}
            result_df = result_df.rename(columns=rename_dict)
        
        # Fill NaN values with None for JSON serialization
        result_df = result_df.where(pd.notna(result_df), None)
        
        logger.info(f"Created {len(result_df)} aggregated groups")
        
        return {
            "data": result_df.to_dict(orient="records"),
            "metadata": {
                "total_rows": filtered_result["metadata"]["filtered_rows"],
                "aggregated_groups": len(result_df),
                "namespace": namespace,
                "version": version
            },
            "group_by": aggregate_request.group_by,
            "aggregations": aggregate_request.aggregations
        }
        
    except Exception as e:
        logger.error(f"Failed to aggregate data: {str(e)}")
        raise ValueError(f"Aggregation failed: {str(e)}")

def _get_required_columns(filter_request: SaltLakeFilterRequest) -> Optional[List[str]]:
    """Get the columns required for filtering operations."""
    required = set()
    
    # Always need these for filtering - use cleaned column names
    if filter_request.date_from or filter_request.date_to:
        required.add("Date_Local")
    if filter_request.time_from or filter_request.time_to:
        required.add("Time_Local")
    if filter_request.measurement_min is not None or filter_request.measurement_max is not None:
        required.add("Sample_Measurement")
    if filter_request.lat_min is not None or filter_request.lat_max is not None:
        required.add("Latitude")
    if filter_request.lng_min is not None or filter_request.lng_max is not None:
        required.add("Longitude")
    if filter_request.parameter_names:
        required.add("Parameter_Name")
    if filter_request.state_codes:
        required.add("State_Code")
    if filter_request.county_codes:
        required.add("County_Code")
    if filter_request.site_nums:
        required.add("Site_Num")
    if filter_request.parameter_codes:
        required.add("Parameter_Code")
    
    # Add requested columns
    if filter_request.columns:
        required.update(filter_request.columns)
    
    return list(required) if required else None

def _apply_filters(df: pd.DataFrame, filter_request: SaltLakeFilterRequest) -> pd.DataFrame:
    """Apply all filters to the DataFrame."""
    filtered_df = df.copy()
    
    # Date filters
    if filter_request.date_from or filter_request.date_to:
        if "Date_Local" in filtered_df.columns:
            filtered_df["Date_Local"] = pd.to_datetime(filtered_df["Date_Local"], errors='coerce')
            
            if filter_request.date_from:
                filtered_df = filtered_df[filtered_df["Date_Local"] >= pd.to_datetime(filter_request.date_from)]
            if filter_request.date_to:
                filtered_df = filtered_df[filtered_df["Date_Local"] <= pd.to_datetime(filter_request.date_to)]
    
    # Time filters
    if filter_request.time_from or filter_request.time_to:
        if "Time_Local" in filtered_df.columns:
            # Convert time to comparable format (assuming HH:MM)
            def time_to_minutes(time_str):
                try:
                    time_parts = str(time_str).split(':')
                    return int(time_parts[0]) * 60 + int(time_parts[1])
                except Exception:
                    return None
            
            filtered_df["_time_minutes"] = filtered_df["Time_Local"].apply(time_to_minutes)
            
            if filter_request.time_from:
                from_minutes = time_to_minutes(filter_request.time_from)
                if from_minutes is not None:
                    filtered_df = filtered_df[filtered_df["_time_minutes"] >= from_minutes]
            
            if filter_request.time_to:
                to_minutes = time_to_minutes(filter_request.time_to)
                if to_minutes is not None:
                    filtered_df = filtered_df[filtered_df["_time_minutes"] <= to_minutes]
            
            # Remove helper column
            filtered_df = filtered_df.drop(columns=["_time_minutes"], errors='ignore')
    
    # Measurement filters
    if filter_request.measurement_min is not None or filter_request.measurement_max is not None:
        if "Sample_Measurement" in filtered_df.columns:
            filtered_df["Sample_Measurement"] = pd.to_numeric(filtered_df["Sample_Measurement"], errors='coerce')
            
            if filter_request.measurement_min is not None:
                filtered_df = filtered_df[filtered_df["Sample_Measurement"] >= filter_request.measurement_min]
            if filter_request.measurement_max is not None:
                filtered_df = filtered_df[filtered_df["Sample_Measurement"] <= filter_request.measurement_max]
    
    # Geographic filters
    if filter_request.lat_min is not None or filter_request.lat_max is not None:
        if "Latitude" in filtered_df.columns:
            filtered_df["Latitude"] = pd.to_numeric(filtered_df["Latitude"], errors='coerce')
            
            if filter_request.lat_min is not None:
                filtered_df = filtered_df[filtered_df["Latitude"] >= filter_request.lat_min]
            if filter_request.lat_max is not None:
                filtered_df = filtered_df[filtered_df["Latitude"] <= filter_request.lat_max]
    
    if filter_request.lng_min is not None or filter_request.lng_max is not None:
        if "Longitude" in filtered_df.columns:
            filtered_df["Longitude"] = pd.to_numeric(filtered_df["Longitude"], errors='coerce')
            
            if filter_request.lng_min is not None:
                filtered_df = filtered_df[filtered_df["Longitude"] >= filter_request.lng_min]
            if filter_request.lng_max is not None:
                filtered_df = filtered_df[filtered_df["Longitude"] <= filter_request.lng_max]
    
    # Categorical filters
    if filter_request.parameter_names:
        if "Parameter_Name" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Parameter_Name"].isin(filter_request.parameter_names)]
    
    if filter_request.state_codes:
        if "State_Code" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["State_Code"].isin(filter_request.state_codes)]
    
    if filter_request.county_codes:
        if "County_Code" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["County_Code"].isin(filter_request.county_codes)]
    
    if filter_request.site_nums:
        if "Site_Num" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Site_Num"].isin(filter_request.site_nums)]
    
    if filter_request.parameter_codes:
        if "Parameter_Code" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Parameter_Code"].isin(filter_request.parameter_codes)]
    
    return filtered_df

def _create_filter_summary(filter_request: SaltLakeFilterRequest) -> Dict[str, Any]:
    """Create a summary of applied filters."""
    summary: Dict[str, Any] = {}
    
    if filter_request.date_from:
        summary["date_from"] = str(filter_request.date_from)
    if filter_request.date_to:
        summary["date_to"] = str(filter_request.date_to)
    if filter_request.time_from:
        summary["time_from"] = filter_request.time_from
    if filter_request.time_to:
        summary["time_to"] = filter_request.time_to
    if filter_request.measurement_min is not None:
        summary["measurement_min"] = filter_request.measurement_min
    if filter_request.measurement_max is not None:
        summary["measurement_max"] = filter_request.measurement_max
    if filter_request.lat_min is not None:
        summary["lat_min"] = filter_request.lat_min
    if filter_request.lat_max is not None:
        summary["lat_max"] = filter_request.lat_max
    if filter_request.lng_min is not None:
        summary["lng_min"] = filter_request.lng_min
    if filter_request.lng_max is not None:
        summary["lng_max"] = filter_request.lng_max
    if filter_request.parameter_names:
        summary["parameter_names"] = filter_request.parameter_names
    if filter_request.state_codes:
        summary["state_codes"] = filter_request.state_codes
    if filter_request.county_codes:
        summary["county_codes"] = filter_request.county_codes
    if filter_request.site_nums:
        summary["site_nums"] = filter_request.site_nums
    if filter_request.parameter_codes:
        summary["parameter_codes"] = filter_request.parameter_codes
    if filter_request.limit:
        summary["limit"] = filter_request.limit
    if filter_request.columns:
        summary["columns"] = filter_request.columns
    
    return summary
