# 视频课表

这里只放**已经核对过的地址**。没有 BV 号的不要自己编。
社区搬运一律标成「中文搬运」，正式学习请以官方页为准。

每周文档里的「对应视频」都链回本表。看不完不要自责：先做当周练习，视频当背景音补。

## 怎么用这张表

1. 官方课优先。需要中文口播时，再用 B 站搬运，并意识到字幕可能过时。
2. 「实战向」用来看别人怎么点按钮、怎么拆图，不要停下来抄他们的仓库。
3. Datawhale 的文字教程放在最后一节，当作延伸阅读，不当作本仓库的正文来源。

| 标签 | 含义 |
| --- | --- |
| 官方 | 课程主办方或老师个人主页 / 官方平台 |
| 中文搬运 | 第三方上传的中文口播或字幕，非正式教材 |
| 实战向 | 偏操作、偏项目演示，用来建立手感 |

## 第 0–1 周 · 先建立直觉

| 标签 | 内容 | 链接 |
| --- | --- | --- |
| 官方 | 李宏毅 ML 2025 Spring 课程主页 | https://speech.ee.ntu.edu.tw/~hylee/ml/2025-spring.php |
| 中文搬运 | 李宏毅 2025 春 B 站合集 | https://www.bilibili.com/video/BV1aiADewEBC/ |
| 官方 | 吴恩达 Agentic AI 课程页 | https://www.deeplearning.ai/courses/agentic-ai |
| 中文搬运 | 吴恩达 Agentic AI 中文搬运 | https://www.bilibili.com/video/BV11Y49zCEuk/ |
| 中文搬运 | 同上 · 模块1-3 自主性（第 1 周） | https://www.bilibili.com/video/BV11Y49zCEuk/?p=3 |
| 官方 | Hugging Face Agents Course 导论 | https://huggingface.co/learn/agents-course/unit0/introduction |

第 0 周不必看完李宏毅整学期。用主页找「今天这一讲的标题」，确认自己没走丢即可。
合集共 31 分 P。模块1-3 自主性是第 3 分 P（`?p=3`），给第 1 周对自主谱，不是给第 0 周装环境。不要用 `?t=` 当分集。

## 第 2 周 · 工具、作业里的 Agent

| 标签 | 内容 | 链接 |
| --- | --- | --- |
| 实战向 | 李宏毅 HW2 Agent（YouTube，林毓翔 / Ulin Sanga，非官方课） | https://youtu.be/o4AT86nLcd0 |
| 官方 | 吴恩达 Agentic AI（Tool Use / 评测相关周） | https://www.deeplearning.ai/courses/agentic-ai |
| 中文搬运 | 同上，B 站搬运 | https://www.bilibili.com/video/BV11Y49zCEuk/ |
| 中文搬运 | 模块3 工具（第 2 周） | https://www.bilibili.com/video/BV11Y49zCEuk/?p=14 |
| 中文搬运 | 模块4-1 evals（第 2 / 8 周） | https://www.bilibili.com/video/BV11Y49zCEuk/?p=19 |

先自己写出 `code/week2` 的循环，再去看老师怎么布置作业。顺序反了容易变成「我看懂了但写不出来」。
分 P 只标核对过的：工具 `?p=14`，evals `?p=19`。合集用 `?p=` 不分集，不要改回 `?t=`。

## 第 3 周 · RAG 与上下文

| 标签 | 内容 | 链接 |
| --- | --- | --- |
| 实战向 | 李宏毅 HW1 RAG（YouTube，林毓翔 / Ulin Sanga，非官方课） | https://youtu.be/0ylc6rnoTOM |
| 中文搬运 | 李宏毅 2026 Agent / Context / Multi-Agent | https://www.bilibili.com/video/BV1Sdw7zREka/ |
| 官方 | 李宏毅 2025 春主页（对照当周讲义） | https://speech.ee.ntu.edu.tw/~hylee/ml/2025-spring.php |

本仓库第 3 周的检索器是关键字 + 分块，不是向量数据库课。看 HW1 是为了听清「引用从哪来」，不是为了重写一份作业。

## 第 4 周 · MCP 与更厚的套件

| 标签 | 内容 | 链接 |
| --- | --- | --- |
| 官方 | Microsoft MCP for Beginners | https://github.com/microsoft/mcp-for-beginners |
| 官方 | LangChain Academy Deep Agents | https://academy.langchain.com/courses/foundation-introduction-to-deepagents |
| 官方 | Hugging Face Agents Course | https://huggingface.co/learn/agents-course/unit0/introduction |
| 中文搬运 | 吴恩达搬运 · 模块3 MCP（第 4 周） | https://www.bilibili.com/video/BV11Y49zCEuk/?p=18 |

MCP 官方仓库是给「自己写一个小服务器」用的。看完请回到 `code/week4`，用本仓库的 `get_week_goal` 交差，不要把微软示例整仓粘过来。
模块3 MCP 是第 18 分 P（`?p=18`）。听完名字就回来写二十行服务器。

## 第 5–7 周 · 多角色与框架课

| 标签 | 内容 | 链接 |
| --- | --- | --- |
| 官方 | LangChain Academy Intro to LangGraph | https://academy.langchain.com/courses/intro-to-langgraph |
| 官方 | LangChain Academy Deep Agents | https://academy.langchain.com/courses/foundation-introduction-to-deepagents |
| 中文搬运 | 李宏毅 2026 Agent / Context / Multi-Agent | https://www.bilibili.com/video/BV1Sdw7zREka/ |
| 实战向 | LangGraph 多智能体实战（B 站） | https://www.bilibili.com/video/BV13roYBXELs/ |
| 实战向 | LangGraph 入门到实战（B 站） | https://www.bilibili.com/video/BV1EGc7zwEkR/ |

工单台和理赔台的 v1 **不要求** LangGraph。第 5 周先用字典状态机把路由讲清楚。
想对照框架课，放到第 6 周晚上当加餐。

## 第 8 周 · 收尾时回看

| 标签 | 内容 | 链接 |
| --- | --- | --- |
| 官方 | 吴恩达 Agentic AI（评测与上线相关讨论） | https://www.deeplearning.ai/courses/agentic-ai |
| 官方 | Hugging Face Agents Course（观测加分单元 bonus-unit2） | https://huggingface.co/learn/agents-course/bonus-unit2/introduction |
| 中文搬运 | 模块4-1 evals（和第 2 周同一分 P） | https://www.bilibili.com/video/BV11Y49zCEuk/?p=19 |
| 中文搬运 | 模块4-6 延迟成本（第 8 周） | https://www.bilibili.com/video/BV11Y49zCEuk/?p=24 |

求职材料以本仓库 `docs/jobs/` 为准。视频用来复习「你会怎么评一个 Agent」，不是背名词。
模块4-6 延迟成本是第 24 分 P（`?p=24`）。对照本仓抽取式 demo 的墙钟，不要抄别人的准确率。

## 延伸阅读（文字课，不是本表的视频）

- Datawhale Agent-Learning-Hub：https://github.com/datawhalechina/Agent-Learning-Hub
- Datawhale hello-agents：https://github.com/datawhalechina/hello-agents

它们覆盖面更像一本教材。本仓库覆盖面更像一间工作室。两者可以并存，请不要把那边的章节粘进这边的 PR。
