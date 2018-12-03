from typing import Optional, List, Type, NamedTuple
import requests
from risesdk.protocol import (
    Timestamp,
    Amount,
    Address,
    PublicKey,
    BaseTx,
)
from risesdk.api.base import BaseAPI, APIError

class TransactionInfo(object):
    tx_id: str
    row_id: int
    height: int
    block_id: str
    confirmations: int
    tx: BaseTx

    def __init__(self, raw):
        self.tx_id = str(raw['id'])
        self.row_id = int(raw['rowId'])
        self.height = int(raw['height'])
        self.block_id = str(raw['blockId'])
        self.confirmations = int(raw['confirmations'])
        self.tx = BaseTx.from_json(raw)

class PendingTransactionInfo(object):
    tx_id: str
    tx: BaseTx

    def __init__(self, raw):
        self.tx_id = str(raw['id'])
        self.tx = BaseTx.from_json(raw)

class TransactionsResult(object):
    transactions: List[TransactionInfo]
    count: int

    def __init__(self, raw):
        self.transactions = [TransactionInfo(t) for t in raw['transactions']]
        self.count = int(raw['count'])

class PendingTransactionsResult(object):
    transactions: List[PendingTransactionInfo]
    count: int

    def __init__(self, raw):
        self.transactions = [PendingTransactionInfo(t) for t in raw['transactions']]
        self.count = int(raw['count'])

class TransactionsCountResult(object):
    confirmed: int
    queued: int
    unconfirmed: int

    def __init__(self, raw):
        self.confirmed = int(raw['confirmed'])
        self.queued = int(raw['queued'])
        self.unconfirmed = int(raw['unconfirmed'])

class RejectedTransaction(NamedTuple):
    tx: BaseTx
    reason: str

class TransactionAddResult(NamedTuple):
    accepted: List[BaseTx]
    rejected: List[RejectedTransaction]

