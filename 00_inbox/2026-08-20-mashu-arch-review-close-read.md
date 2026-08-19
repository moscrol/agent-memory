---
title: 马书 part7 + AAB 原文精读 · Harness 架构评审骨架校正
type: inbox
agent: grok
source: harness-reference/sources/mashu/part7/ch25-28,ch30 + part1/ch03,ch04 + part3/ch12；ai-agent-book/book/chapter1,4,5,6,10
date: 2026-08-20
tags: [inbox, architecture-review, harness, mashu, ai-agent-book]
status: draft
---

# 马书原文精读 · 校正 2026-08-20 八问骨架

> 取代同日 inbox `2026-08-20-harness-books-arch-review.md` 里「可执行清单」的权威地位。那份骨架可用，但 Q1 说反、L2/L5/L6 过瘦。收口产物是 harness-reference `DESIGN.md`（分支 `docs/harness-arch-review`）。
> 读取日期：2026-08-20。下列主张均打开过正文，标 VERIFIED。马书未打开的章仍不得进入结论。

## 打开过的原文

| 文件 | 族 | 用于哪条骨架 |
|---|---|---|
| `sources/mashu/part7/ch25.md` | B | 六原则；Q1 纠正 |
| `sources/mashu/part7/ch26.md` | B | 上下文六原则（扩 Q5） |
| `sources/mashu/part7/ch27.md` | B | 双层约束、能力降维、工具级提示词 |
| `sources/mashu/part7/ch28.md` | B | 旧笔记标「未打开」→ 本轮已打开；不足当反面教材 + 容错三层 |
| `sources/mashu/part7/ch30.md` | B | **评审走六层栈**；谁拥有 loop |
| `sources/mashu/part1/ch03.md` + distilled | B | 回灌一等公民、死亡螺旋 |
| `sources/mashu/part1/ch04.md` | B | fail-closed、分层错误级联 |
| `sources/mashu/part3/ch12.md` §12.8 | B | 「预算是安全机制而非优化机制」 |
| `~/ai-agent-book/book/chapter1.md` | C | 生产公式原文、五功能表 |
| `~/ai-agent-book/book/chapter4.md` | C | Sidecar 只看结构化 JSON；提议者-审核者 |
| `~/ai-agent-book/book/chapter5.md` | C | 故障四层原文、Harness 四原则 |
| `~/ai-agent-book/book/chapter6.md` | C | 评估对象 Model+Harness；swap vs 消融 |
| `~/ai-agent-book/book/chapter10.md` | C | 新信息判据 |
| `distilled/harness-books-ten-principles.md` | B | 9.5/9.7/9.8/9.9；与马书互证无效 |
| `distilled/book2-ch07-convergence.md` | 跨系统 | 政体取舍；堆 prompt |
| `BUILD.md` | D | 七模式挂 0 档 |

HB1 ch09 原文本次未重新打开（蒸馏稿 2026-08-10 已精读全章 66 行）→ 引用走蒸馏，不把标题当新证据。

## 骨架校正（相对旧八问）

### Q1 说反了 — VERIFIED ch25.1

旧写：「结构用代码、行为用提示词」当作原则一的定义。

原文**定义**：「用系统提示词段落引导模型行为，而非用代码逻辑硬编码限制。」共同主题：「控制行为的最佳方式不是编写更多代码，而是设计更好的约束。」反模式是**行为硬编码**（为每种不想要的行为写检测器）。

「用代码处理结构性约束，用提示词处理行为性约束」是**适用边界**，不是对「把约束都写成门禁」的授权。

与 AAB ch5「约束优先于指导」（`chapter5.md` 约 L222，VERIFIED）叠合：能 Linter/CI 强制的不要停在「请遵循」；不能用代码检测的行为不要做成规则引擎。高风险动作用 ch27 **双层约束**（软提示词 + `call()` 硬拒绝）。

### 缺「谁拥有循环」— VERIFIED ch30

ch30：「委托给 CC 内置 Agent 更简单，但你失去了精细控制」。六层映射的前置决策。族 D 五不变量已有拥有/租用表，旧八问没接上。

### 缺「先取舍路线」— HB2 ch07 已精读

堆 prompt 是第三条路。旧八问没有政体。finance 曾被蒸馏稿判为三条同时跑。

### Q5 过瘦 — VERIFIED ch26

「能塞 ≠ 该塞」只覆盖 HB1 9.5。ch26 还有：spawn 时卫生（不是事后压缩）、压缩后选择性恢复、告知而非隐藏、熔断、保守估算。ch12 §12.8 原文：「token 预算是一个安全机制而非优化机制。」ch28.4：告知 ≠ 行动。

### Q4 过瘦 — VERIFIED AAB ch5 + mashu ch03/ch04

故障四层原文：API / 工具 / 上下文 / 控制流。纠正原则（ch1 五功能表）：确认无法恢复之前不暴露中间态。ch03：回灌叫 `stop_hook_blocking`；死亡螺旋时不跑 hook。ch04：选择性级联。HB1 9.7 继续工作。

### 缺 L6 — VERIFIED ch25.5 / ch30.7

先观察再修复。审架构不要求 trace；要求系统设计里有观测点。

### ch28 本轮已打开 — VERIFIED

旧 inbox：「ch28 未打开全文 → 不得写入清单」。现已打开。可进评审的反面形状：分散注入、有损压缩不可逆、Grep≠AST、告知不等于行动、flag 组合打地鼠。每条都有「权衡的另一面」——评审写缺口时要写在付什么代价。容错三层（检查点 / 可恢复执行 / 补偿）审崩溃恢复时用。

### 六层栈应是巡检顺序 — VERIFIED ch30.10

旧八问是扁平问题表。ch30 把 22 个模式收成 L1–L6，并标明模式之间有互补也有张力（预算 vs 缓存断点、编辑前读取 vs token 预算）。`DESIGN.md` 改用六层走，八问散入各层。

## 交叉验证（本轮仍然成立）

- 独立验证：AAB ch4 Sidecar（族 C）× HB1 9.9（族 B）= 有效跨族。马书 YOLO 不能再拿来「证实」同一点。
- CLAUDE.md 四级加载：马书 ch19 × 官方 memory.md，INDEX 已登记，本轮未重读原文。
- 失败关闭默认值：马书 ch02/ch25 × AAB ch1 约束=故障安全默认值，跨族形状一致。

## 明确仍不抽象

- 领域架构（DuckDB / 题材）
- 把 CRG / 生成 wiki 当架构证据
- 把 CC 的 3 次熔断、50K、89 flag 写进本仓门禁
- 未打开的马书章（ch01 全景细节、ch09 压缩模板全文等）——蒸馏稿可作指针，新主张须再打开

## 提炼提示

- 已收口：`harness-reference/.worktrees/docs-design-closeout/DESIGN.md`（分支 `docs/harness-arch-review`）。合入 harness-reference `main` 后改 KIT 指针为仓根 `DESIGN.md`。
- 不要升 `10_knowledge/` 第二份清单；知识层五不变量仍是控制面权威。
- 旧 inbox 八问保留作演进记录，评审以 DESIGN 为准。
