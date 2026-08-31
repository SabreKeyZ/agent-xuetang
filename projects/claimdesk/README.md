# 青途保 · 理赔初审台

虚构「青途保」运费险 / 小额意外险的初审队列。Agent 写案件状态，不触发打款。

**没有引用，就先不答。** 适用**出险日**条款版本，不用投保日印象。

## 从 0 到 1

**第 1 步 · 夹具**

```
projects/claimdesk/fixtures/claims/*.json
projects/claimdesk/docs/policy/qingtu-bao-v1.md
projects/claimdesk/docs/policy/qingtu-bao-v2.md
```

```bash
python -m pip install -e projects/claimdesk
python -m claimdesk demo
```

**第 2 步 · 条款检索**

`retrieve(..., at=incident_at)`。投保在 v1、出险在 v2 的易碎案，必须引用 v2 条款 3.2。

**第 3 步 · 决定书草稿**

核赔员只出 通过 / 补件 / 拒赔 / 差额 / 复议。状态机：已报案 → 立案 → 补件中 → 待核赔 → 待人打款 / 结案。缺件不审结。无条款命中亮红条。决定书必须带条款号和免赔试算。payout 接口 `confirm_required`。

**第 4 步 · Docker**

```bash
docker compose -f projects/claimdesk/docker-compose.yml up --build
```

http://127.0.0.1:8001

## 三个角色

| 角色 | 写入 | 禁止 |
| --- | --- | --- |
| 材料质检 | 缺件清单 | 材料不齐还审结 |
| 条款员 | `条款 3.2 · path:line` | 引用未生效版本 |
| 核赔员 | 建议 + 决定书草稿 | 调用成功打款 |

主管按固定顺序写账，不是五人 Mesh。

## 简历三条

- 理赔队列按出险日检索条款版本；无命中红条拒审。
- 免赔试算 `max(0, 申请 - 免赔 - 店铺冲减)`；店铺部分退走差额，足额退仍拒。payout 必须人确认。
- `python -m claimdesk demo` 无 Key 打印芯片或「没有引用，就先不答」。

## STAR

| | |
| --- | --- |
| 情境 | 5 月投保、8 月墨水瓶碎（v2 除外）；另一张意外门诊 ¥80，免赔 50。 |
| 任务 | 按出险日适用条款；决定书写出计算式；不能打款。 |
| 行动 | 条款检索带生效窗口；`settle()` 算建议赔付；核赔员只写建议。 |
| 结果 | `wrong-policy-version` 引 v2 拒赔；`accident-deductible` 试算 ¥30 且 `executed=false`。无准确率数字。 |

```bash
python -m pytest projects/claimdesk/tests -q
```
