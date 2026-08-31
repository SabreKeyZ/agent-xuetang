# vibe 班参考提纲（日历第 3 周前半）

## 练习

1. 希望听到
- BAD 的 `executed=True` 违反 [`front-desk.md:24`](../../../labs/vibe-minidesk/docs/policy/front-desk.md)（超 200 只许草稿、闸门不打款、接口只回 `confirm_required`）。
- 也可以点名 [`front-desk.md:8`](../../../labs/vibe-minidesk/docs/policy/front-desk.md)「不得自动打款」。
2. 希望听到
- 红的是 `test_lantern_stale_cites_lantern_week_file`（或 05 里同款断言）。
- 只引 [`front-desk.md:20`](../../../labs/vibe-minidesk/docs/policy/front-desk.md)「不赔运费」是错引用；窗口内必须点名 `lantern-week-2026.md`。
- 这份 diff 要拒，不是改评测。
3. 希望听到
- 一次合成 02+03 常见砸法：做成聊天皮、编行号、或先写闸门却不读政策文件。
- 不是「更快」，是失败面糊在一起。
4. 希望听到
- Inbox / 部分退 / 七天无理由（或退货未入库、双重 SLA）里至少三件，并能指班 06 夹具名。
- 迷你台绿 ≠ 工单台收完。
5. 希望听到
- 面试一句原文：用助手从空目录搭过带引用和人确认闸门的工单台，并自己验过 diff。
- 20 秒补：拒过假引用或自动打款或 shell。

## 测验

<details>
<summary>1. 默认 pytest 为什么不含 labs/？</summary>

希望听到：stub 会红；main / CI 要保持绿。学徒自己跑 `pytest labs/vibe-minidesk/evals`。

</details>

<details>
<summary>2. `confirm=True` 应返回什么？</summary>

希望听到：仍然 `confirm_required`，`executed=False`。没有真打款分支。

</details>

<details>
<summary>3. 灯节单只引日常「不赔运费」算对吗？</summary>

希望听到：不对。必须点名 `docs/policy/lantern-week-2026.md` 的真实行号。

</details>
