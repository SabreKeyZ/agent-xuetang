from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from claimdesk.agents.supervisor import Supervisor
from claimdesk.config import has_llm_key, load_dotenv
from claimdesk.rag import read_snippet
from claimdesk.tools.payment import payout

load_dotenv()
app = FastAPI(title="青途保理赔台", version="0.1.0")
_supervisor = Supervisor()
_STATIC = Path(__file__).resolve().parent / "static"


class ExecBody(BaseModel):
    case_id: str = Field(min_length=1)
    confirm: bool = False


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC / "index.html", media_type="text/html; charset=utf-8")


@app.get("/static/claimdesk.css")
def stylesheet() -> FileResponse:
    return FileResponse(_STATIC / "claimdesk.css", media_type="text/css")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "llm": has_llm_key(), "product": "claimdesk", "roles": ["docs_check", "clause", "adjudicator"]}


@app.get("/api/queue")
def queue() -> dict:
    for claim in _supervisor.catalog():
        if claim.id not in _supervisor.store.by_case:
            _supervisor.process(claim)
    return {"cases": list(_supervisor.store.by_case.values())}


@app.get("/api/case/{case_id}")
def case_detail(case_id: str) -> dict:
    if case_id not in _supervisor.store.by_case:
        claim = next((c for c in _supervisor.catalog() if c.id == case_id), None)
        if claim is None:
            return {"ok": False, "error": "案件不在队列"}
        _supervisor.process(claim)
    return {"ok": True, **_supervisor.store.by_case[case_id]}


@app.get("/api/cite")
def cite(ref: str) -> dict:
    return read_snippet(ref)


@app.post("/api/execute")
def execute(body: ExecBody) -> dict:
    if body.case_id not in _supervisor.store.by_case:
        return {"ok": False, "executed": False, "error": "无草稿"}
    case = _supervisor.store.by_case[body.case_id]
    probe = payout(case["claim"].get("amount_yuan") or 0, case["idempotency_key"], confirm=body.confirm)
    case.setdefault("audit", []).append({"role": "human", "action": "payout_clicked", "detail": probe["status"]})
    case["executed"] = False
    return {"ok": False, "executed": False, "payment": probe, "message": "演示模式不打款。"}
