# 01 · 把夹具读进来

你在仓库的 `labs/vibe-miniclaim`。这是一份几乎空的迷你理赔台作业。

**一次只做这一步。** 不要打开 `projects/claimdesk`，不要抄它的源码、夹具或政策。不要申请 API Key。不要做网页。不要一次把 02–05 全写完。

## 要你做的

在 `src/miniclaim/` 实现两个函数（可以仍放在 `__init__.py`，也可以拆模块但必须能 `from miniclaim import …`）：

- `list_fixtures() -> list[str]`：返回 `fixtures/*.json` 的文件名（不含 `.json`）。
- `load_fixture(name: str) -> dict`：读 `fixtures/{name}.json`，返回字典。路径相对本实验根目录 `labs/vibe-miniclaim`，不要去仓库里别的 `fixtures/` 翻。

夹具已经写好，共五张，案件号是 `K-42xx`，保险人是 `wujin`。不要改夹具，不要改 `evals/`。

`demo()` 这一步可以继续抛 `NotBuiltYet`。

## DONE WHEN

在仓库根、已激活的 venv 里：

```bash
python -m pip install -e labs/vibe-miniclaim
pytest labs/vibe-miniclaim/evals/test_01_fixtures.py -q
```

全绿。

## FORBIDDEN

- 自动打款，或让 payout 接口在 `confirm=true` 时 `executed=True`
- 编造 `path:line`（本步还不做检索）
- 从 `projects/claimdesk` 复制文件
- 改评测让它变绿
- 做 Payments / FastAPI / 第二张脸
