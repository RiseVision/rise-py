"""
This example demonstrates how to build a raffle system on top of RISE blockchain.
The raffle works by users sending RISE to the account controlled by this script.
That buys them entries to the raffle. The more RISE they send, the more entries
they get. After a certain amount of time, the raffle round closes. The winner
is picked randomly and will be sent the prize pool content.

On a more technical note, all of the data needed for this to work will be
stored on the blockchain. Round closures are marked by outgoing transactions.
The outgoing transactions can be either the transfer of the winnings, or a
send transaction to itself (burning 0.1 RISE as the fees).

For the raffle to be fair, the round has to be closed before the winner can be
selected. Otherwise people who enter late will have a significant chance of
not being included in the round. Because of that, the raffle will take 2 rounds.
When the round is opened, the users will buy tickets. Then the round is closed
and a new round starts. After the 2nd round ends, the winner of the 1st round
is determined and will be awarded the prize.
"""

import time
from random import randint
from mnemonic import Mnemonic
from decimal import Decimal
from risesdk import (
    Timestamp,
    Amount,
    SecretKey,
    SendTx,
    Client,
)

ROUND_TIME = 300  # seconds (5 minutes)
HOUSE_FEE = Decimal('0.025')  # percent (2.5%)

api = Client('https://twallet.rise.vision/api/')
print('=== Network: RISE testnet ===')
print()

###
# Get the raffle account secret key
###
print('Enter the raffle account 12-word passhphrase or hex-encoded secret key. '
      'Or leave empty to generate a new mnemonic.')
raf_sk = None
inp = input('Passphrase / secret key: ').strip()
if not inp:
    passphrase = Mnemonic('english').generate()
    print()
    print('Your new raffle account passphrase is:')
    print()
    print('===============================================================================')
    print('|                              WRITE THIS DOWN                                |')
    print('===============================================================================')
    print()
    print(passphrase)
    print()
    print('===============================================================================')
    print()
    raf_sk = SecretKey.from_passphrase(passphrase)
else:
    try:
        raf_sk = SecretKey.fromhex(inp)
    except ValueError:
        raf_sk = SecretKey.from_passphrase(inp)
    print()

raf_pk = raf_sk.derive_public_key()
raf_addr = raf_pk.derive_address()

print('Raffle account: {}'.format(raf_addr))
print()


def sleep_for(seconds, msg='Waiting for {} seconds...'):
    while seconds > 0:
        output = msg.format(seconds)
        print(output, end='', flush=True)
        time.sleep(1)
        seconds -= 1
        print('\b' * len(output), end='')


###
# Determine the start time of the current round
###
round_started = None

# 1. Try to find the last round closing transaction in unconfirmed pool
if round_started is None:
    r = api.transactions.get_unconfirmed_transactions(raf_pk)
    send_txs = (tx for tx in r.transactions if isinstance(tx.tx, SendTx))
    for tx in send_txs:
        if round_started is None or round_started < tx.tx.timestamp:
            round_started = tx.tx.timestamp
# 2. Try to find the last round closing transaction in the chain
if round_started is None:
    r = api.transactions.get_transactions(
        and__type_cls=SendTx,
        and__sender_public_key=raf_pk,
        limit=1,
        order_by='timestamp:desc',
    )
    if len(r.transactions) > 0:
        round_started = r.transactions[0].tx.timestamp
# 3. Use the timestamp of the first block with incoming transactions
if round_started is None:
    r = api.transactions.get_transactions(
        and__type_cls=SendTx,
        and__recipient=raf_addr,
        limit=1,
        order_by='height:asc',
    )
    if len(r.transactions) > 0:
        first_tx = r.transactions[0]
        block = api.blocks.get_block(first_tx.block_id)
        assert block, 'Block should have been found'
        round_started = block.timestamp
# 4. If nothing else, then mark the round as just started
if round_started is None:
    round_started = Timestamp.now()

###
# Start the main raffle loop
###
print('Raffle system started')

