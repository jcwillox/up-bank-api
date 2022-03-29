from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from ..client import ClientBase


class ModelBase:
    """Base class for all models."""

    # The unique identifier of the model instance
    id: Optional[str]

    # The raw response data returned from the API
    raw_response: Dict

    _client: "ClientBase"

    def __init__(self, client: "ClientBase", data: Dict):
        self._client = client
        self.id = data.get("id")
        self.raw_response = data

        self.__parse__(
            data.get("attributes"), data.get("relationships"), data.get("links")
        )

    def __parse__(
        self, attrs: Optional[Dict], relations: Optional[Dict], links: Optional[Dict]
    ):
        """Parse the data retrieved from the API"""
        pass


class MoneyObject:
    """Representation of a MoneyObject"""

    # The amount of money
    value: float

    # The amount of money in the smallest denomination for the currency
    value_in_base_units: int

    # The ISO 4217 currency code.
    currency: str

    def __init__(self, data: Dict):
        self.value = data["value"]
        self.value_in_base_units = data["valueInBaseUnits"]
        self.currency = data["currencyCode"]
