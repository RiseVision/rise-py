# RISE Python SDK Examples

This folder contains some examples on how the risesdk package can be used to interact with the RISE blockchain.

All of these examples are standalone and you can run them just by executing the python file in this folder. You do, however, need to make sure that the _risesdk_ package is discoverable by Python. You can do that either by installing the package, or using the _PYTHONPATH_ environment variable as follows:

```
$ PYTHONPATH=../ python 01_summary.py
```

## 1. Current blockchain state summary

This example queries the blockchain for some of it's current state. That includes the height, supply, fees and top delegates. Three different API usages are demonstrated: `api.blocks.get_status()`, `api.blocks.get_fees()` and `api.delegates.get_delegates(..)`.

Source: [01_summary.py](https://github.com/RiseVision/rise-py/blob/master/examples/01_summary.py)

## 2. Account overview

This example queries the blockchain for data about the specified account. The balance & unconfirmed balance, current vote, delegate information (if registered) and a summary of recent transactions is displayed by the script. `api.accounts.get_account(..)`, `api.accounts.get_account_delegates(..)`, `api.delegates.get_delegate(..)`, `api.transactions.get_unconfirmed_transactions(..)` and `api.transactions.get_transactions(..)` API usages are demonstrated.

Source: [02_summary.py](https://github.com/RiseVision/rise-py/blob/master/examples/02_account_overview.py)

## 3. Raffle bot

This is a fully funcional raffle bot example (on the testnet), where people can send RISE to the raffle bot account to buy entries to the raffle rounds. The more RISE they send, the more entries they get to win the whole prize pool.

The bot also takes a 2.5% maintenance fee from the incoming ticket purchases. This feature exists in this example for the sole reason of covering outgoing transaction costs. Each round is closed by creating a transaction on the blockchain, which has a 0.1 RISE cost associate with it.

The example demonstrates working with `SecretKey`, `PublicKey` and `Address` primitives, covers various REST API calls related to getting information about transactions, blocks and (most importantly) submitting new transactions.

Source: [03_raffle.py](https://github.com/RiseVision/rise-py/blob/master/examples/03_raffle.py)
