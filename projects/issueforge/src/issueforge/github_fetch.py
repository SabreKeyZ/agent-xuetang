from __future__ import annotations

import os
from typing import Any

from issueforge.models import Issue


def fetch_public_issue(spec: str) -> Issue:
    """可选：owner/repo#n 。需要 GITHUB_TOKEN。演示默认不走这里。"""
    if "#" not in spec or "/" not in spec:
        raise ValueError("格式应为 owner/repo#number")
    repo, _, num = spec.partition("#")
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("未设置 GITHUB_TOKEN。夹具演示请用 python -m issueforge demo")

    import httpx

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "agent-xuetang-issueforge",
    }
    url = f"https://api.github.com/repos/{repo}/issues/{int(num)}"
    with httpx.Client(timeout=20.0) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
    labels = []
    for item in data.get("labels") or []:
        if isinstance(item, dict):
            labels.append(str(item.get("name") or ""))
        else:
            labels.append(str(item))
    return Issue.from_dict(
        {
            "number": data.get("number"),
            "title": data.get("title"),
            "body": data.get("body") or "",
            "labels": labels,
        },
        fixture_id=spec,
    )
