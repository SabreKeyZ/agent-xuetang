# JSON-RPC 三支纸

对着 [`code/week4/week_goal_server.py`](../../code/week4/week_goal_server.py) 的 `handle`（约 92–134 行）。

| method | 本仓做什么 | 成功长什么样 |
| --- | --- | --- |
| `initialize` | 握手，声明协议版本 | `protocolVersion=2024-11-05`，`serverInfo.name=agent-xuetang-week-goal` |
| `tools/list` | 列出 `get_week_goal`、`list_weeks` | `result.tools[].name` |
| `tools/call` | 读磁盘「本周你要带走什么」原文 | `result.content[0].text` |

stdin 一行 JSON，stdout 一行 JSON。本周服务器不打模型。

## 错误码（本仓会碰到的）

| code | 何时 | 本仓现状 |
| --- | --- | --- |
| `-32700` | 一行根本不是 JSON | `serve_stdio` 现在会炸成 `JSONDecodeError`（练习要你包成这个码） |
| `-32000` | 周数非法、未知工具、缺小节 | `handle` 的 `except` 已经走这条 |
| （没有） | 编一段假目标 | 禁止。读文件失败必须是 error，不是散文 |

## 金样：周数非法

```text
$ python code/week4/week_goal_server.py --once --week 99
week 必须是 0-8，收到 99
```

stdio 等价（`handle` 包好的）：

```json
{"jsonrpc":"2.0","id":7,"error":{"code":-32000,"message":"week 必须是 0-8，收到 99"}}
```

## 金样：坏 JSON（练习应写成这样，主分支现在会 traceback）

```json
{"jsonrpc":"2.0","id":null,"error":{"code":-32700,"message":"parse error: Expecting value"}}
```

同一件「查订单」在工单台可以是进程内函数、MCP、Skill，见 [第 4 周](../weeks/04-mcp-and-skills.md)。
