# 学堂词表

一句话能讲清就进表。广告词、框架百科不进。
一页纸：[cheatsheet.md](cheatsheet.md) · 分册：[cheatsheets/](cheatsheets/)

| 词 | 一句话 | 易混 | 链回 |
| --- | --- | --- | --- |
| Agent | 会停下来的循环：think → act → observe。 | 一次 chat completion 不是 Agent。 | [第 1 周](weeks/01-what-is-an-agent.md) |
| 聊天补全 | `POST /chat/completions` 一问一答就结束。 | 加长系统提示不会把它变成循环。 | [第 0 周](weeks/00-setup.md) |
| 兼容口 | 同一套 `/chat/completions` JSON，换 `OPENAI_BASE_URL` 即换厂商。 | 不是「只有官方 OpenAI 才叫兼容」。 | [第 0 周](weeks/00-setup.md) |
| MAX_STEPS | 循环硬上限，到了必须 `finish`。`echo_agent` 默认 6。 | 不是「模型说做完了」。 | [第 1 周](weeks/01-what-is-an-agent.md) |
| CoT | 只想不伸手，没有 Action。 | 和 ReAct 差一只手；工单台政策员不能只 CoT。 | [第 2 周](weeks/02-tools-and-react.md) |
| ReAct | 把循环写成 Thought / Action / Action Input / Observation 字段。 | 不是信仰，是解析器要抠的键。 | [第 2 周](weeks/02-tools-and-react.md) · [字段纸](cheatsheets/react-fields.md) |
| Thought | 这一步为什么选这个动作。 | 不是给用户看的最终答。 | [第 1 周](weeks/01-what-is-an-agent.md) |
| Action | 工具名或 `finish`。 | 空 Action 又没有 Final Answer → `error:parse`。 | [第 2 周](weeks/02-tools-and-react.md) |
| Observation | 工具返回的文字，喂回下一步。 | 失败也要写成 `error:…`，不要吞掉。 | [第 1 周](weeks/01-what-is-an-agent.md) |
| 工具 | 当前进程里的函数，循环直接 `call`。 | 不是 MCP，也不是 Skill。 | [第 2 周](weeks/02-tools-and-react.md) |
| MCP | 用 JSON-RPC 把工具暴露给**别的进程**。 | 不是「比工具高级」。 | [第 4 周](weeks/04-mcp-and-skills.md) · [三支纸](cheatsheets/jsonrpc-three.md) |
| Skill | 给套件看的短说明书：何时用、哪几条不得。 | 不是服务器，不是加长系统提示。 | [第 4 周](weeks/04-mcp-and-skills.md) |
| 短记忆 | 这次对话的 messages，窗口满了就丢。 | 不是磁盘上的政策文件。 | [第 3 周](weeks/03-memory-rag.md) |
| 长记忆 | 写在磁盘上、下次进程还在的文件。 | 粘进提示当「记忆」会先烧账单。 | [第 3 周](weeks/03-memory-rag.md) |
| RAG（本课） | 先检索，再允许说话；每条命中必须 `path:line`。 | 0 命中仍「凭印象」答，不是本课。 | [第 3 周](weeks/03-memory-rag.md) · [引用纸](cheatsheets/path-line.md) |
| path:line | 相对仓库根或项目根的引用，编辑器能跳转。 | 绝对路径换机器就废。 | [第 3 周](weeks/03-memory-rag.md) |
| 引用芯片 | UI 上贴着的 `docs/policy/…:行号` 或 `条款 3.2 · …`。 | 打码姓名可以，打码引用不行。 | [第 6 周](weeks/06-ticketdesk.md) |
| 抽取式 | 没 Key 时只摘录检索原文，不打云端。 | 看起来「能跑」不等于 Key 已生效。 | [第 6 周](weeks/06-ticketdesk.md) |
| 主管 | 只分流、写账，不互叫成网。 | 不是超级专家，也不该再调用自己。 | [第 5 周](weeks/05-multi-agent.md) |
| Mesh | 角色互相发事件、互相打断。 | 本仓 v1 不用。工单台不是五人网。 | [第 5 周](weeks/05-multi-agent.md) |
| SLA | 从 `created_at` 到 `now` 是否超时。 | 超时且二线空 ≠ 编一个值班人。 | [第 6 周](weeks/06-ticketdesk.md) |
| 闸门 | 最后一个出口：写 next_action，永不 `executed=true`。 | 不是「再写软一点的客服」。 | [第 6 周](weeks/06-ticketdesk.md) · [三角色](cheatsheets/ticketdesk-roles.md) |
| 条款版本 | 按**出险日**滤生效窗口。 | 投保日印象不能用来逃 v2 除外。 | [第 7 周](weeks/07-claimdesk.md) |
| 出险日 | 事故发生的那天，检索 `at=incident_at`。 | 不是投保日，也不是申请日。 | [第 7 周](weeks/07-claimdesk.md) |
| 双重受偿 | 店铺已退，保险再赔同一损失。 | 活动运费补偿也不能再补一笔。 | [第 7 周](weeks/07-claimdesk.md) |
| idempotency | 同一把钥匙处理第二次，不二次补偿。 | 钥匙变了才是新账，不是「再点一次」。 | [第 6 周](weeks/06-ticketdesk.md) |
| confirm_required | 退款 / payout 接口存在，演示不接受打款。 | 人点「执行」仍是这条状态。 | [cheatsheet 禁则](cheatsheet.md) |
| 人在回路 | 打款、改单、删文件必须等人点头。 | 不是「模型说我做完了」。 | [第 4 周](weeks/04-mcp-and-skills.md) |
| 夹具 | 预先写好的脏工单 / 脏案件。 | 不是当场编一个聪明问题。 | [第 6 周](weeks/06-ticketdesk.md) |
| vibe 编码 | 对着助手说话改文件，diff 你验收。 | 不是一次贴完全部规格等聊天皮。 | [vibe](weeks/vibe.md) · [vibe-claim](weeks/vibe-claim.md) |
| 雾津保 | vibe-claim 虚构保险人，案号 `K-42xx`。 | 不是青途保，不要对齐 C-20xx。 | [vibe-claim](weeks/vibe-claim.md) |
| 红条 | 拒绝句：没有引用，就先不答。 | 不是漫画弹窗，也不是「换个模型再试」。 | [第 3 周](weeks/03-memory-rag.md) |
| 分类员 | 工单台：类型 + 紧急度，不改订单。 | 和闸门员不是同一个出口。 | [三角色](cheatsheets/ticketdesk-roles.md) |
| 政策员 | 工单台：生效中的 `path:line`，零命中拒绝。 | 活动期不得只用日常「不赔运费」。 | [第 6 周](weeks/06-ticketdesk.md) |
| 核赔员 | 理赔台：通过 / 补件 / 拒赔，不打款。 | 缺件只出清单，不审结。 | [禁止项](cheatsheets/claimdesk-roles.md) |
