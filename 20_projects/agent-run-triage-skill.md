---
title: agent-run-triage-skill · Agent Skill 库（分诊 + Matt Pocock 适配组）
type: project
agent: claude
source: https://github.com/linxiaoqi5111-del/agent-run-triage-skill （PR #3 适配交付；本笔记由黑板 e2e 补测创建）
date: 2026-08-13
tags: [project, skill, agent-run-triage, matt-pocock]
status: active
---

# agent-run-triage-skill — 项目 MOC

## 概述
- **目标**：canonical skill 库。自研 `agent-run-triage`（trace-first 事后分诊）+ Matt Pocock 28 个 skill 中 27 个的项目适配版（黑板接线、中文教学模式、验收链注入）。
- **状态**：active
- **负责 Agent**：claude（改造与 SSOT）；devin（B/C 组行为冒烟）；grok（路由/确认轮探针）；human（本机安装）
- **SSOT**：仓内 `skills/`；各 harness 安装路径只放 symlink（Mac 实装源：`/Users/a77/projects/agent-run-triage-skill`，分支 `cursor/adapt-matt-pocock-skills-f164`）。

## 关键决策
- 上游 `triage` 改名 `issue-triage`，与既有 `agent-run-triage` 互斥路由表双向消歧。
- tracker 三模式（GitHub / 黑板看板 / 本地 `.scratch/`）；spec/plan 落仓内 `docs/superpowers/`，看板行落本 MOC。
- `scaffold-exercises` 按决策不装。

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|---|---|---|---|
| 01 Mac 本机 symlink 安装 + guardrails hook | human | done | 2026-08-13 经远程隧道实做：28 skill × 3 harness 全 symlink，sha256 一致；hook 两向 12/12+12/12；plan 见仓内 docs/superpowers/plans/2026-08-12-matt-pocock-skills-adaptation.md |
| 02 to-tickets 确认轮补测 | grok | todo | 模拟用户改拆分后重编号发布 |
| 03 黑板看板 e2e（写 vault + vault_lint） | claude | doing | 本 MOC 即其产物；lint 通过后置 done |
| 04 ask-matt 路由补测 | grok | todo | 含「先路由 agent 再路由 skill」 |
| 05 B 组代表路径（grilling/handoff/claude-handoff） | devin | todo | |
| 06 其余 B 组沙盒断言 | devin | todo | /tmp 沙盒，不留仓内产物 |
| 07 C 组适用范围门 | devin | todo | 本仓拒装，JS/TS 沙盒可走前半段 |

## 相关知识
- 仓内设计文档：`docs/superpowers/specs/2026-08-12-matt-pocock-skills-adaptation-design.md`
- 验收记录：`docs/superpowers/acceptance/matt-pocock-skills/behavioral-tests.md`

## 交接记录（谁做了什么）
- 2026-08-13 · claude · Mac 实装 28 skill symlink + guardrails hook 两向验证；创建本 MOC 落 7 张票看板 · 指向仓内 docs/superpowers/plans/2026-08-12-matt-pocock-skills-adaptation.md
