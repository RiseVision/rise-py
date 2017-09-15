"""
This module provides single object to access Rise API.

===
Examples:
    >>> from rise import RiseAPI
    >>> api = RiseAPI('http://127.0.0.1:5566')
    >>> result = api.accounts.open('secret')
    >>> if result['success']:
    ...    print(result['account'])
    ... else:
    ...    print(result['error'])
"""
from .api.account import AccountsAPI
from .api.base import BaseAPI
from .api.blocks import BlocksAPI
from .api.dapps import DappsAPI
from .api.delegates import DelegatesAPI
from .api.loader import LoaderAPI
from .api.multi_signatures import MultiSignaturesAPI
from .api.peers import PeersAPI
from .api.signatures import SignaturesAPI
from .api.transactions import TransactionsAPI
from .api.transport import TransportAPI


class RiseAPI(BaseAPI):
    """
    Wrapper for accessing all Rise API methods.
    """
    def __init__(self, node_address):
        """
        Construct Rise API wrapper.
        :param node_address: URL of Rise node. e. g.: 'http://127.0.0.1:5566'
        """
        super().__init__(node_address)
        self.accounts = AccountsAPI(node_address)
        """Provides access to Rise Accounts API."""
        self.blocks = BlocksAPI(node_address)
        """Provides access to Blocks Accounts API."""
        self.dapps = DappsAPI(node_address)
        """Provides access to Rise Dapps API."""
        self.delegates = DelegatesAPI(node_address)
        """Provides access to Rise Delegates API."""
        self.loader = LoaderAPI(node_address)
        """Provides access to Rise Loader API."""
        self.transport = lambda headers: TransportAPI(node_address, headers)
        """Provides access to Rise Transport API."""
        self.multisig = MultiSignaturesAPI(node_address)
        """Provides access to Rise Multi-Signature API."""
        self.peers = PeersAPI(node_address)
        """Provides access to Rise Peers API."""
        self.signatures = SignaturesAPI(node_address)
        """Provides access to Rise Signatures API."""
        self.transactions = TransactionsAPI(node_address)
        """Provides access to Rise Transactions API."""
