from datetime import datetime
from typing import Dict, Union, Optional, List

import requests

from .base import ClientBase, WebhookAdapterBase
from ..const import BASE_URL, DEFAULT_PAGE_SIZE
from ..models import (
    AccountType,
    OwnershipType,
    Account,
    Transaction,
    TransactionStatus,
    PartialCategory,
    Tag,
    Webhook,
    WebhookEvent,
    WebhookLog,
    Category,
)
from ..models.pagination import PaginatedList


class Client(ClientBase):
    """Synchronous client for interacting with Up's API"""

    webhook: "WebhookAdapter"

    def __init__(self, token: str = None, session: requests.Session = None):
        super().__init__(token)
        self.webhook = WebhookAdapter(self)
        """Property for accessing webhook methods."""

        if session:
            self._session = session
        else:
            self._session = requests.Session()

    def api(
        self,
        endpoint: str,
        method: str = "GET",
        body: Dict = None,
        params: Dict = None,
    ) -> Union[bool, Dict]:
        response = self._session.request(
            method=method,
            json=body,
            params=params,
            headers=self._headers,
            url=f"{BASE_URL}{endpoint}",
        )
        return self._handle_response(response.json(), response.status_code)

    def ping(self) -> str:
        """Retrieves the users unique id and checks if the token is valid.

        Returns:
            The users unique id.

        Raises:
            NotAuthorizedException: If the token is invalid.
        """
        return self._handle_ping()["meta"]["id"]

    def account(self, account_id: str) -> Account:
        """Retrieve a single account by its unique account id.

        Arguments:
            account_id: The unique identifier for an account.

        Returns:
            The specified account.
        """
        return Account(self, self._handle_account(account_id))

    def accounts(
        self,
        type: Optional[AccountType] = None,
        ownership_type: Optional[OwnershipType] = None,
        *,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedList[Account]:
        """Retrieves a list of the users accounts.

        Arguments:
            type: The type of account for which to return records.
            ownership_type: The account ownership structure for which to return records.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the accounts.
        """
        return PaginatedList(
            self,
            Account,
            self._handle_accounts(type, ownership_type, limit, page_size),
            limit,
        )

    def category(self, category_id: str) -> Category:
        """Retrieve a category by its unique category id.

        Arguments:
            category_id: The unique identifier for a category.

        Returns:
            The specified category.
        """
        return Category(self, self._handle_category(category_id))

    def categories(self, parent: Union[str, PartialCategory] = None) -> List[Category]:
        """Retrieves a list of categories.

        Arguments:
            parent: The parent category/id to filter categories by.
                    Raises exception for invalid category.

        Returns:
            A list of the categories.
        """
        return [Category(self, x) for x in self._handle_categories(parent)["data"]]

    def categorize(
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
        return self._handle_categorize(transaction, category)

    def tags(
        self, *, limit: int = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> PaginatedList[Tag]:
        """Retrieves a list of the users tags.

        Arguments:
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the tags.
        """
        return PaginatedList(
            self,
            Tag,
            self._handle_tags(limit, page_size),
            limit,
        )

    def add_tags(self, transaction: Union[str, Transaction], *tags: Tag) -> bool:
        """Add tags to a given transaction.

        Arguments:
            transaction: The transaction/id to add tags on.
            *tags: The tags or tag ids to add to the transaction.

        Returns:
            `True` if successful, otherwise raises exception.
        """
        return self._handle_add_tags(transaction, *tags)

    def remove_tags(
        self, transaction: Union[str, Transaction], *tags: Union[str, Tag]
    ) -> bool:
        """Remove tags from a given transaction.

        Arguments:
            transaction: The transaction/id to remove tags on.
            *tags: The tags or tag ids to remove to the transaction.

        Returns:
            `True` if successful, otherwise raises exception.
        """
        return self._handle_remove_tags(transaction, *tags)

    def transaction(self, transaction_id: str) -> Transaction:
        """Retrieve a single transaction by its unique id.

        Arguments:
            transaction_id: The unique identifier for a transaction.

        Returns:
            The specified transaction.
        """
        return Transaction(self, self._handle_transaction(transaction_id))

    def transactions(
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
    ) -> PaginatedList[Transaction]:
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
        return PaginatedList(
            self,
            Transaction,
            self._handle_transactions(
                account, status, since, until, category, tag, limit, page_size
            ),
            limit,
        )

    def webhooks(
        self, *, limit: int = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> PaginatedList[Webhook]:
        """Retrieves a list of the users webhooks.

        Arguments:
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the webhooks.
        """
        return PaginatedList(
            self,
            Webhook,
            self._handle_webhooks(limit, page_size),
            limit,
        )


class WebhookAdapter(WebhookAdapterBase):
    _client: Client

    def __init__(self, client: Client):
        self._client = client

    def __call__(self, webhook_id: str) -> Webhook:
        """Retrieve a single webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.

        Returns:
            The specified webhook.
        """
        return self.get(webhook_id)

    def get(self, webhook_id: str) -> Webhook:
        """Retrieve a single webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.

        Returns:
            The specified webhook.
        """
        return Webhook(self._client, self._handle_get(webhook_id))

    def create(self, url: str, description: str = None) -> Webhook:
        """Registers and returns a new webhook.

        Arguments:
            url: The URL that this webhook should post events to.
            description: An optional description for this webhook, up to 64 characters in length.

        Returns:
            The newly created webhook.
        """
        return Webhook(self._client, self._handle_create(url, description))

    def ping(self, webhook: Union[str, Webhook]) -> WebhookEvent:
        """Pings a webhook by its unique id.

        Arguments:
            webhook: The webhook or webhook id to ping.

        Returns:
            The ping event response.
        """
        return WebhookEvent(self._client, self._handle_ping(webhook))

    def logs(
        self,
        webhook: Union[str, Webhook],
        *,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedList[WebhookLog]:
        """Retrieves the logs from a webhook by id.

        Arguments:
            webhook: The webhook or webhook id to fetch logs from.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the webhook logs.
        """
        return PaginatedList(
            self._client,
            WebhookLog,
            self._handle_logs(webhook, limit, page_size),
            limit,
        )

    def delete(self, webhook: Union[str, Webhook]) -> bool:
        """Deletes a webhook by its unique id.

        Arguments:
            webhook: The webhook or webhook id to delete.

        Returns:
            `True` if successful, otherwise raises exception.
        """
        return self._handle_delete(webhook)
