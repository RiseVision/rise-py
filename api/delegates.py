from api.base import BaseAPI


class DelegatesAPI(BaseAPI):

    def enable(self, secret, username, second_secret=None):
        return self._put('/delegates', secret=secret, username=username, secondSecret=second_secret)

    def get_list(self, **query):
        return self._get('/delegates', **query)

    def get_by_username(self, username):
        return self._get_by_key_val(username=username)

    def get_by_public_key(self, public_key):
        return self._get_by_key_val(publicKey=public_key)

    def _get_by_key_val(self, **query):
        return self._get('/delegates/get', **query)

    def get_voters(self, public_key):
        return self._get('/delegates/voters', publicKey=public_key)

    def enable_forging(self, secret):
        return self._post('/delegates/forging/enable', secret=secret)

    def disable_forging(self, secret):
        return self._post('/delegates/forging/disable', secret=secret)

    def get_forged_by_account(self, public_key=None):
        return self._post('/delegates/forging/getForgedByAccount', generatorPublicKey=public_key)

    def get_forging_status(self, public_key=None):
        return self._get('/delegates/forging/status', publicKey=public_key)

    def get_next_forgers(self, limit):
        return self._get('/delegates/getNextForgers', limit=limit)
