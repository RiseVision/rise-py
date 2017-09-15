"""
Module provides to access Rise Transport API methods.
"""
from .base import BaseAPI


class TransportAPI(BaseAPI):
    """
    TransactionsAPI object provides access to Rise Transport API methods.
    """
    def __init__(self, node_address, transport_headers=None):
        """
        Construct Rise API wrapper.

        :param node_address: URL of Rise node. E. g.: 'http://127.0.0.1:5566'
        :param transport_headers: header for API requset. Must contain nethash, port and version.
        """
        super().__init__(node_address)
        self.headers = transport_headers

    def get_height(self):
        """
        Get peer using transport api.
        :return: Dictionary with result of request.
        """
        return self._get('/peer/height', api_prefix=False, headers=self.headers)

    def list_peers(self):
        """
        List peers.
        :return: Dictionary with result of request.
        """
        return self._get('/peer/list', api_prefix=False, headers=self.headers)

    def ping(self):
        """
        Ping peer!
        :return: Dictionary with result of request.
        """
        return self._get('/peer/ping', api_prefix=False, headers=self.headers)

    def post_transaction(self, transaction):
        """
        Post signed tx to this peer.
        :param transaction: dictionary with transaction description.
        :return: Dictionary with result of request.
        """
        return self._post('/peer/transactions', api_prefix=False, headers=self.headers, transaction=transaction)

    def post_transactions(self, transactions):
        """
        Post several signed txs to this peer.
        :param transactions: list with dictionaries with transaction description.
        :return: Dictionary with result of request.
        """
        return self._post('/peer/transactions', api_prefix=False, headers=self.headers, transactions=transactions)
