from __future__ import annotations

from ticketdesk.clock import within_minutes
from ticketdesk.models import Ticket
from ticketdesk.rag import tokenize


def find_duplicates(ticket: Ticket, catalog: list[Ticket], window_minutes: int = 10) -> dict:
    siblings = []
    for other in catalog:
        if other.id == ticket.id:
            continue
        if other.customer_id != ticket.customer_id:
            continue
        if not within_minutes(other.created_at, ticket.created_at, window_minutes):
            continue
        siblings.append(
            {
                "id": other.id,
                "fixture_id": other.fixture_id,
                "title": other.title,
                "citation": f"fixtures/tickets/{other.fixture_id}.json:1",
                "created_at": other.created_at,
            }
        )
    similar = _similar_tickets(ticket, catalog)
    return {
        "burst": siblings,
        "burst_count": len(siblings) + 1,
        "is_burst": len(siblings) + 1 >= 3,
        "similar": similar,
    }


def _similar_tickets(ticket: Ticket, catalog: list[Ticket], k: int = 2) -> list[dict]:
    q = set(tokenize(ticket.title + " " + ticket.body))
    ranked: list[tuple[int, Ticket]] = []
    for other in catalog:
        if other.id == ticket.id:
            continue
        tokens = set(tokenize(other.title + " " + other.body))
        overlap = len(q & tokens)
        if overlap >= 3:
            ranked.append((overlap, other))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].id))
    out = []
    for score, other in ranked[:k]:
        out.append(
            {
                "id": other.id,
                "fixture_id": other.fixture_id,
                "score": score,
                "citation": f"fixtures/tickets/{other.fixture_id}.json:1",
            }
        )
    return out
