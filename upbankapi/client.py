from datetime import datetime
from json import JSONDecodeError
from os import getenv
from typing import List, Dict

import requests

from .const import BASE_URL
from .exceptions import *
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
            elif response.status_code == 429:
                raise RateLimitExceededException(error)

            raise UpBankException(error)

        return data

    def ping(self) -> str:
        """Returns the users unique id and will raise an exception if the token is not valid."""
        return self.api("/util/ping")["meta"]["id"]

    def accounts(self, limit: int = 20) -> List[Account]:
        """Returns a list of the users accounts."""
        accounts = self.api("/accounts", params={"page[size]": limit})["data"]
        return [Account(self, account) for account in accounts]

    def account(self, account_id: str) -> Account:
        """Returns a single account by its unique account id."""
        return Account(self, self.api(f"/accounts/{account_id}")["data"])

    def transactions(
        self,
        limit: int = 20,
        status: str = None,
        since: datetime = None,
        until: datetime = None,
        category: str = None,
        tag: str = None,
        account_id: str = None,
    ) -> List[Transaction]:
        """Returns transactions across all the users accounts."""
        params = {"page[size]": limit}
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

        transactions = self.api(endpoint, params=params)["data"]
        return [Transaction(transaction) for transaction in transactions]

    def transaction(self, transaction_id: str):
        """Returns a single transaction by its unique id."""
        return Transaction(self.api(f"/transactions/{transaction_id}")["data"])

    ### Webhooks ###
    def webhooks(self, limit: int = 20) -> List[Webhook]:
        """Returns a list of the users webhooks."""
        webhooks = self.api("/webhooks", params={"page[size]": limit})["data"]
        return [Webhook(self, webhook) for webhook in webhooks]


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

    def logs(self, webhook_id: str, limit: int = 20):
        """Returns the logs from a webhook by its unique id."""
        logs = self._client.api(
            f"/webhooks/{webhook_id}/logs", params={"page[size]": limit}
        )["data"]
        return [WebhookLog(self._client, log) for log in logs]

    def delete(self, webhook_id: str):
        """Deletes a webhook by its unique id."""
        return self._client.api(f"/webhooks/{webhook_id}", method="DELETE")
