ACCOUNT_ID = "7b3121f9-40f3-4230-bdd7-6709e68426fb"

ACCOUNT = {
    "type": "accounts",
    "id": ACCOUNT_ID,
    "attributes": {
        "displayName": "Spending",
        "accountType": "TRANSACTIONAL",
        "ownershipType": "INDIVIDUAL",
        "balance": {
            "currencyCode": "AUD",
            "value": "1.00",
            "valueInBaseUnits": 100,
        },
        "createdAt": "2022-03-22T10:12:05+11:00",
    },
    "relationships": {
        "transactions": {
            "links": {
                "related": "https://api.up.com.au/api/v1/accounts/7b3121f9-40f3-4230-bdd7-6709e68426fb/transactions"
            }
        }
    },
    "links": {
        "self": "https://api.up.com.au/api/v1/accounts/7b3121f9-40f3-4230-bdd7-6709e68426fb"
    },
}

ACCOUNT_RESPONSE = {
    "data": ACCOUNT,
}

ACCOUNTS_RESPONSE = {
    "data": [ACCOUNT],
    "links": {
        "prev": None,
        "next": "https://api.up.com.au/api/v1/accounts?page%5Bafter%5D=WyIyMDIyLTAzLTIxVDIzOjEyOjA1LjUyMzg1MjAwMFoiLCI3YjMxMjFmOS00MGYzLTQyMzAtYmRkNy02NzA5ZTY4NDI2ZmIiXQ%3D%3D&page%5Bsize%5D=1",
    },
}
