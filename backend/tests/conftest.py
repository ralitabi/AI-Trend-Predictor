"""Shared test setup. Point the store at a throwaway SQLite file BEFORE anything
imports it, so tests never touch a real predictions.db (and never need Turso)."""
import math
import os
import random
import tempfile

os.environ["PREDICTIONS_DB"] = os.path.join(tempfile.mkdtemp(), "test_predictions.db")
# Make sure no durable-DB env leaks in from the dev machine / CI.
for _k in ("TURSO_DATABASE_URL", "TURSO_AUTH_TOKEN", "LIBSQL_URL", "LIBSQL_AUTH_TOKEN"):
    os.environ.pop(_k, None)

import pytest


@pytest.fixture
def make_candles():
    """Factory for synthetic OHLCV candles on a noisy, regime-switching trend —
    enough variety that the signal engine actually flips and trades."""
    def gen(n: int = 260, seed: int = 7, tf_sec: int = 3600,
            slope: float = 0.6, noise: float = 0.8) -> list[dict]:
        random.seed(seed)
        t0 = 1_700_000_000
        price = 100.0
        out: list[dict] = []
        for i in range(n):
            price = max(1.0, price + slope * math.sin(i / 18.0) + random.uniform(-noise, noise))
            o = price
            c = price + random.uniform(-0.5, 0.5)
            h = max(o, c) + random.uniform(0, 0.6)
            l = min(o, c) - random.uniform(0, 0.6)
            out.append({
                "time": t0 + i * tf_sec,
                "open": round(o, 4), "high": round(h, 4),
                "low": round(l, 4), "close": round(c, 4),
                "volume": 1000 + random.uniform(0, 500),
            })
            price = c
        return out
    return gen
