from requests_mock import Mocker

from upbankapi import Client
from upbankapi.const import BASE_URL
from .testdata.accounts import ACCOUNT_ID, ACCOUNT_RESPONSE, ACCOUNTS_RESPONSE
from .testdata.categories import (
    CATEGORIES_RESPONSE,
    CATEGORY_PERSONAL_RESPONSE,
    CATEGORY_TECH_RESPONSE,
)
from .testdata.tags import TAGS_RESPONSE
from .testdata.transactions import (
    TRANSACTION_ID,
    TRANSACTION_RESPONSE,
    TRANSACTIONS_RESPONSE,
)


class TestClient:
    def test_account(self, requests_mock: Mocker):
        requests_mock.get(f"{BASE_URL}/accounts/{ACCOUNT_ID}", json=ACCOUNT_RESPONSE)
        client = Client()
        account = client.account(ACCOUNT_ID)
        assert account.id == ACCOUNT_ID

    def test_accounts(self, requests_mock: Mocker):
        requests_mock.get(f"{BASE_URL}/accounts", json=ACCOUNTS_RESPONSE)
        client = Client()
        accounts = client.accounts(limit=1)
        assert len(accounts) == 1
        assert accounts[0].id == ACCOUNT_ID

    def test_category(self, requests_mock: Mocker):
        requests_mock.get(
            f"{BASE_URL}/categories/technology", json=CATEGORY_TECH_RESPONSE
        )
        client = Client()
        category = client.category("technology")
        assert category.id == "technology"

    def test_category_correct(self, requests_mock: Mocker):
        requests_mock.get(
            f"{BASE_URL}/categories/personal", json=CATEGORY_PERSONAL_RESPONSE
        )
        client = Client()
        category = client.category("personal")
        assert category.id != "technology"

    def test_categories(self, requests_mock: Mocker):
        requests_mock.get(f"{BASE_URL}/categories", json=CATEGORIES_RESPONSE)
        client = Client()
        categories = client.categories()
        assert len(categories) == 2
        assert categories[0].id == "technology"
        assert categories[1].id == "personal"

    def test_tags(self, requests_mock: Mocker):
        requests_mock.get(f"{BASE_URL}/tags", json=TAGS_RESPONSE)
        client = Client()
        tags = client.tags()
        assert len(tags) == 2
        assert tags[0].id == "Holiday"
        assert tags[1].id == "Pizza Night"

    def test_transaction(self, requests_mock: Mocker):
        requests_mock.get(
            f"{BASE_URL}/transactions/{TRANSACTION_ID}", json=TRANSACTION_RESPONSE
        )
        client = Client()
        transaction = client.transaction(TRANSACTION_ID)
        assert transaction.id == TRANSACTION_ID

    def test_transactions(self, requests_mock: Mocker):
        requests_mock.get(f"{BASE_URL}/transactions", json=TRANSACTIONS_RESPONSE)
        client = Client()
        transactions = client.transactions()
        assert len(transactions) == 1
        assert transactions[0].id == TRANSACTION_ID
