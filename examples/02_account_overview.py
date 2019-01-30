from sys import exit, argv
from risesdk import (
    Address,
    SendTx,
    RegisterSecondSignatureTx,
    RegisterDelegateTx,
    VoteTx,
    Client,
)

# A simple command line utility to print an account overview
api = Client('https://wallet.rise.vision/api/')
print('=== Network: RISE mainnet ===')
print()


def parse_address(val):
    val = val.upper()
    if not val.endswith('R'):
        return None
    try:
        int(val[:-1])
    except ValueError:
        return None
    return Address(val)


# Get the address from the command arguments, or prompt for it
address = None
if len(argv) >= 2:
    address = parse_address(argv[1])
while address is None:
    inp = input('Enter RISE address: ')
    if not inp:
        print('Empty input, exiting...')
        exit(0)
    address = parse_address(inp)
    if not address:
        print('Invalid address format, try again..')

acc = api.accounts.get_account(address)
if acc is None:
    print('Account {} doesn\'t exist on the network :('.format(address))
    exit(0)

votes = api.accounts.get_account_delegates(address)

print('== Account overview ==')
print('Address: {}'.format(acc.address))
print('Balance: {} RISE'.format(acc.balance.to_unit()))
print('Balance (unconfirmed): {} RISE'.format(acc.unconfirmed_balance.to_unit()))
print('Public key: {}'.format('(unknown)' if acc.public_key is None else acc.public_key.hex()))
print('Has second signature: {}'.format('Yes' if acc.second_signature else 'No'))
print('Voted delegate: {}'.format(
    '(none)' if len(votes) < 1 else '{} ({})'.format(votes[0].username, votes[0].address)
))
print()

# Print delegate information if the account has registered as one
if acc.public_key:
    delegate = api.delegates.get_delegate(acc.public_key)
else:
    delegate = None
if delegate:
    print('== Delegate overview ==')
    print('Username: {}'.format(delegate.username))
    print('Rank: {}'.format(delegate.rank))
    print('Approval: {}'.format(delegate.approval))
    print('Productivity: {}'.format(delegate.productivity))
    print('Consecutive missed blocks: {}'.format(delegate.consecutive_missed_blocks))
    print()

# Get and print transactions
if acc.public_key:
    utxs = api.transactions.get_unconfirmed_transactions(acc.public_key)
else:
    utxs = None
txs = api.transactions.get_transactions(
    # sender OR recipient is the current address
    sender=acc.address,
    recipient=acc.address,
    limit=10,
    order_by='height:desc',
)


def tx_summary_string(tx):
    if isinstance(tx.tx, SendTx):
        if tx.tx.recipient == acc.address:
            return 'Incoming transfer of {} RISE (from {})'.format(
                tx.tx.amount.to_unit(),
                tx.tx.sender_public_key.derive_address(),
            )
        else:
            return 'Outgoing transfer of {} RISE (to {})'.format(
                tx.tx.amount.to_unit(),
                tx.tx.recipient,
            )
    elif isinstance(tx.tx, RegisterSecondSignatureTx):
        return 'Register second signature'
    elif isinstance(tx.tx, RegisterDelegateTx):
        return 'Register as a delegate (username: {})'.format(
            tx.tx.username
        )
    elif isinstance(tx.tx, VoteTx):
        if len(tx.tx.add_votes) > 0:
            return 'Vote for {}'.format(tx.tx.add_votes[0].derive_address())
        elif len(tx.tx.remove_votes) > 0:
            return 'Remove vote from {}'.format(tx.tx.remove_votes[0].derive_address())
    return 'Unknown transaction ({})'.format(tx.tx_id)


if len(txs.transactions) > 0 or (utxs and len(utxs.transactions) > 0):
    print('== Recent transactions ==')
    if utxs and len(utxs.transactions) > 0:
        for tx in utxs.transactions:
            print('- {} (unconfirmed)'.format(tx_summary_string(tx)))
    for tx in txs.transactions:
        print('- {}'.format(tx_summary_string(tx)))
    print()
