import time

from data import store
from engine import scoring


def test_grade_logic():
    assert scoring._grade("up", "up") == 1
    assert scoring._grade("down", "down") == 1
    assert scoring._grade("up", "down") == 0
    assert scoring._grade("neutral", "up") is None  # no call = excluded


def test_evaluate_pending_scores_a_due_prediction():
    tf_sec = 3600
    now = int(time.time())
    ts = now - 3 * tf_sec  # 3h ago on a 1h tf → its target candle has long closed

    conn = store._conn()
    try:
        conn.execute(
            "INSERT INTO predictions (ts, symbol, tf, price, tech_bias, tech_confidence,"
            " ai_direction, ai_confidence, volatility) VALUES (?,?,?,?,?,?,?,?,?)",
            (ts, "SCORETEST", "1h", 100.0, "up", 70, "up", 65, "low"),
        )
        conn.commit()
    finally:
        conn.close()

    target_open = (ts // tf_sec) * tf_sec + tf_sec

    def fake_fetch(symbol, tf, limit):
        # only SCORETEST has data; other pending groups raise → skipped, untouched
        if symbol != "SCORETEST":
            raise RuntimeError("no data for this symbol in test")
        # close went 100 → 105 (up); predicted up → should grade as a hit
        return [{"time": target_open, "open": 100.0, "high": 106.0,
                 "low": 99.0, "close": 105.0, "volume": 1.0}]

    evaluated = scoring.evaluate_pending(fake_fetch)
    assert evaluated >= 1

    rep = store.report("SCORETEST", "1h")
    assert rep["technical"]["hits"] >= 1
    assert rep["technical"]["accuracy"] == 100.0
    assert rep["totals"]["pending"] == 0
