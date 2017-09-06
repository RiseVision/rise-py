from api.account import AccountsAPI
from api.base import BaseAPI
from api.blocks import BlocksAPI
from api.dapps import DappsAPI
from api.delegates import DelegatesAPI
from api.loader import LoaderAPI
from api.multi_signatures import MultiSignaturesAPI
from api.peers import PeersAPI
from api.signatures import SignaturesAPI
from api.transactions import TransactionsAPI
from api.transport import TransportAPI


class RiseAPI(BaseAPI):

    def __init__(self, node_address):
        super().__init__(node_address)
        self.accounts = AccountsAPI(node_address)
        self.blocks = BlocksAPI(node_address)
        self.dapps = DappsAPI(node_address)
        self.delegates = DelegatesAPI(node_address)
        self.loader = LoaderAPI(node_address)
        self.transport = lambda headers: TransportAPI(node_address, headers)
        self.multisig = MultiSignaturesAPI(node_address)
        self.peers = PeersAPI(node_address)
        self.signatures = SignaturesAPI(node_address)
        self.transactions = TransactionsAPI(node_address)
