from datetime import datetime
from typing import Dict, Optional, Union, Coroutine, Any

from .base import ClientBase, WebhookAdapterBase
from ..const import BASE_URL, DEFAULT_PAGE_SIZE
from ..models import (
    Account,
    AccountType,
    OwnershipType,
    Transaction,
    TransactionStatus,
    PartialCategory,
    Tag,
    Webhook,
    WebhookEvent,
    WebhookLog,
)
from ..models.accounts import AsyncAccount
from ..models.pagination import AsyncPaginatedList

try:
    import aiohttp
except ImportError:
    raise ValueError(
        "aiohttp is not installed. Run `pip install up-bank-api[async]` to install it."
    )


class AsyncClient(ClientBase):
    """AsyncClient"""

    webhook: "AsyncWebhookAdapter"

    def __init__(self, token: str = None, session: aiohttp.ClientSession = None):
        super().__init__(token)
        self.webhook = AsyncWebhookAdapter(self)
        if session:
            self.session = session
        else:
            self.session = aiohttp.ClientSession()
        self.session.headers.update({"Authorization": f"Bearer {self._token}"})

    async def api(
        self,
        endpoint: str,
        method: str = "GET",
        body: Dict = None,
        params: Dict = None,
    ) -> Dict:
        async with self.session.request(
            method=method, json=body, params=params, url=f"{BASE_URL}{endpoint}"
        ) as response:
            return self._handle_response(await response.json(), response.status)

    async def ping(self) -> str:
        """Returns the users unique id and will raise an exception if the token is not valid."""
        return (await self._handle_ping())["meta"]["id"]

    async def account(self, account_id: str) -> Account:
        """Returns a single account by its unique account id.

        Arguments:
            account_id: The unique identifier for an account.
        """
        return Account(self, await self._handle_account(account_id))

    async def accounts(
        self,
        type: Optional[AccountType] = None,
        ownership_type: Optional[OwnershipType] = None,
        *,
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncPaginatedList[AsyncAccount]:
        """Returns a list of the users accounts.

        Arguments:
            type: The type of account for which to return records.
            ownership_type: The account ownership structure for which to return records.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)
        """
        return AsyncPaginatedList(
            self,
            AsyncAccount,
            await self._handle_accounts(
                type, ownership_type, limit=limit, page_size=page_size
            ),
            limit,
        )

    async def transaction(self, transaction_id: str) -> Transaction:
        """Returns a single transaction by its unique id.

        Arguments:
            transaction_id: The unique identifier for a transaction.
        """
        return Transaction(self, await self._handle_transaction(transaction_id))

    async def transactions(
        self,
        account: Union[str, Account] = None,
        *,
        status: TransactionStatus = None,
        since: datetime = None,
        until: datetime = None,
        category: Union[str, PartialCategory] = None,
        tag: Union[str, Tag] = None,
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncPaginatedList[Transaction]:
        """Returns transactions for a specific account or all accounts.

        Arguments:
            account: An account/id to fetch transactions from.
                     If `None`, returns transactions across all accounts.
            status: The transaction status for which to return records.
            since: The start `datetime` from which to return records.
            until: The end `datetime` up to which to return records.
            category: The category/id identifier for which to filter transactions.
                      Raises exception for invalid category.
            tag: A transaction tag/id to filter for which to return records.
                 Returns empty if tag does not exist.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)
        """
        return AsyncPaginatedList(
            self,
            Transaction,
            await self._handle_transactions(
                account, status, since, until, category, tag, limit, page_size
            ),
            limit,
        )

    async def webhooks(
        self, *, limit: Optional[int] = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> AsyncPaginatedList[Webhook]:
        """Returns a list of the users webhooks.

        Arguments:
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)
        """
        return AsyncPaginatedList(
            self,
            Webhook,
            await self._handle_webhooks(limit, page_size),
            limit,
        )


class AsyncWebhookAdapter(WebhookAdapterBase):
    _client: AsyncClient

    def __init__(self, client: AsyncClient):
        self._client = client

    def __call__(self, webhook_id: str) -> Coroutine[Any, Any, Webhook]:
        """Returns a single webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.
        """
        return self.get(webhook_id)

    async def get(self, webhook_id: str) -> Webhook:
        """Returns a single webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.
        """
        return Webhook(self._client, await self._handle_get(webhook_id))

    async def create(self, url: str, description: str = None) -> Webhook:
        """Registers and returns a new webhook.

        Arguments:
            url: The URL that this webhook should post events to.
            description: An optional description for this webhook, up to 64 characters in length.
        """
        return Webhook(self._client, await self._handle_create(url, description))

    async def ping(self, webhook_id: str) -> WebhookEvent:
        """Pings a webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.
        """
        return WebhookEvent(self._client, await self._handle_ping(webhook_id))

    async def logs(
        self,
        webhook_id: str,
        *,
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncPaginatedList[WebhookLog]:
        """Returns the logs from a webhook by id.

        Arguments:
            webhook_id: The unique identifier for a webhook.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)
        """
        return AsyncPaginatedList(
            self._client,
            WebhookLog,
            await self._handle_logs(webhook_id, limit, page_size),
            limit,
        )

    async def delete(self, webhook_id: str) -> Dict:
        """Deletes a webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.
        """
        return await self._handle_delete(webhook_id)