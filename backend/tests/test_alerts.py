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


def test_chat_for_routes_by_category(monkeypatch):
    for v in ("TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_CRYPTO", "TELEGRAM_CHAT_FOREX",
              "TELEGRAM_CHAT_COMMODITY", "TELEGRAM_CHAT_INDEX", "TELEGRAM_CHAT_STOCK"):
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100default")
    monkeypatch.setenv("TELEGRAM_CHAT_CRYPTO", "-100crypto")
    monkeypatch.setenv("TELEGRAM_CHAT_FOREX", "-100forex")
    # category with its own group routes there…
    assert alerts.chat_for("crypto") == "-100crypto"
    assert alerts.chat_for("forex") == "-100forex"
    # …a category without one falls back to the default group
    assert alerts.chat_for("stock") == "-100default"
    assert alerts.chat_for(None) == "-100default"


def test_chat_for_no_default_returns_none(monkeypatch):
    for v in ("TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_CRYPTO", "TELEGRAM_CHAT_FOREX",
              "TELEGRAM_CHAT_COMMODITY", "TELEGRAM_CHAT_INDEX", "TELEGRAM_CHAT_STOCK"):
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setenv("TELEGRAM_CHAT_INDEX", "-100idx")
    assert alerts.chat_for("index") == "-100idx"
    assert alerts.chat_for("crypto") == "-100idx"  # only-configured group is the fallback
    assert alerts.chat_for("stock") == "-100idx"
