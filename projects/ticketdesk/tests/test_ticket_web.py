from fastapi.testclient import TestClient

from ticketdesk.web import app


def test_queue_and_cite():
    client = TestClient(app)
    health = client.get("/api/health").json()
    assert health["ok"] is True
    queue = client.get("/api/queue").json()
    assert len(queue["cases"]) >= 8
    case = next(c for c in queue["cases"] if c["ticket"]["fixture_id"] == "promo-overrides-sla")
    assert case["citations"]
    ref = case["citations"][0]
    cite = client.get("/api/cite", params={"ref": ref}).json()
    assert cite["ok"] is True
    exec_out = client.post("/api/execute", json={"case_id": case["case_id"], "confirm": True}).json()
    assert exec_out["executed"] is False


def test_inbox_page_and_stylesheet():
    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    html = page.text
    assert "ticketdesk.css" in html
    assert "td-balloon" in html
    assert "td-dock" in html
    assert "#0a0a0a" not in html
    css = client.get("/static/ticketdesk.css")
    assert css.status_code == 200
    body = css.text.lower()
    assert "#f4f6f8" in body
    assert "#1f8a70" in body
    assert "background:#000" not in body.replace(" ", "")
