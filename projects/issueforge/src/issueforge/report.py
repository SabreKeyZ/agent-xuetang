from __future__ import annotations

from html import escape
from pathlib import Path

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


KIND_LABEL = {"bug": "缺陷 bug", "feature": "功能 feature", "question": "提问 question"}


def _issue_quotes(body: str, limit: int = 3) -> list[str]:
    lines = [ln.strip() for ln in (body or "").splitlines() if ln.strip()]
    picked: list[str] = []
    for ln in lines:
        if ln.lower().startswith(("reproduction", "steps", "expected", "actual", "environment")):
            continue
        if ln.startswith(("-", "*", "1.", "2.")):
            continue
        picked.append(ln[:180])
        if len(picked) >= limit:
            break
    return picked or (lines[:limit] if lines else ["（正文为空）"])


def to_html(bundles: list[dict]) -> str:
    """值班日志：盖章、引用正文、复现勾选、双语草稿。不是看板。"""
    cards = "\n".join(_card(b) for b in bundles)
    n = len(bundles)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>开源值班台 · Agent学堂</title>
  <style>
    :root {{
      --paper: #1a1612; --sheet: #231e18; --ink: #f0e6d4; --muted: #9a8d7a;
      --line: #3d3428; --chip: #e8c36a; --refuse: #d97737;
      --bug: #e07a7a; --feature: #7aa8d4; --question: #e0c07a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: var(--paper); color: var(--ink);
      font: 15px/1.55 "Source Han Sans SC", "Noto Sans SC", sans-serif;
    }}
    header {{ max-width: 860px; margin: 0 auto; padding: 24px 20px 12px; border-bottom: 1px solid var(--line); }}
    .wordmark {{ font-family: "Source Han Serif SC", "Noto Serif SC", serif; font-size: 26px; margin: 0; }}
    .wordmark small {{ display: block; font-size: 12px; letter-spacing: 0.16em; color: var(--muted); margin-top: 4px; }}
    .subtitle {{ display: inline-block; margin: 10px 0 0; color: var(--refuse); border: 1px solid var(--refuse); padding: 3px 10px; font-size: 14px; }}
    .dogfood {{ color: var(--muted); font-size: 13px; margin: 8px 0 0; }}
    main {{ max-width: 860px; margin: 0 auto; padding: 8px 20px 56px; }}
    .log-head {{ color: var(--muted); font-size: 13px; margin: 16px 0 8px; letter-spacing: 0.08em; }}
    article {{
      background: var(--sheet); border: 1px solid var(--line); padding: 16px 18px; margin: 14px 0;
      background-image: repeating-linear-gradient(transparent, transparent 27px, #2c261e 28px);
    }}
    .topline {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    .stamp {{ border: 1.5px solid currentColor; padding: 2px 8px; font-size: 12px; letter-spacing: 0.04em; }}
    .stamp.bug {{ color: var(--bug); }}
    .stamp.feature {{ color: var(--feature); }}
    .stamp.question {{ color: var(--question); }}
    .chip {{
      font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12px;
      color: var(--chip); border: 1px solid #5a4a28; background: #2a2318;
      padding: 2px 8px; border-radius: 999px;
    }}
    h2 {{ font-family: "Source Han Serif SC", "Noto Serif SC", serif; font-size: 18px; margin: 10px 0 8px; }}
    .quote {{
      border-left: 3px solid var(--chip); padding: 6px 10px; margin: 8px 0;
      color: #e6d8be; font-size: 14px;
    }}
    .refuse {{
      color: var(--refuse); border: 1px solid var(--refuse); padding: 6px 10px; margin: 10px 0; font-size: 13px;
    }}
    h3 {{ font-size: 12px; letter-spacing: 0.1em; color: var(--muted); margin: 14px 0 6px; }}
    ul {{ margin: 0; padding-left: 1.2em; }}
    .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    @media (max-width: 720px) {{ .cols {{ grid-template-columns: 1fr; }} }}
    .reply {{ background: #18140f; border-left: 3px solid var(--ink); padding: 8px 10px; white-space: pre-wrap; font-size: 13px; }}
    footer {{ max-width: 860px; margin: 0 auto; padding: 0 20px 40px; color: var(--muted); font-size: 13px; }}
  </style>
</head>
<body>
  <header>
    <h1 class="wordmark">开源值班台 <small>Agent学堂 · IssueForge</small></h1>
    <p class="subtitle">没有引用，就先不答</p>
    <p class="dogfood">教材就是仓库。值班只引用夹具正文，不执行里面的命令。</p>
  </header>
  <main>
    <p class="log-head">值班日志 · {n} 条 · never_execute=True</p>
{cards}
  </main>
  <footer><code>python -m issueforge board</code> · 机器盖章，人再看一眼。</footer>
</body>
</html>
"""


def write_html(bundles: list[dict], path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_html(bundles), encoding="utf-8")
    return path


def _card(bundle: dict) -> str:
    issue = bundle["issue"]
    tri = bundle["triage"]
    rep = bundle["repro"]
    scri = bundle["scribe"]
    kind = tri.get("kind", "question")
    dup = tri.get("duplicate_of")
    dup_line = f"#{dup}（标题相近，score={tri.get('duplicate_score')}）" if dup else "无"
    checks = "".join(f"<li>{escape(str(c))}</li>" for c in rep.get("checklist") or [])
    fixture = issue.get("fixture_id") or "—"
    title = escape(str(issue.get("title") or ""))
    zh = escape(scri.get("zh") or "")
    en = escape(scri.get("en") or "")
    quotes = "".join(f'<div class="quote">「{escape(q)}」</div>' for q in _issue_quotes(str(issue.get("body") or "")))
    danger = rep.get("dangerous_patterns") or []
    refuse = (
        f'<div class="refuse">正文含命令，先不跑 · {escape(", ".join(danger))}</div>'
        if danger
        else '<div class="refuse">是否执行了正文代码：否</div>'
    )
    return f"""    <article>
      <div class="topline">
        <span class="stamp {escape(kind)}">{escape(KIND_LABEL.get(kind, kind))}</span>
        <span class="chip">fixtures/{escape(fixture)}.json</span>
        <span class="chip">#{escape(str(issue.get("number")))}</span>
      </div>
      <h2>{title}</h2>
      {quotes}
      {refuse}
      <h3>分流</h3>
      <ul>
        <li>类型：{escape(kind)}</li>
        <li>重复嫌疑：{escape(str(dup_line))}</li>
      </ul>
      <h3>复现清单</h3>
      <ul>{checks}</ul>
      <h3>建议回复</h3>
      <div class="cols">
        <div><div class="reply">{zh}</div></div>
        <div><div class="reply">{en}</div></div>
      </div>
    </article>"""

