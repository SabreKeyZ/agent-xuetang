from __future__ import annotations

import csv
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from ticketdesk.config import project_root
from ticketdesk.models import SHOP_ID, Order, Ticket


def fixtures_dir() -> Path:
    return project_root() / "fixtures"


def load_roster() -> dict:
    path = fixtures_dir() / "roster.json"
    if not path.is_file():
        return {"l2": []}
    return json.loads(path.read_text(encoding="utf-8"))


def load_orders() -> dict[str, Order]:
    folder = fixtures_dir() / "orders"
    out: dict[str, Order] = {}
    if not folder.is_dir():
        return out
    for path in sorted(folder.glob("*.json")):
        order = Order.from_dict(json.loads(path.read_text(encoding="utf-8")))
        out[order.order_id] = order
    return out


def load_ticket(name: str) -> Ticket:
    folder = fixtures_dir() / "tickets"
    path = folder / f"{name}.json"
    if not path.is_file():
        path = folder / name
    data = json.loads(path.read_text(encoding="utf-8"))
    return Ticket.from_dict(data, fixture_id=path.stem)


# 工期走读工单置顶，避免按文件名排到辱骂单 T-1601。
_TICKET_WALKTHROUGH = ("T-1001", "T-1201", "T-1401", "T-1301")


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


def _split_list(raw: str) -> list[str]:
    text = (raw or "").strip()
    if not text:
        return []
    if text[0] in "[{":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return [text]
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
        return [str(parsed)]
    parts: list[str] = []
    for chunk in text.replace("|", ";").split(";"):
        item = chunk.strip()
        if item:
            parts.append(item)
    return parts


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
    for key in ("attachments", "labels"):
        if key in data and isinstance(data[key], str):
            data[key] = _split_list(data[key])
    for key in ("prior_actions", "messages"):
        if key in data and isinstance(data[key], str):
            data[key] = _maybe_json_list(data[key])
    if "unread" in data and isinstance(data["unread"], str):
        data["unread"] = data["unread"].strip().lower() in {"1", "true", "yes", "y"}
    return data


def tickets_from_csv(path: str | Path) -> list[Ticket]:
    """把 CSV 行映射到现有 Ticket。列名对齐 fixtures 字段。"""
    target = Path(path)
    if not target.is_file():
        raise FileNotFoundError(f"工单 CSV 不是文件或不存在：{target}")
    tickets: list[Ticket] = []
    with target.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"工单 CSV 没有表头：{target}")
        for row in reader:
            mapping = _csv_row_to_mapping(row)
            if not mapping:
                continue
            fixture_id = str(mapping.get("fixture_id") or target.stem)
            tickets.append(Ticket.from_dict(mapping, fixture_id=fixture_id))
    if not tickets:
        raise ValueError(f"工单 CSV 没有有效行：{target}")
    return tickets


