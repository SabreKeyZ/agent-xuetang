"""第 2 周：手写 ReAct。计算器 + 假搜索。无框架。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


MAX_STEPS = 6
HERE = Path(__file__).resolve().parent

SEARCH_TABLE: list[tuple[tuple[str, ...], str]] = [
    (("mcp", "MCP"), "Agent学堂在第4周写一个很小的 MCP 服务器。"),
    (("工单台", "ticketdesk"), "工单台是毕业作品：青匣记售后队列，分类、政策引用、退款闸门。"),
    (("react", "ReAct"), "ReAct 是一种把思考和行动写成字段的循环写法。"),
    (("理赔台", "claimdesk"), "理赔台在第7周：材料质检、条款引用、核赔建议不打款。"),
]


def calculator(expression: str) -> str:
    expr = expression.strip().replace("×", "*").replace("÷", "/")
    expr = expr.replace(" ", "")
    if not expr or not re.fullmatch(r"[0-9+\-*/().]+", expr):
        return "error:invalid_expression"
    if re.search(r"[a-zA-Z_]", expr):
        return "error:invalid_expression"
    try:
        value = _safe_arith(expr)
    except ZeroDivisionError:
        return "error:division_by_zero"
    except Exception:  # noqa: BLE001
        return "error:invalid_expression"
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


def _safe_arith(expr: str) -> float:
    tokens = re.findall(r"\d+\.?\d*|[+\-*/()]", expr)
    if not tokens:
        raise ValueError("empty")
    pos = 0

    def peek() -> str | None:
        return tokens[pos] if pos < len(tokens) else None

    def eat(expected: str | None = None) -> str:
        nonlocal pos
        if pos >= len(tokens):
            raise ValueError("eof")
        tok = tokens[pos]
        if expected is not None and tok != expected:
            raise ValueError("mismatch")
        pos += 1
        return tok

    def parse_expr() -> float:
        val = parse_term()
        while peek() in {"+", "-"}:
            op = eat()
            rhs = parse_term()
            val = val + rhs if op == "+" else val - rhs
        return val

    def parse_term() -> float:
        val = parse_factor()
        while peek() in {"*", "/"}:
            op = eat()
            rhs = parse_factor()
            val = val * rhs if op == "*" else val / rhs
        return val

    def parse_factor() -> float:
        tok = peek()
        if tok == "+":
            eat()
            return parse_factor()
        if tok == "-":
            eat()
            return -parse_factor()
        if tok == "(":
            eat()
            val = parse_expr()
            eat(")")
            return val
        if tok is None or not re.fullmatch(r"\d+\.?\d*", tok):
            raise ValueError("num")
        return float(eat())

    result = parse_expr()
    if pos != len(tokens):
        raise ValueError("trailing")
    return result


def search(query: str) -> str:
    q = query.lower()
    hits: list[str] = []
    for keys, text in SEARCH_TABLE:
        if any(k.lower() in q or k in query for k in keys):
            hits.append(text)
    if not hits:
        return "error:not_found"
    return " / ".join(hits)


TOOLS = {
    "calculator": calculator,
    "search": search,
}


@dataclass
class Decision:
    thought: str
    action: str
    action_input: str = ""


@dataclass
class Trace:
    log: list[dict[str, Any]] = field(default_factory=list)
    final: str = ""


def parse_react_block(text: str) -> Decision | None:
    thought = _field(text, "Thought") or _field(text, "thought") or ""
    action = _field(text, "Action") or _field(text, "action") or ""
    action_input = _field(text, "Action Input") or _field(text, "action_input") or ""
    final = _field(text, "Final Answer") or _field(text, "final")
    if final and not action:
        return Decision(thought=thought or "直接作答", action="finish", action_input=final)
    if action.lower() in {"finish", "final", "none"}:
        return Decision(thought=thought, action="finish", action_input=action_input or final or "")
    if action.lower() in TOOLS:
        return Decision(thought=thought, action=action.lower(), action_input=action_input)
    return None


def _field(text: str, name: str) -> str | None:
    pattern = rf"{name}\s*[：:]\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_math(query: str) -> str | None:
    match = re.search(r"(\d+\s*[+\-*/×÷]\s*\d+(?:\s*[+\-*/×÷]\s*\d+)*)", query)
    return match.group(1) if match else None


def rule_brain(query: str, log: list[dict[str, Any]]) -> Decision:
    used = {row["action"] for row in log}
    math = extract_math(query)
    want_search = any(
        key in query for key in ("第几周", "工单台", "MCP", "mcp", "ReAct", "理赔台", "Agent学堂")
    )
    want_calc = math is not None or "等于多少" in query

    if log and log[-1]["action"] in TOOLS:
        last_obs = str(log[-1]["observation"])
        if last_obs.startswith("error:") and log[-1]["action"] == "calculator":
            return Decision(thought="计算失败，停止。", action="finish", action_input=last_obs)
        if want_calc and "calculator" not in used and math:
            return Decision(thought="还需要算一下。", action="calculator", action_input=math)
        if want_search and "search" not in used:
            return Decision(thought="还需要查一下。", action="search", action_input=query)
        parts = [str(row["observation"]) for row in log if row["action"] in TOOLS]
        return Decision(thought="材料齐了。", action="finish", action_input="；".join(parts))

    if want_search and "search" not in used:
        return Decision(thought="先查课程表。", action="search", action_input=query)
    if want_calc and math and "calculator" not in used:
        return Decision(thought="先算。", action="calculator", action_input=math)
    return Decision(thought="没有工具可调用。", action="finish", action_input=query)


class ReactAgent:
    def __init__(self, brain=rule_brain):
        self.brain = brain

    def run(self, query: str, max_steps: int = MAX_STEPS) -> Trace:
        trace = Trace()
        observation = query
        for step in range(1, max_steps + 1):
            decision = self.brain(query if not trace.log else query, trace.log)
            _ = observation
            if decision.action == "finish":
                trace.final = decision.action_input or decision.thought
                trace.log.append(
                    {
                        "step": step,
                        "thought": decision.thought,
                        "action": "finish",
                        "observation": trace.final,
                    }
                )
                return trace
            fn = TOOLS.get(decision.action)
            if fn is None:
                observation = f"error:unknown_tool:{decision.action}"
            else:
                observation = fn(decision.action_input)
            trace.log.append(
                {
                    "step": step,
                    "thought": decision.thought,
                    "action": decision.action,
                    "observation": observation,
                }
            )
        trace.final = "没做完：步数用尽。"
        return trace


def load_cases(path: Path | None = None) -> list[dict[str, Any]]:
    target = path or HERE / "eval_cases.json"
    return json.loads(target.read_text(encoding="utf-8"))


def evaluate(cases: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    agent = ReactAgent()
    rows = []
    for case in cases or load_cases():
        trace = agent.run(case["query"])
        tools_used = [row["action"] for row in trace.log if row["action"] in TOOLS]
        expected_tools = case.get("expect_tools")
        if expected_tools is None and case.get("expect_tool"):
            expected_tools = [case["expect_tool"]]
        tool_ok = True
        if expected_tools:
            tool_ok = all(t in tools_used for t in expected_tools)
        needles = case.get("expect_contains", [])
        if isinstance(needles, str):
            needles = [needles]
        text_ok = all(n in trace.final for n in needles)
        rows.append(
            {
                "id": case["id"],
                "ok": bool(tool_ok and text_ok),
                "tool_ok": tool_ok,
                "text_ok": text_ok,
                "final": trace.final,
                "tools": tools_used,
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="")
    parser.add_argument("--eval", action="store_true", dest="do_eval")
    args = parser.parse_args(argv)

    if args.do_eval:
        rows = evaluate()
        failed = 0
        for row in rows:
            mark = "PASS" if row["ok"] else "FAIL"
            print(f"[{mark}] {row['id']} tools={row['tools']} final={row['final']}")
            if not row["ok"]:
                failed += 1
        return 1 if failed else 0

    query = args.query or "3 * 7 等于多少"
    trace = ReactAgent().run(query)
    for row in trace.log:
        print(json.dumps(row, ensure_ascii=False))
    print(f"[final] {trace.final}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
