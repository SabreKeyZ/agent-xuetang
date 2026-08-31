from claimdesk.agents.supervisor import Supervisor
from claimdesk.loader import load_claim
from claimdesk.store import CaseStore


def test_over_limit():
    out = Supervisor().process(load_claim("over-limit"))
    assert out["decision"]["recommendation"] == "拒赔"
    assert "保额" in out["draft_reply"] or "限额" in out["draft_reply"]


def test_over_window():
    out = Supervisor().process(load_claim("over-window"))
    assert out["decision"]["recommendation"] == "拒赔"
    assert "窗口" in out["decision"]["title"] or "窗口" in out["draft_reply"]


def test_shop_refund_no_double():
    out = Supervisor().process(load_claim("shop-already-refunded"))
    assert out["decision"]["recommendation"] == "拒赔"
    assert out["decision"]["next_action"] == "deny_or_offset"


def test_shared_photo_escalates():
    out = Supervisor().process(load_claim("shared-photo-b"))
    assert out["decision"]["next_action"] == "human_queue"
    assert out["decision"]["recommendation"] == "拒赔"
    assert out["executed"] is False


def test_valid_low_recommend_pass_no_payout():
    out = Supervisor().process(load_claim("valid-low"))
    assert out["decision"]["recommendation"] == "通过"
    assert out["citations"]
    assert out["executed"] is False
    assert out["decision"]["payout"]["status"] == "confirm_required"


def test_wrong_claimant_identity_gate():
    out = Supervisor().process(load_claim("wrong-claimant"))
    assert out["decision"]["next_action"] == "human_queue"
    assert "身份" in out["decision"]["title"]


def test_idempotent_payout_key():
    store = CaseStore()
    sup = Supervisor(store=store)
    a = sup.process(load_claim("valid-low"))
    b = sup.process(load_claim("valid-low"))
    assert a["idempotency_key"] == b["idempotency_key"]
    assert b["replayed"] is True
    assert a["executed"] is False
