import hashlib
import json
from typing import Annotated, Optional

import pandas as pd  # type: ignore
from dspaces import DSConnectionError, DSModuleError, DSRemoteFaultError
from fastapi import APIRouter, Body, File, Form, HTTPException, Path, Query, Response

from api.config import dspaces_settings
from api.helpers.file_download import (
    cleanup_downloaded_file,
    download_csv_from_url,
    validate_csv_file,
)
from api.models.dspaces_model import (
    BoundingBox,
    CSVDatasetAggregateRequest,
    CSVDatasetAggregateResponse,
    CSVDatasetFilterRequest,
    CSVDatasetFilterResponse,
    CSVIngestionFromURLRequest,
    CSVIngestionResponse,
    DatasetInfo,
    DatasetListResponse,
    DSObject,
    DSRegHandle,
    RequestList,
)
from api.services.dspaces_services.filter_csv_data import (
    _create_column_mapping,
    aggregate_csv_dataset,
    filter_csv_dataset,
)
from api.services.dspaces_services.get_dspaces_obj import get_dspaces_obj
from api.services.dspaces_services.get_dspaces_var_obj import get_dspaces_var_obj
from api.services.dspaces_services.get_dspaces_vars import get_dspaces_vars
from api.services.dspaces_services.ingest_csv_data import (
    ingest_csv_to_dspaces,
    retrieve_csv_from_dspaces,
)
from api.services.dspaces_services.mpexec_dspaces_obj import mpexec_dspaces_obj
from api.services.dspaces_services.pexec_dspaces_obj import pexec_dspaces_obj
from api.services.dspaces_services.put_dspaces_obj import put_dspaces_obj
from api.services.dspaces_services.reg_dspaces import reg_dspaces

router = APIRouter()

@router.get("/datasets",
            status_code=200,
            summary="List all available datasets",
            response_model=DatasetListResponse
)
def list_available_datasets() -> DatasetListResponse:
    """
    List all available CSV datasets that can be ingested and queried.
    
    Returns information about each dataset including:
    - Dataset type identifier
    - Description
    - File path and availability
    - Sample data endpoint
    
    This endpoint helps discover what datasets are available for analysis
    and provides the necessary information to work with each dataset.
    """
    from api.models.dspaces_model import BoundingBox, Interval
    from api.services.dspaces_services.get_dspaces_obj import get_dspaces_obj
    
    datasets = []
    
    # Add dynamically ingested datasets from DataSpaces
    try:
        # Get all variables stored in DataSpaces
        all_vars = get_dspaces_vars()
        if all_vars:
            # Find namespaces that have ingestion metadata
            namespaces_with_metadata = set()
            for var in all_vars:
                if var.endswith("\\__ingestion_metadata__"):
                    namespace = var.replace("\\__ingestion_metadata__", "")
                    namespaces_with_metadata.add(namespace)
            
            # For each namespace with metadata, try to retrieve the metadata
            for namespace in namespaces_with_metadata:
                try:
                    # Retrieve the ingestion metadata
                    metadata_box = BoundingBox(bounds=[Interval(start=0, span=1000000)])  # Large enough for metadata
                    metadata_obj = get_dspaces_obj(namespace, "__ingestion_metadata__", 0, metadata_box)
                    
                    if metadata_obj is not None:
                        # Decode and parse metadata
                        metadata_json = metadata_obj.tobytes().decode('utf-8')
                        metadata = json.loads(metadata_json)
                        file_info = metadata.get("file_info", {})
                        
                        # Create dataset info for the ingested dataset
                        original_file_path = file_info.get("file_path", "Unknown")
                        total_rows = file_info.get("total_rows", 0)
                        total_columns = file_info.get("total_columns", 0)
                        
                        # Create a description based on the metadata
                        if original_file_path.startswith("Downloaded from:"):
                            description = f"URL-ingested dataset from {original_file_path.replace('Downloaded from: ', '')}"
                            file_display_path = original_file_path
                        else:
                            description = f"Ingested CSV dataset ({total_rows} rows, {total_columns} columns)"
                            file_display_path = original_file_path
                        
                        # Generate a unique dataset ID for the ingested dataset
                        unique_string = f"ingested_{namespace}_{description}"
                        short_hash = hashlib.md5(unique_string.encode()).hexdigest()[:8]
                        dataset_id = f"ingested_{namespace}_{short_hash}"
                        
                        # Determine the dataset type from namespace or use "ingested-data"
                        if namespace.startswith("datasets"):
                            dataset_type = "ingested-data"
                        else:
                            dataset_type = namespace.replace("\\", "-").replace("/", "-")
                        
                        dataset_info = DatasetInfo(
                            dataset_id=dataset_id,
                            description=description,
                            file_path=file_display_path,
                            file_exists=True,  # Assume true since it's been ingested
                            file_size_bytes=None,  # Not available for ingested datasets
                            sample_endpoint=f"/dspaces/retrieve/{dataset_type}/{namespace}?limit=10"
                        )
                        datasets.append(dataset_info)
                        
                except Exception as e:
                    # Log the error but continue processing other namespaces
                    print(f"Warning: Could not retrieve metadata for namespace {namespace}: {str(e)}")
                    
                    # Fallback: create dataset info without detailed metadata
                    try:
                        # Generate a unique dataset ID for the ingested dataset
                        unique_string = f"ingested_{namespace}_fallback"
                        short_hash = hashlib.md5(unique_string.encode()).hexdigest()[:8]
                        dataset_id = f"ingested_{namespace}_{short_hash}"
                        
                        # Determine the dataset type from namespace or use "ingested-data"
                        if namespace.startswith("datasets"):
                            dataset_type = "ingested-data"
                        else:
                            dataset_type = namespace.replace("\\", "-").replace("/", "-")
                        
                        # Create fallback description
                        description = f"Ingested dataset in namespace '{namespace}' (metadata unavailable)"
                        
                        dataset_info = DatasetInfo(
                            dataset_id=dataset_id,
                            description=description,
                            file_path="Ingested dataset (original file path unavailable)",
                            file_exists=True,  # Assume true since it's been ingested
                            file_size_bytes=None,  # Not available for ingested datasets
                            sample_endpoint=f"/dspaces/retrieve/{dataset_type}/{namespace}?limit=10"
                        )
                        datasets.append(dataset_info)
                    except Exception as fallback_error:
                        print(f"Warning: Could not create fallback dataset info for namespace {namespace}: {str(fallback_error)}")
                    continue
                    
    except Exception as e:
        # If DataSpaces query fails, return empty list since we only support URL ingestion
        print(f"Warning: Could not query DataSpaces for ingested datasets: {str(e)}")
        pass
    
    return DatasetListResponse(
        datasets=datasets,
        total_datasets=len(datasets),
        api_endpoints={
            "sample_data": "/dspaces/ingest/{dataset_type}/sample",
            "ingest_data": "/dspaces/ingest/{dataset_type}",
            "retrieve_data": "/dspaces/retrieve/{dataset_type}/{namespace}",
            "filter_data": "/dspaces/retrieve/{dataset_type}/{namespace}/filter",
            "aggregate_data": "/dspaces/retrieve/{dataset_type}/{namespace}/aggregate",
            "available_filters": "/dspaces/retrieve/{dataset_type}/{namespace}/available-filters"
        }
    )

