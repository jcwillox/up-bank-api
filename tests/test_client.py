import pytest

from upbankapi import Client, AsyncClient

USER_ID = "66bac1cf-8dd0-4f77-ae9d-5a296f7402e3"
ACCOUNT_ID = "6e0361ab-2b54-57cb-abf4-fcb638040566"
TRANSACTION_ID = "34642cf9-7017-41b4-ac52-98f955d5fe48"


@pytest.fixture
def client():
    return Client()


@pytest.fixture
async def aclient():
    async with AsyncClient() as client:
        yield client


class TestClient:
    @pytest.mark.default_cassette("test_ping.yaml")
    @pytest.mark.vcr()
    def test_ping(self, client: Client):
        assert client.ping() == USER_ID

    @pytest.mark.default_cassette("test_account.yaml")
    @pytest.mark.vcr()
    def test_account(self, client: Client):
        account = client.account(ACCOUNT_ID)
        assert account.id == ACCOUNT_ID

    @pytest.mark.default_cassette("test_accounts.yaml")
    @pytest.mark.vcr()
    def test_accounts(self, client: Client):
        accounts = client.accounts(limit=1)
        assert len(accounts) == 1
        assert accounts[0].id == ACCOUNT_ID

    @pytest.mark.default_cassette("test_category_technology.yaml")
    @pytest.mark.vcr()
    def test_category(self, client: Client):
        category = client.category("technology")
        assert category.id == "technology"

    @pytest.mark.default_cassette("test_category_personal.yaml")
    @pytest.mark.vcr()
    def test_category_correct(self, client: Client):
        category = client.category("personal")
        assert category.id != "technology"

    @pytest.mark.default_cassette("test_categories.yaml")
    @pytest.mark.vcr()
    def test_categories(self, client: Client):
        categories = client.categories()[:2]
        assert len(categories) == 2
        assert categories[0].id == "games-and-software"
        assert categories[1].id == "car-insurance-and-maintenance"

    @pytest.mark.default_cassette("test_tags.yaml")
    @pytest.mark.vcr()
    def test_tags(self, client: Client):
        tags = client.tags()
        assert len(tags) == 2
        assert tags[0].id == "Holiday"
        assert tags[1].id == "Pizza Night"

    @pytest.mark.default_cassette("test_transaction.yaml")
    @pytest.mark.vcr()
    def test_transaction(self, client: Client):
        transaction = client.transaction(TRANSACTION_ID)
        assert transaction.id == TRANSACTION_ID

    @pytest.mark.default_cassette("test_transactions.yaml")
    @pytest.mark.vcr()
    def test_transactions(self, client: Client):
        transactions = client.transactions()
        assert len(transactions) == 1
        assert transactions[0].id == TRANSACTION_ID


class TestAsyncClient:
    @pytest.mark.default_cassette("test_ping.yaml")
    @pytest.mark.vcr()
    async def test_ping(self, aclient):
        assert await aclient.ping() == USER_ID

    @pytest.mark.default_cassette("test_account.yaml")
    @pytest.mark.vcr()
    async def test_account(self, aclient):
        account = await aclient.account(ACCOUNT_ID)
        assert account.id == ACCOUNT_ID

    @pytest.mark.default_cassette("test_accounts.yaml")
    @pytest.mark.vcr()
    async def test_accounts(self, aclient):
        accounts = await aclient.accounts(limit=1)
        assert len(accounts) == 1
        assert (await accounts[0]).id == ACCOUNT_ID

    @pytest.mark.default_cassette("test_category_technology.yaml")
    @pytest.mark.vcr()
    async def test_category(self, aclient):
        category = await aclient.category("technology")
        assert category.id == "technology"

    @pytest.mark.default_cassette("test_category_personal.yaml")
    @pytest.mark.vcr()
    async def test_category_correct(self, aclient):
        category = await aclient.category("personal")
        assert category.id != "technology"

    @pytest.mark.default_cassette("test_categories.yaml")
    @pytest.mark.vcr()
    async def test_categories(self, aclient):
        categories = (await aclient.categories())[:2]
        assert len(categories) == 2
        assert categories[0].id == "games-and-software"
        assert categories[1].id == "car-insurance-and-maintenance"

    @pytest.mark.default_cassette("test_tags.yaml")
    @pytest.mark.vcr()
    async def test_tags(self, aclient):
        tags = await aclient.tags()
        assert len(tags) == 2
        assert (await tags[0]).id == "Holiday"
        assert (await tags[1]).id == "Pizza Night"

    @pytest.mark.default_cassette("test_transaction.yaml")
    @pytest.mark.vcr()
    async def test_transaction(self, aclient):
        transaction = await aclient.transaction(TRANSACTION_ID)
        assert transaction.id == TRANSACTION_ID

    @pytest.mark.default_cassette("test_transactions.yaml")
    @pytest.mark.vcr()
    async def test_transactions(self, aclient):
        transactions = await aclient.transactions()
        assert len(transactions) == 1
        assert (await transactions[0]).id == TRANSACTION_ID
