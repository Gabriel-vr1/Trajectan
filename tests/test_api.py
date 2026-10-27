from fastapi.testclient import TestClient
from trajectan.api import app


def test_end_to_end_api(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///" + str(tmp_path / "api.db"))
    with TestClient(app) as client:
        assert client.get("/api/health").json()["status"] == "degraded"
        data = client.get("/api/matches/26").json()
        last = data["total"]
        s = client.get("/api/matches/26/states/200").json()["state"]
        assert s["sequence"] == 200
        assert client.get("/api/matches/26/states/99999").status_code == 404
        f = client.get(f"/api/matches/26/forecasts/{last}").json()
        assert sum(f["probabilities"].values()) == 1
        recap = client.get("/api/matches/26/recap/200").json()
        assert recap["validation"]["valid"]
        assert all(e["sequence"] <= 200 for e in recap["moments"])
        assert (
            client.post(
                "/api/matches/26/scenarios",
                json={"sequence": 200, "action": "goal", "category": "tactical"},
            ).status_code
            == 422
        )
        assert (
            client.post(
                "/api/matches/26/scenarios", json={"sequence": 200, "samples": 100000}
            ).status_code
            == 422
        )
        # Resume close to full time to avoid waiting through the whole SSE demo.
        stream = client.get(
            "/api/matches/26/stream", headers={"Last-Event-ID": str(last - 1)}
        ).text
        assert f"id: {last}" in stream and f"id: {last - 1}\n" not in stream
