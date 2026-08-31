from fastapi.testclient import TestClient

from askhall.web import app


def test_cite_returns_docs_snippet():
    client = TestClient(app)
    ref = "docs/weeks/03-memory-rag.md:5"
    data = client.get("/api/cite", params={"ref": ref}).json()
    assert data["ok"] is True
    assert data["path"].startswith("docs/")
    assert "短记忆" in data["snippet"] or "长记忆" in data["snippet"] or "记忆" in data["snippet"]


def test_cite_rejects_escape():
    client = TestClient(app)
    data = client.get("/api/cite", params={"ref": "../.env:1"}).json()
    assert data["ok"] is False
