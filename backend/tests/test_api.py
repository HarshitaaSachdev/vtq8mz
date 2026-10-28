from fastapi.testclient import TestClient

from app.main import app, get_dataset
from tests.test_forecasts import make_dataset

app.dependency_overrides[get_dataset] = make_dataset
client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_series_decision_mode():
    body = client.get("/api/series", params={"start": "2026-01-10", "end": "2026-01-10"}).json()
    assert len(body["points"]) == 48
    noon = next(p for p in body["points"] if p["time"].startswith("2026-01-10T12:00"))
    assert noon["forecast"] == 9000
    assert body["metrics"]["mae"] == 1000


def test_series_rejects_dates_outside_january():
    response = client.get("/api/series", params={"start": "2025-06-01"})
    assert response.status_code == 422


def test_accuracy_by_horizon_returns_one_row_per_horizon():
    rows = client.get("/api/accuracy/by-horizon", params={"start": "2026-01-10", "end": "2026-01-10"}).json()
    assert rows[0]["horizon_hours"] == 0
    assert len(rows) == 14