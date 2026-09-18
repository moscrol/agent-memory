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
- 目标：客户记录、沟通与承诺维护、带来源资料、人工确认的 Copilot 准备；不自动联络。
- 业务地区与公司许可未确认；现版是无模型外呼的单人本地起步版，不是友邦官方系统。
- 客户数据不进入本 vault；这里仅存项目索引。

## 关键决策
- 当前运行形态和边界只维护在项目 README/交接，避免第二份能力清单漂移。

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|---|---|---|---|
| 本地起步版与技能入口 | pi | done | 下一步是业务地区/公司规则确认与用户演练；工程通过不代表合规验收 |

## 交接记录
- 2026-09-18 · pi · 独立本地工作台与 skill，暂不接模型 → `~/insurance-copilot/docs/handoffs/inflight/feat-local-client-workbench.md`。
