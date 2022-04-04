from abc import ABC, abstractmethod
from datetime import datetime
from os import getenv
from typing import Union, Dict, Coroutine, Any, Optional, List

from ..const import DEFAULT_PAGE_SIZE
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
from ..models.pagination import PaginatedList, AsyncPaginatedList
from ..utils import Filters


class ClientBase(ABC):
    webhook: "WebhookAdapterBase"

    def __init__(self, token: str = None):
        self._token = token if token else getenv("UP_TOKEN")

    @abstractmethod
    def api(
        self, endpoint: str, method: str = "GET", body: Dict = None, params=None
    ) -> Union[bool, Dict, Coroutine[Any, Any, Union[bool, Dict]]]:
        ...

    @staticmethod
    def _handle_response(data: Dict, status: int) -> Union[bool, Dict]:
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
    def ping(self) -> Union[str, Coroutine[Any, Any, str]]:
        ...

    def _handle_ping(self):
        return self.api("/util/ping")

    ### ACCOUNTS ###
    @abstractmethod
    def account(self, account_id: str) -> Union[Account, Coroutine[Any, Any, Account]]:
        ...

    def _handle_account(self, account_id: str):
        return self.api(f"/accounts/{account_id}")

    @abstractmethod
    def accounts(
        self,
        type: Optional[AccountType] = None,
        ownership_type: Optional[OwnershipType] = None,
        *,
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Union[
        PaginatedList[Account], Coroutine[Any, Any, AsyncPaginatedList[Account]]
    ]:
        ...

    def _handle_accounts(
        self,
        type: Optional[AccountType] = None,
        ownership_type: Optional[OwnershipType] = None,
        limit: Optional[int] = None,
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
    ) -> Union[Category, Coroutine[Any, Any, Category]]:
        ...

    def _handle_category(self, category_id: str):
        return self.api(f"/categories/{category_id}")

    @abstractmethod
    def categories(
        self, parent: Union[str, PartialCategory]
    ) -> Union[List[Category], Coroutine[Any, Any, Category]]:
        ...

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
    ) -> Union[bool, Coroutine[Any, Any, bool]]:
        ...

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
        self, *, limit: Optional[int] = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> Union[PaginatedList[Tag], Coroutine[Any, Any, AsyncPaginatedList[Tag]]]:
        ...

    def _handle_tags(
        self, limit: Optional[int] = None, page_size: int = DEFAULT_PAGE_SIZE
    ):
        return self.api("/tags", params=Filters(page_size, limit))

    @abstractmethod
    def add_tags(
        self, transaction: Union[str, Transaction], *tags: Tag
    ) -> Union[bool, Coroutine[Any, Any, bool]]:
        ...

    def _handle_add_tags(
        self, transaction: Union[str, Transaction], *tags: Union[str, Tag]
    ):
        return self._handle_add_remove_tags("POST", transaction, *tags)

    @abstractmethod
    def remove_tags(
        self, transaction: Union[str, Transaction], *tags: Union[str, Tag]
    ) -> Union[bool, Coroutine[Any, Any, bool]]:
        ...

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
    ) -> Union[Transaction, Coroutine[Any, Any, Transaction]]:
        ...

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
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Union[
        PaginatedList[Transaction], Coroutine[Any, Any, AsyncPaginatedList[Transaction]]
    ]:
        ...

    def _handle_transactions(
        self,
        account: Union[str, Account] = None,
        status: TransactionStatus = None,
        since: datetime = None,
        until: datetime = None,
        category: Union[str, PartialCategory] = None,
        tag: Union[str, Tag] = None,
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ):
        filters = Filters(
            page_size,
            limit,
            {"status": status, "since": since, "until": until, "tag": tag},
        )

        if category:
            if isinstance(category, str):
                filters.filter("category", category)
            else:
                filters.filter("category", category.id)

        endpoint = "/transactions"
        if account:
            if isinstance(account, Account):
                account = account.id
            endpoint = f"/accounts/{account}/transactions"
        return self.api(endpoint, params=filters)

    ### WEBHOOKS ###
    @abstractmethod
    def webhooks(
        self, *, limit: Optional[int] = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> Union[
        PaginatedList[Webhook], Coroutine[Any, Any, AsyncPaginatedList[Webhook]]
    ]:
        ...

    def _handle_webhooks(
        self, limit: Optional[int] = None, page_size: int = DEFAULT_PAGE_SIZE
    ):
        return self.api("/webhooks", params=Filters(page_size, limit))


class WebhookAdapterBase(ABC):
    _client: ClientBase

    @abstractmethod
    def __call__(self, webhook_id: str) -> Union[Webhook, Coroutine[Any, Any, Webhook]]:
        ...

    @abstractmethod
    def get(self, webhook_id: str) -> Union[Webhook, Coroutine[Any, Any, Webhook]]:
        ...

    def _handle_get(self, webhook_id: str):
        return self._client.api(f"/webhooks/{webhook_id}")

    @abstractmethod
    def create(
        self, url: str, description: str = None
    ) -> Union[Webhook, Coroutine[Any, Any, Webhook]]:
        ...

    def _handle_create(self, url: str, description: str = None):
        return self._client.api(
            "/webhooks",
            method="POST",
            body={"data": {"attributes": {"url": url, "description": description}}},
        )

    @abstractmethod
    def ping(
        self, webhook_id: str
    ) -> Union[WebhookEvent, Coroutine[Any, Any, WebhookEvent]]:
        ...

    def _handle_ping(self, webhook_id: str):
        return self._client.api(f"/webhooks/{webhook_id}/ping", method="POST")

    @abstractmethod
    def logs(
        self,
        webhook_id: str,
        *,
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Union[
        PaginatedList[WebhookLog], Coroutine[Any, Any, AsyncPaginatedList[WebhookLog]]
    ]:
        ...

    def _handle_logs(
        self,
        webhook_id: str,
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ):
        return self._client.api(
            f"/webhooks/{webhook_id}/logs", params=Filters(page_size, limit)
        )

    @abstractmethod
    def delete(self, webhook_id: str) -> Union[bool, Coroutine[Any, Any, bool]]:
        ...

    def _handle_delete(self, webhook_id: str):
        return self._client.api(f"/webhooks/{webhook_id}", method="DELETE")
