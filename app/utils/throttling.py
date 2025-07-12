from slowapi.util import get_remote_address
from slowapi import Limiter

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    storage_uri="redis://localhost:6379",
)