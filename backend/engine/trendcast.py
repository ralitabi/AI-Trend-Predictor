"""Multi-horizon trend forecast — "where is this likely to head next?".

For several look-ahead horizons (near / mid / far, measured in bars of the
current timeframe) we project price from its recent drift — the least-squares
slope of the last N closes — and bound the spread by volatility (ATR scaled by
sqrt(horizon)). Direction is up / down / sideways depending on whether the
projected move clears the noise band. Confidence blends how cleanly price has
actually been trending (regression R^2) with ADX trend strength, and decays for
longer horizons. This is a statistical projection, not a promise.
"""
import numpy as np
import pandas as pd

from engine import indicators as ind

# look-ahead horizons in bars of the current timeframe (near, mid, far)
HORIZONS = (3, 12, 48)


def _human(secs: float) -> str:
    if secs < 3600:
        return f"{round(secs / 60)} min"
    if secs < 86400:
        h = secs / 3600
        return f"{round(h)} hr" if h >= 1.5 else "1 hr"
    if secs < 7 * 86400:
        d = secs / 86400
        return f"{round(d)} days" if d >= 1.5 else "1 day"
    return f"{round(secs / (7 * 86400), 1)} wk"


def _headline(horizons: list[dict]) -> str:
    dirs = [h["direction"] for h in horizons]
    up, down = dirs.count("up"), dirs.count("down")
    if up == len(dirs):
        return "Uptrend expected to hold across every horizon"
    if down == len(dirs):
        return "Downtrend expected to hold across every horizon"
    if up and down:
        return "Trend likely flips between horizons — trade the one you hold"
    if up:
        return "Leaning up, but the move fades on longer horizons"
    if down:
        return "Leaning down, but the move fades on longer horizons"
    return "Mostly sideways — no strong directional edge right now"


def project(candles: list[dict], tf_sec: int) -> dict | None:
    if len(candles) < 60:
        return None
    df = pd.DataFrame(candles)
    close = df["close"].to_numpy(dtype=float)
    price = float(close[-1])
    if price <= 0:
        return None

    atr_series = ind.atr(df)
    atr_abs = float(atr_series.iloc[-1]) if not np.isnan(atr_series.iloc[-1]) else 0.0
    adx_series, _pdi, _mdi = ind.adx(df)
    adx_now = float(adx_series.iloc[-1]) if not np.isnan(adx_series.iloc[-1]) else 0.0

    horizons: list[dict] = []
    for i, h in enumerate(HORIZONS):
        # fit on a window proportional to the horizon (longer view → more history)
        win = int(min(len(close) - 1, max(h * 3, 24)))
        y = close[-win:]
        x = np.arange(win, dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        fit = slope * x + intercept
        ss_res = float(np.sum((y - fit) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2)) or 1e-9
        r2 = max(0.0, 1.0 - ss_res / ss_tot)

        projected = price + slope * h
        band = atr_abs * float(np.sqrt(h))  # spread grows with horizon
        move_abs = projected - price
        move_pct = move_abs / price * 100.0

        if band > 0 and abs(move_abs) < 0.5 * band:
            direction = "sideways"
        elif move_abs > 0:
            direction = "up"
        else:
            direction = "down"

        # clean trend (R^2) + real strength (ADX), decayed for far horizons
        conf = 40.0 + r2 * 35.0 + min(adx_now, 40.0) / 40.0 * 20.0
        conf *= 1.0 - 0.06 * i
        if direction == "sideways":
            conf = min(conf, 55.0)
        conf = int(max(20, min(90, round(conf))))

        horizons.append({
            "bars": h,
            "label": _human(h * tf_sec),
            "direction": direction,
            "move_pct": round(move_pct, 2),
            "target": round(projected, 6),
            "low": round(projected - band, 6),
            "high": round(projected + band, 6),
            "confidence": conf,
        })

    return {
        "price": round(price, 6),
        "adx": round(adx_now, 1),
        "bias": horizons[1]["direction"],  # the mid horizon is the headline read
        "headline": _headline(horizons),
        "horizons": horizons,
    }
