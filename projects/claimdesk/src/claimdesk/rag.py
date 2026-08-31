from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from claimdesk.clock import parse_day
from claimdesk.config import project_root

_TOKEN = re.compile(r"[A-Za-z]{2,}|\d+|[一-龥]{2,}|条款\s*\d+\.\d+")


@dataclass
class Chunk:
    path: str
    start_line: int
    end_line: int
    text: str
    effective_from: date | None = None
    effective_to: date | None = None
    version: str = ""
    clause_id: str = ""

    @property
    def citation(self) -> str:
        if self.clause_id:
            return f"{self.clause_id} · {self.path}:{self.start_line}"
        return f"{self.path}:{self.start_line}"

    @property
    def path_line(self) -> str:
        return f"{self.path}:{self.start_line}"


@dataclass
class Hit:
    score: int
    chunk: Chunk

    def as_dict(self) -> dict:
        return {
            "citation": self.chunk.citation,
            "path_line": self.chunk.path_line,
            "clause_id": self.chunk.clause_id,
            "version": self.chunk.version,
            "quote": self.chunk.text.strip()[:400],
            "score": self.score,
        }


@dataclass
class Corpus:
    root: Path
    chunks: list[Chunk] = field(default_factory=list)


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _TOKEN.finditer(text)]


def _meta(lines: list[str]) -> tuple[date | None, date | None, str]:
    ef = et = None
    version = ""
    for line in lines[:12]:
        if line.startswith("生效:"):
            raw = line.split(":", 1)[1].strip()
            ef = date.fromisoformat(raw[:10]) if raw else None
        elif line.startswith("失效:"):
            raw = line.split(":", 1)[1].strip()
            et = date.fromisoformat(raw[:10]) if raw else None
        elif line.startswith("版本:"):
            version = line.split(":", 1)[1].strip()
    return ef, et, version


def _clause_id(text: str) -> str:
    m = re.search(r"条款\s*(\d+\.\d+)", text)
    return f"条款 {m.group(1)}" if m else ""


def load_corpus(root: Path | None = None) -> Corpus:
    base = root or project_root()
    chunks: list[Chunk] = []
    for path in sorted((base / "docs" / "policy").rglob("*.md")):
        rel = path.relative_to(base).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        meta = _meta(lines)
        buf: list[str] = []
        start = 1
        for idx, line in enumerate(lines, start=1):
            if line.strip() == "":
                if buf:
                    text = "\n".join(buf)
                    chunks.append(Chunk(rel, start, idx - 1, text, *meta, _clause_id(text)))
                    buf = []
                start = idx + 1
                continue
            if not buf:
                start = idx
            buf.append(line)
        if buf:
            text = "\n".join(buf)
            chunks.append(Chunk(rel, start, start + len(buf) - 1, text, *meta, _clause_id(text)))
    return Corpus(root=base, chunks=[c for c in chunks if c.text.strip()])


def _in_force(chunk: Chunk, at: str | None) -> bool:
    if not at:
        return True
    day = parse_day(at)
    if chunk.effective_from and day < chunk.effective_from:
        return False
    if chunk.effective_to and day > chunk.effective_to:
        return False
    return True


def retrieve(query: str, at: str | None = None, k: int = 5) -> list[Hit]:
    corp = load_corpus()
    ranked: list[Hit] = []
    for c in corp.chunks:
        if not _in_force(c, at):
            continue
        points = 0
        blob = c.text.lower()
        for tok in set(tokenize(query)):
            if tok in blob:
                points += 3 if len(tok) >= 3 else 1
        if c.clause_id and c.clause_id.replace(" ", "") in query.replace(" ", ""):
            points += 8
        if points:
            ranked.append(Hit(points, c))
    ranked.sort(key=lambda h: (-h.score, h.chunk.path, h.chunk.start_line))
    return ranked[:k]


def citation_exists(citation: str, root: Path | None = None) -> bool:
    path_line = citation
    if " · " in citation:
        path_line = citation.split(" · ", 1)[1]
    if ":" not in path_line:
        return False
    path, _, line = path_line.rpartition(":")
    if not line.isdigit():
        return False
    base = root or project_root()
    target = base / path
    if not target.is_file():
        return False
    n = len(target.read_text(encoding="utf-8").splitlines())
    return 1 <= int(line) <= max(n, 1)


def read_snippet(citation: str, root: Path | None = None) -> dict:
    path_line = citation.split(" · ", 1)[1] if " · " in citation else citation
    if not citation_exists(citation, root):
        return {"ok": False, "ref": citation, "error": "引用对不上磁盘"}
    path, _, line_s = path_line.rpartition(":")
    if ".." in path.split("/") or not path.startswith("docs/policy/"):
        return {"ok": False, "ref": citation, "error": "只允许条款文件"}
    base = root or project_root()
    target = (base / path).resolve()
    if base.resolve() not in target.parents:
        return {"ok": False, "ref": citation, "error": "路径越界"}
    lines = target.read_text(encoding="utf-8").splitlines()
    line = int(line_s)
    start = max(1, line - 2)
    end = min(len(lines), line + 10)
    snippet = "\n".join(f"{i}| {lines[i - 1]}" for i in range(start, end + 1))
    return {"ok": True, "ref": citation, "path": path, "line": line, "snippet": snippet}
