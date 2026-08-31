"""评测用的夹具读取和引用校验。不是迷你台实现。"""

from __future__ import annotations

import json
import re
from pathlib import Path

from minidesk import NotBuiltYet

LAB_ROOT = Path(__file__).resolve().parents[1]
CITE_RE = re.compile(r"^docs/policy/[A-Za-z0-9._-]+\.md:[1-9][0-9]*$")
TICKETDESK_LEAK = (
    "after-sales.md",
    "promo-2026-summer.md",
    "refund-and-risk.md",
    "qingtu-bao",
    "T-1",
    "qingxia",
    "QX-",
)


def read_fixture(name: str) -> dict:
    path = LAB_ROOT / "fixtures" / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_names() -> list[str]:
    return sorted(p.stem for p in (LAB_ROOT / "fixtures").glob("*.json"))


def citation_on_disk(cite: str) -> bool:
    m = CITE_RE.match(cite.strip())
    if not m:
        return False
    rel, line_s = cite.rsplit(":", 1)
    path = LAB_ROOT / rel
    if not path.is_file():
        return False
    n = len(path.read_text(encoding="utf-8").splitlines())
    line = int(line_s)
    return 1 <= line <= n


def call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except NotBuiltYet as exc:
        raise AssertionError(str(exc)) from exc
    except AttributeError as exc:
        raise AssertionError(
            f"还缺这个名字：{exc}。对照 prompts/ 里的函数签名，不要改评测。"
        ) from exc
