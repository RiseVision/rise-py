from risesdk import Client

# Connect to the RISE hosted public node and print out a basic summary
api = Client('https://wallet.rise.vision/api/')
print('=== Network: RISE mainnet ===')
print()

status = api.blocks.get_status()
print('== Chain stats ==')
print('Chain height: {}'.format(status.height))
print('Current supply: {} RISE'.format(status.supply.to_unit()))
print('Block reward: {} RISE'.format(status.reward.to_unit()))
print('')

r = api.blocks.get_fees()
print('== Transaction fees ==')
print('Send: {} RISE'.format(r.fees.send.to_unit()))
print('Vote: {} RISE'.format(r.fees.vote.to_unit()))
print('Second signature setup: {} RISE'.format(r.fees.second_signature.to_unit()))
print('Delegate registration: {} RISE'.format(r.fees.delegate.to_unit()))
print('')

r = api.delegates.get_delegates(
    limit=5,
    order_by='rank:asc',
)
print('== Top 5 delegates ==')
for delegate in r.delegates:
    print('#{}: {} ({})'.format(
        delegate.rank,
        delegate.username,
        delegate.address,
    ))
