# Up Bank API

[![Project version](https://img.shields.io/pypi/v/up-bank-api?style=flat-square)](https://pypi.python.org/pypi/up-bank-api)
[![Supported python versions](https://img.shields.io/pypi/pyversions/up-bank-api?style=flat-square)](https://pypi.python.org/pypi/up-bank-api)
[![License](https://img.shields.io/github/license/jcwillox/up-bank-api?style=flat-square)](https://github.com/jcwillox/up-bank-api/blob/master/LICENSE)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is an unofficial python wrapper (client) for the australian bank Up's API.

- 🕶️ [The Up Website](https://up.com.au)
- 📖 [Up API Documentation](https://developer.up.com.au)
- [Up API on Github](https://github.com/up-banking/api)

## Installation

```shell
$ pip install up-bank-api
```

## Usage

The code is fully typed and documented so I'd recommend just having a look at the code, or letting syntax completion take the wheel. The files of interest are [models.py](https://github.com/jcwillox/up-bank-api/blob/master/upbankapi/models.py) and [client.py](https://github.com/jcwillox/up-bank-api/blob/master/upbankapi/client.py).

This is not yet a complete client and is missing some features, also Up's API is still in beta so new features will likely still be added. You can track this libraries progress [here](https://github.com/jcwillox/up-bank-api/issues/1).

To use this library you will need a personal access token which can be retrieved from https://developer.up.com.au. When using this library you can either provide the token directly or use the environment variable `UP_TOKEN`.

```python
from upbankapi import Client, NotAuthorizedException

# use the environment variable UP_TOKEN
client = Client()

# or directly provide token
client = Client(token="MY_TOKEN")  

# optionally check the token is valid
try:
    user_id = client.ping()
    print("Authorized: " + user_id)
except NotAuthorizedException:
    print("The token is invalid")
```

## Examples

* [Accounts](#accounts)
* [Transactions](#transactions)
* [Pagination](#pagination)
* [Webhooks](#webhooks)

### Accounts

```python
accounts = client.accounts()

# list accounts
for account in accounts:
    print(account)

    # list transactions for account
    for transaction in account.transactions():
        print(transaction)

>>> <Account 'Up Account' (TRANSACTIONAL): 1234.56 AUD>
>>> <Transaction SETTLED: -1.0 AUD [7-Eleven]>
>>> <Account '💰 Savings' (SAVER): 12345.67 AUD>
>>> <Transaction SETTLED: 10.0 AUD [Interest]>
```

```python
# get the unique id of an account
accounts[1].id
>>> "d7cd1152-e78a-4ad7-8202-d27cddb02a28"

# get a specific account by its unique id
savings = client.account("d7cd1152-e78a-4ad7-8202-d27cddb02a28")
savings
>>> <Account '💰 Savings' (SAVER): 12345.67 AUD>
savings.balance
>>> 12345.67
```

### Transactions

Get transactions across all accounts.
```python
>>> list( client.transactions() )
[<Transaction SETTLED: -1.0 AUD [7-Eleven]>, <Transaction SETTLED: 10.0 AUD [Interest]>]
```
Get last 5 transactions for a given account id.
```python
SAVINGS_ID = "d7cd1152-e78a-4ad7-8202-d27cddb02a28"

list( client.account(SAVINGS_ID).transactions(limit=5) )
>>> [<Transaction SETTLED: 10.0 AUD [Interest]>]

list( client.transactions(account_id=SAVINGS_ID, limit=5) )
>>> [<Transaction SETTLED: 10.0 AUD [Interest]>]
```
Get a specific transaction.
```python
client.transaction("17c577f2-ae8e-4622-90a7-87d95094c2a9")
>>> <Transaction SETTLED: -1.0 AUD [7-Eleven]>
```

### Pagination

Up's API uses pagination, this means methods in this library that return more than one record will return a `PaginatedList`. This is effectively just an iterator. 
Every `page_size` records the instance of `PaginatedList` will make a request for the next `page_size` records.

A `limit` can be used to limit the maximum number of records returned, when a limit is specified the iterator will never return more than `limit` but can return less.
Using `limit=None` will return all records.
```python
transactions = client.transactions(limit=5)

for transaction in transactions:
    print(transactions)

print(transactions)
>>> <upbankapi.PaginatedList.PaginatedList object at 0x05BCE670>

print(list( transactions ))
>>> [<Transaction SETTLED: -1.0 AUD [7-Eleven]>, <Transaction SETTLED: 10.0 AUD [Interest]>]
```
`PaginatedList` supports **slicing**, it still returns an iterator and will fetch the records as required.

```python
transactions = client.transactions(limit=20)
list( transactions[10:20] )
>>> [<Transaction ...>, ...]
```
> Note that while it may appear the slice `[:limit]` has the same effect as specifying a `limit`, it does not, when you specify a limit the code optimises the page size. 
> For example, using the slice `[:5]` will fetch the first 20 records and return only 5, using `limit=5` it will fetch and return the first 5 records. However, if you manually specify `page_size=5` then both options have the safe effect.

### Webhooks

List users webhooks
```python
list( client.webhooks() )
>>> [<Webhook '1c3a4fd4-6c57-4aa8-8481-cf31a46bc001': https://mywebhook.tld/c2f89ed40e26c936 (Hello World!)>]
```

Get a specific webhook
```python
client.webhook("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001")
# or equivalently
client.webhook.get("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001")
>>> <Webhook '1c3a4fd4-6c57-4aa8-8481-cf31a46bc001': https://mywebhook.tld/c2f89ed40e26c936 (Hello World!)>
```

Create a webhook
```python
client.webhook.create("https://mywebhook.tld/c2f89ed40e26c936", description="Hello World!")
>>> <Webhook '1c3a4fd4-6c57-4aa8-8481-cf31a46bc001': https://mywebhook.tld/c2f89ed40e26c936 (Hello World!)>
```

Interacting with a webhook
```python
webhook = client.webhook("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001")

# ping the webhook
webhook.ping()
>>> <WebhookEvent PING: webhook_id='1c3a4fd4-6c57-4aa8-8481-cf31a46bc001'>

# get the webhooks logs
list( webhook.logs() )
>>> [<WebhookLog BAD_RESPONSE_CODE: response_code=404>]

# get the event associated with a log entry
webhook.logs()[0].event
>>> <WebhookEvent PING: webhook_id='1c3a4fd4-6c57-4aa8-8481-cf31a46bc001'>

# delete the webhook
webhook.delete()
```

When interacting with with a specific webhook there are two options.

For example the two code blocks below have the same result (deleting the webhook), however the first option uses 2 requests and the second option uses only 1 request.
This is because option 1 will request the webhook details, and then send the delete request. Option 2 directly sends the delete request.
```python
# Option 1
client.webhook("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001").delete()
```
```python
# Option 2
client.webhook.delete("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001")
```
Each option can be useful depending on the use case. Option 2 is primarily useful when do not already have the Webhook object but have the id and only want to perform a single action.