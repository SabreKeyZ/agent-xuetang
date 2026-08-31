# Agent学堂 · From Zero to Hired

**没有引用，就先不答**

> **今天只打开这三个文件**
>
> 1. 本 README（先跑 30 分钟无 Key）
> 2. [docs/weeks/00-setup.md](docs/weeks/00-setup.md)（桌子）
> 3. [docs/weeks/README.md](docs/weeks/README.md)（工期目录）
> 4. （可选）[docs/walkthrough.md](docs/walkthrough.md)（跟学录屏）
>
> 看不懂「抽取式 / 队列」先跑通演示，第 1 周再解释循环。

教材就是仓库。两个毕业作品是队列，不是聊天皮。
A Chinese-first apprenticeship: one month (four calendar weeks), two ops desks, one conversation you can defend.

## 今天就跑通（约 30 分钟）

不需要 Key。你会看到引用芯片，或看到红条拒绝。

1. 克隆并进入仓库

```bash
git clone https://github.com/SabreKeyZ/agent-xuetang.git
cd agent-xuetang
```

2. 建虚拟环境，装两个毕业作品

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate
python -m pip install -U pip pytest
python -m pip install -e projects/ticketdesk -e projects/claimdesk
```

3. 跑两句演示。终端里应当出现芯片或红条：

```bash
python -m ticketdesk demo
# [ticketdesk] llm=off (extractive)
# 引用: docs/policy/promo-2026-summer.md:…
# 红条: 没有引用，就先不答  /  退款超 ¥200 · 只许草稿

python -m claimdesk demo
# [claimdesk] llm=off (extractive)
# 引用: 条款 3.2 · docs/policy/qingtu-bao-v2.md:…
# 红条: 没有引用，就先不答
```

4. 打开两张脸。8000 常被占用，工单台请显式指定 8010（FAQ 同条）：

```bash
python -m ticketdesk serve --port 8010
# http://127.0.0.1:8010
python -m claimdesk serve
# http://127.0.0.1:8001
```

两台都是抽取式，**不需要 Key**。第 0 周的 Key 只为可选的 `hello_chat.py`。没填也能学完夹具和引用芯片。需要模型时：`cp .env.example .env`，按 [第 0 周](docs/weeks/00-setup.md) 填国内 Key。

> 这不是就业保证。第一周能讲清循环和评测；一个月有两个可演示的队列。

## 两张脸：工单台 | 理赔台

左边是虚构店铺「青匣记」的售后队列，右边是虚构「青途保」的初审队列。同一条规矩：没有引用，就先不答。人点执行。演示不打款。

<table>
<tr>
<td width="50%" valign="top">

**工单台 · 青匣记 · Inbox**

![工单台：引用芯片与闸门](docs/images/ticketdesk-citations.png)

分类员 / 政策员 / 闸门员。浅色会话：顾客灰气泡、客服白气泡。芯片贴在气泡下：`docs/policy/promo-2026-summer.md`。退款接口只回 `confirm_required`。

![工单台：拒绝执行](docs/images/ticketdesk-refuse.png)

</td>
<td width="50%" valign="top">

**理赔台 · 青途保 · Payments**

![理赔台：支付表](docs/images/claimdesk-table.png)

材料质检 / 条款员 / 核赔员。支付表 + 巨型 ¥ + blurple。通过案（C-2009）贴条款芯片。易碎拒赔必须点名 `条款 3.2`。无命中亮红条。

![理赔台：通过案的条款芯片（C-2009）](docs/images/claimdesk-citations.png)

![理赔台：条款 3.2 除外拒赔](docs/images/claimdesk-refuse.png)

截图若仍印「建议赔付：¥40」，以当场 CLI 为准：拒赔决定书写「建议拒赔，不予赔付」。试算式可以留。

</td>
</tr>
</table>

[工单台说明](projects/ticketdesk/README.md) · [理赔台说明](projects/claimdesk/README.md)

## 学徒工期

默认给**有一点 Python 的小白**：**1 个月 / 4 周**，每周约 8–12 小时（工作日晚上 + 周末）。材料仍是原来的班文件 `00`–`08`、[vibe](docs/weeks/vibe.md) 和 [vibe-claim](docs/weeks/vibe-claim.md)，一篇不删，只是排得更密。做不完就停在当周验收，不要跳周。

**[只有 2 小时](docs/weeks/two-hour.md)** —— 先见面，不是这 1 个月路径。

| 做什么 | 然后 |
| --- | --- |
| 按 [120 分钟脚本](docs/weeks/two-hour.md) 走完：两台 demo → Inbox 三张单 → Payments 通过/拒赔 → 第 0 班失败对照 + 一条 FAQ | 按脚本走完再停。不申请 Key，不跳第 1 班。 |

**默认 1 个月（4 个日历周）**

| 月份第 1 周<br>~10h | 月份第 2 周<br>~10h | 月份第 3 周<br>~10h | 月份第 4 周<br>~10h |
| :---: | :---: | :---: | :---: |
| 环境 + Agent 循环 + 工具/ReAct | RAG + MCP + 多 Agent | vibe 迷你台 + 客服工单台 | vibe-claim + 理赔台 + 上线求职 |
| [00 环境](docs/weeks/00-setup.md) · [01 循环](docs/weeks/01-what-is-an-agent.md) · [02 ReAct](docs/weeks/02-tools-and-react.md) | [03 引用](docs/weeks/03-memory-rag.md) · [04 MCP](docs/weeks/04-mcp-and-skills.md) · [05 多角色](docs/weeks/05-multi-agent.md) | [vibe](docs/weeks/vibe.md) · [06 工单台](docs/weeks/06-ticketdesk.md) | [vibe-claim](docs/weeks/vibe-claim.md) · [07 理赔台](docs/weeks/07-claimdesk.md) · [08 上线](docs/weeks/08-ship-and-job.md) |
| 芯片或红条 · JSON 日志 · `--eval` 3 条 | `path:line` · 二十行 stdio · 何时不加角色 | 助手验 diff · 售后队列 | 助手验 diff · 初审队列 · 作品集谈话 |

```mermaid
flowchart LR
  W1["第 1 周<br/>00 01 02"] --> W2["第 2 周<br/>03 04 05"]
  W2 --> W3["第 3 周<br/>vibe 06"]
  W3 --> W4["第 4 周<br/>vibe-claim 07 08"]
