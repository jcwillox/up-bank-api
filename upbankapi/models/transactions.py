from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List, Union

from .categories import Tag, PartialCategoryParent, PartialCategory
from .common import ModelBase, MoneyObject


class TransactionStatus(str, Enum):
    HELD = "HELD"
    SETTLED = "SETTLED"


class CardPurchaseMethodEnum(str, Enum):
    BAR_CODE = "BAR_CODE"
    OCR = "OCR"
    CARD_PIN = "CARD_PIN"
    CARD_DETAILS = "CARD_DETAILS"
    CARD_ON_FILE = "CARD_ON_FILE"
    ECOMMERCE = "ECOMMERCE"
    MAGNETIC_STRIPE = "MAGNETIC_STRIPE"
    CONTACTLESS = "CONTACTLESS"


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

    def __repr__(self):
        if self.foreign_amount:
            return f"<HoldInfo {self.amount.value} {self.amount.currency}: foreign_amount='{self.foreign_amount.value} {self.foreign_amount.currency}'>"
        return f"<HoldInfo {self.amount.value} {self.amount.currency}>"


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

    def __repr__(self):
        if self.boost_portion:
            return f"<RoundUp {self.amount.value} {self.amount.currency}: boost_portion='{self.boost_portion.value} {self.boost_portion.currency}'>"
        return f"<RoundUp {self.amount.value} {self.amount.currency}>"


class Cashback:
    """Representation of the Cashback object returned by a `Transaction`."""

    def __init__(self, data: Dict):
        self.amount: MoneyObject = MoneyObject(data["amount"])
        """The total amount of cashback paid, represented as a positive value."""

        self.description: str = data["description"]
        """A brief description of why this cashback was paid."""

    def __repr__(self):
        return f"<Cashback {self.amount.value} {self.amount.currency}>"


class CardPurchaseMethod:
    """Representation of the CardPurchaseMethod object returned by a `Transaction`."""

    def __init__(self, data: Dict):
        self.method: CardPurchaseMethodEnum = data["method"]
        """The type of card purchase."""

        self.card_suffix: Optional[str] = data["cardNumberSuffix"]
        """The last four digits of the card used for the purchase, if applicable."""

    def __repr__(self):
        if self.card_suffix:
            return (
                f"<CardPurchaseMethod {self.method}: card_suffix='{self.card_suffix}'>"
            )
        return f"<CardPurchaseMethod {self.method}>"


class Transaction(ModelBase):
    """Representation of a Transaction."""

    id: str
    """The unique identifier for this transaction."""

    status: TransactionStatus
    """The current processing status of this transaction."""

    raw_text: Optional[str] = None
    """The original, unprocessed text of the transaction."""

    description: str
    """A short description for this transaction. Usually the merchant name for purchases."""

    message: Optional[str] = None
    """Attached message for this transaction, such as a payment message, or a transfer note."""

    categorizable: bool
    """Boolean flag set to `true` on transactions that support the use of categories."""

    hold_info: Optional[HoldInfo] = None
    """The amount and foreign_amount of this transaction while it was/is in the HELD state."""

    round_up: Optional[RoundUp] = None
    """Details of how this transaction was rounded-up.

    If no Round Up was applied this field will be null.
    """

    cashback: Optional[Cashback] = None
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

    foreign_amount: Optional[MoneyObject] = None
    """The foreign currency amount of this transaction.

    This field will be `None` for domestic transactions.
    """

    card_purchase_method: Optional[CardPurchaseMethod] = None
    """Information about the card used for this transaction, if applicable."""

    settled_at: Optional[datetime] = None
    """The `datetime` at which this transaction settled.

    This field will be `None` for transactions that are currently in the `HELD` status.
    """

    created_at: datetime
    """The `datetime` at which this transaction was first encountered."""

    category: Optional[PartialCategoryParent] = None
    """The category assigned to this transaction."""

    tags: List[Tag]
    """The list of tags assigned to this transaction."""

    def __parse__(self, attrs: Dict, relations: Dict, links: Optional[Dict]):
        self.status = attrs["status"]
        self.raw_text = attrs["rawText"]
        self.description = attrs["description"]
        self.message = attrs["message"]
        self.categorizable = attrs["isCategorizable"]

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

        if attrs["cardPurchaseMethod"]:
            self.card_purchase_method = CardPurchaseMethod(attrs["cardPurchaseMethod"])

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

    def categorize(self, category: Optional[Union[str, PartialCategory]]) -> bool:
        """Assign a category to a transaction.

        Arguments:
            category: The category to assign to the transaction.
                      Setting this to `None` will de-categorize the transaction.
        """
        return self._client.categorize(self, category=None)

    def add_tags(self, *tags: Tag) -> bool:
        """Add tags to a given transaction.

        Arguments:
            *tags: The tags or tag ids to add to the transaction.
        """
        return self._client.add_tags(self, *tags)

    def remove_tags(self, *tags: Union[str, Tag]) -> bool:
        """Remove tags from a given transaction.

        Arguments:
            *tags: The tags or tag ids to remove to the transaction.
        """
        return self._client.remove_tags(self, *tags)

    def __repr__(self) -> str:
        """Return the representation of the transaction."""
        return f"<Transaction {self.status}: {self.amount} {self.currency} [{self.description}]>"


class AsyncTransaction(Transaction):
    async def categorize(self, category: Optional[Union[str, PartialCategory]]) -> bool:
        """Assign a category to a transaction.

        Arguments:
            category: The category to assign to the transaction.
                      Setting this to `None` will de-categorize the transaction.
        """
        return await self._client.categorize(self, category=None)

    async def add_tags(self, *tags: Tag) -> bool:
        """Add tags to a given transaction.

        Arguments:
            *tags: The tags or tag ids to add to the transaction.
        """
        return await self._client.add_tags(self, *tags)

    async def remove_tags(self, *tags: Union[str, Tag]) -> bool:
        """Remove tags from a given transaction.

        Arguments:
            *tags: The tags or tag ids to remove to the transaction.
        """
        return await self._client.remove_tags(self, *tags)
