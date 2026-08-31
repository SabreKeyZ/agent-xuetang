from askhall.agents.supervisor import Supervisor


def test_exam_phrase_routes_to_examiner():
    assert Supervisor().route("考我一下 MCP") == "examiner"
    assert Supervisor().route("出一道测验") == "examiner"


def test_plan_phrase_routes_to_planner():
    assert Supervisor().route("怎么学工具调用") == "planner"
    assert Supervisor().route("给我一个学习计划") == "planner"


def test_explain_routes_to_tutor():
    assert Supervisor().route("什么是短记忆") == "tutor"
    assert Supervisor().route("解释一下 MCP 和 Skill 的区别") == "tutor"


def test_handle_exam_returns_examiner_role():
    out = Supervisor().handle("考我记忆和 RAG")
    assert out["route"] == "examiner"
    assert out["turns"][0]["role"] == "examiner"
    assert out["pending_quiz"] is not None
