# 雾津保迷你理赔台 · 学徒入口

用助手从**几乎空的目录**搭一个最小初审台。CLI 优先，不需要 Key，不要做第二张脸。

**打开本文件夹。不要从 `projects/claimdesk` 开写，也不要去翻它的源码。**
日历第 4 周中段那份是已经写完的 Payments 走读。本页是你自己验 diff 的工期。

教学正文：[docs/weeks/vibe-claim.md](../../docs/weeks/vibe-claim.md)

## 今天怎么走

1. 仓库根的 venv 已经在（第 0 班那套）。没有就先读 [第 0 班](../../docs/weeks/00-setup.md)。
2. 用 Cursor（Agent / Composer）或任何能改文件的编码助手，**打开 `labs/vibe-miniclaim`**。Chat 只问答，不会写进仓库。
3. 一次只贴 `prompts/` 里的**一个**文件。从 `01` 开始。
4. 每步跑它点名的评测。红了就看 diff，不要改评测。
5. 五步都绿：`python -m miniclaim demo` 应打出芯片或拒赔决定书。然后去班 07。

```bash
# 仓库根
source .venv/bin/activate
python -m pip install -e labs/vibe-miniclaim
python -m miniclaim demo
# 还没做完时：stderr 写「还没实现，把 prompts/01 …」

# 默认 pytest 不含 labs/（空实现会红，免得 main 红）
pytest labs/vibe-miniclaim/evals/test_01_fixtures.py -q
pytest labs/vibe-miniclaim/evals -q          # 五步都做完再跑
```

## 签名

- 没有引用，就先不答。引用必须是盘上真实存在的 `docs/policy/…:行号`。
- 打款工具只回 `confirm_required`，`confirm=true` 也不打款。
- 同一 `idempotency_key` 不付两次。
- 出险日落在秋切窗口的釉瓶，必须点名秋切文件，不得只用春册「可赔半额」。

## 目录

| 路径 | 谁写 |
| --- | --- |
| `fixtures/` | 教材。五张脏案，`K-42xx`，不是理赔台的 C-20xx |
| `docs/policy/` | 教材。雾津保两份短条款，不是青途保那两份 |
| `prompts/` | 教材。分步粘贴 |
| `evals/` | 教材。验收，不要改 |
| `src/miniclaim/` | **你和助手。** 现在只有会报错的 stub |

## 做完仍缺什么

Payments 表、免赔额试算细节、补件/复议状态机、证据缩略图——这些在 [班 07](../../docs/weeks/07-claimdesk.md)。迷你台绿了 ≠ 理赔台收完。
