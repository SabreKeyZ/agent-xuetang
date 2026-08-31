from __future__ import annotations

import json
from pathlib import Path

from issueforge.models import Issue

# 禁止在复现阶段执行的线索。只用来写警告，不当代码跑。
DANGEROUS_PATTERNS = (
    "os.system",
    "subprocess",
    "curl | sh",
    "curl|sh",
    "| sh",
    "| bash",
    "rm -rf",
    "eval(",
    "__import__",
    "powershell",
)


def fixtures_dir() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "fixtures"
        if cand.is_dir() and any(cand.glob("*.json")):
            return cand
    raise FileNotFoundError("找不到 fixtures/")


def load_fixture(name: str) -> Issue:
    path = fixtures_dir() / f"{name}.json"
    if not path.is_file():
        path = fixtures_dir() / name
    data = json.loads(path.read_text(encoding="utf-8"))
    return Issue.from_dict(data, fixture_id=path.stem)


def load_all_fixtures() -> list[Issue]:
    issues = [load_fixture(p.stem) for p in sorted(fixtures_dir().glob("*.json"))]
    return issues


def looks_dangerous(text: str) -> list[str]:
    blob = text.lower()
    return [p for p in DANGEROUS_PATTERNS if p.lower() in blob]
