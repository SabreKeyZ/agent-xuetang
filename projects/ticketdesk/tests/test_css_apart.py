"""两套 CSS 必须是两套设计系统，禁止换皮。"""

from __future__ import annotations

import re
from pathlib import Path

_PROJ = Path(__file__).resolve().parents[2]
TD_CSS = _PROJ / "ticketdesk/src/ticketdesk/static/ticketdesk.css"
CD_CSS = _PROJ / "claimdesk/src/claimdesk/static/claimdesk.css"
TD_HTML = _PROJ / "ticketdesk/src/ticketdesk/static/index.html"
CD_HTML = _PROJ / "claimdesk/src/claimdesk/static/index.html"

_PROP = re.compile(r"--[a-z0-9-]+")
_CLASS = re.compile(r"\.([a-z][a-z0-9-]*)")
_HTML_CLASS = re.compile(r"""class=["']([^"']+)["']""")
_FORBIDDEN_STEMS = {
    "rail",
    "audit",
    "composer",
    "chip",
    "pill",
    "hero",
    "card",
    "queue",
    "shell",
    "btn",
}


def _classes(css: str) -> set[str]:
    return set(_CLASS.findall(css))


def _props(css: str) -> set[str]:
    return set(_PROP.findall(css))


def _html_classes(html: str) -> set[str]:
    out: set[str] = set()
    for block in _HTML_CLASS.findall(html):
        out.update(block.split())
    return out


def test_stylesheets_exist_and_are_named_per_product():
    assert TD_CSS.is_file()
    assert CD_CSS.is_file()
    assert not (TD_CSS.parent / "desk.css").exists()
    assert not (CD_CSS.parent / "desk.css").exists()
    assert not (TD_CSS.parent / "inbox.css").exists()


def test_custom_properties_and_class_names_are_disjoint():
    td, cd = TD_CSS.read_text(encoding="utf-8"), CD_CSS.read_text(encoding="utf-8")
    tp, cp = _props(td), _props(cd)
    assert tp, "ticketdesk.css 缺少自定义属性"
    assert cp, "claimdesk.css 缺少自定义属性"
    assert tp.isdisjoint(cp), f"共用 token: {sorted(tp & cp)}"
    tc, cc = _classes(td), _classes(cd)
    assert tc.isdisjoint(cc), f"共用 class: {sorted(tc & cc)}"
    assert all(name.startswith("td-") for name in tc)
    assert all(name.startswith("cd-") for name in cc)
    assert all(name.startswith("--td-") for name in tp)
    assert all(name.startswith("--cd-") for name in cp)


def test_ticketdesk_is_light_intercom_not_black():
    td = TD_CSS.read_text(encoding="utf-8")
    low = td.lower()
    assert "#f4f6f8" in low
    assert "#1f8ded" in low
    assert "#eef0f2" in low
    assert "#e8eaed" in low
    assert "#1f8a70" not in low
    assert "#d8efe6" not in low
    assert "#0f5c4a" not in low
    assert "#635bff" not in low
    assert "tabular-nums" not in td
    assert re.search(r"border-radius:\s*(16|18|20)px", td)
    assert not re.search(r"background[^;{]*#0[0-9a-fA-F]{5}", td)
    assert "table" not in td.lower() or "禁止表格" in td
    html = TD_HTML.read_text(encoding="utf-8")
    assert "/static/ticketdesk.css" in html
    assert "td-balloon" in html and "td-dock" in html
    assert "cd-" not in html
    assert "<table" not in html.lower()


def test_claimdesk_is_stripe_finance_not_inbox():
    cd = CD_CSS.read_text(encoding="utf-8")
    assert "#f6f9fc" in cd.lower()
    assert "#635bff" in cd.lower()
    assert "#0a2540" in cd.lower()
    assert "#1f8a70" not in cd.lower()
    assert "tabular-nums" in cd
    assert re.search(r"border-radius:\s*[46]px", cd)
    assert "cd-yen" in cd and "cd-grid" in cd
    assert "td-balloon" not in cd
    html = CD_HTML.read_text(encoding="utf-8")
    assert "/static/claimdesk.css" in html
    assert "<table" in html.lower()
    assert "cd-yen" in html and "cd-thumbs" in html
    assert "td-" not in html
    assert "td-balloon" not in html and "avatar" not in html.lower()


def test_html_classes_are_prefixed_and_not_shared_stems():
    th = _html_classes(TD_HTML.read_text(encoding="utf-8").split("<script>", 1)[0])
    ch = _html_classes(CD_HTML.read_text(encoding="utf-8").split("<script>", 1)[0])
    assert th and ch
    assert th.isdisjoint(ch)
    assert all(name.startswith("td-") for name in th)
    assert all(name.startswith("cd-") for name in ch)
    stems = {name.split("-", 1)[1] for name in th | ch}
    clash = stems & _FORBIDDEN_STEMS
    assert not clash, f"禁止的共用词干: {sorted(clash)}"
