# Up Bank API
This is an unofficial python wrapper (client) for the australian bank up's API.

* 🕶️ [The Up Website](https://up.com.au)
* 📖 [Up API Documentation](https://developer.up.com.au)
* [Up API on Github](https://github.com/up-banking/api)

## Usage
The code is fully typed and documented so I'd recommend just having a look at the code, or letting syntax completion take the wheel. The files of interest are [models.py]() and [client.py]().

This is not yet a complete client and is missing some features, also up's API is still in beta so new features will likely still be added. You can track this libraries progress [here]().

To use this library you will need a personal access token which can be retrieved from https://developer.up.com.au. When using this library you can either provide the token directly or use the environment variable `UP_TOKEN`.

## Example

```python
from upbankapi import Client, NotAuthorizedException

client = Client()  # use environment variable

client = Client(token="MY_TOKEN")  # directly provide token

# check the token is valid
try:
    user_id = client.ping()
    print(f"Authorized ({user_id})")
except NotAuthorizedException:
    print("The token is invalid")

# get a list of all the users accounts
accounts = client.accounts()

for account in accounts:
    print(account)

    # get a list of transactions for this account
    for transaction in account.transactions():
        print(transaction)

# get the unique id of an account
print(accounts[0].id)

# get a specific account by its unique id
savings = client.account("7d7b081f-5ad3-4aeb-8494-15967b51be95")

print(savings)
print(f"${savings.balance}")

# get the last 5 transactions for a specific account
print(savings.transactions(limit=5))
# alternatively
print(client.transactions(account_id=savings.id, limit=5))

# get a specific transaction by its unique id
print(client.transaction("17c577f2-ae8e-4622-90a7-87d95094c2a9"))
```
