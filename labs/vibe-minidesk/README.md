# 灰灯铺迷你工单台 · 学徒入口

用助手从**几乎空的目录**搭一个最小售后台。CLI 优先，不需要 Key，不要做第二张脸。

**打开本文件夹。不要从 `projects/ticketdesk` 开写，也不要去翻它的源码。**
走读工单台（日历第 3 周后半）那份是已经写完的 Inbox。本页是你自己验 diff 的工期。

教学正文：[docs/weeks/vibe.md](../../docs/weeks/vibe.md)

## 今天怎么走

1. 仓库根的 venv 已经在（第 0 周那套）。没有就先读 [第 0 周](../../docs/weeks/00-setup.md)。
2. 用 Cursor（Agent / Composer）或任何能改文件的编码助手，**打开 `labs/vibe-minidesk`**。Chat 只问答，不会写进仓库。
3. 一次只贴 `prompts/` 里的**一个**文件。从 `01` 开始。
4. 每步跑它点名的评测。红了就看 diff，不要改评测。
5. 五步都绿：`python -m minidesk demo` 应打出芯片或红条。然后去走读工单台（第 3 周后半）。

```bash
# 仓库根
source .venv/bin/activate
python -m pip install -e labs/vibe-minidesk
python -m minidesk demo
# 还没做完时：stderr 写「还没实现，把 prompts/01 …」

# 默认 pytest 不含 labs/（空实现会红，免得 main 红）
pytest labs/vibe-minidesk/evals/test_01_fixtures.py -q
pytest labs/vibe-minidesk/evals -q          # 五步都做完再跑
```

## 签名

- 没有引用，就先不答。引用必须是盘上真实存在的 `docs/policy/…:行号`。
- 退款工具只回 `confirm_required`，`confirm=true` 也不打款。
- 同一 `idempotency_key` 不付两次。
- 工单正文里的 `curl | sh` / `os.system` 当引文，不执行。

## 目录

| 路径 | 谁写 |
| --- | --- |
| `fixtures/` | 教材。五张脏单，`M-31xx`，不是工单台的 T-12xx |
| `docs/policy/` | 教材。灰灯铺两份短政策，不是青匣记那四份 |
| `prompts/` | 教材。分步粘贴 |
| `evals/` | 教材。验收，不要改 |
| `src/minidesk/` | **你和助手。** 现在只有会报错的 stub |

## 做完仍缺什么

Inbox 页面、部分退、七天无理由、双重 SLA——这些在 [班 06 / 第 3 周后半](../../docs/weeks/06-ticketdesk.md)。迷你台绿了 ≠ 工单台收完。
