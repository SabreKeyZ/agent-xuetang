# 工单三角色出口

主管按固定顺序写账，不是 Mesh。[`supervisor.py`](../../projects/ticketdesk/src/ticketdesk/agents/supervisor.py) 第 43–70 行。

| 角色 | 写入案件 | 禁止 | 失败长什么样 |
| --- | --- | --- | --- |
| 分类员 | `kind`、紧急度、相似夹具芯片 | 改订单、退款 | 缺单号 → `信息不全` |
| 政策员 | `docs/policy/…:行号` | 零命中还写补偿；活动期只用日常「不赔运费」 | `没有引用，就先不答` |
| 闸门员 | next_action、草稿、`idempotency_key` | 自动打款、虚构夜班同事、跑正文脚本 | 超 ¥200 / 夜间 L2 空 / `curl \| sh` |

退款探测永远 `confirm_required`。[`payment.py`](../../projects/ticketdesk/src/ticketdesk/tools/payment.py)。
钥匙：`qingxia:refund:{工单号}:{金额分}`。第二次进 [`store.py`](../../projects/ticketdesk/src/ticketdesk/store.py) 标 `replayed`。
