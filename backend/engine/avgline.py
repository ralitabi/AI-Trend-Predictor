"""Average trend line with directional prediction colouring.

A smoothed average (EMA) of price. The line predicts the trend continues in its
current direction; each segment is coloured:
  - YELLOW : the average kept its predicted direction (trend held)
  - PURPLE : the average reversed against the prediction (a wrong-prediction
             "branch" — where the trend broke)
An ORANGE projection extends the average forward by its recent slope — the
PREDICTED next line, "where the trend would go" if it continues. Drawn far
enough ahead to be read as a forecast. Statistical projection, not a promise.
"""
import numpy as np
import pandas as pd

from engine import indicators as ind

YELLOW = "#f5c518"   # average held its predicted direction
PURPLE = "#b388ff"   # average broke against the prediction (wrong-prediction branch)
ORANGE = "#ff8a1f"   # forward projection — the predicted next line


def build(candles: list[dict], tf_sec: int, period: int = 20, project: int = 24) -> dict:
    df = pd.DataFrame(candles)
    times = df["time"].tolist()
    ma = ind.ema(df["close"], period).to_numpy()

    points: list[dict] = []
    for i in range(period + 1, len(ma)):
        if np.isnan(ma[i]) or np.isnan(ma[i - 1]) or np.isnan(ma[i - 2]):
            continue
        slope_prev = ma[i - 1] - ma[i - 2]      # the direction we'd extrapolate
        realized = ma[i] - ma[i - 1]            # what actually happened
        held = (slope_prev >= 0 and realized >= 0) or (slope_prev < 0 and realized < 0)
        points.append({"time": int(times[i]), "value": round(float(ma[i]), 6),
                       "color": YELLOW if held else PURPLE, "seg": "trend"})

    # forward projection: extend by the average slope over the last few bars,
    # projecting further out so the predicted line reads clearly as a forecast.
    valid = ma[~np.isnan(ma)]
    if len(valid) >= 6 and points:
        k = min(5, len(valid) - 1)
        slope = (valid[-1] - valid[-1 - k]) / k
        last_t, last_v = int(times[-1]), float(valid[-1])
        for j in range(1, project + 1):
            points.append({"time": last_t + j * tf_sec,
                           "value": round(last_v + slope * j, 6),
                           "color": ORANGE, "seg": "proj"})

    return {"period": period, "points": points,
            "legend": {"trend": YELLOW, "broke": PURPLE, "projection": ORANGE}}
