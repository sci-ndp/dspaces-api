from dspaces import DSClient
from api.config import dspaces_settings

def get_client():
    if get_client.client is None:
        get_client.client = DSClient(conn = dspaces_settings.dspaces_connector)
    return get_client.client
get_client.client = None

def nspace_name(namespace, name):
    name = namespace + '\\' + name if namespace else name
    return name