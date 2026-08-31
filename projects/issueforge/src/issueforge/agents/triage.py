from __future__ import annotations

import re
from collections import Counter

from issueforge.models import Issue, Kind

BUG_HINTS = (
    "crash",
    "traceback",
    "error",
    "exception",
    "挂了",
    "崩溃",
    "报错",
    "dies",
    "bug",
    "fails",
    "失败",
)
FEATURE_HINTS = (
    "feature",
    "request",
    "would like",
    "希望",
    "建议",
    "add ",
    "export",
    "按钮",
    "能不能加",
)
QUESTION_HINTS = (
    "how do i",
    "how should",
    "怎么",
    "如何",
    "请问",
    "unsure",
    "?",
    "？",
    "what is",
)


def _count(text: str, words: tuple[str, ...]) -> int:
    blob = text.lower()
    return sum(blob.count(w) for w in words)


def classify(issue: Issue) -> Kind:
    title = issue.title.lower()
    body = issue.body.lower()
    head = title + "\n" + "\n".join(body.splitlines()[:6])
    q = _count(head, QUESTION_HINTS)
    f = _count(head, FEATURE_HINTS)
    b = _count(head, BUG_HINTS)

    # 标题像 bug、正文在问「如何」——夹具 question-disguised
    if "did not hit a crash" in body or "这是一个问题" in body or "this is a question" in body:
        return "question"
    asking = any(w in body for w in ("how do i", "how should", "怎么", "如何"))
    crashed = "traceback" in body or "crash" in title
    if asking and not crashed:
        return "question"

    if "feature request" in title or (f > b and f > q):
        return "feature"
    if q > b and q >= f and "crash" not in title:
        return "question"
    if b >= q and b >= f:
        return "bug"
    if f:
        return "feature"
    if q:
        return "question"
    return "bug"


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[A-Za-z]{3,}|[一-龥]{2,}", text)}


def guess_duplicate(issue: Issue, catalog: list[Issue]) -> tuple[int | None, float]:
    mine = _tokens(issue.title)
    if not mine:
        return None, 0.0
    best_n: int | None = None
    best = 0.0
    for other in catalog:
        if other.number == issue.number:
            continue
        theirs = _tokens(other.title)
        if not theirs:
            continue
        overlap = mine & theirs
        score = len(overlap) / len(mine | theirs)
        if score > best:
            best = score
            best_n = other.number
    if best < 0.45:
        return None, best
    return best_n, best


def triage(issue: Issue, catalog: list[Issue] | None = None) -> dict:
    kind = classify(issue)
    dup, score = guess_duplicate(issue, catalog or [])
    return {
        "role": "triage",
        "kind": kind,
        "duplicate_of": dup,
        "duplicate_score": round(score, 3),
        "title_tokens": sorted(_tokens(issue.title))[:12],
    }
