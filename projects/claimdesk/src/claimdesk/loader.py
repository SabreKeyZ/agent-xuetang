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


def load_all_claims() -> list[Claim]:
    folder = fixtures_dir() / "claims"
    return [load_claim(p.stem) for p in sorted(folder.glob("*.json"))]
