---
title: 存了历史 ≠ 能按时点重放——追加、冻内容、读取面 as-of，三者缺一不可
type: knowledge
stance: principle
agent: claude
source: 双时态数据建模通用原理；2026-09-14 以 finance-workspace-private@gitea/main:1fef3d27 的 river 工单 #27/#43/#47 与 memory_status / 经验卡读取面逐条核源
date: 2026-09-14
tags: [knowledge, temporal, point-in-time, audit, memory, data-modeling, replay, general]
status: draft
related: ["[[state-transition-identity-must-survive-dedup]]", "[[schema-epoch-when-field-semantics-change]]", "[[correction-channel-must-pass-the-same-evidence-gate]]"]
---

# 存了历史 ≠ 能按时点重放

> **性质：通用原理。**

## 判据

**保存了历史材料，不等于能按历史时点重放。** 三件事缺一不可：

1. **写入端**：撤销与纠正是**追加新记录**，不是修改旧记录
2. **内容端**：这条记录的**内容版本本身被冻结**，而不只是时间戳不动
3. **读取端**：能问「截至 T 时刻，这条是什么状态、什么内容」，而不只是「现在是什么」

任何一件缺席，都不能据此宣称完整的历史重放能力。**如实返回缺口或降档**仍是正确行为；危险的是把今天的值冒充成当时已知的值。

最常见的伪装是第 2 条：**时间戳不更新 ≠ 内容被冻结**。保留首次写入时间、同时允许内容列被覆盖，等于让后来修订的值**带着当时的时间戳通过时点检查**——这是历史泄漏，不是历史保存。

## 怎么判定（可执行的问法）

对任何自称「留了历史」的存储，按顺序问三句，缺一条即不成立：

**问一｜撤销或纠正，是新增一条记录，还是改了旧记录？**
- 改旧记录 → 「当时为什么认为它成立」已经不可知。停在这里，后两问没有意义。

**问二｜这条记录的内容后来能被覆盖吗？覆盖时时间戳跟着走吗？**
- 内容可覆盖 **且** 时间戳不动 → **最危险的那一种**：审计字段齐全、返回值是今天的。
- 这一问专治「我们加了 `recorded_at` / `created_at`，所以有审计了」。

**问三｜能不能问「截至 T 时刻」？还是只能问「现在」？**
- 只能问「现在」→ 材料在，重放不出来。事件存了一堆，读取端只算最新状态，等于没存。

**验收反例（三条同时成立才算过）：**

> T 日写入内容 A → T+7 追加一条撤销 →
> 以 `C=T` 重放，**必须得到 A、且状态为未撤销**；
> 以当前时点读取，**必须看到已撤销**。

**原始内容与撤销事件都要受截止时点约束**——只约束其一都漏：只约束撤销事件，内容被修订后仍返回新值；只约束内容，撤销事件会穿越回 T。

## 适用条件

尤其在这几种时候想起它：

- 任何要回答**「当时看到的是哪个值」**的系统：PIT 回放、模型校准、事后归因、合规审计
- 数据源会**修订**历史（行情、财报、统计口径、评分），而不是只追加
- 你刚给某张表加了 `recorded_at` / `deleted_at` / `version`，正准备说「这下可以审计了」
- 有人说「我们是 append-only 的」——**要追问的是问二和问三，不是问一**

## 什么时候我不用它

1. **数据源本身不修订历史**，只追加（日志流、事件流、成交回报）。时间戳即内容版本，问二自动成立。
2. **不需要按时点回答问题**的场景：纯 serving、只要最新状态的缓存、KV 配置。为它上三件套是过度工程。
3. **【最容易被误用的那一种】** 把它读成「所以必须做全量内容版本化」。**冻结是有成本、有范围的**——能力可以是可选开关、只覆盖部分表、无版本时回落当前源。这条判据要求的是**把选版规则、未覆盖范围、缺版本时的降级行为写明**，不是要求全量冻结。**含糊的「我们支持历史查询」比明确的「不支持」更危险**，因为前者会被下游当成可信。
4. 追溯期短于修订周期时（数据 T+1 定稿、而你只回看当天），成本可能压过收益——但要**显式说出这个假设**，而不是默认它成立。

