import unittest
from risesdk.protocol import (
    Address,
    Amount,
    Timestamp,
    PublicKey,
    Signature,
    SendTx,
)
from risesdk.api import APIError, Client
from risesdk.api.delegates import ForgingStatusResult

class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client('https://twallet.rise.vision/api/')

class TestAccountsAPI(APITestCase):
    def test_get_account(self):
        self.client.accounts.get_account(address=Address('7851658041862611161R'))

    def test_get_account_delegates(self):
        self.client.accounts.get_account_delegates(Address('7851658041862611161R'))

class TestBlocksAPI(APITestCase):
    def test_get_blocks(self):
        self.client.blocks.get_blocks(previous_block_id='5970675629734741993')

    def test_get_block(self):
        self.client.blocks.get_block('5970675629734741993')

    def test_get_fees(self):
        self.client.blocks.get_fees()

    def test_get_status(self):
        self.client.blocks.get_status()

class TestDelegatesAPI(APITestCase):
    def test_get_delegates(self):
        self.client.delegates.get_delegates(limit=3)

    def test_get_forged_by_account(self):
        self.client.delegates.get_forged_by_account(
            generator_public_key=PublicKey.fromhex('8a11b8b63427ab4d3bd5114bb7264d635cbcb7359fcc7e938c3603d32e154a3f'),
        )

    def test_get_delegate(self):
        self.client.delegates.get_delegate(
            public_key=PublicKey.fromhex('8a11b8b63427ab4d3bd5114bb7264d635cbcb7359fcc7e938c3603d32e154a3f'),
        )

    def test_get_voters(self):
        self.client.delegates.get_voters(
            public_key=PublicKey.fromhex('8a11b8b63427ab4d3bd5114bb7264d635cbcb7359fcc7e938c3603d32e154a3f'),
        )

    def test_search_delegates(self):
        self.client.delegates.search_delegates('mcanever')

    def test_get_delegate_count(self):
        self.client.delegates.get_delegate_count()

    def test_get_next_forgers(self):
        self.client.delegates.get_next_forgers()

    def test_get_forging_status(self):
        # The public API we use should deny us access to this API
        try:
            self.client.delegates.get_forging_status()
        except APIError as err:
            self.assertEqual(err.args[0], 'Delegates API access denied')

        # Instead test the parsing directly
        ForgingStatusResult({
            'enabled': True,
            'delegates': [
                'df06ac715314397ae7736d0ad448c6524dc89752ee41147bc6b7dd44948bd8b1',
                '976b9f0c87004fee662de6bdccdbe22125a0de04cb4692ead9c713bd4a201380',
                '0b7bb40385c5261c8cc763babebc9ccf9d392e618dc15104db5efb1c6a5719ee',
                '1413fc21fb3caa48a934b81e04f4a57b8e4042c255f3738135e1e4803dd146cb',
            ],
        })

    def test_enable_forging(self):
        # The public API we use should deny us access to this API
        try:
            secret = 'robust swift grocery peasant forget share enable convince deputy road keep cheap'
            self.client.delegates.enable_forging(secret)
        except APIError as err:
            self.assertEqual(err.args[0], 'Delegates API access denied')

    def test_disable_forging(self):
        # The public API we use should deny us access to this API
        try:
            secret = 'robust swift grocery peasant forget share enable convince deputy road keep cheap'
            self.client.delegates.disable_forging(secret)
        except APIError as err:
            self.assertEqual(err.args[0], 'Delegates API access denied')

class TestTransactionsAPI(APITestCase):
    def test_get_transactions(self):
        # Get all incoming and outgoing send transactions for an account
        self.client.transactions.get_transactions(
            and__type_cls=SendTx,
            sender=Address('7851658041862611161R'),
            recipient=Address('7851658041862611161R'),
        )

    def test_add_transactions(self):
        # Resubmit an old tx
        tx = SendTx(
            sender_public_key=PublicKey.fromhex('b3dc9171d784a3669482103951e0e8e89429f78ee5634950f0f4a7f8fad19378'),
            recipient=Address('7851658041862611161R'),
            amount=Amount(3500000000),
            fee=Amount(10000000),
            timestamp=Timestamp(71278993),
            signature=Signature.fromhex('f3fa873fba4619a82becef2c3921d883b44055f6644acc6721be47e451f45ca00eb657f476f08b7b5f3035cbe60b7b2e5d68290e8391bdc152340df75c5f390f'),
        )
        self.client.transactions.add_transactions(tx)

    def test_get_transaction_count(self):
        self.client.transactions.get_transaction_count()

    def test_get_transaction(self):
        self.client.transactions.get_transaction('11932194661546784672')

    def test_get_queued_transactions(self):
        self.client.transactions.get_queued_transactions()

    def test_get_queued_transaction(self):
        tx = self.client.transactions.get_queued_transaction('15656453436546686275')
        self.assertIsNone(tx)

    def test_get_unconfirmed_transactions(self):
        self.client.transactions.get_unconfirmed_transactions()

    def test_get_unconfirmed_transaction(self):
        tx = self.client.transactions.get_unconfirmed_transaction('15656453436546686275')
        self.assertIsNone(tx)
