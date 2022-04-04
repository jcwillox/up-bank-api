from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from ..client.base import ClientBase


class ModelBase:
    """Base class for all models."""

    id: Optional[str] = None
    """The unique identifier of the model instance."""

    _raw_response: Dict
    """The raw response data returned from the API.

    This should **not** be used, it is only available for intermediary use to access properties
    that have not yet been exposed or to view the entire response.
    """

    _client: "ClientBase"

    def __init__(self, client: "ClientBase", data: Dict):
        self._client = client

        # strip data field from api response
        if "data" in data:
            data = data["data"]

        self.id = data.get("id")
        self._raw_response = data

        self.__parse__(
            attrs=data.get("attributes"),
            relations=data.get("relationships"),
            links=data.get("links"),
        )

    def __parse__(
        self, attrs: Optional[Dict], relations: Optional[Dict], links: Optional[Dict]
    ):
        """Parse the data retrieved from the API"""


class MoneyObject:
    """Representation of a MoneyObject."""

    def __init__(self, data: Dict):
        self.value: float = float(data["value"])
        """The amount of money."""

        self.value_in_base_units: int = data["valueInBaseUnits"]
        """The amount of money in the smallest denomination for the currency."""

        self.currency: str = data["currencyCode"]
        """The ISO 4217 currency code."""

    def __repr__(self):
        return f"<MoneyObject {self.value} {self.currency}>"
