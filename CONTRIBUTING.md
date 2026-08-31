# 如何给 Agent学堂 提贡献

先谢谢你愿意改这份教材。这里不是百科全书，是一份学徒路线。
你改任何一段，都请先问自己：一个刚转行的同学，周五晚上能不能跟着做完？

## 我们欢迎什么

- 把某一步写得更短、命令更能复制。
- 补一张我们自己跑出来的截图（工单台 / 理赔台 / 本周脚本）。
- 给练习加一条会失败的反例，让验收标准更硬。
- 修死链、修 Windows / macOS / 国内镜像的坑。
- 给求职文档补真实岗位观察（注明日期和来源链接）。

## 我们不接受什么

- 从其他教程复制或改写正文。包括但不限于 Datawhale hello-agents、
  handy-multi-agent、Hugging Face Agents Course 课文、吴恩达课程逐字稿、
  各家公众号「万字拆解」。也不要整段搬 multi-agent-education 或
  shopkeeper-agent 的 README 骨架、口号或表格。结构参考见 `docs/resources.md`。
- 发明 Bilibili BV 号或「官方」链接。视频只进 `docs/videos.md`，且必须是
  仓库已经核对过的地址，或该课程的官方站点。
- 盗版 PDF、网盘课件、付费课录音。
- 旅行助手、赛博小镇、或任何一眼能看出来源的作业换皮。
- 「学完月薪三万」这类句子。求职部分必须诚实。

别人的课可以放在「延伸阅读」，给链接，用一两句说明它适合什么时候去看。
不要把别人的章节结构整段搬过来。

## 本地怎么跑

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -U pip
python -m pip install pytest
python -m pip install -e "projects/ticketdesk"
python -m pip install -e "projects/claimdesk"
python -m pytest code projects/ticketdesk/tests projects/claimdesk/tests
```

工单台和理赔台的演示必须能在**没有 API Key** 时跑通（抽取式 / 夹具）。

```bash
python -m ticketdesk demo
python -m claimdesk demo
```

## 改一周教材时请对一下清单

每个 `docs/weeks/*.md` 需要有这些小标题（学徒包，不是博客）：

1. 本周你要带走什么（可勾验收）
2. 先修 / 预计时间 / 对应视频（视频只认 `docs/videos.md` 或新核对过的官方页）
3. 概念：定义 + **一个反例**
4. 对着本仓库代码的逐步带练：命令、期望 stdout、失败对照
5. mermaid 或 ASCII 图
6. 练习题 3–5 道；参考答案只放 `docs/weeks/answers/`，正文不剧透
7. 本周词汇表
8. 面试追问 1 条，答案要点指向本仓代码 path:line
9. 延伸阅读：给链接，不搬别人课文

对着一个害怕的同事说话。短句。能画图就画 mermaid。
命令单独成块，让人可以整段复制。

## 提交方式

1. Fork，或在本仓库开分支。
2. 一个 PR 只做一件事：一周文档、一个项目、或一组测试。
3. PR 描述里写：你改了哪条验收标准、你本地跑了哪条命令。
4. 新代码默认离线可测。需要网络的测试请标 `@pytest.mark.network`。

## 行为约定

提问时请附：操作系统、Python 版本、你执行的命令、完整报错。
讨论可以直率，不要嘲讽「这么简单都不会」。这份仓库就是为这个「不会」写的。
