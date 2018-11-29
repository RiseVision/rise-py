from typing import Union
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import os
import ed25519

RISE_EPOCH = datetime(2016, 5, 24, 17, 0, 0, 0)
UNIT_SCALE = 100000000

class Timestamp(int):
    '''
    Convenience type to represent timestamps.

    Timestamps in the RISE network are represented by a unsigned 64-bit integer
    and are defined as seconds from the RISE epoch (24th may 2016 at 17:00).
    '''

    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if value < 0:
            raise ValueError('Must be a positive value')
        return value

    @staticmethod
    def now() -> 'Timestamp':
        '''
        Return the Timestamp that corresponds to the current time.
        '''
        return Timestamp.from_datetime(datetime.utcnow())

    @staticmethod
    def from_datetime(dt: datetime) -> 'Timestamp':
        '''
        Convert the Python datetime object to Timestamp instance.
        '''
        dur = dt - RISE_EPOCH
        return Timestamp(dur.total_seconds())

    def to_datetime(self) -> datetime:
        '''
        Convert the Timestamp instance to Python datetime object.
        '''
        dur = timedelta(seconds=self)
        return RISE_EPOCH + dur

class Amount(int):
    '''
    Convenience type to represent amounts (in raws).

    The amounts are represented as unsigned 128-bit integer on the RISE network.
    1 RISE is equal to 100000000 raw.
    '''

    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if value < 0:
            raise ValueError('Must be a positive value')
        if value > 0xFFFFFFFFFFFFFFFF:
            raise ValueError('Too big value')
        return value

    @staticmethod
    def from_unit(value: Union[Decimal, Union[int, str]]) -> 'Amount':
        '''
        Create Amount instance by converting unit value to raws.

        For example:

        >>> Amount.from_unit('1.2') == Amount(120000000)
        True
        >>> Amount.from_unit(25) == Amount(2500000000)
        True
        '''
        return Amount(Decimal(value) * UNIT_SCALE)

    def to_unit(self) -> Decimal:
        '''
        Convert Amount instance to Decimal unit value

        For example:

        >>> from decimal import Decimal
        >>> Amount(120000000).to_unit() == Decimal('1.2')
        True
        >>> Amount(2500000000).to_unit() == Decimal(25)
        True
        '''
        return Decimal(self) / UNIT_SCALE

class Address(str):
    '''
    Convenience type to represent addresses.
    '''

    def __new__(cls, address):
        value = super().__new__(cls, address.upper())
        if not value.endswith('R'):
            raise ValueError('Invalid address')
        return value

    def to_bytes(self) -> bytes:
        return int(self[:-1]).to_bytes(8, byteorder='big')

class Signature(bytes):
    '''
    Convenience type to represent signatures.
    '''

    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if len(value) != 64:
            raise ValueError('Must be exactly 64 bytes')
        return value

class PublicKey(bytes):
    '''
    Convenience type to represent public key.
    '''

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
    '''
    Convenience type to represent secret keys.
    '''

    def __new__(cls, *args, **kwargs):
        value = super().__new__(cls, *args, **kwargs)
        if len(value) != 32:
            raise ValueError('Must be exactly 32 bytes')
        return value

    @staticmethod
    def generate(entropy=os.urandom) -> 'SecretKey':
        '''
        Generate new random secret key.

        This function uses os.urandom to generate the secret key. On systems where urandom isn't
        suitable for cryptographic, you should provide an alternative entropy function.
        '''
        seed: bytes = entropy(32)
        return SecretKey(seed)

    @staticmethod
    def from_passphrase(passphrase: str) -> 'SecretKey':
        '''
        Derive the secret key from a passphrase.

        For example:

        >>> sk = SecretKey.from_passphrase('robust swift grocery peasant forget share enable convince deputy road keep cheap')
        >>> sk.hex()
        'b092a6664e9eed658ff50fe796ee695b9fe5617e311e9e8a34eb340eb5b83154'
        '''
        if not passphrase:
            raise ValueError('Missing passphrase')

        digest = hashlib.sha256(passphrase.encode('utf8')).digest()
        return SecretKey(digest)

    def derive_public_key(self) -> PublicKey:
        '''
        Derives and returns the public key.
        '''
        sk = ed25519.SigningKey(bytes(self))
        vk = sk.get_verifying_key()
        return PublicKey(vk.to_bytes())

    def sign(self, message: bytes) -> Signature:
        '''
        Signs the provided message with the private key and returns the signature.
        '''
        sk = ed25519.SigningKey(bytes(self))
        digest = hashlib.sha256(message).digest()
        return Signature(sk.sign(digest))
