from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from ..client.base import ClientBase


class ModelBase:
    """Base class for all models."""

    id: Optional[str]
    """The unique identifier of the model instance."""

    raw_response: Dict
    """The raw response data returned from the API."""

    _client: "ClientBase"

    def __init__(self, client: "ClientBase", data: Dict):
        self._client = client

        # strip data field from api response
        if "data" in data:
            data = data["data"]

        self.id = data.get("id")
        self.raw_response = data

        self.__parse__(
            attrs=data.get("attributes"),
            relations=data.get("relationships"),
            links=data.get("links"),
        )

    def __parse__(
        self, attrs: Optional[Dict], relations: Optional[Dict], links: Optional[Dict]
    ):
        """Parse the data retrieved from the API"""
        pass


class MoneyObject:
    """Representation of a MoneyObject."""

    value: float
    """The amount of money."""

    value_in_base_units: int
    """The amount of money in the smallest denomination for the currency."""

    currency: str
    """The ISO 4217 currency code."""

    def __init__(self, data: Dict):
        self.value = data["value"]
        self.value_in_base_units = data["valueInBaseUnits"]
        self.currency = data["currencyCode"]
