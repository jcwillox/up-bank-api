from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Union

from .categories import PartialCategory, Tag
from .common import ModelBase
from .transactions import TransactionStatus
from ..const import DEFAULT_PAGE_SIZE


class AccountType(str, Enum):
    SAVER = "SAVER"
    TRANSACTIONAL = "TRANSACTIONAL"


class OwnershipType(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    JOINT = "JOINT"


class Account(ModelBase):
    """Representation of an Account."""

    id: str
    """The unique identifier for this account."""

    name: str
    """The name associated with the account in the Up application."""

    type: AccountType
    """The bank account type of this account."""

    ownership_type: OwnershipType
    """The ownership structure for this account."""

    balance: float
    """The available balance of the account, taking into account any amounts that are currently on hold."""

    balance_in_base_units: int
    """The amount of money in the smallest denomination for the currency."""

    currency: str
    """The ISO 4217 currency code."""

    created_at: datetime
    """The `datetime` at which this account was first opened."""

    def __parse__(self, attrs: Dict, relations: Dict, links: Optional[Dict]):
        self.name = attrs["displayName"]
        self.type = attrs["accountType"]
        self.ownership_type = attrs["ownershipType"]
        self.balance = float(attrs["balance"]["value"])
        self.balance_in_base_units = attrs["balance"]["valueInBaseUnits"]
        self.currency = attrs["balance"]["currencyCode"]
        self.created_at = datetime.fromisoformat(attrs["createdAt"])

    def transactions(
        self,
        *,
        status: TransactionStatus = None,
        since: datetime = None,
        until: datetime = None,
        category: Union[str, PartialCategory] = None,
        tag: Union[str, Tag] = None,
        limit: Optional[int] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ):
        """Returns transactions for this account.

        Arguments:
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
        return self._client.transactions(
            account=self,
            status=status,
            since=since,
            until=until,
            category=category,
            tag=tag,
            limit=limit,
            page_size=page_size,
        )

    def __repr__(self) -> str:
        """Return the representation of the account."""
        return f"<Account '{self.name}' ({self.type}): {self.balance} {self.currency}>"
