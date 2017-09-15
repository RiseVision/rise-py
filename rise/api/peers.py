"""
Module provides to access Rise Peers API methods.
"""
from .base import BaseAPI


class PeersAPI(BaseAPI):
    """
    PeersAPI object provides access to Rise Peers API methods.
    """
    def get_list(self, **query):
        return self._get('/peers', **query)

    def get_by_ip_port(self, ip, port):
        return self._get('/peers/get', ip=ip, port=port)

    def version(self):
        return self._get('/peers/version')
