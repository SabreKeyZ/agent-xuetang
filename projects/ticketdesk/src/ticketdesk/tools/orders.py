from __future__ import annotations

from ticketdesk.loader import load_orders
from ticketdesk.models import SHOP_ID, Order


def lookup_order(order_id: str, catalog: dict[str, Order] | None = None) -> dict:
    """假的订单查询：形状像生产接口，读夹具。"""
    orders = catalog if catalog is not None else load_orders()
    oid = (order_id or "").strip()
    if not oid:
        return {"ok": False, "reason": "missing_order_id", "order": None}
    order = orders.get(oid)
    if order is None:
        return {"ok": False, "reason": "not_found", "order": None}
    payload = order.as_dict()
    if order.shop_id != SHOP_ID:
        return {"ok": False, "reason": "wrong_shop", "order": payload}
    return {"ok": True, "reason": "ok", "order": payload}
