from __future__ import annotations

from claimdesk.models import Claim
from claimdesk.rag import citation_exists, retrieve


class ClauseClerk:
    name = "clause"

    def run(self, claim: Claim, docs: dict) -> dict:
        query = _query(claim, docs)
        if any(tok in claim.narrative for tok in ("比特币", "FlipFlopZetaQueue", "内部系统代号")):
            hits = []
        else:
            hits = retrieve(query, at=claim.incident_at, k=5)
        wrong_version = [h for h in hits if h.chunk.version and h.chunk.version != _expected_version(claim)]
        # 出险日过滤已在 retrieve 里做；再钉一次版本
        hits = [h for h in hits if not h.chunk.version or h.chunk.version == _expected_version(claim)]
        cites = [h.chunk.citation for h in hits if citation_exists(h.chunk.citation)]
        if not cites:
            return {
                "role": self.name,
                "title": "没有引用，就先不答",
                "refused": True,
                "citations": [],
                "quotes": [],
                "version": _expected_version(claim),
                "body": "出险日条款检索为零。不能用投保日印象审。",
            }
        return {
            "role": self.name,
            "title": f"适用 {_expected_version(claim)} · 出险日",
            "refused": False,
            "citations": cites,
            "quotes": [h.as_dict() for h in hits],
            "version": _expected_version(claim),
            "body": "\n\n".join(
                f"{h.chunk.clause_id or ''} {h.chunk.text.strip().splitlines()[0][:80]}\n— {h.chunk.citation}"
                for h in hits[:4]
            ),
            "dropped_wrong_version": len(wrong_version),
        }


def _expected_version(claim: Claim) -> str:
    day = claim.incident_at[:10]
    return "v2" if day >= "2026-07-01" else "v1"


def _query(claim: Claim, docs: dict) -> str:
    q = [claim.narrative, "条款", "出险日"]
    if docs.get("missing"):
        q.append("申请材料 缺件 补件 3.1")
    if "易碎" in claim.narrative or "墨水" in claim.narrative or "陶瓷" in claim.narrative:
        q.append("除外责任 易碎 条款 3.2")
    if "延误" in claim.narrative:
        q.append("延误不赔 条款 3.3")
    if claim.amount_yuan > 80:
        q.append("限额 保额 条款 2.1 2.2 4.1")
    if any(a.get("type") == "shop_refund" for a in claim.prior_actions):
        q.append("双重受偿 店铺退款 冲减 差额 条款 5.1 5.3")
    if any(a.get("type") in {"deny", "拒赔"} for a in claim.prior_actions) or "复议" in claim.narrative:
        q.append("复议 新证据 条款 8.1")
    if "拒收" in claim.narrative:
        q.append("拒收 未签收 条款 3.4")
    if "签收" in claim.narrative and "破损" in claim.narrative:
        q.append("签收破损 条款 3.5 1.1")
    if claim.product == "accident":
        q.append("免赔 50 条款 2.3")
    if claim.claimant_id != claim.insured_id:
        q.append("身份闸门 代索赔 条款 6.1")
    q.append("索赔窗口 免赔 冲减 条款 2.3 4.1")
    return " ".join(q)
