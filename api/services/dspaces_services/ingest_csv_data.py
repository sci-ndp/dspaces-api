import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from api.models.dspaces_model import BoundingBox, Interval
from api.services.dspaces_services.put_dspaces_obj import put_dspaces_obj

logger = logging.getLogger(__name__)

def ingest_csv_to_dspaces(
    csv_file_path: str,
    namespace: str,
    version: int = 0,
    chunk_size: int = 10000
) -> dict:
    """
    Ingest CSV data into DataSpaces using chunked processing.
    Each column is stored as a separate DataSpaces object.
    
    Args:
        csv_file_path: Path to the CSV file to ingest
        namespace: The namespace to store the data under
        version: Version number for the stored objects (default: 0)
        chunk_size: Number of rows to process at once (default: 10000)
        
    Returns:
        dict: Summary of ingestion results including metadata about stored columns
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If the CSV file is empty or malformed
    """
    
    # Validate file exists
    file_path = Path(csv_file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    logger.info(f"Starting chunked CSV ingestion from {csv_file_path} with chunk_size={chunk_size}")
    
    # Initialize streaming storage
    column_storage: Dict[str, Dict] = {}
    total_rows_processed = 0
    
    try:
        # Read CSV in chunks and process immediately
        chunk_reader = pd.read_csv(csv_file_path, chunksize=chunk_size)
        
        for chunk_idx, chunk in enumerate(chunk_reader):
            logger.info(f"Processing chunk {chunk_idx + 1} with {len(chunk)} rows")
            
            # Initialize column storage on first chunk
            if chunk_idx == 0:
                for col in chunk.columns:
                    clean_col_name = _clean_column_name(col)
                    column_storage[clean_col_name] = {
                        'original_name': col,
                        'dtype': str(chunk[col].dtype),
                        'is_string': chunk[col].dtype == 'object',
                        'byte_arrays': [],
                        'lengths': [],
                        'numeric_data': []
                    }
                    logger.info(f"Initialized column: {col} -> {clean_col_name} (dtype: {chunk[col].dtype})")
            
            # Process each column in this chunk immediately
            for col in chunk.columns:
                clean_col_name = _clean_column_name(col)
                col_storage = column_storage[clean_col_name]
                
                if col_storage['is_string']:
                    # Process string data
                    string_data = chunk[col].astype(str).fillna("")
                    for s in string_data:
                        encoded = s.encode('utf-8')
                        col_storage['byte_arrays'].append(encoded)
                        col_storage['lengths'].append(len(encoded))
                else:
                    # Process numeric data - force measurement columns to float
                    if any(measurement_keyword in col.lower() for measurement_keyword in ['measurement', 'value', 'amount']):
                        # Force measurement columns to float to avoid precision issues
                        numeric_chunk = chunk[col].astype('float64').fillna(0.0).to_numpy()
                    elif chunk[col].dtype in ['float64', 'float32']:
                        numeric_chunk = chunk[col].to_numpy()
                    else:
                        numeric_chunk = chunk[col].fillna(0).to_numpy()
                    col_storage['numeric_data'].append(numeric_chunk)
            
            total_rows_processed += len(chunk)
            
            # Log progress every 5 chunks to avoid spam
            if chunk_idx % 5 == 0 and chunk_idx > 0:
                logger.info(f"Progress: {total_rows_processed} rows processed across {chunk_idx + 1} chunks")
        
        logger.info(f"Finished reading CSV. Total rows: {total_rows_processed}, Columns: {len(column_storage)}")
        
    except Exception as e:
        raise ValueError(f"Failed to read CSV file in chunks: {str(e)}")
    
    if not column_storage:
        raise ValueError("CSV file is empty or has no valid data")
    
    # Store metadata about the ingestion
    ingestion_metadata = {
        "file_path": csv_file_path,
        "total_rows": total_rows_processed,
        "total_columns": len(column_storage),
        "columns": list(column_storage.keys()),
        "namespace": namespace,
        "version": version,
        "stored_objects": {}
    }
    
    # Now process each column's collected data
    for clean_col_name, col_storage in column_storage.items():
        try:
            logger.info(f"Storing column: {clean_col_name}")
            
            if col_storage['is_string']:
                # Handle string columns - concatenate all byte arrays
                all_byte_arrays = col_storage['byte_arrays']
                all_lengths = col_storage['lengths']
                
                # Calculate total length needed
                total_length = sum(all_lengths)
                
                # Create a flat byte array
                flat_data = np.empty(total_length, dtype=np.uint8)
                
                # Fill the flat array efficiently
                pos = 0
                for ba in all_byte_arrays:
                    ba_len = len(ba)
                    flat_data[pos:pos+ba_len] = np.frombuffer(ba, dtype=np.uint8)
                    pos += ba_len
                
                # Store the lengths metadata
                lengths_array = np.array(all_lengths, dtype=np.int32)
                lengths_box = BoundingBox(bounds=[Interval(start=0, span=len(lengths_array))])
                put_dspaces_obj(
                    namespace=namespace,
                    name=f"{clean_col_name}_lengths",
                    version=version,
                    box=lengths_box,
                    element_size=lengths_array.itemsize,
                    element_type=lengths_array.dtype.num,
                    data=lengths_array.tobytes()
                )
                
                # Store the string data
                data_box = BoundingBox(bounds=[Interval(start=0, span=len(flat_data))])
                put_dspaces_obj(
                    namespace=namespace,
                    name=clean_col_name,
                    version=version,
                    box=data_box,
                    element_size=1,  # uint8 size
                    element_type=1,  # np.uint8.num
                    data=flat_data.tobytes()
                )
                
                ingestion_metadata["stored_objects"][clean_col_name] = {
                    "data_type": "string",
                    "total_bytes": len(flat_data),
                    "num_strings": len(lengths_array),
                    "has_lengths_metadata": True
                }
                
            else:
                # Handle numeric columns - concatenate all numeric chunks
                full_column_data = np.concatenate(col_storage['numeric_data'])
                
                # Store numeric data
                data_box = BoundingBox(bounds=[Interval(start=0, span=len(full_column_data))])
                put_dspaces_obj(
                    namespace=namespace,
                    name=clean_col_name,
                    version=version,
                    box=data_box,
                    element_size=full_column_data.itemsize,
                    element_type=full_column_data.dtype.num,
                    data=full_column_data.tobytes()
                )
                
                ingestion_metadata["stored_objects"][clean_col_name] = {
                    "data_type": str(full_column_data.dtype),
                    "total_bytes": full_column_data.nbytes,
                    "num_elements": len(full_column_data),
                    "has_lengths_metadata": False
                }
            
            logger.info(f"Successfully stored column: {clean_col_name}")
            
        except Exception as e:
            logger.error(f"Failed to store column {clean_col_name}: {str(e)}")
            ingestion_metadata["stored_objects"][clean_col_name] = {
                "error": str(e)
            }
    
    # Store overall metadata
    try:
        _store_ingestion_metadata(namespace, version, ingestion_metadata)
        logger.info("Stored ingestion metadata")
    except Exception as e:
        logger.warning(f"Failed to store metadata: {str(e)}")
    
    successful_columns = len([v for v in ingestion_metadata["stored_objects"].values() if "error" not in v])
    logger.info(f"CSV ingestion completed. Stored {successful_columns} columns successfully")
    
    return ingestion_metadata


def _clean_column_name(col_name: str) -> str:
    """Clean column name for DataSpaces storage by removing special characters."""
    return (col_name.replace(" ", "_")
                    .replace("(", "")
                    .replace(")", "")
                    .replace("/", "_")
                    .replace("-", "_"))


def _store_ingestion_metadata(namespace: str, version: int, metadata: dict) -> None:
    """Store ingestion metadata in DataSpaces."""
    metadata_dict = {
        "ingestion_timestamp": pd.Timestamp.now().isoformat(),
        "file_info": metadata
    }
    
    # Convert metadata to JSON string and then to bytes
    metadata_json = json.dumps(metadata_dict)
    metadata_bytes = metadata_json.encode('utf-8')
    
    metadata_box = BoundingBox(bounds=[Interval(start=0, span=len(metadata_bytes))])
    put_dspaces_obj(
        namespace=namespace,
        name="__ingestion_metadata__",
        version=version,
        box=metadata_box,
        element_size=1,  # uint8 size
        element_type=1,  # np.uint8.num
        data=metadata_bytes
    )


def retrieve_csv_from_dspaces(
    namespace: str,
    version: int = 0,
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Retrieve and reconstruct a DataFrame from DataSpaces.
    
    Args:
        namespace: The namespace where the data is stored
        version: Version number of the stored objects (default: 0)
        columns: List of specific column names to retrieve (default: None for all columns)
        
    Returns:
        pd.DataFrame: Reconstructed DataFrame from DataSpaces
        
    Raises:
        ValueError: If metadata is not found or malformed
    """
    from api.services.dspaces_services.get_dspaces_obj import get_dspaces_obj
    from api.services.dspaces_services.get_dspaces_var_obj import get_dspaces_var_obj
    
    logger.info(f"Retrieving CSV data from namespace: {namespace}")
    
    # First, try to get the metadata
    try:
        metadata_box = BoundingBox(bounds=[Interval(start=0, span=1000000)])  # Large enough for metadata
        metadata_obj = get_dspaces_obj(namespace, "__ingestion_metadata__", version, metadata_box)
        
        if metadata_obj is not None:
            # Decode metadata
            metadata_json = metadata_obj.tobytes().decode('utf-8')
            metadata = json.loads(metadata_json)
            file_info = metadata["file_info"]
            columns_info = file_info["stored_objects"]
        else:
            raise ValueError("No ingestion metadata found")
            
    except Exception as e:
        logger.warning(f"Could not retrieve metadata: {str(e)}. Attempting to discover columns...")
        # Fallback: try to discover columns by listing variables
        from api.services.dspaces_services.get_dspaces_vars import get_dspaces_vars
        vars_list = get_dspaces_vars()
        # Filter out length metadata and reconstruct info
        columns_info = {}
        for var in vars_list:
            if var.startswith(f"{namespace}\\") and not var.endswith("_lengths") and var != f"{namespace}\\__ingestion_metadata__":
                col_name = var.replace(f"{namespace}\\", "")
                # Convert clean column name back to original format for fallback
                original_name = col_name.replace("_", " ")
                columns_info[col_name] = {
                    "original_name": original_name,
                    "data_type": "unknown"
                }
    
    # Apply column filtering if specified
    if columns:
        # Convert requested column names to clean names and filter
        requested_clean_names = [_clean_column_name(col) for col in columns]
        # Also create a mapping from clean names back to original requested names
        clean_to_requested = {_clean_column_name(col): col for col in columns}
        
        # Filter columns_info to only include requested columns
        filtered_columns_info = {}
        missing_columns = []
        
        for requested_clean_name in requested_clean_names:
            if requested_clean_name in columns_info:
                filtered_columns_info[requested_clean_name] = columns_info[requested_clean_name]
            else:
                # Try to find by original name
                found = False
                for clean_name, col_info in columns_info.items():
                    if col_info.get("original_name") == clean_to_requested[requested_clean_name]:
                        filtered_columns_info[clean_name] = col_info
                        found = True
                        break
                if not found:
                    missing_columns.append(clean_to_requested[requested_clean_name])
        
        if missing_columns:
            available_original_names = [col_info.get("original_name", clean_name) 
                                     for clean_name, col_info in columns_info.items()]
            raise ValueError(f"Column(s) not found: {missing_columns}. Available columns: {available_original_names}")
        
        columns_info = filtered_columns_info
        logger.info(f"Filtered to {len(columns_info)} requested columns: {list(columns_info.keys())}")
    
    # Reconstruct DataFrame
    df_data = {}
    
    for clean_col_name, col_info in columns_info.items():
        if "error" in col_info:
            continue
            
        try:
            logger.info(f"Retrieving column: {clean_col_name}")
            
            # Get column objects
            col_objects = get_dspaces_var_obj(namespace, clean_col_name)
            if not col_objects:
                logger.warning(f"No objects found for column: {clean_col_name}")
                continue
                
            # Get the specified version or latest
            col_obj = next((obj for obj in col_objects if obj.version == version), None)
            if col_obj is None:
                col_obj = max(col_objects, key=lambda x: x.version)
            
            # Create bounding box for retrieval
            bounds = col_obj.bounds
            retrieve_box = BoundingBox(bounds=bounds)
            
            # Retrieve data
            col_data = get_dspaces_obj(namespace, clean_col_name, col_obj.version, retrieve_box)
            
            if col_data is None:
                logger.warning(f"Failed to retrieve data for column: {clean_col_name}")
                continue
            
            # Check if this is a string column (has lengths metadata)
            lengths_objects = get_dspaces_var_obj(namespace, f"{clean_col_name}_lengths")
            
            if lengths_objects:
                # String column - reconstruct strings
                logger.info(f"Reconstructing string column: {clean_col_name}")
                
                # Get lengths data
                lengths_obj = next((obj for obj in lengths_objects if obj.version == version), None)
                if lengths_obj is None:
                    lengths_obj = max(lengths_objects, key=lambda x: x.version)
                
                lengths_box = BoundingBox(bounds=lengths_obj.bounds)
                lengths_data = get_dspaces_obj(namespace, f"{clean_col_name}_lengths", lengths_obj.version, lengths_box)
                
                if lengths_data is not None:
                    lengths = np.frombuffer(lengths_data.tobytes(), dtype=np.int32)
                    
                    # Reconstruct strings
                    strings = []
                    pos = 0
                    for length in lengths:
                        if pos + length <= len(col_data):
                            string_bytes = col_data[pos:pos+length].tobytes()
                            strings.append(string_bytes.decode('utf-8'))
                            pos += length
                        else:
                            strings.append("")  # Handle truncated data
                    
                    df_data[col_info.get("original_name", clean_col_name)] = strings
                else:
                    logger.warning(f"Failed to retrieve lengths for string column: {clean_col_name}")
            else:
                # Numeric column
                logger.info(f"Processing numeric column: {clean_col_name}")
                
                # Try to determine the data type from the stored data
                data_bytes = col_data.tobytes()
                
                # Check if we have dtype info from metadata
                original_dtype = col_info.get("dtype", "")
                logger.info(f"Column {clean_col_name} original dtype: {original_dtype}")
                
                # Try to use the original dtype first, then fallback to common types
                dtype_priority = []
                if "float" in original_dtype:
                    dtype_priority = [np.float64, np.float32, np.int64, np.int32]
                elif "int" in original_dtype:
                    dtype_priority = [np.int64, np.int32, np.float64, np.float32]
                else:
                    # Default order - prioritize float for lat/lng type columns
                    if any(coord in clean_col_name.lower() for coord in ['lat', 'lng', 'lon', 'latitude', 'longitude']):
                        dtype_priority = [np.float64, np.float32, np.int64, np.int32]
                    else:
                        dtype_priority = [np.float64, np.int64, np.float32, np.int32]
                
                # Try data types in priority order
                for dtype in dtype_priority:
                    try:
                        if len(data_bytes) % dtype().itemsize == 0:
                            array = np.frombuffer(data_bytes, dtype=dtype)
                            df_data[col_info.get("original_name", clean_col_name)] = array
                            logger.info(f"Successfully decoded {clean_col_name} as {dtype}")
                            break
                    except Exception as e:
                        logger.debug(f"Failed to decode {clean_col_name} as {dtype}: {e}")
                        continue
                else:
                    # Fallback to raw bytes
                    logger.warning(f"Could not determine data type for column: {clean_col_name}")
                    df_data[col_info.get("original_name", clean_col_name)] = list(col_data)
            
            logger.info(f"Successfully retrieved column: {clean_col_name}")
            
        except Exception as e:
            logger.error(f"Error retrieving column {clean_col_name}: {str(e)}")
            continue
    
    # Create DataFrame
    df = pd.DataFrame(df_data)
    logger.info(f"Successfully reconstructed DataFrame with {len(df)} rows and {len(df.columns)} columns")
    
    return df
