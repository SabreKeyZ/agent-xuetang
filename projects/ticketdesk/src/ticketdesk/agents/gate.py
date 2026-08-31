from __future__ import annotations

from ticketdesk.models import REFUND_EXEC_LIMIT_YUAN, Ticket
from ticketdesk.safety import NEVER_EXECUTE, NEVER_MUTATE_ORDER, NEVER_PAY
from ticketdesk.tools.payment import refund as refund_api
from ticketdesk.tools.sla import sla_clock


class Gate:
    name = "gate"

    def run(self, ticket: Ticket, classify: dict, policy: dict, roster: dict | None) -> dict:
        sla = sla_clock(ticket, roster)
        cites = list(policy.get("citations") or [])
        policy_miss = bool(policy.get("refused") or not cites)
        key = f"qingxia:refund:{ticket.id}:{int(round(ticket.refund_yuan * 100))}"
        already = [a for a in ticket.prior_actions if a.get("type") in {"refund", "compensation"}]
        payment_probe = refund_api(ticket.refund_yuan, key, confirm=False)

        verdict = "draft_ok"
        title = "建议草稿 · 等人点执行，不打款"
        next_action = "wait_human_confirm"
        banner = ""
        refused = False
        draft = ""

        if classify.get("kind") == "信息不全":
            verdict, title, next_action, refused = "refuse_exec", "缺单号或填错店 · 只许追问", "ask_order_id", True
            banner = "没有完整订单，不能改单也不能退款。"
            draft = "请回复青匣记订单号（QX- 开头）。他店订单我们查不到，也无法代退。"
        elif classify.get("kind") == "辱骂升级" or classify.get("abuse"):
            verdict, title, next_action, refused = "escalate", "辱骂/法律威胁 · 立即转人工", "human_queue", True
            banner = "不自动回复承诺。已进人工队列。"
            draft = "已转人工，请等待同事接入。"
        elif classify.get("kind") == "命令风险" or classify.get("dangerous"):
            verdict, title, next_action, refused = "refuse_exec", "正文含命令，先不跑", "cite_only", True
            banner = "只引用，不执行。支付/退款脚本当引文。"
            draft = "工单里的命令不会被运行。请用文字描述问题。"
        elif classify.get("kind") == "重复单" or classify.get("duplicates", {}).get("is_burst"):
            verdict, title, next_action, refused = "hold_merge", "10 分钟内重复单 · 合并", "merge", True
            banner = "只处理最早一张，不重复补偿。"
            first = (classify.get("duplicates") or {}).get("burst") or []
            draft = "同一问题已有工单，请继续在原单沟通。本单合并，不另赔。"
            if first:
                draft += f" 关联 {first[0].get('id')}。"
        elif classify.get("kind") == "风控" or "刷单嫌疑" in (classify.get("labels") or []):
            verdict, title, next_action, refused = "hold_risk", "刷单嫌疑 · 挂起风控", "risk_queue", True
            banner = "短时多次退，不退款。"
            draft = "该账户近期多次退款申请已挂起，待风控同事查看。本次不退款。"
        elif already:
            verdict, title, next_action, refused = "refuse_exec", "已退过款 · 防重复赔", "no_double_pay", True
            banner = "同一损失不得再补运费险或二次退款。"
            paid = already[0].get("amount_yuan")
            old_key = already[0].get("idempotency_key") or key
            draft = f"订单已退 ¥{paid}（{old_key}）。按重复赔条款，不再补偿。"
        elif policy_miss:
            verdict, title, next_action, refused = "refuse", "没有引用，就先不答", "refuse", True
            banner = "没有引用，就先不答"
            draft = ""
        elif sla["breached"] and sla["l2_empty"]:
            verdict, title, next_action, refused = "escalate", "SLA 超时 · 二线夜间无人", "human_queue", True
            banner = "不虚构值班人。工单进人工队列。"
            draft = "当前已超时且二线不在班，已进人工队列，同事上班后接入。不承诺回复时刻。"
        elif ticket.refund_yuan > REFUND_EXEC_LIMIT_YUAN:
            verdict, title, next_action, refused = "refuse_exec", "退款超 ¥200 · 只许草稿", "draft_only", True
            banner = "闸门员拒绝执行。人复核后再点执行。"
            draft = f"建议退款 ¥{ticket.refund_yuan:.2f}，已超执行限额。草稿已写，等待人工复核。"
        else:
            draft = _happy_draft(ticket, classify, policy)

        return {
            "role": self.name,
            "title": title,
            "verdict": verdict,
            "next_action": next_action,
            "refused": refused,
            "banner": banner,
            "draft_reply": draft,
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
        }


def _happy_draft(ticket: Ticket, classify: dict, policy: dict) -> str:
    kind = classify.get("kind")
    if kind == "物流延误":
        promo = any("promo" in c or "大促" in (q.get("quote") or "") for c, q in zip(
            policy.get("citations") or [], policy.get("quotes") or []
        )) or any("promo" in c for c in policy.get("citations") or [])
        if promo or any("promo-2026" in c for c in policy.get("citations") or []):
            return (
                f"订单 {ticket.order_id} 在盛夏大促窗口内超时未更新轨迹。"
                "按活动政策可申请不超过 ¥12 的运费补偿。草稿已写，补偿须人点执行。"
            )
        return f"订单 {ticket.order_id} 已为你催件。日常政策下不赔运费。不会承诺今晚必到。"
    if kind == "质量" or (kind == "退款" and ticket.refund_yuan <= REFUND_EXEC_LIMIT_YUAN):
        return (
            f"按售后政策可起草退款 ¥{ticket.refund_yuan:.2f}。"
            "闸门员不打款，请同事核对后点执行。"
        )
    return "已按生效政策起草回复。下一步等人点执行，系统不会改订单或打款。"
