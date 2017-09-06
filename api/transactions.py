from api.base import BaseAPI


class TransactionsAPI(BaseAPI):
    def get(self, id):
        return self._get('/transactions/get', id=id)

    def count(self):
        return self._get('/transactions/count')

    def get_list(self, **query):
        return self._get('/transactions', **query)

    def send(self, secret, amount, recipient_id, public_key=None, second_secret=None):
        return self._put('/transactions', secret=secret, amount=amount,
                         recipientId=recipient_id, publicKey=public_key, secondSecret=second_secret)

    def get_unconfirmed_transactions(self):
        return self._get('/transactions/unconfirmed')

    def get_unconfirmed_transaction(self, id):
        return self._get('/transactions/unconfirmed/get', id=id)
