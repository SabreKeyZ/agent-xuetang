import os

from issueforge.agents import repro as repro_mod
from issueforge.agents.repro import write_repro
from issueforge.loader import load_fixture
from issueforge.report import process


def test_repro_module_has_no_process_helpers():
    source = open(repro_mod.__file__, encoding="utf-8").read()
    assert "subprocess" not in source
    assert "os.system" not in source
    assert "eval(" not in source


def test_os_system_not_called_on_malicious_fixture(monkeypatch):
    called: list = []

    def boom(*args, **kwargs):
        called.append((args, kwargs))
        raise AssertionError("os.system should never run")

    monkeypatch.setattr(os, "system", boom)
    issue = load_fixture("bug-crash")
    out = write_repro(issue)
    assert called == []
    assert out["executed_code"] is False
    assert out["never_execute"] is True
    assert any("os.system" in p for p in out["dangerous_patterns"])


def test_curl_pipe_is_listed_not_run():
    issue = load_fixture("bug-empty-docs")
    out = write_repro(issue)
    assert out["dangerous_patterns"]
    assert all(not line.startswith("curl ") for line in out["checklist"])


def test_process_keeps_guard():
    issue = load_fixture("bug-crash")
    bundle = process(issue, [issue])
    assert bundle["repro"]["executed_code"] is False
    assert "不要运行" in "\n".join(bundle["repro"]["checklist"]) or bundle["repro"]["dangerous_patterns"]
