# RISE Python SDK

Python library that provides APIs for interacting with the RISE blockchain.

## Getting started

The simplest way to get started is to use pip to install this library:

```
pip install risesdk
```

The Python APIs are (mostly) strongly typed to help your IDE help you write code faster.

Here's a very simple program that prints out the current height of the chain:

```python
from risesdk import Client

api = Client('https://wallet.rise.vision/api/')
status = api.blocks.get_status()
print('Chain height: {}'.format(status.height))
```

For more complete examples check out the [examples/](https://github.com/RiseVision/rise-py/tree/master/examples) directory.