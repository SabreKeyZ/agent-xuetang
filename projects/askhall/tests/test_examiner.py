from askhall.agents.examiner import REFUSE_EMPTY, Examiner, grade_answer
from askhall.agents.supervisor import Supervisor


def test_empty_answer_via_pending_quiz_is_refused():
    quiz = Supervisor().handle("考我循环三步")
    out = Supervisor().handle("", pending_quiz=quiz["pending_quiz"])
    assert out["turns"][0]["refused"] is True


def test_empty_answer_is_refused():
    result = grade_answer("", "think act observe", "循环三步是什么")
    assert result["refused"] is True
    assert result["passed"] is False
    assert REFUSE_EMPTY in result["body"]


def test_whitespace_only_is_refused():
    result = grade_answer("   \n  ", "MCP", "什么是 MCP")
    assert result["refused"] is True


def test_non_empty_is_graded():
    result = grade_answer("循环是 think、act、再 observe。", "think act observe", "三步")
    assert result["refused"] is False
    assert result["passed"] is True


def test_demo_includes_refuse():
    script = Supervisor().demo()["script"]
    last = script[-1]["turns"][0]
    assert last["refused"] is True


def test_ask_returns_one_question():
    asked = Examiner().ask("MCP")
    assert asked["role"] == "examiner"
    assert asked["body"]
    assert asked.get("answer_key")
