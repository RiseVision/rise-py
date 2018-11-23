import unittest
from datetime import datetime
from risesdk.protocol import PublicKey, Signature, Address, Timestamp, Amount

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
        self.assertEqual(dt, datetime(2016, 4, 24, 17, 1, 40, 0))

    def test_from(self):
        dt = Timestamp.from_datetime(datetime(2016, 4, 24, 20, 25, 45, 0))
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
        value = Amount.from_unit('25')
        self.assertIsInstance(value, Amount)
        self.assertEqual(value, 2500000000)

class TestAddress(unittest.TestCase):
    def test_valid(self):
        value = Address('10820014087913201714R')
        self.assertIsInstance(value, Address)

class TestPublicKey(unittest.TestCase):
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
