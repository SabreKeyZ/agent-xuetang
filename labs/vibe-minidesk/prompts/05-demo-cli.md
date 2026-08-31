# 05 · demo CLI：芯片或红条

前面四张评测都绿了再贴本页。不要打开 `projects/ticketdesk`。不要申请 Key。不要做网页。不要做 Inbox。

## 要你做的

1. `process(ticket: dict) -> dict`：`cite_policy` → `gate` → 调一次 `refund`（金额用 `refund_yuan`，钥匙 `huideng:refund:{id}:{分}`，`confirm=False`）。返回至少：

   - `citations`：真实 `path:line`
   - `gate`：闸门字典
   - `payment`：退款工具的返回（`status=confirm_required`，`executed=False`）
   - `executed`：永远 `False`

2. 改掉现在的 `demo(fixture: str | None = None) -> str`：

   - `fixture` 有值就只跑这一张；没有值就按夹具名跑完全部。
   - 打印（并返回同一段文字）：有引用就写 `引用: docs/policy/…:行号`；被拒就写 `红条: …`。
   - 灯节那张必须出现 `lantern-week-2026.md`。超 ¥200、缺单号必须有 `红条:`。
   - 不要出现「已打款」或 `executed=True`。

命令：

```bash
python -m minidesk demo
python -m minidesk demo --fixture lantern-stale
```

## DONE WHEN

```bash
pytest labs/vibe-minidesk/evals -q
python -m minidesk demo
```

评测全绿。终端里能指着芯片或红条。然后合上本目录，去读 [第 6 周](../../../docs/weeks/06-ticketdesk.md) / `projects/ticketdesk` 的**走读**（不是把源码抄回来）。

## FORBIDDEN

- 自动打款
- 假引用
- 对工单正文跑 shell
- FastAPI / 第二张脸 / 聊天机器人皮
- 为了绿而改 `evals/` 或改夹具
- 把工单台源码搬进 `src/minidesk`
