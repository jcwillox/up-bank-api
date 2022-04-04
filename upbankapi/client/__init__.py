from ._sync import Client

try:
    from ._async import AsyncClient
except ValueError:
    pass
