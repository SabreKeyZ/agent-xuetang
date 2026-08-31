"""第 4 周：最小 MCP 风格 stdio 服务器。暴露 get_week_goal。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


WEEK_FILES = {
    0: "00-setup.md",
    1: "01-what-is-an-agent.md",
    2: "02-tools-and-react.md",
    3: "03-memory-rag.md",
    4: "04-mcp-and-skills.md",
    5: "05-multi-agent.md",
    6: "06-ticketdesk.md",
    7: "07-claimdesk.md",
    8: "08-ship-and-job.md",
}


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "docs" / "weeks").is_dir():
            return parent
    raise FileNotFoundError("找不到 docs/weeks")


def extract_section(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    collecting = False
    buf: list[str] = []
    for line in lines:
        if line.startswith("## "):
            title = line[3:].strip()
            if collecting:
                break
            if heading in title:
                collecting = True
            continue
        if collecting:
            buf.append(line)
    return "\n".join(buf).strip()


def get_week_goal(week: int) -> str:
    if week not in WEEK_FILES:
        raise ValueError(f"week 必须是 0-8，收到 {week}")
    path = repo_root() / "docs" / "weeks" / WEEK_FILES[week]
    text = path.read_text(encoding="utf-8")
    goal = extract_section(text, "本周你要带走什么")
    if not goal:
        goal = extract_section(text, "目标")
    if not goal:
        raise FileNotFoundError(f"{path} 里没有「本周你要带走什么」或「目标」小节")
    title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), path.name)
    return f"{title}\n\n{goal}"


def list_weeks() -> list[dict[str, Any]]:
    rows = []
    root = repo_root() / "docs" / "weeks"
    for num, name in WEEK_FILES.items():
        first = (root / name).read_text(encoding="utf-8").splitlines()[0]
        rows.append({"week": num, "file": name, "title": first.lstrip("# ").strip()})
    return rows


def tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "name": "get_week_goal",
            "description": "返回 Agent学堂第 N 周的「本周你要带走什么」小节原文。",
            "inputSchema": {
                "type": "object",
                "properties": {"week": {"type": "integer", "minimum": 0, "maximum": 8}},
                "required": ["week"],
            },
        },
        {
            "name": "list_weeks",
            "description": "列出 0-8 周标题。",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]


def handle(message: dict[str, Any]) -> dict[str, Any]:
    mid = message.get("id")
    method = message.get("method", "")
    params = message.get("params") or {}
    try:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": mid,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "agent-xuetang-week-goal", "version": "0.1.0"},
                    "capabilities": {"tools": {}},
                },
            }
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": mid, "result": {"tools": tool_schemas()}}
        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") or {}
            if name == "get_week_goal":
                week = int(arguments["week"])
                text = get_week_goal(week)
                return {
                    "jsonrpc": "2.0",
                    "id": mid,
                    "result": {"content": [{"type": "text", "text": text}]},
                }
            if name == "list_weeks":
                text = json.dumps(list_weeks(), ensure_ascii=False)
                return {
                    "jsonrpc": "2.0",
                    "id": mid,
                    "result": {"content": [{"type": "text", "text": text}]},
                }
            raise ValueError(f"unknown tool: {name}")
        raise ValueError(f"unknown method: {method}")
    except Exception as exc:  # noqa: BLE001 — JSON-RPC 错误通道
        return {
            "jsonrpc": "2.0",
            "id": mid,
            "error": {"code": -32000, "message": str(exc)},
        }


def serve_stdio(stdin, stdout) -> None:
    for raw in stdin:
        line = raw.strip()
        if not line:
            continue
        message = json.loads(line)
        stdout.write(json.dumps(handle(message), ensure_ascii=False) + "\n")
        stdout.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--week", type=int, default=4)
    args = parser.parse_args(argv)
    if args.once:
        try:
            print(get_week_goal(args.week))
            return 0
        except Exception as exc:  # noqa: BLE001
            print(str(exc), file=sys.stderr)
            return 1
    serve_stdio(sys.stdin, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
