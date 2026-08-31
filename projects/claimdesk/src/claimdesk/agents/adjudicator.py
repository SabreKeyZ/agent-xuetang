from __future__ import annotations

from claimdesk.clock import days_between
from claimdesk.models import LIMITS, Claim
from claimdesk.settle import case_status, settle
from claimdesk.tools.payment import payout
from claimdesk.tools.tracking import lookup_tracking


class Adjudicator:
    name = "adjudicator"

    def run(self, claim: Claim, docs: dict, clause: dict, catalog: list[Claim]) -> dict:
        cites = list(clause.get("citations") or [])
        math = settle(claim)
        key = f"qingtu:payout:{claim.id}:{int(round(math['suggested_yuan'] * 100))}"
        probe = payout(math["suggested_yuan"], key, confirm=False)
        shared = _shared_photos(claim, catalog)
        limit = LIMITS.get(claim.product, 80.0)
        window = 15 if clause.get("version") == "v2" else 7
        late = days_between(claim.incident_at, claim.filed_at) > window
        identity_bad = claim.claimant_id != claim.insured_id
        exclusion = _exclusion(claim)
        appeal = _is_appeal(claim)
        track = lookup_tracking(claim.tracking or "")
        track_bad = _photo_signed_track_open(claim, track)

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
        elif track_bad:
            rec, title, next_action, refused = "补件", "轨迹未签收 · 照片不符", "supplement", True
            banner = "照片称签收但轨迹未签收，补件或升级，不通过。"
            last = (track.get("tracking") or {}).get("last_scan") or (track.get("tracking") or {}).get("status")
            letter = f"附件称已签收，轨迹状态为 {last or '未签收'}。按条款 3.5 补件/升级，不得通过。"
        elif appeal:
            has_appeal_cite = any("8.1" in c or "复议" in c for c in cites)
            if not has_appeal_cite:
                rec, title, next_action, refused = "拒赔", "复议无条款 · 不改判", "deny", True
                letter = "复议缺少复议条款引用，不得默示改判通过。"
            else:
                rec, title, next_action, refused = "复议", "复议受理 · 待核赔", "appeal_review", True
                letter = "已引用复议条款。进入待核赔，不因新证据默示改判通过。须人审。"
        elif math["shop_refund_yuan"] >= claim.amount_yuan and math["shop_refund_yuan"] > 0:
            rec, title, next_action, refused = "拒赔", "店铺已退 · 双重受偿", "deny_or_offset", True
            letter = f"店铺已退 ¥{math['shop_refund_yuan']:.2f}。保险再赔即双重受偿，建议冲减至零或拒。"
        elif 0 < math["shop_refund_yuan"] < claim.amount_yuan:
            rec, title, next_action, refused = "差额", "店铺部分退 · 建议差额", "wait_human_confirm", False
            letter = (
                f"店铺已退 ¥{math['shop_refund_yuan']:.2f}，小于申请 ¥{claim.amount_yuan:.2f}。"
                f"建议差额赔付 ¥{math['suggested_yuan']:.2f}，须人确认。"
            )
        elif claim.amount_yuan > limit:
            rec, title, next_action, refused = "拒赔", "超保额", "deny", True
            letter = f"申请 ¥{claim.amount_yuan:.2f}，超过 {claim.product} 限额 ¥{limit:.0f}。"
        else:
            letter = (
                f"材料齐、条款覆盖、金额 ¥{claim.amount_yuan:.2f} 未超限。"
                f"免赔 ¥{math['deductible']:.2f}。核赔建议：通过。"
                "打款须人点执行，演示不打款。"
            )

        if letter:
            letter = _with_formula(letter, cites, math, refused=refused)
        status = case_status(rec, bool(docs.get("complete")))

        return {
            "role": self.name,
            "title": title,
            "recommendation": rec,
            "case_status": status,
            "settlement": math,
            "next_action": next_action,
            "refused": refused,
            "banner": banner,
            "decision_letter": letter,
            "executed": False,
            "requires_human": True,
            "idempotency_key": key,
            "payout": probe,
            "citations": cites,
            "tracking": track,
            "enabled": bool(cites) and rec in {"通过", "补件", "拒赔", "复议", "差额"},
        }


def _with_formula(letter: str, cites: list[str], math: dict, refused: bool = False) -> str:
    clauses = [c.split(" · ", 1)[0] for c in cites if "条款" in c]
    clause_txt = "、".join(dict.fromkeys(clauses)) if clauses else "（见引用芯片）"
    payout_line = "建议拒赔，不予赔付。" if refused else f"建议赔付：¥{math['suggested_yuan']:.2f}。"
    return (
        f"{letter}\n条款：{clause_txt}\n计算：{math['formula']}\n"
        f"{payout_line}"
    )


def _is_appeal(claim: Claim) -> bool:
    prior = any(a.get("type") in {"deny", "拒赔"} for a in claim.prior_actions)
    return prior and any(w in claim.narrative for w in ("复议", "不服", "再审"))


def _photo_signed_track_open(claim: Claim, track: dict) -> bool:
    if not track.get("ok"):
        return False
    payload = track.get("tracking") or {}
    status = str(payload.get("status") or "")
    if status in {"signed", "delivered", "签收"}:
        return False
    photo = any("签收" in str(a.get("kind") or a.get("name") or "") for a in claim.attachments)
    return photo and status in {"in_transit", "rejected", "揽收", "在途"}


def _exclusion(claim: Claim) -> str:
    text = claim.narrative
    if any(w in text for w in ("易碎", "陶瓷", "玻璃", "墨水瓶", "墨水碎")):
        return "易碎"
    if "延误" in text and "破损" not in text and "丢失" not in text and "拒收" not in text:
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
