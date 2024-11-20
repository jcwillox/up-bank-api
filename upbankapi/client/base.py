from abc import ABC, abstractmethod
from datetime import datetime
from os import getenv
from typing import Union, Dict, Coroutine, Any, Optional, List

from ..const import DEFAULT_PAGE_SIZE, RATE_LIMIT_HEADER
from ..exceptions import (
    NotAuthorizedException,
    RateLimitExceededException,
    UpBankException,
)
from ..models import (
    Account,
    Webhook,
    OwnershipType,
    AccountType,
    Transaction,
    TransactionStatus,
    Tag,
    PartialCategory,
    WebhookEvent,
    WebhookLog,
    Category,
)
from ..models.accounts import AsyncAccount
from ..models.categories import AsyncTag, AsyncCategory
from ..models.common import RateLimit
from ..models.pagination import PaginatedList, AsyncPaginatedList
from ..models.transactions import AsyncTransaction
from ..models.webhooks import AsyncWebhook, AsyncWebhookEvent, AsyncWebhookLog
from ..utils import Filters


class ClientBase(ABC):
    webhook: "WebhookAdapterBase"
    """Property for accessing webhook methods."""

    rate_limit: RateLimit
    """The information regarding the current rate limiting status."""

    def __init__(self, token: str = None):
        self._token: str = token if token else getenv("UP_TOKEN")
        self._headers = {"Authorization": f"Bearer {self._token}"}
        self.rate_limit = RateLimit()

    @abstractmethod
    def api(
        self, endpoint: str, method: str = "GET", body: Dict = None, params=None
    ) -> Union[bool, Dict, Coroutine[Any, Any, Union[bool, Dict]]]: ...

    def _handle_response(
        self, data: Dict, status: int, headers: Optional[Dict]
    ) -> Union[bool, Dict]:
        if headers and RATE_LIMIT_HEADER in headers:
            self.rate_limit.remaining = int(headers[RATE_LIMIT_HEADER])

        if status == 204:
            return True

        if status >= 400:
            try:
                error = data["errors"][0]
            except ValueError:
                error = {}

            if status == 401:
                raise NotAuthorizedException(error)
            if status == 429:
                raise RateLimitExceededException(error)

            raise UpBankException(error)
        return data

    @abstractmethod
    def ping(self) -> Union[str, Coroutine[Any, Any, str]]: ...

    def _handle_ping(self):
        return self.api("/util/ping")

    ### ACCOUNTS ###
    @abstractmethod
    def account(
        self, account_id: str
    ) -> Union[Account, Coroutine[Any, Any, AsyncAccount]]: ...

    def _handle_account(self, account_id: str):
        return self.api(f"/accounts/{account_id}")

    @abstractmethod
    def accounts(
        self,
        type: Optional[AccountType] = None,
        ownership_type: Optional[OwnershipType] = None,
        *,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Union[
        PaginatedList[Account], Coroutine[Any, Any, AsyncPaginatedList[AsyncAccount]]
    ]: ...

    def _handle_accounts(
        self,
        type: Optional[AccountType] = None,
        ownership_type: Optional[OwnershipType] = None,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ):
        return self.api(
            "/accounts",
            params=Filters(
                page_size,
                limit,
                {
                    "accountType": type,
                    "ownershipType": ownership_type,
                },
            ),
        )

    ### CATEGORIES ###
    @abstractmethod
    def category(
        self, category_id: str
    ) -> Union[Category, Coroutine[Any, Any, AsyncCategory]]: ...

    def _handle_category(self, category_id: str):
        return self.api(f"/categories/{category_id}")

    @abstractmethod
    def categories(
        self, parent: Union[str, PartialCategory]
    ) -> Union[List[Category], Coroutine[Any, Any, List[AsyncCategory]]]: ...

    def _handle_categories(self, parent: Union[str, PartialCategory]):
        filters = Filters()
        if parent:
            if isinstance(parent, str):
                filters.filter("parent", parent)
            else:
                filters.filter("parent", parent.id)
        return self.api("/categories", params=filters)

    @abstractmethod
    def categorize(
        self,
        transaction: Union[str, Transaction],
        category: Optional[Union[str, PartialCategory]],
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...

    def _handle_categorize(
        self,
        transaction: Union[str, Transaction],
        category: Optional[Union[str, PartialCategory]],
    ):
        if isinstance(transaction, Transaction):
            if not transaction.categorizable:
                raise ValueError("Transaction is not categorizable.")
            transaction = transaction.id

        body = {"data": None}
        if category:
            if isinstance(category, PartialCategory):
                category = category.id

            body["data"] = {"type": "categories", "id": category}

        return self.api(
            f"/transactions/{transaction}/relationships/category",
            method="PATCH",
            body=body,
        )

    ### TAGS ###
    @abstractmethod
    def tags(
        self, *, limit: int = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> Union[
        PaginatedList[Tag], Coroutine[Any, Any, AsyncPaginatedList[AsyncTag]]
    ]: ...

    def _handle_tags(self, limit: int = None, page_size: int = DEFAULT_PAGE_SIZE):
        return self.api("/tags", params=Filters(page_size, limit))

    @abstractmethod
    def add_tags(
        self, transaction: Union[str, Transaction], *tags: Union[str, Tag]
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...

    def _handle_add_tags(
        self, transaction: Union[str, Transaction], *tags: Union[str, Tag]
    ):
        return self._handle_add_remove_tags("POST", transaction, *tags)

    @abstractmethod
    def remove_tags(
        self, transaction: Union[str, Transaction], *tags: Union[str, Tag]
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...

    def _handle_remove_tags(
        self, transaction: Union[str, Transaction], *tags: Union[str, Tag]
    ):
        return self._handle_add_remove_tags("DELETE", transaction, *tags)

    def _handle_add_remove_tags(
        self, method: str, transaction: Union[str, Transaction], *tags: Union[str, Tag]
    ):
        if isinstance(transaction, Transaction):
            transaction = transaction.id

        body = []
        for tag in tags:
            if isinstance(tag, Tag):
                tag = tag.id
            body.append({"type": "tags", "id": tag})

        return self.api(
            f"/transactions/{transaction}/relationships/tags",
            method=method,
            body={"data": body},
        )

    ### TRANSACTIONS ###
    @abstractmethod
    def transaction(
        self, transaction_id: str
    ) -> Union[Transaction, Coroutine[Any, Any, AsyncTransaction]]: ...

    def _handle_transaction(self, transaction_id: str):
        return self.api(f"/transactions/{transaction_id}")

    @abstractmethod
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
    ) -> Union[
        PaginatedList[Transaction],
        Coroutine[Any, Any, AsyncPaginatedList[AsyncTransaction]],
    ]: ...

    def _handle_transactions(
        self,
        account: Union[str, Account] = None,
        status: TransactionStatus = None,
        since: datetime = None,
        until: datetime = None,
        category: Union[str, PartialCategory] = None,
        tag: Union[str, Tag] = None,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ):
        if tag and isinstance(tag, Tag):
            tag = tag.id

        if category and isinstance(category, PartialCategory):
            category = category.id

        if account:
            if isinstance(account, Account):
                account = account.id
            endpoint = f"/accounts/{account}/transactions"
        else:
            endpoint = "/transactions"

        return self.api(
            endpoint,
            params=Filters(
                page_size,
                limit,
                {
                    "status": status,
                    "since": since,
                    "until": until,
                    "tag": tag,
                    "category": category,
                },
            ),
        )

    ### WEBHOOKS ###
    @abstractmethod
    def webhooks(
        self, *, limit: int = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> Union[
        PaginatedList[Webhook], Coroutine[Any, Any, AsyncPaginatedList[AsyncWebhook]]
    ]: ...

    def _handle_webhooks(self, limit: int = None, page_size: int = DEFAULT_PAGE_SIZE):
        return self.api("/webhooks", params=Filters(page_size, limit))


class WebhookAdapterBase(ABC):
    _client: ClientBase

    @abstractmethod
    def __call__(
        self, webhook_id: str
    ) -> Union[Webhook, Coroutine[Any, Any, AsyncWebhook]]: ...

    @abstractmethod
    def get(
        self, webhook_id: str
    ) -> Union[Webhook, Coroutine[Any, Any, AsyncWebhook]]: ...

    def _handle_get(self, webhook_id: str):
        return self._client.api(f"/webhooks/{webhook_id}")

    @abstractmethod
    def create(
        self, url: str, description: str = None
    ) -> Union[Webhook, Coroutine[Any, Any, AsyncWebhook]]: ...

    def _handle_create(self, url: str, description: str = None):
        return self._client.api(
            "/webhooks",
            method="POST",
            body={"data": {"attributes": {"url": url, "description": description}}},
        )

    @abstractmethod
    def ping(
        self, webhook: Union[str, Webhook]
    ) -> Union[WebhookEvent, Coroutine[Any, Any, AsyncWebhookEvent]]: ...

    def _handle_ping(self, webhook: Union[str, Webhook]):
        if isinstance(webhook, Webhook):
            webhook = webhook.id
        return self._client.api(f"/webhooks/{webhook}/ping", method="POST")

    @abstractmethod
    def logs(
        self,
        webhook: Union[str, Webhook],
        *,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Union[
        PaginatedList[WebhookLog],
        Coroutine[Any, Any, AsyncPaginatedList[AsyncWebhookLog]],
    ]: ...

    def _handle_logs(
        self,
        webhook: Union[str, Webhook],
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ):
        if isinstance(webhook, Webhook):
            webhook = webhook.id
        return self._client.api(
            f"/webhooks/{webhook}/logs", params=Filters(page_size, limit)
        )

    @abstractmethod
    def delete(
        self, webhook: Union[str, Webhook]
    ) -> Union[bool, Coroutine[Any, Any, bool]]: ...

    def _handle_delete(self, webhook: Union[str, Webhook]):
        if isinstance(webhook, Webhook):
            webhook = webhook.id
        return self._client.api(f"/webhooks/{webhook}", method="DELETE")
