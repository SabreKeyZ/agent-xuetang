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


def test_payments_page_and_stylesheet():
    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    html = page.text
    assert "claimdesk.css" in html
    assert "<table" in html.lower()
    assert "cd-yen" in html
    assert "td-balloon" not in html
    css = client.get("/static/claimdesk.css")
    assert css.status_code == 200
    body = css.text.lower()
    assert "#f6f9fc" in body
    assert "#635bff" in body
    assert "tabular-nums" in body