## 与项目的关系

[实测 2026-09-14，`finance-workspace-private@gitea/main:1fef3d27`]

- **river 问二的完整现场**：工单 #43（`07857c80`）撤掉 `LEAST(updated_at, 名单快照 captured_at)`——台账 `captured_at` 证明的是**名单版本**、不证明行情内容，于是 T 日 1% 被 T+7 修订成 9% 的那一行会被标 strict 并返回 9%。而工单 #27 的 `recorded_at = COALESCE(<table>.recorded_at, excluded.recorded_at)`「已有就不动」**单独不充分**（内容列照常被覆盖），且该写法自其唯一一次提交 `575136b9` 起就存在，**不是后来才失效的**。问二的正解是工单 #47：`slice_river(frozen_snapshot_root=...)` + `river_frozen.connect_frozen`，已在 main。
- **同一函数里两种失败、两种待遇**（`river.py:898-903, 945-978`）：封印校验失败 → **抛错不回退**；无 ≤ cutoff 快照，或最近快照早于 `as_of` → **回落当前库并在 `content_source.reason` 留痕**。回落后仍过既有时点门，不能称作静默放行：当前内容的 `updated_at <= C` 仍是当时已知的充分证据；`updated_at > C` 或缺失时，普通读取降为 `trade_date_only`，`require_strict=True` 则滤除这些对象，被滤空的轨返回 `Gap(reason="pit_filtered")`（`river.py:174-192, 854-878, 1030-1031`）。**无冻结版本不等于必须整片降档**，还要看当前行是否能证明当时已知。
- **默认不选版、能力范围有限**：不传 `frozen_snapshot_root` 时沿用当前库读取和上述时点门；传入后只对 `SNAPSHOT_TABLES` 覆盖集取冻结内容（该 revision 为 14 张骨干表），集内未拍到的表保持空，不偷读当前值；集外表与实体别名仍读当前库，`content_source.config_tables=live` 声明此边界。#47 是**日频 PIT**，不区分同日盘中多个版本，也不承诺全表历史冻结；`river_window` / `anchor_windows` 在该 revision 尚未接版本源。应逐项陈述这些已定边界，不能概括成「缺版本的等级契约未定」或「所有历史问题已解决」。
- **经验卡 / `memory_status` 同病**：`memory_status` 已过问一（归档/撤销/恢复都追加事件，源码解释了为什么不能改历史）；经验卡尚未接入该协议；**两者读取端都只算最新状态、无按时点查询——问三未过**。

一条**存在性观察，不作有效性证据**：Mem0 在 2026-04 换代时，把 LLM 决策的 ADD/UPDATE/DELETE 整体换成 ADD-only。这只证明有主流项目做了这个选择；其 README 同批列了实体关联、多信号检索、时间排序等多项改动，分数又来自含专有优化的托管版，**没有消融，不能把涨分归因到取消覆盖**。

## 订正记录

- 2026-09-14 · codex · 保留 claude 原文的三层判据；据固定 `finance-workspace-private@1fef3d27` 的 `river.py::RiverSlice.pit_grade`、`_enforce_cutoff`、`slice_river`，以及 `river_frozen.py` 和工单 #47，撤销「无快照回落就是 fail-open / 静默返回今天数据、缺版本降档契约未定」的判断。回落是否可 strict 取决于内容时点证据；补记日频、覆盖集与尚未接线的区间读取边界。

## 参考

- [[state-transition-identity-must-survive-dedup]]
- [[schema-epoch-when-field-semantics-change]]
- [[correction-channel-must-pass-the-same-evidence-gate]]
- [[fast-path-must-not-mint-authority]]
- [[finance-agent-capability-graph]]
