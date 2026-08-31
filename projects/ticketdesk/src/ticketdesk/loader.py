from __future__ import annotations

import json
from pathlib import Path

from ticketdesk.config import project_root
from ticketdesk.models import Order, Ticket


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


def load_all_tickets() -> list[Ticket]:
    folder = fixtures_dir() / "tickets"
    return [load_ticket(p.stem) for p in sorted(folder.glob("*.json"))]
