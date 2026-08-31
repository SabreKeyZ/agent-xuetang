# 小白常见坑

你卡住时先在这里搜报错关键字。这里不讲「心态」，只讲命令和账单。

## `python3.11: command not found`

正文要的是 **Python 3.11 或更新**，命令写 `python3 -m venv .venv`。
没有名为 `python3.11` 的二进制很正常。先跑 `python3 --version`，只要是 3.11+ 就能建 venv。
Windows 用 `py -3`。不要为了复制旧命令去装一个刚好叫 `python3.11` 的别名。

## Key 填错

症状：`401`、`AuthenticationError`、`invalid api key`、`The API key you provided is incorrect`。
第 0 周脚本还会先在本机拦住两种「还没发出去」的情况：

- 根目录没有 `.env`：stderr 写「缺少 .env」，请复制 `.env.example`。
- `.env` 已经在、但 `OPENAI_API_KEY=` 仍是空的：stderr 写「OPENAI_API_KEY 是空的」。复制示例文件不会自动带钥匙。

对照清单：

1. 根目录有没有 `.env`？只有 `.env.example` 不够。
2. Key 两边有没有空格、有没有用引号包一层？`OPENAI_API_KEY=sk-...` 即可，不要写成 `"sk-..."`。
3. `OPENAI_BASE_URL` 和 Key 是不是同一家。DeepSeek 的 Key 不能打到 `api.openai.com`。
4. 智谱、通义的兼容地址必须带它们文档里写的路径后缀，不要只写到域名。
5. 改完 `.env` 要**重新开**终端里的进程。已经在跑的 `serve` 读不到你后写的文件。

默认路径不需要 Key：先跑 `python -m ticketdesk demo` / `python -m claimdesk demo`。
**测 Key** 才用第 0 周的 `code/week0/hello_chat.py`。工单台在钥匙空时会走抽取式，看起来「能跑」，容易让你误以为 Key 已经生效。

## 代理和网络

症状：`Connection timed out`、`ProxyError`、`SSLError`、卡在「正在请求」超过 30 秒。

- 公司网或校园网常要 HTTP 代理。把 `https_proxy` / `HTTPS_PROXY` 设成你们网管给的地址。
- 开了系统代理但 Python 读不到时，试 `export HTTPS_PROXY=http://127.0.0.1:7890`（端口换成你自己的）。
- 不想走代理时，确认环境变量里没有残留的 `ALL_PROXY`。
- 国内访问部分官方课程视频会慢。本仓库练习本身不依赖 YouTube。
- Ollama 用 `http://localhost:11434/v1`，不要套一层需要认证的公司 HTTPS 代理，除非你知道自己在做什么。

## Token 账单

症状：控制台余额掉得很快，或突然欠费停服。

- 练习阶段选各家的**小聊天模型**，不要选最贵的推理模型。
- 第 2 周就把 `max_steps` 写死（我们的示例是 6）。循环没有上限，账单也没有上限。
- 多 Agent 会把同一段上下文复制多份。第 5 周的练习就是让你亲眼看见「多一次交接多一笔输入」。
- 调试时把完整 prompt 打到日志里之前，先确认日志文件不会被同步到网盘。
- 免费额度用完会变成 402 / 429。先检查账单页，再怀疑代码。

本仓库的 `demo` 命令默认不打云端。想省钱：先把评测和抽取式跑绿，最后再开 Key。

## 无限循环

症状：终端不停刷 `Thought:`，或同一条工具被调用十几次。

原因通常是下面四个之一：

1. 模型把「再试一次」当成策略，而你没有步数上限。
2. 工具报错时，你把同样的错误观察又喂回去，没有改输入。
3. 停止条件写的是「模型说我做完了」，但模型从不说。
4. 搜索工具每次都返回同一句「未找到」，模型以为换个问法就能找到。

处理：

- 硬上限：步数、总 token、墙钟时间，至少设一个。
- 结构化日志里看是不是 `action` 和 `observation` 在重复。重复两次就该停。
- 工具失败要换一种失败信息，例如 `invalid_expression`，不要只回 `error`。
- 人在回路：第 4 周的 Skill 里可以要求「删除文件必须先问人」。练习阶段用打印代替真正的危险操作。

## Windows 路径和编码

- PowerShell 激活：`.venv\Scripts\Activate.ps1`
- cmd 激活：`.venv\Scripts\activate`
- 若 `python` 不是 3.11+，用 `py -3`。
- 控制台乱码时：`chcp 65001`，或在 PowerShell 里 `$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8`。
- 不要把仓库放在带中文空格的桌面路径里，早期脚本会把路径当参数切错。

## `pip install -e` 失败

- 先升级 pip：`python -m pip install -U pip setuptools`。
- 确认你在仓库根目录，路径是 `projects/ticketdesk` 而不是你自己新建的空文件夹。
- 公司镜像若缺 `fastapi`，临时切到官方源：`pip install -e projects/ticketdesk -i https://pypi.org/simple`。

## 演示能跑、服务起不来

- 8000 端口被占用：`python -m ticketdesk serve --port 8010`。理赔台默认 8001。
- 浏览器打开的是 `https://` 而服务是 `http://`。
- Docker 里要映射端口，见工单台 README 的 compose 段。

## 可以不手写全部代码吗

班 01–05 仍手写小脚本（`code/week1` … `code/week5`）。日历第 3 周前半用工单台最小版：[vibe](weeks/vibe.md) + `labs/vibe-minidesk`：你贴分步提示，自己验 diff。第 3 周后半 / 第 4 周前半走读已经写好的两台，不是让你从零手写 Inbox。

默认 `pytest`（以及 CI）不含 `labs/`——空 stub 会红，不能让 main 红。学徒验收：

```bash
python -m pip install -e labs/vibe-minidesk
pytest labs/vibe-minidesk/evals
```

不要从 `projects/ticketdesk` 开写，不要一次把五份提示贴完。不需要 Key。

还是不行：用 [卡住了](../.github/ISSUE_TEMPLATE/stuck.yml) 模板开 Issue，贴操作系统、`python3 --version`、你敲的整条命令、完整 traceback。不要只贴「跑不起来」。
