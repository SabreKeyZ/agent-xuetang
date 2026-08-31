import io
import json

from week_goal_server import get_week_goal, handle, serve_stdio


def test_get_week_goal_mentions_mcp_server():
    text = get_week_goal(4)
    assert "MCP" in text
    assert "目标" not in text.splitlines()[0] or "MCP" in text


def test_week_out_of_range_is_error():
    msg = handle(
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {"name": "get_week_goal", "arguments": {"week": 99}},
        }
    )
    assert "error" in msg
    assert msg["id"] == 7


def test_tools_list_includes_get_week_goal():
    msg = handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    names = [t["name"] for t in msg["result"]["tools"]]
    assert "get_week_goal" in names


def test_stdio_roundtrip():
    incoming = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "get_week_goal", "arguments": {"week": 4}},
        }
    )
    stdin = io.StringIO(incoming + "\n")
    stdout = io.StringIO()
    serve_stdio(stdin, stdout)
    reply = json.loads(stdout.getvalue().strip().splitlines()[0])
    body = reply["result"]["content"][0]["text"]
    assert "stdio" in body or "MCP" in body
