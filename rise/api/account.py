"""
Module provides to access Rise Accounts API methods.
"""

from .base import BaseAPI


class AccountsAPI(BaseAPI):
    """
    AccountsAPI object provides access to Rise Accounts API methods.
    """
    def open(self, secret):
        """
        Opens a new account using the specified secret string
        :param secret: the string to use to generate the new account
        """
        return self._post('/accounts/open', secret=secret)

    def get_balance(self, address):
        """
        Returns balance and unconfirmed balance for the specified address
        :param address: address to check
        """
        return self._get('/accounts/getBalance', address=address)

    def get_public_key(self, address):
        """
        Returns the address public key
        """
        return self._get('/accounts/getPublicKey', address=address)

    def generate_public_key(self, secret):
        """
        Generates a Public Key
        :param secret: the secret to use
        """
        return self._post('/accounts/generatePublicKey', secret=secret)

    def get_account(self, address):
        """
        Get Account information by its address
        """
        return self._get('/accounts', address=address)

    def get_account_by_public_key(self, public_key):
        """
        Get Account information by its publicKey
        """
        return self._get('/accounts', publicKey=public_key)

    def get_delegates(self, address):
        """
        Return accounts delegates by using the given address
        """
        return self._get('/accounts/delegates', address=address)

    def put_delegates(self, secret, public_key, delegates, second_secret=None):
        """
        Cast votes. The delegates array must use delegate Public Key prepended witha "+" or "-" sign wether you want to up/downvote the delegate
        """
        return self._put('/accounts/delegates', secret=secret,
                        publicKey=public_key, delegates=delegates, secondSecret=second_secret)
