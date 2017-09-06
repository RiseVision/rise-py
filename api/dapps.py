from api.base import BaseAPI


class DappsAPI(BaseAPI):

    def get_categories(self):
        return self._get('/dapps/categories')
