from classroom_lab import handle, route


def test_route_exam_and_plan():
    assert route("考我一下") == "examiner"
    assert route("怎么学循环") == "planner"
    assert route("解释主管") == "tutor"


def test_empty_grade_refuses():
    out = handle("空答")
    assert out["refused"] is True
    assert out["citations"] == []


def test_unknown_refuses():
    out = handle("什么是 FlipFlopZetaQueue")
    assert out["refused"] is True


def test_plan_has_citation():
    out = handle("怎么学循环")
    assert out["citations"]
    assert all("classroom.md:" in c for c in out["citations"])
