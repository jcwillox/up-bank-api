"""Typed python client for interacting with Up's banking API."""
from .client import Client
from .exceptions import *

try:
    from .client import AsyncClient
except ImportError:
    pass
