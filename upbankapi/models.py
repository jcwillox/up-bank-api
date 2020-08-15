from datetime import datetime
from typing import Optional, Dict, List

from .const import TRANSACTION_SETTLED


class Transaction:
    """Representation of a transaction

    id: the unique id of the transaction
    status: either "HELD" or "SETTLED"
    pending: whether the transaction has been settled
    raw_text:
    description: typically the merchant/account
    message: typically the message/description
    settled_at:
    created_at:
    amount:
    currency:
    raw: the raw serialised data from the api
    """

    def __init__(self, data):
        self.raw: Dict = data
        self.id: str = data["id"]

        attributes = data["attributes"]

        self.status: str = attributes["status"]
        self.pending: bool = self.status != TRANSACTION_SETTLED
        self.raw_text: Optional[str] = attributes["rawText"]
        self.description: str = attributes["description"]
        self.message: Optional[str] = attributes["message"]
        self.settled_at: Optional[datetime] = datetime.fromisoformat(
            attributes["settledAt"]
        ) if attributes["settledAt"] else None
        self.created_at: datetime = datetime.fromisoformat(attributes["createdAt"])
        self.amount: float = float(attributes["amount"]["value"])
        self.currency: str = attributes["amount"]["currencyCode"]

    def format_desc(self):
        """Returns a formatted description using the transactions description and message."""
        if self.message:
            return f"{self.description}: {self.message}"
        return f"{self.description}"

    def __repr__(self) -> str:
        """Return the representation of the transaction."""
        return f"<Transaction ({self.status}): {self.amount} ({self.currency}) [{self.description}]>"


class Account:
    """Representation of a transaction

    id: the unique id of the account
    type: either "TRANSACTIONAL" or "SAVER"
    name: the name of the account
    balance: amount of available funds
    currency:
    created_at: date and time the account was created
    raw: the raw serialised data from the api
    """

    def __init__(self, client, data: Dict):
        self._client = client
        self.raw: Dict = data
        self.id: str = data["id"]

        attributes = data["attributes"]

        self.name: str = attributes["displayName"]
        self.type: str = attributes["accountType"]
        self.created_at: datetime = datetime.fromisoformat(attributes["createdAt"])
        self.balance: float = float(attributes["balance"]["value"])
        self.currency: str = attributes["balance"]["currencyCode"]

    def transactions(
        self,
        limit: int = 20,
        since: datetime = None,
        until: datetime = None,
        tag: str = None,
    ) -> List[Transaction]:
        """Returns the transactions for this account."""
        return self._client.transactions(
            limit=limit, since=since, until=until, tag=tag, account_id=self.id
        )

    def __repr__(self) -> str:
        """Return the representation of the account."""
        return (
            f"<Account '{self.name}' ({self.type}): {self.balance} ({self.currency})>"
        )
