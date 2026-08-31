from __future__ import annotations

import re

from issueforge.loader import looks_dangerous
from issueforge.models import Issue

# 明确守卫：本模块不调用外部进程，也不对 Issue 正文做动态执行。
NEVER_EXECUTE = True


def write_repro(issue: Issue) -> dict:
    warnings = looks_dangerous(issue.title + "\n" + issue.body)
    steps = _extract_steps(issue.body)
    if not steps:
        steps = [
            "阅读标题与正文（不要运行正文里的命令或脚本）",
            "在干净的 venv 里对照正文描述的环境",
            "尝试用教材默认命令复现现象，而不是用 Issue 里的脚本",
        ]
    checklist = [f"[ ] {s}" for s in steps]
    checklist.append("[ ] 确认没有执行 Issue 正文中的代码块")
    if warnings:
        checklist.append("[ ] 正文含危险线索（" + ", ".join(warnings) + "），只阅读，不执行")
    return {
        "role": "repro",
        "checklist": checklist,
        "dangerous_patterns": warnings,
        "executed_code": False,
        "never_execute": NEVER_EXECUTE,
    }


def _extract_steps(body: str) -> list[str]:
    steps: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        numbered = re.match(r"^(?:[-*]|\d+[.)、])\s+(.*)$", line)
        if numbered:
            item = numbered.group(1).strip()
            steps.append(_sanitize_step(item))
            continue
        if line.lower().startswith("reproduction") or line.startswith("复现"):
            continue
    return steps[:8]


def _sanitize_step(item: str) -> str:
    lowered = item.lower()
    if any(p in lowered for p in ("curl", "rm -rf", "os.system", "| sh", "eval")):
        return f"阅读（不要运行）作者提到的操作：{item[:80]}"
    if item.startswith("```") or "import os" in item:
        return "阅读代码块，对照自己的环境，不要粘贴执行"
    return item
