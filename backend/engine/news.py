"""Free news via RSS — no API key, no rate limits worth worrying about."""
import re
from concurrent.futures import ThreadPoolExecutor

import feedparser
import httpx

from data import cache

# Tiny finance lexicon for a fast, key-free headline sentiment read.
_BULL = {
    "surge", "surges", "surged", "soar", "soars", "soared", "rally", "rallies", "rallied",
    "jump", "jumps", "jumped", "gain", "gains", "gained", "rise", "rises", "rose", "climb",
    "climbs", "record", "high", "highs", "bullish", "boom", "beat", "beats", "upgrade",
    "upgraded", "outperform", "strong", "tops", "wins", "optimism", "recovery", "rebound",
    "breakout", "approval", "approved", "adoption", "adopts", "inflows", "soaring",
}
_BEAR = {
    "plunge", "plunges", "plunged", "crash", "crashes", "crashed", "fall", "falls", "fell",
    "drop", "drops", "dropped", "slump", "slumps", "selloff", "fear", "fears", "bearish",
    "tumble", "tumbles", "sink", "sinks", "downgrade", "downgraded", "underperform", "weak",
    "miss", "misses", "loss", "losses", "warning", "warns", "slide", "slides", "recession",
    "ban", "bans", "hack", "hacked", "lawsuit", "crackdown", "liquidation", "liquidated",
    "dump", "outflows", "selloffs", "sell-off",
}

# Per asset-class feeds; broad finance feeds apply to everything.
FEEDS = {
    "global": [
        "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "https://www.investing.com/rss/news_25.rss",  # market overview
    ],
    "crypto": [
        "https://cointelegraph.com/rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
    ],
    "forex": ["https://www.investing.com/rss/news_1.rss"],
    "commodity": ["https://www.investing.com/rss/news_11.rss"],
    "index": ["https://www.investing.com/rss/news_25.rss"],
}


def headlines(asset_class: str, limit: int = 10) -> list[str]:
    key = f"news:{asset_class}"
    cached = cache.get(key)
    if cached is not None:
        return cached[:limit]

    def _fetch(url: str) -> list[str]:
        try:
            # fetch ourselves with a hard timeout — feedparser.parse(url) has none
            # and one slow RSS server would hang the whole /predict request
            resp = httpx.get(url, timeout=6, follow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0 (TrendPredictor RSS)"})
            feed = feedparser.parse(resp.content)
            return [e.title.strip() for e in feed.entries[:6] if getattr(e, "title", None)]
        except Exception:
            return []  # a dead feed should never break a prediction

    urls = FEEDS.get(asset_class, []) + FEEDS["global"]
    titles: list[str] = []
    # parallel fetch: worst case = slowest single feed, not the sum of all
    with ThreadPoolExecutor(max_workers=len(urls)) as pool:
        for batch in pool.map(_fetch, urls):
            titles += batch

    # de-dupe, keep order
    seen, unique = set(), []
    for t in titles:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)

    cache.put(key, unique, ttl=600)  # news refresh: 10 min
    return unique[:limit]


def sentiment(asset_class: str) -> dict:
    """Lexicon-based sentiment over recent headlines — a quick, key-free read."""
    heads = headlines(asset_class, limit=12)
    items, total = [], 0
    for h in heads:
        words = set(re.findall(r"[a-z'-]+", h.lower()))
        net = len(words & _BULL) - len(words & _BEAR)
        total += net
        items.append({
            "title": h,
            "sentiment": "bullish" if net > 0 else "bearish" if net < 0 else "neutral",
        })
    n = len(heads) or 1
    score = max(-100, min(100, round(total / n * 45)))
    label = "Bullish" if score >= 15 else "Bearish" if score <= -15 else "Neutral"
    return {
        "score": score, "label": label,
        "bullish": sum(1 for i in items if i["sentiment"] == "bullish"),
        "bearish": sum(1 for i in items if i["sentiment"] == "bearish"),
        "headlines": items[:8],
    }
