from engine import forecast


def test_project_points_with_bias(make_candles):
    fc = forecast.project(make_candles(80), 3600, "up", 70)
    assert fc is not None
    assert fc["direction"] == "up"
    assert fc["close"] > fc["open"]
    assert fc["high"] >= fc["close"] and fc["low"] <= fc["open"]


def test_project_needs_enough_candles(make_candles):
    assert forecast.project(make_candles(10), 3600, "up", 70) is None


def test_reconstruct_and_summarize(make_candles):
    fcs = forecast.reconstruct(make_candles(160), 3600)
    s = forecast.summarize(fcs)
    assert s["graded"] == len(fcs)
    assert s["total"] == s["correct"] + s["slight"] + s["complete"]
    if s["total"]:
        assert s["accuracy"] == round(s["correct"] / s["total"] * 100, 1)
