from ticketdesk.agents.supervisor import Supervisor
from ticketdesk.loader import load_ticket
from ticketdesk.store import CaseStore


def test_refund_over_200_refuses_execution():
    out = Supervisor().process(load_ticket("refund-over-200"))
    assert out["ticket"]["refund_yuan"] > 200
    assert out["gate"]["verdict"] == "refuse_exec"
    assert out["executed"] is False
    assert out["requires_human"] is True


def test_already_refunded_no_double_pay():
    out = Supervisor().process(load_ticket("already-refunded"))
    assert out["gate"]["verdict"] == "refuse_exec"
    assert out["gate"]["next_action"] == "no_double_pay"
    assert "重复" in (out["banner"] + out["draft_reply"])


def test_p0_night_escalates_to_queue_not_invented_handler():
    out = Supervisor().process(load_ticket("p0-sla-night"))
    assert out["sla"]["breached"] is True
    assert out["sla"]["l2_empty"] is True
    assert out["gate"]["verdict"] == "escalate"
    assert out["gate"]["next_action"] == "human_queue"
    assert "虚构" not in out["draft_reply"] or "不" in out["draft_reply"]


def test_abuse_escalates_without_promise():
    out = Supervisor().process(load_ticket("abuse-legal"))
    assert out["gate"]["verdict"] == "escalate"
    draft = out["draft_reply"]
    assert "已转人工" in draft
    assert "今晚必须" not in draft
    assert "赔偿" not in draft


def test_fraud_burst_holds_risk():
    out = Supervisor().process(load_ticket("fraud-burst-refunds"))
    assert out["gate"]["verdict"] == "hold_risk"
    assert out["executed"] is False


def test_idempotent_replay_does_not_double():
    store = CaseStore()
    sup = Supervisor(store=store)
    first = sup.process(load_ticket("happy-quality"))
    second = sup.process(load_ticket("happy-quality"))
    assert first["idempotency_key"] == second["idempotency_key"]
    assert second["replayed"] is True
    assert second["executed"] is False
    assert first["executed"] is False
