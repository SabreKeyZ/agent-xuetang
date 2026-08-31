import json
from pathlib import Path

from react_agent import ReactAgent, calculator, evaluate, parse_react_block, search


def test_calculator_happy():
    assert calculator("3 * 7") == "21"
    assert calculator("2 + 5") == "7"


def test_calculator_rejects_names_and_zero():
    assert calculator("__import__('os')") == "error:invalid_expression"
    assert calculator("3/0") == "error:division_by_zero"


def test_search_mcp_week():
    text = search("Agent学堂第几周讲 MCP")
    assert "第4周" in text


def test_parse_fullwidth_colon():
    decision = parse_react_block("Thought：要算一下\nAction：calculator\nAction Input：1+1")
    assert decision is not None
    assert decision.action == "calculator"
    assert decision.action_input == "1+1"


def test_eval_cases_all_pass():
    rows = evaluate()
    assert len(rows) == 3
    assert all(row["ok"] for row in rows), rows


def test_eval_json_has_three_cases():
    data = json.loads((Path(__file__).parent / "eval_cases.json").read_text(encoding="utf-8"))
    assert len(data) == 3


def test_mix_uses_both_tools():
    trace = ReactAgent().run("问学堂是什么？另外 2 + 5 等于多少")
    actions = [row["action"] for row in trace.log]
    assert "search" in actions
    assert "calculator" in actions
    assert "7" in trace.final
