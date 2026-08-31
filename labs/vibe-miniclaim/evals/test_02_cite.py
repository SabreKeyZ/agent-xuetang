from __future__ import annotations

import miniclaim
from helpers import CITE_RE, CLAIMDESK_LEAK, call, citation_on_disk, read_fixture


def _cites(name: str) -> list[str]:
    cite = getattr(miniclaim, "cite_policy", None)
    assert cite, "还缺 cite_policy。把 prompts/02 贴给助手。"
    return list(call(cite, read_fixture(name)))


def test_cite_format_is_path_line():
    cites = _cites("over-cap")
    assert cites, "破损单也必须有引用，不准空嘴答"
    for c in cites:
        assert CITE_RE.match(c), f"引用必须是 docs/policy/文件.md:行号，收到 {c!r}"
        assert citation_on_disk(c), f"假引用或行号越界：{c}"


def test_autumn_pot_cites_autumn_cut_file():
    cites = _cites("autumn-pot")
    assert cites, "秋切窗口釉瓶案必须有引用"
    assert any("autumn-cut-2026.md" in c for c in cites), (
        "出险日在秋切后必须点名 docs/policy/autumn-cut-2026.md，"
        "不得只引春册「可赔半额」"
    )
    assert all(citation_on_disk(c) for c in cites)


def test_citations_stay_inside_this_lab():
    cites = _cites("over-cap")
    assert cites
    blob = " ".join(cites)
    for leak in CLAIMDESK_LEAK:
        assert leak not in blob, f"不要去引理赔台政策：{leak}"
    assert all(citation_on_disk(c) for c in cites)


def test_mute_story_returns_no_invented_clause():
    cites = _cites("mute-story")
    assert cites == [], "对不上条款就返回空列表，不准编一条"
    assert all(citation_on_disk(c) for c in cites)
