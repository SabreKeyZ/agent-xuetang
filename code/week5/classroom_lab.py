"""第 5 周可选实验：教室玩具。不是毕业作品，也不是简历 STAR。

主管按关键字分流。不是五人 Mesh。
公开产品在 projects/ticketdesk 与 projects/claimdesk。
"""

from __future__ import annotations

import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "classroom.md"

PLAN_HINTS = ("计划", "怎么学", "路线")
EXAM_HINTS = ("考我", "测验", "空答")


def route(text: str) -> str:
    q = text or ""
    if any(h in q for h in EXAM_HINTS):
        return "examiner"
    if any(h in q for h in PLAN_HINTS):
        return "planner"
    return "tutor"


def retrieve(query: str) -> list[str]:
    lines = FIXTURE.read_text(encoding="utf-8").splitlines()
    needles = []
    if any(w in query for w in ("计划", "怎么学", "循环")):
        needles.extend(("规划", "循环"))
    if any(w in query for w in ("解释", "为什么", "主管")):
        needles.extend(("主管", "角色"))
    if any(w in query for w in ("考", "空", "引用")):
        needles.extend(("空答", "引用", "考试"))
    hits = []
    for i, line in enumerate(lines, start=1):
        if any(n in line for n in needles):
            hits.append(f"code/week5/classroom.md:{i}")
    return hits[:3]


def handle(message: str) -> dict:
    text = (message or "").strip()
    dest = route(text)
    if dest == "examiner" and (not text or "空答" in text):
        return {
            "route": dest,
            "refused": True,
            "title": "没有引用，就先不答",
            "body": "空答案拒改。这是教室玩具，不是工单台。",
            "citations": [],
        }
    if "FlipFlop" in text:
        return {
            "route": dest,
            "refused": True,
            "title": "没有引用，就先不答",
            "body": "便签里没有这句话。",
            "citations": [],
        }
    cites = retrieve(text)
    if not cites:
        return {
            "route": dest,
            "refused": True,
            "title": "没有引用，就先不答",
            "body": "便签里没有这句话。",
            "citations": [],
        }
    return {
        "route": dest,
        "refused": False,
        "title": dest,
        "body": FIXTURE.read_text(encoding="utf-8").strip(),
        "citations": cites,
    }


def demo() -> list[dict]:
    return [
        handle("怎么学循环"),
        handle("解释为什么只要一个主管"),
        handle("考我一下"),
        handle("空答"),
        handle("什么是 FlipFlopZetaQueue"),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="第 5 周教室实验")
    parser.add_argument("cmd", nargs="?", default="demo")
    args = parser.parse_args(argv)
    if args.cmd != "demo":
        return 2
    print("[week5] 教室玩具，不是毕业作品。公开产品：工单台 / 理赔台。")
    for row in demo():
        print(f"[{row['route']}] {row['title']}")
        if row["citations"]:
            print("引用: " + ", ".join(row["citations"]))
        if row["refused"]:
            print("没有引用，就先不答")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
