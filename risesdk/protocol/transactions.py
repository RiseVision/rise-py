import hashlib
from typing import Dict, Type, Optional, List
from abc import ABC, abstractmethod
from risesdk.protocol.primitives import Timestamp, Amount, Address, PublicKey, Signature

_tx_type_registry: Dict[int, Type['BaseTx']] = {}

def transaction_type(type_id: int):
    '''
    Decorator to associate transaction type_id with a BaseTx subclass.
    '''
    def decorator(cls):
        if not issubclass(cls, BaseTx):
            raise ValueError('{} is not a subclass of BaseTx'.format(cls))
        if type in _tx_type_registry:
            raise ValueError('Type {} already handled by class {}'.format(type_id, _tx_type_registry[type_id]))
        _tx_type_registry[type_id] = cls
        return cls
    return decorator

class BaseTx(ABC):
    timestamp: Timestamp
    sender_public_key: PublicKey
    requester_public_key: Optional[PublicKey] = None
    fee: Amount
    signature: Optional[Signature] = None
    second_signature: Optional[Signature] = None
    signatures: List[Signature] = []

    def __init__(
        self,
        sender_public_key: PublicKey,
        fee: Amount,
        timestamp: Optional[Timestamp] = None,
        requester_public_key: Optional[PublicKey] = None,
        signature: Optional[Signature] = None,
        second_signature: Optional[Signature] = None,
        signatures: List[Signature] = [],
    ):
        if timestamp is None:
            self.timestamp = Timestamp.now()
        else:
            self.timestamp = timestamp
        self.sender_public_key = sender_public_key
        self.requester_public_key = requester_public_key
        self.fee = fee
        self.signature = signature
        self.second_signature = second_signature
        self.signatures = signatures

    @classmethod
    def _type_id(cls) -> int:
        for (type_id, type_cls) in _tx_type_registry.items():
            if type_cls == cls:
                return type_id
        raise TypeError('{} has not been decorated with @transaction_type'.format(cls))

    def derive_id(self) -> str:
        '''
        Compute the transaction ID (hash) based on the properties of this object.
        '''
        msg = self.to_bytes()
        digest = hashlib.sha256(msg).digest()
        i = int.from_bytes(digest[:8], byteorder='little')
        return str(i)

    @abstractmethod
    def _asset_bytes(self) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def _asset_json(self):
        raise NotImplementedError()

    @property
    def _recipient(self) -> Optional[Address]:
        return None

    @property
    def _amount(self) -> Amount:
        return Amount('0')

    def to_bytes(self, skip_signature: bool = False, skip_second_signature: bool = False) -> bytes:
        '''
        Serialize the transaction to binary format.

        This format is used to calculate the transaction
        ID, used as the input for the SecretKey.sign() function or can be passed to the Ledger app
        for signing.

        When skip_signature=True, the signature property value is ignored during serialization.
        When skip_second_signature=True, the second_signature property value is ignored.
        '''
        buf = bytearray()
        buf.append(self._type_id())
        buf += self.timestamp.to_bytes(4, byteorder='little')
        buf += self.sender_public_key
        if self.requester_public_key:
            buf += self.requester_public_key
        if self._recipient:
            buf += self._recipient.to_bytes()
        else:
            buf += bytes(8)
        buf += self._amount.to_bytes(8, byteorder='little')
        buf += self._asset_bytes()
        if not skip_signature and self.signature:
            buf += self.signature
        if not skip_second_signature and self.second_signature:
            buf += self.second_signature
        return bytes(buf)

    @classmethod
    @abstractmethod
    def parse_json(cls, data):
        try:
            if data.get('requesterPublicKey'):
                requester_public_key = PublicKey.fromhex(data.get('requesterPublicKey'))
            else:
                requester_public_key = None
            if data.get('signature'):
                signature = Signature.fromhex(data.get('signature'))
            else:
                signature = None
            if data.get('signSignature'):
                second_signature = Signature.fromhex(data.get('signSignature'))
            else:
                second_signature = None

            return {
                'timestamp': Timestamp(data['timestamp']),
                'sender_public_key': PublicKey.fromhex(data['senderPublicKey']),
                'requester_public_key': requester_public_key,
                'fee': Amount(data['fee']),
                'signature': signature,
                'second_signature': second_signature,
                'signatures': [
                    Signature.fromhex(sig)
                    for sig in (data.get('signatures') or [])
                ],
            }
        except KeyError as err:
            raise ValueError('Data dictionary is missing "{}" item'.format(err.args[0]))

    @staticmethod
    def from_json(data) -> 'BaseTx':
        '''
        Attempt to deserialize the transaction from a plain JSON-compatible Python dictionary.
        '''
        if 'type' not in data:
            raise ValueError('Data dictionary is missing "type" item')
        if data['type'] not in _tx_type_registry:
            raise ValueError('Data dictionary contains unknown transaction "type"')
        cls = _tx_type_registry[data['type']]

        return cls(**cls.parse_json(data))

    def to_json(self):
        '''
        Serialize the transaction to a plain JSON-compatible Python dictionary.
        '''
        return {
            'type': self._type_id(),
            'id': self.derive_id(),
            'timestamp': self.timestamp,
            'senderId': self.sender_public_key.derive_address(),
            'senderPublicKey': self.sender_public_key.hex(),
            'requesterPublicKey': self.requester_public_key.hex() if self.requester_public_key else None,
            'fee': self.fee,
            'signature': self.signature.hex() if self.signature else None,
            'signSignature': self.second_signature.hex() if self.second_signature else None,
            'signatures': [sig.hex() for sig in (self.signatures or [])],
            'amount': self._amount,
            'recipientId': self._recipient,
            'asset': self._asset_json(),
        }

