from datetime import datetime
from os import getenv
from typing import Optional, Dict

import requests

from .list import PaginatedList
from .const import BASE_URL, DEFAULT_PAGE_SIZE, DEFAULT_LIMIT
from .exceptions import (
    NotAuthorizedException,
    RateLimitExceededException,
    UpBankException,
)
from .models import Account, Transaction, Webhook, WebhookLog, WebhookEvent


class Client:
    def __init__(self, token: str = None):
        self._token = token if token else getenv("UP_TOKEN")
        self._session = requests.Session()
        self._session.headers = {"Authorization": f"Bearer {self._token}"}
        self.webhook = WebhookAdapter(self)

    def api(
        self, endpoint: str, method: str = "GET", body: Dict = None, params=None
    ) -> Dict:
        """This method is used to directly interact the up bank api."""
        response = self._session.request(
            method=method, json=body, params=params, url=f"{BASE_URL}{endpoint}"
        )

        data = response.json()

        if response.status_code == 204:
            return {}

        if response.status_code >= 400:
            try:
                error = data["errors"][0]
            except ValueError:
                error = {}

            if response.status_code == 401:
                raise NotAuthorizedException(error)
            if response.status_code == 429:
                raise RateLimitExceededException(error)

            raise UpBankException(error)

        return data

    def ping(self) -> str:
        """Returns the users unique id and will raise an exception if the token is not valid."""
        return self.api("/util/ping")["meta"]["id"]

    def accounts(
        self,
        limit: Optional[int] = DEFAULT_LIMIT,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedList[Account]:
        """Returns a list of the users accounts.

        :param limit maximum number of records to return (set to None for all transactions)
        :param page_size number of records to fetch in each request (max 100)
        """
        if limit and limit < page_size:
            page_size = limit

        response = self.api("/accounts", params={"page[size]": page_size})
        elements = [Account(self, account) for account in response["data"]]
        return PaginatedList(self, Account, elements, response["links"]["next"], limit)

    def account(self, account_id: str) -> Account:
        """Returns a single account by its unique account id."""
        return Account(self, self.api(f"/accounts/{account_id}")["data"])

    def transactions(
        self,
        limit: Optional[int] = DEFAULT_LIMIT,
        page_size: int = DEFAULT_PAGE_SIZE,
        status: str = None,
        since: datetime = None,
        until: datetime = None,
        category: str = None,
        tag: str = None,
        account_id: str = None,
    ) -> PaginatedList[Transaction]:
        """Returns transactions for a specific account or all accounts.

        :param limit maximum number of records to return (set to None for all transactions)
        :param page_size number of records to fetch in each request (max 100)
        :param status:
        :param since:
        :param until:
        :param category:
        :param tag:
        :param account_id: optionally supply a unique id of the account to fetch transactions from
        """
        if limit and limit < page_size:
            page_size = limit

        params = {"page[size]": page_size}

        if status:
            params["filter[status]"] = status
        if since:
            params["filter[since]"] = since.astimezone().isoformat()
        if until:
            params["filter[until]"] = until.astimezone().isoformat()
        if category:
            params["filter[category]"] = category
        if tag:
            params["filter[tag]"] = tag

        endpoint = "/transactions"
        if account_id:
            endpoint = f"/accounts/{account_id}/transactions"

        response = self.api(endpoint, params=params)
        elements = [Transaction(self, transaction) for transaction in response["data"]]
        return PaginatedList(
            self, Transaction, elements, response["links"]["next"], limit
        )

    def transaction(self, transaction_id: str):
        """Returns a single transaction by its unique id."""
        return Transaction(self, self.api(f"/transactions/{transaction_id}")["data"])

    ### Webhooks ###
    def webhooks(
        self, limit: Optional[int] = DEFAULT_LIMIT, page_size: int = DEFAULT_PAGE_SIZE
    ) -> PaginatedList[Webhook]:
        """Returns a list of the users webhooks.

        :param limit maximum number of records to return (set to None for all transactions)
        :param page_size number of records to fetch in each request (max 100)
        """
        if limit and limit < page_size:
            page_size = limit

        response = self.api("/webhooks", params={"page[size]": page_size})
        elements = [Webhook(self, webhook) for webhook in response["data"]]
        return PaginatedList(self, Webhook, elements, response["links"]["next"], limit)


class WebhookAdapter:
    def __init__(self, client):
        self._client = client

    def __call__(self, webhook_id: str) -> Webhook:
        """Returns a single webhook by its unique id."""
        return self.get(webhook_id)

    def get(self, webhook_id: str) -> Webhook:
        """Returns a single webhook by its unique id."""
        return Webhook(
            self._client, self._client.api(f"/webhooks/{webhook_id}")["data"]
        )

    def create(self, url: str, description: str = None) -> Webhook:
        """Registers and returns a new webhook."""
        response = self._client.api(
            "/webhooks",
            method="POST",
            body={"data": {"attributes": {"url": url, "description": description}}},
        )
        return Webhook(self._client, response["data"])

    def ping(self, webhook_id: str) -> WebhookEvent:
        """Pings a webhook by its unique id."""
        return WebhookEvent(
            self._client,
            self._client.api(f"/webhooks/{webhook_id}/ping", method="POST")["data"],
        )

    def logs(
        self,
        webhook_id: str,
        limit: Optional[int] = DEFAULT_LIMIT,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedList[WebhookLog]:
        """Returns the logs from a webhook by id.

        :param webhook_id: unique id of a webhook
        :param limit maximum number of records to return (set to None for all transactions)
        :param page_size number of records to fetch in each request (max 100)
        """
        if limit and limit < page_size:
            page_size = limit

        response = self._client.api(
            f"/webhooks/{webhook_id}/logs", params={"page[size]": page_size}
        )
        elements = [WebhookLog(self._client, log) for log in response["data"]]
        return PaginatedList(
            self._client, WebhookLog, elements, response["links"]["next"], limit
        )

    def delete(self, webhook_id: str):
        """Deletes a webhook by its unique id."""
        return self._client.api(f"/webhooks/{webhook_id}", method="DELETE")
