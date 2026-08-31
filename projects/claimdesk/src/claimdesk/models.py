from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

REQUIRED = {
    "freight": ["运单号", "物流签收图", "发票或支付截图"],
    "accident": ["出险说明", "医疗票据或回执", "身份证明"],
}

LIMITS = {"freight": 80.0, "accident": 500.0}
DEDUCTIBLE = {"freight": 0.0, "accident": 50.0}
STATUSES = ("已报案", "立案", "补件中", "待核赔", "待人打款", "结案")


@dataclass
class Claim:
    id: str
    product: str
    channel: str
    insured_id: str
    insured_name: str
    claimant_id: str
    claimant_name: str
    policy_no: str
    order_id: str
    insured_at: str
    incident_at: str
    filed_at: str
    now: str
    amount_yuan: float
    attachments: list[dict[str, Any]]
    prior_actions: list[dict[str, Any]]
    narrative: str
    fixture_id: str = ""
    tracking: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], fixture_id: str = "") -> "Claim":
        atts = data.get("attachments") or []
        norm = []
        for item in atts:
            if isinstance(item, str):
                norm.append({"name": item, "file_id": item, "kind": item})
            else:
                norm.append(item)
        return cls(
            id=str(data.get("id") or ""),
            product=str(data.get("product") or "freight"),
            channel=str(data.get("channel") or "App"),
            insured_id=str(data.get("insured_id") or ""),
            insured_name=str(data.get("insured_name") or ""),
            claimant_id=str(data.get("claimant_id") or data.get("insured_id") or ""),
            claimant_name=str(data.get("claimant_name") or data.get("insured_name") or ""),
            policy_no=str(data.get("policy_no") or ""),
            order_id=str(data.get("order_id") or ""),
            insured_at=str(data.get("insured_at") or ""),
            incident_at=str(data.get("incident_at") or ""),
            filed_at=str(data.get("filed_at") or ""),
            now=str(data.get("now") or data.get("filed_at") or ""),
            amount_yuan=float(data.get("amount_yuan") or 0),
            attachments=norm,
            prior_actions=list(data.get("prior_actions") or []),
            narrative=str(data.get("narrative") or data.get("body") or ""),
            fixture_id=fixture_id or str(data.get("fixture_id") or ""),
            tracking=str(data.get("tracking") or ""),
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
