from __future__ import annotations

from issueforge.agents.repro import write_repro
from issueforge.agents.scribe import draft_reply
from issueforge.agents.triage import triage
from issueforge.models import Issue


def process(issue: Issue, catalog: list[Issue] | None = None) -> dict:
    tri = triage(issue, catalog)
    rep = write_repro(issue)
    scri = draft_reply(issue, tri, rep)
    return {"issue": issue.as_dict(), "triage": tri, "repro": rep, "scribe": scri}


def to_markdown(bundle: dict) -> str:
    issue = bundle["issue"]
    tri = bundle["triage"]
    rep = bundle["repro"]
    scri = bundle["scribe"]
    dup = tri.get("duplicate_of")
    dup_line = f"#{dup} （标题相近，score={tri.get('duplicate_score')}）" if dup else "无"
    checks = "\n".join(f"- {c}" if not c.startswith("- ") else f"- {c}" for c in rep["checklist"])
    # checklist 项已经带 [ ]
    checks = "\n".join(f"- {c}" for c in rep["checklist"])
    return f"""# Issue #{issue['number']} 值班报告

- 标题: {issue['title']}
- 夹具: {issue.get('fixture_id') or '—'}

## 分流

- 类型: {tri['kind']}
- 重复嫌疑: {dup_line}

## 复现清单

{checks}

- 是否执行了正文代码: **否**（守卫 never_execute={rep.get('never_execute')}）

## 建议回复

### 中文

{scri['zh']}

### English

{scri['en']}
"""
