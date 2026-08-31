# 02 · 抽取式条款检索，必须 path:line

上一张 `test_01_fixtures.py` 已经绿。还是只改 `labs/vibe-miniclaim`。不要打开 `projects/claimdesk`。不要申请 Key。不要做网页。

签名没变：**没有引用，就先不答。** 每一条建议都要带能跳转的 `docs/policy/文件.md:行号`。

## 要你做的

实现 `cite_policy(claim: dict) -> list[str]`：

- 语料只扫本实验的 `docs/policy/`（现在两份：`counter.md`、`autumn-cut-2026.md`）。
- 做法对齐班 03：按空行分块、记下起始行号、关键字打分。可以看 `code/week3/mini_rag.py` 的思路，**不要**抄 `projects/claimdesk/src/claimdesk/rag.py`。
- 每条命中格式必须是 `docs/policy/….md:行号`，行号必须落在该文件真实行数之内。不许编行号，不许写绝对路径。
- `autumn-pot` 这张案：投保在春册，**出险日**在 2026-07-01 及之后。叙述在要「按春册赔半」。引用里**必须出现** `autumn-cut-2026.md`，不得只引柜面「可赔半额」那句。
- 零命中就返回 `[]`，不要拿「常识」补一条条款。`mute-story` 的叙述对不上任何条款，应是空列表。

适用时点按 `incident_at`，不要读 `insured_at` 来选文件。

## DONE WHEN

```bash
pytest labs/vibe-miniclaim/evals/test_02_cite.py -q
```

全绿。`test_01` 必须仍绿。

## FORBIDDEN

- 假引用（文件不存在、行号越界、或去引理赔台的 `qingtu-bao-v1.md` / `qingtu-bao-v2.md`）
- 按投保日选用春册半额
- 自动打款
- 向量库、云端 embedding、Key
- 一次把闸门和 demo 全做了
