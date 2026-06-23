from data import store


def test_prediction_round_trip():
    store.log_prediction(
        "UNITTEST", "4h", 50.0,
        {"bias": "down", "confidence": 60, "volatility": "high"},
        {"direction": "down", "confidence": 55},
    )
    hist = store.history("UNITTEST", "4h")
    assert hist and hist[0]["tech_bias"] == "down"
    assert hist[0]["ai_direction"] == "down"

    rep = store.report("UNITTEST", "4h")
    assert rep["totals"]["logged"] >= 1
    assert rep["totals"]["pending"] >= 1  # not yet evaluated


def test_paper_trade_lifecycle():
    store.open_paper_trade("PAPERTST", "1h", "long", 10.0, 9.0, 12.0, 2.0)
    assert store.has_open_trade("PAPERTST", "1h") is True

    trade = next(t for t in store.open_trades() if t["symbol"] == "PAPERTST")
    store.close_paper_trade(trade["id"], 12.0, "win", 2.0)

    pf = store.paper_portfolio("PAPERTST", "1h")
    assert pf["closed_count"] == 1
    assert pf["wins"] == 1
    assert pf["win_rate"] == 100.0
    assert pf["net_r"] == 2.0
    assert store.has_open_trade("PAPERTST", "1h") is False


def test_signal_snapshot_round_trip():
    scored = {"bias": "up", "confidence": 71}
    analysis = {
        "volatility": "low", "adx": 27.4, "trend_strength": "strong",
        "votes": {"up": 9, "down": 2, "neutral": 3},
        "support": 99.0, "resistance": 110.0,
    }
    store.log_signal("SIGTEST", "1h", 100.5, scored, analysis)
    rows = store.signal_history("SIGTEST", "1h")
    assert rows and rows[0]["bias"] == "up"
    assert rows[0]["confidence"] == 71
    assert rows[0]["votes_up"] == 9
    assert rows[0]["adx"] == 27.4
    assert rows[0]["resistance"] == 110.0


def test_save_candles_is_incremental_and_idempotent():
    base = [{"time": 1_700_000_000 + i * 3600, "open": 1.0, "high": 2.0, "low": 0.5,
             "close": 1.5, "volume": 100} for i in range(5)]
    assert store.save_candles("CNDL", "1h", base) == 5          # backfill all
    assert store.save_candles("CNDL", "1h", base) == 1          # only the last (forming) re-written
    more = base + [{"time": 1_700_000_000 + 5 * 3600, "open": 1.5, "high": 2.1,
                    "low": 1.4, "close": 2.0, "volume": 120}]
    assert store.save_candles("CNDL", "1h", more) == 2          # last existing + 1 new
    hist = store.candle_history("CNDL", "1h")
    assert len(hist) == 6
    assert hist[-1]["close"] == 2.0
    assert hist[0]["time"] < hist[-1]["time"]                   # chronological


def test_mark_broadcast_dedupes_per_candle():
    assert store.mark_broadcast("BCAST", "1h", 1_700_000_000) is True
    assert store.mark_broadcast("BCAST", "1h", 1_700_000_000) is False  # same candle → skip
    assert store.mark_broadcast("BCAST", "1h", 1_700_003_600) is True   # next candle → allowed


def test_counts_reports_tables():
    c = store.counts()
    for table in ("predictions", "signals", "forecasts", "paper_trades"):
        assert table in c and isinstance(c[table], int)
    assert "last_signal_ts" in c


def test_forecast_upsert_keeps_latest():
    fc = {"time": 1_700_000_000, "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "direction": "up"}
    store.log_forecast("FCTEST", "1h", fc)
    store.log_forecast("FCTEST", "1h", {**fc, "close": 1.8})  # same target_time → replace

    rows = store.forecast_history("FCTEST", "1h")
    assert len(rows) == 1
    assert rows[0]["close"] == 1.8
