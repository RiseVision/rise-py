from api.base import BaseAPI


class LoaderAPI(BaseAPI):

    def status(self):
        return self._get('/loader/status')

    def sync_status(self):
        return self._get('/loader/status/sync')