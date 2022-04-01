from abc import ABC, abstractmethod
from datetime import datetime
from os import getenv
from typing import Union, Dict, Coroutine, Any, Optional

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
    ) -> Union[Dict, Coroutine[Any, Any, Dict]]:
        ...

    @staticmethod
    def _handle_response(data: Dict, status: int) -> Dict:
        if status == 204:
            return {}

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

    @abstractmethod
    def account(self, account_id: str) -> Account:
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
    ) -> PaginatedList[Account]:
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

    @abstractmethod
    def transaction(self, transaction_id: str) -> Transaction:
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

    @abstractmethod
    def webhooks(
        self, *, limit: Optional[int] = None, page_size: int = DEFAULT_PAGE_SIZE
    ) -> PaginatedList[Webhook]:
        ...

    def _handle_webhooks(
        self, limit: Optional[int] = None, page_size: int = DEFAULT_PAGE_SIZE
    ):
        return self.api("/webhooks", params=Filters(page_size, limit))


class WebhookAdapterBase(ABC):
    _client: ClientBase

    @abstractmethod
    def __call__(self, webhook_id: str) -> Webhook:
        ...

    @abstractmethod
    def get(self, webhook_id: str) -> Webhook:
        ...

    def _handle_get(self, webhook_id: str):
        return self._client.api(f"/webhooks/{webhook_id}")

    @abstractmethod
    def create(self, url: str, description: str = None) -> Webhook:
        ...

    def _handle_create(self, url: str, description: str = None):
        return self._client.api(
            "/webhooks",
            method="POST",
            body={"data": {"attributes": {"url": url, "description": description}}},
        )

    @abstractmethod
    def ping(self, webhook_id: str) -> WebhookEvent:
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
    ) -> PaginatedList[WebhookLog]:
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
    def delete(self, webhook_id: str) -> Dict:
        ...

    def _handle_delete(self, webhook_id: str):
        return self._client.api(f"/webhooks/{webhook_id}", method="DELETE")
