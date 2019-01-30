import json
from os import path

FIXTURES_DIR = path.abspath(path.dirname(__file__))


def _load(name):
    with open(path.join(FIXTURES_DIR, name), encoding='utf-8') as fp:
        return json.load(fp)


class Fixtures(object):
    def __init__(self):
        self.delegate_txs = _load('delegateTxs.json')
        self.second_signature_txs = _load('secondSignatureTxs.json')
        self.send_txs = _load('sendTxs.json')
        self.vote_txs = _load('voteTxs.json')
        self.genesis_delegates = _load('genesisDelegates.json')
