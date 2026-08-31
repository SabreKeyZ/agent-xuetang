# 学徒工期目录

默认 8 周 × 5–6 小时。压缩 6 周见根目录 README 的工期条。做不完就停在验收，不要跳周。

词表：[../glossary.md](../glossary.md) · 一页纸：[../cheatsheet.md](../cheatsheet.md) · 分册：[../cheatsheets/](../cheatsheets/) · 参考答案：[answers/](answers/)（做完题再打开）

## 资料怎么用

顺序反了，这套包会变成「我看懂了但写不出来」。请按这个走：

1. **先打开当周文档的「本周你要带走什么」**，用铅笔在纸上抄勾选框。这是验收，不是目录装饰。
2. **先做带练命令，再看视频。** 视频课表在 [../videos.md](../videos.md)。口播用来补直觉，作业以本仓库脚本的 stdout 为准。看不完不要自责。
3. **先自己做练习题，再打开 `answers/`。** 正文故意不写答案。抄答案过验收，第 8 周面试会穿。
4. **失败对照比成功路径更重要。** 错 Key、空目录、除零、坏 JSON、无条款命中，都是本周要亲手跑的。
5. **卡超过 40 分钟，去 [FAQ](../faq.md) 搜报错关键字。** 还不行按 [卡住了](../../.github/ISSUE_TEMPLATE/stuck.yml) 开 Issue。不要先换框架。
6. **第 6–7 周以两个队列为作业。** 教室玩具、问学堂、五人教育网不是毕业作品。

| 周 | 文档 | 小时 |
| --- | --- | --- |
| 0 | [把桌子摆好](00-setup.md) | 5 |
| 1 | [Agent 是循环](01-what-is-an-agent.md) | 5 |
| 2 | [工具与 ReAct](02-tools-and-react.md) | 6 |
| 3 | [记忆与 RAG](03-memory-rag.md) | 5 |
| 4 | [MCP 与 Skill](04-mcp-and-skills.md) | 5 |
| 5 | [多智能体](05-multi-agent.md) | 5 |
| 6 | [客服工单台](06-ticketdesk.md) | 6 |
| 7 | [理赔初审台](07-claimdesk.md) | 6 |
| 8 | [上线与求职](08-ship-and-job.md) | 5 |

八周对照（不是别人仓的「理解原理→面试」四段，是本仓工期）：

| 工期 | 打开哪篇 | 改哪份代码 | 手上能演示什么 |
| --- | --- | --- | --- |
| 0 | [00-setup](00-setup.md) | 两台 demo；可选 `hello_chat.py` | 芯片或红条；可选 `[ok] reply=` |
| 1 | [01-what-is-an-agent](01-what-is-an-agent.md) | `code/week1/echo_agent.py` | 一行一条 JSON 循环 |
| 2 | [02-tools-and-react](02-tools-and-react.md) | `code/week2/react_agent.py` | `--eval` 三条 PASS |
| 3 | [03-memory-rag](03-memory-rag.md) | `code/week3/mini_rag.py` | `path:line` 命中 |
| 4 | [04-mcp-and-skills](04-mcp-and-skills.md) | `code/week4/week_goal_server.py` | stdio `get_week_goal` |
| 5 | [05-multi-agent](05-multi-agent.md) | `code/week5/classroom_lab.py` | 画路由、决定不加第四人 |
| 6 | [06-ticketdesk](06-ticketdesk.md) | `projects/ticketdesk` | 芯片 + 闸门红条 |
| 7 | [07-claimdesk](07-claimdesk.md) | `projects/claimdesk` | 条款芯片 + 决定书 |
| 8 | [08-ship-and-job](08-ship-and-job.md) | README / 评测 / Docker | 两分钟讲清两个队列 |

视频：[../videos.md](../videos.md) · 求职：[../jobs/roles.md](../jobs/roles.md) · 坑：[../faq.md](../faq.md) · 延伸：[../resources.md](../resources.md)
