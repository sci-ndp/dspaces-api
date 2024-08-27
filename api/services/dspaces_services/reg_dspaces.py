from api.helpers.dspaces_client import get_client
from api.models.dspaces_model import DSRegHandle

def reg_dspaces(type: str, 
                name: str, 
                data: dict) -> DSRegHandle:
    client = get_client()
    return(client.Register(type, name, data))
    
    