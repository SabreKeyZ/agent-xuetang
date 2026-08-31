from __future__ import annotations

import json
import sys
from typing import Any

from ticketdesk.agents.classifier import Classifier
from ticketdesk.agents.gate import Gate
from ticketdesk.agents.policy import PolicyClerk
from ticketdesk.config import has_llm_key
from ticketdesk.loader import load_all_tickets, load_orders, load_roster, load_ticket
from ticketdesk.models import Ticket
from ticketdesk.store import CaseStore


class Supervisor:
    """主管只做分流与写账，不互叫成网。"""

    def __init__(self, store: CaseStore | None = None) -> None:
        self.classifier = Classifier()
        self.policy = PolicyClerk()
        self.gate = Gate()
        self.store = store or CaseStore()
        self._tickets: list[Ticket] | None = None
        self._orders = None
        self._roster = None

    def catalog(self) -> list[Ticket]:
        if self._tickets is None:
            self._tickets = load_all_tickets()
        return self._tickets

    def orders(self):
        if self._orders is None:
            self._orders = load_orders()
        return self._orders

    def roster(self) -> dict:
        if self._roster is None:
            self._roster = load_roster()
        return self._roster

    def process(self, ticket: Ticket) -> dict[str, Any]:
        classify = self.classifier.run(ticket, self.catalog(), self.orders())
        policy = self.policy.run(ticket, classify)
        gate = self.gate.run(ticket, classify, policy, self.roster())
        audit = [
            {"role": "classifier", "action": "label", "detail": classify["title"], "citations": classify.get("citations") or []},
            {"role": "policy", "action": "cite" if not policy.get("refused") else "refuse", "detail": policy["title"], "citations": policy.get("citations") or []},
            {"role": "gate", "action": gate["verdict"], "detail": gate["title"], "citations": gate.get("citations") or []},
        ]
        result = {
            "case_id": ticket.id,
            "ticket": ticket.as_dict(),
            "labels": classify["labels"],
            "classify": classify,
            "policy": policy,
            "gate": gate,
            "sla": gate["sla"],
            "next_action": gate["next_action"],
            "draft_reply": gate["draft_reply"],
            "citations": policy.get("citations") or [],
            "executed": False,
            "requires_human": True,
            "idempotency_key": gate["idempotency_key"],
            "refused": gate.get("refused") or policy.get("refused"),
            "banner": gate.get("banner") or ("没有引用，就先不答" if policy.get("refused") else ""),
            "audit": audit,
            "mode": "llm" if has_llm_key() else "extractive",
        }
        stored = self.store.remember(ticket.id, result)
        self._log(stored)
        return stored

    def process_fixture(self, name: str) -> dict[str, Any]:
        return self.process(load_ticket(name))

    def process_all(self) -> list[dict[str, Any]]:
        return [self.process(t) for t in self.catalog()]

    def demo(self) -> dict[str, Any]:
        highlight = [
            "missing-order-id",
            "promo-overrides-sla",
            "already-refunded",
            "refund-over-200",
            "p0-sla-night",
            "abuse-legal",
            "shell-in-body",
            "happy-logistics",
        ]
        catalog = {t.fixture_id: t for t in self.catalog()}
        script = []
        for name in highlight:
            ticket = catalog.get(name)
            if ticket is None:
                continue
            script.append(self.process(ticket))
        return {"mode": "extractive" if not has_llm_key() else "llm-or-extractive", "cases": script}

    @staticmethod
    def _log(payload: dict[str, Any]) -> None:
        row = {
            "role": "supervisor",
            "case_id": payload.get("case_id"),
            "next_action": payload.get("next_action"),
            "citations": payload.get("citations"),
            "idempotency_key": payload.get("idempotency_key"),
            "executed": payload.get("executed"),
            "replayed": payload.get("replayed"),
        }
        sys.stderr.write(json.dumps(row, ensure_ascii=False) + "\n")
