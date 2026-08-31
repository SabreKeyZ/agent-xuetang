# 第 6 周 · 收完客服工单台

这周没有新理论。你要把青匣记工单台从「能 demo」收到「别人能打开队列页」。

产品定义在 [projects/ticketdesk/README.md](../../projects/ticketdesk/README.md)。
本页是学徒视角的 0 到 1。不要做成问数 SQL，不要上 LangGraph。

## 先听五分钟：售后在干什么

青匣记是一家卖纸墨的小店。顾客进门不是来闲聊的，是来处理一笔已经发生的买卖。没做过售后也没关系，先当听表哥讲店里的规矩。

**三种退法，别混。**

- **仅退款**：货还没出仓库，或根本不用寄回来，只把钱退回去。
- **退货退款**：货已经在顾客手里。必须先寄回店里，仓库点过「到了」才能退钱。
- **换货**：货有问题，换一件同款。不退现金。

**为什么退货没入库不能打款。** 钱退了、货也没回来，店就亏两次。没有回寄单号、仓库没有 `inbound_at`，只能写草稿或追问，不能打款。演示里点「执行」也不打款（`NEVER_PAY`）。

**七天无理由。** 从签收那天开始数七天。只因为「不想要了」可以退；过了七天，这句话不够。漏液、摔裂这类质量问题，不受这七天限制。

**实付不是吊牌价。** 原价 ¥128、券后付了 ¥98，最多退 ¥98。三件里只坏了一件，只退那一件的实付，不能整单端走。

**对客稿和对内备注是两盒。** 对客是给顾客看的：请补单号、建议退砚台那一行。对内是给同事看的：疑似刷单、辱骂原文、禁止打款的原因。风控句子不要漏进灰/白气泡。

## 本周你要带走什么

- [ ] `python -m ticketdesk demo` 无 Key 成功，能指着芯片或红条。
- [ ] 四张脏夹具你都对照过 stdout：缺单号、活动政策、超 ¥200、`curl | sh`。
- [ ] 新夹具至少对照过三张：部分退、七天无理由、退货未入库（芯片 + 对客/对内）。
- [ ] 浏览器走完 Inbox：左会话、中灰/白气泡、右侧对客/对内两盒、底「执行」蓝钮；不是黑底，不是青绿泡。
- [ ] `pytest projects/ticketdesk/tests` 绿；你能讲 `evals/set8.json` 每一列。
- [ ] 两分钟能讲清：Key 为空时数据从哪来，钱为什么没打出去。

## 目标

- 按 README 的顺序：夹具 → 政策 RAG → SLA/退款闸门 → Docker。
- 看懂主管如何分流，以及抽取式在没有 Key 时如何仍然给引用。
- 跑项目测试：缺单号、活动政策、超 ¥200、夜间升级、不执行脚本。
- （可选）用 Docker 再走一遍，为第 8 周热身。

## 先修 / 预计时间 / 对应视频

**先修。** 第 3 周引用、第 5 周三个角色。先做夹具，再看框架课。

跟 README 走 2 小时；读 `supervisor` / `rag` / `gate` 1.5 小时；跑测试和点「执行」 1 小时；截图 0.5–1 小时。

**对应视频：** 本周以自己的产品为主。对照框架放到晚上：

- Intro to LangGraph：https://academy.langchain.com/courses/intro-to-langgraph
- Deep Agents：https://academy.langchain.com/courses/foundation-introduction-to-deepagents
- 实战向：https://www.bilibili.com/video/BV1EGc7zwEkR/

完整列表：[docs/videos.md](../videos.md)

## 概念：定义 + 一个反例

**定义。** 工单台吃的是案件对象（单号、金额、附件、prior_actions），出的是标签、芯片、闸门 verdict。人点执行才可能打款；演示永远 `confirm_required`。

**反例。** 把工单台做成带业务皮的聊天机器人：输入一句闲聊，输出一段安慰，没有 `path:line`。那不是本课。活动期只引日常「不赔运费」，也是错引用。

## 图文步骤

