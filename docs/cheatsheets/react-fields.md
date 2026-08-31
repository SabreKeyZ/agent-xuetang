# ReAct 字段纸

对着 [`code/week2/react_agent.py`](../../code/week2/react_agent.py) 的 `parse_react_block`（约 131–142 行）。

| 字段 | 认什么 | 本仓写到日志的哪一列 |
| --- | --- | --- |
| Thought / thought | 这一步为什么动手 | `thought` |
| Action / action | 工具名或 finish | `action` |
| Action Input / action_input | 传给工具的参数 | 不单独打行，进工具 |
| Observation | 工具返回（解析器不读，循环写） | `observation` |
| Final Answer / final | 收口 | `action=finish` |

## 全角冒号

解析器用的是 `Name\s*[：:]\s*(.+)`。下面两行都算：

```text
Action: calculator
Action：calculator
```

下面不算，会打出 `error:parse`：

```text
我想用计算器算 3*7
Action calculator
Thought 我忘了冒号
```

本机：

```bash
python code/week2/react_agent.py --parse "我想算一下但是忘了字段"
# error:parse
# 退出码 1
```

全角能过：

```bash
python code/week2/react_agent.py --parse $'Thought：要算一下\nAction：calculator\nAction Input：1+1'
# {"thought": "要算一下", "action": "calculator", "action_input": "1+1"}
```

## 工单台怎么对上这四个字段

政策员不是在聊「我想想」。它的 Action 是 `search_policy`，Observation 是带 `path:line` 的摘录。闸门员的 Final 是草稿 + `confirm_required`，不是一段软话。
详：[../weeks/02-tools-and-react.md](../weeks/02-tools-and-react.md)
