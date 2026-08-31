# 2 小时路径 · 只走读两张脸

这不是第 1–5 周的代码课，也不是申请 Key 的下午。
120 分钟里你只做三件事：把两台桌子跑起来，点开队列里的几张单，能用自己的话讲清芯片、红条、钱为什么没走。

空 `.env` 即可。两台都是抽取式。不要申请 Key，不要 Docker，不要改 Python。

完整 1 个月仍从 [第 0 班](00-setup.md) 进。本页是先见面的走读，不是那 4 周表。

对照：[第 0 周](00-setup.md) · [工单台](06-ticketdesk.md) · [理赔台](07-claimdesk.md) · [FAQ](../faq.md)

## 你要带走什么

- [ ] `python -m ticketdesk demo` 和 `python -m claimdesk demo` 打出芯片或红条。
- [ ] Inbox 点过缺单号、超 ¥200、活动芯片各一张；每张各写三句。
- [ ] Payments 点过通过案和拒赔案，能用自己的话区分出险日 / 投保日。
- [ ] 读过第 0 周失败对照，并从 FAQ 抄过一行会搜的关键字。
- [ ] 能向旁边的人讲：芯片引什么、红条拦什么、演示为什么不打款。

## 0–20 · 克隆、venv、两句 demo

克隆并进入仓库：

```bash
git clone https://github.com/SabreKeyZ/agent-xuetang.git
cd agent-xuetang
```

已经在仓库里就跳过 `git clone`，确认当前目录是仓库根。

建虚拟环境，装两个毕业作品：

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate
python -m pip install -U pip pytest
python -m pip install -e projects/ticketdesk -e projects/claimdesk
```

提示符前面要有 `(.venv)`。没有 Key、空 `.env` 也能跑。终端里应当出现芯片或红条：

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

打开两张脸。8000 常被占用，工单台请显式指定 8010（[FAQ](../faq.md)「演示能跑、服务起不来」同条）。理赔台默认 8001。另开一个终端，两边都先 `source .venv/bin/activate`：

```bash
python -m ticketdesk serve --port 8010
# http://127.0.0.1:8010
```

```bash
python -m claimdesk serve
# http://127.0.0.1:8001
```

浏览器开 `http://`，不要写成 `https://`。工单台是浅色会话；理赔台是支付表。两台都不要黑底。

- [ ] 两句 demo 打出芯片或红条。
- [ ] 8010 和 8001 都能打开。

## 20–50 · 工单台 Inbox，点三张单

浏览器打开 http://127.0.0.1:8010 。画面应当是左边 Inbox、中间灰/白气泡，不是理赔台那张支付表。细节见 [第 6 周 Inbox](06-ticketdesk.md#浏览器--inbox-怎么走)。

现场 Inbox **约 25 行**（夹具都留着，不删）。走读工单 T-1001 / T-1201 / T-1401 在 PR11 之后可能置顶；截图是指定工单，不是「列表第一行就是你要的那张」。找不到就用地址栏：

```
http://127.0.0.1:8010/?case=T-1001
http://127.0.0.1:8010/?case=T-1401
http://127.0.0.1:8010/?case=T-1201
```

也可以 `?case=missing-order-id`、`?case=refund-over-200`、`?case=promo-overrides-sla`。筛选先点「全部」：缺单号和超 ¥200 不会出现在「待你执行」里。

对下面三张单，**各写三句话**（一句芯片、一句红条、一句执行钮）。没有红条就写「没有红条」。不要抄第 6 周实录当自己的话。

### 1. 缺单号 · T-1001 · `missing-order-id`

点 T-1001（宋纸，快递没到先退钱）。

- 芯片引的是哪份政策？（常见：`docs/policy/after-sales.md:…`）
- 玫瑰色红条写了什么？（常见：没有完整订单）
- 「执行」为什么锁着，还是 `confirm_required`？（常见：缺单号，只许追问）

### 2. 超 ¥200 · T-1401 · `refund-over-200`

点 T-1401（赵牧，镇尺整单 ¥486）。

- 芯片引的是哪份政策？（常见：`docs/policy/refund-and-risk.md:…`）
- 红条写了什么？（常见：闸门员拒绝执行）
- 「执行」锁着还是能点？锁着的原因写进笔记。（常见：超 ¥200，只许草稿）

不要把玫瑰色拒绝看成「已退款成功」。

### 3. 活动芯片 · T-1201 · `promo-overrides-sla`

点 T-1201（林小秋，大促墨水五天没动）。

- 芯片必须点名哪份活动文件？（常见：`docs/policy/promo-2026-summer.md:…`）
- 有没有红条？对客草稿是发券还是发现金？
- 「执行」锁着，还是须人确认（`confirm_required`）？点了会不会打款？

