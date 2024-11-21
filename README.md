# Up Bank API

[![Project version](https://img.shields.io/pypi/v/up-bank-api?style=flat-square)](https://pypi.python.org/pypi/up-bank-api)
[![Supported python versions](https://img.shields.io/pypi/pyversions/up-bank-api?style=flat-square)](https://pypi.python.org/pypi/up-bank-api)
[![License](https://img.shields.io/github/license/jcwillox/up-bank-api?style=flat-square)](https://github.com/jcwillox/up-bank-api/blob/main/LICENSE)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/jcwillox/up-bank-api?style=flat-square)](https://www.codefactor.io/repository/github/jcwillox/up-bank-api)
[![Monthly Downloads](https://img.shields.io/pypi/dm/up-bank-api?style=flat-square)](https://pypistats.org/packages/up-bank-api)
[![Total Downloads](https://img.shields.io/pepy/dt/up-bank-api?style=flat-square)](https://pepy.tech/project/up-bank-api)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

This is an unofficial Python API wrapper for the Australian Bank [Up's](https://up.com.au/) API.

This package is fully typed, documented, and it has an intuitive structure, so I'd recommend just having quick look at the [docs](https://jcwillox.github.io/up-bank-api), and letting syntax completion take the wheel.

- 📚 [Package Documentation](https://jcwillox.github.io/up-bank-api)
- 🕶️ [The Up Website](https://up.com.au)
- 📖 [Up API Documentation](https://developer.up.com.au)
- 🔗 [Up API on GitHub](https://github.com/up-banking/api)

## Installation

```shell
pip install up-bank-api
```

To include async support

```shell
pip install up-bank-api[async]
```

## Usage

To use this library you will need a personal access token which can be retrieved from https://developer.up.com.au. When using this library you can either provide the token directly or use the environment variable `UP_TOKEN`.

**Synchronous Client**

```python
from upbankapi import Client, NotAuthorizedException

# implicitly use the environment variable UP_TOKEN
client = Client()

# or directly provide token
client = Client(token="MY_TOKEN")

# check the token is valid
try:
    user_id = client.ping()
    print(f"Authorized: {user_id}")
except NotAuthorizedException:
    print("The token is invalid")
```

**Asynchronous Client**

```python
import asyncio
from upbankapi import AsyncClient, NotAuthorizedException

async def main():
    # implicitly use the environment variable UP_TOKEN
    client = AsyncClient()

    # or directly provide token
    client = AsyncClient(token="MY_TOKEN")

    # use a context manager to automatically close the aiohttp session
    async with AsyncClient() as client:
        try:
            user_id = await client.ping()
            print(f"Authorized: {user_id}")
        except NotAuthorizedException:
            print("The token is invalid")

if __name__ == "__main__":
    asyncio.run(main())
```

See the [docs](https://jcwillox.github.io/up-bank-api) for more information, examples and code reference.
