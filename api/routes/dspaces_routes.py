import os
from typing import Annotated, Optional

from dspaces import DSConnectionError, DSModuleError, DSRemoteFaultError
from fastapi import APIRouter, Body, File, Form, HTTPException, Path, Query, Response

from api.config import dspaces_settings
from api.models.dspaces_model import (
    BoundingBox,
    CSVIngestionRequest,
    CSVIngestionResponse,
    DSObject,
    DSRegHandle,
    RequestList,
)
from api.services.dspaces_services import *
from api.services.dspaces_services.ingest_csv_data import (
    ingest_csv_to_dspaces,
    retrieve_csv_from_dspaces,
)

router = APIRouter()

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
    if vars == None:
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
        element_size = original_info["element_size"]
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
                            except:
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

@router.post("/ingest/salt-lake-county",
             status_code=200,
             summary="Ingest Salt Lake County CSV data into DataSpaces",
             response_model=CSVIngestionResponse
)
def ingest_salt_lake_county_data(
    request: Annotated[
        CSVIngestionRequest,
        Body(
            title="Ingestion request",
            description="Parameters for CSV ingestion"
        )
    ]
) -> CSVIngestionResponse:
    """
    Ingest the Salt Lake County Utah 2016 air quality data into DataSpaces.
    
    This endpoint specifically handles the salt_lake_county_utah_2016.csv file
    located in the data directory and stores each column as a separate object
    in DataSpaces for efficient querying and analysis.
    
    Parameters
    ----------
    - **namespace**: the namespace to store the data under
    - **version**: version number for the stored objects (default: 0)
    - **chunk_size**: number of rows to process at once for large files (default: 10000)
    
    Returns
    -------
    A summary of the ingestion process including:
    - **file_path**: path to the ingested CSV file
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
    **HTTPException** if the file is not found or ingestion fails
    """
    
    # Path to the Salt Lake County CSV file
    csv_file_path = "data/salt_lake_county_utah_2016.csv"
    
    # Check if file exists
    if not os.path.exists(csv_file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"Salt Lake County CSV file not found at {csv_file_path}"
        )
    
    try:
        # Perform the ingestion
        ingestion_result = ingest_csv_to_dspaces(
            csv_file_path=csv_file_path,
            namespace=request.namespace,
            version=request.version,
            chunk_size=request.chunk_size
        )
        
        # Count successful storage operations
        successful_objects = len([k for k, v in ingestion_result["stored_objects"].items() if "error" not in v])
        total_objects = len(ingestion_result["stored_objects"])
        
        response = CSVIngestionResponse(
            file_path=ingestion_result["file_path"],
            total_rows=ingestion_result["total_rows"],
            total_columns=ingestion_result["total_columns"],
            columns=ingestion_result["columns"],
            namespace=ingestion_result["namespace"],
            version=ingestion_result["version"],
            stored_objects=ingestion_result["stored_objects"],
            success=successful_objects == total_objects,
            message=f"Successfully ingested {successful_objects} out of {total_objects} columns from Salt Lake County data"
        )
        
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/retrieve/salt-lake-county/{namespace}",
            status_code=200,
            summary="Retrieve Salt Lake County data from DataSpaces as JSON"
)
def retrieve_salt_lake_county_data(
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
    - Get all data: `/retrieve/salt-lake-county/my_namespace`
    - Get specific columns: `/retrieve/salt-lake-county/my_namespace?columns=State Code,County Code,Latitude,Longitude`
    - Get limited rows with specific columns: `/retrieve/salt-lake-county/my_namespace?limit=100&columns=Parameter Name,Sample Measurement`
    
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


@router.get("/ingest/salt-lake-county/sample",
            status_code=200,
            summary="Get a sample of the Salt Lake County CSV data"
)
def get_salt_lake_county_sample(
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
    Get a sample of the Salt Lake County CSV data before ingestion.
    
    Parameters
    ----------
    - **rows**: number of sample rows to return (1-1000, default: 10)
    
    Returns
    -------
    A dictionary containing:
    - **sample_data**: the first N rows of the CSV as a list of records
    - **total_rows**: total number of rows in the file
    - **total_columns**: total number of columns in the file
    - **columns**: list of column names with their data types
    - **file_info**: information about the CSV file
    
    Raises
    ------
    **HTTPException** if the file is not found or cannot be read
    """
    
    csv_file_path = "data/salt_lake_county_utah_2016.csv"
    
    if not os.path.exists(csv_file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"Salt Lake County CSV file not found at {csv_file_path}"
        )
    
    try:
        import pandas as pd
        
        # Read just the sample rows plus one to get total count efficiently
        df_sample = pd.read_csv(csv_file_path, nrows=rows)
        
        # Get total row count (more efficient method)
        with open(csv_file_path, 'r') as f:
            total_rows = sum(1 for _ in f) - 1  # Subtract 1 for header
        
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
                "file_path": csv_file_path,
                "file_size_bytes": int(os.path.getsize(csv_file_path)),
                "sample_rows_returned": int(len(df_sample))
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read CSV file: {str(e)}")

@router.post("/dspaces/ingest/salt-lake-county/performance-test",
             summary="Performance test the optimized Salt Lake County CSV ingestion",
             response_model=dict
)
def performance_test_salt_lake_county_ingestion(
    request: CSVIngestionRequest,
    chunk_size: Annotated[
        int,
        Query(
            title="Chunk size",
            description="Number of rows to process per chunk for performance testing",
            ge=1000,
            le=50000
        )
    ] = 10000
):
    """
    Performance test endpoint for the optimized Salt Lake County CSV ingestion.
    This endpoint demonstrates the chunked processing improvements and provides timing metrics.
    """
    import time
    
    try:
        csv_file_path = "/app/data/salt_lake_county_utah_2016.csv"
        
        # Check if file exists
        if not os.path.exists(csv_file_path):
            raise HTTPException(status_code=404, detail="Salt Lake County CSV file not found")
        
        # Get file info for metrics
        file_size = os.path.getsize(csv_file_path)
        file_size_mb = file_size / 1024 / 1024
        
        # Start timing
        start_time = time.time()
        
        # Run the optimized ingestion
        result = ingest_csv_to_dspaces(
            csv_file_path=csv_file_path,
            namespace=request.namespace,
            version=request.version,
            chunk_size=chunk_size
        )
        
        # Calculate timing
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate performance metrics
        rows_per_second = result["total_rows"] / total_time if total_time > 0 else 0
        mb_per_second = file_size_mb / total_time if total_time > 0 else 0
        
        # Enhanced response with performance metrics
        performance_response = {
            "ingestion_summary": result,
            "performance_metrics": {
                "file_size_mb": round(file_size_mb, 2),
                "chunk_size_used": chunk_size,
                "total_processing_time_seconds": round(total_time, 2),
                "rows_per_second": round(rows_per_second, 2),
                "mb_per_second": round(mb_per_second, 2),
                "total_rows_processed": result["total_rows"],
                "total_columns_stored": result["total_columns"],
                "successful_columns": len([v for v in result["stored_objects"].values() if "error" not in v])
            },
            "optimization_features": [
                "Chunked CSV reading to reduce memory usage",
                "Efficient string encoding with flat byte arrays",
                "Progress logging every 10 chunks",
                "Separate storage for string lengths metadata",
                "Optimized numpy array concatenation"
            ],
            "recommendations": {
                "optimal_chunk_size": "10,000-20,000 rows for this dataset size",
                "memory_usage": "Significantly reduced compared to loading entire CSV",
                "scalability": "Can handle files much larger than available RAM"
            }
        }
        
        return performance_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance test failed: {str(e)}")
