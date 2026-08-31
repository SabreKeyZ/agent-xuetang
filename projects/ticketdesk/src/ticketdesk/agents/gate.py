from __future__ import annotations

import re

from ticketdesk.aftersales import (
    broken_line,
    infer_after_sales_type,
    last_customer_text,
    paid_yuan,
    policy_says_coupon,
    return_ready,
    seven_day_no_reason_late,
)
from ticketdesk.models import REFUND_EXEC_LIMIT_YUAN, Ticket
from ticketdesk.safety import NEVER_EXECUTE, NEVER_MUTATE_ORDER, NEVER_PAY
from ticketdesk.tools.payment import coupon as coupon_api
from ticketdesk.tools.payment import refund as refund_api
from ticketdesk.tools.sla import sla_clock

_OPERATOR_TOKEN = re.compile(
    r"[（(]?\b(?:qingxia:(?:refund|coupon)|qingtu:payout):[A-Za-z0-9_.:-]+[)）]?"
)


def strip_operator_tokens(text: str) -> str:
    """对客草稿不得出现幂等钥匙。对内备注 / 审计 JSON 可以留。"""
    cleaned = _OPERATOR_TOKEN.sub("", text or "")
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = cleaned.replace(" 。", "。").replace("（）", "").replace("()", "")
    return cleaned.strip()


