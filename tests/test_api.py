import os

from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "modelo" in data


def test_telegram():
    r = client.post("/telegram", json={"update_id": 1})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_chat_validation_422():
    r = client.post("/chat", json={"user_id": "u1"})
    assert r.status_code == 422