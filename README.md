# Agent学堂 · From Zero to Hired

**没有引用，就先不答**

教材就是仓库，Agent 只能引用这本教材。
A Chinese-first apprenticeship: eight weeks, two desks you can open, one conversation you can defend.

## 今天就跑通（约 30 分钟）

不需要 Key。你会看到引用芯片，或看到红条拒绝。

1. 克隆并进入仓库

```bash
git clone https://github.com/SabreKeyZ/agent-xuetang.git
cd agent-xuetang
```

2. 建虚拟环境，装两个毕业作品

```bash
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install -U pip pytest
python -m pip install -e projects/askhall -e projects/issueforge
```

3. 跑两句演示。终端里应当出现这些字：

```bash
python -m askhall demo
# [askhall] llm=off (extractive)
# [planner] 三步学习计划
# 引用: docs/weeks/02-tools-and-react.md:…
# （考试官拒绝了空答案）

python -m issueforge demo
# # Issue #12 值班报告
# - 夹具: bug-empty-docs
# [issueforge] html=demo-out/duty-report.html
```

4. 打开两张脸：浏览器 `python -m askhall serve` → http://127.0.0.1:8000 ；值班日志 `python -m issueforge board` 后打开 `demo-out/duty-report.html`。

需要模型时：`cp .env.example .env`，按 [第 0 周](docs/weeks/00-setup.md) 填国内 Key。没填也能学完抽取式和夹具。

> 这不是就业保证。两周能讲清循环和评测；八周有两个可演示仓库。

## 两张脸：学员桌 / 维护者桌

左边教人读教材，右边替开源仓库值一夜班。同一条规矩：没有引用，就先不答。

<table>
<tr>
<td width="50%" valign="top">

**问学堂 · 学员桌**

![问学堂：讲师给出 path:line 引用芯片](docs/images/askhall-tutor-citations.png)

规划员 / 讲师 / 考试官。芯片：`docs/weeks/03-memory-rag.md:5`。零命中亮红条。

![考试官拒改空答](docs/images/askhall-examiner-grade.png)

</td>
<td width="50%" valign="top">

**值班台 · 维护者桌**

![开源值班台：值班日志，正文摘句，命令先不跑](docs/images/issueforge-duty-log.png)

分流盖章、夹具芯片 `fixtures/bug-empty-docs.json`、正文摘句。`curl | sh` 只引用。

</td>
</tr>
</table>

[问学堂说明](projects/askhall/README.md) · [值班台说明](projects/issueforge/README.md)

## 学徒工期

默认给**有一点 Python 的小白**：一到两个月，每周 5–6 小时。做不完就停在当周验收，不要跳周。

**默认 8 周（含第 0 周摆桌子）**

| 0<br>5h | 1<br>5h | 2<br>6h | 3<br>5h | 4<br>5h | 5<br>5h | 6<br>6h | 7<br>6h | 8<br>5h |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| [环境](docs/weeks/00-setup.md) | [循环](docs/weeks/01-what-is-an-agent.md) | [ReAct](docs/weeks/02-tools-and-react.md) | [引用](docs/weeks/03-memory-rag.md) | [MCP](docs/weeks/04-mcp-and-skills.md) | [多角色](docs/weeks/05-multi-agent.md) | [问学堂](docs/weeks/06-askhall.md) | [值班台](docs/weeks/07-issueforge.md) | [上线](docs/weeks/08-ship-and-job.md) |
| 一次 chat | JSON 日志 | `--eval` 3 条 | `path:line` | 二十行 stdio | 何时不加角色 | 可演示教练 | 夹具值班 | 作品集谈话 |

**压缩 6 周**（合并 1+2、3+4；第 0 周并进第一格）

| 工期 1<br>8–10h | 工期 2<br>8–10h | 工期 3<br>5h | 工期 4<br>6h | 工期 5<br>6h | 工期 6<br>5h |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0 + 1 + 2 | 3 + 4 | 5 | 6 | 7 | 8 |
| 循环写完就能评测 | 检索引用 + 小 MCP | 主管分流 | 问学堂收口 | 值班日志 | 求职谈话 |

视频只放核对过的链接：[docs/videos.md](docs/videos.md)。踩坑：[docs/faq.md](docs/faq.md)。周目录：[docs/weeks/README.md](docs/weeks/README.md)。

转行、在校、后端转 Agent 都从第 0 周进。已经独立用过 LangGraph 上线的人，这份工期会偏慢，去文末结构参考即可。

## 两个工位怎么协作

问学堂是**主管教练**：一个入口，按关键字把话交给规划员、讲师或考试官。三者共用对本仓库的检索。不做成五人互叫的网。

