from ticketdesk.agents.supervisor import Supervisor
from ticketdesk.loader import load_ticket


def test_missing_order_id_is_incomplete():
    out = Supervisor().process(load_ticket("missing-order-id"))
    assert out["classify"]["kind"] == "信息不全"
    assert out["gate"]["verdict"] == "refuse_exec"
    assert out["executed"] is False


def test_wrong_shop_is_incomplete():
    out = Supervisor().process(load_ticket("wrong-shop-order"))
    assert out["classify"]["order"]["reason"] == "wrong_shop"
    assert out["classify"]["kind"] == "信息不全"


def test_burst_third_ticket_is_duplicate():
    out = Supervisor().process(load_ticket("burst-c"))
    assert out["classify"]["duplicates"]["is_burst"] is True
    assert out["gate"]["verdict"] == "hold_merge"
    assert out["executed"] is False
