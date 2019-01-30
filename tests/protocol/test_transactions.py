import unittest
from tests.fixtures import Fixtures
from risesdk.protocol import (
    Timestamp,
    Amount,
    Address,
    SecretKey,
    PublicKey,
    Signature,
    BaseTx,
    SendTx,
    RegisterSecondSignatureTx,
    RegisterDelegateTx,
    VoteTx,
)


class TestTransactions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = Fixtures()

    def test_tx_fixtures(self):
        tests = [
            ('send', self.fixtures.send_txs, SendTx),
            ('delegate', self.fixtures.delegate_txs, RegisterDelegateTx),
            ('vote_txs', self.fixtures.vote_txs, VoteTx),
        ]
        for (fixture, raw_txs, tx_cls) in tests:
            for (idx, raw_tx) in enumerate(raw_txs):
                with self.subTest(fixture=fixture, index=idx):
                    tx = BaseTx.from_json(raw_tx)
                    self.assertIsInstance(tx, tx_cls)

                    # Verify signatures
                    pk, sig = tx.sender_public_key, tx.signature
                    msg = tx.to_bytes(skip_signature=True, skip_second_signature=True)
                    self.assertTrue(pk.verify(sig, msg))

    def test_signing_fixtures(self):
        for (idx, raw) in enumerate(self.fixtures.second_signature_txs):
            with self.subTest(index=idx):
                sk1 = SecretKey.from_passphrase(raw['secret'])
                sk2 = SecretKey.from_passphrase(raw['secondSecret'])
                tx = BaseTx.from_json(raw['tx'])

                msg1 = tx.to_bytes(skip_signature=True, skip_second_signature=True)
                sig1 = sk1.sign(msg1)
                self.assertEqual(sig1, tx.signature)

                msg2 = tx.to_bytes(skip_second_signature=True)
                sig2 = sk2.sign(msg2)
                self.assertEqual(sig2, tx.second_signature)

    def test_send_from_json(self):
        raw_tx = {
            'type': 0,
            'id': '1092317355789257411',
            'timestamp': 78872341,
            'senderPublicKey': '061c63bbaa21ab00ee5c51f4af169f79572f06a74b60b5a2d2d6700aa008aa33',
            'senderId': '17164919068117155466R',
            'recipientId': '13696181858322754778R',
            'amount': 10000000000,
            'fee': 10000000,
            'requesterPublicKey': None,
            'asset': None,
            'signature': '9330b761583736c0f97b6bc15a5457c574bac0d8b4c10f1f3e7b29840c33baff'
                         '4c819f8a416a66919d676e3ae94e5fe5149e7e6c806758372a7df9ba12da1104',
            'signSignature': None,
            'signatures': [],
        }

        # Parse and check that the data is correctly parsed
        tx = BaseTx.from_json(raw_tx)
        self.assertIsInstance(tx, SendTx)
        self.assertIsInstance(tx.timestamp, Timestamp)
        self.assertEqual(tx.timestamp, Timestamp(78872341))
        self.assertIsInstance(tx.sender_public_key, PublicKey)
        self.assertEqual(tx.sender_public_key,
                         PublicKey.fromhex('061c63bbaa21ab00ee5c51f4af169f79572f06a74b60b5a2d2d6700aa008aa33'))
        self.assertEqual(tx.requester_public_key, None)
        self.assertIsInstance(tx.fee, Amount)
        self.assertEqual(tx.fee, Amount.from_unit('0.1'))
        self.assertIsInstance(tx.signature, Signature)
        self.assertEqual(tx.signature,
                         Signature.fromhex('9330b761583736c0f97b6bc15a5457c574bac0d8b4c10f1f3e7b29840c33baff'
                                           '4c819f8a416a66919d676e3ae94e5fe5149e7e6c806758372a7df9ba12da1104'))
        self.assertEqual(tx.second_signature, None)
        self.assertEqual(tx.signatures, [])
        self.assertIsInstance(tx.amount, Amount)
        self.assertEqual(tx.amount, Amount.from_unit(100))
        self.assertIsInstance(tx.recipient, Address)
        self.assertEqual(tx.recipient, Address('13696181858322754778R'))

        # Check that serialization is done correctly
        self.assertEqual(tx.to_bytes(), bytes.fromhex('00157fb304061c63bbaa21ab00ee5c51f4af169f79572f06a74b60b5a2d2'
                                                      'd6700aa008aa33be129cd5ac7a2cda00e40b54020000009330b761583736'
                                                      'c0f97b6bc15a5457c574bac0d8b4c10f1f3e7b29840c33baff4c819f8a41'
                                                      '6a66919d676e3ae94e5fe5149e7e6c806758372a7df9ba12da1104'))

        # Check that we're able to get back the original raw_tx
        self.assertEqual(tx.to_json(), raw_tx)

    def test_vote_from_json(self):
        raw_tx = {
            'type': 3,
            'id': '16152087920553557659',
            'timestamp': 73873282,
            'senderPublicKey': 'b3dc9171d784a3669482103951e0e8e89429f78ee5634950f0f4a7f8fad19378',
            'senderId': '10820014087913201714R',
            'recipientId': '10820014087913201714R',
            'amount': 0,
            'fee': 100000000,
            'asset': {
                'votes': [
                    '-151b4d4c6de2395ec0af23274768c58b9a2b0dedfda3a6841e2a20a51f955c3b',
                    '+e1fb38191066f18e3e381ce41e80735aaab24df672df93304363ff923b320d8c',
                ],
            },
            'requesterPublicKey': None,
            'signature': 'b0742a9c4f2d022bde9aacfa8a7ad8667c44978c11ad076316118f9717f2b278'
                         '4e72b7ca4f6ba6865b4d0baca536151a37c6c6a3679f2ce330b7c3739d3d000c',
            'signSignature': None,
            'signatures': [],
        }

        # Parse and check that the data is correctly parsed
        tx = BaseTx.from_json(raw_tx)
        self.assertIsInstance(tx, VoteTx)
        self.assertIsInstance(tx.timestamp, Timestamp)
        self.assertEqual(tx.timestamp, Timestamp(73873282))
        self.assertIsInstance(tx.sender_public_key, PublicKey)
        self.assertEqual(tx.sender_public_key,
                         PublicKey.fromhex('b3dc9171d784a3669482103951e0e8e89429f78ee5634950f0f4a7f8fad19378'))
        self.assertEqual(tx.requester_public_key, None)
        self.assertIsInstance(tx.fee, Amount)
        self.assertEqual(tx.fee, Amount.from_unit('1'))
        self.assertIsInstance(tx.signature, Signature)
        self.assertEqual(tx.signature,
                         Signature.fromhex('b0742a9c4f2d022bde9aacfa8a7ad8667c44978c11ad076316118f9717f2b278'
                                           '4e72b7ca4f6ba6865b4d0baca536151a37c6c6a3679f2ce330b7c3739d3d000c'))
        self.assertEqual(tx.second_signature, None)
        self.assertEqual(tx.signatures, [])
        self.assertEqual(tx.add_votes,
                         [PublicKey.fromhex('e1fb38191066f18e3e381ce41e80735aaab24df672df93304363ff923b320d8c')])
        self.assertEqual(tx.remove_votes,
                         [PublicKey.fromhex('151b4d4c6de2395ec0af23274768c58b9a2b0dedfda3a6841e2a20a51f955c3b')])

        # Check that we're able to get back the original raw_tx
        self.assertEqual(tx.to_json(), raw_tx)

    def test_register_delegate_from_json(self):
        raw_tx = {
            'type': 2,
            'id': '10022032017304944489',
            'timestamp': 71349199,
            'senderPublicKey': 'b3dc9171d784a3669482103951e0e8e89429f78ee5634950f0f4a7f8fad19378',
            'senderId': '10820014087913201714R',
            'recipientId': None,
            'amount': 0,
            'fee': 2500000000,
            'asset': {
                'delegate': {
                    'username': '123sadasd@@@asd',
                },
            },
            'requesterPublicKey': None,
            'signatures': [],
            'signature': 'e40f9f9052946bfa7cec888f5f910da573ff4d883b099393d41047ff00cf1c59'
                         'fa7ba01ff4df06385506fc9e13ebddc898d1906c16736e56a2fe7aaec986800a',
            'signSignature': None,
        }

        # Parse and check that the data is correctly parsed
        tx = BaseTx.from_json(raw_tx)
        self.assertIsInstance(tx, RegisterDelegateTx)
        self.assertIsInstance(tx.timestamp, Timestamp)
        self.assertEqual(tx.timestamp, Timestamp(71349199))
        self.assertIsInstance(tx.sender_public_key, PublicKey)
        self.assertEqual(tx.sender_public_key,
                         PublicKey.fromhex('b3dc9171d784a3669482103951e0e8e89429f78ee5634950f0f4a7f8fad19378'))
        self.assertEqual(tx.requester_public_key, None)
        self.assertIsInstance(tx.fee, Amount)
        self.assertEqual(tx.fee, Amount.from_unit('25'))
        self.assertIsInstance(tx.signature, Signature)
        self.assertEqual(tx.signature,
                         Signature.fromhex('e40f9f9052946bfa7cec888f5f910da573ff4d883b099393d41047ff00cf1c59'
                                           'fa7ba01ff4df06385506fc9e13ebddc898d1906c16736e56a2fe7aaec986800a'))
        self.assertEqual(tx.second_signature, None)
        self.assertEqual(tx.signatures, [])
        self.assertEqual(tx.username, '123sadasd@@@asd')

        # Check that we're able to get back the original raw_tx
        self.assertEqual(tx.to_json(), raw_tx)

    def test_register_second_signature_from_json(self):
        raw_tx = {
            'type': 1,
            'id': '7295833138365523053',
            'timestamp': 71800027,
            'senderPublicKey': '45b6cf39cb819fb8dfc9f241caaf5f54be9f39fd66837c99e9d08161c9339684',
            'senderId': '7851658041862611161R',
            'recipientId': None,
            'amount': 0,
            'fee': 500000000,
            'asset': {
                'signature': {
                    'publicKey': 'ca311fd450248e1faa90e6353ce3cdd913465679b90fbb9d4da9345d580feabb',
                },
            },
            'requesterPublicKey': None,
            'signature': '3a529c162c223d0ecc88ced17d3d93e4c69d74601da129753c05afb31e25a83a'
                         'b923ed85760e5dc1f2925d70d4ce9bc59a1fdc00f2b7f82384aeb443d0328e0d',
            'signSignature': None,
            'signatures': [],
        }

        # Parse and check that the data is correctly parsed
        tx = BaseTx.from_json(raw_tx)
        self.assertIsInstance(tx, RegisterSecondSignatureTx)
        self.assertIsInstance(tx.timestamp, Timestamp)
        self.assertEqual(tx.timestamp, Timestamp(71800027))
        self.assertIsInstance(tx.sender_public_key, PublicKey)
        self.assertEqual(tx.sender_public_key,
                         PublicKey.fromhex('45b6cf39cb819fb8dfc9f241caaf5f54be9f39fd66837c99e9d08161c9339684'))
        self.assertEqual(tx.requester_public_key, None)
        self.assertIsInstance(tx.fee, Amount)
        self.assertEqual(tx.fee, Amount.from_unit('5'))
        self.assertIsInstance(tx.signature, Signature)
        self.assertEqual(tx.signature,
                         Signature.fromhex('3a529c162c223d0ecc88ced17d3d93e4c69d74601da129753c05afb31e25a83a'
                                           'b923ed85760e5dc1f2925d70d4ce9bc59a1fdc00f2b7f82384aeb443d0328e0d'))
        self.assertEqual(tx.second_signature, None)
        self.assertEqual(tx.signatures, [])
        self.assertIsInstance(tx.second_public_key, PublicKey)
        self.assertEqual(tx.second_public_key,
                         PublicKey.fromhex('ca311fd450248e1faa90e6353ce3cdd913465679b90fbb9d4da9345d580feabb'))

        # Check that we're able to get back the original raw_tx
        self.assertEqual(tx.to_json(), raw_tx)
