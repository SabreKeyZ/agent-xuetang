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


def test_inbox_student_ui_hides_operator_tokens():
    client = TestClient(app)
    html = client.get("/").text
    assert "不是青绿" not in html
    assert "td-toast" in html
    assert "wait_human_confirm" in html
    assert 'next_action === "wait_human_confirm"' in html
    assert '["wait_human_confirm", "draft_only"]' not in html
    assert "idempotency_key" not in html.split("<script>", 1)[0]
    assert "confirm_required" not in html.split("<script>", 1)[0]
    assert "td-quote" in html
    assert "slaMinutes" in html
    assert "padStart" not in html


def test_execute_writes_audit_without_paying():
    client = TestClient(app)
    queue = client.get("/api/queue").json()
    case = next(c for c in queue["cases"] if c["ticket"]["fixture_id"] == "happy-quality")
    assert case["next_action"] == "wait_human_confirm"
    before = len(case.get("audit") or [])
    exec_out = client.post("/api/execute", json={"case_id": case["case_id"], "confirm": True}).json()
    assert exec_out["executed"] is False
    detail = client.get(f"/api/case/{case['case_id']}").json()
    assert any(a.get("action") == "execute_clicked" for a in detail.get("audit") or [])
    assert len(detail.get("audit") or []) >= before


def test_over_200_is_draft_only_not_todo():
    client = TestClient(app)
    queue = client.get("/api/queue").json()
    case = next(c for c in queue["cases"] if c["ticket"]["id"] == "T-1401")
    assert case["next_action"] == "draft_only"
    assert case["refused"] is True


def test_inbox_page_and_stylesheet():
    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    html = page.text
    assert "ticketdesk.css" in html
    assert "td-balloon" in html
    assert "td-dock" in html
    assert "td-cusbox" in html
    assert "td-l2box" in html
    assert "对客" in html
    assert "对内" in html
    assert "#0a0a0a" not in html
    css = client.get("/static/ticketdesk.css")
    assert css.status_code == 200
    body = css.text.lower()
    assert "#f4f6f8" in body
    assert "#1f8ded" in body
    assert "#1f8a70" not in body
    assert "background:#000" not in body.replace(" ", "")
