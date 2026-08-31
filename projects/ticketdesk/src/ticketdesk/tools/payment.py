from __future__ import annotations

from ticketdesk.safety import NEVER_PAY

# 形状像生产退款接口。演示永远不打款。
DEMO_FORBIDS_CONFIRM = True


def refund(amount_yuan: float, idempotency_key: str, confirm: bool = False) -> dict:
    if NEVER_PAY or DEMO_FORBIDS_CONFIRM or not confirm:
        return {
            "ok": False,
            "status": "confirm_required",
            "executed": False,
            "amount_yuan": amount_yuan,
            "idempotency_key": idempotency_key,
            "message": "退款接口存在，但必须人点执行。演示模式不接受 confirm=true。",
        }
    return {
        "ok": False,
        "status": "demo_forbidden",
        "executed": False,
        "amount_yuan": amount_yuan,
        "idempotency_key": idempotency_key,
    }


def coupon(amount_yuan: float, idempotency_key: str, confirm: bool = False) -> dict:
    """活动补偿券。形状像发券接口，演示同样不执行。"""
    probe = refund(amount_yuan, idempotency_key, confirm=confirm)
    probe["kind"] = "coupon"
    probe["message"] = "补偿券须人点执行。演示不发券、不打款。"
    return probe
