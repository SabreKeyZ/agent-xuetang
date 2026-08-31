from __future__ import annotations

import json
import sys
from typing import Any

from claimdesk.agents.adjudicator import Adjudicator
from claimdesk.agents.clause import ClauseClerk
from claimdesk.agents.docs_check import DocsCheck
from claimdesk.config import has_llm_key
from claimdesk.loader import load_all_claims, load_claim
from claimdesk.models import Claim
from claimdesk.store import CaseStore


class Supervisor:
    def __init__(self, store: CaseStore | None = None) -> None:
        self.docs = DocsCheck()
        self.clause = ClauseClerk()
        self.adjudicator = Adjudicator()
        self.store = store or CaseStore()
        self._claims: list[Claim] | None = None

    def catalog(self) -> list[Claim]:
        if self._claims is None:
            self._claims = load_all_claims()
        return self._claims

    def process(self, claim: Claim) -> dict[str, Any]:
        docs = self.docs.run(claim)
        clause = self.clause.run(claim, docs)
        decision = self.adjudicator.run(claim, docs, clause, self.catalog())
        audit = [
            {"role": "docs_check", "action": "checklist", "detail": docs["title"]},
            {"role": "clause", "action": "cite" if not clause.get("refused") else "refuse", "detail": clause["title"], "citations": clause.get("citations") or []},
            {"role": "adjudicator", "action": decision["recommendation"], "detail": decision["title"]},
        ]
        result = {
            "case_id": claim.id,
            "claim": claim.as_dict(),
            "docs": docs,
            "clause": clause,
            "decision": decision,
            "labels": [claim.product, decision["recommendation"]],
            "next_action": decision["next_action"],
            "draft_reply": decision["decision_letter"],
            "citations": clause.get("citations") or [],
            "executed": False,
            "requires_human": True,
            "idempotency_key": decision["idempotency_key"],
            "refused": decision.get("refused") or clause.get("refused"),
            "banner": decision.get("banner") or "",
            "policy_version": clause.get("version"),
            "audit": audit,
            "mode": "extractive" if not has_llm_key() else "llm-or-extractive",
        }
        stored = self.store.remember(claim.id, result)
        sys.stderr.write(json.dumps({"role": "supervisor", "case_id": claim.id, "rec": decision["recommendation"], "citations": result["citations"], "executed": False}, ensure_ascii=False) + "\n")
        return stored

    def process_fixture(self, name: str) -> dict[str, Any]:
        return self.process(load_claim(name))

    def demo(self) -> dict[str, Any]:
        names = [
            "missing-docs",
            "wrong-policy-version",
            "exclusion-fragile",
            "over-limit",
            "over-window",
            "shop-already-refunded",
            "shared-photo-b",
            "valid-low",
            "wrong-claimant",
            "no-clause",
        ]
        catalog = {c.fixture_id: c for c in self.catalog()}
        cases = [self.process(catalog[n]) for n in names if n in catalog]
        return {"cases": cases}
