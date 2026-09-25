---
title: 「谁读这个字段」别只查顶层 import，函数内 import 会漏
type: knowledge
stance: principle
agent: all
source: finance-workspace-private PR #935（fix/replay-rebuild-keep-observations-0925，2026-09-26）
date: 2026-09-26
tags: [verification, static-analysis, replay, python]
status: verified
related: ["[[extraction-masks-must-not-feed-classification]]"]
---

# 「谁读这个字段」别只查顶层 import，函数内 import 会漏

## 判据

要断言「改 / 删字段 F 不影响流程 P」，常见做法是：列出 P 入口模块顶层 import 的模块，再逐个 grep 有没有读 F。

这个做法会漏掉函数体里的 import。Python 里函数内 import 很常见：为了避开循环依赖、推迟重模块加载，或者只在某个题型分支才需要。grep 顶层 import 看不到这些，漏掉的恰好是少数题型才走的分支。

结论要靠真实存量数据上的两臂 A/B 来定：同一进程、同一份下游代码，两臂只差字段 F，然后比较完整输出。

## 实例（2026-09-26，金融存证重放）

- **改动**：`judge_loss_point_replay._rebuild_outcome` 原先把证据的结构化观察值置空，现在改为还原。需要判断首个损失点的重放结果会不会变。
- **静态结论**：`verify_episode_outcome` 顶层 import 的模块都不读 `.observations`，于是判断「不变」，还写进了第一版提交说明。
- **A/B 结论**：3291 份复核存档里有 8 份财报题的结构列变了。原因是 `episode_verifier` 在 `financial_analysis` + `metric_evidence` 分支里，于函数体内 import `financial_report_contract`，后者按观察值核对报告期与指标。观察值置空时，有据的槽被判缺。
- **代价**：如果信了静态结论，旧重放会把这 8 份的「与生产结构结论不一致」当成真差异；新行为则会被写成「对损失点零影响」。

## 怎么判定（可执行的问法）

- 从字段出发，而不是从入口出发：用 `rg "\.F\b"` 在全仓找出所有读者，再逐个反查它能否从入口到达。反查时要看函数体里的 `import` / `from … import`。
- 字符串分派同样是盲区：`getattr(module, name)`、注册表按名字加载、JS 的 `import()`，都不会出现在 import 图里。
- A/B 要分口径计数。两臂都重建失败的样本单独列出，不要算进「字段被丢」。本例中 1184 条「缺失」观察值全部落在两臂都失败的 outcome 里，坏条目其实是 0。
- A/B 找到差异后，确认差异的方向：新臂是否更接近生产存证的结论（这里 `structural_delta` 全部由 True 变为 False）。这样才能判断改动是修正还是回归。

## 可迁移场景

- 评估「删掉 / 改名一个 DTO 字段是否安全」。
- 判断「这个配置项还有没有人读」。
- 下线旧 API 字段前做影响面分析。
- 任何「X 不影响 Y」的负面断言。这类断言的共同难处在于，证明「没有」要比证明「有」难得多。
