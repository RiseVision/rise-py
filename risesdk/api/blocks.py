from typing import Optional, List
import requests
from risesdk.protocol import (
    Timestamp,
    Amount,
    PublicKey,
    Signature,
    BaseTx,
)
from risesdk.api.base import BaseAPI, APIError
from risesdk.api.transactions import TransactionInfo

class BlockInfo(object):
    block_id: str
    row_id: Optional[int]
    version: int
    timestamp: Timestamp
    height: int
    previous_block_id: Optional[str]
    number_of_transactions: int
    total_amount: Amount
    total_fee: Amount
    reward: Amount
    payload_length: int
    payload_hash: bytes
    generator_public_key: PublicKey
    block_signature: Signature
    transactions: List[BaseTx]

    def __init__(self, raw):
        self.block_id = str(raw['id'])
        if 'rowId'in raw:
            self.row_id = int(raw['rowId'])
        else:
            self.row_id = None
        self.version = int(raw['version'])
        self.timestamp = Timestamp(raw['timestamp'])
        self.height = int(raw['height'])
        if raw['previousBlock']:
            self.previous_block_id = str(raw['previousBlock'])
        else:
            self.previous_block_id = None
        self.number_of_transactions = int(raw['numberOfTransactions'])
        self.total_amount = Amount(raw['totalAmount'])
        self.total_fee = Amount(raw['totalFee'])
        self.reward = Amount(raw['reward'])
        self.payload_length = int(raw['payloadLength'])
        self.payload_hash = bytes.fromhex(raw['payloadHash'])
        self.generator_public_key = PublicKey.fromhex(raw['generatorPublicKey'])
        self.block_signature = Signature.fromhex(raw['blockSignature'])
        self.transactions = [TransactionInfo(t) for t in raw['transactions']]

class BlocksResult(object):
    blocks: List[BlockInfo]
    count: int

    def __init__(self, raw):
        self.blocks = [BlockInfo(b) for b in raw['blocks']]
        self.count = int(raw['count'])

class FeesInfo(object):
    send: Amount
    vote: Amount
    second_signature: Amount
    delegate: Amount

    def __init__(self, raw):
        self.send = Amount(raw['send'])
        self.vote = Amount(raw['vote'])
        self.second_signature = Amount(raw['secondsignature'])
        self.delegate = Amount(raw['delegate'])

class FeesResult(object):
    fees: FeesInfo
    from_height: int
    height: int
    to_height: Optional[int]

    def __init__(self, raw):
        self.fees = FeesInfo(raw['fees'])
        self.from_height = int(raw['fromHeight'])
        self.height = int(raw['height'])
        if raw['toHeight']:
            self.to_height = int(raw['toHeight'])
        else:
            self.to_height = None

class StatusResult(object):
    broad_hash: bytes
    epoch: str
    fee: Amount
    height: int
    milestone: int
    net_hash: bytes
    reward: Amount
    supply: Amount

    def __init__(self, raw):
        self.broad_hash = bytes.fromhex(raw['broadhash'])
        self.epoch = str(raw['epoch'])
        self.fee = Amount(raw['fee'])
        self.height = int(raw['height'])
        self.milestone = int(raw['milestone'])
        self.net_hash = bytes.fromhex(raw['nethash'])
        self.reward = Amount(raw['reward'])
        self.supply = Amount(raw['supply'])

class BlocksAPI(BaseAPI):
    def get_blocks(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        generator_public_key: Optional[PublicKey] = None,
        previous_block_id: Optional[str] = None,
        height: Optional[int] = None,
    ) -> BlocksResult:
        r = self._get('/blocks', params={
            'limit': limit,
            'offset': offset,
            'orderBy': order_by,
            'generatorPublicKey': None if generator_public_key is None else generator_public_key.hex(),
            'previousBlock': previous_block_id,
            'height': height,
        })
        return BlocksResult(r)

    def get_block(self, block_id: str) -> Optional[BlockInfo]:
        try:
            r = self._get('/blocks/get', params={
                'id': block_id,
            })
        except APIError as err:
            if err.args[0] == 'Block not found':
                return None
            else:
                raise
        return BlockInfo(r['block'])

    def get_fees(self, height: Optional[int] = None) -> FeesResult:
        r = self._get('/blocks/getFees', params={
            'height': height,
        })
        return FeesResult(r)

    def get_status(self) -> StatusResult:
        r = self._get('/blocks/getStatus')
        return StatusResult(r)
