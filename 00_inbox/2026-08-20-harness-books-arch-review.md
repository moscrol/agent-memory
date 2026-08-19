---
title: 从 harness 书目抽象 Agent 架构评审
type: inbox
agent: grok
source: harness-reference INDEX/MAP + distilled aab/mashu/hb1 + mashu ch25 原文
date: 2026-08-20
tags: [inbox, architecture-review, harness, ai-agent-book, mashu]
status: superseded
---

# 从 harness 书目抽象 Agent 架构评审

> **已被取代。** 权威收口见 harness-reference `DESIGN.md`（分支 `docs/harness-arch-review`）；精读校正见 `2026-08-20-mashu-arch-review-close-read.md`。本文 Q1 把马书原则一写成了「约束全进代码」，与 ch25.1 原文定义相反。
> 原始产出，服务于「代码地图能否升级成审架构」。读取日期：2026-08-20。

## 对象边界（先于清单）

书目在 `harness-reference`（INDEX=按来源，MAP=按方向），不是「一般软件架构教科书」。

| 代号 | 书 | 族 | 对「审架构」的可用性 |
|---|---|---|---|
| AAB | ai-agent-book《深入理解 AI Agent》10 章 | C | 章名≈agent 分层；生产公式可当评审脊柱 |
| MASHU | 马书《驾驭工程》ch25 六原则 | B | 控制面/fail-closed/锁存；与 HB1 同族，互证无效 |
| HB1 | harness-books book1 十条原则 | B | 9.5/9.7/9.8/9.9 可执行；同族于马书 |
| HB2 | book2 对比篇 | 跨系统 | 有跨系统成分，但多数章仍仅见标题 → 本笔记不用 |
| OFF | Claude 官方 harness 文档 | A | 冲突时以它为准 |
| BUILD | harness-reference/BUILD.md 七模式 | D | 本仓已落地的可迁移失败形状，评审时对照实现 |

**能审**：金融 Agent 的 Harness（上下文 / 工具 / 约束 / 验证 / 纠正、分层、到达率、门禁）。
**不能审**：DuckDB 星型模型、板块 VIEW、题材生命周期——书没覆盖。那是领域架构，对象是 specs。
**不要**把代码地图 / CRG 社区 / 空图 architecture overview 当评审证据。

## 评审脊柱（跨族一致处）

生产公式（AAB ch1，`distilled/aab-deep-read.md`，VERIFIED 2026-08-12 精读）：

`Agent = Model + Harness(上下文 + 工具 + 约束 + 验证 + 纠正)`

Demo 只需前三项；生产缺口几乎都在后三项。评审按五件套提问，缺一层就写「Harness 缺口」而不是「模型笨」。

AAB ch6：用 **model swap**（固定 Harness 换模型）vs **消融**（关某一 Harness 部件）区分「模型瓶颈」和「架构瓶颈」。这是审架构的实验方法，不是读调用图。

## 可执行清单（给评审 agent 的问题，不是新数据库）

### 1. 约束落在哪一层

- 结构（权限、预算、分层 import、无证据不准 finish）是否用**代码**强制？行为（文风、别过度工程）是否留在提示词？
- 来源：马书 ch25.1 适用边界「用代码处理结构性约束，用提示词处理行为性约束」（`sources/mashu/part7/ch25.md`，VERIFIED 2026-08-20 打开原文）；HB1 9.2 Prompt 是控制面一部分（蒸馏稿）。
- 本仓对表：BUILD 模式 1 棘轮门禁、模式 7 fail-closed、`layer_audit.py`。

### 2. 默认值是不是最安全的

- 未声明是否当危险？认不出的值是否放行？
- 来源：马书原则三失败关闭；AAB ch1「约束=故障安全默认值」；HB1 9.4 工具是受管执行接口。
- 本仓对表：BUILD 模式 7、`vault_lint` 白名单。

### 3. 验证是否独立

- 实现者 / composer 是否在给自己打分？
- 来源：HB1 9.9（蒸馏）；AAB ch4 与之**跨族一致**（INDEX 已登记，算交叉验证）。
- 本仓对表：judge≠composer；Bugbot/独立 review；不要让生成 wiki 审正门。

### 4. 每类故障有没有检测 / 恢复 / 终止

- API / 工具 / 上下文 / 控制流 四层是否都有路径？错误是否回灌成结构化输入而不是毁会话？
- 来源：AAB ch5 故障四层（`distilled/aab-deep-read.md` VERIFIED）；HB1 9.6/9.7 错误路径即主路径、恢复目标是继续工作。
- 本仓对表：不要「格式滑一档整份销毁」；episode 降级保留草稿。

### 5. 上下文是否可治理

- 能塞 ≠ 该塞。砍了什么有没有声明？状态栏/SessionStart 是否代码维护、是否覆盖会被问到的维度？
- 来源：HB1 9.5；AAB ch2 状态栏三条经验；马书 ch12 预算是安全机制（已精读）。
- 本仓对表：BUILD 模式 4 预算+声明式截断。

### 6. 多 Agent 是否在分区不确定性

- 并行理由是职责隔离还是「更快」？子 agent 是否只回结构化摘要？
- 来源：HB1 9.8；AAB ch10 新信息判据（2026-08-17 精读记忆）。
- 反模式：为审架构再开一个读 CRG 的子 agent 而不隔离职责。

### 7. 单一真本源且生成

- 能力清单 / 分层 / 工具目录是否手抄第二份？
- 来源：BUILD 模式 6（族 D 实测）；能力图谱 + graph_audit。
- 与代码地图关系：steering 不得变成第二份能力清单（已有 spec）。

### 8. 结论是否携带成立条件

- 「测试全绿」有没有树 / 解释器 / revision / dirty？
- 来源：BUILD 模式 5。审架构报告同样必须写成立条件，否则下一 agent 会重跑。

## 明确不从书里抽象出来的东西

- [推断] 马书 part7 ch28「CC 的不足」可能有架构反面教材，INDEX 标最该翻但本轮未打开全文 → 不得写入清单。
- HB2 多数章仅见标题 → 不用。
- 代码地图的 Leiden 社区名、CRG `architecture` CLI、空图 overview → 与上述清单的「验证独立 / 正门压过生成物」直接冲突。
- Trace：AAB ch6 说观测最有价值的去向是回流成评估资产；马书附录 f 是 CC `/commit` 子系统串联示例。审架构**不必先跑 trace**；只有在查「这一次循环死在哪一层故障」时才需要。

## 和代码地图的关系

| 产品 | 对象 | 问题 |
|---|---|---|
| 代码地图 query/ask | 正门 + 符号位置 | 有没有现成实现、该走哪条路 |
| 本书单抽象的评审 | Harness 五件套 | 约束/验证/纠正有没有设计上的洞 |
| 领域规格对照 | DuckDB / 复盘写入 / 题材 | 业务架构对不对 |

三者并列，不要升级成一张图。

## 提炼提示（哪些值得沉淀？）

- 若用户点头做 skill：checklist 用上面 8 问，引用只指向 distilled + mashu ch25 原文路径，不抄书。
- 机械体检（layer_audit / graph_audit / unread-fields / drift）挂在第 1/2/7 问下面当 0 档，不替代判断题。
- 不要把 AAB 量纲（连续 3 次压缩熔断、25 万次 API）写进本仓门禁。
