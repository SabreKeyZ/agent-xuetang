from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from askhall.config import docs_root

_TOKEN = re.compile(r"[A-Za-z]{2,}|\d+|[一-龥]{2,}")


@dataclass
class Chunk:
    path: str
    start_line: int
    end_line: int
    text: str

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
        }


@dataclass
class Corpus:
    root: Path
    chunks: list[Chunk] = field(default_factory=list)


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _TOKEN.finditer(text)]


def load_corpus(root: Path | None = None) -> Corpus:
    base = root or docs_root()
    docs = base / "docs"
    chunks: list[Chunk] = []
    for path in sorted(docs.rglob("*.md")):
        rel = path.relative_to(base).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        buf: list[str] = []
        start = 1
        for idx, line in enumerate(lines, start=1):
            if line.strip() == "":
                if buf:
                    chunks.append(Chunk(rel, start, idx - 1, "\n".join(buf)))
                    buf = []
                start = idx + 1
                continue
            if not buf:
                start = idx
            buf.append(line)
            if len(buf) >= 80:
                chunks.append(Chunk(rel, start, idx, "\n".join(buf)))
                buf = []
                start = idx + 1
        if buf:
            chunks.append(Chunk(rel, start, start + len(buf) - 1, "\n".join(buf)))
    return Corpus(root=base, chunks=[c for c in chunks if c.text.strip()])


def _score(query: str, chunk: Chunk) -> int:
    points = 0
    blob = chunk.text.lower()
    for tok in set(tokenize(query)):
        if tok in blob:
            points += 2 if len(tok) >= 3 else 1
    for piece in re.findall(r"[一-龥]{2,}", query):
        if piece in chunk.text:
            points += 3
    for piece in re.findall(r"[A-Za-z]{3,}", query):
        if piece.lower() in blob:
            points += 2
    return points


def retrieve(query: str, corpus: Corpus | None = None, k: int = 4) -> list[Hit]:
    corp = corpus or load_corpus()
    ranked = [Hit(_score(query, c), c) for c in corp.chunks]
    ranked = [h for h in ranked if h.score > 0]
    ranked.sort(key=lambda h: (-h.score, h.chunk.path, h.chunk.start_line))
    top = ranked[:k]
    # 查询里很长的专有名词若从未出现在语料中，宁可空，也不用「什么是」这种停用词硬凑命中。
    rare = [t for t in tokenize(query) if len(t) >= 10]
    if rare and top:
        blob = "\n".join(h.chunk.text.lower() for h in top)
        if not any(r in blob for r in rare):
            return []
    return top


def citation_exists(citation: str, root: Path | None = None) -> bool:
    if ":" not in citation:
        return False
    path, _, line = citation.rpartition(":")
    if not line.isdigit():
        return False
    base = root or docs_root()
    target = base / path
    if not target.is_file():
        return False
    n = len(target.read_text(encoding="utf-8").splitlines())
    return 1 <= int(line) <= max(n, 1)
