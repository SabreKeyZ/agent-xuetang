from __future__ import annotations

import miniclaim
from helpers import call, read_fixture

REAL_CITE = "docs/policy/counter.md:12"


def _gate(claim: dict, citations: list[str] | None = None):
    gate = getattr(miniclaim, "gate", None)
    assert gate, "还缺 gate。把 prompts/03 贴给助手。"
    if citations is None:
        citations = [REAL_CITE]
    return call(gate, claim, citations)


def test_missing_cite_shows_house_banner():
    claim = dict(read_fixture("over-cap"))
    out = _gate(claim, [])
    assert out["verdict"] == "refuse_exec"
    assert out.get("executed") is False
    banner = out.get("banner") or ""
    assert "没有引用" in banner


def test_need_photo_asks_supplement():
    out = _gate(read_fixture("need-photo"), ["docs/policy/counter.md:16"])
    assert out["verdict"] == "refuse_exec"
    assert out["next"] == "ask_docs"
    assert out.get("executed") is False
    banner = out.get("banner") or ""
    assert "补件" in banner


def test_over_cap_is_draft_only():
    out = _gate(read_fixture("over-cap"), ["docs/policy/counter.md:24"])
    assert out["verdict"] == "refuse_exec"
    assert out["next"] == "draft_only"
    assert out.get("executed") is False
    banner = out.get("banner") or ""
    assert "180" in banner


def test_bare_reject_refuses_unsigned():
    out = _gate(read_fixture("bare-reject"), ["docs/policy/counter.md:20"])
    assert out["verdict"] == "refuse_exec"
    assert out["next"] == "ask_docs"
    assert out.get("executed") is False
    banner = out.get("banner") or ""
    assert "未签收" in banner or "拒收" in banner


def test_autumn_pot_with_cites_can_draft():
    out = _gate(read_fixture("autumn-pot"), ["docs/policy/autumn-cut-2026.md:12"])
    assert out["verdict"] == "draft_ok"
    assert out["next"] == "wait_human_confirm"
    assert out.get("executed") is False