```

> 敢慢跟：仍按 `00`–`08` 文件一周一篇。默认是上面这张 4 周表。

视频只放核对过的链接：[docs/videos.md](docs/videos.md)。踩坑：[docs/faq.md](docs/faq.md)。周目录：[docs/weeks/README.md](docs/weeks/README.md)。词表 / 一页纸：[docs/glossary.md](docs/glossary.md) · [docs/cheatsheet.md](docs/cheatsheet.md)。练习先做再看 [docs/weeks/answers](docs/weeks/answers)。

第 3 周前半是 [对着助手搭最小工单台](docs/weeks/vibe.md)，后半走读工单台。第 4 周最先是 [对着助手搭最小理赔台](docs/weeks/vibe-claim.md)，再走读理赔台，再收上线。不需要 Key，不要从 `projects/ticketdesk` / `projects/claimdesk` 开写。

转行、在校、后端转 Agent 都从第 0 班进。已经独立用过 LangGraph 上线的人，这份工期会偏慢，去文末结构参考即可。

## 两个工位怎么协作

工单台是**主管教练售后**：结构化工单进门，分类 → 政策 → 闸门。不做成五人互叫的网。

```mermaid
flowchart LR
  工单对象 --> 主管
  主管 --> 分类员
  主管 --> 政策员
  主管 --> 闸门员
  分类员 --> 订单查询
  政策员 --> 政策检索
  闸门员 --> 退款接口
  退款接口 -->|人点执行| 队列
```

理赔台是**初审流水**：材料质检 → 条款（出险日版本）→ 核赔建议。角色不回头互聊，payout 永不自动成功。

```mermaid
flowchart LR
  案件对象 --> 质检
  质检 --> 条款员
  条款员 --> 核赔员
  核赔员 --> 决定书
  核赔员 -->|confirm_required| 人
