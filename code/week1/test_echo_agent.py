from echo_agent import EchoAgent, MAX_STEPS, rule_brain


def test_weekday_query_calls_tool():
    agent = EchoAgent(rule_brain)
    result = agent.run("今天星期几")
    actions = [row["action"] for row in result["log"]]
    assert "weekday" in actions
    assert result["log"][-1]["action"] == "finish"
    assert "工具返回：" in result["final"]


def test_max_steps_one_admits_incomplete():
    agent = EchoAgent(rule_brain)
    result = agent.run("今天星期几", max_steps=1)
    # 第一步只会调用工具，到上限后必须承认没做完
    assert result["final"].startswith("没做完") or (
        result["log"][-1]["action"] == "finish" and result["log"][-1]["thought"] == "hard stop"
    )


def test_unknown_sentence_finishes_without_tool():
    agent = EchoAgent(rule_brain)
    result = agent.run("随便聊聊天气")
    assert all(row["action"] != "weekday" for row in result["log"])
    assert result["final"] == "随便聊聊天气"


def test_log_fields_are_stable():
    agent = EchoAgent(rule_brain)
    result = agent.run("周几")
    for row in result["log"]:
        assert set(row) >= {"step", "thought", "action", "observation"}


def test_default_max_steps_is_small():
    assert MAX_STEPS <= 8
