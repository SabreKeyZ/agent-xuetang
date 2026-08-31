from __future__ import annotations

from ticketdesk.rag import Hit, retrieve


def search_policy(query: str, at: str | None = None, prefer_promo: bool = False, k: int = 4) -> list[Hit]:
    return retrieve(query, k=k, at=at, prefer_promo=prefer_promo)
