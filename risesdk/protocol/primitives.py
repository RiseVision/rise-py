from typing import Union
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import os
import ed25519

RISE_EPOCH = datetime(2016, 4, 24, 17, 0, 0, 0)
UNIT_SCALE = 100000000

class Timestamp(int):
    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if value < 0:
            raise ValueError('Must be a positive value')
        return value

    @staticmethod
    def now() -> 'Timestamp':
        return Timestamp.from_datetime(datetime.utcnow())

    @staticmethod
    def from_datetime(dt: datetime) -> 'Timestamp':
        dur = dt - RISE_EPOCH
        return Timestamp(dur.total_seconds())

    def to_datetime(self) -> datetime:
        dur = timedelta(seconds=self)
        return RISE_EPOCH + dur

class Amount(int):
    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if value < 0:
            raise ValueError('Must be a positive value')
        if value > 0xFFFFFFFFFFFFFFFF:
            raise ValueError('Too big value')
        return value

    @staticmethod
    def from_unit(value: Union[Decimal, Union[int, str]]) -> 'Amount':
        return Amount(Decimal(value) * UNIT_SCALE)

    def to_unit(self) -> Decimal:
        return Decimal(self) / UNIT_SCALE

class Address(str):
    def __new__(cls, address):
        value = super().__new__(cls, address.upper())
        if not value.endswith('R'):
            raise ValueError('Invalid address')
        return value

    def to_bytes(self) -> bytes:
        return int(self[:-1]).to_bytes(8, byteorder='big')

class Signature(bytes):
    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if len(value) != 64:
            raise ValueError('Must be exactly 64 bytes')
        return value

class PublicKey(bytes):
    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if len(value) != 32:
            raise ValueError('Must be exactly 32 bytes')
        return value

    def derive_address(self) -> Address:
        digest = hashlib.sha256(self).digest()
        i = int.from_bytes(digest[:8], byteorder='little')
        return Address('{}R'.format(i))

    def verify(self, signature: Signature, message: bytes) -> bool:
        vk = ed25519.VerifyingKey(bytes(self))
        digest = hashlib.sha256(message).digest()
        try:
            vk.verify(bytes(signature), digest)
            return True
        except ed25519.BadSignatureError:
            return False

class SecretKey(bytes):
    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if len(value) != 32:
            raise ValueError('Must be exactly 32 bytes')
        return value

    @staticmethod
    def generate(entropy=os.urandom) -> 'SecretKey':
        seed: bytes = entropy(32)
        return SecretKey(seed)

    @staticmethod
    def from_passphrase(passphrase: str) -> 'SecretKey':
        if not passphrase:
            raise ValueError('Missing passphrase')

        digest = hashlib.sha256(passphrase.encode('utf8')).digest()
        return SecretKey(digest)

    def derive_public_key(self) -> PublicKey:
        sk = ed25519.SigningKey(bytes(self))
        vk = sk.get_verifying_key()
        return PublicKey(vk.to_bytes())

    def sign(self, message: bytes) -> Signature:
        sk = ed25519.SigningKey(bytes(self))
        digest = hashlib.sha256(message).digest()
        return Signature(sk.sign(digest))
