from engine import alerts


def test_no_channels_is_a_safe_noop(monkeypatch):
    for k in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "DISCORD_WEBHOOK_URL"):
        monkeypatch.delenv(k, raising=False)
    assert alerts.channels() == []
    result = alerts.notify("Title", "body")
    assert result == {"sent": [], "errors": [], "configured": []}


def test_channels_reports_configured(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "y")
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    assert alerts.channels() == ["telegram"]
