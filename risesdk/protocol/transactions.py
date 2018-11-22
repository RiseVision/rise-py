from typing import Dict, Type, Optional, List
from abc import ABC, abstractmethod
from risesdk.protocol.primitives import Timestamp, Amount, Address, PublicKey, Signature

_tx_type_registry: Dict[int, Type['BaseTx']] = {}

def transaction_type(type_id: int):
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

    @property
    def __type_id(self) -> int:
        for (type_id, cls) in _tx_type_registry.items():
            if cls == type(self):
                return type_id
        raise TypeError('{} has not been decorated with @transaction_type'.format(type(self)))

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
        buf = bytearray()
        buf.append(self.__type_id)
        buf += self.timestamp.to_bytes(4, byteorder='big')
        buf += self.sender_public_key
        if self.requester_public_key:
            buf += self.requester_public_key
        recipient = self._recipient
        if recipient:
            buf += recipient.to_bytes()
        else:
            buf += bytes(8)
        buf += self._amount.to_bytes(8, byteorder='big')
        buf += self._asset_bytes()
        if not skip_signature and self.signature:
            buf += self.signature
        if not skip_second_signature and self.second_signature:
            buf += self.second_signature
        return bytes(buf)

    @staticmethod
    @abstractmethod
    def parse_json(data):
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
        if 'type' not in data:
            raise ValueError('Data dictionary is missing "type" item')
        if data['type'] not in _tx_type_registry:
            raise ValueError('Data dictionary contains unknown transaction "type"')
        cls = _tx_type_registry[data['type']]

        return cls(**cls.parse_json(data))

    def to_json(self):
        return {
            'type': self.__type_id,
            'timestamp': self.timestamp,
            'senderId': self.sender_public_key.derive_address(),
            'senderPublicKey': self.sender_public_key.hex(),
            'requesterPublicKey': self.requester_public_key.hex() if self.requester_public_key else None,
            'fee': self.fee,
            'signature': self.signature.hex() if self.signature else None,
            'signSignature': self.second_signature.hex() if self.second_signature else None,
            'signatures': [sig.hex() for sig in (self.signatures or [])],
            'amount': self._amount,
            'recipientId': self._recipient or sender_address,
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

    @staticmethod
    def parse_json(data):
        base = super().parse_json(data)

        try:
            return {
                **base,
                'amount': Amount(data['amount']),
                'recipientId': Address(data['recipientId']),
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

    @staticmethod
    def parse_json(data):
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
            second_public_key = asset_sig['publicKey']
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

    @staticmethod
    def parse_json(data):
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

    @staticmethod
    def parse_json(data):
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

@transaction_type(4)
class RegisterMultisignatureTx(BaseTx):
    minimum_signatures: int
    lifetime: int
    add_public_keys: List[PublicKey]
    remove_public_keys: List[PublicKey]

    def __init__(
        self,
        sender_public_key: PublicKey,
        minimum_signatures: int,
        lifetime: int,
        add_public_keys: List[PublicKey],
        remove_public_keys: List[PublicKey],
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
        self.minimum_signatures = minimum_signatures
        self.lifetime = lifetime
        self.add_public_keys = add_public_keys
        self.remove_public_keys = remove_public_keys

    def _asset_bytes(self) -> bytes:
        buf = bytearray()
        buf.append(self.minimum_signatures)
        buf.append(self.lifetime)
        for pk in self.remove_public_keys:
            buf += bytes('-{}'.format(pk.hex()), 'utf8')
        for pk in self.add_public_keys:
            buf += bytes('+{}'.format(pk.hex()), 'utf8')
        return bytes(buf)

    def _asset_json(self):
        return {
            'multisignature': {
                'min': self.minimum_signatures,
                'lifetime': self.lifetime,
                'keysgroup': [
                    '-{}'.format(pk.hex()) for pk in self.remove_public_keys
                ] + [
                    '+{}'.format(pk.hex()) for pk in self.add_public_keys
                ],
            },
        }

    @staticmethod
    def parse_json(data):
        base = super().parse_json(data)

        try:
            asset = data['asset']
        except KeyError as err:
            raise ValueError('Data dictionary is missing "{}" item'.format(err.args[0]))

        try:
            asset_multisig = asset['multisignature']
        except KeyError as err:
            raise ValueError('Data dictionary is missing "asset.{}" item'.format(err.args[0]))

        try:
            minimum_signatures = int(asset_multisig['min'])
            lifetime = int(asset_multisig['lifetime'])
            signatories = asset_multisig['keysgroup']
        except KeyError as err:
            raise ValueError('Data dictionary is missing "asset.multisignature.{}" item'.format(err.args[0]))

        add_public_keys: List[PublicKey] = []
        remove_public_keys: List[PublicKey] = []
        for val in signatories:
            if val[0] == '-':
                remove_public_keys.append(PublicKey.fromhex(val[1:]))
            elif val[0] == '+':
                add_public_keys.append(PublicKey.fromhex(val[1:]))

        return {
            **base,
            'minimum_signatures': minimum_signatures,
            'lifetime': lifetime,
            'add_public_keys': add_public_keys,
            'remove_public_keys': remove_public_keys,
        }
