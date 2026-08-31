from __future__ import annotations

import json
from pathlib import Path

from claimdesk.config import project_root
from claimdesk.models import Claim


def fixtures_dir() -> Path:
    return project_root() / "fixtures"


def load_claim(name: str) -> Claim:
    folder = fixtures_dir() / "claims"
    path = folder / f"{name}.json"
    if not path.is_file():
        path = folder / name
    data = json.loads(path.read_text(encoding="utf-8"))
    return Claim.from_dict(data, fixture_id=path.stem)


# 工期走读案件置顶：通过 C-2009、拒赔 C-2002。
_CLAIM_WALKTHROUGH = ("C-2009", "C-2002", "C-2012")


def _walkthrough_key(case_id: str, first: tuple[str, ...]) -> tuple[int, str]:
    try:
        return (first.index(case_id), case_id)
    except ValueError:
        return (len(first), case_id)


def load_all_claims() -> list[Claim]:
    folder = fixtures_dir() / "claims"
    claims = [load_claim(p.stem) for p in folder.glob("*.json")]
    return sorted(claims, key=lambda c: _walkthrough_key(c.id, _CLAIM_WALKTHROUGH))
