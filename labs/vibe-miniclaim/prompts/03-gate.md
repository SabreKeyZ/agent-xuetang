# 03 · 四道闸门：缺引用 / 补件 / 超限额 / 拒收未签收

`test_02_cite.py` 绿了再贴本页。不要打开 `projects/claimdesk`。不要申请 Key。不要做网页。

闸门是最后一个出口。它只许写草稿、补件清单或红条，不许打款。

## 要你做的

实现 `gate(claim: dict, citations: list[str]) -> dict`，按这个顺序判断（先命中先返回）：

1. `citations` 为空 → `verdict=refuse_exec`，`next=refuse`，`banner` 含「没有引用」，`executed=False`
2. 叙述含「拒收」或「未签收」，且附件 `kind` 里没有「拒收证明」→ `verdict=refuse_exec`，`next=ask_docs`，`banner` 含「未签收」或「拒收」，`executed=False`
3. 附件 `kind` 里没有「物流签收图」→ `verdict=refuse_exec`，`next=ask_docs`，`banner` 含「补件」，`executed=False`
4. `amount_yuan > 180` → `verdict=refuse_exec`，`next=draft_only`，`banner` 含 `180`，`executed=False`
5. 其余 → `verdict=draft_ok`，`next=wait_human_confirm`，`executed=False`

返回字典至少含 `verdict` / `next` / `banner` / `executed`。

材料看 `attachments` 里的 `kind`，不要猜照片内容。缺件只出清单，不审结。

## DONE WHEN

```bash
pytest labs/vibe-miniclaim/evals/test_03_gate.py -q
```

全绿。01、02 仍绿。

## FORBIDDEN

- 自动打款，或「超 180 拆成两笔 90」
- 假引用
- 把闸门写成一段安慰投保人的聊天回复
- 抄 `projects/claimdesk/.../adjudicator.py` 或状态机
