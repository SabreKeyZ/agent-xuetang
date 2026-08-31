# 面试：业务背景（学徒口述）

面试官坐下说「先介绍这个项目的业务」时，打开这一页。
[先听五分钟](../../projects/ticketdesk/README.md#先听五分钟售后在干什么) 教店规；README 里的 STAR 四行教一次取舍；[场景题](interview.md) 教被追问怎么答。
这一页只教**开场**：店 / 保司是谁、谁来排队、钱从哪走、agent 卡在哪一段。

用学徒口吻。你走读过这两条队列、对着夹具跑过 demo，不是创始人，也不报 GMV、准确率、并发。
演示里钱停在 `confirm_required`，没有真实打款。

用法：先对着镜子念完 30 秒，再念 2 分钟。被追问翻「业务是谁」和文末三句。折页也在两台 README 的「面试：业务背景」。一页纸：[business-pitch](../cheatsheets/business-pitch.md)。

---

## 青匣记 · 客服工单台

产品：[projects/ticketdesk/README.md](../../projects/ticketdesk/README.md)。日历第 3 周后半走读。

### 30 秒口述（面试官刚坐下）

我走读的第一个队列，是虚构纸墨店「青匣记」的售后工单台。顾客进门不是来闲聊的，是来处理一笔已经成交的买卖：仅退款、退货退款、换货；大促期物流延误发券，不发现金。Agent 坐在工单里，做三件事——把单子分流、引用当天仍生效的政策、在闸门停手。退款接口形状像生产，必须人点执行；演示永远 `confirm_required`，不打款。

### 2 分钟口述（被要求展开）

青匣记卖纸墨。8 月盛夏大促，快递挤、轨迹停在揽收，顾客会拿着活动页来要现金。日常政策写「72 小时催件、不赔运费」；活动文件写「揽收起 48 小时可发不超过 12 块的补偿券」。店里的人一天对着 Inbox：核单号、对实付、看仓库有没有 `inbound_at`、写对客稿和对内备注。钱从订单优惠后实付走，券从活动补偿走，两笔不能混；已经退过的同一笔损失，不能再用活动券补一次。

三种退法不能混。货没出库走仅退款；货在顾客手里必须先回寄、仓库点过到了才能退钱；换货不退现金。七天无理由从签收日起算，「不想要了」过了七日不够；漏液、摔裂不受这七日限制。三件套只裂了砚台，只能退那一行实付，不能整单端走。

我把 agent 卡在三段：分类员打标——缺单号就是信息不全，不退款；政策员必须点名生效文件——活动期不能只用日常「不赔运费」；闸门员写草稿和 `next_action`。超 200、退货未入库、部分退要整单、夜间二线空，都停在人。我拒绝把它做成客服聊天机器人，也拒绝做成「AI 自动打款」。

### 业务是谁

**店。** 虚构店铺青匣记，`shop_id=qingxia`。他店订单查不到、不代退（夹具 `wrong-shop-order`）。

**谁来排队。** 已经下过单的顾客，渠道是在线客服工单，不是对话框闲聊。夹具里能指着说的：林小秋大促墨水轨迹停揽收（`promo-overrides-sla`）、三件套只裂砚台却要整单 198（`partial-refund-one-line`）、宋纸没单号就要先退 48（`missing-order-id`）、赵牧镇尺整单 486（`refund-over-200`）。

**人一天在干什么。** 客服开 Inbox：核 `QX-` 单号、查轨迹、对 `lines[].paid_yuan`、看回寄单号 / `inbound_at`、写灰/白气泡里的对客稿。辱骂、刷单、禁止打款的原因只进对内盒。夜间完结 SLA 超时且名册空（`fixtures/roster.json` 只有白班），只能转人工，不能编值班人。

**钱从哪走。** 货款退的是优惠后实付，不是吊牌价（`refund-over-paid`：原价 128、实付 98）。活动物流走补偿券，上限 12，不发现金（`promo-coupon-not-cash`）。换货不退现金。未发货取消是仅退款，仍须人点。钥匙 `qingxia:refund:{工单号}:{金额分}`，同一把不二次补偿。

**agent 卡在哪一段。** 分流 + 引用 + 闸门。不改订单、不跑工单正文里的脚本、不打款。主管按固定顺序写账，不是五人互叫。

### 为什么不是客服聊天机器人

聊天机器人吃一句闲聊，吐一段安慰。工单台吃结构化工单（单号、多 SKU 行、实付、messages、prior_actions），出的是标签、双 SLA、`path:line`、对客/对内两盒和闸门 verdict。没有引用就亮红条，不编「今晚必到」。

### 为什么不是「AI 自动打款」

[`tools/payment.py`](../../projects/ticketdesk/src/ticketdesk/tools/payment.py) 接口存在，形状像生产；`confirm=false` 且演示禁止 `confirm=true`。人点「执行」只写审计，[`web.py`](../../projects/ticketdesk/src/ticketdesk/web.py) 仍 `executed=False`。超 200 不得拆两笔 199。这是人在回路，不是支付系统。

### 真实脏数据与闸门（夹具名）

没有 GMV，没有队列吞吐。现场 Inbox 是夹具队列（约 25 条），评测是 `evals/set8.json` 十行。

| 夹具 | 店里发生了什么 | 闸门停在哪 |
| --- | --- | --- |
| `missing-order-id` | 没单号就要退 | `ask_order_id`，不打款 |
| `promo-overrides-sla` / `promo-coupon-not-cash` | 大促物流要现金 | 必须点名 `promo-2026-summer.md`，发券 |
| `partial-refund-one-line` | 三件只裂砚台，要整单 198 | `partial_line`，只建议砚台小样 ¥72 |
| `return-no-inbound` | 漏液要退货退款，没回寄 | `ask_return` |
| `seven-day-no-reason-late` | 签收过七日「不想要了」 | `deny_seven_day` |
| `quality-after-seven-days` | 过七日但是漏液 | 走质量，不拒无理由 |
| `refund-over-200` | 整单 486 | `refuse_exec`，不拆笔 |
| `refund-over-paid` | 按原价要，实付更少 | `cap_paid` |
| `already-refunded` | 已退还要 | `no_double_pay` |
| `p0-sla-night` | 夜间二线空 | `human_queue`，不编同事 |
| `shell-in-body` | 正文 `curl \| sh` | 当引文，不执行 |
| `exchange-no-cash` | 换货要现金 | 不退现金 |
| `unshipped-cancel` | 未发货取消 | 仅退款草稿，仍 `confirm_required` |
| `abuse-legal` / `fraud-burst-refunds` / `burst-*` | 辱骂、短时连退、10 分钟连发 | 升级 / 挂起，不自动赔 |

### 面试官常问的三句业务题

#### Q1. 店里一天最容易赔错的是哪一类？

希望听到：活动窗口引错文件，或实付 / 部分退算错行。不是「模型不够聪明」。

- 大促必须点名 [`promo-2026-summer.md`](../../projects/ticketdesk/docs/policy/promo-2026-summer.md)。检索按出票日滤生效：[`rag.py`](../../projects/ticketdesk/src/ticketdesk/rag.py) `_in_force`；物流延误 [`policy.py`](../../projects/ticketdesk/src/ticketdesk/agents/policy.py) `prefer_promo=True`。夹具 `promo-overrides-sla`。只引日常「不赔运费」是错引用。
- 多 SKU 只退损坏行：[`aftersales.py`](../../projects/ticketdesk/src/ticketdesk/aftersales.py) `broken_line`，闸门 [`gate.py`](../../projects/ticketdesk/src/ticketdesk/agents/gate.py) `partial_line`。夹具 `partial-refund-one-line`，对客只建议砚台 ¥72。

#### Q2. 钱从顾客口袋回到哪？agent 碰哪一段？

希望听到：货款退实付，活动走券，换货不现金。Agent 写草稿和 `idempotency_key`，探测退款接口，停在 `confirm_required`。

- 退款 / 发券：[`payment.py`](../../projects/ticketdesk/src/ticketdesk/tools/payment.py) `refund` / `coupon`。
- 人点仍不打：[`web.py`](../../projects/ticketdesk/src/ticketdesk/web.py) `executed=False`。
- 第二次同一钥匙：[`store.py`](../../projects/ticketdesk/src/ticketdesk/store.py) `replayed=True`。

#### Q3. 为什么售后台不是做客服机器人？

希望听到：进的是案件对象，出的是案件变更 + 审计。三种退法、入库、七日、对客/对内两盒，都是队列纪律。做成闲聊就丢了单号、实付和闸门。

- 分类失败面是打错标，政策失败面是没引用，闸门失败面是误打款。三者共用案件字典，见 [`supervisor.py`](../../projects/ticketdesk/src/ticketdesk/agents/supervisor.py)。
- README「我拒绝的设计」：不带业务皮的聊天机器人、不自动打款。

---

## 青途保 · 理赔初审台

产品：[projects/claimdesk/README.md](../../projects/claimdesk/README.md)。日历第 4 周中段走读。

### 30 秒口述（面试官刚坐下）

第二个队列是虚构「青途保」的运费险 / 小额意外险初审台。进门的是已经发生的损失：报案、补件、核赔。适用出险日条款版本，不用投保日印象。Agent 做材料质检、引用条款、写决定书草稿。建议不是打款；payout 必须人确认，演示 `NEVER_PAYOUT`。

### 2 分钟口述（被要求展开）

青途保不是聊天客服。投保人把运单、签收图、发票或门诊票据交进来，初审员一天对着支付表和卷宗：材料齐不齐、这张图是不是两案共用、出险那天用哪一版条款、免赔和店铺冲减怎么算。2026-07-01 条款从 v1 切到 v2：易碎从「可赔 50%」变成全部除外，索赔窗口从 7 日变成 15 日。5 月买的保单、8 月墨水瓶碎了，仍看 8 月那天的 v2，不能因为「我投保早」用旧版放行。

店铺已经退过货款，保险不能再拿同一笔损失全额赔——足额退就拒，部分退走差额。意外险每次先扣 50 再谈赔多少，式子要写进决定书。单纯延误、轨迹未签收却上传「签收图」，都不能装通过。

我把 agent 卡在三段：质检列缺件清单，材料不齐不审结；条款员按出险日检索，无命中亮红条「没有引用，就先不答」；核赔员只出通过 / 补件 / 拒赔 / 差额 / 复议。我拒绝把它做成「AI 理赔自动打款」，也拒绝做成工单台换皮的聊天气泡。

### 业务是谁

**保司。** 虚构青途保。两个产品：运费险（单次限额 80，免赔 0）、小额意外险（限额 500，免赔 50）。条款两本：[`qingtu-bao-v1.md`](../../projects/claimdesk/docs/policy/qingtu-bao-v1.md) 失效于 2026-06-30，[`qingtu-bao-v2.md`](../../projects/claimdesk/docs/policy/qingtu-bao-v2.md) 从 2026-07-01 起。

**谁来排队。** 投保人本人报案，渠道是 App 案件。代索赔、非投保人先过身份闸门（`wrong-claimant`）。夹具里能指着说的：易墨 5 月投保、8 月墨水瓶碎却要按 v1 赔 50%（`wrong-policy-version`）；店已退 128 还要再申保险 12（`shop-already-refunded`）；意外门诊 80、免赔 50（`accident-deductible`）。

**人一天在干什么。** 初审对着支付表：案件号、险种、试算 ¥、状态机、出险日。点进卷宗看缺件清单、条款芯片、决定书。核赔键在无芯片时是灰的。状态：已报案 → 立案 → 补件中 → 待核赔 → 待人打款 / 结案。

**钱从哪走。** 建议赔付 = `max(0, 申请 - 免赔 - 店铺冲减)`，且不超过保额。[`settle.py`](../../projects/claimdesk/src/claimdesk/settle.py)。运费险免赔 0；意外先扣 50。店铺已退冲减同一损失。式子写进决定书。打款接口存在，演示不打。

**agent 卡在哪一段。** 质检清单 + 出险日引用 + 核赔建议。不打款。主管按固定顺序写账，不是 Mesh。

### 为什么不是客服聊天机器人

画面是支付表 + 卷宗 + 巨型试算 ¥，不是灰/白气泡。决定书要条款号和计算式。没条款就拒审，不能「看起来像就赔」。工单台售后政策不得硬塞进理赔检索。

### 为什么不是「AI 理赔自动打款」

核赔员只出建议。[`tools/payment.py`](../../projects/claimdesk/src/claimdesk/tools/payment.py) 即使传入 `confirm=True`，演示仍因 `NEVER_PAYOUT` 回 `confirm_required`。人点「执行打款」，[`web.py`](../../projects/claimdesk/src/claimdesk/web.py) 仍 `executed=False`。`valid-low` 建议通过、钱不动——set8 的 `cd-7` 就是这条纪律，不要删行来凑满分。

### 真实脏数据与闸门（夹具名）

没有赔付额口号，没有准确率。现场是夹具队列（约 19 行）。

| 夹具 | 柜台上发生了什么 | 闸门停在哪 |
| --- | --- | --- |
| `wrong-policy-version` | 5 月投保、8 月墨水瓶碎，要按 v1 赔 50% | 引 v2 条款 3.2，拒赔 |
| `exclusion-fragile` | 易碎除外 | 条款 3.2 |
| `no-clause` | 叙述塞比特币 / FlipFlop | 红条拒审 |
| `missing-docs` | 缺运单 / 签收图 / 发票 | 补件，不审结 |
| `accident-deductible` | 意外门诊 80，免赔 50 | 试算 30，`executed=false` |
| `shop-already-refunded` | 店已退 128，再申保险 12 | 条款 5.1，冲减至 0，拒 |
| `shop-partial-offset` | 店退 8，申请 20 | 差额 12，仍不打款 |
| `shared-photo-a` / `shared-photo-b` | 两案同一张图 | 条款 5.2，升人工 |
| `over-window` | 逾期 | 拒 |
| `over-limit` | 超保额 | 拒或转人工 |
| `delay-only` | 单纯延误、货已完好 | 条款 3.3 除外 |
| `photo-signed-track-unsigned` | 照片称签收，轨迹在途 | 补件 |
| `unsigned-reject-proof` | 拒收证明代签收图 | 条款 3.4；通过建议仍不打款 |
| `appeal-after-deny` | 复议 | 引 8.1，不默示通过 |
| `wrong-claimant` | 非投保人 | 身份闸门 |

两台夹具对得上：`shop-already-refunded` 的 `prior_actions` 里有一把 `qingxia:refund:…` 钥匙——店退过的损失，保险不能再全额赔。

### 面试官常问的三句业务题

#### Q1. 为什么按出险日、不按投保日？

希望听到：条款改的是出险当天那本。v1 易碎可赔 50%、窗口 7 日；v2 易碎除外、窗口 15 日。投保日字段在夹具里，检索不读它。

- [`clause.py`](../../projects/claimdesk/src/claimdesk/agents/clause.py) `_expected_version`：`incident_at[:10] >= 2026-07-01` → v2；`retrieve(..., at=claim.incident_at)`。
- [`rag.py`](../../projects/claimdesk/src/claimdesk/rag.py) `_in_force` 用出险日滤生效/失效。
- 夹具 `wrong-policy-version`；测试 `test_incident_date_uses_v2_not_v1`。

#### Q2. 店铺已经退过，保险为什么还来排队？

希望听到：顾客会再申运费险。同一笔损失不能拿两份钱。足额退拒赔，部分退走差额。

- 条款 5.1 / 5.3。[`adjudicator.py`](../../projects/claimdesk/src/claimdesk/agents/adjudicator.py) 店铺已退 ≥ 申请 → 拒；小于申请 → 差额。
- `shop-already-refunded`（店退 128 ≥ 申请 12）；`shop-partial-offset`（店退 8、申请 20 → 建议 12）。
- 活动券也不能再补同一损失（工单台 `already-refunded` / 大促政策第 2 条）。

#### Q3. 为什么不是「AI 理赔自动打款」？

希望听到：初审写决定书，打款是另一段生产权限。建议通过也不等于钱出去了。

- 试算只出数字：[`settle.py`](../../projects/claimdesk/src/claimdesk/settle.py) `settle()`。
- 探测永不成功：[`payment.py`](../../projects/claimdesk/src/claimdesk/tools/payment.py) `NEVER_PAYOUT`。
- 人点仍 false：[`web.py`](../../projects/claimdesk/src/claimdesk/web.py)。`valid-low` / set8 `cd-7` 留下当回归。

---

## 两台对照（30 秒收口）

工单台是店里的售后 Inbox；理赔台是保司的初审支付表。都是队列，都是分流 + 引用 + 闸门，都不打款。店退过的损失，保险不能再全额赔——夹具上对得上，不是两套皮。

STAR 四行仍在各自 README。场景题从这一页讲完业务再翻 [interview.md](interview.md)。
