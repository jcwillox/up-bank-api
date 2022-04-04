TRANSACTION_ID = "34642cf9-7017-41b4-ac52-98f955d5fe48"

TRANSACTION = {
    "type": "transactions",
    "id": "34642cf9-7017-41b4-ac52-98f955d5fe48",
    "attributes": {
        "status": "HELD",
        "rawText": "Spotify 0123456789",
        "description": "Spotify",
        "message": None,
        "isCategorizable": True,
        "holdInfo": {
            "amount": {
                "currencyCode": "AUD",
                "value": "-11.95",
                "valueInBaseUnits": -1195,
            },
            "foreignAmount": None,
        },
        "roundUp": None,
        "cashback": None,
        "amount": {
            "currencyCode": "AUD",
            "value": "-11.95",
            "valueInBaseUnits": -1195,
        },
        "foreignAmount": None,
        "cardPurchaseMethod": None,
        "settledAt": None,
        "createdAt": "2022-03-19T06:03:29+11:00",
    },
    "relationships": {
        "account": {
            "data": {
                "type": "accounts",
                "id": "d7967cba-0894-47f8-bbbc-c152b0d9e46f",
            },
            "links": {
                "related": "https://api.up.com.au/api/v1/accounts/d7967cba-0894-47f8-bbbc-c152b0d9e46f"
            },
        },
        "transferAccount": {"data": None},
        "category": {
            "data": {"type": "categories", "id": "tv-and-music"},
            "links": {
                "self": "https://api.up.com.au/api/v1/transactions/34642cf9-7017-41b4-ac52-98f955d5fe48/relationships/category",
                "related": "https://api.up.com.au/api/v1/categories/tv-and-music",
            },
        },
        "parentCategory": {
            "data": {"type": "categories", "id": "good-life"},
            "links": {"related": "https://api.up.com.au/api/v1/categories/good-life"},
        },
        "tags": {
            "data": [],
            "links": {
                "self": "https://api.up.com.au/api/v1/transactions/34642cf9-7017-41b4-ac52-98f955d5fe48/relationships/tags"
            },
        },
    },
    "links": {
        "self": "https://api.up.com.au/api/v1/transactions/34642cf9-7017-41b4-ac52-98f955d5fe48"
    },
}


TRANSACTION_RESPONSE = {
    "data": TRANSACTION,
}

TRANSACTIONS_RESPONSE = {
    "data": [TRANSACTION],
    "links": {
        "prev": None,
        "next": None,
    },
}
