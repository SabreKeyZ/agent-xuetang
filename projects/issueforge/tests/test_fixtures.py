from issueforge.agents.scribe import draft_reply
from issueforge.agents.triage import classify, guess_duplicate, triage
from issueforge.cli import main as issueforge_main
from issueforge.loader import load_all_fixtures, load_fixture
from issueforge.report import process, to_html, to_markdown


def _by_id() -> dict:
    return {i.fixture_id: i for i in load_all_fixtures()}


def test_expected_kinds():
    items = _by_id()
    assert classify(items["bug-empty-docs"]) == "bug"
    assert classify(items["bug-crash"]) == "bug"
    assert classify(items["feature-export"]) == "feature"
    assert classify(items["question-how"]) == "question"
    assert classify(items["question-disguised"]) == "question"
    assert classify(items["duplicate-a"]) == "bug"


def test_near_duplicate_titles():
    items = _by_id()
    catalog = load_all_fixtures()
    num, score = guess_duplicate(items["duplicate-b"], catalog)
    assert num == 50
    assert score >= 0.45


def test_empty_docs_close_to_crash_fixture():
    items = _by_id()
    catalog = load_all_fixtures()
    out = triage(items["bug-crash"], catalog)
    assert out["kind"] == "bug"
    assert out["duplicate_of"] in {12, None} or out["duplicate_score"] >= 0.3


def test_scribe_is_bilingual():
    issue = load_fixture("question-how")
    bundle = process(issue, load_all_fixtures())
    md = to_markdown(bundle)
    assert "### 中文" in md
    assert "### English" in md
    assert bundle["scribe"]["zh"]
    assert bundle["scribe"]["en"]
    reply = draft_reply(issue, bundle["triage"], bundle["repro"])
    assert "不能承诺" in reply["zh"]
    assert "cannot promise" in reply["en"].lower()


def test_demo_all_fixtures_produce_kind():
    catalog = load_all_fixtures()
    assert len(catalog) >= 6
    for issue in catalog:
        bundle = process(issue, catalog)
        assert bundle["triage"]["kind"] in {"bug", "feature", "question"}
        assert bundle["repro"]["executed_code"] is False


def test_html_report_lists_fixtures_and_bilingual_reply():
    catalog = load_all_fixtures()
    bundles = [process(i, catalog) for i in catalog]
    html = to_html(bundles)
    assert "bug-empty-docs" in html
    assert "question-how" in html
    assert "feature-export" in html
    assert "复现清单" in html
    assert "不能承诺" in html
    assert "cannot promise" in html
    assert "never_execute" in html
    assert "<html" in html
    assert "「" in html and "」" in html
    assert "没有引用，就先不答" in html


def test_board_writes_self_contained_file(tmp_path):
    out = tmp_path / "duty-report.html"
    assert issueforge_main(["board", "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert out.is_file()
    assert "开源值班台" in text
    assert "夹具" in text
    assert "bug" in text
