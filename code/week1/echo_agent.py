"""第 1 周：think → act → observe。无框架。

默认用规则脑，不访问网络。本周作业没有 --llm；有 Key 也不打兼容口，避免账单。
"""

from __future__ import annotations

import argparse
import calendar
import json
import os
import sys
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable


MAX_STEPS = 6


def weekday_tool(_arg: str) -> str:
    today = date.today()
    return calendar.day_name[today.weekday()]


def echo_upper_tool(arg: str) -> str:
    return arg.upper()


TOOLS: dict[str, Callable[[str], str]] = {
    "weekday": weekday_tool,
    "echo_upper": echo_upper_tool,
}


@dataclass
class Decision:
    thought: str
    action: str
    action_input: str = ""


class EchoAgent:
    def __init__(self, brain: Callable[[str, list[dict[str, Any]]], Decision]):
        self.brain = brain

    def run(self, user_input: str, max_steps: int = MAX_STEPS) -> dict[str, Any]:
        log: list[dict[str, Any]] = []
        observation = user_input
        final = ""
        for step in range(1, max_steps + 1):
            decision = self.brain(observation, log)
            if decision.action == "finish":
                final = decision.action_input or decision.thought
                record = {
                    "step": step,
                    "thought": decision.thought,
                    "action": "finish",
                    "observation": final,
                }
                log.append(record)
                break
            fn = TOOLS.get(decision.action)
            if fn is None:
                observation = f"error:unknown_tool:{decision.action}"
            else:
                try:
                    observation = fn(decision.action_input)
                except Exception as exc:  # noqa: BLE001 — 工具失败必须变成观察值
                    observation = f"error:{type(exc).__name__}:{exc}"
            record = {
                "step": step,
                "thought": decision.thought,
                "action": decision.action,
                "observation": observation,
            }
            log.append(record)
        else:
            final = "没做完：步数用尽。"
            log.append(
                {
                    "step": max_steps,
                    "thought": "hard stop",
                    "action": "finish",
                    "observation": final,
                }
            )
        return {"final": final, "log": log}


def rule_brain(observation: str, log: list[dict[str, Any]]) -> Decision:
    """无模型时的脑子：看见线索就调用工具，有观察值就收工。"""
    if log and log[-1]["action"] in TOOLS:
        last = log[-1]["observation"]
        return Decision(
            thought="已经有观察值。",
            action="finish",
            action_input=f"工具返回：{last}",
        )
    text = observation
    if "大写" in text:
        return Decision(thought="用户要大写。", action="echo_upper", action_input=text)
    if "星期" in text or "weekday" in text.lower() or "周几" in text:
        return Decision(thought="问的是星期，调用工具。", action="weekday", action_input="")
    return Decision(thought="没有匹配的工具，直接结束。", action="finish", action_input=text)


def dump_log(log: list[dict[str, Any]], stream: Any = sys.stdout) -> None:
    for row in log:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Week 1 echo agent")
    parser.add_argument("--query", default="今天星期几")
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS)
    args = parser.parse_args(argv)

    # 预留：有 Key 也不在作业默认路径打网，避免账单。需要时自己改 brain。
    _ = os.environ.get("OPENAI_API_KEY", "")

    agent = EchoAgent(rule_brain)
    result = agent.run(args.query, max_steps=args.max_steps)
    dump_log(result["log"])
    print(f"[final] {result['final']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
