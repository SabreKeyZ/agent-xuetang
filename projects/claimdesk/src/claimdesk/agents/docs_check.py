from __future__ import annotations

from claimdesk.models import REQUIRED, Claim


class DocsCheck:
    name = "docs_check"

    def run(self, claim: Claim) -> dict:
        required = list(REQUIRED.get(claim.product) or REQUIRED["freight"])
        names = []
        kinds = []
        for att in _all_attachments(claim):
            names.append(str(att.get("name") or ""))
            kinds.append(str(att.get("kind") or att.get("name") or ""))
        blob = " ".join(names + kinds)
        if claim.order_id:
            blob += " 运单号"
        reject = "拒收" in claim.narrative
        checklist = []
        missing = []
        for item in required:
            aliases = {
                "运单号": ("运单", "tracking", claim.order_id),
                "物流签收图": ("签收", "pod", "物流签收") + (("拒收证明", "拒收") if reject else ()),
                "发票或支付截图": ("发票", "支付截图", "receipt"),
                "出险说明": ("出险说明", "narrative"),
                "医疗票据或回执": ("医疗", "回执", "invoice"),
                "身份证明": ("身份", "id-card", "身份证"),
            }[item]
            ok = any(a and a in blob for a in aliases if a)
            if item == "出险说明" and claim.narrative.strip():
                ok = True
            checklist.append({"item": item, "ok": ok})
            if not ok:
                missing.append(item)
        return {
            "role": self.name,
            "title": "材料齐全" if not missing else "缺件 · 不审结",
            "required": required,
            "checklist": checklist,
            "missing": missing,
            "complete": not missing,
            "supplement_applied": _has_supplement(claim),
        }


def _has_supplement(claim: Claim) -> bool:
    return any(a.get("type") == "supplement" for a in claim.prior_actions)


def _all_attachments(claim: Claim) -> list[dict]:
    rows = list(claim.attachments or [])
    for action in claim.prior_actions:
        if action.get("type") != "supplement":
            continue
        for att in action.get("attachments") or []:
            if isinstance(att, str):
                rows.append({"name": att, "file_id": att, "kind": att})
            else:
                rows.append(att)
    return rows
