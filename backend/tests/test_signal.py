from engine import indicators, signal


def test_make_plan_long_math():
    p = signal.make_plan("up", 100.0, 2.0)
    assert p["direction"] == "long"
    assert p["entry"] == 100.0
    assert p["stop"] == round(100.0 - 1.5 * 2.0, 6)
    assert p["target"] == round(100.0 + 2.5 * 2.0, 6)
    assert p["rr"] == round(2.5 / 1.5, 2)


def test_make_plan_short_math():
    p = signal.make_plan("down", 100.0, 2.0)
    assert p["direction"] == "short"
    assert p["stop"] == round(100.0 + 1.5 * 2.0, 6)
    assert p["target"] == round(100.0 - 2.5 * 2.0, 6)


def test_make_plan_guards():
    assert signal.make_plan("neutral", 100.0, 2.0) is None
    assert signal.make_plan("up", 100.0, 0.0) is None
    assert signal.make_plan("up", 0.0, 2.0) is None


def test_score_empty_board_is_neutral():
    s = signal.score({"details": [], "trend_strength": "moderate",
                      "volatility": "moderate", "adx": 20})
    assert s["bias"] == "neutral"
    assert s["confidence"] == 0


def test_score_on_real_analysis_is_bounded(make_candles):
    s = signal.score(indicators.analyze(make_candles(220)))
    assert s["bias"] in ("up", "down", "neutral")
    assert 0 <= s["confidence"] <= 92
    # the calibration floor: any committed call clears the 60 confidence floor
    if s["bias"] != "neutral":
        assert s["confidence"] >= 60


def test_assess_safety_neutral_is_never_safe():
    sf = signal.assess_safety(
        {"bias": "neutral", "confidence": 0, "htf_note": None},
        {"volatility": "moderate", "adx": 10},
    )
    assert sf["direction"] == "none"
    assert sf["level"] == "risky"
    assert sf["score"] >= 72
