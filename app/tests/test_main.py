from fastapi.testclient import TestClient

from app.src.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "app" in r.json()


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_readyz_ready_by_default():
    # READY_AFTER_SECONDS defaults to 0, so readiness is immediate.
    r = client.get("/readyz")
    assert r.status_code == 200


def test_items():
    r = client.get("/api/items")
    assert r.status_code == 200
    assert len(r.json()["items"]) == 2


def test_metrics_exposes_prometheus():
    client.get("/")  # generate at least one metric
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text