class TransactionsAPI(BaseAPI):
    def get_transactions(
        self,
        block_id: Optional[str] = None,
        and__block_id: Optional[str] = None,
        type_cls: Optional[Type[BaseTx]] = None,
        and__type_cls: Optional[Type[BaseTx]] = None,
        sender: Optional[Address] = None,
        and__sender: Optional[Address] = None,
        sender_public_key: Optional[PublicKey] = None,
        and__sender_public_key: Optional[PublicKey] = None,
        recipient: Optional[Address] = None,
        and__recipient: Optional[Address] = None,
        sender_public_keys: Optional[List[PublicKey]] = None,
        senders: Optional[List[Address]] = None,
        recipients: Optional[List[Address]] = None,
        from_height: Optional[int] = None,
        and__from_height: Optional[int] = None,
        to_height: Optional[int] = None,
        and__to_height: Optional[int] = None,
        from_timestamp: Optional[Timestamp] = None,
        and__from_timestamp: Optional[Timestamp] = None,
        to_timestamp: Optional[Timestamp] = None,
        and__to_timestamp: Optional[Timestamp] = None,
        min_amount: Optional[Amount] = None,
        and__min_amount: Optional[Amount] = None,
        max_amount: Optional[Amount] = None,
        and__max_amount: Optional[Amount] = None,
        min_confirmations: Optional[int] = None,
        and__min_confirmations: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
    ) -> TransactionsResult:
        r = self._get('/transactions', params={
            'blockId': block_id,
            'and:blockId': and__block_id,
            'type': None if type_cls is None else type_cls._type_id(),
            'and:type': None if and__type_cls is None else and__type_cls._type_id(),
            'senderId': None if sender is None else str(sender),
            'and:senderId': None if and__sender is None else str(and__sender),
            'senderPublicKey': None if sender_public_key is None
                else sender_public_key.hex(),
            'and:senderPublicKey': None if and__sender_public_key is None
                else and__sender_public_key.hex(),
            'recipientId': None if recipient is None else str(recipient),
            'and:recipientId': None if and__recipient is None else str(and__recipient),
            'senderPublicKeys': None if sender_public_keys is None
                else ','.join([k.hex() for k in sender_public_keys]),
            'senderIds': None if senders is None
                else ','.join([str(a) for a in senders]),
            'recipientIds': None if recipients is None
                else ','.join([str(a) for a in recipients]),
            'fromHeight': from_height,
            'and:fromHeight': and__from_height,
            'toHeight': to_height,
            'and:toHeight': and__to_height,
            'fromTimestamp': None if from_timestamp is None else int(from_timestamp),
            'and:fromTimestamp': None if and__from_timestamp is None else int(and__from_timestamp),
            'toTimestamp': None if to_timestamp is None else int(to_timestamp),
            'and:toTimestamp': None if and__to_timestamp is None else int(and__to_timestamp),
            'minAmount': None if min_amount is None else int(min_amount),
            'and:minAmount': None if and__min_amount is None else int(and__min_amount),
            'maxAmount': None if max_amount is None else int(max_amount),
            'and:maxAmount': None if and__max_amount is None else int(and__max_amount),
            'minConfirmations': min_confirmations,
            'and:minConfirmations': and__min_confirmations,
            'limit': limit,
            'offset': offset,
            'orderBy': order_by,
        })
        return TransactionsResult(r)

    def add_transactions(self, *txs: BaseTx) -> TransactionAddResult:
        tx_by_id = {}
        tx_jsons = []
        for tx in txs:
            tx_json = tx.to_json()
            tx_by_id[str(tx_json['id'])] = tx
            tx_jsons.append(tx_json)


        r = self._put('/transactions', data={
            'transactions': tx_jsons,
        })

        return TransactionAddResult(
            accepted=[
                tx_by_id[str(tx_id)]
                for tx_id in r['accepted']
            ],
            rejected=[
                RejectedTransaction(
                    tx=tx_by_id[str(i['id'])],
                    reason=str(i['reason']),
                )
                for i in r['invalid']
            ],
        )

    def get_transaction_count(self) -> TransactionsCountResult:
        r = self._get('/transactions/count')
        return TransactionsCountResult(r)

    def get_transaction(self, tx_id: str) -> Optional[TransactionInfo]:
        try:
            r = self._get('/transactions/get', params={
                'id': tx_id,
            })
        except APIError as err:
            if err.args[0] == 'Transaction not found':
                return None
            else:
                raise
        return TransactionInfo(r['transaction'])

    def get_queued_transactions(
        self,
        sender_public_key: Optional[PublicKey] = None,
        address: Optional[Address] = None,
    ) -> PendingTransactionsResult:
        r = self._get('/transactions/queued', params={
            'senderPublicKey': None if sender_public_key is None else sender_public_key.hex(),
            'address': None if address is None else str(address),
        })
        return PendingTransactionsResult(r)

    def get_queued_transaction(self, tx_id: str) -> Optional[PendingTransactionInfo]:
        try:
            r = self._get('/transactions/queued/get', params={
                'id': tx_id,
            })
        except APIError as err:
            if err.args[0].startswith('Transaction not found'):
                return None
            else:
                raise
        return PendingTransactionInfo(r['transaction'])

    def get_unconfirmed_transactions(
        self,
        sender_public_key: Optional[PublicKey] = None,
        address: Optional[Address] = None,
    ) -> PendingTransactionsResult:
        r = self._get('/transactions/unconfirmed', params={
            'senderPublicKey': None if sender_public_key is None else sender_public_key.hex(),
            'address': None if address is None else str(address),
        })
        return PendingTransactionsResult(r)

    def get_unconfirmed_transaction(self, tx_id: str) -> Optional[PendingTransactionInfo]:
        try:
            r = self._get('/transactions/unconfirmed/get', params={
                'id': tx_id,
            })
        except APIError as err:
            if err.args[0].startswith('Transaction not found'):
                return None
            else:
                raise
        return PendingTransactionInfo(r['transaction'])