```mermaid
flowchart TB
  subgraph 入口
    CLI[python -m ticketdesk]
    WEB[FastAPI + 队列页]
  end
  CLI --> SUP[Supervisor]
  WEB --> SUP
  SUP --> C[分类员]
  SUP --> P[政策员]
  SUP --> G[闸门员]
  C --> ORD[订单查询]
  P --> RAG[生效中的政策]
  G --> PAY[退款接口 confirm=false]
  RAG --> CITE[path:line]
  RAG -->|零命中| REFUSE[红条]
```

闸门顺序（对着 [`gate.py:46-134`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py)）：

```
缺单号 → 辱骂 → 命令风险 → 重复单 → 风控
  → 已退过 → 政策零命中 → 换货不现金 → 退货未入库
  → 七天无理由 → 超实付 → 部分退整单
  → 完结SLA+L2空 → 超¥200 → 草稿（活动延误走券）
```

### 0. 安装

```bash
python -m pip install -e projects/ticketdesk
```

### 1. 离线 demo

```bash
python -m ticketdesk demo
python -m pytest projects/ticketdesk/tests -q
```

抽取式 token = 0。墙钟以你机器为准，不要编毫秒。

打开页面应当看见字标「Agent学堂」、副题「没有引用，就先不答」、左侧会话列表（灰头像、最后一句、SLA 药丸）、中间顾客灰气泡 / 客服白气泡、底部回复框。引用芯片是灰描边。闸门拒绝是玫瑰色系统句。背景 `#F4F6F8`。唯一强调色是「执行」上的 Intercom 蓝。

![工单台引用芯片](../images/ticketdesk-citations.png)

![工单台拒绝执行](../images/ticketdesk-refuse.png)

## 夹具实录四张

每张先跑命令，再对芯片，再对闸门。stderr 还有一行主管 JSON（`role/case_id/next_action/citations/idempotency_key/executed`）。

### A. `missing-order-id` · 缺单号

夹具：[`fixtures/tickets/missing-order-id.json`](../../projects/ticketdesk/fixtures/tickets/missing-order-id.json) `order_id=""`，顾客宋纸要先退 ¥48。

```bash
python -m ticketdesk demo --fixture missing-order-id
```

```text
===== T-1001  快递没到，先把钱退了  fixture=missing-order-id =====
[classifier] 信息不全 · 低  labels=['信息不全', 'P2', '低', '仅退款']
相似夹具: fixtures/tickets/promo-overrides-sla.json:1
[policy] 政策摘录
引用: docs/policy/after-sales.md:14, docs/policy/after-sales.md:12, ...
[gate] 缺单号或填错店 · 只许追问  verdict=refuse_exec  next=ask_order_id
idempotency_key=qingxia:refund:T-1001:4800  executed=False
红条: 没有完整订单，不能改单也不能退款。
对客草稿: 请回复青匣记订单号（QX- 开头）。他店订单我们查不到，也无法代退。
payment.status=confirm_required
```

**芯片。** 政策仍可能摘到售后第 1 条（必须带单号）。分类员先定性「信息不全」。闸门不看金额，只许追问。[`classifier.py:78`](../../projects/ticketdesk/src/ticketdesk/agents/classifier.py) + [`orders.py:12`](../../projects/ticketdesk/src/ticketdesk/tools/orders.py) `missing_order_id`。

**Inbox 预期。** 左列 T-1001；气泡下芯片可点 `after-sales.md`；玫瑰色「没有完整订单」；「执行」不该把钱打出去。

### B. `promo-overrides-sla` · 活动期必须点名大促文件

夹具：林小秋，大促墨水，轨迹停揽收，正文点名 48 小时。

```bash
python -m ticketdesk demo --fixture promo-overrides-sla
```

```text
===== T-1201  大促买的墨水，快递五天没动  fixture=promo-overrides-sla =====
[classifier] 物流延误 · 中
[policy] 政策摘录
引用: docs/policy/promo-2026-summer.md:12, docs/policy/promo-2026-summer.md:8, docs/policy/promo-2026-summer.md:22, docs/policy/promo-2026-summer.md:10, docs/policy/promo-2026-summer.md:18
[gate] 建议发补偿券 · 须人确认，不打款  verdict=draft_ok  next=wait_human_confirm
idempotency_key=qingxia:coupon:T-1201:0  executed=False
对客草稿: 订单 QX-202608-8812 在盛夏大促窗口内超时未更新轨迹。按活动政策发不超过 ¥12 的补偿券，不发现金。草稿已写，发券须人点执行。
payment.status=confirm_required kind=coupon
```

