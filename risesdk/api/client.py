from typing import Optional
import requests
from risesdk.api.accounts import AccountsAPI
from risesdk.api.blocks import BlocksAPI
from risesdk.api.delegates import DelegatesAPI
from risesdk.api.transactions import TransactionsAPI

class Client(object):
    accounts: AccountsAPI
    blocks: BlocksAPI
    delegates: DelegatesAPI
    transactions: TransactionsAPI

    def __init__(
        self,
        base_url: str ='http://127.0.0.1:5566',
        session: Optional[requests.Session] = None,
    ):
        self.accounts = AccountsAPI(base_url, session)
        self.blocks = BlocksAPI(base_url, session)
        self.delegates = DelegatesAPI(base_url, session)
        self.transactions = TransactionsAPI(base_url, session)