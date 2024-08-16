import numpy as np

from api.helpers.dspaces_client import get_client, nspace_name
from api.models.dspaces_model import BoundingBox
from api.helpers.bounding_box import get_box_volume

def put_dspaces_obj(
        namespace: str,
        name: str,
        version: int,
        box: BoundingBox,
        element_size: int,
        element_type: int,
        data: bytes
) -> None:
    '''
    Put a data object into the DataSpaces server

    Parameters
    ----------
    namespace
        The namespace of the request
    name
        The object name
    version
        The object version to store
    box
        The space in which to write the data
    element_size
        The number of bytes per element
    element_type
        The type of the elements, referring NumPy scalar types
    data
        An array of bytes containing the data to be written

    Raises
    ------
    ValueError
        If the data does not contain the right number of bytes to fill the box with elements of the given size     
    '''
    client = get_client()
    offset = tuple([b.start for b in box.bounds])
    if len(data) != get_box_volume(box) * element_size:
        raise ValueError("data object does not match size parameters")
    dims = [b.span for b in box.bounds]
    arr = np.ndarray(
        dims, 
        dtype=np.sctypeDict[element_type],
        buffer=data
    )
    name = nspace_name(namespace, name)
    client.Put(arr, name, version, offset)