from api.helpers.dspaces_client import get_client

def get_dspaces_vars()->list[str]:
    '''
    Get all the variables names stored in the DataSpaces server

    Returns
    -------
    A list of names
    '''
    client = get_client()
    return client.GetVars()
