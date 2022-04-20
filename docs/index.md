# Usage

This is an unofficial Python API wrapper for the Australian Bank [Up's](https://up.com.au/) API.

## Installation

=== "Base"

    ```shell
    pip install up-bank-api
    ```

=== "Async Support"

    ```shell
    pip install up-bank-api[async]
    ```

## Setup

To use this library you will need a personal access token which can be retrieved from [https://developer.up.com.au](https://developer.up.com.au). When using this library you can either provide the token directly or use the environment variable `UP_TOKEN`.

=== "Sync"

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

=== "Async"

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

=== "Async Session"

    ```python
    import asyncio
    import aiohttp
    from upbankapi import AsyncClient, NotAuthorizedException

    async def main():
        # use a context manager to automatically close the aiohttp session
        async with aiohttp.ClientSession() as session:
            # implicitly use the environment variable UP_TOKEN
            client = AsyncClient(session=session)

            # or directly provide token
            client = AsyncClient(token="MY_TOKEN", session=session)

            try:
                user_id = await client.ping()
                print(f"Authorized: {user_id}")
            except NotAuthorizedException:
                print("The token is invalid")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

We will assume top-level await is possible for the following examples.

## Account

=== "Sync"

    ```python
    from upbankapi import Client

    client = Client()
    accounts = client.accounts()

    # get the unique id of an account
    print(accounts[1].id)

    # get a specific account by its unique id
    account = client.account("d7cd1152-e78a-4ad7-8202-d27cddb02a28")

    print(account)
    print(account.balance)
    ```

=== "Async"

    ```python
    from upbankapi import AsyncClient

    client = AsyncClient()
    accounts = await client.accounts()

    # get the unique id of an account
    # this is an async paginated list so we must use `await` to get an item
    # as it may need to make a request to fetch additional content.
    print((await accounts[1]).id)

    # get a specific account by its unique id
    account = await client.account("d7cd1152-e78a-4ad7-8202-d27cddb02a28")

    print(account)
    print(account.balance)
    ```

```python
>>> "d7cd1152-e78a-4ad7-8202-d27cddb02a28"
>>> <Account '💰 Savings' (SAVER): 12345.67 AUD>
>>> 12345.67
```

## Accounts

=== "Sync"

    ```python title="Print all accounts and their transactions"
    from upbankapi import Client, NotAuthorizedException

    client = Client()
    accounts = client.accounts()

    # list accounts
    for account in accounts:
        print(account)

        # list transactions for account
        for transaction in account.transactions(limit=10):
            print(transaction)
    ```

    ```python
    >>> <Account 'Up Account' (TRANSACTIONAL): 1234.56 AUD>
    >>> <Transaction SETTLED: -1.0 AUD [7-Eleven]>
    >>> <Account '💰 Savings' (SAVER): 12345.67 AUD>
    >>> <Transaction SETTLED: 10.0 AUD [Interest]>
    ```

=== "Async"

    ```python title="Print all accounts and their transactions"
    from upbankapi import AsyncClient, NotAuthorizedException

    client = AsyncClient()
    accounts = await client.accounts()

    # list accounts
    async for account in accounts:
        print(account)

        # list transactions for account
        async for transaction in await account.transactions(limit=10):
            print(transaction)
    ```

    ```python
    >>> <Account 'Up Account' (TRANSACTIONAL): 1234.56 AUD>
    >>> <Transaction SETTLED: -1.0 AUD [7-Eleven]>
    >>> <Account '💰 Savings' (SAVER): 12345.67 AUD>
    >>> <Transaction SETTLED: 10.0 AUD [Interest]>
    ```

## Transaction

=== "Sync"

    ```python
    from upbankapi import Client

    client = Client()

    # get a specific transaction by its unique id
    transaction = client.transaction("17c577f2-ae8e-4622-90a7-87d95094c2a9")

    print(transaction)
    print(transaction.category)

    # the API only gives us a partial category for the transaction, so we can 
    # resolve the full category information using `.category()`. This will
    # return itself if it's already a full category object.
    print(transaction.category.category())

    # we don't need to resolve the full category to use it, for example,
    # we can fetch all transactions from the parent category of the transaction.
    transactions = transaction.category.parent.transactions(limit=10)

    print(list(transactions))
    ```

    ```python
    >>> <Transaction SETTLED: -1.0 AUD [7-Eleven]>
    >>> <PartialCategoryParent id='takeaway' parent='good-life'>

    >>> <Category 'Takeaway': id='takeaway' parent='good-life'>

    >>> [<Transaction SETTLED: -1.0 AUD [7-Eleven]>]
    ```

=== "Async"

    ```python
    from upbankapi import AsyncClient

    client = AsyncClient()

    # get a specific transaction by its unique id
    transaction = await client.transaction("17c577f2-ae8e-4622-90a7-87d95094c2a9")

    print(transaction)
    print(transaction.category)

    # the API only gives us a partial category for the transaction, so we can 
    # resolve the full category information using `.category()`. This will
    # return itself if it's already a full category object.
    print(await transaction.category.category())

    # we don't need to resolve the full category to use it, for example,
    # we can fetch all transactions from the parent category of the transaction.
    transactions = await transaction.category.parent.transactions(limit=10)

    print([x async for x in transactions])
    ```

    ```python
    >>> <Transaction SETTLED: -1.0 AUD [7-Eleven]>
    >>> <PartialCategoryParent id='takeaway' parent='good-life'>

    >>> <Category 'Takeaway': id='takeaway' parent='good-life'>

    >>> [<Transaction SETTLED: -1.0 AUD [7-Eleven]>]
    ```

## Transactions

=== "Sync"

    ```python title="Get all transactions for all accounts"
    print(list(client.transactions()))

    >>> [<Transaction SETTLED: -1.0 AUD [7-Eleven]>, <Transaction SETTLED: 10.0 AUD [Interest]>]
    ```

=== "Async"

    ```python title="Get all transactions for all accounts"
    print([x async for x in await client.transactions()])

    >>> [<Transaction SETTLED: -1.0 AUD [7-Eleven]>, <Transaction SETTLED: 10.0 AUD [Interest]>]
    ```

<span></span>

=== "Sync"

    ```python title="Get last 5 transactions for a given account"
    SAVINGS_ID = "d7cd1152-e78a-4ad7-8202-d27cddb02a28"

    print(client.account(SAVINGS_ID).transactions(limit=5))

    # alternative which avoids making an extra request for the account details
    print(client.transactions(SAVINGS_ID, limit=5))

    # using an account object
    account = client.account(SAVINGS_ID)
    print(client.transactions(account, limit=5))

    >>> [<Transaction SETTLED: 10.0 AUD [Interest]>]
    ```

=== "Async"

    ```python title="Get last 5 transactions for a given account"
    SAVINGS_ID = "d7cd1152-e78a-4ad7-8202-d27cddb02a28"

    print(await (await client.account(SAVINGS_ID)).transactions(limit=5))

    # alternative which avoids making an extra request for the account details
    print(await client.transactions(SAVINGS_ID, limit=5))

    # using an account object
    account = await client.account(SAVINGS_ID)
    print(await client.transactions(account, limit=5))

    >>> [<Transaction SETTLED: 10.0 AUD [Interest]>]
    ```

## Webhooks

=== "Sync"

    ```python title="List users webhooks"
    print(list(client.webhooks()))

    >>> [<Webhook '1c3a4fd4-6c57-4aa8-8481-cf31a46bc001': https://mywebhook.tld/c2f89ed40e26c936 (Hello World!)>]
    ```

    ```python title="Get a specific webhook"
    print(client.webhook("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001"))
    # or equivalently
    print(client.webhook.get("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001"))

    >>> <Webhook '1c3a4fd4-6c57-4aa8-8481-cf31a46bc001': https://mywebhook.tld/c2f89ed40e26c936 (Hello World!)>
    ```

    ```python title="Create a webhook"
    print(
        client.webhook.create(
            "https://mywebhook.tld/c2f89ed40e26c936", description="Hello World!"
        )
    )

    >>> <Webhook '1c3a4fd4-6c57-4aa8-8481-cf31a46bc001': https://mywebhook.tld/c2f89ed40e26c936 (Hello World!)>
    ```

    ```python title="Interacting with a webhook"
    webhook = client.webhook("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001")

    # ping the webhook
    print(webhook.ping())
    >>> <WebhookEvent PING: webhook_id='1c3a4fd4-6c57-4aa8-8481-cf31a46bc001'>

    # get the webhooks logs
    print(list(webhook.logs()))
    >>> [<WebhookLog BAD_RESPONSE_CODE: response_code=404>]

    # get the event associated with a log entry
    print(webhook.logs()[0].event)
    >>> <WebhookEvent PING: webhook_id='1c3a4fd4-6c57-4aa8-8481-cf31a46bc001'>

    # delete the webhook, raises exception on failure, `True` on success.
    print(webhook.delete())
    >>> True
    ```

=== "Async"

    ```python title="List users webhooks"
    print([x async for x in await client.webhooks()])

    >>> [<Webhook '1c3a4fd4-6c57-4aa8-8481-cf31a46bc001': https://mywebhook.tld/c2f89ed40e26c936 (Hello World!)>]
    ```

    ```python title="Get a specific webhook"
    print(await client.webhook("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001"))
    # or equivalently
    print(await client.webhook.get("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001"))

    >>> <Webhook '1c3a4fd4-6c57-4aa8-8481-cf31a46bc001': https://mywebhook.tld/c2f89ed40e26c936 (Hello World!)>
    ```

    ```python title="Create a webhook"
    print(
        await client.webhook.create(
            "https://mywebhook.tld/c2f89ed40e26c936", description="Hello World!"
        )
    )

    >>> <Webhook '1c3a4fd4-6c57-4aa8-8481-cf31a46bc001': https://mywebhook.tld/c2f89ed40e26c936 (Hello World!)>
    ```

    ```python title="Interacting with a webhook"
    webhook = await client.webhook("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001")

    # ping the webhook
    print(await webhook.ping())
    >>> <WebhookEvent PING: webhook_id='1c3a4fd4-6c57-4aa8-8481-cf31a46bc001'>

    # get the webhooks logs
    print([x async for x in await webhook.logs()])
    >>> [<WebhookLog BAD_RESPONSE_CODE: response_code=404>]

    # get the event associated with a log entry
    logs = await webhook.logs()
    print((await logs[0]).event)
    >>> <WebhookEvent PING: webhook_id='1c3a4fd4-6c57-4aa8-8481-cf31a46bc001'>

    # delete the webhook, raises exception on failure, `True` on success.
    print(await webhook.delete())
    >>> True
    ```

When interacting with a specific webhook there are two options.

For example the two code blocks below have the same result (deleting the webhook), however, the first option uses 2 requests and the second option uses only 1 request. This is because option 1 will request the webhook details, and then send the delete request. Option 2 directly sends the delete request.

```python title="Option 1"
client.webhook("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001").delete()
```

```python title="Option 2"
client.webhook.delete("1c3a4fd4-6c57-4aa8-8481-cf31a46bc001")
```

Each option can be useful depending on the use case. Option 2 is primarily useful when you do not already have the Webhook object but have the id and only want to perform a single action.

## Pagination

Up's API uses pagination, this means methods in this library that return more than one record will return a `PaginatedList`. This is effectively just an iterator.
Every `page_size` records the instance of `PaginatedList` will make a request for the next `page_size` records.

A `limit` can be used to limit the maximum number of records returned, when a limit is specified the iterator will never return more than `limit` but can return less.
The default is no limit, so it will return all records.

=== "Sync"

    ```python
    from upbankapi import Client

    client = Client()

    transactions = client.transactions(limit=5)

    print(transactions)

    print(len(transactions))

    print(list(transactions))
    ```

=== "Async"

    ```python
    from upbankapi import AsyncClient

    client = AsyncClient()

    transactions = await client.transactions(limit=5)

    print(transactions)

    print(len(transactions))

    print([x async for x in transactions])
    ```

```python
>>> <upbankapi.models.pagination.AsyncPaginatedList object at 0x00000256206D5720>
>>> 2
>>> [<Transaction SETTLED: -1.0 AUD [7-Eleven]>, <Transaction SETTLED: 10.0 AUD [Interest]>]
```

`PaginatedList` supports **slicing**, it still returns an iterator and will fetch the records as required.

=== "Sync"

    ```python
    from upbankapi import Client

    client = Client()

    transactions = client.transactions(limit=20)

    print(list(transactions[10:20]))
    ```

=== "Async"

    ```python
    from upbankapi import AsyncClient

    client = AsyncClient()

    transactions = await client.transactions(limit=20)

    print([x async for x in transactions[10:20]])
    ```

```python
>>> [<Transaction ...>, ...]
```

???+ important

    While it may appear the slice `[:limit]` has the same effect as providing the `limit` argument, it does not, when you specify a limit the code optimises the page size.
    For example, using the slice `[:5]` will fetch the first 20 records and return only 5, using `limit=5` it will fetch and return the only first 5 records. Alternatively, if you manually specify `page_size=5` then both options have the same effect.


## Rate Limiting

Up's API is rate limited, and a `RateLimitExceededException` will be raised if you exceed this. After making a request to the API the number of remaining requests will be available through `#!python client.rate_limit.remaining`. The limit appears to be `1000 requests/h`.

It's recommended that if you are iterating over transactions at you use a `limit` or `slice` to avoid fetching all transactions.

Additionally, when fetching a large number of transactions, you should increase the `page_size` option to reduce the number of individual requests made.
