from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Optional, Dict

from .common import ModelBase
from .pagination import AsyncPaginatedList, PaginatedList
from .transactions import AsyncTransaction, Transaction
from ..const import DEFAULT_PAGE_SIZE


class WebhookDeliveryStatus(str, Enum):
    DELIVERED = "DELIVERED"
    UNDELIVERABLE = "UNDELIVERABLE"
    BAD_RESPONSE_CODE = "BAD_RESPONSE_CODE"


class WebhookEventType(str, Enum):
    PING = "PING"
    TRANSACTION_CREATED = "TRANSACTION_CREATED"
    TRANSACTION_SETTLED = "TRANSACTION_SETTLED"
    TRANSACTION_DELETED = "TRANSACTION_DELETED"


class Webhook(ModelBase):
    """Representation of a Webhook."""

    id: str
    """The unique identifier for this webhook."""

    url: str
    """The URL that this webhook is configured to `POST` events to."""

    description: Optional[str] = None
    """An optional description that was provided at the time the webhook was created."""

    secret_key: Optional[str] = None
    """A shared secret key used to sign all webhook events sent to the configured webhook URL.

    This field is returned only once, upon the initial creation of the webhook.
    """

    created_at: datetime
    """The `datetime` at which this webhook was created."""

    def __parse__(self, attrs: Dict, **kwargs):
        self.url = attrs["url"]
        self.description = attrs["description"]
        self.secret_key = attrs.get("secretKey")
        self.created_at = datetime.fromisoformat(attrs["createdAt"])

    def ping(self) -> WebhookEvent:
        """Sends a ping event to the webhook

        Returns:
            The ping event response.
        """
        return self._client.webhook.ping(self)

    def logs(
        self,
        *,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedList[WebhookLog]:
        """Retrieves the logs for this webhook.

        Arguments:
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the webhook logs.
        """
        return self._client.webhook.logs(self, limit=limit, page_size=page_size)

    def delete(self) -> bool:
        """Deletes this webhook.

        Returns:
            `True` if successful, otherwise raises exception.
        """
        return self._client.webhook.delete(self)

    def __repr__(self) -> str:
        """Return the representation of the webhook."""
        if self.description:
            return f"<Webhook '{self.id}': {self.url} ({self.description})>"
        return f"<Webhook '{self.id}': {self.url}>"


class AsyncWebhook(Webhook):
    async def ping(self) -> AsyncWebhookEvent:
        """Sends a ping event to the webhook

        Returns:
            The ping event response.
        """
        return await self._client.webhook.ping(self)

    async def logs(
        self,
        *,
        limit: int = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncPaginatedList[WebhookLog]:
        """Retrieves the logs for this webhook.

        Arguments:
            limit: The maximum number of records to return.
            page_size: The number of records to return in each page. (max appears to be 100)

        Returns:
            A paginated list of the webhook logs.
        """
        return await self._client.webhook.logs(self, limit=limit, page_size=page_size)

    async def delete(self) -> bool:
        """Deletes this webhook.

        Returns:
            `True` if successful, otherwise raises exception.
        """
        return await self._client.webhook.delete(self)


class WebhookResponse:
    """Representation of a WebhookResponse."""

    def __init__(self, data: Dict):
        self.status_code: int = data["statusCode"]
        """The HTTP status code received in the response."""

        self.body: str = data["body"]
        """The payload that was received in the response body."""

    def __repr__(self):
        return f"<WebhookResponse {self.status_code}>"


class WebhookLog(ModelBase):
    """Representation of a WebhookLog entry."""

    id: str
    """The unique identifier for this log entry."""

    event: WebhookEvent
    """The webhook event associated with this log entry."""

    response: Optional[WebhookResponse] = None
    """Information about the response that was received from the webhook URL."""

    status: WebhookDeliveryStatus
    """The success or failure status of this delivery attempt."""

    created_at: datetime
    """The `datetime` at which this log entry was created."""

    def __parse__(self, attrs: Dict, relations: Dict, **kwargs):
        self.event = WebhookEvent(
            self._client, json.loads(attrs["request"]["body"])["data"]
        )

        if attrs["response"]:
            self.response = WebhookResponse(attrs["response"])

        self.status = attrs["deliveryStatus"]
        self.created_at = datetime.fromisoformat(attrs["createdAt"])

    def __repr__(self) -> str:
        """Return the representation of the webhook log."""
        if self.response:
            return (
                f"<WebhookLog {self.status}: response_code={self.response.status_code}>"
            )
        return f"<WebhookLog {self.status}>"


class AsyncWebhookLog(WebhookLog):
    event: AsyncWebhookEvent


class WebhookEvent(ModelBase):
    """Representation of a WebhookEvent."""

    id: str
    """The unique identifier for this event. This will remain constant across delivery retries."""

    type: WebhookEventType
    """The type of this event. This can be used to determine what action to take in response to the event."""

    created_at: datetime
    """The `datetime` at which this event was generated."""

    webhook_id: str
    """The id of the webhook that that event was sent to."""

    transaction_id: Optional[str] = None
    """The id of the transaction associated with this webhook."""

    def __parse__(self, attrs: Dict, relations: Dict, **kwargs):
        self.type = attrs["eventType"]
        self.created_at = datetime.fromisoformat(attrs["createdAt"])
        self.webhook_id = relations["webhook"]["data"]["id"]

        if "transaction" in relations:
            self.transaction_id = relations["transaction"]["data"]["id"]

    def webhook(self) -> Webhook:
        """Fetch the details of the associated webhook.

        Returns:
            The associated webhook.
        """
        return self._client.webhook.get(self.webhook_id)

    def transaction(self) -> Transaction:
        """Fetch the details of the associated transaction.

        Returns:
            The associated transaction.
        """
        if self.transaction_id:
            return self._client.transaction(self.transaction_id)

    def __repr__(self) -> str:
        """Return the representation of the webhook event."""
        if self.transaction_id:
            return f"<WebhookEvent {self.type}: webhook_id='{self.webhook_id}' transaction_id='{self.transaction_id}'>"
        return f"<WebhookEvent {self.type}: webhook_id='{self.webhook_id}'>"


class AsyncWebhookEvent(WebhookEvent):
    async def webhook(self) -> AsyncWebhook:
        """Fetch the details of the associated webhook.

        Returns:
            The associated webhook.
        """
        return await self._client.webhook.get(self.webhook_id)

    async def transaction(self) -> AsyncTransaction:
        """Fetch the details of the associated transaction.

        Returns:
            The associated transaction.
        """
        if self.transaction_id:
            return await self._client.transaction(self.transaction_id)
