from typing import Any, Optional
import requests

class APIError(Exception):
    pass

class BaseAPI(object):
    def __init__(
        self,
        base_url: str,
        session: Optional[requests.Session],
    ):
        self._base_url = base_url.rstrip('/')
        self._session = session

    def _get(self, path: str, params: Any = None) -> Any:
        url = self.__build_url(path)
        if self._session:
            r = self._session.get(url, params=params)
        else:
            r = requests.get(url, params=params)
        return self.__process_response(r)

    def _put(self, path: str, data: Any) -> Any:
        url = self.__build_url(path)
        if self._session:
            r = self._session.put(url, json=data)
        else:
            r = requests.put(url, json=data)
        return self.__process_response(r)

    def _post(self, path: str, data: Any) -> Any:
        url = self.__build_url(path)
        if self._session:
            r = self._session.post(url, json=data)
        else:
            r = requests.post(url, json=data)
        return self.__process_response(r)
    
    def __build_url(self, path):
        return '{}{}'.format(self._base_url, path)

    def __process_response(self, resp: requests.Response) -> Any:
        raw = resp.json()
        # Raise an exception for node errors
        if raw['success'] is False:
            raise APIError(raw['error'])
        del raw['success']
        return raw
