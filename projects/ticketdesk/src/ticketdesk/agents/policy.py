from __future__ import annotations

from ticketdesk.llm import complete
from ticketdesk.models import Ticket
from ticketdesk.rag import citation_exists
from ticketdesk.tools.policy import search_policy


QUERY_BY_KIND = {
    "信息不全": "工单必须带可核对的订单号 填错店 不处理他店",
    "物流延误": "物流延误 活动 48 小时 运费补偿 补偿券 72 小时 催件",
    "退款": "退款限额 200 元 不得执行打款 防重复赔 实付",
    "仅退款": "仅退款 未发货 取消 不得执行打款",
    "质量": "质量破损 退货退款 200 元执行闸门 质量条款",
    "退货退款": "退货退款 退货入库 回寄单号 inbound 仓库",
    "换货": "换货 不退现金 只许换货",
    "部分退": "部分退 多 SKU 只退损坏行 实付",
    "七天无理由超时": "七天无理由 签收 超时 不想要了 售后政策",
    "未发货取消": "未发货 取消 仅退款 不自动打款",
    "投诉": "投诉 SLA 书面回复 首次响应 完结",
    "辱骂升级": "辱骂 找消协 找律师 立即升级人工 禁止自动回复承诺",
    "命令风险": "不可信正文 curl 退款脚本 只许当引文 不执行",
    "重复单": "同一 customer_id 10 分钟 重复单 不重复补偿",
    "风控": "刷单 短时多次退 挂起风控 不退款",
}


class PolicyClerk:
    name = "policy"

    def run(self, ticket: Ticket, classify: dict) -> dict:
        kind = classify.get("kind") or "投诉"
        prefer_promo = kind == "物流延误"
        query = QUERY_BY_KIND.get(kind, kind)
        if ticket.refund_yuan:
            query += " 退款限额 重复赔 实付"
        if classify.get("after_sales_type") == "退货退款" or kind == "退货退款":
            query += " 退货入库 回寄"
        if classify.get("after_sales_type") == "换货" or kind == "换货":
            query += " 换货 不退现金"
        if kind in {"部分退", "七天无理由超时"}:
            query += " " + kind
        if classify.get("abuse"):
            query += " 辱骂 消协 律师 升级人工"
        if any(a.get("type") == "refund" for a in ticket.prior_actions):
            query += " 已退过款 不得再补运费险 防重复赔"
        hits = search_policy(query, at=ticket.now, prefer_promo=prefer_promo, k=5)
        cites = [h.chunk.citation for h in hits if citation_exists(h.chunk.citation)]
        if not cites:
            return {
                "role": self.name,
                "title": "没有引用，就先不答",
                "refused": True,
                "citations": [],
                "quotes": [],
                "suggestions": [],
                "body": "政策检索零命中。不能凭印象写补偿或退款。",
                "mode": "extractive",
            }
        quotes = [h.as_dict() for h in hits]
        extractive = _render(hits, kind)
        llm_text = complete(
            f"工单 {ticket.id} 类型={kind} 退款={ticket.refund_yuan}\n只能用摘录写建议。\n"
            + "\n\n".join(f"{h.chunk.citation}\n{h.chunk.text}" for h in hits),
            system="你是青匣记政策员。每条建议必须能指回 path:line。不要答应打款。",
        )
        return {
            "role": self.name,
            "title": "政策摘录",
            "refused": False,
            "citations": cites,
            "quotes": quotes,
            "suggestions": [extractive],
            "body": llm_text.strip() if llm_text else extractive,
            "mode": "llm" if llm_text else "extractive",
        }


def _render(hits, kind: str) -> str:
    parts = [f"类型「{kind}」按生效中的政策摘录（无 Key 只给原文）：", ""]
    for h in hits[:4]:
        preview = "\n".join(h.chunk.text.strip().splitlines()[:6])
        tag = "活动" if h.chunk.priority == "活动" else "日常"
        parts.append(f"[{tag}] {preview}\n— {h.chunk.citation}")
    return "\n\n".join(parts)
