from __future__ import annotations

from claimdesk.models import DEDUCTIBLE, LIMITS, Claim


def shop_refund_yuan(claim: Claim) -> float:
    return sum(float(a.get("amount_yuan") or 0) for a in claim.prior_actions if a.get("type") == "shop_refund")


def settle(claim: Claim) -> dict:
    limit = LIMITS.get(claim.product, 80.0)
    deductible = DEDUCTIBLE.get(claim.product, 0.0)
    shop = shop_refund_yuan(claim)
    offset = min(shop, float(claim.amount_yuan))
    suggested = max(0.0, float(claim.amount_yuan) - deductible - offset)
    suggested = min(suggested, limit)
    return {
        "amount_yuan": float(claim.amount_yuan),
        "deductible": deductible,
        "shop_refund_yuan": shop,
        "shop_offset": offset,
        "limit": limit,
        "suggested_yuan": suggested,
        "formula": (
            f"max(0, {claim.amount_yuan:.2f} - {deductible:.2f} - {offset:.2f}) "
            f"= {suggested:.2f}（保额¥{limit:.0f}）"
        ),
    }


def case_status(recommendation: str, docs_complete: bool) -> str:
    if recommendation == "补件":
        return "补件中"
    if recommendation in {"通过", "差额"}:
        return "待人打款"
    if recommendation == "复议":
        return "待核赔"
    if recommendation in {"拒赔", "拒审"}:
        return "结案"
    if docs_complete:
        return "待核赔"
    return "立案"
