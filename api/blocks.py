from api.base import BaseAPI


class BlocksAPI(BaseAPI):

    def get_fee_schedule(self):
        return self._get('/blocks/getFees')

    def get_fee(self):
        return self._get('/blocks/getFee')

    def get_reward(self):
        return self._get('/blocks/getReward')

    def get_supply(self):
        return self._get('/blocks/getSupply')

    def get_status(self):
        return self._get('/blocks/getStatus')

    def get_height(self):
        return self._get('/blocks/getHeight')

    def get_nethash(self):
        return self._get('/blocks/getNethash')

    def get_milestone(self):
        return self._get('/blocks/getMilestone')

    def get_block(self, id):
        return self._get('/blocks/get', id=id)

    def get_blocks(self, **query):
        return self._get('/blocks', **query)
