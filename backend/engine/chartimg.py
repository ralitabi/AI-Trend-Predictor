"""Render a candlestick PNG for Telegram signals.

A self-contained matplotlib (Agg) drawing of the recent candles in the app's
dark theme, with the entry/stop/target lines and the projected next candle
overlaid — so a signal in the group carries the picture, not just numbers.
Best-effort: callers fall back to a text message if this raises.
"""
import io

import matplotlib

matplotlib.use("Agg")  # headless — no display needed (serverless)
import matplotlib.pyplot as plt  # noqa: E402

_BG = "#0b0e14"
_GRID = "#1b2230"
_TEXT = "#aab3c5"
_UP = "#26a69a"
_DOWN = "#ef5350"


def _fmt(p: float) -> str:
    return f"{p:,.2f}" if p >= 100 else f"{p:.5f}"


def render(candles: list[dict], plan: dict | None, forecast: dict | None,
           title: str, subtitle: str = "", bars: int = 60) -> bytes:
    data = candles[-bars:]
    if len(data) < 5:
        raise ValueError("not enough candles to draw")

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=110)
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_BG)

    for i, c in enumerate(data):
        up = c["close"] >= c["open"]
        color = _UP if up else _DOWN
        ax.plot([i, i], [c["low"], c["high"]], color=color, linewidth=0.8, zorder=2)
        lo, hi = min(c["open"], c["close"]), max(c["open"], c["close"])
        ax.add_patch(plt.Rectangle((i - 0.3, lo), 0.6, max(hi - lo, (hi or 1) * 1e-6),
                                   facecolor=color, edgecolor=color, zorder=3))

    # projected next candle as a hollow dashed ghost just past the last bar
    if forecast:
        x = len(data)
        up = forecast["close"] >= forecast["open"]
        color = _UP if up else _DOWN
        ax.plot([x, x], [forecast["low"], forecast["high"]], color=color,
                linewidth=0.8, linestyle="--", alpha=0.8, zorder=2)
        lo, hi = min(forecast["open"], forecast["close"]), max(forecast["open"], forecast["close"])
        ax.add_patch(plt.Rectangle((x - 0.3, lo), 0.6, max(hi - lo, (hi or 1) * 1e-6),
                                   fill=False, edgecolor=color, linestyle="--", zorder=3))

    if plan:
        for key, col, lab in (("entry", _TEXT, "Entry"), ("stop", _DOWN, "Stop"),
                              ("target", _UP, "Target")):
            y = plan.get(key)
            if y:
                ax.axhline(y, color=col, linewidth=1.0, linestyle="--", alpha=0.9, zorder=1)
                ax.text(0, y, f" {lab} {_fmt(y)}", color=col, fontsize=8,
                        va="bottom", ha="left")

    ax.set_title(title, color="#e8edf5", fontsize=13, fontweight="bold", loc="left", pad=14)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, color=_TEXT, fontsize=9, va="bottom")
    ax.grid(True, color=_GRID, linewidth=0.6, alpha=0.6)
    ax.tick_params(colors=_TEXT, labelsize=8)
    for s in ax.spines.values():
        s.set_color(_GRID)
    ax.set_xticks([])
    ax.margins(x=0.02)

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", facecolor=_BG, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()