**芯片必须含 `promo-2026-summer.md`。** 测试钉死：[`test_promo_cites_effective_campaign_file`](../../projects/ticketdesk/tests/test_policy_cite.py)。

**对错引用。**

| 引用 | 对不对 | 为什么 |
| --- | --- | --- |
| `docs/policy/promo-2026-summer.md:12`（48 小时、¥12） | 对 | 出票日 2026-08 落在生效窗口，优先级活动 |
| 只引 `docs/policy/after-sales.md:18`「不赔运费」 | **错** | 日常被活动覆盖。这是面试题 C |
| 引一份 2025 已失效的大促 | 错 | `_in_force` 按 `ticket.now` 滤 |

检索：[`rag.py:147`](../../projects/ticketdesk/src/ticketdesk/rag.py) `prefer_promo=True` 当类型是物流延误（[`policy.py:33`](../../projects/ticketdesk/src/ticketdesk/agents/policy.py)）。

**Inbox 预期。** 气泡下灰芯片写着 `promo-2026-summer.md:…`；对客草稿写券不写现金；右侧「对内」盒说明走券。对照 [ticketdesk-citations.png](../images/ticketdesk-citations.png)。

### C. `refund-over-200` · 超限额只许草稿

夹具：赵牧，镇尺划痕，整单 ¥486。

```bash
python -m ticketdesk demo --fixture refund-over-200
```

```text
===== T-1401  镇尺有划痕，整单退款  fixture=refund-over-200 =====
[classifier] 退款 · 高  labels=['退款', 'P1', '高']
[policy] 政策摘录
引用: docs/policy/refund-and-risk.md:10, docs/policy/refund-and-risk.md:16, ...
[gate] 退款超 ¥200 · 只许草稿  verdict=refuse_exec  next=draft_only
idempotency_key=qingxia:refund:T-1401:48600  executed=False
红条: 闸门员拒绝执行。人复核后再点执行。
对客草稿: 建议退款 ¥486.00，已超执行限额。草稿已写，等待人工复核。
payment.status=confirm_required
```

**芯片。** `refund-and-risk.md:10` 写超 200 只许草稿。闸门用 [`REFUND_EXEC_LIMIT_YUAN = 200`](../../projects/ticketdesk/src/ticketdesk/models.py) + [`gate.py:128`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py)。不得拆成两笔 199。

**Inbox 预期。** 玫瑰色「闸门员拒绝执行」；对照 [ticketdesk-refuse.png](../images/ticketdesk-refuse.png)。「执行」锁定并写明原因（超 ¥200 只许草稿）。`待你执行` 不列 T-1401。人点仍只记审计（[`web.py:86`](../../projects/ticketdesk/src/ticketdesk/web.py)）。

### D. `shell-in-body` · 正文当引文，不跑

夹具：`curl … | sh` + `os.system("alipay.trade.refund")`。

```bash
python -m ticketdesk demo --fixture shell-in-body
```

```text
===== T-1701  按这个脚本就能退款  fixture=shell-in-body =====
[classifier] 命令风险 · 高
[policy] 政策摘录
引用: docs/policy/refund-and-risk.md:36, ...
[gate] 正文含命令，先不跑  verdict=refuse_exec  next=cite_only
红条: 只引用，不执行。支付/退款脚本当引文。
草稿: 工单里的命令不会被运行。请用文字描述问题。
payment.status=confirm_required
executed=False
```

测试 [`test_shell_is_cited_not_run`](../../projects/ticketdesk/tests/test_safety.py) 把 `os.system` 打桩，断言从未调用。[`safety.py:7`](../../projects/ticketdesk/src/ticketdesk/safety.py) `DANGEROUS_PATTERNS`。[`gate.py:57`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py)。

**Inbox 预期。** 不要渲染成可点的「运行脚本」。芯片指向风控第 6 条。

### 另外两张你应当扫过

