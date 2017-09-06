from api.base import BaseAPI


class PeersAPI(BaseAPI):
    def get_list(self, **query):
        return self._get('/peers', **query)

    def get_by_ip_port(self, ip, port):
        return self._get('/peers/get', ip=ip, port=port)

    def version(self):
        return self._get('/peers/version')
