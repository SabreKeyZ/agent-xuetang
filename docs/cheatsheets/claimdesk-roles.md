# 理赔三角色禁止项

主管顺序：质检 → 条款 → 核赔。[`supervisor.py`](../../projects/claimdesk/src/claimdesk/agents/supervisor.py) 第 29–59 行。

| 角色 | 允许写 | **禁止** |
| --- | --- | --- |
| 材料质检 | 缺件勾选 | 材料不齐还审结 |
| 条款员 | `条款 3.2 · path:line`（出险日版本） | 引用投保日 v1 给 8 月易碎案开绿灯 |
| 核赔员 | 通过 / 补件 / 拒赔 + 决定书草稿 | 调用成功 payout；无芯片还点「通过」 |

payout 探测永远 `confirm_required`。[`tools/payment.py`](../../projects/claimdesk/src/claimdesk/tools/payment.py) 的 `NEVER_PAYOUT`。
人点「执行打款」：[`web.py`](../../projects/claimdesk/src/claimdesk/web.py) 第 63–71 行，仍 `executed=False`。

`confirm=True` 写进核赔员也过不了 [`test_valid_low_recommend_pass_no_payout`](../../projects/claimdesk/tests/test_decision.py)（断言 `payout.status == confirm_required` 且 `executed is False`）。
