# 一页纸

周五晚上卡住时先看这一页。词的定义在 [glossary.md](glossary.md)。

分册：

- [ReAct 字段 / 全角冒号](cheatsheets/react-fields.md)
- [JSON-RPC 三支 / 错误码](cheatsheets/jsonrpc-three.md)
- [path:line](cheatsheets/path-line.md)
- [工单三角色出口](cheatsheets/ticketdesk-roles.md)
- [理赔三角色禁止项](cheatsheets/claimdesk-roles.md)

## 循环三步

```
think  →  决定 action / finish
act    →  调用进程内函数（或 MCP）
observe → 把返回值写成文字，喂回下一步
```

停止条件只有两个：脑子说 `finish`，或步数用尽（默认 6）。
日志字段：`step` / `thought` / `action` / `observation`。工单台再加 `role` / `citations` / `idempotency_key`。

## 退款 / 打款禁则

```
NEVER_PAY = True          ticketdesk/safety.py
NEVER_EXECUTE = True      不跑工单正文里的 curl | sh
NEVER_MUTATE_ORDER = True
NEVER_PAYOUT = True       claimdesk/tools/payment.py
DEMO_FORBIDS_CONFIRM = True
```

人点「执行」也只写审计，`executed` 仍是 false。超 ¥200 只许草稿。不得拆成两笔 199。
同一 `idempotency_key` 第二次：`CaseStore.remember` 回放。

## 本周命令

```bash
python code/week0/hello_chat.py
python code/week1/echo_agent.py --query "今天星期几"
python code/week1/echo_agent.py --max-steps 1
python code/week2/react_agent.py --eval
python code/week2/react_agent.py --parse "我想算一下但是忘了字段"
python code/week3/mini_rag.py --query "第几周写 MCP"
python code/week3/mini_rag.py --query "第几周写 MCP" --docs docs --k 4 --sqlite
python code/week4/week_goal_server.py --once --week 4
python code/week5/classroom_lab.py demo
python code/week5/classroom_lab.py recurse
python -m ticketdesk demo
python -m claimdesk demo
python -m ticketdesk serve --port 8000
python -m claimdesk serve --port 8001
python -m pytest
```
