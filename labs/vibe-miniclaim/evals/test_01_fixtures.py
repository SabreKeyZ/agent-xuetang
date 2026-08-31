from __future__ import annotations

import miniclaim
from helpers import CLAIMDESK_LEAK, LAB_ROOT, call, fixture_names, read_fixture


def test_five_fixture_files_exist():
    names = fixture_names()
    for need in ("mute-story", "need-photo", "over-cap", "bare-reject", "autumn-pot"):
        assert need in names, f"缺夹具 {need}.json"


def test_fixtures_are_not_claimdesk_clones():
    for name in fixture_names():
        raw = (LAB_ROOT / "fixtures" / f"{name}.json").read_text(encoding="utf-8")
        for leak in CLAIMDESK_LEAK:
            assert leak not in raw, f"{name} 看起来像从理赔台粘的（含 {leak}）"
        data = read_fixture(name)
        assert str(data["id"]).startswith("K-")
        assert data["insurer_id"] == "wujin"


def test_mute_story_has_unmatchable_narrative():
    t = read_fixture("mute-story")
    assert t["id"] == "K-4201"
    assert "RibbonNexusOmega" in t["narrative"]


def test_need_photo_lacks_signed_pod():
    t = read_fixture("need-photo")
    kinds = [a.get("kind") for a in t.get("attachments") or []]
    assert "物流签收图" not in kinds
    assert "运单" in kinds


def test_over_cap_is_over_180():
    t = read_fixture("over-cap")
    assert float(t["amount_yuan"]) > 180


def test_bare_reject_is_unsigned_without_proof():
    t = read_fixture("bare-reject")
    assert "拒收" in t["narrative"] and "未签收" in t["narrative"]
    kinds = [a.get("kind") for a in t.get("attachments") or []]
    assert "拒收证明" not in kinds


def test_autumn_pot_sits_after_cut():
    t = read_fixture("autumn-pot")
    assert t["incident_at"][:10] >= "2026-07-01"
    assert t["insured_at"][:10] < "2026-07-01"
    assert "釉瓶" in t["narrative"] or "春册" in t["narrative"]


def test_load_fixture_returns_same_json():
    load = getattr(miniclaim, "load_fixture", None)
    list_fn = getattr(miniclaim, "list_fixtures", None)
    assert load and list_fn, "还缺 load_fixture / list_fixtures。把 prompts/01 贴给助手。"
    listed = call(list_fn)
    assert set(listed) >= set(fixture_names())
    for name in fixture_names():
        got = call(load, name)
        assert got["id"] == read_fixture(name)["id"]
        assert got["fixture_id"] == name
