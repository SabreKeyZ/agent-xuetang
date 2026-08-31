# vibe-claim 班参考提纲（日历第 4 周最先）

## 练习

1. 希望听到
- BAD 的 `executed=True` 违反 [`counter.md:24`](../../../labs/vibe-miniclaim/docs/policy/counter.md)（超 180 只许草稿、闸门不打款、接口只回 `confirm_required`）。
- 也可以点名 [`counter.md:8`](../../../labs/vibe-miniclaim/docs/policy/counter.md)「不得自动打款」。
2. 希望听到
- 红的是 `test_autumn_pot_cites_autumn_cut_file`（或 05 里同款断言）。
- 只引 [`counter.md:30`](../../../labs/vibe-miniclaim/docs/policy/counter.md)「可赔半额」是错引用；出险日在秋切后必须点名 `autumn-cut-2026.md`。
- 这份 diff 要拒，不是改评测。
3. 希望听到
- 一次合成 02+03 常见砸法：做成聊天皮、编行号、或先写闸门却不读政策文件。
- 不是「更快」，是失败面糊在一起。
4. 希望听到
- Payments 表 / 免赔试算 / 补件复议状态机（或证据缩略图）里至少三件，并能指班 07 夹具名。
- 迷你台绿 ≠ 理赔台收完。
5. 希望听到
- 面试一句原文：用助手从空目录搭过带条款引用和人确认闸门的迷你理赔台，并自己验过 diff。
- 20 秒补：拒过假引用或自动打款或按投保日选条款。

## 测验

<details>
<summary>1. 默认 pytest 为什么不含 labs/？</summary>

希望听到：stub 会红；main / CI 要保持绿。学徒自己跑 `pytest labs/vibe-miniclaim/evals`。

</details>

<details>
<summary>2. `confirm=True` 应返回什么？</summary>

希望听到：仍然 `confirm_required`，`executed=False`。没有真打款分支。

</details>

<details>
<summary>3. 釉瓶案只引柜面「可赔半额」算对吗？</summary>

希望听到：不对。必须点名 `docs/policy/autumn-cut-2026.md` 的真实行号。适用出险日，不是投保日。

</details>
