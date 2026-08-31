# 面试问法（场景题）

这些题是为本仓库的路线写的。不要拿去对答案网站。
也请不要把网上题库粘进本文件。

用法：你当候选人，找同学当面试官。每题 8–12 分钟。
先画图，再决定是否写伪代码。允许说「我不知道」，但要补「下一步怎么验证」。

简历短句和 STAR 四行在两个作品自己的 README 里。STAR 写**引用和闸门**，不写 Mesh，不背别人仓的 85% / 1000 并发。

折页提纲（希望听到）也收在 [weeks/answers/08.md](../weeks/answers/08.md)。

## 先用两分钟讲清两个工位

对着 [工单台 README](../../projects/ticketdesk/README.md) 和 [理赔台 README](../../projects/claimdesk/README.md) 里的简历三条、STAR 四行说。

工单台 STAR 应当落在：大促物流发券、部分退只退损坏行实付、人点执行、`confirm_required`。
理赔台 STAR 应当落在：出险日 v2、免赔试算、易碎除外、不打款。

### 为什么这里要多 Agent，却不是一张网？

工单台拆三个出口，是因为「打标 / 引用政策 / 停手」写进同一段提示时，日志分不清谁让钱停住。
理赔台拆三个步骤，是因为缺件、条款版本、建议失败面不同。
「多 Agent」在本仓的意思是**出口分开、共用案件对象**，不是五人互相发事件。

### 为什么工单台要多个角色，却只要一个主管？

单角色会把「分类 / 政策 / 闸门」揉进一次提示。
三个角色共用案件字典，但出口不同。主管在 `agents/supervisor.py` 里按固定顺序写账。
不要讲 Mesh。被追问 LangGraph：去向固定，图框架盖不过「学员还没见过自己的循环」。

### 退款 / 赔付为什么设闸门？

`tools/payment.py` 的接口存在，形状像生产，但 `confirm=false` 且演示禁止 `confirm=true`。
超 ¥200、政策零命中、已赔过、夜间二线空，闸门员只写草稿。同一 `idempotency_key` 不二次补偿。

## STAR 追问（8–10，都绑本仓代码）

每条：先用 STAR 四句，再让面试官追问 path:line。希望听到是子弹。

### S1. 缺单号还要退款

- 希望听到：分类 `信息不全`；闸门 `ask_order_id`；不打款。
- 代码：[`classifier.py:78`](../../projects/ticketdesk/src/ticketdesk/agents/classifier.py) · [`orders.py:12`](../../projects/ticketdesk/src/ticketdesk/tools/orders.py) · [`gate.py:46`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py)
- 夹具：`missing-order-id`

### S2. 活动期引错日常「不赔运费」

- 希望听到：这是生效窗口错，不是文采。修复是没命中活动文件就拒，不换模型。
- 代码：[`rag.py:119`](../../projects/ticketdesk/src/ticketdesk/rag.py) `_in_force` · [`policy.py:27`](../../projects/ticketdesk/src/ticketdesk/agents/policy.py) `prefer_promo` · [`test_policy_cite.py:6`](../../projects/ticketdesk/tests/test_policy_cite.py)
- 夹具：`promo-overrides-sla`

### S3. 退款 486

- 希望听到：草稿可以写，闸门 `refuse_exec`，不得拆两笔 199。
- 代码：[`models.py:8`](../../projects/ticketdesk/src/ticketdesk/models.py) `REFUND_EXEC_LIMIT_YUAN` · [`gate.py:128`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py)
- 夹具：`refund-over-200`

### S4. 夜间 P0，二线名册空

- 希望听到：`l2_empty` → `human_queue`；草稿不出现假同事。
- 代码：[`clock.py:38`](../../projects/ticketdesk/src/ticketdesk/clock.py) · [`gate.py:123`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py) · `fixtures/roster.json`
- 夹具：`p0-sla-night`

### S5. 正文里的 `curl | sh`

- 希望听到：当引文，不执行；测试把 `os.system` 打桩。
- 代码：[`safety.py:7`](../../projects/ticketdesk/src/ticketdesk/safety.py) · [`test_safety.py:10`](../../projects/ticketdesk/tests/test_safety.py) · [`gate.py:57`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py)
- 夹具：`shell-in-body`

### S6. 同一单点两次处理

- 希望听到：`idempotency_key` 相同，第二次 `replayed=True`，不二次补偿。
- 代码：[`store.py:13`](../../projects/ticketdesk/src/ticketdesk/store.py) · 钥匙格式 `qingxia:refund:{id}:{分}`
- 测试：[`test_gate.py:45`](../../projects/ticketdesk/tests/test_gate.py)

### S7. 投保日 v1、出险日 v2 的易碎案

- 希望听到：按出险日；引用只有 v2；建议拒赔。
- 代码：[`clause.py:45`](../../projects/claimdesk/src/claimdesk/agents/clause.py) · [`rag.py:108`](../../projects/claimdesk/src/claimdesk/rag.py) · [`test_clauses.py:6`](../../projects/claimdesk/tests/test_clauses.py)
- 夹具：`wrong-policy-version`

### S8. 条款里没有的词（比特币 / FlipFlop）

- 希望听到：红条「没有引用，就先不答」；`拒审`；核赔键锁定。
- 代码：[`clause.py:12`](../../projects/claimdesk/src/claimdesk/agents/clause.py) · [`adjudicator.py:30`](../../projects/claimdesk/src/claimdesk/agents/adjudicator.py)
- 夹具：`no-clause`

