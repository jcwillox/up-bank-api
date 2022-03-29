from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List

from .categories import Tag, PartialCategoryParent
from .common import ModelBase, MoneyObject


class TransactionStatus(str, Enum):
    HELD = "HELD"
    SETTLED = "SETTLED"


class HoldInfo:
    # The amount of this transaction while in the HELD status, in Australian dollars.
    amount: MoneyObject

    # The foreign currency amount of this transaction while in the HELD status.
    # This field will be `None` for domestic transactions.
    foreign_amount: Optional[MoneyObject]

    def __init__(self, data: Dict):
        self.amount = MoneyObject(data["amount"])
        if data["foreignAmount"]:
            self.foreign_amount = MoneyObject(data["foreignAmount"])


class RoundUp:
    # The total amount of this Round Up, including any boosts, represented as a negative value.
    amount: MoneyObject

    # The portion of the Round Up amount owing to boosted Round Ups, represented as a negative value.
    # If no boost was added to the Round Up this field will be `None`.
    boost_portion: Optional[MoneyObject]

    def __init__(self, data: Dict):
        self.amount = MoneyObject(data["amount"])
        if data["boostPortion"]:
            self.boost_portion = MoneyObject(data["boostPortion"])


class Cashback:
    # A brief description of why this cashback was paid.
    description: str

    # The total amount of cashback paid, represented as a positive value.
    amount: MoneyObject

    def __init__(self, data: Dict):
        self.amount = MoneyObject(data["amount"])
        self.description = data["description"]


class Transaction(ModelBase):
    """Representation of a Transaction"""

    # The unique identifier for this transaction.
    id: str

    # The current processing status of this transaction.
    status: TransactionStatus

    # The original, unprocessed text of the transaction.
    raw_text: Optional[str]

    # A short description for this transaction. Usually the merchant name for purchases.
    description: str

    # Attached message for this transaction, such as a payment message, or a transfer note.
    message: Optional[str]

    # The amount and foreign_amount of this transaction while it was/is in the HELD state.
    hold_info: Optional[HoldInfo]

    # Details of how this transaction was rounded-up.
    # If no Round Up was applied this field will be null.
    round_up: Optional[RoundUp]

    # Provides details of the reimbursement, if all or part of this
    # transaction was instantly reimbursed in the form of cashback.
    cashback: Optional[Cashback]

    # The amount of this transaction in Australian dollars.
    # For transactions that were once HELD but are now SETTLED, refer to the
    # `hold_info` field for the original amount the transaction was HELD at.
    amount: float

    # The amount of money in the smallest denomination for the currency.
    amount_in_base_units: int

    # The ISO 4217 currency code.
    currency: str

    # The foreign currency amount of this transaction.
    # This field will be `None` for domestic transactions.
    foreign_amount: Optional[MoneyObject]

    # The date-time at which this transaction settled. This field will be `None`
    # for transactions that are currently in the HELD status.
    settled_at: Optional[datetime]

    # The date-time at which this transaction was first encountered.
    created_at: datetime

    # The category assigned to this transaction.
    category: Optional[PartialCategoryParent]

    # The list of tags assigned to this transaction.
    tags: List[Tag]

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

        self.foreign_amount = MoneyObject(attrs["foreignAmount"])

        if attrs["settledAt"]:
            self.settled_at = datetime.fromisoformat(attrs["settledAt"])
        self.created_at = datetime.fromisoformat(attrs["createdAt"])

        if attrs["category"]["data"]:
            self.category = PartialCategoryParent(
                self._client,
                {
                    "id": attrs["category"]["data"]["id"],
                    "relationships": {"parent": attrs["parentCategory"]},
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
