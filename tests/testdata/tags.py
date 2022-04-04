TAG_HOLIDAY = {
    "type": "tags",
    "id": "Holiday",
    "relationships": {
        "transactions": {
            "links": {
                "related": "https://api.up.com.au/api/v1/transactions?filter%5Btag%5D=Holiday"
            }
        }
    },
}

TAG_PIZZA = {
    "type": "tags",
    "id": "Pizza Night",
    "relationships": {
        "transactions": {
            "links": {
                "related": "https://api.up.com.au/api/v1/transactions?filter%5Btag%5D=Pizza+Night"
            }
        }
    },
}

TAGS_RESPONSE = {
    "data": [TAG_HOLIDAY, TAG_PIZZA],
    "links": {
        "prev": None,
        "next": "https://api.up.com.au/api/v1/tags?page%5Bafter%5D=WyJQaXp6YSBOaWdodCJd&page%5Bsize%5D=2",
    },
}
