# Rise Python SDK

# Introduction

Rise meets Python

The Rise Python SDK is cross platform library based on Rise (https://rise.vision) and entirely rewritten in Python.

#### Third party dependencies
1. Requests


## Examples

All the APIs are designed to be easy to use. All request results returns as dictionaries.

For example you can open a new account by doing:

```python
from rise import RiseAPI

api = RiseAPI('http://127.0.0.1:5566')

result = api.accounts.open('secret')

if result['success']:
    print(result['account'])
else:
    print(result['error'])
```

Every API method can be accessed via single RiseAPI object:

```python
from rise import RiseAPI

api = RiseAPI('http://127.0.0.1:5566')

block_height = api.blocks.get_height()['height']
version = api.peers.version()['version']

print(block_height, version)
```

### Working with multiple nodes

In some cases you need to connect to multiple nodes.

```python
from rise import RiseAPI

api1 = RiseAPI('http://node1:5566')
api2 = RiseAPI('http://node2:5566')

version1 = api1.peers.version()
version2 = api2.peers.version()

print(version1, version2)
```