```

第 1–4 周的循环、工具、引用、MCP **不依赖** LangChain。能用原始 Python 写清楚，再决定要不要上框架。

## 国内模型

默认 OpenAI 兼容协议。根目录 [`.env.example`](.env.example) 写了 DeepSeek / 智谱 / 通义 / Ollama 的 `OPENAI_BASE_URL`。
没有 GPU 也能学完：笔记本发 JSON、写日志、跑测试。

## 和现有教程有何不同

定位，不是排名。我们吃自己的 `docs/`，作业是两个队列，不是旅行助手或问数大屏。

| | **Agent学堂（本仓）** | [hello-agents](https://github.com/datawhalechina/hello-agents) | [HF Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction) | [吴恩达 Agentic AI](https://www.deeplearning.ai/courses/agentic-ai) | [multi-agent-education](https://github.com/bcefghj/multi-agent-education) | [shopkeeper-agent](https://github.com/didilili/shopkeeper-agent) |
| --- | --- | --- | --- | --- | --- | --- |
| 给谁 | 1 个月中文小白学徒（4 日历周，材料仍是 00–08），国内 Key 可选 | 系统教材 + 自研框架 | 英文课 + 证书 | 英文短课，四种模式 | 面试包装项目，三语言 / Mesh | LangGraph 问数全栈 |
| 作业长什么样 | 工单台引用芯片 + 理赔台决定书 | 旅行助手、赛博小镇等 | 单元作业 | Notebook | 五人教育 Mesh、BKT/SM-2 | SQL / Qdrant / ES 流水线 |
| 求职 | [岗位/作品集/面试](docs/jobs/roles.md) 分册，首页不堆题库 | 不是主线 | 不是主线 | 没有 | 简历/STAR 写在首页 | 工程履历 |
| 评测 | 第 2 周三条 `--eval`；两台闸门夹具 | 后续引入 | 观测作加分 | 课内强调 eval | 常写量化数字 | 问数链路 |
| 默认供应商 | DeepSeek / 智谱 / 通义 / Ollama | 多供应商 | HF 与云 | 偏国际云 | 视实现 | 硅基流动等 |
| 2026 接口 | 第 4 周自己写 MCP + 一段 Skill | 有进阶章 | 工具加分 | 工具是模式之一 | 视实现 | LangGraph 节点 |

我们不造 HelloAgents 式框架，不重做旅行助手，不教 Qdrant/ES 问数，不提供三语言对照作业。

## 这套不覆盖什么

- 就业承诺、薪资数字、并发或「准确率百分之几」。
- 向量库、混合检索、NL2SQL、电商数仓。
- Java / Go 第二实现。
- 五人 Mesh、苏格拉底导师、BKT、SM-2。
- 生产权限、多租户、监控平台。

这些去别人的仓或进阶课。本仓先把循环、引用和两个队列做硬。

## 仓库怎么拆

```
agent-xuetang/
  docs/weeks/            班 00–08 + vibe + vibe-claim；默认按 1 个月 / 4 周排
  docs/jobs/             岗位 · 作品集 · 业务背景 · 面试（STAR 在作品 README）
  code/week0–5/          无框架小脚本；第 5 班是可选教室实验
  projects/ticketdesk/   青匣记工单台
  projects/claimdesk/    青途保理赔台
  labs/week5/            问学堂 / 值班台降级说明
  labs/vibe-minidesk/    日历第 3 周前半：助手搭最小工单台（评测自跑）
  labs/vibe-miniclaim/   日历第 4 周最先：助手搭最小理赔台（评测自跑）
```

## 求职材料

简历三条和 STAR 四行写在作品自己的 README，以及 [docs/jobs](docs/jobs/roles.md)。首页不贴题库。
[岗位地图](docs/jobs/roles.md) · [作品集](docs/jobs/portfolio.md) · [业务背景](docs/jobs/business.md) · [面试问法](docs/jobs/interview.md)

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
