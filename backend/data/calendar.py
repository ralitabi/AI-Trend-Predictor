"""Upcoming high-impact economic events from the free ForexFactory weekly feed
(faireconomy mirror) — no API key."""
import datetime as dt

import httpx

from data import cache

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"


def upcoming(limit: int = 8) -> list[dict]:
    cached = cache.get("calendar")
    if cached is not None:
        return cached
    out: list[dict] = []
    try:
        r = httpx.get(URL, timeout=8, headers={"User-Agent": "Mozilla/5.0 (TrendPredictor)"})
        r.raise_for_status()
        now = dt.datetime.now(dt.timezone.utc).timestamp()
        for e in r.json():
            if e.get("impact") not in ("High", "Medium"):
                continue
            try:
                ts = dt.datetime.fromisoformat(e["date"]).timestamp()
            except Exception:
                continue
            if ts < now - 3600:  # drop events more than an hour past
                continue
            out.append({
                "title": e.get("title", ""),
                "country": e.get("country", ""),
                "time": int(ts),
                "impact": e["impact"],
                "forecast": e.get("forecast", ""),
                "previous": e.get("previous", ""),
            })
        out = sorted(out, key=lambda x: x["time"])[:limit]
    except Exception:
        out = []
    cache.put("calendar", out, ttl=1800)  # refresh every 30 min
    return out
