from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from askhall.agents.supervisor import Supervisor
from askhall.config import has_llm_key, load_dotenv

load_dotenv()
app = FastAPI(title="问学堂 AskHall", version="0.1.0")
_supervisor = Supervisor()
_STATIC = Path(__file__).resolve().parent / "static" / "index.html"


class AskBody(BaseModel):
    message: str = Field(default="", max_length=2000)
    pending_quiz: dict | None = None


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC, media_type="text/html; charset=utf-8")


@app.get("/api/health")
def health() -> dict:
    from askhall.config import docs_root

    return {
        "ok": True,
        "llm": has_llm_key(),
        "docs": str(docs_root()),
    }


@app.post("/api/ask")
def ask(body: AskBody) -> dict:
    return _supervisor.handle(body.message, pending_quiz=body.pending_quiz)
