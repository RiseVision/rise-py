# RISE SDK (Python)

Python library that provides APIs for interfacing with the RISE blockchain.

## Getting started

The simplest way to get started is to use pip to install this library:

```
pip install risesdk
```

## Usage examples

All the APIs are designed to be easy to use. All request results are returned as dictionaries.

Every API method can be accessed via single RiseAPI object:

```python
from risesdk import RiseAPI

# In production you should use your own node, as there are no stability
# guarantees for the public wallet node at wallet.rise.vision
api = RiseAPI('https://wallet.rise.vision')

block_height = api.blocks.get_height()['height']
version = api.peers.version()['version']

print(block_height, version)
```

### Working with multiple nodes

In some cases you need to connect to multiple nodes.

```python
from risesdk import RiseAPI

api1 = RiseAPI('http://node1:5566')
api2 = RiseAPI('http://node2:5566')

version1 = api1.peers.version()
version2 = api2.peers.version()

print(version1, version2)
```

