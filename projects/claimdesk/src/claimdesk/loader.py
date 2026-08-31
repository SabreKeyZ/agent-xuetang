from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any

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


def resolve_optional_path(raw: str) -> Path:
    text = (raw or "").strip()
    p = Path(text).expanduser()
    candidates = [p]
    if not p.is_absolute():
        candidates.append(Path.cwd() / p)
        try:
            candidates.append(project_root() / p)
        except FileNotFoundError:
            pass
    for cand in candidates:
        if cand.exists():
            return cand.resolve()
    return p


def _split_list(raw: str) -> list[Any]:
    text = (raw or "").strip()
    if not text:
        return []
    if text[0] in "[{":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return [text]
        if isinstance(parsed, list):
            return list(parsed)
        return [parsed]
    return [chunk.strip() for chunk in text.replace("|", ";").split(";") if chunk.strip()]


def _maybe_json_list(raw: str) -> list[Any]:
    text = (raw or "").strip()
    if not text:
        return []
    if text[0] in "[{":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return []
        return parsed if isinstance(parsed, list) else []
    return []


def _csv_row_to_mapping(row: dict[str, str | None]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for key, value in row.items():
        if not key or key.strip() == "":
            continue
        data[key.strip()] = value.strip() if isinstance(value, str) else value
    if not any(str(v).strip() for v in data.values() if v is not None):
        return {}
    if "attachments" in data and isinstance(data["attachments"], str):
        data["attachments"] = _split_list(data["attachments"])
    if "prior_actions" in data and isinstance(data["prior_actions"], str):
        data["prior_actions"] = _maybe_json_list(data["prior_actions"])
    return data


def claims_from_csv(path: str | Path) -> list[Claim]:
    """CSV 行映射到现有 Claim。列名对齐 fixtures 字段。"""
    target = Path(path)
    if not target.is_file():
        raise FileNotFoundError(f"案件 CSV 不是文件或不存在：{target}")
    claims: list[Claim] = []
    with target.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"案件 CSV 没有表头：{target}")
        for row in reader:
            mapping = _csv_row_to_mapping(row)
            if not mapping:
                continue
            fixture_id = str(mapping.get("fixture_id") or target.stem)
            claims.append(Claim.from_dict(mapping, fixture_id=fixture_id))
    if not claims:
        raise ValueError(f"案件 CSV 没有有效行：{target}")
    return claims


def claims_from_json(path: str | Path) -> list[Claim]:
    """JSON 文件或目录。对象 / 数组都走 Claim.from_dict。"""
    target = Path(path)
    if target.is_dir():
        claims: list[Claim] = []
        for child in sorted(target.glob("*.json")):
            claims.extend(claims_from_json(child))
        if not claims:
            raise ValueError(f"案件目录里没有有效 JSON：{target}")
        return claims
    if not target.is_file():
        raise FileNotFoundError(f"案件 JSON 不是文件或不存在：{target}")
    payload = json.loads(target.read_text(encoding="utf-8"))
    items = payload if isinstance(payload, list) else [payload]
    claims = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"JSON 案件必须是对象或对象列表：{target}")
        fixture_id = str(item.get("fixture_id") or target.stem)
        claims.append(Claim.from_dict(item, fixture_id=fixture_id))
    if not claims:
        raise ValueError(f"案件 JSON 没有有效对象：{target}")
    return claims


def try_optional_claims() -> tuple[list[Claim] | None, list[str]]:
    notes: list[str] = []
    csv_raw = os.environ.get("CLAIMDESK_IMPORT_CSV", "").strip()
    json_raw = os.environ.get("CLAIMDESK_IMPORT_JSON", "").strip()
    if not csv_raw and not json_raw:
        return None, notes

    collected: list[Claim] = []
    if csv_raw:
        try:
            collected.extend(claims_from_csv(resolve_optional_path(csv_raw)))
        except (OSError, ValueError, json.JSONDecodeError, csv.Error) as exc:
            notes.append(f"CSV 导入失败，忽略：{exc}")
    if json_raw:
        try:
            collected.extend(claims_from_json(resolve_optional_path(json_raw)))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            notes.append(f"JSON 导入失败，忽略：{exc}")
    if collected:
        return collected, notes
    notes.append("可选导入没有有效案件，回退 fixtures/。")
    return None, notes


def _load_fixture_claims() -> list[Claim]:
    folder = fixtures_dir() / "claims"
    claims = [load_claim(p.stem) for p in folder.glob("*.json")]
    return sorted(claims, key=lambda c: _walkthrough_key(c.id, _CLAIM_WALKTHROUGH))


def load_all_claims() -> list[Claim]:
    imported, notes = try_optional_claims()
    for note in notes:
        sys.stderr.write(f"[claimdesk] {note}\n")
    if imported:
        return sorted(imported, key=lambda c: c.id)
    return _load_fixture_claims()
