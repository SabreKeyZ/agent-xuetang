# 第 5 周 · 多个角色，以及何时不要加角色

到第 4 周，你已经有一个循环、两只手、一份长记忆、一个对外的小服务器。
有人会说：下一步当然是「上多智能体」。

先泼冷水。多一个角色，就是多一次完整的提示、多一轮等待、多一个会说错话的出口。
本周的上半场用来建立三种结构；下半场才打开问学堂的空壳。

## 目标

- 分清主管（supervisor）、交接（handoff）、辩论（debate）。
- 能用费用和延迟解释「为什么两个角色够了」。
- 给问学堂选定三个角色和一条路由规则。
- 仍然用字典状态机，不强制 LangGraph。

## 你将做出的东西

- 一张你自己画的路由图（可以画在纸上，拍照留着写第 8 周作品集）。
- 问学堂仓库里跑通 `python -m askhall demo` 的抽取式路径（完整产品在第 6 周收完）。

## 预计 4–6 小时

读三种结构 2 小时；算一笔「多一次交接」的账 1 小时；clone 后跑问学堂 demo 1 小时；看一节多 Agent 视频 1–2 小时。

## 图文步骤

### 主管

一个角色只做分流，不做长篇讲解。

```mermaid
flowchart TB
  U[用户] --> S[Supervisor]
  S -->|计划| P[Planner]
  S -->|讲解| T[Tutor]
  S -->|出题| E[Examiner]
```

优点：入口唯一，日志好读。
缺点：主管自己也会分错。分错的修复是改路由规则或加评测，不是再加一个「超级主管」。

### 交接

A 做完把整包状态交给 B，A 不再说话。像工单流转。

```mermaid
flowchart LR
  T[Triage] --> R[Repro] --> S[Scribe]
```

值班台更接近这种。分流的结论是给后面用的标签，不是给用户看的散文。

### 辩论

两个角色互相挑错，第三个角色（或规则）投票。

适合：高风险、值得付双倍延迟的判断（要不要合并一条会删库的指令）。
不适合：解释「什么是短记忆」。那会变成两个人抢话筒。

### 费用和延迟（请写在笔记里）

假设一次模型调用 2 秒、0.01 元：

| 结构 | 最少调用次数 | 大概等待 | 大概钱 |
| --- | --- | --- | --- |
| 单循环 + 检索 | 1 | 2s | 0.01 |
| 主管 + 一个专家 | 2 | 4s | 0.02 |
| 主管 + 三专家串行 | 4 | 8s | 0.04 |
| 两专家辩论 + 裁判 | 3+ | 6s+ | 0.03+ |

数字是示意。你用自己的账单页替换。
结论应当是句子，不是口号：**先问「一个循环是不是做不完」，再问「第二个角色负责哪一种失败」。**

### 问学堂为什么是三个角色

| 角色 | 只做 | 不做 |
| --- | --- | --- |
| planner | 把问题变成三步，并引用周文件 | 不写作文式讲解 |
| tutor | 用教材原文解释 | 不编造教材里没有的周数 |
| examiner | 出一题、批改；空答拒绝 | 不顺便把下周内容剧透完 |

第四个「鼓励师」不在 v1。语气用模板，比再付一次调用便宜。

### 开始搭

```bash
python -m pip install -e projects/askhall
python -m askhall demo
```

demo 在没有 Key 时也必须打印：路由结果、至少一条 `path:line`、考试官的拒绝或题目。
如果你看到空输出，停下来开 Issue，不要自己先「加一个总结 Agent」把空包起来。

第 6 周会把 FastAPI 和页面收完。本周只要求你能指着 demo 说：现在是谁在说话。

## 对应视频

[视频课表 · 第 5–7 周](../videos.md)

- 李宏毅 2026 Agent / Context / Multi-Agent：https://www.bilibili.com/video/BV1Sdw7zREka/
- LangChain Academy Intro to LangGraph：https://academy.langchain.com/courses/intro-to-langgraph
- LangGraph 多智能体实战（实战向）：https://www.bilibili.com/video/BV13roYBXELs/
- LangGraph 入门到实战（实战向）：https://www.bilibili.com/video/BV1EGc7zwEkR/

框架课放到晚上。白天请先用本仓库的 demo 建立「角色 = 函数 + 检索」的直觉。

## 练习

1. 写四条用户原话，标你会交给哪个角色。其中一条必须是「考我一下」。
2. 假设 tutor 平均 800 token、examiner 平均 400 token，计算「先讲再考」和「只考」的输入差。不必精确到分。
3. 反对题：给值班台加「情绪安抚 Agent」。用第 8 周面试题 D 的结构写六句反对或支持。

## 验收标准

- [ ] 三种结构各有一个你自己的生活例子（可以是请假、code review、家庭争论）。
- [ ] `python -m askhall demo` 退出码 0，输出里有引用。
- [ ] 你能说出 v1 不加第四个角色的理由，且理由包含费用或失败面。

## 常见坑

- 把三个角色做成三个相同提示，只改名字。那是一个人戴三顶帽子，账单按三个人收。
- 主管提示里写「你可以决定再调用自己」。递归主管是无限循环的亲戚。
- 看完 B 站实战视频后，把别人的图框架配置贴进问学堂。v1 不允许硬依赖。

## 延伸阅读

- Deep Agents 课（子 Agent、HITL）：https://academy.langchain.com/courses/foundation-introduction-to-deepagents
- 吴恩达 Agentic AI 的 Multi-agent 周：https://www.deeplearning.ai/courses/agentic-ai
- 下一周：[问学堂收完](06-askhall.md)