```mermaid
flowchart LR
  学员 --> 主管
  主管 -->|计划| 规划员
  主管 -->|解释| 讲师
  主管 -->|考我| 考试官
  规划员 --> 检索
  讲师 --> 检索
  考试官 --> 检索
  检索 -->|path:line| 芯片
  检索 -->|零命中| 红条
```

值班台是**流水夜班**：夹具进门，分流盖章 → 摘正文写清单 → 执笔双语回复。角色不回头互聊。

```mermaid
flowchart LR
  夹具 --> 分流
  夹具 --> 复现
  分流 --> 执笔
  复现 --> 执笔
  执笔 --> HTML日志
```

第 1–4 周的循环、工具、引用、MCP **不依赖** LangChain。能用原始 Python 写清楚，再决定要不要上框架。

## 国内模型

默认 OpenAI 兼容协议。根目录 [`.env.example`](.env.example) 写了 DeepSeek / 智谱 / 通义 / Ollama 的 `OPENAI_BASE_URL`。
没有 GPU 也能学完：笔记本发 JSON、写日志、跑测试。

## 和现有教程有何不同

定位，不是排名。我们吃自己的 `docs/`，作业是两个工位，不是旅行助手或问数大屏。

| | **Agent学堂** | hello-agents | HF Agents Course | 吴恩达 Agentic AI | 某「面试包装」多 Agent 仓 | 某 LangGraph 问数全栈 |
| --- | --- | --- | --- | --- | --- | --- |
| 给谁 | 中文小白，国内 Key 默认 | 系统教材 + 自研框架 | 英文课 + 证书 | 英文短课，四种模式 | 简历项目，三语言/Mesh | 问数工程课 |
| 作业长什么样 | 问学堂引用芯片 + 值班日志 | 旅行助手、赛博小镇等 | 单元作业 | Notebook | 教育 Mesh 演示 | SQL / 检索流水线 |
| 求职 | [岗位/作品集/面试](docs/jobs/roles.md) 分册，首页不堆题库 | 不是主线 | 不是主线 | 没有 | 简历/STAR 写在首页 | 工程履历 |
| 评测 | 第 2 周三条 `--eval`；问学堂十行 | 后续引入 | 观测作加分 | 课内强调 eval | 常写量化数字 | 问数链路 |
| 默认供应商 | DeepSeek / 智谱 / 通义 / Ollama | 多供应商 | HF 与云 | 偏国际云 | 视实现 | 硅基流动等 |
| 2026 接口 | 第 4 周自己写 MCP + 一段 Skill | 有进阶章 | 工具加分 | 工具是模式之一 | 视实现 | LangGraph 节点 |

我们不造 HelloAgents 式框架，不重做旅行助手，不教 Qdrant/ES 问数，不提供三语言对照作业。

## 这套不覆盖什么

- 就业承诺、薪资数字、并发或「准确率百分之几」。
- 向量库、混合检索、NL2SQL、电商数仓。
- Java / Go 第二实现。
- 五人 Mesh、苏格拉底导师、BKT、SM-2。
- 生产权限、多租户、监控平台。

这些去别人的仓或进阶课。本仓先把循环、引用和两个工位做硬。

## 仓库怎么拆

```
agent-xuetang/
  docs/weeks/          工期 0–8
  docs/jobs/           岗位 · 作品集 · 面试（STAR 在这里）
  code/week0–4/        无框架小脚本
  projects/askhall/    问学堂
  projects/issueforge/ 值班台
```

## 求职材料

简历三条和 STAR 四行写在作品自己的 README，以及 [docs/jobs](docs/jobs/roles.md)。首页不贴题库。
[岗位地图](docs/jobs/roles.md) · [作品集](docs/jobs/portfolio.md) · [面试问法](docs/jobs/interview.md)

## 如何贡献

读 [CONTRIBUTING.md](CONTRIBUTING.md)。补坑、补图、补验收。不要搬别人的课文或别人的 README 骨架。

## 许可证

[MIT](LICENSE) © SabreKeyZ

## 结构参考（不是课文来源）

我们看过别人**怎么排版和带学**，用来检查密度：该有截图、该有工期、该有边界。正文、练习、两个工位和面试题是本仓库写的。

延伸阅读集中在 [docs/resources.md](docs/resources.md)。其中：

- 吴恩达 [Agentic AI](https://www.deeplearning.ai/courses/agentic-ai)
- [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction)
- Datawhale [hello-agents](https://github.com/datawhalechina/hello-agents)
- 结构密度参考（产品不同）：[multi-agent-education](https://github.com/bcefghj/multi-agent-education)、[shopkeeper-agent](https://github.com/didilili/shopkeeper-agent)

CiteKit（可选引用伙伴）：<https://github.com/SabreKeyZ/citekit>
