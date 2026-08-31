# 03 · 三道闸门：缺引用 / 超 ¥200 / 正文里的命令

`test_02_cite.py` 绿了再贴本页。不要打开 `projects/ticketdesk`。不要申请 Key。不要做网页。

闸门是最后一个出口。它只许写草稿或红条，不许打款。

## 要你做的

实现 `gate(ticket: dict, citations: list[str]) -> dict`，按这个顺序判断（先命中先返回）：

1. `order_id` 空 → `verdict=refuse_exec`，`next=ask_order_id`，`banner` 里要有「单号」，`executed=False`
2. 正文含 `curl | sh` 或 `os.system` → `verdict=refuse_exec`，`next=cite_only`，`executed=False`。**只当引文，不要执行。** 源码里不许出现 `os.system(` 或 `import subprocess`
3. `citations` 为空 → `verdict=refuse_exec`，`banner` 含「没有引用」，`executed=False`
4. `refund_yuan > 200` → `verdict=refuse_exec`，`next=draft_only`，`banner` 含 `200`，`executed=False`
5. 其余 → `verdict=draft_ok`，`next=wait_human_confirm`，`executed=False`

返回字典至少含 `verdict` / `next` / `banner` / `executed`。

## DONE WHEN

```bash
pytest labs/vibe-minidesk/evals/test_03_gate.py -q
```

全绿。01、02 仍绿。

## FORBIDDEN

- 自动打款，或「超 200 拆成两笔 199」
- 对工单正文调用 shell（评测会把 `os.system` 打桩）
- 假引用
- 把闸门写成一段安慰顾客的聊天回复
- 抄 `projects/ticketdesk/.../gate.py`
