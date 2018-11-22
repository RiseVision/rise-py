import unittest
from risesdk.protocol.primitives import PublicKey, Address, Amount
from risesdk.protocol.transactions import SendTx

class TestTransactions(unittest.TestCase):
    def test_something(self):
        tx = SendTx(
            sender_public_key=PublicKey.fromhex('b3dc9171d784a3669482103951e0e8e89429f78ee5634950f0f4a7f8fad19378'),
            recipient=Address('10820014087913201714R'),
            amount=Amount.from_unit('1.230'),
            fee=Amount.from_unit('0.1'),
        )
        print(tx.to_json())