def tickets_from_dir(folder: str | Path) -> list[Ticket]:
    """本地目录里的 *.json，字段走 Ticket.from_dict，不另起一套模型。"""
    target = Path(folder)
    if not target.is_dir():
        raise FileNotFoundError(f"工单目录不存在：{target}")
    tickets: list[Ticket] = []
    for path in sorted(target.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                raise ValueError(f"目录 JSON 必须是对象或对象列表：{path}")
            fixture_id = str(item.get("fixture_id") or path.stem)
            tickets.append(Ticket.from_dict(item, fixture_id=fixture_id))
    if not tickets:
        raise ValueError(f"工单目录里没有有效 JSON：{target}")
    return tickets


def tickets_from_github_issues(issues: list[dict[str, Any]]) -> list[Ticket]:
    """只读 Issues JSON → Ticket。不写仓库、不打款。"""
    tickets: list[Ticket] = []
    for issue in issues:
        if not isinstance(issue, dict) or "pull_request" in issue:
            continue
        number = issue.get("number")
        user = issue.get("user") or {}
        login = str(user.get("login") or "github")
        labels = []
        for lab in issue.get("labels") or []:
            if isinstance(lab, dict) and lab.get("name"):
                labels.append(str(lab["name"]))
            elif isinstance(lab, str):
                labels.append(lab)
        created = str(issue.get("created_at") or "")
        data = {
            "id": f"GH-{number}" if number is not None else str(issue.get("id") or ""),
            "channel": "GitHub",
            "created_at": created,
            "now": str(issue.get("updated_at") or created),
            "order_id": "",
            "shop_id": SHOP_ID,
            "customer_id": f"gh_{login}",
            "customer_name": login,
            "amount_yuan": 0,
            "refund_yuan": 0,
            "attachments": [],
            "prior_actions": [],
            "title": str(issue.get("title") or ""),
            "body": str(issue.get("body") or ""),
            "labels": labels,
            "sla_minutes": 24 * 60,
            "priority": "P2",
            "fixture_id": f"github-{number}" if number is not None else "github",
        }
        tickets.append(Ticket.from_dict(data, fixture_id=str(data["fixture_id"])))
    if not tickets:
        raise ValueError("GitHub Issues 列表里没有可映射的工单")
    return tickets


def fetch_github_issues(repo: str, token: str) -> list[dict[str, Any]]:
    """GET /repos/{owner}/{repo}/issues。只读；Token 缺失由调用方拦截。"""
    name = (repo or "").strip().strip("/")
    if "/" not in name:
        raise ValueError(f"TICKETDESK_GITHUB_REPO 应为 owner/repo，收到：{repo!r}")
    owner, repo_name = name.split("/", 1)
    url = (
        f"https://api.github.com/repos/{owner}/{repo_name}/issues"
        "?state=open&per_page=30"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ticketdesk-readonly-import",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise ValueError(f"GitHub Issues 只读拉取失败 HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"GitHub Issues 只读拉取失败：{exc.reason}") from exc
    if not isinstance(payload, list):
        raise ValueError("GitHub Issues 响应不是列表")
    return [item for item in payload if isinstance(item, dict)]


def tickets_from_github(repo: str, token: str) -> list[Ticket]:
    if not (token or "").strip():
        raise PermissionError("GITHUB_TOKEN 未设置，跳过 Issues 导入")
    return tickets_from_github_issues(fetch_github_issues(repo, token))


def try_optional_tickets() -> tuple[list[Ticket] | None, list[str]]:
    """有配置则尝试导入；缺文件 / 无 Token / 拉失败返回 None，由调用方回退夹具。"""
    notes: list[str] = []
    csv_raw = os.environ.get("TICKETDESK_IMPORT_CSV", "").strip()
    dir_raw = os.environ.get("TICKETDESK_IMPORT_DIR", "").strip()
    repo = os.environ.get("TICKETDESK_GITHUB_REPO", "").strip()
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not csv_raw and not dir_raw and not repo:
        return None, notes

    collected: list[Ticket] = []
    if csv_raw:
        try:
            collected.extend(tickets_from_csv(resolve_optional_path(csv_raw)))
        except (OSError, ValueError, json.JSONDecodeError, csv.Error) as exc:
            notes.append(f"CSV 导入失败，忽略：{exc}")
    if dir_raw:
        try:
            collected.extend(tickets_from_dir(resolve_optional_path(dir_raw)))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            notes.append(f"目录导入失败，忽略：{exc}")
    if repo:
        if not token:
            notes.append("已设 TICKETDESK_GITHUB_REPO 但无 GITHUB_TOKEN，跳过 Issues。")
        else:
            try:
                collected.extend(tickets_from_github(repo, token))
            except (OSError, ValueError, PermissionError, json.JSONDecodeError) as exc:
                notes.append(f"GitHub Issues 导入失败，忽略：{exc}")
    if collected:
        return collected, notes
    notes.append("可选导入没有有效工单，回退 fixtures/。")
    return None, notes


def _load_fixture_tickets() -> list[Ticket]:
    folder = fixtures_dir() / "tickets"
    tickets = [load_ticket(p.stem) for p in folder.glob("*.json")]
    return sorted(tickets, key=lambda t: _walkthrough_key(t.id, _TICKET_WALKTHROUGH))


def load_all_tickets() -> list[Ticket]:
    imported, notes = try_optional_tickets()
    for note in notes:
        sys.stderr.write(f"[ticketdesk] {note}\n")
    if imported:
        return sorted(imported, key=lambda t: t.id)
    return _load_fixture_tickets()
