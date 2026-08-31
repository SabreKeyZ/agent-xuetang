from __future__ import annotations

from ticketdesk.clock import days_between
from ticketdesk.models import Ticket

CUSTOMER_ROLES = {"customer", "顾客", "guest", "user"}
QUALITY_HINTS = ("漏液", "破损", "质量", "裂了", "发霉", "划痕", "坏了", "开箱破")
NO_REASON_HINTS = ("不想要了", "不喜欢", "用不上", "无理由")
# 先剥否定再匹配「退货」，避免「不用退货」被当成退货退款。
NEGATED_RETURN_PHRASES = (
    "不需要退货",
    "不用退货",
    "无需退货",
    "不要退货",
    "不必退货",
    "无须退货",
    "不用退",
    "不退货",
)


def last_customer_text(ticket: Ticket) -> str:
    """分类只看最后一轮顾客话。无 messages 时退回 title+body。"""
    last = ""
    for row in ticket.messages or []:
        if str(row.get("role") or "") in CUSTOMER_ROLES:
            last = str(row.get("body") or "")
    if last.strip():
        return last
    return f"{ticket.title}{ticket.body}"


def mentions_return_goods(blob: str) -> bool:
    """肯定要退货才算。否定短语里的「退货」两字不算。"""
    cleaned = blob or ""
    for phrase in NEGATED_RETURN_PHRASES:
        cleaned = cleaned.replace(phrase, "")
    return "退货退款" in cleaned or "退货" in cleaned


def infer_after_sales_type(ticket: Ticket, text: str = "") -> str:
    if ticket.after_sales_type.strip():
        return ticket.after_sales_type.strip()
    blob = text or last_customer_text(ticket)
    if any(w in blob for w in ("换货", "换一个", "换成")):
        return "换货"
    if mentions_return_goods(blob):
        return "退货退款"
    if any(w in blob for w in ("仅退款", "未发货", "还没发货", "取消订单")):
        return "仅退款"
    if ticket.refund_yuan > 0:
        return "仅退款"
    return ""


def seven_day_no_reason_late(ticket: Ticket, order: dict | None) -> bool:
    signed = str((order or {}).get("signed_at") or "")
    if not signed:
        return False
    text = last_customer_text(ticket)
    if any(h in text for h in QUALITY_HINTS):
        return False
    if not any(h in text for h in NO_REASON_HINTS):
        return False
    return days_between(signed, ticket.now) > 7


def return_ready(ticket: Ticket, order: dict | None) -> bool:
    track = ticket.return_tracking or str((order or {}).get("return_tracking") or "")
    inbound = str((order or {}).get("inbound_at") or "")
    return bool(track.strip() or inbound.strip())


def paid_yuan(order: dict | None) -> float:
    if not order:
        return 0.0
    if order.get("paid_yuan") not in (None, ""):
        return float(order.get("paid_yuan") or 0)
    lines = order.get("lines") or []
    if lines:
        return sum(float(x.get("paid_yuan") or 0) for x in lines)
    return float(order.get("amount_yuan") or 0)


def broken_line(ticket: Ticket, order: dict | None) -> dict | None:
    lines = list((order or {}).get("lines") or [])
    if len(lines) < 2:
        return None
    text = last_customer_text(ticket)
    near = []
    mentioned = []
    for ln in lines:
        sku = str(ln.get("sku") or "")
        if not sku or sku not in text:
            continue
        mentioned.append(ln)
        start = 0
        while True:
            idx = text.find(sku, start)
            if idx < 0:
                break
            after = text[idx + len(sku) : idx + len(sku) + 6]
            if any(w in after for w in ("裂", "坏了", "漏液", "破损", "发霉", "划痕")):
                near.append(ln)
                break
            start = idx + 1
    if len(near) == 1:
        return near[0]
    if len(mentioned) == 1:
        return mentioned[0]
    return None


def policy_says_coupon(policy: dict) -> bool:
    cites = " ".join(policy.get("citations") or [])
    quotes = " ".join(str(q.get("quote") or "") for q in policy.get("quotes") or [])
    return "券" in cites + quotes
