from api.base import BaseAPI


class MultiSignaturesAPI(BaseAPI):
    def get_ending(self, public_key):
        return self._get('/multisignatures/pending', publicKey=public_key)

    def create_multisig_account(self, secret, lifetime, min, public_keys):
        return self._put('/multisignatures', secret=secret, lifetime=lifetime, min=min, keysgroup=public_keys)

    def sign(self, secret, public_key, transaction_id):
        return self._post('/multisignatures/sign', secret=secret, publicKey=public_key, transactionId=transaction_id)

    def get_accounts(self, public_key):
        return self._get('/multisignatures/accounts', publicKey=public_key)
