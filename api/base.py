import requests


class BaseAPI:
    def __init__(self, node_address):
        self._address = node_address

    def _get(self, route, api_prefix=True, headers=None, **args):
        url = self._build_url(route, api_prefix)
        return requests.get(url, args, headers=headers).json()

    def _post(self, route, api_prefix=True, headers=None, **args):
        url = self._build_url(route, api_prefix)
        return requests.post(url, args, headers=headers).json()

    def _put(self, route,  api_prefix=True, headers=None, **args):
        url = self._build_url(route, api_prefix)
        return requests.put(url, args, headers=headers).json()

    def _build_url(self, route, api_prefix):
        return '{}{}{}'.format(self._address, '/api' if api_prefix else '', route)