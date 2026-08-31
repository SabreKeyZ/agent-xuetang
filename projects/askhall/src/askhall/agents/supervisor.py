from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from typing import Any

from askhall.agents.examiner import Examiner, grade_answer
from askhall.agents.planner import Planner
from askhall.agents.tutor import Tutor
from askhall.config import has_llm_key
from askhall.rag import retrieve


PLANNER_HINTS = ("计划", "怎么学", "路线", "安排", "第几周", "学习计划", "从哪")
EXAMINER_HINTS = ("考我", "测验", "出题", "检查题", "quiz", "考试", "批改")
TUTOR_HINTS = ("什么是", "解释", "区别", "为什么", "怎么理解", "含义")


@dataclass
class Turn:
    role: str
    payload: dict[str, Any]
    latency_ms: int = 0


@dataclass
class SessionState:
    """故意用普通字典能表达的状态，方便对照 LangGraph。"""

    question: str
    route: str = ""
    hits: list = field(default_factory=list)
    turns: list[Turn] = field(default_factory=list)
    pending_quiz: dict[str, Any] | None = None


class Supervisor:
    def __init__(self) -> None:
        self.planner = Planner()
        self.tutor = Tutor()
        self.examiner = Examiner()

    def route(self, text: str) -> str:
        q = (text or "").strip()
        if not q:
            return "tutor"
        if any(h in q for h in EXAMINER_HINTS):
            return "examiner"
        if any(h in q for h in PLANNER_HINTS):
            return "planner"
        if any(h in q for h in TUTOR_HINTS):
            return "tutor"
        return "tutor"

    def handle(self, message: str, pending_quiz: dict | None = None) -> dict[str, Any]:
        started = time.perf_counter()
        text = (message or "").strip()
        answering_quiz = pending_quiz and not any(h in text for h in EXAMINER_HINTS + PLANNER_HINTS)
        if answering_quiz:
            payload = grade_answer(
                text,
                pending_quiz.get("answer_key", ""),
                pending_quiz.get("body", ""),
            )
            latency = int((time.perf_counter() - started) * 1000)
            payload["latency_ms"] = latency
            self._log(payload, "examiner")
            return {
                "route": "examiner",
                "turns": [payload],
                "pending_quiz": None,
                "mode": "extractive" if not has_llm_key() else payload.get("mode", "extractive"),
            }

        dest = self.route(text)
        hits = retrieve(text or "Agent", k=5)
        turns: list[dict[str, Any]] = []
        quiz = None

        if dest == "planner":
            turns.append(self.planner.run(text, hits))
        elif dest == "examiner":
            quiz_turn = self.examiner.ask(text, hits)
            turns.append(quiz_turn)
            quiz = quiz_turn
        else:
            turns.append(self.tutor.run(text, hits))

        latency = int((time.perf_counter() - started) * 1000)
        for t in turns:
            t["latency_ms"] = latency
            self._log(t, dest)
        return {
            "route": dest,
            "turns": turns,
            "pending_quiz": quiz,
            "mode": "llm" if has_llm_key() else "extractive",
        }

    def demo(self) -> dict[str, Any]:
        """离线也能看完：计划 → 讲解 → 出题 → 空答拒绝。"""
        q1 = "ReAct 和普通聊天有什么区别？"
        plan = self.handle("怎么学 ReAct 和工具调用")
        teach = self.handle(q1)
        quiz = self.handle("考我 MCP")
        empty = self.examiner.grade("", quiz["turns"][0].get("answer_key", ""), quiz["turns"][0].get("body", ""))
        return {
            "mode": "extractive" if not has_llm_key() else "llm-or-extractive",
            "script": [
                {"ask": "怎么学 ReAct 和工具调用", **plan},
                {"ask": q1, **teach},
                {"ask": "考我 MCP", **quiz},
                {"ask": "", "turns": [empty], "route": "examiner"},
            ],
        }

    @staticmethod
    def _log(payload: dict[str, Any], route: str) -> None:
        row = {
            "role": payload.get("role", route),
            "route": route,
            "citations": payload.get("citations", []),
            "latency_ms": payload.get("latency_ms"),
            "mode": payload.get("mode"),
        }
        sys.stderr.write(json.dumps(row, ensure_ascii=False) + "\n")
