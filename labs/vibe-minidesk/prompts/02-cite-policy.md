# 02 · 抽取式政策检索，必须 path:line

上一张 `test_01_fixtures.py` 已经绿。还是只改 `labs/vibe-minidesk`。不要打开 `projects/ticketdesk`。不要申请 Key。不要做网页。

签名没变：**没有引用，就先不答。** 每一条建议都要带能跳转的 `docs/policy/文件.md:行号`。

## 要你做的

实现 `cite_policy(ticket: dict) -> list[str]`：

- 语料只扫本实验的 `docs/policy/`（现在两份：`front-desk.md`、`lantern-week-2026.md`）。
- 做法对齐第 3 周：按空行分块、记下起始行号、关键字打分。可以看 `code/week3/mini_rag.py` 的思路，**不要**抄 `projects/ticketdesk/src/ticketdesk/rag.py`。
- 每条命中格式必须是 `docs/policy/….md:行号`，行号必须落在该文件真实行数之内。不许编行号，不许写绝对路径。
- `lantern-stale` 这张单的 `now` 落在灯节窗口。正文在要补偿券。引用里**必须出现** `lantern-week-2026.md`，不得只引日常「不赔运费」。
- 零命中就返回 `[]`，不要拿「常识」补一条店规。

## DONE WHEN

```bash
pytest labs/vibe-minidesk/evals/test_02_cite.py -q
```

全绿。`test_01` 必须仍绿。

## FORBIDDEN

- 假引用（文件不存在、行号越界、或去引工单台的 `after-sales.md` / `promo-2026-summer.md`）
- 自动打款
- 对工单正文跑 shell
- 向量库、云端 embedding、Key
- 一次把闸门和 demo 全做了
