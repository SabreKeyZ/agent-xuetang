from fastapi.testclient import TestClient

from claimdesk.web import app


def test_queue_cite_and_no_payout():
    client = TestClient(app)
    assert client.get("/api/health").json()["ok"] is True
    queue = client.get("/api/queue").json()["cases"]
    assert len(queue) >= 8
    case = next(c for c in queue if c["claim"]["fixture_id"] == "valid-low")
    assert case["citations"]
    cite = client.get("/api/cite", params={"ref": case["citations"][0]}).json()
    assert cite["ok"] is True
    paid = client.post("/api/execute", json={"case_id": case["case_id"], "confirm": True}).json()
    assert paid["executed"] is False
