# Agent学堂 · From Zero to Hired

中文社区的 Agent 学徒路线：八周做出两个能部署的多智能体小产品，并准备一次说得清楚的求职谈话。
A Chinese-first apprenticeship — not another encyclopedia — from the first agent loop to a portfolio you can defend.

```
  +--------------------------------------------------+
  |  问学堂 AskHall          开源值班台 IssueForge    |
  |  用本仓库当教材的学伴      Issue 分流 / 复现 / 回复 |
  |                                                  |
  |   [你] --> think --> act --> observe --> [停]     |
  +--------------------------------------------------+
```

## 这是给谁的

默认读者是**有基础的小白**：会写一点 Python（函数、列表、`if`），用过 ChatGPT，或已经成功调用过一次 LLM API。
还不会 Python 的人先做 [Week -1](docs/ROADMAP.md)（venv / 函数 / 读报错）。那一周在 8 周日历**外面**。

- **转行**：听过 ChatGPT，但没写过「模型自己决定要不要调用工具」的循环。
- **在校**：课程里只有调用一次 API，想补一段能放进简历的作品。
- **后端想做 Agent**：你会写服务，但还不习惯把评测、日志、权限和多角色路由当成一等公民。

不默认你会深度学习，也不默认你有 GPU。
已经能独立用 LangGraph 上线过系统的人，这份路线会偏慢，去看文末延伸阅读即可。

## 默认日历：8 周 · 约 43 小时 · 大约两个月

不要先「自学三个月再来」。就按这张表走。
节奏：两个工作日晚上各 1.5 小时 + 一个周末块 2–3 小时。
做完是作品集，**不是**录用通知。完整说明见 [docs/ROADMAP.md](docs/ROADMAP.md)。

| 日历周 | 小时 | 教材 | 做完时手上有什么 |
| --- | --- | --- | --- |
| 1 | 3 | [0 环境](docs/weeks/00-setup.md) | `.env` 打通 DeepSeek / 智谱 / Ollama |
| 2 | 5 | [1 Agent 是循环](docs/weeks/01-what-is-an-agent.md) | `echo_agent.py` + JSON 日志 |
| 3 | 6 | [2 工具与 ReAct](docs/weeks/02-tools-and-react.md) | 手写 ReAct + 3 条评测 |
| 4 | 6 | [3 记忆与 RAG](docs/weeks/03-memory-rag.md) | 对本仓库 `docs/` 的引用 |
| 5 | 5 | [4 MCP 与 Skill](docs/weeks/04-mcp-and-skills.md) | 二十行 MCP + Skill |
| 6 | 6 | [5 多智能体](docs/weeks/05-multi-agent.md) + 开始 [6 问学堂](docs/weeks/06-askhall.md) | 问学堂 `demo` / `serve` |
| 7 | 6 | [7 值班台](docs/weeks/07-issueforge.md) | 夹具报告，可部署 |
| 8 | 5 | [8 上线与求职](docs/weeks/08-ship-and-job.md) | Docker、日志、十行评测、作品集、模拟面试 |

6 周压缩（合并 1+2、3+4，作品不变）写在 [docs/ROADMAP.md](docs/ROADMAP.md)，不是另一条主路。

视频课表（只放核对过的链接）：[docs/videos.md](docs/videos.md)。
默认日历详表：[docs/ROADMAP.md](docs/ROADMAP.md) · [docs/weeks/README.md](docs/weeks/README.md)。
怕踩坑：[docs/faq.md](docs/faq.md)。
求职三件套：[岗位](docs/jobs/roles.md) · [作品集](docs/jobs/portfolio.md) · [面试](docs/jobs/interview.md)。

## 两个毕业作品

### 问学堂 AskHall

本地多智能体学伴。知识库就是**本仓库的周文档**。

- `planner` 把问题拆成三步学习计划，并引用周文件。
- `tutor` 用仓库原文解释，必须带引用。
- `examiner` 出一道题并批改；空答案直接拒绝。
- 没有 API Key 时走抽取式：只检索、只引用，`python -m askhall demo` 仍然能跑。

[从 0 到 1 的说明](projects/askhall/README.md) · [第 6 周带练](docs/weeks/06-askhall.md)

### 开源值班台 IssueForge

GitHub Issue 值班桌。不是旅行机器人，也不模拟一个虚拟小镇。

- `triage` 标 bug / feature / question，并按标题猜重复。
- `repro` 从正文写复现清单，**不执行** Issue 里的代码。
- `scribe` 起草中英双语、口气克制的维护者回复。
- 默认读 `fixtures/`，不需要 Token。

[从 0 到 1 的说明](projects/issueforge/README.md) · [第 7 周带练](docs/weeks/07-issueforge.md)

