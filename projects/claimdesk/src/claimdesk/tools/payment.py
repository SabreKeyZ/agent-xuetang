from __future__ import annotations

NEVER_PAYOUT = True
DEMO_FORBIDS_CONFIRM = True


def payout(amount_yuan: float, idempotency_key: str, confirm: bool = False) -> dict:
    if NEVER_PAYOUT or DEMO_FORBIDS_CONFIRM or not confirm:
        return {
            "ok": False,
            "status": "confirm_required",
            "executed": False,
            "amount_yuan": amount_yuan,
            "idempotency_key": idempotency_key,
            "message": "payout 接口存在，必须人确认。演示模式不打款。",
        }
    return {"ok": False, "status": "demo_forbidden", "executed": False, "idempotency_key": idempotency_key}
