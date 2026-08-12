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
| 02 to-tickets 确认轮补测 | grok | done | 2026-08-13 模拟用户 3 票并拆为 2 票重编号发布，FIELDS_RC=0（T9） |
| 03 黑板看板 e2e（写 vault + vault_lint） | claude | done | 2026-08-13 lint 全绿（182 文件 0 错 0 警）；本 MOC 即其产物 |
| 04 ask-matt 路由补测 | grok | done | 2026-08-13 ROUTE_SCORE 6/6，先 agent 后 skill，无旧名 /triage（T10） |
| 05 B 组代表路径（grilling/handoff/claude-handoff） | devin | done | 2026-08-13 三条全 PASS（T11） |
| 06 其余 B 组沙盒断言 | devin | done | 2026-08-13 七条 [实测] 全 PASS，仓内零残留（T12） |
| 07 C 组适用范围门 | devin | done | 2026-08-13 本仓三拒装 + 沙盒前半段可走（T13）；finhot 真仓后半段未做 |

## 相关知识
- 仓内设计文档：`docs/superpowers/specs/2026-08-12-matt-pocock-skills-adaptation-design.md`
- 验收记录：`docs/superpowers/acceptance/matt-pocock-skills/behavioral-tests.md`

## 交接记录（谁做了什么）
- 2026-08-13 · claude · Mac 实装 28 skill symlink + guardrails hook 两向验证；创建本 MOC 落 7 张票看板 · 指向仓内 docs/superpowers/plans/2026-08-12-matt-pocock-skills-adaptation.md
- 2026-08-13 · claude · plan 7 票全部执行完毕（Mac 实做 01/03，fresh 子 agent 冒烟 02/04–07 全 PASS，T7–T14）；28 skill 全部有行为证据 · 指向仓内 docs/superpowers/acceptance/matt-pocock-skills/behavioral-tests.md
- 2026-08-13 · claude · 与 harness-reference 接线（不合仓）：skill 仓 TOOLKIT 空指针改为 canonical+vault fallback；KIT/BUILD/TOOLKIT 回指本仓 skills/ · 指向 harness-reference commit 14ad10e 与 skill 仓 5678703
- 2026-08-13 · claude · 适配收录 khazix leader（哑巴执行者任务书，默认落盘 goal-brief 不绑 /goal）并自审压 3 条超 250 字 description；Mac 三 harness 已链 symlink · 指向 PR #4（cursor/adapt-leader-skill-f164，base=Matt 适配分支）
