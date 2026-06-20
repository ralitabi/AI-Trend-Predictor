from engine import backtest


def test_run_metrics_are_self_consistent(make_candles):
    res = backtest.run(make_candles(280), 3600)
    assert res["trades"] == res["wins"] + res["losses"]
    if res["trades"]:
        # equity curve has a zero anchor plus one point per closed trade
        assert len(res["equity"]) == res["trades"] + 1
        assert res["equity"][0]["r"] == 0.0
        assert res["win_rate"] == round(res["wins"] / res["trades"] * 100, 1)
        assert res["max_drawdown_r"] >= 0
        assert len(res["recent"]) <= 15
        # net R equals the final point on the equity curve
        assert res["net_r"] == res["equity"][-1]["r"]


def test_run_with_too_little_history_is_empty():
    flat = [{"time": i * 3600, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0}
            for i in range(12)]
    res = backtest.run(flat, 3600)
    assert res["trades"] == 0
    assert res["equity"] == []
    assert "note" in res
