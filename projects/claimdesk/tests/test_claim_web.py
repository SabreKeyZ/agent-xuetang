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


def test_pass_case_page_enables_payout_and_hides_keys():
    client = TestClient(app)
    html = client.get("/").text
    assert "paintActs" in html
    assert "canPay" in html
    assert "data-case" in html
    assert "idempotency_key" not in html.split("<script>", 1)[0]
    assert "confirm_required" not in html
    assert "cd-toast" in html
    queue = client.get("/api/queue").json()["cases"]
    case = next(c for c in queue if c["claim"]["fixture_id"] == "valid-low")
    assert case["decision"]["recommendation"] == "通过"
    paid = client.post("/api/execute", json={"case_id": case["case_id"], "confirm": True}).json()
    assert paid["executed"] is False
    assert paid["payment"]["status"] == "confirm_required"


def test_pass_click_keeps_payout_gated_on_server_rec():
    client = TestClient(app)
    html = client.get("/").text
    assert "canPay(serverRec" in html
    assert "本机改选不会改服务端结论" in html
    queue = client.get("/api/queue").json()["cases"]
    refused = next(c for c in queue if c["claim"]["id"] == "C-2002")
    assert refused["decision"]["recommendation"] == "拒赔"
    paid = client.post("/api/execute", json={"case_id": refused["case_id"], "confirm": True}).json()
    assert paid["executed"] is False
    assert paid["payment"]["status"] == "confirm_required"


def test_payments_page_and_stylesheet():
    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    html = page.text
    assert "claimdesk.css" in html
    assert "<table" in html.lower()
    assert "cd-yen" in html
    assert "cd-math" in html
    assert "状态机" in html
    assert "td-balloon" not in html
    css = client.get("/static/claimdesk.css")
    assert css.status_code == 200
    body = css.text.lower()
    assert "#f6f9fc" in body
    assert "#635bff" in body
    assert "tabular-nums" in body
