from __future__ import annotations

from ticketdesk.clock import l2_on_duty, plus_minutes, sla_remaining_minutes
from ticketdesk.models import Ticket


def sla_clock(ticket: Ticket, roster: dict | None = None) -> dict:
    remaining = sla_remaining_minutes(ticket.created_at, ticket.now, ticket.sla_minutes)
    breached = remaining < 0
    on_duty = l2_on_duty(ticket.now, roster)
    return {
        "priority": ticket.priority,
        "sla_minutes": ticket.sla_minutes,
        "remaining_minutes": remaining,
        "breached": breached,
        "deadline": plus_minutes(ticket.created_at, ticket.sla_minutes),
        "l2": on_duty,
        "l2_empty": on_duty is None,
        "queue": "human" if breached and on_duty is None else "agent",
    }
