import numpy as np

from api.helpers.dspaces_client import nspace_name, get_client
from api.helpers.bounding_box import get_corners_from_bounds
from api.models.dspaces_model import BoundingBox

def get_dspaces_obj(
                namespace:str, 
                name:str, 
                version:int, 
                box: BoundingBox,
) -> np.ndarray | None:
    '''
    Get a data object from the DataSpaces server
    
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

    Returns
    -------
    An ndarray containing the results, or None if there are no results
    '''
    client = get_client()
    lb,ub = get_corners_from_bounds(box)
    name = nspace_name(namespace, name)
    return(client.Get(name, version, lb, ub, 0))
