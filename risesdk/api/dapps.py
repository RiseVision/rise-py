"""
Module provides to access Rise Decentralized Apps API methods. (in progress)
"""
from .base import BaseAPI


class DappsAPI(BaseAPI):
    """
    DappsAPI object provides access to Rise  Decentralized Apps API methods.
    """
    def get_categories(self):
        return self._get('/dapps/categories')