## 国内模型（默认）

本仓库默认走 **OpenAI 兼容协议**，Key 填国内厂商即可。根目录 [`.env.example`](.env.example) 写了 DeepSeek / 智谱 / 通义 / Ollama 的 `OPENAI_BASE_URL`。

Week 1–4 和问学堂 v1 **不依赖** LangChain、LlamaIndex。
能用原始 Python 写清楚循环，再决定要不要上框架。

没有 GPU 也能学完。本地模型用 Ollama；云端用各家的小上下文聊天模型就够练习。

## 和现有教程有何不同

我们学过别人的**目录结构**，正文是自己写的。下面是定位，不是高下判决。

| | Agent学堂 | [hello-agents](https://github.com/datawhalechina/hello-agents) | [HF Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction) | [吴恩达 Agentic AI](https://www.deeplearning.ai/courses/agentic-ai) | LangGraph 实战仓 |
| --- | --- | --- | --- | --- | --- |
| 读者 | 中文小白 + 国内模型默认 | 中文系统教材，自研框架 | 英文课程，有测验与证书 | 英文短课，讲清四种模式 | 工程向示例 |
| 求职 | 一等公民（岗位 / 作品集 / 面试） | 不是主线 | 不是主线 | 没有 | 没有 |
| 视频课表 | 有核对 URL 的周表 | 以文字为主 | 课程自带视频 | 课程自带视频 | 社区实战视频 |
| 可部署作品 | 问学堂 + 值班台，带 Docker / 夹具 | 课程项目（旅行助手、赛博小镇等） | 单元作业 | Notebook 为主 | 框架示例 |
| 2026 的接口 | 第 4 周自己写 MCP，并写一段 Skill | 有 MCP 等进阶章 | 有工具与观测加分 | 工具使用是模式之一 | 视版本 |
| 评测与日志 | 第一个能跑的 loop 就打结构化日志 | 后续引入 | Observability 作加分 | 从第一周强调 eval | 生产向更重 |
| 默认供应商 | DeepSeek / 智谱 / 通义 / Ollama | 多供应商 | HF 与云厂商 | 偏国际云 | 偏 LangGraph 生态 |

我们**不会**再造一个 HelloAgents 式自研框架。
我们**不会**重做旅行助手或赛博小镇。

## 先跑起来（约 10 分钟）

```bash
git clone https://github.com/SabreKeyZ/agent-xuetang.git
cd agent-xuetang
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip pytest
python -m pip install -e projects/askhall -e projects/issueforge

# 没有 Key 也能看这两个演示
python -m askhall demo
python -m issueforge demo

# 浏览器里打开问学堂（仍可不填 Key）
python -m askhall serve
# http://127.0.0.1:8000
```

需要模型时：`cp .env.example .env`，按 [第 0 周](docs/weeks/00-setup.md) 填 Key。

## 如何贡献

请读 [CONTRIBUTING.md](CONTRIBUTING.md)。一句话：补坑、补图、补验收，不要搬别人的课文。

## 许可证

[MIT](LICENSE) © SabreKeyZ

## 致谢

我们读过这些课的**大纲和开场**，用来检查「该覆盖哪些主题」。
正文、练习、两个产品和面试题都是本仓库原创。把它们当作延伸阅读，不要和本仓库的段落对照着抄。

- 吴恩达 [Agentic AI](https://www.deeplearning.ai/courses/agentic-ai)（DeepLearning.AI）：Reflection / Tool Use / Planning / Multi-agent，以及「评测不要拖到最后」。
- [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction)：入门节奏、测验、每周 3–4 小时、观测加分。
- Datawhale [hello-agents](https://github.com/datawhalechina/hello-agents)、[Agent-Learning-Hub](https://github.com/datawhalechina/Agent-Learning-Hub)：从定义到手写 ReAct 再到框架的阶梯。
- [kevinten-ai/ai-agent-langgraph](https://github.com/kevinten-ai/ai-agent-langgraph)：观测、评测、Docker 的生产阶段。
- LangChain Academy [Intro to LangGraph](https://academy.langchain.com/courses/intro-to-langgraph)、[Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents)：MCP、Skill、人在回路、子 Agent、摘要记忆。
- Microsoft [MCP for Beginners](https://github.com/microsoft/mcp-for-beginners)：学习者自己写一个很小的 MCP 服务器。
- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)：把 Agent 看成循环 + 工具 + 权限的套件（我们不克隆其代码）。
- 李宏毅老师 2025 / 2026 学期公开课，链接见 [视频课表](docs/videos.md)。

CiteKit（可选的引用伙伴项目）：<https://github.com/SabreKeyZ/citekit>
