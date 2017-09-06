# Rise Python SDK

# Introduction

Rise meets Python

The Rise Python SDK is cross platform library based on Rise (https://rise.vision) and entirely rewritten in Python. Check the github wiki for the full documentation. (https://github.com/RiseVision/Rise-SDK-Python/wiki)

#### Third party dependencies
1. Requests

## Installation instructions

The easiest way to install the Rise Python SDK is using pip.

    pip install risesdk

(https://pypi.python.org/pypi?:action=display&name=risesdk)

## Example

Basic example of usage.

```python
from rise import RiseAPI

api = RiseAPI('http://127.0.0.1:5566')

api.blocks.get_height()
```

