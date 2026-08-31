from claimdesk.agents.supervisor import Supervisor
from claimdesk.loader import load_claim
from claimdesk.models import DEDUCTIBLE
from claimdesk.settle import settle
from claimdesk.tools.payment import payout


def test_accident_deductible_formula_no_payout():
    out = Supervisor().process(load_claim("accident-deductible"))
    math = out["settlement"]
    assert DEDUCTIBLE["accident"] == 50
    assert math["deductible"] == 50
    assert math["suggested_yuan"] == 30
    assert "50" in math["formula"]
    assert out["decision"]["recommendation"] == "通过"
    assert out["case_status"] == "待人打款"
    assert "条款" in out["draft_reply"]
    assert "计算" in out["draft_reply"]
    assert out["executed"] is False
    assert out["decision"]["payout"]["status"] == "confirm_required"


def test_shop_partial_offset_is_delta_not_full_deny():
    out = Supervisor().process(load_claim("shop-partial-offset"))
    assert out["decision"]["recommendation"] == "差额"
    assert out["settlement"]["suggested_yuan"] == 12
    assert "8" in out["draft_reply"]
    assert out["executed"] is False
    assert out["case_status"] == "待人打款"


def test_shop_full_refund_still_denies():
    out = Supervisor().process(load_claim("shop-already-refunded"))
    assert out["decision"]["recommendation"] == "拒赔"
    assert out["decision"]["next_action"] == "deny_or_offset"
    assert out["settlement"]["suggested_yuan"] == 0


def test_reject_unsigned_vs_signed_damaged():
    rej = Supervisor().process(load_claim("reject-unsigned"))
    sig = Supervisor().process(load_claim("signed-damaged"))
    delay = Supervisor().process(load_claim("delay-only"))
    assert any("3.4" in c or "拒收" in c for c in rej["citations"])
    assert rej["decision"]["recommendation"] == "通过"
    assert sig["decision"]["recommendation"] == "通过"
    assert delay["decision"]["recommendation"] == "拒赔"
    assert "延误" in (delay["decision"]["title"] + delay["draft_reply"])
    assert rej["executed"] is False and sig["executed"] is False


def test_supplement_returned_enters_adjudication():
    missing = Supervisor().process(load_claim("missing-docs"))
    back = Supervisor().process(load_claim("supplement-returned"))
    assert missing["decision"]["recommendation"] == "补件"
    assert missing["case_status"] == "补件中"
    assert back["docs"]["complete"] is True
    assert back["docs"]["supplement_applied"] is True
    assert back["decision"]["recommendation"] in {"通过", "差额"}
    assert back["case_status"] == "待人打款"
    assert back["executed"] is False


def test_appeal_cites_clause_and_does_not_silent_pass():
    out = Supervisor().process(load_claim("appeal-after-deny"))
    assert any("8.1" in c or "复议" in c for c in out["citations"])
    assert out["decision"]["recommendation"] == "复议"
    assert out["decision"]["recommendation"] != "通过"
    assert out["case_status"] == "待核赔"
    assert "复议" in out["draft_reply"]
    assert out["executed"] is False


def test_photo_signed_but_track_open_is_not_pass():
    out = Supervisor().process(load_claim("photo-signed-track-unsigned"))
    assert out["decision"]["recommendation"] in {"补件", "拒赔"}
    assert out["decision"]["recommendation"] != "通过"
    assert out["decision"]["tracking"]["ok"] is True
    assert out["decision"]["tracking"]["tracking"]["status"] == "in_transit"
    assert out["executed"] is False


def test_decision_letter_has_clause_and_formula():
    out = Supervisor().process(load_claim("valid-low"))
    assert "条款" in out["draft_reply"]
    assert "计算" in out["draft_reply"]
    assert "建议赔付" in out["draft_reply"]
    math = settle(load_claim("valid-low"))
    assert math["suggested_yuan"] == 12
    assert math["deductible"] == 0


def test_status_machine_values():
    filed_like = Supervisor().process(load_claim("missing-docs"))
    pay = Supervisor().process(load_claim("valid-low"))
    closed = Supervisor().process(load_claim("delay-only"))
    assert filed_like["case_status"] == "补件中"
    assert pay["case_status"] == "待人打款"
    assert closed["case_status"] == "结案"


def test_payout_never_fires():
    probe = payout(30, "qingtu:payout:C-x:3000", confirm=True)
    assert probe["executed"] is False
    assert probe["status"] == "confirm_required"
