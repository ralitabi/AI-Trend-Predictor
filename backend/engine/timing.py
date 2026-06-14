"""Best-time-to-trade estimate.

Buckets recent hourly candles by hour-of-day and finds the window where this
asset historically makes its largest moves — i.e. when there's the most
opportunity (and the most volatility). Returned in UTC; the UI converts to the
viewer's local time. This is a statistical tendency, not a guarantee.
"""
import pandas as pd

WINDOW = 4  # hours


def best_window(hourly: list[dict]) -> dict | None:
    if len(hourly) < 72:  # need ~3 days of hourly data
        return None
    df = pd.DataFrame(hourly)
    df["hour"] = ((df["time"] // 3600) % 24).astype(int)  # UTC hour-of-day
    df["absret"] = (df["close"] - df["open"]).abs() / df["open"] * 100
    by = df.groupby("hour")["absret"].mean().to_dict()
    hours = [float(by.get(h, 0.0)) for h in range(24)]

    best_sum, best_start = -1.0, 0
    for s in range(24):
        tot = sum(hours[(s + i) % 24] for i in range(WINDOW))
        if tot > best_sum:
            best_sum, best_start = tot, s

    overall = sum(hours) / 24 or 1e-9
    intensity = (best_sum / WINDOW) / overall  # how much busier than average
    return {
        "start_utc": best_start,
        "end_utc": (best_start + WINDOW) % 24,
        "intensity": round(intensity, 2),
        "basis": "hours with the largest average moves over the last ~2 weeks",
    }
