from datetime import datetime
from typing import Dict, Union, Optional

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
)
from ..models.pagination import PaginatedList


class Client(ClientBase):
    """Client"""

    webhook: "WebhookAdapter"

    def __init__(self, token: str = None, session: requests.Session = None):
        super().__init__(token)
        self.webhook = WebhookAdapter(self)
        if session:
            self.session = session
        else:
            self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self._token}"})

    def api(
        self,
        endpoint: str,
        method: str = "GET",
        body: Dict = None,
        params: Dict = None,
    ) -> Dict:
        response = self.session.request(
            method=method, json=body, params=params, url=f"{BASE_URL}{endpoint}"
        )
        return self._handle_response(response.json(), response.status_code)

    def ping(self) -> str:
        """Returns the users unique id and will raise an exception if the token is not valid."""
        return self._handle_ping()["meta"]["id"]

    def account(self, account_id: str) -> Account:
        """Returns a single account by its unique account id.

        Arguments:
            account_id: The unique identifier for an account.
        """
        return Account(self, self._handle_account(account_id))

    def accounts(
        self,
        type: Optional[AccountType] = None,
        ownership_type: Optional[OwnershipType] = None,
        *,
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedList[Account]:
        """Returns a list of the users accounts.

        Arguments:
            type: The type of account for which to return records.
            ownership_type: The account ownership structure for which to return records.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)
        """
        return PaginatedList(
            self,
            Account,
            self._handle_accounts(type, ownership_type, limit, page_size),
            limit,
        )

    def transaction(self, transaction_id: str) -> Transaction:
        """Returns a single transaction by its unique id.

        Arguments:
            transaction_id: The unique identifier for a transaction.
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
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedList[Transaction]:
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
        return PaginatedList(
            self,
            Transaction,
            self._handle_transactions(
                account, status, since, until, category, tag, limit, page_size
            ),
            limit,
        )

    def webhooks(
        self, *, limit: Optional[int] = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> PaginatedList[Webhook]:
        """Returns a list of the users webhooks.

        Arguments:
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)
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
        """Returns a single webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.
        """
        return self.get(webhook_id)

    def get(self, webhook_id: str) -> Webhook:
        """Returns a single webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.
        """
        return Webhook(self._client, self._handle_get(webhook_id))

    def create(self, url: str, description: str = None) -> Webhook:
        """Registers and returns a new webhook.

        Arguments:
            url: The URL that this webhook should post events to.
            description: An optional description for this webhook, up to 64 characters in length.
        """
        return Webhook(self._client, self._handle_create(url, description))

    def ping(self, webhook_id: str) -> WebhookEvent:
        """Pings a webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.
        """
        return WebhookEvent(self._client, self._handle_ping(webhook_id))

    def logs(
        self,
        webhook_id: str,
        *,
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedList[WebhookLog]:
        """Returns the logs from a webhook by id.

        Arguments:
            webhook_id: The unique identifier for a webhook.
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)
        """
        return PaginatedList(
            self._client,
            WebhookLog,
            self._handle_logs(webhook_id, limit, page_size),
            limit,
        )

    def delete(self, webhook_id: str) -> Dict:
        """Deletes a webhook by its unique id.

        Arguments:
            webhook_id: The unique identifier for a webhook.
        """
        return self._handle_delete(webhook_id)
