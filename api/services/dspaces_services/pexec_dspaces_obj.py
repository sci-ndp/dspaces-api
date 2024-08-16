import numpy as np
import dill

from api.helpers.dspaces_client import nspace_name, get_client
from api.helpers.bounding_box import get_corners_from_bounds
from api.models.dspaces_model import BoundingBox

def pexec_dspaces_obj(
                namespace:str, 
                name:str, 
                version:int, 
                box: BoundingBox,
                fn: bytes
) -> np.ndarray | None:
    '''
    Get the results of a remote exec from the DataSpaces server
    
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
    timeout
        How long to wait for data to be available: -1 means\
              indefinitely, otherwise fail if not available
    fn
        A dill serialized function to run on the data

    Returns
    -------
    An ndarray containing the results, or None if there are no results
    '''
    client = get_client()
    lb,ub = get_corners_from_bounds(box)
    name = nspace_name(namespace, name)
    result = client.Exec(name, version, lb, ub, dill.loads(fn))
    return(dill.dumps(result))