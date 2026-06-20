import pytest

from engine import indicators


def test_analyze_returns_expected_shape(make_candles):
    a = indicators.analyze(make_candles(220))
    for key in ("votes", "details", "volatility", "atr_pct", "atr_abs",
                "adx", "trend_strength", "support", "resistance", "price"):
        assert key in a
    assert a["atr_abs"] > 0
    assert a["trend_strength"] in ("weak", "moderate", "strong")
    votes = a["votes"]
    # every counted vote belongs to an available, enabled indicator
    assert votes["up"] + votes["down"] + votes["neutral"] <= len(a["details"])
    assert votes["up"] + votes["down"] + votes["neutral"] > 0


def test_analyze_rejects_too_few_candles(make_candles):
    with pytest.raises(ValueError):
        indicators.analyze(make_candles(10))
