from __future__ import annotations

import re

from askhall.llm import complete
from askhall.rag import Hit, retrieve

REFUSE_EMPTY = "拒绝批改：答案是空的。请先写一句，哪怕是「我不知道」。"


class Examiner:
    name = "examiner"

    def ask(self, topic: str, hits: list[Hit] | None = None) -> dict:
        hits = hits if hits is not None else retrieve(topic or "Agent 循环", k=3)
        question, answer_key, citation = _make_question(topic, hits)
        llm_q = None
        if hits:
            llm_q = complete(
                f"根据摘录出一道简答题，只要一问。摘录：\n{hits[0].chunk.text[:500]}",
                system="你是问学堂考试官。不要一次出多题。",
            )
        if llm_q:
            question = llm_q.strip().splitlines()[0]
        return {
            "role": self.name,
            "title": "一道检查题",
            "body": question,
            "answer_key": answer_key,
            "citations": [citation] if citation else [h.chunk.citation for h in hits[:1]],
            "mode": "llm" if llm_q else "extractive",
        }

    def grade(self, answer: str, answer_key: str, question: str = "") -> dict:
        return grade_answer(answer, answer_key, question)


def grade_answer(answer: str, answer_key: str, question: str = "") -> dict:
    text = (answer or "").strip()
    if not text:
        return {
            "role": "examiner",
            "title": "未批改",
            "body": REFUSE_EMPTY,
            "passed": False,
            "refused": True,
            "citations": [],
        }
    key_tokens = set(_tokens(answer_key + " " + question))
    ans_tokens = set(_tokens(text))
    overlap = key_tokens & ans_tokens
    passed = len(overlap) >= 1 and len(text) >= 4
    comment = (
        "能对上教材里的词，先记一笔通过。回去把引用那一段再读一遍。"
        if passed
        else "没对上关键词。打开引用再答一次，不要凭印象。"
    )
    return {
        "role": "examiner",
        "title": "批改",
        "body": comment,
        "passed": passed,
        "refused": False,
        "overlap": sorted(overlap)[:8],
        "citations": [],
    }


def _make_question(topic: str, hits: list[Hit]) -> tuple[str, str, str]:
    if not hits:
        return (
            "教材里暂时没有这段。请先自己打开 docs/weeks/01-what-is-an-agent.md，用一句话写出循环的三步。",
            "think act observe 思考 行动 观察",
            "docs/weeks/01-what-is-an-agent.md:1",
        )
    hit = hits[0]
    lines = [ln.strip() for ln in hit.chunk.text.splitlines() if ln.strip() and not ln.startswith("#")]
    seed = lines[0] if lines else hit.chunk.text[:80]
    question = f"根据 {hit.chunk.citation}，用自己的话解释：{seed[:60]}……它在强调什么？"
    return question, seed, hit.chunk.citation


def _tokens(text: str) -> list[str]:
    return [m.group(0).lower() for m in re.finditer(r"[A-Za-z]{2,}|\d+|[一-龥]{2,}", text)]