@router.post("/obj/{obj_name}/{obj_version}",
             summary="Retrieve a DataSpaces object"
)
def ds_get(
    obj_name: Annotated[
        str,
        Path(
            title="Object name",
            description="Object name to query",
            max_length=96
        )
    ],
    obj_version: Annotated[
        int,
        Path(
            title="Object version",
            description="Object version to retrieve",
            ge=0
        )
    ],
    box: Annotated[
        BoundingBox,
        Body(
            title="Bounding box",
            description="Bounding box region to retrieve",
        )
    ],
    namespace: Annotated[
        str,
        Query(
            title="Request namespace",
            description="Request namespace which defines the context of the query",
            max_length=48
        )
    ] = None
):
    """
    Query DataSpaces for a data object:
    
    Parameters
    ----------
    - **namespace**: the namespace within which to search
    - **obj_name**: the name of the object which to query
    - **obj_version**: the version for which to query
    - **box**: the geometric bounds to retrieve. box is a list of integer \
        pairs. The first of the pair defines the start of an interval, and \
        the second the size of the interval. For example, [(1,2),(3,4)] \
        defines the rectangle that starts at (1,3) and has dimensions 2x4 \
        elements.

    Returns
    -------
    An octet-stream of the requested data, serialized in row major order.\
    The response will additionally contain custom headers necessary for \
    deserializing the data into an n-dimensional array, ane localizing it\
    relative to the global domain. These headers are:

    - **X-DS-Tag**: a tag value attached to the data object. This is user-defined, but\
         can generally be interpreted as a numpy data type integer.
    - **X-DS-Element-Size**: size in bytes of each member of the array.
    - **X-DS-Lower-Bounds**: the lower bounds of the requested array.
    - **X-DS-Upper-Bounds**: the upper bounds of the requested array.
    - **X-DS-Dims**: the dimensions of the returned array. **NB**: the returned array\
         might be truncated, projected, etc. relative to the requested bounds. In other\
         words, it may be that X-DS-Dims is not equal to the lower bounds subtracted\
         from the upper bounds; it may not even have the same dimensionality as the bounds.

    Raises
    ------
    **HTTPException** if the object is not found in DataSpaces
    """
    obj_name = obj_name.replace("~", "/")
    data = get_dspaces_obj(
            namespace=namespace,
            name=obj_name,
            version=obj_version,
            box=box,
        )
    if data is None:
        raise HTTPException(status_code=404, detail="could not find the object")
    return(Response(
            content=data.tobytes(),
            headers={
                'X-DS-Tag': str(data.dtype.num),
                'X-DS-Element-Size': str(data.itemsize),
                'X-DS-Lower-Bounds': ','.join([str(b.start) for b in box.bounds]),
                'X-DS-Upper-Bounds': ','.join([str(b.start+sp-1) for (b,sp) in zip(box.bounds, data.shape)]),
                'X-DS-Dims': ','.join([str(x) for x in data.shape])
            },
            media_type='application/octet-stream'
        )
    )

