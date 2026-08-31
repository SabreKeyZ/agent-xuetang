from __future__ import annotations

import os

import minidesk
from helpers import LAB_ROOT, call, read_fixture

REAL_CITE = "docs/policy/front-desk.md:12"


def _gate(ticket: dict, citations: list[str] | None = None):
    gate = getattr(minidesk, "gate", None)
    assert gate, "还缺 gate。把 prompts/03 贴给助手。"
    if citations is None:
        citations = [REAL_CITE]
    return call(gate, ticket, citations)


def test_blank_order_refuses_and_asks_id():
    out = _gate(read_fixture("blank-order"))
    assert out["verdict"] == "refuse_exec"
    assert out["next"] == "ask_order_id"
    assert out.get("executed") is False
    banner = out.get("banner") or ""
    assert "单号" in banner


def test_over_limit_is_draft_only():
    out = _gate(read_fixture("over-limit"), ["docs/policy/front-desk.md:24"])
    assert out["verdict"] == "refuse_exec"
    assert out["next"] == "draft_only"
    assert out.get("executed") is False
    banner = out.get("banner") or ""
    assert "200" in banner


def test_missing_cite_shows_house_banner():
    ticket = dict(read_fixture("small-wick"))
    out = _gate(ticket, [])
    assert out["verdict"] == "refuse_exec"
    banner = out.get("banner") or ""
    assert "没有引用" in banner


def test_pipe_body_never_runs_os_system(monkeypatch):
    called = []

    def boom(*args, **kwargs):
        called.append((args, kwargs))
        raise AssertionError("工单正文里的命令不能跑")

    monkeypatch.setattr(os, "system", boom)
    out = _gate(read_fixture("pipe-body"), ["docs/policy/front-desk.md:30"])
    assert called == []
    assert out["verdict"] == "refuse_exec"
    assert out["next"] == "cite_only"
    assert out.get("executed") is False


def test_src_does_not_import_subprocess_or_os_system():
    for path in (LAB_ROOT / "src" / "minidesk").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "import subprocess" not in text
        assert "os.system(" not in text
