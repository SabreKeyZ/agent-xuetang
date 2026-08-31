from ticketdesk.agents.supervisor import Supervisor
from ticketdesk.loader import load_ticket
from ticketdesk.rag import citation_exists


def test_promo_cites_effective_campaign_file():
    out = Supervisor().process(load_ticket("promo-overrides-sla"))
    cites = out["citations"]
    assert cites, "活动期必须有引用"
    assert all(citation_exists(c) for c in cites)
    assert any("promo-2026-summer.md" in c for c in cites)


def test_happy_logistics_has_chips():
    out = Supervisor().process(load_ticket("happy-logistics"))
    assert out["citations"]
    assert all(citation_exists(c) for c in out["citations"])
    assert out["executed"] is False


def test_quality_small_refund_is_draft_not_pay():
    out = Supervisor().process(load_ticket("happy-quality"))
    assert out["citations"]
    assert out["gate"]["verdict"] == "draft_ok"
    assert out["gate"]["payment"]["status"] == "confirm_required"
    assert out["executed"] is False
