CATEGORY_TECH = {
    "attributes": {"name": "Technology"},
    "id": "technology",
    "links": {"self": "https://api.up.com.au/api/v1/categories/technology"},
    "relationships": {
        "children": {
            "data": [],
            "links": {
                "related": "https://api.up.com.au/api/v1/categories?filter%5Bparent%5D=technology"
            },
        },
        "parent": {
            "data": {"id": "personal", "type": "categories"},
            "links": {"related": "https://api.up.com.au/api/v1/categories/personal"},
        },
    },
    "type": "categories",
}

CATEGORY_PERSONAL = {
    "attributes": {"name": "Personal"},
    "id": "personal",
    "links": {"self": "https://api.up.com.au/api/v1/categories/personal"},
    "relationships": {
        "children": {
            "data": [
                {"id": "life-admin", "type": "categories"},
                {"id": "mobile-phone", "type": "categories"},
                {"id": "news-magazines-and-books", "type": "categories"},
                {"id": "technology", "type": "categories"},
            ],
            "links": {
                "related": "https://api.up.com.au/api/v1/categories?filter%5Bparent%5D=personal"
            },
        },
        "parent": {"data": None},
    },
    "type": "categories",
}

CATEGORY_TECH_RESPONSE = {"data": CATEGORY_TECH}
CATEGORY_PERSONAL_RESPONSE = {"data": CATEGORY_PERSONAL}

CATEGORIES_RESPONSE = {"data": [CATEGORY_TECH, CATEGORY_PERSONAL]}
