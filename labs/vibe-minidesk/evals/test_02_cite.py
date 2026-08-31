from __future__ import annotations

import minidesk
from helpers import CITE_RE, TICKETDESK_LEAK, call, citation_on_disk, read_fixture


def _cites(name: str) -> list[str]:
    cite = getattr(minidesk, "cite_policy", None)
    assert cite, "还缺 cite_policy。把 prompts/02 贴给助手。"
    return list(call(cite, read_fixture(name)))


def test_cite_format_is_path_line():
    cites = _cites("small-wick")
    assert cites, "小额单也必须有引用，不准空嘴答"
    for c in cites:
        assert CITE_RE.match(c), f"引用必须是 docs/policy/文件.md:行号，收到 {c!r}"
        assert citation_on_disk(c), f"假引用或行号越界：{c}"


def test_lantern_stale_cites_lantern_week_file():
    cites = _cites("lantern-stale")
    assert cites, "灯节窗口单必须有引用"
    assert any("lantern-week-2026.md" in c for c in cites), (
        "灯节窗口必须点名 docs/policy/lantern-week-2026.md，"
        "不得只引日常「不赔运费」"
    )
    assert all(citation_on_disk(c) for c in cites)


def test_citations_stay_inside_this_lab():
    cites = _cites("over-limit")
    assert cites
    blob = " ".join(cites)
    for leak in TICKETDESK_LEAK:
        assert leak not in blob, f"不要去引工单台政策：{leak}"
    assert all(citation_on_disk(c) for c in cites)


def test_blank_order_still_may_cite_order_rule():
    cites = _cites("blank-order")
    # 缺单号也可以引「先核单号」那一条；不许编行号。
    assert all(citation_on_disk(c) for c in cites)
