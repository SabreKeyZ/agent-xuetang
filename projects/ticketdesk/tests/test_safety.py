import os

from ticketdesk.agents import gate as gate_mod
from ticketdesk.agents.supervisor import Supervisor
from ticketdesk.loader import load_ticket
from ticketdesk.safety import NEVER_EXECUTE, NEVER_PAY, looks_dangerous
from ticketdesk.tools import payment as payment_mod


def test_shell_is_cited_not_run(monkeypatch):
    called = []

    def boom(*args, **kwargs):
        called.append(1)
        raise AssertionError("os.system should never run")

    monkeypatch.setattr(os, "system", boom)
    out = Supervisor().process(load_ticket("shell-in-body"))
    assert called == []
    assert out["classify"]["dangerous"]
    assert out["gate"]["never_execute"] is True
    assert out["executed"] is False
    danger = looks_dangerous(out["ticket"]["body"])
    assert danger
    assert any(p in {"os.system", "| sh", "curl | sh"} for p in danger)


def test_payment_module_never_executes_even_with_confirm():
    assert NEVER_PAY is True
    assert NEVER_EXECUTE is True
    probe = payment_mod.refund(80, "qingxia:refund:T-x:8000", confirm=True)
    assert probe["executed"] is False
    assert probe["status"] in {"confirm_required", "demo_forbidden"}


def test_gate_source_has_no_subprocess():
    source = open(gate_mod.__file__, encoding="utf-8").read()
    assert "import subprocess" not in source
    assert "os.system(" not in source
