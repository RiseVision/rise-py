"""
Module provides to access Rise Signatures API methods.
"""
from .base import BaseAPI


class SignaturesAPI(BaseAPI):
    """
    SignaturesAPI object provides access to Rise Signatures API methods.
    """
    def add(self, secret, second_secret, public_key=None):
        return self._get('/signatures', secret=secret, secondSecret=second_secret, publicKey=public_key)

