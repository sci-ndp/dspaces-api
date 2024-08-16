from api.helpers.dspaces_client import get_client, nspace_name
from api.models.dspaces_model import DSObject
from api.helpers.bounding_box import get_bounds_from_corners

def get_dspaces_var_obj(
        namespace: str,
        name: str
) -> list[DSObject]:
    """
    Get all objects for a given variable

    Parameters
    ----------
    namespace
        The namespace of the request
    name
        The variable name
    """
    client = get_client()
    name = nspace_name(namespace, name)
    obj_list = client.GetObjVars(name)
    objs = []
    for obj in obj_list:
        objs.append(
            DSObject(
                name = obj.name,
                version = obj.version,
                bounds = get_bounds_from_corners(obj.lb, obj.ub)
            )
        )
    return(objs)