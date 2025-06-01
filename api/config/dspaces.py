import socket

from pydantic_settings import BaseSettings


class DSpacesSettings(BaseSettings):
    dspaces_server_ip: str = socket.getaddrinfo('dspaces', None)[0][-1][0]
    dspaces_server_port: int = 4000
    dspaces_unsafe_endpoints: bool = False
    dspaces_default_namespace: str = "datasets"

    @property
    def dspaces_connector(self) -> str:
        return f'tcp://{self.dspaces_server_ip}:{self.dspaces_server_port}'

    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }

settings = DSpacesSettings()
