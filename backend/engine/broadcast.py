"""Telegram signal-service — posts high-conviction setups to the group on a
schedule, one per market per candle, with a rendered chart.

Runs server-side off the same scheduled trigger as the snapshot collector, so it
works 24/7 with nobody on the site. For every tracked asset on 1h it computes the
live read (same scorer + higher-timeframe confluence the dashboard uses), saves
the snapshot, and — only when the call is a confident directional one — renders a
chart and broadcasts it (deduped per candle so it never spams).
"""
from datetime import datetime, timezone

from data import store
from data.assets import ASSETS
from engine import alerts, chartimg, forecast, indicators, signal, timing, trendcast

TF_SECONDS = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400, "1wk": 604800}
MIN_CONFIDENCE = 75  # "high-conviction only"


def _fmt(p: float) -> str:
    return f"{p:,.2f}" if p >= 100 else f"{p:.5f}"


def _utc(ts: int) -> str:
    return datetime.fromtimestamp(int(ts), timezone.utc).strftime("%H:%M")


def build_message(name: str, tf: str, scored: dict, analysis: dict, plan: dict,
                  fc: dict | None, tcast: dict | None, bw: dict | None,
                  candle_open: int, tf_sec: int) -> str:
    bias = scored["bias"]
    emoji = "🟢" if bias == "up" else "🔴"
    word = "LONG" if bias == "up" else "SHORT"
    arrow = "UP" if bias == "up" else "DOWN"
    entry = plan["entry"]
    stop, target, rr = plan["stop"], plan["target"], plan["rr"]
    stop_pct = abs((stop - entry) / entry * 100) if entry else 0
    tgt_pct = abs((target - entry) / entry * 100) if entry else 0

    lines = [
        f"{emoji} {name} · {tf} · {word}    confidence {scored['confidence']}%",
        f"Regime: {analysis.get('trend_strength', '—')} trend (ADX {round(analysis.get('adx', 0))})",
        "",
        f"⏰ {_utc(candle_open)}→{_utc(candle_open + tf_sec)} UTC (this candle) → {arrow}",
    ]
    if tcast and tcast.get("horizons"):
        h = tcast["horizons"][0]
        hdir = {"up": "UP", "down": "DOWN", "sideways": "SIDEWAYS"}.get(h["direction"], h["direction"])
        lines.append(f"🎯 Next {h['label']}: {hdir} toward {_fmt(h['target'])} ({h['confidence']}%)")
    lines += [
        "",
        f"Entry   {_fmt(entry)}",
        f"Stop    {_fmt(stop)}   (−{stop_pct:.1f}%)",
        f"Target  {_fmt(target)}   (+{tgt_pct:.1f}%, R:R {rr})",
    ]
    if bw:
        lines.append(f"\n🕒 Best hours: {int(bw['start_utc']):02d}:00–{int(bw['end_utc']):02d}:00 UTC")
    lines.append("\nTrading AI · auto-generated signal")
    return "\n".join(lines)


def run(candles_for, htf_of, min_conf: int = MIN_CONFIDENCE, force: bool = False) -> dict:
    """One broadcast pass over all assets on 1h. `candles_for(sym, tf, n)` and
    `htf_of(sym, tf) -> (htf, htf_trend)` are injected by the API layer."""
    tf, tf_sec = "1h", TF_SECONDS["1h"]
    sent = skipped = saved = errors = 0
    posted: list[str] = []

    for sym, asset in ASSETS.items():
        try:
            data = candles_for(sym, tf, 300)
            closed = data[:-1] if len(data) > indicators.MIN_CANDLES else data
            analysis = indicators.analyze(closed)
            _, htf_trend = htf_of(sym, tf)
            scored = signal.score(analysis, htf_trend)
            price = data[-1]["close"]
            plan = signal.make_plan(scored["bias"], price, analysis["atr_abs"])
            fc = forecast.project(data, tf_sec, scored["bias"], scored["confidence"])

            # always save the snapshot/prediction/forecast (this also feeds the
            # accuracy report + saved history, durable when Turso is configured)
            try:
                store.log_signal(sym, tf, analysis["price"], scored, analysis)
                store.log_prediction(
                    sym, tf, analysis["price"],
                    {"bias": scored["bias"], "confidence": scored["confidence"],
                     "volatility": analysis["volatility"]},
                    {"direction": "neutral", "confidence": 0},
                )
                if fc:
                    store.log_forecast(sym, tf, fc)
                saved += 1
            except Exception:
                pass

            # broadcast gate: configured + confident directional + once per candle
            if not alerts.telegram_configured():
                continue
            if scored["bias"] not in ("up", "down") or scored["confidence"] < min_conf or not plan:
                skipped += 1
                continue
            candle_open = int(data[-1]["time"])
            if not force and not store.mark_broadcast(sym, tf, candle_open):
                skipped += 1  # already sent this candle
                continue

            try:
                tcast = trendcast.project(data, tf_sec)
            except Exception:
                tcast = None
            try:
                bw = timing.best_window(data)
            except Exception:
                bw = None

            caption = build_message(asset["name"], tf, scored, analysis, plan, fc,
                                    tcast, bw, candle_open, tf_sec)
            png = None
            try:
                png = chartimg.render(
                    data, plan, fc,
                    title=f"{asset['name']} · {tf} · {scored['bias'].upper()}",
                    subtitle=f"confidence {scored['confidence']}%",
                )
            except Exception:
                png = None

            ok = alerts.send_telegram_photo(caption, png) if png else alerts.send_telegram(caption)
            if ok:
                sent += 1
                posted.append(sym)
            else:
                errors += 1
        except Exception:
            errors += 1

    return {"sent": sent, "skipped": skipped, "saved": saved, "errors": errors,
            "posted": posted, "min_confidence": min_conf}
