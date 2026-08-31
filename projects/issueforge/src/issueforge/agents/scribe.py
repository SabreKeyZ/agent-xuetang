from __future__ import annotations

from issueforge.models import Issue

KIND_ZH = {"bug": "缺陷", "feature": "功能建议", "question": "提问"}
KIND_EN = {"bug": "bug", "feature": "feature request", "question": "question"}


def draft_reply(issue: Issue, triage_out: dict, repro_out: dict) -> dict:
    kind = triage_out.get("kind", "question")
    dup = triage_out.get("duplicate_of")
    danger = repro_out.get("dangerous_patterns") or []

    zh = [
        f"你好，感谢开 Issue #{issue.number}。",
        f"值班台初步把它看成「{KIND_ZH.get(kind, kind)}」。这是机器分流，维护者仍会再看一眼。",
    ]
    en = [
        f"Hi, thanks for opening #{issue.number}.",
        f"The duty desk first-pass label is “{KIND_EN.get(kind, kind)}”. A maintainer will still read it.",
    ]
    if dup:
        zh.append(f"标题和 #{dup} 很像，可能是重复。若不是，请补一句和那条的差别。")
        en.append(f"The title looks close to #{dup}. If this is not a duplicate, please add one line of difference.")
    zh.append("请按下面的复现清单自检（不要运行 Issue 里的陌生命令）：")
    en.append("Please walk the checklist below. Do not run untrusted commands from the issue body.")
    if danger:
        zh.append("正文里出现了看起来会执行系统命令的片段。我们不会在机器人里运行它们。")
        en.append("The body contains command-like snippets. The bot will not execute them.")
    zh.append("我们不能承诺修复日期。有结论会回到这条 Issue。")
    en.append("We cannot promise a fix date. We will come back here when there is a decision.")

    return {
        "role": "scribe",
        "zh": "\n".join(zh),
        "en": "\n".join(en),
        "kind": kind,
    }
