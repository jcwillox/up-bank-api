from datetime import datetime
from json import JSONDecodeError
from os import getenv
from typing import List, Dict

import requests

from .const import BASE_URL
from .exceptions import *
from .models import Account, Transaction


class Client:
    def __init__(self, token: str = None):
        self._token = token if token else getenv("UP_TOKEN")
        self._session = requests.Session()
        self._session.headers = {"Authorization": f"Bearer {token}"}

    def api(self, endpoint: str, method: str = "GET", params=None) -> Dict:
        """This method is used to directly interact the up bank api."""
        response = self._session.request(
            method=method, params=params, url=f"{BASE_URL}{endpoint}"
        )

        if response.status_code == 401:
            raise NotAuthorizedException()
        elif response.status_code == 429:
            raise RateLimitExceededException()

        try:
            data = response.json()
        except JSONDecodeError:
            raise BadResponseException()

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
        since: datetime = None,
        until: datetime = None,
        tag: str = None,
        account_id: str = None,
    ) -> List[Transaction]:
        """Returns transactions across all the users accounts."""
        params = {"page[size]": limit}
        if since:
            params["filter[since]"] = since.isoformat()
        if until:
            params["filter[until]"] = until.isoformat()
        if until:
            params["filter[tag]"] = tag

        endpoint = "/transactions"
        if account_id:
            endpoint = f"/accounts/{account_id}/transactions"

        transactions = self.api(endpoint, params=params)["data"]
        return [Transaction(transaction) for transaction in transactions]

    def transaction(self, transaction_id: str):
        """Returns a single transaction by its unique id."""
        return Transaction(self.api(f"/transactions/{transaction_id}")["data"])
