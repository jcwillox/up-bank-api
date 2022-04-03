from ._sync import Client

try:
    from ._async import AsyncClient as AsyncClient
except ValueError:
    pass
