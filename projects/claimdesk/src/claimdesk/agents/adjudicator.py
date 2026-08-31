from __future__ import annotations

from claimdesk.clock import days_between
from claimdesk.models import LIMITS, Claim
from claimdesk.tools.payment import payout


class Adjudicator:
    name = "adjudicator"

    def run(self, claim: Claim, docs: dict, clause: dict, catalog: list[Claim]) -> dict:
        cites = list(clause.get("citations") or [])
        key = f"qingtu:payout:{claim.id}:{int(round(claim.amount_yuan * 100))}"
        probe = payout(claim.amount_yuan, key, confirm=False)
        shared = _shared_photos(claim, catalog)
        limit = LIMITS.get(claim.product, 80.0)
        window = 15 if clause.get("version") == "v2" else 7
        late = days_between(claim.incident_at, claim.filed_at) > window
        shop_paid = [a for a in claim.prior_actions if a.get("type") == "shop_refund"]
        identity_bad = claim.claimant_id != claim.insured_id
        exclusion = _exclusion(claim)

        rec = "通过"
        title = "通过建议 · 仍不打款"
        next_action = "wait_human_confirm"
        refused = False
        banner = ""
        letter = ""

        if clause.get("refused") or not cites:
            rec, title, next_action, refused = "拒审", "没有引用，就先不答", "refuse", True
            banner = "没有引用，就先不答"
        elif identity_bad:
            rec, title, next_action, refused = "拒赔", "代索赔 · 身份闸门", "human_queue", True
            banner = "索赔人不是投保人，升级人工，不通过。"
            letter = "请投保人本人申请。代办须先过身份闸门。"
        elif shared:
            rec, title, next_action, refused = "拒赔", "重复现场图 · 欺诈线索", "human_queue", True
            banner = "同一张图出现在两起案件，升级人工，不通过。"
            letter = f"影像 {shared[0]} 与其他案件重复。按条款 5.2 转人工。"
        elif docs.get("missing"):
            rec, title, next_action, refused = "补件", "缺件 · 不审结", "supplement", True
            banner = "材料不齐，只出补件清单。"
            letter = "请补： " + "、".join(docs["missing"]) + "。本次不审结。"
        elif late:
            rec, title, next_action, refused = "拒赔", "超索赔窗口", "deny", True
            letter = f"出险日至申请已超过 {window} 日（适用 {clause.get('version')}）。"
        elif exclusion:
            rec, title, next_action, refused = "拒赔", f"除外责任 · {exclusion}", "deny", True
            letter = f"出险叙述命中除外（{exclusion}）。建议拒赔，须人确认。"
        elif shop_paid:
            rec, title, next_action, refused = "拒赔", "店铺已退 · 双重受偿", "deny_or_offset", True
            letter = f"店铺已退 ¥{shop_paid[0].get('amount_yuan')}。保险再赔即双重受偿，建议冲减或拒。"
        elif claim.amount_yuan > limit:
            rec, title, next_action, refused = "拒赔", "超保额", "deny", True
            letter = f"申请 ¥{claim.amount_yuan:.2f}，超过 {claim.product} 限额 ¥{limit:.0f}。"
        else:
            letter = (
                f"材料齐、条款覆盖、金额 ¥{claim.amount_yuan:.2f} 未超限。"
                "核赔建议：通过。payout 须人点执行，演示不打款。"
            )

        return {
            "role": self.name,
            "title": title,
            "recommendation": rec,
            "next_action": next_action,
            "refused": refused,
            "banner": banner,
            "decision_letter": letter,
            "executed": False,
            "requires_human": True,
            "idempotency_key": key,
            "payout": probe,
            "citations": cites,
            "enabled": bool(cites) and rec in {"通过", "补件", "拒赔"},
        }


def _exclusion(claim: Claim) -> str:
    text = claim.narrative
    if any(w in text for w in ("易碎", "陶瓷", "玻璃", "墨水瓶", "墨水碎")):
        return "易碎"
    if "延误" in text and "破损" not in text and "丢失" not in text:
        return "延误不赔"
    if "自行丢弃" in text or "扔掉" in text:
        return "自行丢弃"
    return ""


def _shared_photos(claim: Claim, catalog: list[Claim]) -> list[str]:
    mine = {str(a.get("file_id") or a.get("name")) for a in claim.attachments}
    hits = []
    for other in catalog:
        if other.id == claim.id:
            continue
        theirs = {str(a.get("file_id") or a.get("name")) for a in other.attachments}
        overlap = [x for x in mine & theirs if x]
        hits.extend(overlap)
    return hits
