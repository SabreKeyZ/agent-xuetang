from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SHOP_ID = "qingxia"
REFUND_EXEC_LIMIT_YUAN = 200.0


@dataclass
class Ticket:
    id: str
    channel: str
    created_at: str
    now: str
    order_id: str
    shop_id: str
    customer_id: str
    customer_name: str
    amount_yuan: float
    refund_yuan: float
    attachments: list[str]
    prior_actions: list[dict[str, Any]]
    title: str
    body: str
    labels: list[str]
    sla_minutes: int
    priority: str
    fixture_id: str = ""
    unread: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any], fixture_id: str = "") -> "Ticket":
        return cls(
            id=str(data.get("id") or ""),
            channel=str(data.get("channel") or "在线客服"),
            created_at=str(data.get("created_at") or ""),
            now=str(data.get("now") or data.get("created_at") or ""),
            order_id=str(data.get("order_id") or ""),
            shop_id=str(data.get("shop_id") or SHOP_ID),
            customer_id=str(data.get("customer_id") or ""),
            customer_name=str(data.get("customer_name") or ""),
            amount_yuan=float(data.get("amount_yuan") or 0),
            refund_yuan=float(data.get("refund_yuan") or 0),
            attachments=[str(x) for x in data.get("attachments") or []],
            prior_actions=list(data.get("prior_actions") or []),
            title=str(data.get("title") or ""),
            body=str(data.get("body") or ""),
            labels=[str(x) for x in data.get("labels") or []],
            sla_minutes=int(data.get("sla_minutes") or 24 * 60),
            priority=str(data.get("priority") or "P2"),
            fixture_id=fixture_id or str(data.get("fixture_id") or ""),
            unread=bool(data.get("unread", True)),
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Order:
    order_id: str
    shop_id: str
    customer_id: str
    placed_at: str
    amount_yuan: float
    sku: str
    tracking: str
    last_scan_at: str
    status: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Order":
        return cls(
            order_id=str(data.get("order_id") or ""),
            shop_id=str(data.get("shop_id") or ""),
            customer_id=str(data.get("customer_id") or ""),
            placed_at=str(data.get("placed_at") or ""),
            amount_yuan=float(data.get("amount_yuan") or 0),
            sku=str(data.get("sku") or ""),
            tracking=str(data.get("tracking") or ""),
            last_scan_at=str(data.get("last_scan_at") or ""),
            status=str(data.get("status") or ""),
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
