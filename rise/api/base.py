"""
Module provides base class for API wrappers.
"""
import requests


class BaseAPI:
    """
    Base object for accessing Rise API.
    """
    def __init__(self, node_address):
        """
        Construct Rise API wrapper.
        :param node_address: URL of Rise node. E. g.: 'http://127.0.0.1:5566'
        """
        self._address = node_address
        """URL of Rise node"""

    def _get(self, route, api_prefix=True, headers=None, **args):
        """
        Perform GET request to API.
        :param route: Route to API method. E. g.: /accounts/open
        :param api_prefix: if True append '/api' to Rise node URL for API call.
        :param headers: Headers to append to the request.
        :param args: Arguments to pass in the request.
        :return: Dictionary with request result.
        """
        url = self._build_url(route, api_prefix)
        return requests.get(url, args, headers=headers).json()

    def _post(self, route, api_prefix=True, headers=None, **args):
        """
        Perform POST request to API.
        :param route: Route to API method. E. g.: /accounts/open
        :param api_prefix: if True append '/api' to Rise node URL for API call.
        :param headers: Headers to append to the request.
        :param args: Arguments to pass in the request.
        :return: Dictionary with request result.
        """
        url = self._build_url(route, api_prefix)
        return requests.post(url, args, headers=headers).json()

    def _put(self, route,  api_prefix=True, headers=None, **args):
        """
        Perform PUT request to API.
        :param route: Route to API method. E. g.: /accounts/open
        :param api_prefix: if True append '/api' to Rise node URL for API call.
        :param headers: Headers to append to the request.
        :param args: Arguments to pass in the request.
        :return: Dictionary with request result.
        """
        url = self._build_url(route, api_prefix)
        return requests.put(url, args, headers=headers).json()

    def _build_url(self, route, api_prefix):
        """Builds URL to make API call."""
        return '{}{}{}'.format(self._address, '/api' if api_prefix else '', route)
