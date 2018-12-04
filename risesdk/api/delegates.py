from typing import Optional, List
import requests
from risesdk.protocol import (
    Timestamp,
    Amount,
    Address,
    PublicKey,
)
from risesdk.api.base import BaseAPI, APIError
from risesdk.api.blocks import BlockInfo

class DelegateInfo(object):
    address: Address
    public_key: PublicKey
    username: str
    approval: float
    productivity: float
    consecutive_missed_blocks: Optional[int]
    missed_blocks: int
    produced_blocks: int
    rank: int
    rate: Optional[int]
    vote: Amount
    votes_weight: Optional[int]
    voters_count: Optional[int]
    registration_time: Optional[Timestamp]

    def __init__(self, raw):
        self.address = Address(raw['address'])
        self.public_key = PublicKey.fromhex(raw['publicKey'])
        self.username = str(raw['username'])
        self.approval = float(raw['approval'])
        self.productivity = float(raw['productivity'])
        if 'cmb' in raw:
            self.consecutive_missed_blocks = int(raw['cmb'])
        else:
            self.consecutive_missed_blocks = None
        self.missed_blocks = int(raw['missedblocks'])
        self.produced_blocks = int(raw['producedblocks'])
        self.rank = int(raw['rank'])
        if 'rate' in raw:
            self.rate = int(raw['rate'])
        else:
            self.rate = None
        self.vote = Amount(raw['vote'])
        if 'votesWeight' in raw:
            self.votes_weight = int(raw['votesWeight'])
        else:
            self.votes_weight = None
        if 'voters_cnt' in raw:
            self.voters_count = int(raw['voters_cnt'])
        else:
            self.voters_count = None
        if 'register_timestamp' in raw:
            self.registration_time = Timestamp(raw['register_timestamp'])
        else:
            self.register_timestamp = None

class DelegatesResult(object):
    delegates: List[DelegateInfo]
    count: int

    def __init__(self, raw):
        self.delegates = [DelegateInfo(d) for d in raw['delegates']]
        self.count = int(raw['totalCount'])

class DelegateForgingResult(object):
    fees: Amount
    rewards: Amount
    forged: Amount

    def __init__(self, raw):
        self.fees = Amount(raw['fees'])
        self.rewards = Amount(raw['rewards'])
        self.forged = Amount(raw['forged'])

class VoterInfo(object):
    address: Address
    public_key: PublicKey
    username: Optional[str]
    balance: Amount

    def __init__(self, raw):
        self.address = Address(raw['address'])
        self.public_key = PublicKey.fromhex(raw['publicKey'])
        self.username = raw['username']
        self.balance = Amount(raw['balance'])

class NextForgersResult(object):
    current_block: BlockInfo
    current_block_slot: int
    current_block_relays: Optional[int]
    current_slot: int
    delegates: List[PublicKey]

    def __init__(self, raw):
        self.current_block = BlockInfo(raw['currentBlock'])
        self.current_block_slot = int(raw['currentBlockSlot'])
        if 'relays' in raw['currentBlock']:
            self.current_block_relays = int(raw['currentBlock']['relays'])
        else:
            self.current_block_relays = None
        self.delegates = [PublicKey.fromhex(d) for d in raw['delegates']]

class ForgingStatusResult(object):
    enabled: bool
    delegates: List[PublicKey]

    def __init__(self, raw):
        self.enabled = bool(raw['enabled'])
        self.delegates = [PublicKey.fromhex(d) for d in raw['delegates']]

class DelegatesAPI(BaseAPI):
    def get_delegates(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
    ) -> DelegatesResult:
        r = self._get('/delegates', params={
            'limit': limit,
            'offset': offset,
            'orderBy': order_by,
        })
        return DelegatesResult(r)

    def get_forged_by_account(
        self,
        generator_public_key: PublicKey,
        start_time: Optional[Timestamp] = None,
        end_time: Optional[Timestamp] = None,
    ) -> DelegateForgingResult:
        r = self._get('/delegates/forging/getForgedByAccount', params={
            'generatorPublicKey': None if generator_public_key is None else generator_public_key.hex(),
            'start': None if start_time is None else int(start_time),
            'end': None if end_time is None else int(end_time),
        })
        return DelegateForgingResult(r)

    def get_delegate(
        self,
        public_key: Optional[PublicKey],
        username: Optional[str] = None,
    ) -> Optional[DelegateInfo]:
        try:
            r = self._get('/delegates/get', params={
                'publicKey': None if public_key is None else public_key.hex(),
                'username': username,
            })
        except APIError as err:
            if err.args[0] == 'Delegate not found':
                return None
            else:
                raise
        return DelegateInfo(r['delegate'])

    def get_voters(self, public_key: PublicKey) -> List[VoterInfo]:
        r = self._get('/delegates/voters', params={
            'publicKey': public_key.hex(),
        })
        return [VoterInfo(a) for a in r['accounts']]

    def search_delegates(
        self,
        query: str,
        limit: Optional[int] = None,
    ):
        r = self._get('/delegates/search', params={
            'q': query,
            'limit': limit,
        })
        return [DelegateInfo(d) for d in r['delegates']]

    def get_delegate_count(self) -> int:
        r = self._get('/delegates/count')
        return int(r['count'])

    def get_next_forgers(
        self,
        limit: Optional[int] = None,
    ) -> NextForgersResult:
        r = self._get('/delegates/getNextForgers', params={
            'limit': limit,
        })
        return NextForgersResult(r)

    def get_forging_status(
        self,
        public_key: Optional[PublicKey] = None,
    ) -> ForgingStatusResult:
        r = self._get('/delegates/forging/status', params={
            'publicKey': None if public_key is None else public_key.hex(),
        })
        return ForgingStatusResult(r)

    def enable_forging(
        self,
        secret_passphrase: str,
        public_key: Optional[PublicKey] = None,
    ):
        self._post('/delegates/forging/enable', data={
            'secret': secret_passphrase,
            'publicKey': None if public_key is None else public_key.hex(),
        })

    def disable_forging(
        self,
        secret_passphrase: str,
        public_key: Optional[PublicKey] = None,
    ):
        self._post('/delegates/forging/disable', data={
            'secret': secret_passphrase,
            'publicKey': None if public_key is None else public_key.hex(),
        })
