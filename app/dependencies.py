from functools import lru_cache

from app.client import UberEatsClient


@lru_cache
def get_client() -> UberEatsClient:
    return UberEatsClient()
