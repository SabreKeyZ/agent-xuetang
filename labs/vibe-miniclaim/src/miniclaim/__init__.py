"""雾津保迷你理赔台。实现写在 prompts/ 里，不要从 claimdesk 抄。"""

from __future__ import annotations

__version__ = "0.0.0"


class NotBuiltYet(RuntimeError):
    """评测会红，直到学徒按 prompts/ 一步一步实现。"""


def demo(fixture: str | None = None) -> str:
    raise NotBuiltYet(
        "还没实现，把 prompts/01-load-fixtures.md 贴给助手（一次只贴一步）。"
        "不要打开 projects/claimdesk，不要申请 Key。"
    )
