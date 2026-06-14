"""Tiny in-memory TTL cache so we stay well inside free-tier API limits."""
import time
from threading import Lock

_store: dict[str, tuple[float, object]] = {}
_lock = Lock()


def get(key: str):
    with _lock:
        hit = _store.get(key)
        if hit is None:
            return None
        expires, value = hit
        if time.time() > expires:
            del _store[key]
            return None
        return value


def put(key: str, value, ttl: float):
    with _lock:
        _store[key] = (time.time() + ttl, value)


def ttl_for(tf: str) -> float:
    """Refresh cadence per timeframe — kept short so the technical signal reflects
    a newly-closed candle within a couple of seconds."""
    return {"1m": 3, "5m": 5, "15m": 8, "1h": 20, "4h": 90, "1d": 300, "1wk": 900}.get(tf, 20)
