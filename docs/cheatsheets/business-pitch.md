# 业务开场一页纸

面试官说「先介绍业务」时用。[全文](../jobs/business.md)。STAR 仍在两台 README。不要报 GMV / 准确率 / 并发。

## 青匣记 · 30 秒

虚构纸墨店售后队列。进门是已成交的买卖：仅退款 / 退货退款 / 换货；大促物流发券不发现金。Agent 分流 + 引用生效政策 + 闸门停手。退款接口在，人点执行；演示 `confirm_required`，不打款。

**我拒绝把 agent 做成**客服聊天机器人，也拒绝做成「AI 自动打款」。

夹具能开口：`promo-overrides-sla`（必须点名 `promo-2026-summer.md`）· `partial-refund-one-line`（只退砚台 ¥72）· `return-no-inbound` · `seven-day-no-reason-late` · `refund-over-200`。

钱：货款走实付，活动走券，换货不现金。钥匙 `qingxia:refund:{id}:{分}`。

## 青途保 · 30 秒

虚构运费险 / 小额意外险初审队列。进门是已发生的损失：报案 → 补件 → 核赔。按**出险日**条款，不用投保日印象。Agent 质检 + 引用 + 决定书。建议不是打款；演示 `NEVER_PAYOUT`。

**我拒绝把 agent 做成**客服聊天机器人，也拒绝做成「AI 理赔自动打款」。

夹具能开口：`wrong-policy-version`（5 月投保、8 月墨水瓶，引 v2 拒）· `accident-deductible`（80−50=30）· `shop-already-refunded` / `shop-partial-offset` · `no-clause`。

钱：`max(0, 申请 - 免赔 - 店铺冲减)`。运费免赔 0，意外 50。店已退不能再全额赔。

## 被追问先指哪

| 问 | 指 |
| --- | --- |
| 活动为什么发券 | `policy.py` `prefer_promo` · `rag.py` `_in_force` |
| 三件为什么不能整单退 | `aftersales.py` `broken_line` · `gate.py` `partial_line` |
| 出险日还是投保日 | `clause.py` `_expected_version` · `retrieve(..., at=incident_at)` |
| 人点了为什么还没打款 | 两台 `tools/payment.py` · `web.py` `executed=False` |
