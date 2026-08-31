from __future__ import annotations

from ticketdesk.clock import within_minutes
from ticketdesk.models import Ticket


def by_customer(
    customer_id: str,
    catalog: list[Ticket],
    now: str,
    window_minutes: int = 120,
) -> list[dict]:
    rows = []
    for ticket in catalog:
        if ticket.customer_id != customer_id:
            continue
        if window_minutes and not within_minutes(ticket.created_at, now, window_minutes):
            continue
        rows.append(
            {
                "id": ticket.id,
                "fixture_id": ticket.fixture_id,
                "title": ticket.title,
                "created_at": ticket.created_at,
                "refund_yuan": ticket.refund_yuan,
                "prior_actions": ticket.prior_actions,
            }
        )
    return rows