@transaction_type(0)
class SendTx(BaseTx):
    amount: Amount
    recipient: Address

    def __init__(
        self,
        sender_public_key: PublicKey,
        recipient: Address,
        amount: Amount,
        fee: Amount,
        timestamp: Optional[Timestamp] = None,
        requester_public_key: Optional[PublicKey] = None,
        signature: Optional[Signature] = None,
        second_signature: Optional[Signature] = None,
        signatures: List[Signature] = [],
    ):
        super().__init__(
            sender_public_key = sender_public_key,
            fee = fee,
            timestamp = timestamp,
            requester_public_key = requester_public_key,
            signature = signature,
            second_signature = second_signature,
            signatures = signatures,
        )
        self.amount = amount
        self.recipient = recipient

    def _asset_bytes(self) -> bytes:
        return bytes()

    def _asset_json(self):
        return None

    @property
    def _amount(self) -> Amount:
        return self.amount
    
    @property
    def _recipient(self) -> Optional[Address]:
        return self.recipient

    @classmethod
    def parse_json(cls, data):
        base = super().parse_json(data)

        try:
            return {
                **base,
                'amount': Amount(data['amount']),
                'recipient': Address(data['recipientId']),
            }
        except KeyError as err:
            raise ValueError('Data dictionary is missing "{}" item'.format(err.args[0]))

@transaction_type(1)
class RegisterSecondSignatureTx(BaseTx):
    second_public_key: PublicKey

    def __init__(
        self,
        sender_public_key: PublicKey,
        second_public_key: PublicKey,
        fee: Amount,
        timestamp: Optional[Timestamp] = None,
        requester_public_key: Optional[PublicKey] = None,
        signature: Optional[Signature] = None,
        second_signature: Optional[Signature] = None,
        signatures: List[Signature] = [],
    ):
        super().__init__(
            sender_public_key = sender_public_key,
            fee = fee,
            timestamp = timestamp,
            requester_public_key = requester_public_key,
            signature = signature,
            second_signature = second_signature,
            signatures = signatures,
        )
        self.second_public_key = second_public_key

    def _asset_bytes(self) -> bytes:
        return bytes(self.second_public_key)

    def _asset_json(self):
        return {
            'signature': {
                'publicKey': self.second_public_key.hex(),
            },
        }

    @classmethod
    def parse_json(cls, data):
        base = super().parse_json(data)

        try:
            asset = data['asset']
        except KeyError as err:
            raise ValueError('Data dictionary is missing "{}" item'.format(err.args[0]))

        try:
            asset_sig = asset['signature']
        except KeyError as err:
            raise ValueError('Data dictionary is missing "asset.{}" item'.format(err.args[0]))

        try:
            second_public_key = PublicKey.fromhex(asset_sig['publicKey'])
        except KeyError as err:
            raise ValueError('Data dictionary is missing "asset.signature.{}" item'.format(err.args[0]))

        return {
            **base,
            'second_public_key': second_public_key,
        }

