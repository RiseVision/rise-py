from api.base import BaseAPI


class TransportAPI(BaseAPI):

    def __init__(self, node_address, transport_headers=None):
        super().__init__(node_address)
        self.headers = transport_headers

    def get_height(self):
        return self._get('/peer/height', api_prefix=False, headers=self.headers)

    def list_peers(self):
        return self._get('/peer/list', api_prefix=False, headers=self.headers)

    def ping(self):
        return self._get('/peer/ping', api_prefix=False, headers=self.headers)

    def post_transaction(self, transaction):
        return self._post('/peer/transactions', api_prefix=False, headers=self.headers, transaction=transaction)

    def post_transactions(self, transactions):
        return self._post('/peer/transactions', api_prefix=False, headers=self.headers, transactions=transactions)
