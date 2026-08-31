"""第 3 周：对本仓库 docs/ 做关键字检索，引用格式 path:line。"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    path: str
    start_line: int
    end_line: int
    text: str

    @property
    def citation(self) -> str:
        return f"{self.path}:{self.start_line}"


def repo_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__).resolve()).resolve()
    for parent in [here, *here.parents]:
        if (parent / "docs" / "weeks").is_dir():
            return parent
    raise FileNotFoundError("找不到带 docs/weeks 的仓库根目录")


def iter_markdown(docs_dir: Path) -> list[Path]:
    return sorted(p for p in docs_dir.rglob("*.md") if p.is_file())


def chunk_file(path: Path, repo: Path) -> list[Chunk]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rel = path.relative_to(repo).as_posix()
    chunks: list[Chunk] = []
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
    return [c for c in chunks if c.text.strip()]


def build_corpus(repo: Path | None = None) -> list[Chunk]:
    root = repo or repo_root()
    docs = root / "docs"
    if not docs.is_dir():
        return []
    chunks: list[Chunk] = []
    for path in iter_markdown(docs):
        chunks.extend(chunk_file(path, root))
    return chunks


_TOKEN = re.compile(r"[A-Za-z]{2,}|\d+|[一-龥]{2,}")


def tokenize(text: str) -> list[str]:
    raw = [m.group(0).lower() for m in _TOKEN.finditer(text)]
    extra: list[str] = []
    for tok in raw:
        if re.fullmatch(r"[一-龥]{2,}", tok) and len(tok) >= 3:
            extra.extend(tok[i : i + 2] for i in range(len(tok) - 1))
    return raw + extra


def score(query: str, chunk: Chunk) -> int:
    q_tokens = set(tokenize(query))
    if not q_tokens:
        return 0
    blob = chunk.text.lower()
    path = chunk.path.lower()
    points = 0
    for tok in q_tokens:
        if tok in blob:
            points += 2 if len(tok) >= 3 else 1
        if tok in path:
            points += 4
    for piece in re.findall(r"[一-龥]{2,}", query):
        if piece in chunk.text:
            points += 3
    for piece in re.findall(r"[A-Za-z]{3,}", query):
        if piece.lower() in blob:
            points += 3
        if piece.lower() in path:
            points += 5
    return points


def retrieve(query: str, chunks: list[Chunk], k: int = 4) -> list[tuple[int, Chunk]]:
    ranked = [(score(query, c), c) for c in chunks]
    ranked = [pair for pair in ranked if pair[0] > 0]
    ranked.sort(key=lambda pair: (-pair[0], pair[1].path, pair[1].start_line))
    return ranked[:k]


def retrieve_sqlite(query: str, chunks: list[Chunk], k: int = 4) -> list[tuple[int, Chunk]]:
    """可选路径：用 sqlite FTS5。不可用时退回纯 Python。"""
    try:
        conn = sqlite3.connect(":memory:")
        conn.execute(
            "CREATE VIRTUAL TABLE docs USING fts5(path, start_line, text)"
        )
        for c in chunks:
            conn.execute(
                "INSERT INTO docs VALUES (?, ?, ?)",
                (c.path, str(c.start_line), c.text),
            )
        tokens = tokenize(query)
        if not tokens:
            return []
        match = " OR ".join(tokens)
        rows = conn.execute(
            "SELECT path, start_line, text, bm25(docs) FROM docs WHERE docs MATCH ? LIMIT ?",
            (match, k),
        ).fetchall()
        conn.close()
    except sqlite3.OperationalError:
        return retrieve(query, chunks, k=k)
    out: list[tuple[int, Chunk]] = []
    by_key = {(c.path, c.start_line): c for c in chunks}
    for path, start, _text, rank in rows:
        chunk = by_key.get((path, int(start)))
        if chunk:
            out.append((int(-rank * 10) if rank else 1, chunk))
    return out or retrieve(query, chunks, k=k)


def format_hits(hits: list[tuple[int, Chunk]]) -> str:
    if not hits:
        return json.dumps({"hits": []}, ensure_ascii=False)
    lines = []
    for points, chunk in hits:
        lines.append(f"[hit] {chunk.citation}  score={points}")
        quote = chunk.text.splitlines()[0][:80]
        lines.append(f"[quote] {quote}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--k", type=int, default=4)
    parser.add_argument("--sqlite", action="store_true")
    parser.add_argument("--docs", default="")
    args = parser.parse_args(argv)

    if args.docs:
        root = Path(args.docs).resolve()
        if (root / "docs").is_dir():
            chunks = build_corpus(root)
        else:
            chunks = []
            fake_repo = root
            for path in iter_markdown(root):
                chunks.extend(chunk_file(path, fake_repo))
    else:
        chunks = build_corpus()

    if not chunks:
        print(json.dumps({"hits": []}, ensure_ascii=False))
        return 1

    hits = retrieve_sqlite(args.query, chunks, k=args.k) if args.sqlite else retrieve(
        args.query, chunks, k=args.k
    )
    print(format_hits(hits))
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
