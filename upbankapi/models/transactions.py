from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List

from .categories import Tag, PartialCategoryParent
from .common import ModelBase, MoneyObject


class TransactionStatus(str, Enum):
    HELD = "HELD"
    SETTLED = "SETTLED"


class HoldInfo:
    """Representation of the HoldInfo object returned by a `Transaction`."""

    def __init__(self, data: Dict):
        self.amount: MoneyObject = MoneyObject(data["amount"])
        """The amount of this transaction while in the `HELD` status, in Australian dollars."""

        self.foreign_amount: Optional[MoneyObject] = None
        """The foreign currency amount of this transaction while in the `HELD` status.

        This field will be `None` for domestic transactions.
        """

        if data["foreignAmount"]:
            self.foreign_amount = MoneyObject(data["foreignAmount"])


class RoundUp:
    """Representation of the RoundUp object returned by a `Transaction`."""

    def __init__(self, data: Dict):
        self.amount: MoneyObject = MoneyObject(data["amount"])
        """The total amount of this Round Up, including any boosts, represented as a negative value."""

        self.boost_portion: Optional[MoneyObject] = None
        """The portion of the Round Up amount owing to boosted Round Ups, represented as a negative value.

        If no boost was added to the Round Up this field will be `None`.
        """

        if data["boostPortion"]:
            self.boost_portion = MoneyObject(data["boostPortion"])


class Cashback:
    """Representation of the Cashback object returned by a `Transaction`."""

    def __init__(self, data: Dict):
        self.amount: MoneyObject = MoneyObject(data["amount"])
        """The total amount of cashback paid, represented as a positive value."""

        self.description: str = data["description"]
        """A brief description of why this cashback was paid."""


class Transaction(ModelBase):
    """Representation of a Transaction."""

    id: str
    """The unique identifier for this transaction."""

    status: TransactionStatus
    """The current processing status of this transaction."""

    raw_text: Optional[str]
    """The original, unprocessed text of the transaction."""

    description: str
    """A short description for this transaction. Usually the merchant name for purchases."""

    message: Optional[str]
    """Attached message for this transaction, such as a payment message, or a transfer note."""

    hold_info: Optional[HoldInfo]
    """The amount and foreign_amount of this transaction while it was/is in the HELD state."""

    round_up: Optional[RoundUp]
    """Details of how this transaction was rounded-up.

    If no Round Up was applied this field will be null.
    """

    cashback: Optional[Cashback]
    """Provides details of the reimbursement if all or part of 
    this transaction was instantly reimbursed in the form of cashback.
    """

    amount: float
    """The amount of this transaction in Australian dollars.

    For transactions that were once `HELD` but are now `SETTLED`, refer to the
    `hold_info` field for the original amount the transaction was `HELD` at.
    """

    amount_in_base_units: int
    """The amount of money in the smallest denomination for the currency."""

    currency: str
    """The ISO 4217 currency code."""

    foreign_amount: Optional[MoneyObject]
    """The foreign currency amount of this transaction.

    This field will be `None` for domestic transactions.
    """

    settled_at: Optional[datetime]
    """The `datetime` at which this transaction settled.

    This field will be `None` for transactions that are currently in the `HELD` status.
    """

    created_at: datetime
    """The `datetime` at which this transaction was first encountered."""

    category: Optional[PartialCategoryParent]
    """The category assigned to this transaction."""

    tags: List[Tag]
    """The list of tags assigned to this transaction."""

    def __parse__(self, attrs: Dict, relations: Dict, links: Optional[Dict]):
        self.status = attrs["status"]
        self.raw_text = attrs["rawText"]
        self.description = attrs["description"]
        self.message = attrs["message"]

        if attrs["holdInfo"]:
            self.hold_info = HoldInfo(attrs["holdInfo"])

        if attrs["roundUp"]:
            self.round_up = RoundUp(attrs["roundUp"])

        if attrs["cashback"]:
            self.cashback = Cashback(attrs["cashback"])

        self.amount = float(attrs["amount"]["value"])
        self.amount_in_base_units = attrs["amount"]["valueInBaseUnits"]
        self.currency = attrs["amount"]["currencyCode"]

        if attrs["foreignAmount"]:
            self.foreign_amount = MoneyObject(attrs["foreignAmount"])

        if attrs["settledAt"]:
            self.settled_at = datetime.fromisoformat(attrs["settledAt"])
        self.created_at = datetime.fromisoformat(attrs["createdAt"])

        if relations["category"]["data"]:
            self.category = PartialCategoryParent(
                self._client,
                {
                    "id": relations["category"]["data"]["id"],
                    "relationships": {"parent": relations["parentCategory"]},
                },
            )

        self.tags = [Tag(self._client, x) for x in relations["tags"]["data"]]

    @property
    def pending(self) -> bool:
        """Returns true when the transaction is pending."""
        return self.status != TransactionStatus.SETTLED

    @property
    def long_description(self) -> str:
        """Returns a longer description using the description and message properties."""
        if self.message:
            return f"{self.description}: {self.message}"
        return self.description

    def __repr__(self) -> str:
        """Return the representation of the transaction."""
        return f"<Transaction {self.status}: {self.amount} {self.currency} [{self.description}]>"
