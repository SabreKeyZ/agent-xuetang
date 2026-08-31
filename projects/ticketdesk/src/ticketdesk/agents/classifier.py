from __future__ import annotations

from ticketdesk.models import Ticket
from ticketdesk.safety import looks_abuse, looks_dangerous
from ticketdesk.tools.duplicates import find_duplicates
from ticketdesk.tools.history import by_customer
from ticketdesk.tools.orders import lookup_order


TYPE_HINTS = (
    ("辱骂升级", ("找消协", "找律师", "律师函", "投诉工商", "垃圾客服", "傻逼", "智障")),
    ("命令风险", ("curl | sh", "os.system", "refund_api", "alipay.trade.refund")),
    ("物流延误", ("物流", "快递", "揽收", "轨迹", "没动", "延误", "还没到")),
    ("质量", ("漏液", "破损", "质量", "裂了", "发霉")),
    ("退款", ("退款", "退货", "退钱", "不想要了")),
    ("投诉", ("投诉", "态度", "差评")),
)


class Classifier:
    name = "classifier"

    def run(self, ticket: Ticket, catalog: list[Ticket], orders: dict | None = None) -> dict:
        order = lookup_order(ticket.order_id, orders)
        dup = find_duplicates(ticket, catalog)
        history = by_customer(ticket.customer_id, catalog, ticket.now, window_minutes=120)
        refund_burst = sum(1 for row in history if float(row.get("refund_yuan") or 0) > 0)
        kind = self._kind(ticket, order, dup, refund_burst)
        urgency = self._urgency(ticket, kind, dup)
        labels = [kind, ticket.priority, urgency]
        if dup["is_burst"]:
            labels.append("重复单")
        if refund_burst >= 2 and kind not in {"信息不全", "重复单"}:
            labels.append("刷单嫌疑")
        cites = [s["citation"] for s in dup.get("similar") or []]
        cites.extend(s["citation"] for s in dup.get("burst") or [])
        return {
            "role": self.name,
            "title": f"{kind} · {urgency}",
            "kind": kind,
            "urgency": urgency,
            "labels": labels,
            "order": order,
            "duplicates": dup,
            "history_count": len(history),
            "refund_burst": refund_burst,
            "citations": cites,
            "abuse": looks_abuse(ticket.title + ticket.body),
            "dangerous": looks_dangerous(ticket.title + "\n" + ticket.body),
        }

    def _kind(self, ticket: Ticket, order: dict, dup: dict, refund_burst: int) -> str:
        if not ticket.order_id.strip() or order.get("reason") in {"missing_order_id", "not_found", "wrong_shop"}:
            return "信息不全"
        blob = ticket.title + ticket.body
        if looks_abuse(blob):
            return "辱骂升级"
        if looks_dangerous(blob):
            return "命令风险"
        if dup["is_burst"]:
            return "重复单"
        if refund_burst >= 2 and ticket.refund_yuan > 0:
            return "风控"
        for kind, hints in TYPE_HINTS:
            if any(h in blob for h in hints):
                return kind
        if ticket.refund_yuan > 0:
            return "退款"
        return "投诉"

    def _urgency(self, ticket: Ticket, kind: str, dup: dict) -> str:
        if ticket.priority == "P0" or kind in {"辱骂升级", "命令风险"}:
            return "高"
        if ticket.refund_yuan > 200 or kind == "风控" or dup["is_burst"]:
            return "高"
        if kind in {"质量", "投诉", "物流延误"}:
            return "中"
        return "低"
