from typing import Optional, List
from risesdk.protocol import (
    Address,
    Amount,
    PublicKey,
)
from risesdk.api.base import BaseAPI, APIError
from risesdk.api.delegates import DelegateInfo

class AccountInfo(object):
    address: Address
    balance: Amount
    unconfirmed_balance: Amount
    public_key: Optional[PublicKey]
    second_public_key: Optional[PublicKey]
    second_signature: bool
    unconfirmed_second_signature: bool

    def __init__(self, raw):
        self.address = Address(raw['address'])
        self.balance = Amount(raw['balance'])
        self.unconfirmed_balance = Amount(raw['unconfirmedBalance'])
        self.public_key = None if raw['publicKey'] is None \
            else PublicKey.fromhex(raw['publicKey'])
        if raw['secondPublicKey']:
            self.second_public_key = PublicKey.fromhex(raw['secondPublicKey'])
        else:
            self.second_public_key = None
        self.second_signature = bool(raw['secondSignature'])
        self.unconfirmed_second_signature = bool(raw['unconfirmedSignature'])

class AccountsAPI(BaseAPI):
    def get_account(
        self,
        address: Optional[Address],
        public_key: Optional[PublicKey] = None,
    ) -> Optional[AccountInfo]:
        try:
            r = self._get('/accounts', params={
                'address': None if address is None else str(address),
                'publicKey': None if public_key is None else public_key.hex(),
            })
        except APIError as err:
            if err.args[0] == 'Account not found':
                return None
            else:
                raise
        return AccountInfo(r['account'])

    def get_account_delegates(self, address: Address) -> List[DelegateInfo]:
        r = self._get('/accounts/delegates', params={
            'address': str(address),
        })
        return [DelegateInfo(d) for d in r['delegates']]