@router.put("/obj/{obj_name}/{obj_version}",
            status_code=200,
            summary="Store a DataSpaces object"
)
def ds_put(
    data: Annotated[
       bytes,
       File(
            title="Object data",
            description="Object data for storage"
        )
    ],
    obj_name: Annotated[
        str,
        Path(
            title="Object name",
            description="Object name to store",
            max_length=96
        )
    ],
    obj_version: Annotated[
        int,
        Path(
            title="Object version",
            description="Object version to store",
            ge=0
        )
    ],
    box: Annotated[
        BoundingBox,
        Form(
            title="Bounding box",
            description="Bounding box region in which to place data",
        )
    ],
    element_size: Annotated[
        int,
        Query(
            title="Element size",
            description="Size of individual element in put data",
            gt=0
        )
    ],
    element_type: Annotated[
        int,
        Query(
            title="Element type",
            description="Element type of data",
            gt=0
        )
    ],
    namespace: Annotated[
        str,
        Query(
            title="Request namespace",
            description="Request namespace which defines the context of the query",
            max_length=48
        )
    ] = None
):
    """
    Store data to DataSpaces
    
    Parameters
    ----------
    - **namespace**: the namespace within which to search
    - **obj_name**: the name of the object which to query
    - **obj_version**: the version for which to query
    - **box**: the geometric bounds to retrieve. box is a list of integer \
        pairs. The first of the pair defines the start of an interval, and \
        the second the size of the interval. For example, [(1,2),(3,4)] \
        defines the rectangle that starts at (1,3) and has dimensions 2x4 \
        elements.
    - **element_size**: the size of element in bytes
    - **element_type**: the type of the elements in the array, using the \
        NumPy type scalar
    - **data**: an array of bytes containing the data to be stored

    Raises
    ------
    **HTTPException** on failure.
    """
    try:
        put_dspaces_obj(namespace, obj_name, obj_version, box, element_size, element_type, data)
        return {'message': "Stored data successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="put failed")

@router.get("/var/",
            status_code=200,
            summary="Get a list of stored variables"
)
def ds_get_vars() -> list[str]:
    """
    Get a list of variables stored in DataSpaces

    Returns
    -------
    A list of strings that hold the names of the variables storged in DataSpaces.

    Raises
    ------
    **HTTPException** on failure.
    """
    vars = get_dspaces_vars()
    if vars is None:
        raise HTTPException(status_code=502, detail="query failed.")
    return vars

@router.get("/var/{obj_name}",
            status_code=200,
            summary="Get a list of stored objects of a given variable name"
)
def ds_get_var_objs(
     obj_name: Annotated[
        str,
        Path(
            title="Object name",
            description="Object name to query",
            max_length=96
        )
    ],
    namespace: Annotated[
        str,
        Query(
            title="Request namespace",
            description="Request namespace which defines the context of the query",
            max_length=48
        )
    ] = None
) -> list[DSObject]:
    """
    Get a list of objects stored for a given variable name.

    Parameters
    ----------
    - **namespace**: the namespace within which to search
    - **obj_name**: the name of the object to query

    Returns
    -------
    A list of objects. Each object is a dict containing:
    - **name** the object's variable name
    - **namespace** (optional) the object's namespace
    - **version** the object's version
    - **bounds** the upper and lower bounds of the object

    Raises
    ------
    **HTTPException** on failure.
    """
    obj_name = obj_name.replace("~", "/")
    objs = get_dspaces_var_obj(namespace, obj_name)
    if objs == []:
        raise HTTPException(status_code=404, detail="could not find any objects")
    return(objs)

if dspaces_settings.dspaces_unsafe_endpoints:
    @router.post("/exec/{obj_name}/{obj_version}",
                status_code=200,
                summary="Perform a single-argument remote execution"
                )
    def ds_pexec(
        fn: Annotated[
            bytes,
            File(
                title="Method",
                description="Dilled python method"
            )
        ],
        obj_name: Annotated[
            str,
            Path(
                title="Object name",
                description="Object name to query",
                max_length=96
            )
        ],
        obj_version: Annotated[
            int,
            Path(
                title="Object version",
                description="Object version to retrieve",
                ge=0
            )
        ],
        box: Annotated[
            BoundingBox,
            Body(
                title="Bounding box",
                description="Bounding box region to retrieve"
            )
        ],
        namespace: Annotated[
            str,
            Query(
                title="Request namespace",
                description="Request namespace which defines the context of the query",
                max_length=48
            )
        ] = None
    ):
        """
        Perform a remote execution operation on a single object.

        Parameters
        ----------
        - **namespace**: the namespace within which to search
        - **obj_name**: the name of the object which to query
        - **obj_version**: the version for which to query
        - **box**: the geometric bounds to retrieve. box is a list of integer \
            pairs. The first of the pair defines the start of an interval, and \
            the second the size of the interval. For example, [(1,2),(3,4)] \
            defines the rectangle that starts at (1,3) and has dimensions 2x4 \
            elements.
        - **fn**: a dill pickled function that takes a single ndarray argument.\
            this function will be executed on the serve with the defined object \
            as its argumenet. 

        Returns
        -------
        The return value of fn as a dill pickled byte string.

        Raises
        ------
        **HTTPException** on failure.
        """
        obj_name = obj_name.replace("~", "/")
        data = pexec_dspaces_obj(
                namespace=namespace,
                name=obj_name,
                version=obj_version,
                box=box,
                fn=fn
            )
        if data is None:
            raise HTTPException(status_code=404, detail="could not find the input data")
        return(Response(
            content=data,
            media_type='application/octet-stream'
            )
        )

    @router.post("/exec/",
                status_code=200,
                summary="Perform a multi-argument remote execution"
                )
    def ds_mpexec(
        fn: Annotated[
            bytes,
            File(
                title="Method",
                description="Dilled python method"
            )
        ],
        requests: Annotated[
            RequestList,
            Body(
                title = "Request list",
                description = "List of requests to pass to fn as arguments"
            )
        ]
    ):
        """
        Perform a remote execution operation on multiple objects object.

        Parameters
        ----------
        - **namespace**: the namespace within which to search
        - **obj_name**: the name of the object which to query
        - **obj_version**: the version for which to query
        - **box**: the geometric bounds to retrieve. box is a list of integer \
            pairs. The first of the pair defines the start of an interval, and \
            the second the size of the interval. For example, [(1,2),(3,4)] \
            defines the rectangle that starts at (1,3) and has dimensions 2x4 \
            elements.
        - **fn**: a dill pickled function that takes a single ndarray argument.\
            this function will be executed on the serve with the defined object \
            as its argumenet. 

        Returns
        -------
        The return value of fn as a dill pickled byte string.

        Raises
        ------
        **HTTPException** on failure.
        """
        data = mpexec_dspaces_obj(
            reqs = requests.requests,
            fn=fn
        )
        if data is None:
            raise HTTPException(status_code=404, detail="could not find the input data")
        return(Response(
                content=data,
                media_type='application/octet-stream'
            )
        )

@router.post("/register/{type}/{name}",
            status_code=200,
            summary="Register a new data source"
            )
def ds_reg(
    type: Annotated[
        str,
        Path(
            title="Registration Type",
            description="The access type for the registration - corresponds to a known DataSpaces module."
        )
    ],
    name: Annotated[
        str,
        Path(
            title="Registration name",
            description="A name unique to the registration."
        )
    ],
    data: Annotated[
        dict,
        Body(
            title="Registration data",
            description="type-specific access parameters."
        )
    ]
) -> DSRegHandle:
    """
    Register an external dataset with DataSpaces for later access
    
    Parameters
    ----------
    - **type**: a label denoting the access method and format of the dataset.\
         This correspond to the module to use to service later queries against\
         this registration.
    - **name**: an identifier for the registration. The (type,name) pair must\
         be unique per registration.
    - **data**: a serialized json-encoded dict stored in the registry. The \
        dict will be passed as a parameter list during query handling of the \
        registered dataset.

    Returns
    -------
    A DSRegHandle, which contains a namespace agaisnt which to make queries \
    for this dataset, and parameters to use to construct the query.

    Raises
     ------
    **HTTPException** on failure.
    """
    try:
        return(reg_dspaces(type, name, data))
    except DSModuleError:
        raise HTTPException(status_code=500, detail="invalid registration type")
    except DSRemoteFaultError:
        raise HTTPException(status_code=500, detail="plugin handling fault")
    except DSConnectionError:
        raise HTTPException(status_code=500, detail="backend server connection failed")


@router.post("/ingest/{dataset_type}/from-url",
             status_code=200,
             summary="Ingest CSV dataset from URL into DataSpaces",
             response_model=CSVIngestionResponse
)
def ingest_csv_dataset_from_url(
    dataset_type: Annotated[
        str,
        Path(
            title="Dataset type",
            description="Type/identifier of the CSV dataset (e.g., 'air-quality', 'environmental-data', etc.)",
            max_length=96
        )
    ],
    request: Annotated[
        CSVIngestionFromURLRequest,
        Body(
            title="URL ingestion request",
            description="Parameters for CSV ingestion from URL"
        )
    ]
) -> CSVIngestionResponse:
    """
    Download a CSV file from a URL and ingest it into DataSpaces.
    
    This endpoint downloads a CSV file from the provided URL, validates it,
    and then ingests it into DataSpaces using the same logic as the regular
    CSV ingestion endpoint. The downloaded file is automatically cleaned up
    after ingestion.
    
    Parameters
    ----------
    - **url**: the URL to download the CSV file from
    - **namespace**: the namespace to store the data under (default: "datasets")
    - **version**: version number for the stored objects (default: 0)
    - **chunk_size**: number of rows to process at once for large files (default: 10000)
    - **filename**: optional custom filename for the downloaded file
    
    Returns
    -------
    A summary of the ingestion process including:
    - **file_path**: path to the downloaded and ingested CSV file
    - **total_rows**: number of rows processed
    - **total_columns**: number of columns processed
    - **columns**: list of column names
    - **namespace**: namespace used for storage
    - **version**: version number used
    - **stored_objects**: detailed information about each stored column
    - **success**: whether the ingestion was successful
    - **message**: summary message
    
    Raises
    ------
    **HTTPException** if the URL is invalid, download fails, or ingestion fails
    """
    
    downloaded_file_path = None
    
    try:
        # Download the CSV file from the URL to the /data directory
        downloaded_file_path = download_csv_from_url(
            url=request.url,
            custom_filename=request.filename,
            download_dir="/data",  # Store downloaded files in /data directory
            timeout=300  # 5 minute timeout
        )
        
        # Validate that the downloaded file is a valid CSV
        validation_result = validate_csv_file(downloaded_file_path)
        if not validation_result['is_valid']:
            raise ValueError(f"Downloaded file is not a valid CSV: {validation_result['error']}")
        
        # Perform the ingestion using the existing logic
        ingestion_result = ingest_csv_to_dspaces(
            csv_file_path=downloaded_file_path,
            namespace=request.namespace,
            version=request.version,
            chunk_size=request.chunk_size
        )
        
        # Count successful storage operations
        successful_objects = len([k for k, v in ingestion_result["stored_objects"].items() if "error" not in v])
        total_objects = len(ingestion_result["stored_objects"])
        
        response = CSVIngestionResponse(
            file_path=f"Downloaded from: {request.url}",
            total_rows=ingestion_result["total_rows"],
            total_columns=ingestion_result["total_columns"],
            columns=ingestion_result["columns"],
            namespace=ingestion_result["namespace"],
            version=ingestion_result["version"],
            stored_objects=ingestion_result["stored_objects"],
            success=successful_objects == total_objects,
            message=f"Successfully downloaded from URL and ingested {successful_objects} out of {total_objects} columns from {dataset_type} dataset"
        )
        
        return response
        
    except ValueError as e:
        # Handle URL download and validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"URL ingestion failed: {str(e)}")
    finally:
        # Always clean up the downloaded file
        if downloaded_file_path:
            cleanup_downloaded_file(downloaded_file_path)


@router.get("/retrieve/{dataset_type}/{namespace}",
            status_code=200,
            summary="Retrieve CSV dataset from DataSpaces as JSON"
)
def retrieve_csv_dataset(
    dataset_type: Annotated[
        str,
        Path(
            title="Dataset type",
            description="Type/identifier of the CSV dataset",
            max_length=96
        )
    ],
    namespace: Annotated[
        str,
        Path(
            title="Namespace",
            description="The namespace where the Salt Lake County data is stored",
            max_length=48
        )
    ],
    version: Annotated[
        int,
        Query(
            title="Version",
            description="Version number of the stored data to retrieve",
            ge=0
        )
    ] = 0,
    limit: Annotated[
        int,
        Query(
            title="Limit",
            description="Maximum number of rows to return (0 for all rows)",
            ge=0
        )
    ] = 0,
    columns: Annotated[
        Optional[str],
        Query(
            title="Columns",
            description="Comma-separated list of column names to retrieve (e.g., 'State Code,County Code,Latitude'). If not specified, all columns are returned."
        )
    ] = None
) -> dict:
    """
    Retrieve and reconstruct the Salt Lake County data from DataSpaces.
    
    Parameters
    ----------
    - **namespace**: the namespace where the data is stored
    - **version**: version number of the data to retrieve (default: 0)
    - **limit**: maximum number of rows to return (0 for all rows, default: 0)
    - **columns**: comma-separated list of specific columns to retrieve (optional)
    
    Returns
    -------
    A dictionary containing:
    - **data**: the reconstructed data as a list of records
    - **metadata**: information about the retrieved dataset
    - **total_rows**: total number of rows
    - **total_columns**: total number of columns (filtered if columns parameter used)
    - **columns**: list of column names (filtered if columns parameter used)
    
    Examples
    --------
    - Get all data: `/retrieve/air-quality/my_namespace`
    - Get specific columns: `/retrieve/air-quality/my_namespace?columns=State Code,County Code,Latitude,Longitude`
    - Get limited rows with specific columns: `/retrieve/environmental-data/my_namespace?limit=100&columns=Parameter Name,Sample Measurement`
    
    Raises
    ------
    **HTTPException** if the data is not found or retrieval fails
    """
    
    try:
        # Parse columns if specified
        requested_columns = None
        if columns:
            requested_columns = [col.strip() for col in columns.split(",")]
        
        # Retrieve the DataFrame from DataSpaces with column filtering
        df = retrieve_csv_from_dspaces(
            namespace=namespace, 
            version=version,
            columns=requested_columns
        )
        
        if df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found in namespace '{namespace}' with version {version}"
            )
        
        # Apply row limit if specified
        if limit > 0:
            df = df.head(limit)
        
        # Convert to JSON-serializable format
        result = {
            "data": df.to_dict(orient="records"),
            "metadata": {
                "namespace": namespace,
                "version": version,
                "retrieved_rows": len(df),
                "limit_applied": limit if limit > 0 else None,
                "columns_filtered": bool(columns),
                "requested_columns": requested_columns if columns else None
            },
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns)
        }
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@router.get("/ingest/{dataset_type}/sample",
            status_code=200,
            summary="Get a sample of the CSV dataset"
)
def get_csv_dataset_sample(
    dataset_type: Annotated[
        str,
        Path(
            title="Dataset type",
            description="Type/identifier of the CSV dataset",
            max_length=96
        )
    ],
    rows: Annotated[
        int,
        Query(
            title="Number of rows",
            description="Number of sample rows to return",
            ge=1,
            le=1000
        )
    ] = 10
) -> dict:
    """
    Get a sample of the CSV dataset data.
    
    Works with dynamically ingested datasets from URLs.
    Retrieves sample data from DataSpaces storage for datasets that have been ingested from URLs.
    
    Parameters
    ----------
    - **rows**: number of sample rows to return (1-1000, default: 10)
    
    Returns
    -------
    A dictionary containing:
    - **sample_data**: the first N rows of the CSV as a list of records
    - **total_rows**: total number of rows in the file/dataset
    - **total_columns**: total number of columns in the file/dataset
    - **columns**: list of column names with their data types
    - **file_info**: information about the CSV file or ingested dataset
    
    Raises
    ------
    **HTTPException** if the dataset is not found or cannot be read
    """
    
    # Check for ingested datasets in DataSpaces
    try:
        import json

        from api.models.dspaces_model import BoundingBox, Interval
        from api.services.dspaces_services.get_dspaces_obj import get_dspaces_obj
        from api.services.dspaces_services.get_dspaces_vars import get_dspaces_vars
        from api.services.dspaces_services.ingest_csv_data import (
            retrieve_csv_from_dspaces,
        )
        
        # Look for ingested datasets that might match the dataset_type
        all_vars = get_dspaces_vars()
        if not all_vars:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset type '{dataset_type}' not found. No datasets have been ingested from URLs yet. Please use the ingest endpoints to load datasets from URLs first."
            )
        
        # Find namespaces that have ingestion metadata
        matching_namespaces = []
        for var in all_vars:
            if var.endswith("\\__ingestion_metadata__"):
                namespace = var.replace("\\__ingestion_metadata__", "")
                # Check if this namespace might match the dataset_type
                # Try various matching strategies:
                # 1. Exact match
                # 2. Namespace contains dataset_type (with underscores)
                # 3. dataset_type contains part of namespace
                dataset_type_normalized = dataset_type.replace("-", "_")
                namespace_normalized = namespace.replace("\\", "_").replace("/", "_")
                
                if (namespace_normalized == dataset_type_normalized or
                    dataset_type_normalized in namespace_normalized or
                    namespace_normalized in dataset_type_normalized or
                    namespace.endswith(dataset_type_normalized) or
                    namespace.startswith(dataset_type_normalized)):
                    matching_namespaces.append(namespace)
        
        if not matching_namespaces:
            # Try fallback: look for any namespaces that might contain data
            # This handles cases where dataset_type doesn't exactly match namespace
            fallback_namespaces = set()
            for var in all_vars:
                if var.endswith("\\__ingestion_metadata__"):
                    namespace = var.replace("\\__ingestion_metadata__", "")
                    fallback_namespaces.add(namespace)
            
            if fallback_namespaces:
                # If we only have one namespace, use it
                if len(fallback_namespaces) == 1:
                    matching_namespaces = list(fallback_namespaces)
                else:
                    available_namespaces = list(fallback_namespaces)
                    raise HTTPException(
                        status_code=404,
                        detail=f"Dataset type '{dataset_type}' not found. Available ingested namespaces: {available_namespaces}"
                    )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Dataset type '{dataset_type}' not found. No ingested datasets available."
                )
        
        # Use the first matching namespace (or the only one)
        namespace = matching_namespaces[0]
        
        # Try to retrieve sample data from the ingested dataset
        try:
            # Get a limited sample from the ingested dataset
            df_sample = retrieve_csv_from_dspaces(namespace=namespace, version=0)
            
            if df_sample.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"Dataset '{dataset_type}' found but contains no data in namespace '{namespace}'"
                )
            
            # Limit to requested number of rows
            df_sample = df_sample.head(rows)
            total_rows = len(df_sample)  # We can't easily get the total without reading everything
            
            # Try to get total row count from metadata if available
            try:
                metadata_box = BoundingBox(bounds=[Interval(start=0, span=1000000)])
                metadata_obj = get_dspaces_obj(namespace, "__ingestion_metadata__", 0, metadata_box)
                if metadata_obj is not None:
                    metadata_json = metadata_obj.tobytes().decode('utf-8')
                    metadata = json.loads(metadata_json)
                    file_info = metadata.get("file_info", {})
                    total_rows = file_info.get("total_rows", len(df_sample))
                    original_file_path = file_info.get("file_path", f"Ingested dataset in namespace '{namespace}'")
                else:
                    original_file_path = f"Ingested dataset in namespace '{namespace}'"
            except Exception:
                original_file_path = f"Ingested dataset in namespace '{namespace}'"
            
            # Get column information
            column_info = {}
            for col in df_sample.columns:
                # Convert sample values to native Python types
                sample_values = df_sample[col].head(3).tolist()
                # Convert numpy types to native Python types
                sample_values = [val.item() if hasattr(val, 'item') else val for val in sample_values]
                
                column_info[col] = {
                    "dtype": str(df_sample[col].dtype),
                    "sample_values": sample_values,
                    "non_null_count": int(df_sample[col].notna().sum())
                }
            
            result = {
                "sample_data": df_sample.to_dict(orient="records"),
                "total_rows": int(total_rows),
                "total_columns": int(len(df_sample.columns)),
                "columns": column_info,
                "file_info": {
                    "file_path": original_file_path,
                    "file_size_bytes": None,  # Not available for ingested datasets
                    "sample_rows_returned": int(len(df_sample)),
                    "data_source": "ingested_dataset",
                    "namespace": namespace
                }
            }
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to retrieve sample from ingested dataset '{dataset_type}' in namespace '{namespace}': {str(e)}"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search for ingested dataset '{dataset_type}': {str(e)}"
        )

