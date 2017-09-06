# Rise Python SDK

# Introduction

Rise meets Python

The Rise Python SDK is cross platform library based on Rise (https://rise.vision) and entirely rewritten in Python.

#### Third party dependencies
1. Requests


## Example

Basic example of usage.

```python
from rise import RiseAPI

api = RiseAPI('http://127.0.0.1:5566')

api.blocks.get_height()
```

