from ._sync import Client, WebhookAdapter

try:
    from ._async import AsyncClient, AsyncWebhookAdapter
except ValueError:
    pass