@transaction_type(2)
class RegisterDelegateTx(BaseTx):
    username: str

    def __init__(
        self,
        sender_public_key: PublicKey,
        username: str,
        fee: Amount,
        timestamp: Optional[Timestamp] = None,
        requester_public_key: Optional[PublicKey] = None,
        signature: Optional[Signature] = None,
        second_signature: Optional[Signature] = None,
        signatures: List[Signature] = [],
    ):
        super().__init__(
            sender_public_key = sender_public_key,
            fee = fee,
            timestamp = timestamp,
            requester_public_key = requester_public_key,
            signature = signature,
            second_signature = second_signature,
            signatures = signatures,
        )
        self.username = username

    def _asset_bytes(self) -> bytes:
        return bytes(self.username, 'utf8')

    def _asset_json(self):
        return {
            'delegate': {
                'username': self.username,
            }
        }

    @classmethod
    def parse_json(cls, data):
        base = super().parse_json(data)

        try:
            asset = data['asset']
        except KeyError as err:
            raise ValueError('Data dictionary is missing "{}" item'.format(err.args[0]))

        try:
            asset_delegate = asset['delegate']
        except KeyError as err:
            raise ValueError('Data dictionary is missing "asset.{}" item'.format(err.args[0]))

        try:
            username = asset_delegate['username']
        except KeyError as err:
            raise ValueError('Data dictionary is missing "asset.delegate.{}" item'.format(err.args[0]))

        return {
            **base,
            'username': username,
        }

@transaction_type(3)
class VoteTx(BaseTx):
    add_votes: List[PublicKey] = []
    remove_votes: List[PublicKey] = []

    def __init__(
        self,
        sender_public_key: PublicKey,
        add_votes: List[PublicKey],
        remove_votes: List[PublicKey],
        fee: Amount,
        timestamp: Optional[Timestamp] = None,
        requester_public_key: Optional[PublicKey] = None,
        signature: Optional[Signature] = None,
        second_signature: Optional[Signature] = None,
        signatures: List[Signature] = [],
    ):
        super().__init__(
            sender_public_key = sender_public_key,
            fee = fee,
            timestamp = timestamp,
            requester_public_key = requester_public_key,
            signature = signature,
            second_signature = second_signature,
            signatures = signatures,
        )
        self.add_votes = add_votes
        self.remove_votes = remove_votes

    @property
    def _recipient(self) -> Optional[Address]:
        return self.sender_public_key.derive_address()

    def _asset_bytes(self) -> bytes:
        buf = bytearray()
        for pk in self.remove_votes:
            buf += bytes('-{}'.format(pk.hex()), 'utf8')
        for pk in self.add_votes:
            buf += bytes('+{}'.format(pk.hex()), 'utf8')
        return bytes(buf)

    def _asset_json(self):
        return {
            'votes': [
                '-{}'.format(pk.hex()) for pk in self.remove_votes
            ] + [
                '+{}'.format(pk.hex()) for pk in self.add_votes
            ],
        }

    @classmethod
    def parse_json(cls, data):
        base = super().parse_json(data)

        try:
            asset = data['asset']
        except KeyError as err:
            raise ValueError('Data dictionary is missing "{}" item'.format(err.args[0]))

        try:
            asset_votes = asset['votes']
        except KeyError as err:
            raise ValueError('Data dictionary is missing "asset.{}" item'.format(err.args[0]))

        add_votes: List[PublicKey] = []
        remove_votes: List[PublicKey] = []
        for val in asset_votes:
            if val[0] == '-':
                remove_votes.append(PublicKey.fromhex(val[1:]))
            elif val[0] == '+':
                add_votes.append(PublicKey.fromhex(val[1:]))

        return {
            **base,
            'add_votes': add_votes,
            'remove_votes': remove_votes,
        }