while True:
    round_duration = Timestamp.now() - round_started
    if round_duration < ROUND_TIME:
        wait_time = max(0, ROUND_TIME - round_duration)
        sleep_for(wait_time, 'Waiting {} seconds for the round to end...')

    # Make sure that all of our send blocks have been confirmed
    r = api.transactions.get_unconfirmed_transactions(raf_pk)
    send_txs = [tx for tx in r.transactions if isinstance(tx.tx, SendTx)]
    if len(send_txs) > 0:
        wait_time = 60
        sleep_for(wait_time, 'Oops! Our last transaction hasn\'t made it to the chain yet, waiting {} seconds...')
        continue

    # Determine the blocks where we'll be looking for the raffle entries
    from_height = None
    to_height = None
    r = api.transactions.get_transactions(
        and__type_cls=SendTx,
        and__sender_public_key=raf_pk,
        limit=2,
        order_by='height:desc',
    )
    for tx in r.transactions:
        if to_height is None:
            to_height = tx.height
        elif from_height is None:
            from_height = min(tx.height + 1, to_height)

    tickets = []
    total_tickets = 0
    round_prize_pool = Amount(0)
    winner_public_key = None

    # Count the tickets. For the very first round we skip this step (to_height is None)
    if to_height is not None:
        tickets_map = {}
        offset = 0
        while offset is not None:
            r = api.transactions.get_transactions(
                and__type_cls=SendTx,
                and__recipient=raf_addr,
                and__to_height=to_height,
                and__from_height=from_height,
                offset=offset,
                order_by='height:desc',
            )
            if offset + len(r.transactions) >= r.count:
                offset = None
            else:
                offset += len(r.transactions)

            for tx in r.transactions:
                # Make sure we don't allocate any tickets to the raffle system itself
                if tx.tx.sender_public_key == raf_pk:
                    continue
                prev_tickets = tickets_map.get(tx.tx.sender_public_key, 0)
                tickets_map[tx.tx.sender_public_key] = prev_tickets + int(tx.tx.amount)
                total_tickets = total_tickets + tx.tx.amount
        tickets = list(tickets_map.items())
        round_prize_pool = Amount(total_tickets * (1 - HOUSE_FEE))

        # Determine the winner (by using weighted random)
        if total_tickets > 0:
            i = randint(1, total_tickets)
            for (pk, entries) in tickets:
                i -= entries
                if i <= 0:
                    # Winner!
                    winner_public_key = pk
                    break
            assert winner_public_key, 'Random selection is malfunctioning'

        print()
        print('Round #{} stats:'.format(to_height))
        print('- Prize pool: {} RISE'.format(round_prize_pool.to_unit()))
        print('- Participants: {}'.format(len(tickets)))
        print('- Total tickets: {}'.format(total_tickets))
        if winner_public_key:
            print('- Winner: {}'.format(winner_public_key.derive_address()))
        print()

    # Get the current fee
    r = api.blocks.get_fees()
    fees = r.fees

    # Close the round by paying the winner or doing a no-op Send transaction
    if winner_public_key:
        tx = SendTx(
            sender_public_key=raf_pk,
            recipient=winner_public_key.derive_address(),
            amount=round_prize_pool,
            fee=fees.send,
            timestamp=Timestamp.now(),
        )
    else:
        tx = SendTx(
            sender_public_key=raf_pk,
            recipient=raf_addr,
            amount=Amount(1),
            fee=fees.send,
            timestamp=Timestamp.now(),
        )
    tx.signature = raf_sk.sign(tx.to_bytes(
        skip_signature=True,
        skip_second_signature=True,
    ))

    while tx is not None:
        r = api.transactions.add_transactions(tx)
        if len(r.rejected) > 0:
            wait_time = 15
            print('Oops! Failed to submit round close transaction: {}'.format(r.rejected[0].reason))
            sleep_for(wait_time, 'Retrying in {} seconds...')
        else:
            print('Submitted round close transaction ({})'.format(tx.derive_id()))
            round_started = tx.timestamp
            tx = None
