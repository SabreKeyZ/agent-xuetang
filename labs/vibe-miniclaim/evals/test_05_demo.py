from __future__ import annotations

import miniclaim
from helpers import call, citation_on_disk, read_fixture


def _process(name: str) -> dict:
    process = getattr(miniclaim, "process", None)
    assert process, "还缺 process。把 prompts/05 贴给助手。"
    return call(process, read_fixture(name))


def _demo_text(name: str | None = None) -> str:
    return str(call(miniclaim.demo, name) or "")


def test_process_never_executes():
    for name in ("mute-story", "need-photo", "over-cap", "bare-reject", "autumn-pot"):
        out = _process(name)
        assert out.get("executed") is False
        payment = out.get("payment") or {}
        if payment:
            assert payment.get("status") == "confirm_required"
            assert payment.get("executed") is False


def test_process_autumn_keeps_real_cites():
    out = _process("autumn-pot")
    cites = out.get("citations") or []
    assert any("autumn-cut-2026.md" in c for c in cites)
    assert all(citation_on_disk(c) for c in cites)


def test_demo_prints_chips_or_refuse_letter():
    text = _demo_text()
    assert "引用:" in text or "红条:" in text or "决定书:" in text
    assert "已打款" not in text
    assert "executed=True" not in text


def test_demo_autumn_mentions_policy_file():
    text = _demo_text("autumn-pot")
    assert "autumn-cut-2026.md" in text
    assert "引用:" in text


def test_demo_over_cap_red_banner():
    text = _demo_text("over-cap")
    assert "红条:" in text or "决定书:" in text
    assert "180" in text


def test_demo_mute_story_red_banner():
    text = _demo_text("mute-story")
    assert "红条:" in text or "决定书:" in text
    assert "没有引用" in text


def test_demo_need_photo_asks_docs():
    text = _demo_text("need-photo")
    assert "红条:" in text or "决定书:" in text
    assert "补件" in text


def test_demo_bare_reject_unsigned():
    text = _demo_text("bare-reject")
    assert "红条:" in text or "决定书:" in text
    assert "未签收" in text or "拒收" in text
