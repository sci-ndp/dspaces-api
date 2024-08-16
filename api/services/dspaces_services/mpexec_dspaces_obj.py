from api.helpers.dspaces_client import nspace_name, get_client
from dspaces import DSObject as Request
from api.models.dspaces_model import BoundingBox, DSObject
from api.helpers.bounding_box import get_corners_from_bounds

import dill
import numpy as np

def mpexec_dspaces_obj(
            reqs: list[DSObject],
            fn: bytes
        ) -> np.ndarray | None:
    client = get_client()
    args = []
    for req in reqs:
        lb, ub = get_corners_from_bounds(BoundingBox(bounds=req.bounds))
        args.append(Request(
                name = nspace_name(req.namespace, req.name),
                version = req.version,
                lb = lb,
                ub = ub
            )
        )
    result = client.VecExec(args, dill.loads(fn))
    return(dill.dumps(result))

 