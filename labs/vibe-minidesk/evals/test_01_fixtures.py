from __future__ import annotations

import minidesk
from helpers import LAB_ROOT, TICKETDESK_LEAK, call, fixture_names, read_fixture


def test_five_fixture_files_exist():
    names = fixture_names()
    for need in ("blank-order", "lantern-stale", "over-limit", "pipe-body", "small-wick"):
        assert need in names, f"缺夹具 {need}.json"


def test_fixtures_are_not_ticketdesk_clones():
    for name in fixture_names():
        raw = (LAB_ROOT / "fixtures" / f"{name}.json").read_text(encoding="utf-8")
        for leak in TICKETDESK_LEAK:
            assert leak not in raw, f"{name} 看起来像从工单台粘的（含 {leak}）"
        data = read_fixture(name)
        assert str(data["id"]).startswith("M-")
        assert data["shop_id"] == "huideng"


def test_blank_order_has_empty_order_id():
    t = read_fixture("blank-order")
    assert t["order_id"] == ""
    assert t["id"] == "M-3101"


def test_lantern_stale_sits_in_promo_window():
    t = read_fixture("lantern-stale")
    assert t["order_id"].startswith("HD-")
    assert t["now"].startswith("2026-08-")
    assert "灯节" in t["body"]


def test_over_limit_is_over_200():
    t = read_fixture("over-limit")
    assert float(t["refund_yuan"]) > 200


def test_pipe_body_contains_shell():
    t = read_fixture("pipe-body")
    assert "curl" in t["body"] and "| sh" in t["body"]
    assert "os.system" in t["body"]


def test_load_fixture_returns_same_json():
    load = getattr(minidesk, "load_fixture", None)
    list_fn = getattr(minidesk, "list_fixtures", None)
    assert load and list_fn, "还缺 load_fixture / list_fixtures。把 prompts/01 贴给助手。"
    listed = call(list_fn)
    assert set(listed) >= set(fixture_names())
    for name in fixture_names():
        got = call(load, name)
        assert got["id"] == read_fixture(name)["id"]
        assert got["fixture_id"] == name
