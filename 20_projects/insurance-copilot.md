---
title: 关系笺 · 保险客户经营助手
type: project
agent: pi
source: 用户搭建请求与本地实现验证（2026-09-18）
date: 2026-09-18
tags: [project, insurance, crm, local-first]
status: active
---

# 关系笺 — 项目入口

## 概述
- 位置：`~/insurance-copilot`，独立于投研仓；入口与存储边界读该仓 `README.md`。
- 用户明确目标：帮助客户分析家庭资产配置，不推销，不将分析当保险销售入口。已有服务底座与可复算的固定虚构报告，正式客户分析引擎未建；状态以应用仓README/交接为准。人工确认、不自动联络。
- 用户确认杭州、高净值目标及本人二级市场经验，关系来源为投资圈与滑雪朋友；自述具备正式展业条件，公司对个人工具/AI的许可仍未确认。详见应用仓定位文档；不将朋友自动标为客户或高净值。
- 客户数据不进入本 vault；这里仅存项目索引。

## 关键决策
- 当前运行形态和边界只维护在项目 README/交接，避免第二份能力清单漂移。

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|---|---|---|---|
| 本地起步版与技能入口 | pi | done | 已加全流程服务事项与交付确认；现状见仓内说明，下一步虚构演练与公司边界确认 |

## 交接记录
- 2026-09-18 · pi · 独立本地工作台与 skill，暂不接模型 → `~/insurance-copilot/docs/handoffs/inflight/feat-local-client-workbench.md`。
- 2026-09-18 · pi · 内地高净值方向与二级市场经验落访谈工作包，保持筹备状态 → `~/insurance-copilot/docs/handoffs/2026-09-18-mainland-family-positioning.md`。
- 2026-09-18 · pi · 并行服务事项、交付确认与旧库安全升级 → `~/insurance-copilot/docs/handoffs/2026-09-18-service-lifecycle.md`；复用判据 [[async-preview-revocation-needs-response-version]]。
- 2026-09-18 · pi · 杭州投资圈/滑雪圈定位与展业自述落文档，不更改数据许可开关 → `~/insurance-copilot/docs/handoffs/2026-09-18-hangzhou-service-positioning.md`。
- 2026-09-18 · pi · 用户纠正为家庭资产配置分析，取代前条的保险服务切入口路线；仅改定位、未增分析模块 → `~/insurance-copilot/docs/handoffs/2026-09-18-household-allocation-correction.md`。
- 2026-09-18 · pi · 固定虚构家庭报告、复算/浏览器检查与空白模板，待用户确认交付价值 → `~/insurance-copilot/docs/handoffs/2026-09-18-household-example.md`。
