from __future__ import annotations

from ticketdesk.clock import is_night_or_weekend, l2_on_duty, plus_minutes, sla_remaining_minutes
from ticketdesk.models import Ticket


def sla_clock(ticket: Ticket, roster: dict | None = None) -> dict:
    first_minutes = ticket.first_response_sla_minutes or ticket.sla_minutes
    res_minutes = ticket.resolution_sla_minutes or ticket.sla_minutes
    first_remaining = sla_remaining_minutes(ticket.created_at, ticket.now, first_minutes)
    res_remaining = sla_remaining_minutes(ticket.created_at, ticket.now, res_minutes)
    first_breached = first_remaining < 0
    res_breached = res_remaining < 0
    on_duty = l2_on_duty(ticket.now, roster)
    return {
        "priority": ticket.priority,
        "sla_minutes": ticket.sla_minutes,
        "first_response_sla_minutes": first_minutes,
        "resolution_sla_minutes": res_minutes,
        "remaining_minutes": first_remaining,
        "first_response_remaining": first_remaining,
        "resolution_remaining": res_remaining,
        "first_response_breached": first_breached,
        "resolution_breached": res_breached,
        "breached": first_breached,
        "deadline": plus_minutes(ticket.created_at, first_minutes),
        "resolution_deadline": plus_minutes(ticket.created_at, res_minutes),
        "l2": on_duty,
        "l2_empty": on_duty is None,
        "is_night": is_night_or_weekend(ticket.now),
        "queue": "human" if res_breached and on_duty is None else "agent",
    }
