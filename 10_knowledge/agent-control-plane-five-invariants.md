---
title: Agent 控制面五条不变量：设计可知，量纲必测，谁拥有循环决定形态
type: knowledge
agent: claude
source: finance-workspace-private R-20260804-10 headless in-flight tool handoff（2026-08-04 质检实测）
date: 2026-08-04
tags: [knowledge, harness, agent, control-plane, timeout, budget, concurrency, methodology, core]
status: verified
related: ["[[../20_projects/finance-workspace-private]]", "[[agent-system-closed-loop-first-principles]]", "[[eval-harness-variance-governance]]"]
---

# Agent 控制面五条不变量

## 先分三层，别混为一谈

做 agent harness 时，"该严还是该松"的答案取决于在哪一层。三层的**可知性完全不同**：

| 层 | 管什么 | 正确设计可知吗 |
|---|---|---|
| **控制面** | 预算、超时、取消、配额、发布权 | ✅ 完全可知，业界解决几十年 |
| 通用层 | 格式、解析、编号、JSON 合法性 | 🟡 大体可知，宽容度要标定 |
| 领域层 | 数字有没有出处、claim 绑没绑证据 | ❌ 无已知正确解，只能实验 |

**推论：控制面的轮次消耗是设计纪律问题，不是问题本身难。** 领域层才是该花实验预算的地方。
（通用层/领域层的松紧原则另见 harness 分层记忆：通用层宽容、领域层严格。）

## 控制面五条不变量（设计评审逐条打勾）

不是发明，是同一形状在 Go `context.Context`、Trio cancel scope、Erlang supervision tree、
数据库两阶段预留里反复出现：

1. **预算单一权威** — "还剩多少"只能有一处说了算。多处各算一遍必然算出自相矛盾
   （典型症状：`remaining_calls=0` 同时 `must_finalize=false`）。
2. **预留-结算（reserve-then-settle）** — 名额在干活**前**原子占住，事后只结算差额。
   放在干活后就是 check-then-act race：两个请求同时看到"还剩 1"，双双执行，最后才有
   一个扣账失败——而活已经干完了。
3. **取消传播** — 上游的截止时间必须传到最下游那个真正干活的人手里。
4. **发布权闸门** — 到点先收回"你还能不能写结果"的权限，再谈通知。顺序反了会有迟到写入。
5. **绝对截止而非相对超时** — 存"几点几分必须结束"，不存"给你 30 秒"。后者每跳重新计时，
   总时长会膨胀。

**实测教训**：R-10 的设计文档写对了 1/4/5，**漏了第 3 条**，于是 Task 1 忠实实现了设计，
grant 变成了只记录不执行的 telemetry——比完全不做更危险，因为仪表显示一切正常。
这与"覆盖率正常、值是空壳"的静默降级同族。**逐条对表本可在写 design 当天拦住。**

## 谁拥有循环，决定控制层的形态

复用现成 agent SDK 时，能复用到哪一层取决于这个：

| 形态 | 谁拥有 agent loop | 控制层怎么进去 |
|---|---|---|
| **拥有循环** | 我们（SDK 在我们进程内） | 直接注入：传 context、传 config |
| **租用循环** | 对方 CLI/服务（subprocess/HTTP） | 只能守门：在工具调用的缝上设闸 |

实例（finance-workspace-private）：
- `sdk_gpt` / `sdk_glm` → 真调 `agents` SDK 的 `Runner.run(max_turns=...)`，属"拥有循环"。
- `codex_headless` → `subprocess` 起 Codex CLI，模型 loop 在**对方进程**，靠 mailbox（文件）
  或 HTTP 通信。属"租用循环"，因此必须有 `headless_tool_gateway` 这道边界闸。

**这不是重造 SDK 控制层，是两种根本不同的形态。** 不存在谁复用谁。

## SDK 给能力，不给数值

即使用了 SDK，这三样仍然要自己写：

- SDK 的 `max_turns` 管**一次 run 之内**转几圈；我们的预算单位是 **episode**
  （初次研究 → repair → 再研究，跨多次 run，还要算秒数）。**量纲对不上。**
- 因此 `_ROOT_BUDGET_CALL_RESERVATION_SECONDS`、`_sdk_runtime_timeout`、
  `_sdk_delivery_reserve` 全长在自己的文件里，即使那条路已经用了 SDK。

**同一个"预留收尾时间"的形状，三条后端三个数**：Codex 的 60s 是 wrapper 协议的静态事实
（不是我们选的）、30s synthesis reserve 是 profile 定的、SDK 那条是第三套推导。

→ 呼应总原则：**资料/框架给形状，量纲自己算。** 已踩过的坑：抄参考资料里的 30s stall
阈值，而我们单阶段只跑 31–45 秒，那个阈值永不触发。

## 试错 vs 实验

- **试错** = 改一版跑跑看，好像好点了，留下。攒不出命中率。
- **实验** = 动手**前**写下"改完会看到什么"，再验证，错了记 `refuted`。

`refuted` 是最有价值的输出（"上次判错了层"的硬证据）。配合"同类 fix_type 连续 3 次
`refuted` → 停止堆补丁、升格质疑架构层"，这是防止实验退化成无限试错的刹车。

## 已知技术债（记录，勿立即动手）

同一套 reservation 逻辑正在被写第二遍（SDK runtime 一份、gateway 一份），靠人工同步
`1e-9` 这类常量。正确做法是抽成共享控制面模块、两侧实现同一组接口。

**但不要在验证闭环结案前重构底座**——那会同时换掉唯一的验证基线，让结论无法归因。
等 R-20260804-10 `confirmed` 后再提。
