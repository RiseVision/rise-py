from api.base import BaseAPI


class SignaturesAPI(BaseAPI):
    def add(self, secret, second_secret, public_key=None):
        return self._get('/signatures', secret=secret, secondSecret=second_secret, publicKey=public_key)