class Gate:
    name = "gate"

    def run(self, ticket: Ticket, classify: dict, policy: dict, roster: dict | None) -> dict:
        sla = sla_clock(ticket, roster)
        cites = list(policy.get("citations") or [])
        policy_miss = bool(policy.get("refused") or not cites)
        order = (classify.get("order") or {}).get("order") or {}
        after_type = classify.get("after_sales_type") or infer_after_sales_type(ticket)
        line = broken_line(ticket, order)
        paid = paid_yuan(order)
        coupon = classify.get("kind") == "物流延误" and policy_says_coupon(policy)
        key_kind = "coupon" if coupon else "refund"
        key = f"qingxia:{key_kind}:{ticket.id}:{int(round(ticket.refund_yuan * 100))}"
        already = [a for a in ticket.prior_actions if a.get("type") in {"refund", "compensation"}]
        payment_probe = (
            coupon_api(12.0, key, confirm=False) if coupon else refund_api(ticket.refund_yuan, key, confirm=False)
        )

        verdict = "draft_ok"
        title = "建议草稿 · 等人点执行，不打款"
        next_action = "wait_human_confirm"
        banner = ""
        refused = False
        draft = ""
        internal = ""

        if classify.get("kind") == "信息不全":
            verdict, title, next_action, refused = "refuse_exec", "缺单号或填错店 · 只许追问", "ask_order_id", True
            banner = "没有完整订单，不能改单也不能退款。"
            draft = "请回复青匣记订单号（QX- 开头）。他店订单我们查不到，也无法代退。"
            internal = "对内：缺单号或填错店，只许追问，不退款。"
        elif classify.get("kind") == "辱骂升级" or classify.get("abuse"):
            verdict, title, next_action, refused = "escalate", "辱骂/法律威胁 · 立即转人工", "human_queue", True
            banner = "不自动回复承诺。已进人工队列。"
            draft = "已转人工，请等待同事接入。"
            hits = classify.get("abuse") or []
            internal = f"对内：辱骂/法律威胁 {hits}。勿对客承诺时效或赔偿。升级 L2。"
        elif classify.get("kind") == "命令风险" or classify.get("dangerous"):
            verdict, title, next_action, refused = "refuse_exec", "正文含命令，先不跑", "cite_only", True
            banner = "只引用，不执行。支付/退款脚本当引文。"
            draft = "工单里的命令不会被运行。请用文字描述问题。"
            internal = f"对内：正文命中 {classify.get('dangerous')}。NEVER_EXECUTE。"
        elif classify.get("kind") == "重复单" or classify.get("duplicates", {}).get("is_burst"):
            verdict, title, next_action, refused = "hold_merge", "10 分钟内重复单 · 合并", "merge", True
            banner = "只处理最早一张，不重复补偿。"
            first = (classify.get("duplicates") or {}).get("burst") or []
            draft = "同一问题已有工单，请继续在原单沟通。本单合并，不另赔。"
            if first:
                draft += f" 关联 {first[0].get('id')}。"
            internal = "对内：重复单合并，不重复补偿。"
        elif classify.get("kind") == "风控" or "刷单嫌疑" in (classify.get("labels") or []):
            verdict, title, next_action, refused = "hold_risk", "刷单嫌疑 · 挂起风控", "risk_queue", True
            banner = "短时多次退，不退款。"
            draft = "该账户近期多次退款申请已挂起，待风控同事查看。本次不退款。"
            internal = "对内：2 小时内多次退，挂起风控，不对客解释模型细节。"
        elif already:
            verdict, title, next_action, refused = "refuse_exec", "已退过款 · 防重复赔", "no_double_pay", True
            banner = "同一损失不得再补运费险或二次退款。"
            paid_old = already[0].get("amount_yuan")
            old_key = already[0].get("idempotency_key") or key
            draft = f"订单已退 ¥{paid_old}。按重复赔条款，不再补偿。"
            internal = f"对内：prior_actions 已有退款 ¥{paid_old}，钥匙 {old_key}，防重复赔。"
        elif policy_miss:
            verdict, title, next_action, refused = "refuse", "没有引用，就先不答", "refuse", True
            banner = "没有引用，就先不答"
            draft = ""
            internal = "对内：政策零命中，红条拒答。"
        elif after_type == "换货" or classify.get("kind") == "换货":
            verdict, title, next_action, refused = "refuse_exec", "换货不退现金", "exchange_only", True
            banner = "换货不打款。只许安排换货草稿。"
            draft = f"订单 {ticket.order_id} 按换货处理，不退现金。请保留包装，等待换货单。须人确认。"
            internal = "对内：换货路径，refund_yuan 忽略，NEVER_PAY。"
        elif (after_type == "退货退款" or classify.get("kind") == "退货退款") and not return_ready(ticket, order):
            verdict, title, next_action, refused = "refuse_exec", "退货未入库 · 只许草稿/追问", "ask_return", True
            banner = "没有回寄单号或仓库 inbound_at，不能退款。"
            draft = "退货退款须先回寄。请回复快递单号；仓库签收入库前只许追问，不退款。"
            internal = "对内：退货退款缺 return_tracking / inbound_at，禁止打款。"
        elif classify.get("kind") == "七天无理由超时" or seven_day_no_reason_late(ticket, order):
            verdict, title, next_action, refused = "refuse_exec", "七天无理由已过 · 拒退", "deny_seven_day", True
            banner = "签收超过七日且叙述是不想要了，按售后政策拒退。"
            signed = order.get("signed_at") or ""
            draft = (
                f"订单 {ticket.order_id} 已于 {signed[:10] or '签收日'} 签收，"
                "超过七日无理由时限。仅因「不想要了」不能退款。质量问题请另附开箱照片走质量条款。"
            )
            internal = "对内：七天无理由时钟已过；质量条款仍可走，本单叙述不是质量。"
        elif paid and ticket.refund_yuan > paid + 0.001:
            verdict, title, next_action, refused = "refuse_exec", "超过实付 · 不得按原价", "cap_paid", True
            banner = "退款不得超过优惠后实付。"
            draft = (
                f"本单实付 ¥{paid:.2f}（优惠后），不能按原价退 ¥{ticket.refund_yuan:.2f}。"
                "请按实付起草。须人复核，不打款。"
            )
            internal = f"对内：refund_yuan={ticket.refund_yuan} > paid_yuan={paid}，卡实付上限。"
        elif line and ticket.refund_yuan > float(line.get("paid_yuan") or 0) + 0.001:
            line_paid = float(line.get("paid_yuan") or 0)
            verdict, title, next_action, refused = "refuse_exec", "部分退 · 不得整单", "partial_line", True
            banner = "多 SKU 只退损坏行实付，不得整单。"
            draft = (
                f"订单有多件。损坏的是「{line.get('sku')}」，该行实付 ¥{line_paid:.2f}。"
                f"不能按整单 ¥{ticket.refund_yuan:.2f} 退。建议只退该行，须人确认。"
            )
            internal = f"对内：建议只退 {line.get('sku')} 实付 ¥{line_paid}，勿整单。"
        elif sla["resolution_breached"] and sla["l2_empty"]:
            verdict, title, next_action, refused = "escalate", "完结 SLA 超时 · 二线夜间无人", "human_queue", True
            banner = "不虚构值班人。工单进人工队列。"
            draft = "当前完结时限已到且二线不在班，已进人工队列，同事上班后接入。不承诺回复时刻。"
            internal = "对内：只升级完结时钟。首次响应超时夜间不单独升级。"
        elif ticket.refund_yuan > REFUND_EXEC_LIMIT_YUAN:
            verdict, title, next_action, refused = "refuse_exec", "退款超 ¥200 · 只许草稿", "draft_only", True
            banner = "闸门员拒绝执行。人复核后再点执行。"
            draft = f"建议退款 ¥{ticket.refund_yuan:.2f}，已超执行限额。草稿已写，等待人工复核。"
            internal = "对内：超 200 执行闸门，不得拆笔。"
        else:
            draft, internal = _happy_draft(ticket, classify, policy, after_type, coupon, order)
            if coupon:
                title = "建议发补偿券 · 须人确认，不打款"

        if not internal:
            internal = f"对内：verdict={verdict} kind={classify.get('kind')} 售后={after_type}。"
        if sla.get("first_response_breached") and not sla.get("resolution_breached"):
            internal += " 首次响应已超时，完结时钟未到；夜间 L2 空不因此升级。"

        return {
            "role": self.name,
            "title": title,
            "verdict": verdict,
            "next_action": next_action,
            "refused": refused,
            "banner": banner,
            "draft_reply": strip_operator_tokens(draft),
            "internal_note": internal,
            "after_sales_type": after_type,
            "compensation_kind": "coupon" if coupon else ("none" if after_type == "换货" else "cash"),
            "executed": False,
            "requires_human": True,
            "never_execute": NEVER_EXECUTE,
            "never_pay": NEVER_PAY,
            "never_mutate_order": NEVER_MUTATE_ORDER,
            "idempotency_key": key,
            "sla": sla,
            "payment": payment_probe,
            "citations": cites,
            "prior_paid": already,
            "suggested_refund_yuan": float((line or {}).get("paid_yuan") or 0) if line else min(ticket.refund_yuan, paid or ticket.refund_yuan),
            "last_customer_text": last_customer_text(ticket),
        }


