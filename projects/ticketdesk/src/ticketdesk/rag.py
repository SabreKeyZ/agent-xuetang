from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from ticketdesk.clock import parse_dt
from ticketdesk.config import project_root

_TOKEN = re.compile(r"[A-Za-z]{2,}|\d+|[一-龥]{2,}")


@dataclass
class Chunk:
    path: str
    start_line: int
    end_line: int
    text: str
    effective_from: date | None = None
    effective_to: date | None = None
    priority: str = "日常"
    doc_id: str = ""

    @property
    def citation(self) -> str:
        return f"{self.path}:{self.start_line}"


@dataclass
class Hit:
    score: int
    chunk: Chunk

    def as_dict(self) -> dict:
        return {
            "citation": self.chunk.citation,
            "path": self.chunk.path,
            "start_line": self.chunk.start_line,
            "end_line": self.chunk.end_line,
            "quote": self.chunk.text.strip()[:400],
            "score": self.score,
            "priority": self.chunk.priority,
            "doc_id": self.chunk.doc_id,
        }


@dataclass
class Corpus:
    root: Path
    chunks: list[Chunk] = field(default_factory=list)


def tokenize(text: str) -> list[str]:
    raw = [m.group(0).lower() for m in _TOKEN.finditer(text)]
    extra: list[str] = []
    for tok in raw:
        if re.fullmatch(r"[一-龥]{2,}", tok) and len(tok) >= 3:
            extra.extend(tok[i : i + 2] for i in range(len(tok) - 1))
    return raw + extra


def _parse_meta(lines: list[str]) -> tuple[date | None, date | None, str, str]:
    effective_from = None
    effective_to = None
    priority = "日常"
    doc_id = ""
    for line in lines[:12]:
        if line.startswith("生效:"):
            effective_from = _parse_date(line.split(":", 1)[1])
        elif line.startswith("失效:"):
            effective_to = _parse_date(line.split(":", 1)[1])
        elif line.startswith("优先级:"):
            priority = line.split(":", 1)[1].strip() or "日常"
        elif line.startswith("文档编号:"):
            doc_id = line.split(":", 1)[1].strip()
    return effective_from, effective_to, priority, doc_id


def _parse_date(raw: str) -> date | None:
    text = raw.strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def load_corpus(root: Path | None = None) -> Corpus:
    base = root or project_root()
    docs = base / "docs" / "policy"
    chunks: list[Chunk] = []
    for path in sorted(docs.rglob("*.md")):
        rel = path.relative_to(base).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        meta = _parse_meta(lines)
        buf: list[str] = []
        start = 1
        for idx, line in enumerate(lines, start=1):
            if line.strip() == "":
                if buf:
                    chunks.append(Chunk(rel, start, idx - 1, "\n".join(buf), *meta))
                    buf = []
                start = idx + 1
                continue
            if not buf:
                start = idx
            buf.append(line)
            if len(buf) >= 80:
                chunks.append(Chunk(rel, start, idx, "\n".join(buf), *meta))
                buf = []
                start = idx + 1
        if buf:
            chunks.append(Chunk(rel, start, start + len(buf) - 1, "\n".join(buf), *meta))
    return Corpus(root=base, chunks=[c for c in chunks if c.text.strip()])


def _in_force(chunk: Chunk, at: str | None) -> bool:
    if not at:
        return True
    day = parse_dt(at).date()
    if chunk.effective_from and day < chunk.effective_from:
        return False
    if chunk.effective_to and day > chunk.effective_to:
        return False
    return True


def _score(query: str, chunk: Chunk) -> int:
    points = 0
    blob = chunk.text.lower()
    path = chunk.path.lower()
    for tok in set(tokenize(query)):
        if tok in blob:
            points += 2 if len(tok) >= 3 else 1
        if tok in path:
            points += 4
    for piece in re.findall(r"[一-龥]{2,}", query):
        if piece in chunk.text:
            points += 3
    if chunk.priority == "活动":
        points += 2
    return points


def retrieve(
    query: str,
    corpus: Corpus | None = None,
    k: int = 4,
    at: str | None = None,
    prefer_promo: bool = False,
) -> list[Hit]:
    corp = corpus or load_corpus()
    ranked = [Hit(_score(query, c), c) for c in corp.chunks if _in_force(c, at)]
    ranked = [h for h in ranked if h.score > 0]
    ranked.sort(
        key=lambda h: (
            -(2 if prefer_promo and h.chunk.priority == "活动" else 0),
            -h.score,
            0 if h.chunk.priority == "活动" else 1,
            h.chunk.path,
            h.chunk.start_line,
        )
    )
    top = ranked[:k]
    return top


def citation_exists(citation: str, root: Path | None = None) -> bool:
    if ":" not in citation:
        return False
    path, _, line = citation.rpartition(":")
    if not line.isdigit():
        return False
    base = root or project_root()
    target = base / path
    if not target.is_file():
        return False
    n = len(target.read_text(encoding="utf-8").splitlines())
    return 1 <= int(line) <= max(n, 1)


def read_snippet(citation: str, root: Path | None = None) -> dict:
    if not citation_exists(citation, root):
        return {"ok": False, "ref": citation, "error": "引用对不上磁盘"}
    path, _, line_s = citation.rpartition(":")
    if ".." in path.split("/") or path.startswith("/"):
        return {"ok": False, "ref": citation, "error": "路径不合法"}
    if not path.startswith("docs/policy/") and not path.startswith("fixtures/"):
        return {"ok": False, "ref": citation, "error": "只允许政策或夹具路径"}
    base = root or project_root()
    target = (base / path).resolve()
    if base.resolve() not in target.parents and target != base.resolve():
        return {"ok": False, "ref": citation, "error": "路径越界"}
    lines = target.read_text(encoding="utf-8").splitlines()
    line = int(line_s)
    start = max(1, line - 2)
    end = min(len(lines), line + 10)
    snippet = "\n".join(f"{i}| {lines[i - 1]}" for i in range(start, end + 1))
    return {"ok": True, "ref": citation, "path": path, "line": line, "snippet": snippet}
