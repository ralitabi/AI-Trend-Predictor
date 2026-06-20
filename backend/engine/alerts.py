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


def channels() -> list[str]:
    """Which relay channels are currently configured."""
    out = []
    if telegram_configured():
        out.append("telegram")
    if os.environ.get("DISCORD_WEBHOOK_URL"):
        out.append("discord")
    return out


def telegram_configured() -> bool:
    return bool(os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"))


def send_telegram(text: str) -> bool:
    """Plain-text message to the configured Telegram chat. Returns success."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
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


def send_telegram_photo(caption: str, png: bytes) -> bool:
    """Photo (PNG bytes) with a caption to the configured Telegram chat."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
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
