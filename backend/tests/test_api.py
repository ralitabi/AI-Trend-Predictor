from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health_reports_db_and_counts():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "durable" in body
    assert isinstance(body["counts"], dict)
    assert "signals" in body["counts"]


def test_signals_history_endpoint():
    r = client.get("/signals/BTCUSDT?tf=1h&limit=5")
    assert r.status_code == 200
    assert r.json()["symbol"] == "BTCUSDT"
    assert isinstance(r.json()["signals"], list)


def test_signals_unknown_symbol_404():
    assert client.get("/signals/NOPE").status_code == 404


def test_snapshot_guard_when_secret_set(monkeypatch):
    # with CRON_SECRET set, an unauthenticated call is rejected (no network hit)
    monkeypatch.setattr(main, "CRON_SECRET", "topsecret")
    assert client.get("/snapshot?tf=1h").status_code == 401
    assert client.get("/snapshot?tf=1h&secret=wrong").status_code == 401
