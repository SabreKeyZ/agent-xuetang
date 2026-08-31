# path:line 纸

引用必须能让编辑器跳转。格式：`相对路径:行号`。

| 谁打印 | 样子 | 从哪算根 |
| --- | --- | --- |
| 第 3 周 `mini_rag.py` | `docs/weeks/04-mcp-and-skills.md:1` | 仓库根 |
| 工单台芯片 | `docs/policy/promo-2026-summer.md:12` | `projects/ticketdesk` |
| 理赔台标签 | `条款 3.2 · docs/policy/qingtu-bao-v2.md:32` | `projects/claimdesk`（先剥 `条款 3.2 · `） |
| 分类员相似夹具 | `fixtures/tickets/promo-overrides-sla.json:1` | 工单台项目根 |

## 允许 / 拒绝

`ticketdesk.rag.read_snippet` 只允许 `docs/policy/` 或 `fixtures/`。带 `..` 或绝对路径直接拒。
`claimdesk.rag.read_snippet` 只允许 `docs/policy/`。

## 零命中

```text
$ python code/week3/mini_rag.py --query "MCP" --docs /tmp/empty-docs
{"hits": []}
```

退出码 1。工单台政策员、理赔台条款员在这一步亮红条：**没有引用，就先不答**。
