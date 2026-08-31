# 05 · demo CLI：芯片或拒赔决定书

前面四张评测都绿了再贴本页。不要打开 `projects/claimdesk`。不要申请 Key。不要做网页。不要做 Payments 表。

## 要你做的

1. `process(claim: dict) -> dict`：`cite_policy` → `gate` → 调一次 `payout`（金额用 `amount_yuan`，钥匙 `wujin:payout:{id}:{分}`，`confirm=False`）。返回至少：

   - `citations`：真实 `path:line`
   - `gate`：闸门字典
   - `payment`：打款工具的返回（`status=confirm_required`，`executed=False`）
   - `executed`：永远 `False`

2. 改掉现在的 `demo(fixture: str | None = None) -> str`：

   - `fixture` 有值就只跑这一张；没有值就按夹具名跑完全部。
   - 打印（并返回同一段文字）：有引用就写 `引用: docs/policy/…:行号`；被拒就写 `红条: …` 或 `决定书: …`。
   - 秋切那张必须出现 `autumn-cut-2026.md`。超 ¥180、缺引用、补件、拒收未签收必须有 `红条:` 或 `决定书:`。
   - 不要出现「已打款」或 `executed=True`。

命令：

```bash
python -m miniclaim demo
python -m miniclaim demo --fixture autumn-pot
```

## DONE WHEN

```bash
pytest labs/vibe-miniclaim/evals -q
python -m miniclaim demo
```

评测全绿。终端里能指着芯片或拒赔决定书。然后合上本目录，去读 [班 07](../../../docs/weeks/07-claimdesk.md) / `projects/claimdesk` 的**走读**（不是把源码抄回来）。

## FORBIDDEN

- 自动打款
- 假引用
- FastAPI / 第二张脸 / 聊天机器人皮
- 为了绿而改 `evals/` 或改夹具
- 把理赔台源码搬进 `src/miniclaim`
