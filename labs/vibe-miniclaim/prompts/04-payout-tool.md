# 04 · 打款工具永远 confirm_required

`test_03_gate.py` 绿了再贴本页。不要打开 `projects/claimdesk`。不要申请 Key。不要做网页。

payout 接口可以长得像生产接口。演示必须停在人确认。同一把钥匙不得付两次。

## 要你做的

实现 `payout(amount_yuan: float, idempotency_key: str, confirm: bool = False) -> dict`：

- **无论** `confirm` 是 true 还是 false，都返回 `status="confirm_required"`，`executed=False`。不要写一条「真打款」分支。
- `ok` 不要是 `True`。
- 同一 `idempotency_key` 第二次调用：仍不打款，并设 `replayed=True`。钥匙格式约定 `wujin:payout:{案件号}:{金额分}`。
- 内存字典记住见过的钥匙即可，不必上数据库。

不要让闸门在 `confirm=True` 时绕过这个函数。

## DONE WHEN

```bash
pytest labs/vibe-miniclaim/evals/test_04_payout.py -q
```

全绿。01–03 仍绿。

## FORBIDDEN

- `confirm=True` 时 `executed=True` 或 `status="paid"`
- 同一把钥匙第二次再补一笔
- 假引用
- 接支付宝 / 微信真实接口
- 抄 `projects/claimdesk/.../payment.py`
