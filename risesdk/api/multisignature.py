import requests
from risesdk.protocol import (
    PublicKey,
)
from risesdk.api.base import BaseAPI

class MultisignatureAPI(BaseAPI):
    def get_accounts(self, public_key: PublicKey):
        raise NotImplementedError()

    def get_pending_transactions(self, public_key: PublicKey):
        raise NotImplementedError()
