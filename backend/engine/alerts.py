"""Outbound alert relay — pushes a short message to Telegram and/or Discord.

The browser is the trigger (it watches the live signal bias and price and fires
the native notification), but fan-out to chat channels goes through here so the
bot token / webhook URL stay server-side instead of shipping to every client.

Every channel is optional and configured by env:
    TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID   → Telegram
    DISCORD_WEBHOOK_URL                      → Discord
With none set, notify() is a harmless no-op that reports nothing was sent.
"""
import os

import httpx


# Per-category routing: each asset class can post to its own group, e.g.
# TELEGRAM_CHAT_CRYPTO / _FOREX / _COMMODITY / _INDEX / _STOCK. Any class without
# its own group falls back to the single TELEGRAM_CHAT_ID.
_CLASS_ENV = {
    "crypto": "TELEGRAM_CHAT_CRYPTO",
    "forex": "TELEGRAM_CHAT_FOREX",
    "commodity": "TELEGRAM_CHAT_COMMODITY",
    "index": "TELEGRAM_CHAT_INDEX",
    "stock": "TELEGRAM_CHAT_STOCK",
}


def chat_for(asset_class: str | None) -> str | None:
    """Which chat a signal for this asset class goes to (its category group,
    else the single default group)."""
    if asset_class:
        specific = os.environ.get(_CLASS_ENV.get(asset_class, ""))
        if specific:
            return specific
    return _default_chat()


def _default_chat() -> str | None:
    return os.environ.get("TELEGRAM_CHAT_ID") or next(
        (os.environ[v] for v in _CLASS_ENV.values() if os.environ.get(v)), None)


def channels() -> list[str]:
    """Which relay channels are currently configured."""
    out = []
    if telegram_configured():
        out.append("telegram")
    if os.environ.get("DISCORD_WEBHOOK_URL"):
        out.append("discord")
    return out


def telegram_configured() -> bool:
    return bool(os.environ.get("TELEGRAM_BOT_TOKEN") and _default_chat())


def send_telegram(text: str, chat_id: str | None = None) -> bool:
    """Plain-text message to a Telegram chat (default group if none given)."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = chat_id or _default_chat()
    if not (token and chat):
        return False
    try:
        r = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": text, "disable_web_page_preview": True},
            timeout=15,
        )
        r.raise_for_status()
        return True
    except Exception:
        return False


def send_telegram_photo(caption: str, png: bytes, chat_id: str | None = None) -> bool:
    """Photo (PNG bytes) with a caption to a Telegram chat (default if none)."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = chat_id or _default_chat()
    if not (token and chat) or not png:
        return False
    try:
        r = httpx.post(
            f"https://api.telegram.org/bot{token}/sendPhoto",
            data={"chat_id": chat, "caption": caption[:1024]},
            files={"photo": ("chart.png", png, "image/png")},
            timeout=20,
        )
        r.raise_for_status()
        return True
    except Exception:
        return False


def notify(title: str, message: str = "") -> dict:
    """Relay a single alert. Returns which channels accepted it + any errors."""
    text = f"{title}\n{message}".strip() if message else title.strip()
    sent: list[str] = []
    errors: list[str] = []

    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    tg_chat = os.environ.get("TELEGRAM_CHAT_ID")
    if tg_token and tg_chat:
        try:
            r = httpx.post(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                json={"chat_id": tg_chat, "text": text, "disable_web_page_preview": True},
                timeout=8,
            )
            r.raise_for_status()
            sent.append("telegram")
        except Exception as e:
            errors.append(f"telegram: {type(e).__name__}")

    discord = os.environ.get("DISCORD_WEBHOOK_URL")
    if discord:
        try:
            r = httpx.post(discord, json={"content": text}, timeout=8)
            r.raise_for_status()
            sent.append("discord")
        except Exception as e:
            errors.append(f"discord: {type(e).__name__}")

    return {"sent": sent, "errors": errors, "configured": channels()}