活动期只引日常「不赔运费」是错引用。点芯片应打开政策片段，不是 404。

- [ ] 三张单各写了三句，用的是你屏幕上的原文。

## 50–80 · 理赔台 Payments，通过与拒赔

浏览器打开 http://127.0.0.1:8001 。先看见 Payments 表（案件号 / 险种 / ¥ / 状态机 / 出险日），再点一行进卷宗。这里没有会话气泡。细节见 [第 7 周浏览器](07-claimdesk.md#浏览器)。

现场约 19 行。C-2009 / C-2002 在 PR11 之后可能置顶。找不到就：

```
http://127.0.0.1:8001/?case=C-2009
http://127.0.0.1:8001/?case=C-2002
```

也可以 `?case=valid-low`、`?case=wrong-policy-version`。

### 1. 通过案 · C-2009

点 C-2009。芯片应是条款号 + `qingtu-bao-v2.md`，**不要**出现条款 3.2。巨型 ¥ 是试算，不是已经打款。

右侧「执行打款」即使能点，演示也永远 `confirm_required`，钱不会走。点一下，确认提示是审计、不是到账。

### 2. 拒赔案 · C-2002 · 条款 3.2

点 C-2002。芯片必须点名 **条款 3.2**，路径是 `qingtu-bao-v2.md`，不要出现 `qingtu-bao-v1.md`。决定书写「建议拒赔，不予赔付」；试算式可以留着，那不是赔付承诺。

**不要**在拒赔案上点「通过」，指望服务端改判。本机改选不会改服务端结论，打款仍按核赔建议锁定。

### 用自己的话写：出险日 vs 投保日

打开 [第 7 周「出险日 vs 投保日」](07-claimdesk.md#出险日-vs-投保日pathline)。看 C-2002 卷宗上的出险日、投保日、条款版本。在纸上写三句：

- 出险日是哪一天、用来干什么。
- 投保日是哪一天、检索读不读它。
- 为什么 8 月易碎案必须用 v2，不能因为「我投保早」就主张 v1「易碎赔 50%」。

- [ ] 通过案和拒赔案都点过；出险日三句是自己的话。
- [ ] 你看见过：执行打款不打款。

## 80–110 · 第 0 周失败对照 + 一条 FAQ

打开 [第 0 周 · 失败对照 · 钥匙写错](00-setup.md#失败对照--钥匙写错)，把下面三行抄进笔记（只读，**不要申请 Key**）：

| 现场 | 你会看见 |
| --- | --- |
| 根目录没有 `.env` | 退出码 2，「缺少 .env」 |
| `.env` 在、`OPENAI_API_KEY=` 仍空 | 退出码 2，「OPENAI_API_KEY 是空的」 |
| `OPENAI_API_KEY=sk-wrong` | HTTP 401，不是「模型不会中文」 |

「缺少 .env」和「钥匙是空的」不是同一句话。两句都还没发出去。

可选：不建 `.env`，跑一句，把 stderr 原文贴进笔记。

```bash
python code/week0/hello_chat.py
```

不要填 Key，不要改 `OPENAI_BASE_URL`。错 Key 那一行只对照文档，本小时不打网。

然后打开 [FAQ](../faq.md)，**任选一行**，写下：

- 标题是什么。
- 卡住时你会搜哪个报错关键字（例如 `401`、`command not found`、`8000`）。
- 这一行让你下一步敲哪条命令，或去核哪一件事。

- [ ] 失败对照三行在笔记里。
- [ ] FAQ 选过一行，写下会搜的关键字。

## 110–120 · 验收

合上屏幕，对着一张纸或旁边的人讲完这三句。讲不出来就回到对应分钟，再点一遍，不要往下翻第 1 周。

- [ ] **芯片**：工单台是 `docs/policy/…:行号`；理赔台是 `条款 3.2 · path:line`。没芯片就不能当答案。
- [ ] **红条**：缺单号、超限额、无条款命中，都会拦。活动案可以没有红条，但必须点名大促文件。
- [ ] **钱不走**：闸门锁「执行」，或钮能点也只记审计。`confirm_required` / `executed=False`。演示不打款。

停。不申请 Key，不跳第 1 班。还要学循环和评测，从 [工期目录](README.md) 的 4 周表接着走。

有余力、还没摸过助手改代码：日历第 3 周前半 [vibe 班](vibe.md) 大约 20–30 分钟（只走 01 + 看一份 BAD/GOOD diff 也行）。理赔侧同款指针：[vibe-claim](vibe-claim.md)。不计入这 120 分钟，不要从工单台 / 理赔台源码抄。