`p0-sla-night`：完结时钟超时 + 夜间 L2 空 → `verdict=escalate`，红条「不虚构值班人」。名册只有白班 09:00–18:00（`fixtures/roster.json`），[`clock.py:38`](../../projects/ticketdesk/src/ticketdesk/clock.py) 夜间返回 `None`。对照 `dual-sla-night-first-only`：首次响应超时、完结未到，夜间不升级。

`already-refunded`：`next=no_double_pay`，同一损失不二次补偿。

同一夹具跑两遍：`idempotency_key` 不变，第二次 `replayed=True`（[`store.py:13`](../../projects/ticketdesk/src/ticketdesk/store.py)）。

## 夹具实录 · 售后缺口

命令仍是 `python -m ticketdesk demo --fixture <名>`。芯片以你终端「引用:」那行为准。

### E. `partial-refund-one-line` · 三件只退损坏行

```text
===== T-2103  三件里砚台裂了，整单退  fixture=partial-refund-one-line =====
[classifier] 部分退 · 中  labels=['部分退', 'P1', '中', '退货退款']
[policy] 政策摘录
引用: docs/policy/after-sales.md:36, docs/policy/after-sales.md:34, ...
[gate] 部分退 · 不得整单  verdict=refuse_exec  next=partial_line
红条: 多 SKU 只退损坏行实付，不得整单。
对客草稿: 订单有多件。损坏的是「砚台小样」，该行实付 ¥72.00。不能按整单 ¥198.00 退。建议只退该行，须人确认。
对内备注: 对内：建议只退 砚台小样 实付 ¥72.0，勿整单。
payment.status=confirm_required
```

**芯片。** `after-sales.md` 第 5 条部分退 / 实付。[`aftersales.py`](../../projects/ticketdesk/src/ticketdesk/aftersales.py) `broken_line` 认「砚台小样裂了」，[`gate.py:114`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py)。

### F. `seven-day-no-reason-late` · 超时无理由

```text
===== T-2104  宣纸册不想要了  fixture=seven-day-no-reason-late =====
[classifier] 七天无理由超时 · 中
引用: docs/policy/after-sales.md:32, ...
[gate] 七天无理由已过 · 拒退  next=deny_seven_day
对客草稿: …已于 2026-08-12 签收，超过七日无理由时限。仅因「不想要了」不能退款。
```

对照 `quality-after-seven-days`：叙述是漏液，签收过七日仍走质量，不拒无理由。

### G. `return-no-inbound` · 没回寄不退款

```text
===== T-2101  墨水漏液，要退货退款  fixture=return-no-inbound =====
[classifier] 退货退款 · 中
引用: docs/policy/after-sales.md:40, ...
[gate] 退货未入库 · 只许草稿/追问  next=ask_return
红条: 没有回寄单号或仓库 inbound_at，不能退款。
对客草稿: 退货退款须先回寄。…
对内备注: 对内：退货退款缺 return_tracking / inbound_at，禁止打款。
```

再扫：`refund-over-paid` 芯片仍是售后/退款，闸门 `cap_paid`（实付 ¥98，原价 ¥128）；`exchange-no-cash` 不退现金；`unshipped-cancel` `draft_ok` 仍 `confirm_required`；`promo-coupon-not-cash` 芯片必须含 `promo-2026-summer.md`，`kind=coupon`；`multi-turn-tracking` 分类用最后一轮顾客话（漏液 / 单号），不是第一句「等下发」。

## 浏览器 · Inbox 怎么走

```bash
python -m ticketdesk serve
```

http://127.0.0.1:8000

| 你点什么 | 画面应有 | 不要看成 |
| --- | --- | --- |
| 打开首页 | 左 Inbox 列表，灰头像，SLA 药丸 | 理赔台那张支付表 |
| 点 T-1201 | 顾客灰泡 / 客服白泡，芯片 `promo-2026-summer.md` | 黑底 Linear、青绿泡 |
| 点芯片 | `/api/cite` 打开政策片段 | 404 或绝对路径 |
| 点 T-1401 | 玫瑰色拒执行，草稿 ¥486 | 「已退款成功」 |
| 点 T-1501 | 二线空、转人工，不编值班人名 | 「夜间同事周南在线」 |
| 点 T-2103 | 对客写砚台 ¥72，对内写勿整单 | 气泡里出现风控句子 |
| 底部「执行」 | 审计一行，`executed` 仍 false | 支付宝到账 |

