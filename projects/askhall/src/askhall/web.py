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
        "roles": ["planner", "tutor", "examiner"],
    }


@app.get("/api/cite")
def cite(ref: str) -> dict:
    """点引用芯片时返回教材片段。只读 docs/，拒绝路径穿越。"""
    from askhall.config import docs_root
    from askhall.rag import citation_exists

    if not citation_exists(ref):
        return {"ok": False, "ref": ref, "error": "引用对不上磁盘"}
    path, _, line_s = ref.rpartition(":")
    if ".." in path.split("/") or path.startswith("/") or not path.startswith("docs/"):
        return {"ok": False, "ref": ref, "error": "只允许 docs/ 下的相对路径"}
    root = docs_root()
    target = (root / path).resolve()
    if root.resolve() not in target.parents and target != root.resolve():
        return {"ok": False, "ref": ref, "error": "路径越界"}
    lines = target.read_text(encoding="utf-8").splitlines()
    line = int(line_s)
    start = max(1, line - 2)
    end = min(len(lines), line + 10)
    snippet = "\n".join(f"{i}| {lines[i - 1]}" for i in range(start, end + 1))
    return {"ok": True, "ref": ref, "path": path, "line": line, "snippet": snippet}


@app.post("/api/ask")
def ask(body: AskBody) -> dict:
    return _supervisor.handle(body.message, pending_quiz=body.pending_quiz)
