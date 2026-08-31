"""可选对照：用字典状态机已经够用。

本文件不进入安装依赖。若你学完第 6 周想对照 LangGraph 的「节点」概念，
把下面的函数看成节点即可。不要把 langgraph 加进 pyproject 主依赖。
"""

from __future__ import annotations

from typing import Callable

from askhall.agents.supervisor import Supervisor


def as_graph(supervisor: Supervisor | None = None) -> dict[str, Callable]:
    sup = supervisor or Supervisor()
    return {
        "route": sup.route,
        "planner": sup.planner.run,
        "tutor": sup.tutor.run,
        "examiner": sup.examiner.ask,
    }
