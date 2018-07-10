"""
Module provides to access Rise Loader API methods.
"""
from .base import BaseAPI


class LoaderAPI(BaseAPI):
    """
    LoaderAPI object provides access to Rise Loader API methods.
    """
    def status(self):
        return self._get('/loader/status')

    def sync_status(self):
        return self._get('/loader/status/sync')