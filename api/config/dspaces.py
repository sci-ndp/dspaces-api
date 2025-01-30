from pydantic_settings import BaseSettings
import socket

import requests
import os

class DSpacesSettings(BaseSettings):
    # dspaces_server_ip:str = socket.getaddrinfo('dspaces', None)[0][-1][0]
    # dspaces_server_ip:str = "dspaces-server-service.dspaces.svc.cluster.local"
    dspaces_server_port:int = 4000
    dspaces_unsafe_endpoints:bool = False

    @property
    def dspaces_server_ip(self) -> str:
        """
        Retrieves the ClusterIP of the dspaces-server-service from the Kubernetes API.
        """
        try:
            # Fetch namespace (default is 'default' if not running in a specific namespace)
            namespace = os.getenv("POD_NAMESPACE", "dspaces")

            # Query the Kubernetes API for service details
            response = requests.get(
                f"https://kubernetes.default.svc/api/v1/namespaces/{namespace}/services/dspaces-server-service",
                headers={"Authorization": f"Bearer {self._get_k8s_token()}"},
                verify="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
            )

            response.raise_for_status()
            service_data = response.json()
            
            # Extract ClusterIP
            cluster_ip = service_data["spec"]["clusterIP"]
            print(f"Retrieved DataSpaces ClusterIP: {cluster_ip}")
            return cluster_ip

        except Exception as e:
            print(f"Failed to retrieve DataSpaces ClusterIP: {e}")
            return "dspaces-server-service.dspaces.svc.cluster.local"  # Fallback to service DNS

    @staticmethod
    def _get_k8s_token():
        """
        Reads the Kubernetes service account token from the pod's filesystem.
        """
        try:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Failed to read Kubernetes token: {e}")
            return ""

    @property
    def dspaces_connector(self) -> str:
        # return f'tcp://{self.dspaces_server_ip}:{self.dspaces_server_port}'
        cluster_ip = self.dspaces_server_ip
        print (f'In dspacesSettings - tcp://{self.dspaces_server_ip}:{self.dspaces_server_port}')
        return f'tcp://{cluster_ip}:{self.dspaces_server_port}'
        
    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }

settings = DSpacesSettings()