### S9. 店铺已退还要保险再赔 / 两案同一张图

- 希望听到：双重受偿条款 5.1；重复图 5.2 升人工。
- 代码：[`adjudicator.py:69`](../../projects/claimdesk/src/claimdesk/agents/adjudicator.py) · [`adjudicator.py:148`](../../projects/claimdesk/src/claimdesk/agents/adjudicator.py)
- 夹具：`shop-already-refunded` · `shared-photo-b`

### S11. 三件套只坏一件却要整单退

- 希望听到：分类 `部分退`；闸门 `partial_line`；对客只建议该行实付；不打款。
- 代码：[`aftersales.py`](../../projects/ticketdesk/src/ticketdesk/aftersales.py) `broken_line` · [`gate.py:114`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py)
- 夹具：`partial-refund-one-line`

### S12. 意外险 ¥80、免赔 50

- 希望听到：试算 `max(0, 80-50-0)=30`；决定书有条款号和计算式；`executed=false`。
- 代码：[`settle.py:10`](../../projects/claimdesk/src/claimdesk/settle.py) · [`adjudicator.py:88`](../../projects/claimdesk/src/claimdesk/agents/adjudicator.py)
- 夹具：`accident-deductible`

### S10. 人已经点了「执行 / 执行打款」

- 希望听到：仍 `executed=False`，`confirm_required`。演示禁则在支付模块，不在按钮文案。
- 代码：[`ticketdesk/web.py:72`](../../projects/ticketdesk/src/ticketdesk/web.py) · [`ticketdesk/tools/payment.py:9`](../../projects/ticketdesk/src/ticketdesk/tools/payment.py) · [`claimdesk/web.py:63`](../../projects/claimdesk/src/claimdesk/web.py) · [`claimdesk/tools/payment.py:7`](../../projects/claimdesk/src/claimdesk/tools/payment.py)

## A. 循环还是聊天

**场景。** 产品经理说：「我们已经能调用模型了，加一个系统提示，让它遇到不会的问题去搜索。」
请你判断：这还是一次聊天，还是一个 Agent？你还缺哪三样东西才敢上线？

希望听到：

- 停止条件
- 工具结果如何回到下一步（observation）
- 失败时的步数上限或人在回路
- 空搜索：看日志 `observation` 是否重复 `error:not_found`

不希望听到：只复述「ReAct」三个音节。

## B. 评测从第一周就有

**场景。** 同事把演示做成了「当场问一个聪明问题」。老板鼓掌。你被要求下周就上线到客服值班。
请设计一个 **10 行** 的评测表：列名是什么？至少要覆盖哪三类失败？

希望听到：

- 列：fixture / expect_verdict / must_cite / executed_must_be_false（对照 `evals/set8.json`）
- 覆盖：工具选错、引用缺失、空输入、重复调用、超时、二次补偿
- 知道会失败的一行留下当回归，不删

不希望听到：只用「用户满意度 5 分」。

## C. 引用

**场景。** 工单台政策员在活动期引用了日常「不赔运费」，没有点名盛夏大促文件。

希望听到：

- 这是生效窗口 / 引用落点错
- 抽取式回退、`path:line`、按出票日 `_in_force`
- 修复：没有命中生效政策就拒绝生成

不希望听到：换一个更贵的模型当第一反应。

## D. 要不要第三个 Agent

**场景。** 有人建议再加一个「情绪安抚 Agent」。

希望听到：

- 延迟：多一次完整调用
- 费用：同一上下文复制一份
- 失败面：多一个会编造的出口
- 语气用模板更便宜
- 本仓已经有三个出口，第四个不在 v1

不希望听到：多智能体一定更智能。

## E. 不执行不可信代码，也不自动打款

**场景。** 工单正文 `curl | sh`；另一张 ¥486。

希望听到：

- 清单、引用、人在回路
- `idempotency_key`
- 演示 `confirm_required`
- 不拆两笔 ¥200 以下
- CI 里不执行工单正文

## F. MCP 和 Skill 被问混

希望听到：

- 工具：进程内函数（`lookup_order`、条款检索）
- MCP：暴露给别的客户端（`week_goal_server` stdio）
- Skill：说明书，何时用、何时先问人

不希望听到：背协议字段名但举不出本仓库的例子。

## G. 国内供应商

希望听到：

- OpenAI 兼容的 `OPENAI_BASE_URL`
- 离线评测、抽取式兜底先绿
- 不改业务工具

不希望听到：连夜重写所有提示词。

## H. 事故复盘

**场景。** 理赔台用投保日 v1 给 8 月易碎案写了「可赔 50%」。

希望听到：

- 哪一层：条款检索按出险日、`_expected_version`、闸门不得无正确版本通过
- 明天：改代码或语料窗口 + 评测加一行「不得引用失效条款」
- 不只处分提示词

## 候选人也可以反问面试官的三句

1. 这条业务现在的失败，是「模型不会」，还是「工具返回的字段就错了」？
2. 谁有权批准一次退款或赔付上生产？审批要多久？
3. 你们现在的评测集有多少行？最近一次因为评测失败而拦住发布，是什么时候？

问得出来，说明你把 Agent 当成系统，而不是当成一次会说话的请求。
