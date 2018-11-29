import unittest
from datetime import datetime
from risesdk.protocol import (
    SecretKey,
    PublicKey,
    Signature,
    Address,
    Timestamp,
    Amount,
)
from tests.fixtures import Fixtures

class TestTimestamp(unittest.TestCase):
    def test_negative(self):
        for i in [-1, -10]:
            with self.subTest(i=i):
                with self.assertRaises(ValueError):
                    Timestamp(i)

    def test_valid(self):
        for i in [0, 1, 10, 100000]:
            with self.subTest(i=i):
                value = Timestamp(i)
                self.assertIsInstance(value, Timestamp)

    def test_to_datetime(self):
        dt = Timestamp(100).to_datetime()
        self.assertEqual(dt, datetime(2016, 5, 24, 17, 1, 40, 0))

    def test_from(self):
        dt = Timestamp.from_datetime(datetime(2016, 5, 24, 20, 25, 45, 0))
        self.assertEqual(dt, Timestamp(12345))

class TestAmount(unittest.TestCase):
    def test_negative(self):
        with self.assertRaises(ValueError):
            Amount(-1)

    def test_upper_bound(self):
        with self.assertRaises(ValueError):
            Amount.from_unit('184467440737.09551616')
        Amount.from_unit('184467440737.09551615')

    def test_valid(self):
        for i in [0, 1, 10, 100000]:
            with self.subTest(i=i):
                value = Amount(i)
                self.assertIsInstance(value, Amount)

    def test_from_unit(self):
        self.assertEqual(Amount.from_unit('25'), 2500000000)
        self.assertEqual(Amount.from_unit('0.1'), 10000000)

class TestAddress(unittest.TestCase):
    def test_valid(self):
        value = Address('10820014087913201714R')
        self.assertIsInstance(value, Address)

class TestPublicKey(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = Fixtures()

    def test_invalid(self):
        with self.assertRaises(ValueError):
            PublicKey([0, 1, 2])

    def test_valid(self):
        value = PublicKey([
             0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
        ])
        self.assertIsInstance(value, PublicKey)

    def test_derive_address(self):
        pk = PublicKey.fromhex('b3dc9171d784a3669482103951e0e8e89429f78ee5634950f0f4a7f8fad19378')
        self.assertEqual(Address('10820014087913201714R'), pk.derive_address())

    def test_verify(self):
        msg = b'Hello, world!'
        sig = Signature.fromhex('90906e741ccf000046672a4f7350dde1e7f6efe32389e8af79930ea6d42cbddc1f68419809da74bf69a09d9bac9cd3c1a32cf081a655e5fa44590be70c264c0a')
        pk = PublicKey.fromhex('9d3058175acab969f41ad9b86f7a2926c74258670fe56b37c429c01fca9f2f0f')

        self.assertEqual(pk.verify(sig, msg), True)
        self.assertEqual(pk.verify(sig, b'Wrong message'), False)

class TestSecretKey(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = Fixtures()

    def test_derive_public_key(self):
        for (idx, raw) in enumerate(self.fixtures.genesis_delegates['delegates']):
            with self.subTest(username=raw['username'], index=idx):
                sk = SecretKey.from_passphrase(raw['secret'])
                self.assertIsInstance(sk, SecretKey)
                pk = sk.derive_public_key()
                self.assertIsInstance(pk, PublicKey)
                self.assertEqual(pk, PublicKey.fromhex(raw['publicKey']))

    def test_sign(self):
        msg = b'Hello, world!'
        sk = SecretKey.from_passphrase('robust swift grocery peasant forget share enable convince deputy road keep cheap')

        sig = sk.sign(msg)
        self.assertIsInstance(sig, Signature)
        self.assertEqual(sig, Signature.fromhex('90906e741ccf000046672a4f7350dde1e7f6efe32389e8af79930ea6d42cbddc1f68419809da74bf69a09d9bac9cd3c1a32cf081a655e5fa44590be70c264c0a'))

    def test_generate(self):
        sk = SecretKey.generate()
        self.assertIsInstance(sk, SecretKey)

class TestSignature(unittest.TestCase):
    def test_invalid(self):
        with self.assertRaises(ValueError):
            Signature([0, 1, 2])

    def test_valid(self):
        value = Signature([
             0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
            32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
            48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
        ])
        self.assertIsInstance(value, Signature)
