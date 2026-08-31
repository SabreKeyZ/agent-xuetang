from ticketdesk.agents.supervisor import Supervisor
from ticketdesk.loader import load_ticket
from ticketdesk.safety import NEVER_EXECUTE, NEVER_PAY


def test_return_without_inbound_is_ask_only():
    out = Supervisor().process(load_ticket("return-no-inbound"))
    assert out["classify"]["kind"] == "退货退款"
    assert out["gate"]["verdict"] == "refuse_exec"
    assert out["gate"]["next_action"] == "ask_return"
    assert out["executed"] is False
    assert "不退款" in (out["banner"] + out["draft_reply"])


def test_exchange_never_pays_cash():
    out = Supervisor().process(load_ticket("exchange-no-cash"))
    assert out["classify"]["kind"] == "换货"
    assert out["gate"]["next_action"] == "exchange_only"
    assert "不退现金" in out["draft_reply"] or "不退现金" in out["gate"]["title"]
    assert out["executed"] is False
    assert out["gate"]["never_pay"] is True
    assert NEVER_PAY is True


def test_partial_refund_one_line_not_whole_order():
    out = Supervisor().process(load_ticket("partial-refund-one-line"))
    assert out["classify"]["kind"] == "部分退"
    assert out["gate"]["next_action"] == "partial_line"
    assert "砚台小样" in out["draft_reply"]
    assert "198" not in out["draft_reply"] or "不能按整单" in out["draft_reply"]
    assert "72" in out["draft_reply"]
    assert out["executed"] is False


def test_seven_day_no_reason_refuses_and_cites():
    out = Supervisor().process(load_ticket("seven-day-no-reason-late"))
    assert out["classify"]["kind"] == "七天无理由超时"
    assert out["gate"]["next_action"] == "deny_seven_day"
    assert out["citations"]
    assert any("after-sales" in c for c in out["citations"])
    assert "七日" in out["draft_reply"] or "七天" in out["draft_reply"]
    assert out["executed"] is False


def test_quality_after_seven_days_still_quality():
    out = Supervisor().process(load_ticket("quality-after-seven-days"))
    assert out["classify"]["kind"] != "七天无理由超时"
    assert out["gate"]["next_action"] != "deny_seven_day"
    assert out["executed"] is False
    assert out["gate"]["never_pay"] is True


def test_refund_cannot_exceed_paid_yuan():
    out = Supervisor().process(load_ticket("refund-over-paid"))
    assert out["ticket"]["refund_yuan"] == 128
    assert out["gate"]["next_action"] == "cap_paid"
    assert "98" in out["draft_reply"]
    assert out["executed"] is False


def test_promo_delay_is_coupon_not_cash():
    out = Supervisor().process(load_ticket("promo-coupon-not-cash"))
    assert out["classify"]["kind"] == "物流延误"
    assert any("promo-2026-summer.md" in c for c in out["citations"])
    assert out["compensation_kind"] == "coupon"
    assert "券" in out["draft_reply"]
    assert "现金" in out["draft_reply"]
    assert out["gate"]["payment"]["status"] == "confirm_required"
    assert out["executed"] is False


def test_unshipped_cancel_draft_no_auto_pay():
    out = Supervisor().process(load_ticket("unshipped-cancel"))
    assert out["classify"]["kind"] == "未发货取消"
    assert out["gate"]["verdict"] == "draft_ok"
    assert out["executed"] is False
    assert out["gate"]["payment"]["status"] == "confirm_required"


def test_classifier_uses_last_customer_turn():
    out = Supervisor().process(load_ticket("multi-turn-tracking"))
    last = out["classify"]["last_customer_text"]
    assert "QX-202608-2108" in last
    assert "漏液" in last
    assert out["classify"]["kind"] in {"退货退款", "质量"}
    assert "等下发" not in last


def test_dual_sla_night_escalates_resolution_only():
    out = Supervisor().process(load_ticket("dual-sla-night-first-only"))
    sla = out["sla"]
    assert sla["first_response_breached"] is True
    assert sla["resolution_breached"] is False
    assert sla["l2_empty"] is True
    assert out["gate"]["verdict"] != "escalate"
    assert out["executed"] is False


def test_abuse_internal_note_stays_off_customer_draft():
    out = Supervisor().process(load_ticket("abuse-legal"))
    assert "已转人工" in out["draft_reply"]
    assert "律师" not in out["draft_reply"]
    assert "对内" in out["internal_note"]
    assert "律师" in out["internal_note"] or "威胁" in out["internal_note"]
    assert NEVER_EXECUTE is True


def test_p0_resolution_night_still_escalates():
    out = Supervisor().process(load_ticket("p0-sla-night"))
    assert out["sla"]["resolution_breached"] is True
    assert out["gate"]["verdict"] == "escalate"


def test_negated_return_phrase_is_logistics_not_return_refund():
    from ticketdesk.aftersales import mentions_return_goods

    assert mentions_return_goods("轨迹好久没动。按盛夏大促运费补偿规则处理就行，不用退货。") is False
    assert mentions_return_goods("墨水漏液，要退货退款。") is True
    out = Supervisor().process(load_ticket("happy-logistics"))
    assert out["classify"]["kind"] == "物流延误"
    assert out["classify"]["after_sales_type"] != "退货退款"
    assert out["gate"]["next_action"] != "ask_return"
    assert out["gate"]["verdict"] == "draft_ok"
    assert any("promo-2026-summer.md" in c for c in out["citations"])
    assert out["executed"] is False
