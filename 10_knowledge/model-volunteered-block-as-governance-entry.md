---
title: 模型自愿输出的结构块不能当治理路径的唯一入口——换模型即静默失效
type: knowledge
agent: cursor
source: finance-workspace-private 2026-09-03 实测（deep 升档链 PLAN→govern_mode→批 deep→起分支：08-17 生产模型 gpt-5.6-terra→GLM 后 PLAN 率 30%→0%，deep 48/417→2/385，子研究协调器休眠 12 天无人察觉，门禁全绿；docs/verification/2026-09-03-plan-deep-rate-by-model.md）
date: 2026-09-03
tags: [knowledge, agent, governance, prompt, failure-shape, model-swap]
status: verified
related: ["[[info-not-delivered-bug-pattern]]", "[[two-phase-page-first-nonempty-is-not-final]]", "[[../20_projects/finance-workspace-private]]"]
---

# 模型自愿输出的结构块不能当治理路径的唯一入口

> **失败形状**：某条治理/升档/分支路径的第一环，是模型「可以」在回合里输出的一个结构块（PLAN、self-critique、
> requested_mode…）。指令写的是「可以先输出…也可以直接调工具」。换了模型，新模型几乎从不选那条「可以」，
> 整条路径归零——代码没改、测试全绿、指令原文一字未动，只有生产统计能看出来，而没人天天数它。

## 怎么认

- 某类事件（`mode_decision` / 分支启动）在时间线上有一个干净的断点，断点日与代码提交对不上、与模型切换对得上。
- **同一天双模型对照**是最强证据：本例 08-13 同一份代码，gpt 24/80 交 PLAN、glm 0/20。一天就能钉死，比翻两周 diff 快。
- 先别信「是那次 prompt 重构」的直觉：本例最可疑的提交 diff 里没有一行碰该结构块。

## 修法（三档，哪档是产品决定）

1. **治理侧不依赖模型自愿**：升档按可观察信号（题型、证据域数、未覆盖要素）自己判，结构块只是可选加分。
2. **对特定题型把「可以」改成必填**——代价是每题多一轮模型调用，且要验新模型能否稳定产出合规 JSON。
3. **接受该路径在新模型下为零**，把依赖它的功能（本例：子代理工具）明确搁置，别装一个够不着的东西。

## 顺带的纪律

- 换模型是一次**行为迁移**，不是配置改动：换模型当天就该跑一遍「每条依赖模型自愿行为的路径」的频率读数。
- 任何 A/B 若跨了模型切换日，先把这类频率并列写出，否则会把「模型不交 PLAN」读成「新版本 loop 更差/更好」。
