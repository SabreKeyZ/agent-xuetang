from __future__ import annotations

import json
from pathlib import Path

from claimdesk.config import project_root


def tracking_dir() -> Path:
    return project_root() / "fixtures" / "tracking"


def lookup_tracking(tracking_no: str, catalog: dict | None = None) -> dict:
    """假轨迹：形状像承运商回传，读夹具。"""
    tid = (tracking_no or "").strip()
    if not tid:
        return {"ok": False, "reason": "missing_tracking", "tracking": None}
    if catalog is not None and tid in catalog:
        return {"ok": True, "reason": "ok", "tracking": catalog[tid]}
    path = tracking_dir() / f"{tid}.json"
    if not path.is_file():
        return {"ok": False, "reason": "not_found", "tracking": None}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"ok": True, "reason": "ok", "tracking": data}


def load_all_tracking() -> dict[str, dict]:
    folder = tracking_dir()
    out: dict[str, dict] = {}
    if not folder.is_dir():
        return out
    for path in sorted(folder.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        key = str(data.get("tracking") or path.stem)
        out[key] = data
    return out
