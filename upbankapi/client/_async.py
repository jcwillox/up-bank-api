from datetime import datetime
from typing import Dict, Optional, Union, Coroutine, Any, List

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
)
from ..models.accounts import AsyncAccount
from ..models.categories import AsyncTag, AsyncCategory
from ..models.common import RateLimit
from ..models.pagination import AsyncPaginatedList
from ..models.transactions import AsyncTransaction
from ..models.webhooks import AsyncWebhook, AsyncWebhookEvent, AsyncWebhookLog, Webhook

try:
    import aiohttp
except ImportError:
    raise ValueError(
        "aiohttp is not installed. Run `pip install up-bank-api[async]` to install it."
    )


class AsyncClient(ClientBase):
    """Asynchronous client for interacting with Up's API"""

    webhook: "AsyncWebhookAdapter"

    rate_limit: RateLimit
    """The information regarding the current rate limiting status."""

    def __init__(self, token: str = None, session: aiohttp.ClientSession = None):
        super().__init__(token)
        self.webhook = AsyncWebhookAdapter(self)
        """Property for accessing webhook methods."""

        if session:
            self._session = session
        else:
            self._session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()

    async def api(
        self,
        endpoint: str,
        method: str = "GET",
        body: Dict = None,
        params: Dict = None,
    ) -> Union[bool, Dict]:
        async with self._session.request(
            method=method,
            json=body,
            params=params,
            headers=self._headers,
            url=f"{BASE_URL}{endpoint}",
        ) as response:
            if response.status == 204:
                data = {}
            else:
                data = await response.json()
            return self._handle_response(data, response.status, dict(response.headers))

    async def ping(self) -> str:
        """Retrieves the users unique id and checks if the token is valid.

        Returns:
            The users unique id.

        Raises:
            NotAuthorizedException: If the token is invalid.
        """
        return (await self._handle_ping())["meta"]["id"]

    async def account(self, account_id: str) -> AsyncAccount:
        """Retrieve a single account by its unique account id.

        Arguments:
            account_id: The unique identifier for an account.

        Returns:
            The specified account.
        """
        return AsyncAccount(self, await self._handle_account(account_id))

    async def accounts(
        self,
        type: Optional[AccountType] = None,
        ownership_type: Optional[OwnershipType] = None,
        *,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncPaginatedList[AsyncAccount]:
        """Retrieves a list of the users accounts.

        Arguments:
            type: The type of account for which to return records.
            ownership_type: The account ownership structure for which to return records.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the accounts.
        """
        return AsyncPaginatedList(
            self,
            AsyncAccount,
            await self._handle_accounts(
                type, ownership_type, limit=limit, page_size=page_size
            ),
            limit,
        )

    async def category(self, category_id: str) -> AsyncCategory:
        """Retrieve a category by its unique category id.

        Arguments:
            category_id: The unique identifier for a category.

        Returns:
            The specified category.
        """
        return AsyncCategory(self, await self._handle_category(category_id))

    async def categories(
        self, parent: Union[str, PartialCategory] = None
    ) -> List[AsyncCategory]:
        """Retrieves a list of categories.

        Arguments:
            parent: The parent category/id to filter categories by.
                    Raises exception for invalid category.

        Returns:
            A list of the categories.
        """
        return [
            AsyncCategory(self, x)
            for x in (await self._handle_categories(parent))["data"]
        ]

    async def categorize(
        self,
        transaction: Union[str, Transaction],
        category: Optional[Union[str, PartialCategory]],
    ) -> bool:
        """Assign a category to a transaction.

        Arguments:
            transaction: The transaction/id to change the category on.
                         The transaction must be categorizable otherwise
                         a `ValueError` will be raised.
            category: The category to assign to the transaction.
                      Setting this to `None` will de-categorize the transaction.

        Returns:
            `True` if successful, otherwise raises exception.

        Raises:
            ValueError: If the transaction is not `categorizable`.
        """
        return await self._handle_categorize(transaction, category)

    async def tags(
        self, *, limit: int = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> AsyncPaginatedList[AsyncTag]:
        """Retrieves a list of the users tags.

        Arguments:
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the tags.
        """
        return AsyncPaginatedList(
            self,
            AsyncTag,
            await self._handle_tags(limit, page_size),
            limit,
        )

    async def add_tags(
        self, transaction: Union[str, Transaction], *tags: Union[str, Tag]
    ) -> bool:
        """Add tags to a given transaction.

        Arguments:
            transaction: The transaction/id to add tags on.
            *tags: The tags or tag ids to add to the transaction.

        Returns:
            `True` if successful, otherwise raises exception.
        """
        return await self._handle_add_tags(transaction, *tags)

    async def remove_tags(
        self, transaction: Union[str, Transaction], *tags: Union[str, Tag]
    ) -> bool:
        """Remove tags from a given transaction.

        Arguments:
            transaction: The transaction/id to remove tags on.
            *tags: The tags or tag ids to remove to the transaction.

        Returns:
            `True` if successful, otherwise raises exception.
        """
        return await self._handle_remove_tags(transaction, *tags)

    async def transaction(self, transaction_id: str) -> AsyncTransaction:
        """Retrieve a single transaction by its unique id.

        Arguments:
            transaction_id: The unique identifier for a transaction.

        Returns:
            The specified transaction.
        """
        return AsyncTransaction(self, await self._handle_transaction(transaction_id))

    async def transactions(
        self,
        account: Union[str, Account] = None,
        *,
        status: TransactionStatus = None,
        since: datetime = None,
        until: datetime = None,
        category: Union[str, PartialCategory] = None,
        tag: Union[str, Tag] = None,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncPaginatedList[AsyncTransaction]:
        """Retrieves transactions for a specific account or all accounts.

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

        Returns:
            A paginated list of the transactions.
        """
        return AsyncPaginatedList(
            self,
            AsyncTransaction,
            await self._handle_transactions(
                account, status, since, until, category, tag, limit, page_size
            ),
            limit,
        )

    async def webhooks(
        self, *, limit: int = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> AsyncPaginatedList[AsyncWebhook]:
        """Retrieves a list of the users webhooks.

        Arguments:
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the webhooks.
        """
        return AsyncPaginatedList(
            self,
            AsyncWebhook,
            await self._handle_webhooks(limit, page_size),
            limit,
        )


class AsyncWebhookAdapter(WebhookAdapterBase):
    _client: AsyncClient

    def __init__(self, client: AsyncClient):
        self._client = client

    def __call__(self, webhook_id: str) -> Coroutine[Any, Any, AsyncWebhook]:
        """Retrieve a single webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.

        Returns:
            The specified webhook.
        """
        return self.get(webhook_id)

    async def get(self, webhook_id: str) -> AsyncWebhook:
        """Retrieve a single webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.

        Returns:
            The specified webhook.
        """
        return AsyncWebhook(self._client, await self._handle_get(webhook_id))

    async def create(self, url: str, description: str = None) -> AsyncWebhook:
        """Registers and returns a new webhook.

        Arguments:
            url: The URL that this webhook should post events to.
            description: An optional description for this webhook, up to 64 characters in length.

        Returns:
            The newly created webhook.
        """
        return AsyncWebhook(self._client, await self._handle_create(url, description))

    async def ping(self, webhook: Union[str, Webhook]) -> AsyncWebhookEvent:
        """Pings a webhook by its unique id.

        Arguments:
            webhook: The webhook or webhook id to ping.

        Returns:
            The ping event response.
        """
        return AsyncWebhookEvent(self._client, await self._handle_ping(webhook))

    async def logs(
        self,
        webhook: Union[str, Webhook],
        *,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncPaginatedList[AsyncWebhookLog]:
        """Retrieves the logs from a webhook by id.

        Arguments:
            webhook: The webhook or webhook id to fetch logs from.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the webhook logs.
        """
        return AsyncPaginatedList(
            self._client,
            AsyncWebhookLog,
            await self._handle_logs(webhook, limit, page_size),
            limit,
        )

    async def delete(self, webhook: Union[str, Webhook]) -> bool:
        """Deletes a webhook by its unique id.

        Arguments:
            webhook: The webhook or webhook id to delete.

        Returns:
            `True` if successful, otherwise raises exception.
        """
        return await self._handle_delete(webhook)
