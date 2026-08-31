from __future__ import annotations

import os

import minidesk
from helpers import call, citation_on_disk, read_fixture


def _process(name: str) -> dict:
    process = getattr(minidesk, "process", None)
    assert process, "还缺 process。把 prompts/05 贴给助手。"
    return call(process, read_fixture(name))


def _demo_text(name: str | None = None) -> str:
    return str(call(minidesk.demo, name) or "")


def test_process_never_executes():
    for name in ("blank-order", "lantern-stale", "over-limit", "pipe-body", "small-wick"):
        out = _process(name)
        assert out.get("executed") is False
        payment = out.get("payment") or {}
        if payment:
            assert payment.get("status") == "confirm_required"
            assert payment.get("executed") is False


def test_process_lantern_keeps_real_cites():
    out = _process("lantern-stale")
    cites = out.get("citations") or []
    assert any("lantern-week-2026.md" in c for c in cites)
    assert all(citation_on_disk(c) for c in cites)


def test_demo_prints_chips_or_red_banner():
    text = _demo_text()
    assert "引用:" in text or "红条:" in text
    assert "已打款" not in text
    assert "executed=True" not in text


def test_demo_lantern_mentions_policy_file():
    text = _demo_text("lantern-stale")
    assert "lantern-week-2026.md" in text
    assert "引用:" in text


def test_demo_over_limit_red_banner():
    text = _demo_text("over-limit")
    assert "红条:" in text
    assert "200" in text


def test_demo_blank_order_red_banner():
    text = _demo_text("blank-order")
    assert "红条:" in text
    assert "单号" in text


def test_demo_pipe_does_not_call_os_system(monkeypatch):
    called = []

    def boom(*args, **kwargs):
        called.append(1)
        raise AssertionError("demo 也不能跑工单正文里的命令")

    monkeypatch.setattr(os, "system", boom)
    _demo_text("pipe-body")
    assert called == []