def _happy_draft(ticket: Ticket, classify: dict, policy: dict, after_type: str, coupon: bool, order: dict) -> tuple[str, str]:
    kind = classify.get("kind")
    if kind == "未发货取消" or order.get("status") == "paid_unshipped":
        return (
            f"订单 {ticket.order_id} 尚未发货，可按仅退款起草 ¥{ticket.refund_yuan:.2f}。"
            "闸门员不打款，请同事核对后点执行。",
            "对内：paid_unshipped，仅退款草稿，仍不自动打款。",
        )
    if kind == "物流延误":
        if coupon or any("promo-2026" in c for c in policy.get("citations") or []):
            return (
                f"订单 {ticket.order_id} 在盛夏大促窗口内超时未更新轨迹。"
                "按活动政策发不超过 ¥12 的补偿券，不发现金。草稿已写，发券须人点执行。",
                "对内：活动物流走券，不走现金退款。须人点执行。",
            )
        return (
            f"订单 {ticket.order_id} 已为你催件。日常政策下不赔运费。不会承诺今晚必到。",
            "对内：日常物流催件，不赔运费。",
        )
    if kind in {"质量", "退货退款", "部分退"} or (kind == "退款" and ticket.refund_yuan <= REFUND_EXEC_LIMIT_YUAN):
        return (
            f"按售后政策可起草退款 ¥{ticket.refund_yuan:.2f}。"
            "闸门员不打款，请同事核对后点执行。",
            f"对内：{after_type or kind} 草稿，等人点执行。",
        )
    return (
        "已按生效政策起草回复。下一步等人点执行，系统不会改订单或打款。",
        "对内：默认草稿，NEVER_PAY。",
    )