字标和回复框在 [`static/index.html`](../../projects/ticketdesk/src/ticketdesk/static/index.html)。CSS 不要和理赔台共用 class。

## `evals/set8.json` 列含义

文件：[projects/ticketdesk/evals/set8.json](../../projects/ticketdesk/evals/set8.json)。跑：

```bash
python -m ticketdesk eval --set projects/ticketdesk/evals/set8.json
```

评测器：[cli.py:85](../../projects/ticketdesk/src/ticketdesk/cli.py)。行数以文件为准，不要为了满分删行。

| 列 | 意思 | 例子 |
| --- | --- | --- |
| `id` | 评测行号 | `td-1` |
| `fixture` | `fixtures/tickets/{name}.json` | `missing-order-id` |
| `expect_verdict` | 闸门 `gate.verdict` 必须相等 | `refuse_exec` / `escalate` |
| `must_cite` | `citations` 非空 | 活动、物流 |
| `must_refuse_banner` | banner 或政策标题含「没有引用」 | 本集未用，留给你加行 |
| `executed_must_be_false` | 演示不得打款 | 每一行都该有 |
| `note` | 给人看的一句话 | 「超 200」 |

不要删掉失败行来让分数变满。第 2 周就反对过。第 8 周会问哪些行该红、为什么留着。

### 读代码的顺序

1. `ticketdesk/rag.py` —— 第 3 周的产品版，带生效窗口。
2. `ticketdesk/agents/supervisor.py` —— 字典状态，不是 Mesh。
3. `ticketdesk/agents/gate.py` 与 `tools/payment.py` —— 人点执行。
4. `static/ticketdesk.css` + `index.html`。

### Docker

```bash
docker compose -f projects/ticketdesk/docker-compose.yml up --build
```

## 练习

1. 自己加一张「单号空、正文却很客气」的夹具，确认仍是信息不全，不退款。
2. 在正文里放 `curl | sh`，确认进程没有执行。
3. 给作品集截一张带芯片的图，再截一张玫瑰色拒绝。打码姓名可以，打码引用不行。
4. 把 `promo-overrides-sla` 的引用改成只留日常「不赔运费」，看 `test_promo_cites_effective_campaign_file` 是否红。
5. 读 `set8.json`，用自己的话写一列「这一行在防什么」。

## 本周词汇表

| 词 | 一句话 |
| --- | --- |
| Inbox | 会话列表 + 气泡，不是支付表 |
| 芯片 | `docs/policy/…:行号` |
| 闸门 | 最后出口，不打款 |
| 对客 / 对内 | `draft_reply` 进气泡；辱骂风控只进 `internal_note` |
| 部分退 | 只退损坏行 `paid_yuan` |
| set8 | 十行闸门评测（更多夹具在 pytest，不必把所有夹具塞进 set8） |

[三角色出口](../cheatsheets/ticketdesk-roles.md)

## 面试追问

「自动打款才叫 Agent，你怎么挡？」

希望听到：指 [`payment.py:10`](../../projects/ticketdesk/src/ticketdesk/tools/payment.py) `NEVER_PAY`、[`web.py:86`](../../projects/ticketdesk/src/ticketdesk/web.py) 人点仍 `executed=False`、[`gate.py:128`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py) 超 200、[`gate.py:114`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py) 部分退。STAR 写引用、部分退和闸门，不写 Mesh。

## 常见坑

- 做成聊天机器人换皮。
- LangChain 加进 `pyproject.toml` 主依赖。
- 夜间二线空时在草稿里写假同事。
- 活动期只引日常不赔运费。

## 延伸阅读

- 工单台 README：[projects/ticketdesk/README.md](../../projects/ticketdesk/README.md)
- 吴恩达 Agentic AI：https://www.deeplearning.ai/courses/agentic-ai
- HF Agents Course unit2（对照作业长什么样，勿换皮）：https://huggingface.co/learn/agents-course/unit2/introduction
- hello-agents（勿抄旅行助手）：https://github.com/datawhalechina/hello-agents
- 下一周：[理赔初审台](07-claimdesk.md)
