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
- 目标：承载全流程长期客户服务与未尽责任，辅助准备交付物；人工确认、不自动联络。
- 用户确认中国内地、高净值目标人群及本人二级市场经验；公司许可未确认。现版无模型外呼、单人本地，不是友邦官方系统。
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
