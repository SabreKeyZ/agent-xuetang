# 如何给 Agent学堂 提贡献

先谢谢你愿意改这份教材。这里不是百科全书，是一份学徒路线。
你改任何一段，都请先问自己：一个刚转行的同学，周五晚上能不能跟着做完？

## 我们欢迎什么

- 把某一步写得更短、命令更能复制。
- 补一张我们自己跑出来的截图（问学堂 / 值班台 / 本周脚本）。
- 给练习加一条会失败的反例，让验收标准更硬。
- 修死链、修 Windows / macOS / 国内镜像的坑。
- 给求职文档补真实岗位观察（注明日期和来源链接）。

## 我们不接受什么

- 从其他教程复制或改写正文。包括但不限于 Datawhale hello-agents、
  handy-multi-agent、Hugging Face Agents Course 课文、吴恩达课程逐字稿、
  各家公众号「万字拆解」。
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
python -m pip install -e "projects/askhall"
python -m pip install -e "projects/issueforge"
python -m pytest code projects/askhall/tests projects/issueforge/tests
```

问学堂和值班台的演示必须能在**没有 API Key** 时跑通（抽取式 / 夹具）。

```bash
python -m askhall demo
python -m issueforge demo
```

## 改一周教材时请对一下清单

每个 `docs/weeks/*.md` 需要有这些小标题：

1. 目标
2. 你将做出的东西
3. 预计 4–6 小时
4. 图文步骤
5. 对应视频
6. 练习
7. 验收标准
8. 常见坑
9. 延伸阅读

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
