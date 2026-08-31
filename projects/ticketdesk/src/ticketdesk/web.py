from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ticketdesk.agents.supervisor import Supervisor
from ticketdesk.config import has_llm_key, load_dotenv
from ticketdesk.rag import read_snippet
from ticketdesk.tools.payment import refund as refund_api

load_dotenv()
app = FastAPI(title="青匣记工单台", version="0.1.0")
_supervisor = Supervisor()
_STATIC = Path(__file__).resolve().parent / "static"


class ExecBody(BaseModel):
    case_id: str = Field(min_length=1)
    confirm: bool = False


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC / "index.html", media_type="text/html; charset=utf-8")


@app.get("/static/ticketdesk.css")
def stylesheet() -> FileResponse:
    return FileResponse(_STATIC / "ticketdesk.css", media_type="text/css")


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "llm": has_llm_key(),
        "product": "ticketdesk",
        "shop": "青匣记",
        "roles": ["classifier", "policy", "gate"],
    }


@app.get("/api/queue")
def queue() -> dict:
    cases = []
    # 每张夹具只处理一次；store 保证幂等
    for ticket in _supervisor.catalog():
        if ticket.id not in _supervisor.store.by_case:
            _supervisor.process(ticket)
        cases.append(_supervisor.store.by_case[ticket.id])
    return {"cases": cases}


@app.get("/api/case/{case_id}")
def case_detail(case_id: str) -> dict:
    if case_id not in _supervisor.store.by_case:
        ticket = next((t for t in _supervisor.catalog() if t.id == case_id), None)
        if ticket is None:
            return {"ok": False, "error": "案件不在队列"}
        _supervisor.process(ticket)
    return {"ok": True, **_supervisor.store.by_case[case_id]}


@app.get("/api/cite")
def cite(ref: str) -> dict:
    return read_snippet(ref)


@app.post("/api/execute")
def execute(body: ExecBody) -> dict:
    """人点执行的入口。演示仍拒绝打款，只写审计。"""
    if body.case_id not in _supervisor.store.by_case:
        return {"ok": False, "executed": False, "error": "案件未出草稿"}
    case = _supervisor.store.by_case[body.case_id]
    probe = refund_api(case["ticket"].get("refund_yuan") or 0, case["idempotency_key"], confirm=body.confirm)
    case.setdefault("audit", []).append(
        {
            "role": "human",
            "action": "execute_clicked",
            "detail": f"confirm={body.confirm} status={probe['status']}",
        }
    )
    case["executed"] = False
    return {"ok": False, "executed": False, "payment": probe, "message": "演示模式不打款。"}