@router.get("/retrieve/{dataset_type}/{namespace}/filter",
            status_code=200,
            summary="Filter CSV dataset with advanced criteria",
            response_model=CSVDatasetFilterResponse
)
def filter_csv_dataset_data(
    dataset_type: Annotated[
        str,
        Path(
            title="Dataset type",
            description="Type/identifier of the CSV dataset",
            max_length=96
        )
    ],
    namespace: Annotated[
        str,
        Path(
            title="Namespace",
            description="The namespace where the CSV dataset is stored",
            max_length=48
        )
    ],
    version: Annotated[
        int,
        Query(
            title="Version",
            description="Version number of the stored data to retrieve",
            ge=0
        )
    ] = 0,
    # Date/Time filters
    date_from: Annotated[
        Optional[str],
        Query(
            title="Date From",
            description="Start date filter (YYYY-MM-DD format)"
        )
    ] = None,
    date_to: Annotated[
        Optional[str],
        Query(
            title="Date To", 
            description="End date filter (YYYY-MM-DD format)"
        )
    ] = None,
    time_from: Annotated[
        Optional[str],
        Query(
            title="Time From",
            description="Start time filter (HH:MM format)"
        )
    ] = None,
    time_to: Annotated[
        Optional[str],
        Query(
            title="Time To",
            description="End time filter (HH:MM format)"
        )
    ] = None,
    # Numeric filters
    measurement_min: Annotated[
        Optional[float],
        Query(
            title="Measurement Min",
            description="Minimum sample measurement value"
        )
    ] = None,
    measurement_max: Annotated[
        Optional[float],
        Query(
            title="Measurement Max",
            description="Maximum sample measurement value"
        )
    ] = None,
    # Geographic filters
    lat_min: Annotated[
        Optional[float],
        Query(
            title="Latitude Min",
            description="Minimum latitude",
            ge=-90,
            le=90
        )
    ] = None,
    lat_max: Annotated[
        Optional[float],
        Query(
            title="Latitude Max",
            description="Maximum latitude",
            ge=-90,
            le=90
        )
    ] = None,
    lng_min: Annotated[
        Optional[float],
        Query(
            title="Longitude Min",
            description="Minimum longitude",
            ge=-180,
            le=180
        )
    ] = None,
    lng_max: Annotated[
        Optional[float],
        Query(
            title="Longitude Max",
            description="Maximum longitude",
            ge=-180,
            le=180
        )
    ] = None,
    # Categorical filters
    parameter_names: Annotated[
        Optional[str],
        Query(
            title="Parameter Names",
            description="Comma-separated list of parameter names (e.g., 'Nitrogen dioxide (NO2),Ozone')"
        )
    ] = None,
    state_codes: Annotated[
        Optional[str],
        Query(
            title="State Codes",
            description="Comma-separated list of state codes (e.g., '49,06')"
        )
    ] = None,
    county_codes: Annotated[
        Optional[str],
        Query(
            title="County Codes",
            description="Comma-separated list of county codes (e.g., '035,037')"
        )
    ] = None,
    site_nums: Annotated[
        Optional[str],
        Query(
            title="Site Numbers",
            description="Comma-separated list of site numbers"
        )
    ] = None,
    parameter_codes: Annotated[
        Optional[str],
        Query(
            title="Parameter Codes",
            description="Comma-separated list of parameter codes"
        )
    ] = None,
    # Result controls
    limit: Annotated[
        Optional[int],
        Query(
            title="Limit",
            description="Maximum number of rows to return",
            ge=1
        )
    ] = None,
    columns: Annotated[
        Optional[str],
        Query(
            title="Columns",
            description="Comma-separated list of column names to return"
        )
    ] = None
) -> CSVDatasetFilterResponse:
    """
    Filter Salt Lake County data using advanced criteria.
    
    This endpoint allows filtering the dataset by:
    - **Date/Time ranges**: Filter by specific date and time ranges
    - **Measurement values**: Filter by min/max sample measurement values
    - **Geographic bounds**: Filter by latitude/longitude bounding box
    - **Categorical values**: Filter by parameter names, codes, locations
    - **Result controls**: Limit rows and select specific columns
    
    Examples:
    - High pollution readings: `measurement_min=50`
    - Winter months: `date_from=2016-12-01&date_to=2016-02-29`
    - Peak hours: `time_from=07:00&time_to=09:00`
    - Downtown area: `lat_min=40.7&lat_max=40.8&lng_min=-111.9&lng_max=-111.8`
    - NO2 only: `parameter_names=Nitrogen dioxide (NO2)`
    
    Returns
    -------
    Filtered data with metadata including:
    - **data**: Array of filtered records
    - **metadata**: Information about filtering results
    - **filter_summary**: Summary of applied filters
    
    Raises
    ------
    **HTTPException** if the data is not found or filtering fails
    """
    
    try:
        # Parse comma-separated lists
        parsed_parameter_names = None
        if parameter_names:
            parsed_parameter_names = [name.strip() for name in parameter_names.split(",")]
        
        parsed_state_codes = None
        if state_codes:
            parsed_state_codes = [code.strip() for code in state_codes.split(",")]
            
        parsed_county_codes = None
        if county_codes:
            parsed_county_codes = [code.strip() for code in county_codes.split(",")]
            
        parsed_site_nums = None
        if site_nums:
            parsed_site_nums = [num.strip() for num in site_nums.split(",")]
            
        parsed_parameter_codes = None
        if parameter_codes:
            parsed_parameter_codes = [code.strip() for code in parameter_codes.split(",")]
            
        parsed_columns = None
        if columns:
            parsed_columns = [col.strip() for col in columns.split(",")]
        
        # Parse dates
        from datetime import datetime
        parsed_date_from = None
        parsed_date_to = None
        
        if date_from:
            try:
                parsed_date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid date format for date_from: {date_from}. Use YYYY-MM-DD.")
                
        if date_to:
            try:
                parsed_date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid date format for date_to: {date_to}. Use YYYY-MM-DD.")
        
        # Create filter request
        filter_request = CSVDatasetFilterRequest(
            date_from=parsed_date_from,
            date_to=parsed_date_to,
            time_from=time_from,
            time_to=time_to,
            measurement_min=measurement_min,
            measurement_max=measurement_max,
            lat_min=lat_min,
            lat_max=lat_max,
            lng_min=lng_min,
            lng_max=lng_max,
            parameter_names=parsed_parameter_names,
            state_codes=parsed_state_codes,
            county_codes=parsed_county_codes,
            site_nums=parsed_site_nums,
            parameter_codes=parsed_parameter_codes,
            limit=limit,
            columns=parsed_columns
        )
        
        # Apply filters
        result = filter_csv_dataset(namespace, filter_request, version)
        
        return CSVDatasetFilterResponse(
            data=result["data"],
            metadata=result["metadata"],
            filter_summary=result["filter_summary"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filtering failed: {str(e)}")

@router.post("/retrieve/{dataset_type}/{namespace}/filter",
             status_code=200,
             summary="Filter CSV dataset with JSON criteria",
             response_model=CSVDatasetFilterResponse
)
def filter_csv_dataset_data_json(
    dataset_type: Annotated[
        str,
        Path(
            title="Dataset type",
            description="Type/identifier of the CSV dataset",
            max_length=96
        )
    ],
    namespace: Annotated[
        str,
        Path(
            title="Namespace",
            description="The namespace where the Salt Lake County data is stored",
            max_length=48
        )
    ],
    filter_request: Annotated[
        CSVDatasetFilterRequest,
        Body(
            title="Filter criteria",
            description="JSON object containing filtering criteria"
        )
    ],
    version: Annotated[
        int,
        Query(
            title="Version",
            description="Version number of the stored data to retrieve",
            ge=0
        )
    ] = 0
) -> CSVDatasetFilterResponse:
    """
    Filter Salt Lake County data using JSON criteria.
    
    This endpoint accepts a JSON body with filtering criteria, allowing for more
    complex filter combinations than the query parameter version.
    
    Request Body Example:
    ```json
    {
        "date_from": "2016-01-01",
        "date_to": "2016-01-31", 
        "measurement_min": 25.0,
        "parameter_names": ["Nitrogen dioxide (NO2)", "Ozone"],
        "lat_min": 40.7,
        "lat_max": 40.8,
        "limit": 1000,
        "columns": ["Date Local", "Parameter Name", "Sample Measurement", "Latitude", "Longitude"]
    }
    ```
    
    Returns
    -------
    Filtered data with metadata including:
    - **data**: Array of filtered records
    - **metadata**: Information about filtering results  
    - **filter_summary**: Summary of applied filters
    
    Raises
    ------
    **HTTPException** if the data is not found or filtering fails
    """
    
    try:
        # Apply filters
        result = filter_csv_dataset(namespace, filter_request, version)
        
        return CSVDatasetFilterResponse(
            data=result["data"],
            metadata=result["metadata"],
            filter_summary=result["filter_summary"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filtering failed: {str(e)}")

@router.post("/retrieve/{dataset_type}/{namespace}/aggregate",
             status_code=200,
             summary="Get aggregated CSV dataset data",
             response_model=CSVDatasetAggregateResponse
)
def aggregate_csv_dataset_data(
    dataset_type: Annotated[
        str,
        Path(
            title="Dataset type",
            description="Type/identifier of the CSV dataset",
            max_length=96
        )
    ],
    namespace: Annotated[
        str,
        Path(
            title="Namespace",
            description="The namespace where the Salt Lake County data is stored",
            max_length=48
        )
    ],
    aggregate_request: Annotated[
        CSVDatasetAggregateRequest,
        Body(
            title="Aggregation criteria",
            description="JSON object containing aggregation criteria"
        )
    ],
    version: Annotated[
        int,
        Query(
            title="Version",
            description="Version number of the stored data to retrieve",
            ge=0
        )
    ] = 0
) -> CSVDatasetAggregateResponse:
    """
    Get aggregated Salt Lake County data.
    
    This endpoint performs aggregations on the dataset, allowing you to get
    statistics grouped by specific fields.
    
    Request Body Example:
    ```json
    {
        "date_from": "2016-01-01",
        "date_to": "2016-12-31",
        "parameter_names": ["Nitrogen dioxide (NO2)"],
        "group_by": ["Parameter Name", "Date Local"],
        "aggregations": ["mean", "min", "max", "count"]
    }
    ```
    
    Available aggregations:
    - **mean**: Average sample measurement
    - **min**: Minimum sample measurement
    - **max**: Maximum sample measurement
    - **count**: Number of measurements
    - **std**: Standard deviation
    - **median**: Median value
    
    Returns
    -------
    Aggregated data including:
    - **data**: Array of aggregated records
    - **metadata**: Information about the aggregation
    - **group_by**: Fields used for grouping
    - **aggregations**: Functions applied
    
    Raises
    ------
    **HTTPException** if the data is not found or aggregation fails
    """
    
    try:
        # Apply aggregation
        result = aggregate_csv_dataset(namespace, aggregate_request, version)
        
        return CSVDatasetAggregateResponse(
            data=result["data"],
            metadata=result["metadata"],
            group_by=result["group_by"],
            aggregations=result["aggregations"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aggregation failed: {str(e)}")

@router.get("/retrieve/{dataset_type}/{namespace}/available-filters",
            status_code=200,
            summary="Get available filter values for CSV dataset"
)
def get_available_filter_values(
    dataset_type: Annotated[
        str,
        Path(
            title="Dataset type",
            description="Type/identifier of the CSV dataset",
            max_length=96
        )
    ],
    namespace: Annotated[
        str,
        Path(
            title="Namespace",
            description="The namespace where the Salt Lake County data is stored",
            max_length=48
        )
    ],
    version: Annotated[
        int,
        Query(
            title="Version",
            description="Version number of the stored data to retrieve",
            ge=0
        )
    ] = 0
) -> dict:
    """
    Get available values for categorical filters.
    
    This endpoint returns unique values for categorical fields that can be used
    in filtering, helping users understand what filter values are available.
    
    Returns
    -------
    A dictionary containing unique values for:
    - **parameter_names**: Available parameter names
    - **state_codes**: Available state codes
    - **county_codes**: Available county codes
    - **site_nums**: Available site numbers
    - **parameter_codes**: Available parameter codes
    - **date_range**: Min and max dates in the dataset
    - **measurement_range**: Min and max sample measurements
    - **geographic_bounds**: Min/max latitude and longitude
    
    Raises
    ------
    **HTTPException** if the data is not found
    """
    
    try:
        # Retrieve a small sample to get available values
        df = retrieve_csv_from_dspaces(namespace=namespace, version=version)
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found in namespace '{namespace}' with version {version}"
            )
        
        # Create column mapping for consistent field access
        column_mapping = _create_column_mapping()
        
        # Helper function to get column data safely
        def get_column_data(field_name, original_name=None):
            """Get column data using either cleaned or original column name"""
            if original_name and original_name in df.columns:
                return df[original_name]
            elif field_name in df.columns:
                return df[field_name]
            elif field_name in column_mapping and column_mapping[field_name] in df.columns:
                return df[column_mapping[field_name]]
            return None
        
        # Get unique values for categorical fields using consistent column access
        result = {}
        
        # Parameter names
        param_data = get_column_data("parameter_name", "Parameter Name")
        if param_data is not None:
            result["parameter_names"] = sorted(param_data.dropna().unique().tolist())
        else:
            result["parameter_names"] = []
        
        # State codes
        state_data = get_column_data("state_code", "State Code")
        if state_data is not None:
            result["state_codes"] = sorted(state_data.dropna().unique().tolist())
        else:
            result["state_codes"] = []
        
        # County codes
        county_data = get_column_data("county_code", "County Code")
        if county_data is not None:
            result["county_codes"] = sorted(county_data.dropna().unique().tolist())
        else:
            result["county_codes"] = []
        
        # Site numbers
        site_data = get_column_data("site_num", "Site Num")
        if site_data is not None:
            result["site_nums"] = sorted(site_data.dropna().unique().tolist())
        else:
            result["site_nums"] = []
        
        # Parameter codes
        param_code_data = get_column_data("parameter_code", "Parameter Code")
        if param_code_data is not None:
            result["parameter_codes"] = sorted(param_code_data.dropna().unique().tolist())
        else:
            result["parameter_codes"] = []
        
        # Get date range
        date_data = get_column_data("date_local", "Date Local")
        if date_data is not None:
            date_series = pd.to_datetime(date_data, errors='coerce')
            valid_dates = date_series.dropna()
            if not valid_dates.empty:
                result["date_range"] = {
                    "min": valid_dates.min().strftime("%Y-%m-%d"),
                    "max": valid_dates.max().strftime("%Y-%m-%d")
                }
        
        # Get measurement range
        measurement_data = get_column_data("sample_measurement", "Sample Measurement")
        if measurement_data is not None:
            measurement_series = pd.to_numeric(measurement_data, errors='coerce')
            valid_measurements = measurement_series.dropna()
            if not valid_measurements.empty:
                result["measurement_range"] = {
                    "min": float(valid_measurements.min()),
                    "max": float(valid_measurements.max())
                }
        
        # Get geographic bounds
        lat_data = get_column_data("latitude", "Latitude")
        lng_data = get_column_data("longitude", "Longitude")
        
        if lat_data is not None and lng_data is not None:
            lat_series = pd.to_numeric(lat_data, errors='coerce')
            lng_series = pd.to_numeric(lng_data, errors='coerce')
            
            valid_lat = lat_series.dropna()
            valid_lng = lng_series.dropna()
            
            if not valid_lat.empty and not valid_lng.empty:
                result["geographic_bounds"] = {
                    "lat_min": float(valid_lat.min()),
                    "lat_max": float(valid_lat.max()),
                    "lng_min": float(valid_lng.min()),
                    "lng_max": float(valid_lng.max())
                }
        
        # Add metadata with column information
        available_columns = list(df.columns)
        result["metadata"] = {
            "namespace": namespace,
            "version": version,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "available_columns": available_columns,
            "column_format": "original" if "Parameter Name" in available_columns else "cleaned"
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available filter values: {str(e)}")

@router.get("/joel", summary="Joel route")
def joel():
    import logging

    import numpy as np
    import pandas as pd

    from api.helpers.dspaces_client import get_client
    from api.models.dspaces_model import BoundingBox, Interval
    from api.services.dspaces_services.get_dspaces_var_obj import get_dspaces_var_obj
    from api.services.dspaces_services.put_dspaces_obj import put_dspaces_obj

    # Set up logging
    logger = logging.getLogger(__name__)

    # Utility function to store DataFrame column in DataSpaces
    def store_dataframe_column(df, col_name, namespace, version):
        """Store a single DataFrame column in DataSpaces"""
        logger.info(f"Storing column {col_name} in DataSpaces")

        # Handle different data types appropriately
        if df[col_name].dtype == "object":  # String columns
            # Convert strings to bytes for storage
            col_data = np.array([str(x).encode("utf-8") for x in df[col_name]])
            element_type = 1  # np.uint8.num (byte data)
            element_size = 1  # Size of uint8

            # Store string lengths to enable reconstruction
            str_lengths = np.array([len(x) for x in col_data], dtype=np.int32)

            # Store string lengths metadata
            lengths_box = BoundingBox(bounds=[Interval(start=0, span=len(str_lengths))])
            put_dspaces_obj(
                namespace=namespace,
                name=f"{col_name}_lengths",
                version=version,
                box=lengths_box,
                element_size=str_lengths.itemsize,
                element_type=str_lengths.dtype.num,
                data=str_lengths.tobytes(),
            )

            # Each string could have different length, flatten the array
            flat_data = np.concatenate(
                [np.frombuffer(x, dtype=np.uint8) for x in col_data]
            )
        else:
            # For numeric columns
            col_data = df[col_name].to_numpy()
            element_type = col_data.dtype.num
            element_size = col_data.itemsize
            flat_data = col_data

        # Create bounding box for this column
        box = BoundingBox(bounds=[Interval(start=0, span=len(flat_data))])

        # Store the column data in DataSpaces
        put_dspaces_obj(
            namespace=namespace,
            name=col_name,
            version=version,
            box=box,
            element_size=element_size,
            element_type=element_type,
            data=flat_data.tobytes(),
        )
        
        # Return metadata for verification
        return {
            "data": flat_data.tobytes(),
            "element_type": element_type,
            "element_size": element_size,
            "box": box,
            "is_string": df[col_name].dtype == "object"
        }

    # Utility function to verify DataSpaces data against original
    def verify_dataframe_column(col_name, namespace, original_info):
        """Verify DataSpaces column data against original"""
        logger.info(f"Verifying column {col_name} from DataSpaces")

        # Get objects for this column
        objects = get_dspaces_var_obj(namespace=namespace, name=col_name)

        # Check that objects exist
        if not objects:
            logger.error(f"No objects found for column {col_name}")
            assert len(objects) > 0, f"No objects found for column {col_name}"

        # Get the latest version
        latest_obj = max(objects, key=lambda x: x.version)
        
        # Get the bounds for retrieval
        lb = tuple([b.start for b in latest_obj.bounds])
        ub = tuple([(b.start + b.span) - 1 for b in latest_obj.bounds])
        
        # Fetch the actual data
        client = get_client()
        timeout = -1  # -1 means wait indefinitely
        fetched_data = client.Get(latest_obj.name, latest_obj.version, lb, ub, timeout)
        
        # Check that data was retrieved
        if fetched_data is None:
            logger.error(f"Failed to fetch data for column {col_name}")
            assert fetched_data is not None, f"Failed to fetch data for column {col_name}"

        # Get the original data info for comparison
        original_data = original_info["data"]
        element_type = original_info["element_type"]

        # Verify data integrity based on data type
        if element_type == 1:  # String/byte data
            if len(fetched_data) != len(original_data):
                logger.error(f"Data length mismatch for column {col_name}")
                assert len(fetched_data) == len(original_data), f"Data length mismatch for column {col_name}"
        else:  # Numeric data
            # Convert to numpy arrays for comparison
            dtype = np.dtype(np.sctypeDict.get(element_type))
            fetched_array = np.frombuffer(fetched_data, dtype=dtype)
            original_array = np.frombuffer(original_data, dtype=dtype)

            if len(fetched_array) != len(original_array):
                logger.error(f"Data length mismatch for column {col_name}: fetched={len(fetched_array)}, original={len(original_array)}")
                assert len(fetched_array) == len(original_array), f"Data length mismatch for column {col_name}"

            # Check array content equality
            try:
                np.testing.assert_array_equal(fetched_array, original_array)
            except AssertionError as e:
                logger.error(f"Data content mismatch for column {col_name}: {e}")
                raise

        logger.info(f"Verification successful for column {col_name}")
        return "Success"

    # Utility function to reconstruct a DataFrame from DataSpaces
    def reconstruct_dataframe(columns, namespace, version):
        """Reconstruct a DataFrame from columns stored in DataSpaces"""
        logger.info(f"Reconstructing DataFrame from {len(columns)} columns")

        df_data = {}
        client = get_client()
        timeout = -1  # -1 means wait indefinitely

        for col_name in columns:
            try:
                # Get object metadata
                objects = get_dspaces_var_obj(namespace=namespace, name=col_name)

                if not objects:
                    logger.error(f"No objects found for column {col_name}")
                    continue

                logger.info(f"Found {len(objects)} objects for column {col_name}")

                # Get the specified version or the latest if not found
                col_obj = next((obj for obj in objects if obj.version == version), None)
                if col_obj is None:
                    col_obj = max(objects, key=lambda x: x.version)

                # Get bounds for retrieval
                lb = tuple([b.start for b in col_obj.bounds])
                ub = tuple([(b.start + b.span) - 1 for b in col_obj.bounds])

                logger.info(f"Retrieving data for column {col_name}, bounds: {lb} to {ub}")

                # Fetch the actual data
                fetched_data = client.Get(col_obj.name, col_obj.version, lb, ub, timeout)
                if fetched_data is None:
                    logger.error(f"Failed to fetch data for column {col_name}")
                    continue

                logger.info(f"Successfully fetched {len(fetched_data)} bytes for column {col_name}")

                # Check if this is a string column by looking for _lengths metadata
                length_objects = get_dspaces_var_obj(namespace=namespace, name=f"{col_name}_lengths")

                logger.info(f"Column {col_name}: {'Found' if length_objects else 'Did not find'} _lengths metadata")

                if length_objects:
                    # It's a string column - need to reconstruct from bytes and lengths
                    # Get the string lengths object
                    length_obj = next((obj for obj in length_objects if obj.version == version), None)
                    if length_obj is None:
                        length_obj = max(length_objects, key=lambda x: x.version)

                    # Get bounds for retrieval
                    lb_len = tuple([b.start for b in length_obj.bounds])
                    ub_len = tuple([(b.start + b.span) - 1 for b in length_obj.bounds])

                    logger.info(f"Retrieving length data for column {col_name}, bounds: {lb_len} to {ub_len}")

                    # Fetch the lengths data
                    lengths_data = client.Get(length_obj.name, length_obj.version, lb_len, ub_len, timeout)
                    if lengths_data is None:
                        logger.error(f"Failed to fetch length data for string column {col_name}")
                        continue

                    # Convert to numpy array
                    lengths = np.frombuffer(lengths_data, dtype=np.int32)

                    logger.info(f"Got {len(lengths)} string lengths for column {col_name}: {lengths}")

                    # Reconstruct strings from flat byte array
                    strings = []
                    pos = 0
                    for i, length in enumerate(lengths):
                        if pos + length > len(fetched_data):
                            logger.error(f"Out of bounds error at position {pos}, length {length}, data size {len(fetched_data)}")
                            break

                        string_bytes = fetched_data[pos:pos+length]
                        strings.append(string_bytes.decode('utf-8'))
                        logger.debug(f"Reconstructed string {i}: '{strings[-1]}' (length {length})")
                        pos += length

                    logger.info(f"Reconstructed {len(strings)} strings for column {col_name}")
                    df_data[col_name] = strings
                else:
                    # It's a numeric column
                    # First, check if we have information about the element type
                    # In a real scenario, it's better to store dtype information separately
                    if col_name == "Age":
                        # For this example, we know Age is an integer
                        array = np.frombuffer(fetched_data, dtype=np.int64)
                        df_data[col_name] = array.tolist()  # Convert to list for DataFrame construction
                        logger.info(f"Processed numeric column {col_name} as int64: {array.tolist()}")
                    else:
                        # Try common numeric types in order of likelihood
                        for dtype_try in [np.int32, np.int64, np.float32, np.float64]:
                            try:
                                array = np.frombuffer(fetched_data, dtype=dtype_try)
                                df_data[col_name] = array.tolist()  # Convert to list for DataFrame construction
                                logger.info(f"Processed numeric column {col_name} as {dtype_try}: {array.tolist()}")
                                break
                            except Exception:
                                continue

            except Exception as e:
                logger.error(f"Error reconstructing column {col_name}: {str(e)}")
                continue

        # Create pandas DataFrame from reconstructed data
        logger.info(f"Reconstructed data keys: {list(df_data.keys())}")
        logger.info(f"Reconstructed data: {df_data}")
        return pd.DataFrame(df_data)

    # Create a sample pandas DataFrame
    logger.info("Creating sample DataFrame")
    data = {
        "Name": ["Bo", "Philip", "Saleem", "Jess"],
        "Age": [28, 34, 29, 42],
        "City": ["New York", "Boston", "Chicago", "Denver"],
    }
    df = pd.DataFrame(data)

    # Handle edge case: empty DataFrame
    if df.empty:
        logger.warning("Empty DataFrame provided, returning early")
        return {"error": "Empty DataFrame cannot be processed"}

    # Process each column and store in DataSpaces
    namespace = "joel_dataframe"
    version = 0
    stored_columns = {}

    # Store each column in DataSpaces
    for col in df.columns:
        try:
            stored_columns[col] = store_dataframe_column(df, col, namespace, version)
            logger.info(f"Successfully stored column {col}")
        except Exception as e:
            logger.error(f"Failed to store column {col}: {str(e)}")
            return {"error": f"Failed to store column {col}: {str(e)}"}

    # Verify all stored columns
    verification_results = {}
    for col in df.columns:
        try:
            verification_results[col] = verify_dataframe_column(col, namespace, stored_columns[col])
        except Exception as e:
            logger.error(f"Verification failed for column {col}: {str(e)}")
            verification_results[col] = f"Failed: {str(e)}"

    logger.info("DataFrame processing and verification complete")

    # Demonstrate DataFrame reconstruction
    try:
        # Use the stored_columns dictionary keys instead of querying DataSpaces
        df_columns = list(stored_columns.keys())
        logger.info(f"Columns to reconstruct from stored_columns: {df_columns}")

        # Reconstruct the DataFrame
        reconstructed_df = reconstruct_dataframe(df_columns, namespace, version)
        logger.info("DataFrame reconstruction successful")

        # Compare with original DataFrame
        logger.info(f"Original DataFrame:\n{df}")
        logger.info(f"Reconstructed DataFrame:\n{reconstructed_df}")

        # Check if the DataFrames are equal
        is_equal = df.equals(reconstructed_df)
        logger.info(f"DataFrames are equal: {is_equal}")

        # Include reconstructed DataFrame in the response
        reconstruction_result = {
            "success": is_equal,
            "reconstructed_data": reconstructed_df.to_dict(orient="records")
        }
    except Exception as e:
        logger.error(f"DataFrame reconstruction failed: {str(e)}")
        reconstruction_result = {
            "success": False,
            "error": str(e)
        }

    # Return the DataFrame as JSON along with verification results
    return {
        "data": df.to_dict(orient="records"),
        "verification": verification_results,
        "reconstruction": reconstruction_result
    }
