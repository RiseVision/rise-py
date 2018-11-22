from typing import Union
from datetime import datetime, timedelta
import hashlib
from decimal import Decimal

RISE_EPOCH = datetime(2016, 4, 24, 17, 0, 0, 0)
UNIT_SCALE = 100000000

class Timestamp(int):
    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if value <= 0:
            raise ValueError('Must be greater than zero')
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
        if value <= 0:
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
    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        value = value.upper()
        if not value.endswith('R'):
            raise ValueError('Invalid address')
        return value

    def to_bytes(self) -> bytes:
        return int(self[:-1]).to_bytes(8, byteorder='big')

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

class Signature(bytes):
    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if len(value) != 64:
            raise ValueError('Must be exactly 64 bytes')
        return value
