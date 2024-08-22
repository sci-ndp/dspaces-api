from typing import Annotated
from fastapi import APIRouter, HTTPException, Body, File, Form, Path, Query, Request, Response

from api.models.dspaces_model import BoundingBox, DSObject, RequestList
from api.services.dspaces_services import *

from dspaces import DSModuleError, DSRemoteFaultError, DSConnectionError

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
    Query the DataSpaces fabric for a data object:
    
    - **namespace**: the namespace within which to search
    - **obj_name**: the name of the object which to query
    - **obj_version**: the version for which to query
    - **box**: the geometric bounds to retrieve. box is a list of integer \
        pairs. The first of the pair defines the start of an interval, and \
        the second the size of the interval. For example, [(1,2),(3,4)] \
        defines the rectangle that starts at (1,3) and has dimensions 2x4 \
        elements.
    - **timeout**: query timeout interval. A value of -1 means wait \
        indefinitely, non-negative means fail if not already available.
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
    Store data in the DataSpaces fabric:
    
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
    Get a list of varibles stored in the DataSpaces fabric
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
    - **namespace**: the namespace within which to search
    - **obj_name**: the name of the object which to query
    """
    obj_name = obj_name.replace("~", "/")
    objs = get_dspaces_var_obj(namespace, obj_name)
    if objs == []:
        raise HTTPException(status_code=404, detail="could not find any objects")
    return(objs)

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
    Perform a remote execution operation on stored data:

        
    - **namespace**: the namespace within which to search
    - **obj_name**: the name of the object which to query
    - **obj_version**: the version for which to query
    - **box**: the geometric bounds to retrieve. box is a list of integer \
        pairs. The first of the pair defines the start of an interval, and \
        the second the size of the interval. For example, [(1,2),(3,4)] \
        defines the rectangle that starts at (1,3) and has dimensions 2x4 \
        elements.
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
    Perform a remote execution operation on stored data:
    
    - **requests**: a list of request objects that fn takes as arugments. \
        The list must match fn's signature.
    - **fn**: a python method that takes an ndarray as an argument, \
        serialized using dill
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
):
    try:
        return(reg_dspaces(type, name, data))
    except DSModuleError:
        raise HTTPException(status_code=400, detail="invalid registration type")
    except DSRemoteFaultError:
        raise HTTPException(status_code=500, detail="plugin handling fault")
    except DSConnectionError:
        raise HTTPException(status_code=500, detail="backend server connection failed")