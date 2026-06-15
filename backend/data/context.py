"""Market-context data — crypto Fear & Greed index + perpetual funding rates.

Both are free, no-key public endpoints:
  - Fear & Greed: alternative.me (market-wide crypto sentiment, updates ~daily)
  - Funding rate: Binance USDⓈ-M futures premiumIndex (per perpetual, every 8h)
"""
import httpx

from data import cache

FNG_URL = "https://api.alternative.me/fng/?limit=1"
FAPI_HOSTS = ["https://fapi.binance.com", "https://fapi1.binance.com"]


def fear_greed() -> dict | None:
    cached = cache.get("fng")
    if cached is not None:
        return cached
    out = None
    try:
        r = httpx.get(FNG_URL, timeout=8)
        r.raise_for_status()
        d = r.json()["data"][0]
        out = {
            "value": int(d["value"]),
            "classification": d["value_classification"],
            "timestamp": int(d["timestamp"]),
        }
    except Exception:
        out = None
    cache.put("fng", out, ttl=1800)  # updates ~daily; refresh every 30 min
    return out


def funding_rate(symbol: str) -> dict | None:
    """Current perpetual funding for a Binance symbol. Positive = longs pay
    shorts (crowd leaning long); negative = shorts pay longs."""
    key = f"funding:{symbol}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    out = None
    for host in FAPI_HOSTS:
        try:
            r = httpx.get(f"{host}/fapi/v1/premiumIndex", params={"symbol": symbol}, timeout=8)
            r.raise_for_status()
            d = r.json()
            rate = float(d["lastFundingRate"])
            if rate > 0.0003:
                sentiment = "Longs pay shorts — crowd heavily long (overheated)"
            elif rate > 0:
                sentiment = "Longs pay shorts — mild long bias"
            elif rate < -0.0003:
                sentiment = "Shorts pay longs — crowd heavily short"
            elif rate < 0:
                sentiment = "Shorts pay longs — mild short bias"
            else:
                sentiment = "Flat funding — balanced"
            out = {
                "symbol": symbol,
                "rate_pct": round(rate * 100, 4),
                "annualized_pct": round(rate * 3 * 365 * 100, 2),  # 3 fundings/day
                "next_funding_time": int(d["nextFundingTime"]) // 1000,
                "mark_price": float(d["markPrice"]),
                "sentiment": sentiment,
            }
            break
        except Exception:
            continue
    cache.put(key, out, ttl=120)  # mark price moves; refresh every 2 min
    return out
