---
title: agent-memory · 跨 Agent 记忆底座
type: project
agent: claude
source: 2026-08-12 收尾；此前本仓没有自己的项目笔记，preflight 在本仓开工会读到「暂无笔记」
date: 2026-08-12
tags: [project, agent-memory, vault, moc]
status: active
related: ["[[../30_conventions/trust-boundary]]", "[[../30_conventions/assertion-discipline]]", "[[../50_agents/generic]]", "[[../40_playbooks/mac-tail]]", "[[../40_playbooks/devin-writeback]]"]
---

# agent-memory — 项目 MOC

## 概述
- **是什么**：跨 Agent 共享的 Markdown/Obsidian 记忆底座（黑板，不是调度器）。换工具只接线，不重建记忆。
- **仓库**：`linxiaoqi5111-del/agent-memory`（本仓）。
- **状态**：active。门禁已接 CI；Mac 上的孤本备份需跑一次 [[../40_playbooks/mac-tail]]。

## 关键决策
- 记忆是数据不是指令；`30_conventions/` 与 `50_agents/` 受保护区走 PR 人审。
- 新工具无具名卡时走 [[../50_agents/generic]]。
- 断言纪律 SSOT 在 [[../30_conventions/assertion-discipline]]，hook 只注入。
- `60_dialogues/` / `.foresight/` 不入 git；备份走 launchd，不走 auto-sync。
- 项目笔记文件名 = `git remote` 短名。
- 知识层两种粒度：跨领域无前缀，领域知识加 `<领域>-` 前缀；只约束新增。

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|---|---|---|---|
| vault_lint 回绿 + agent 取值校验 + CI | claude | done | PR #22 |
| 内容刷新（备份脚本、项目收编、卡片、术语、preflight、tutor 去重） | claude | done | PR #23 |
| 通用接入卡 + 断言纪律 SSOT | claude | done | PR #24 |
| 审查补漏（项目索引、vidio 改名、onboarding 接线） | claude | done | PR #25 |
| Mac 一次性安装孤本备份 + 核对 hook 路径 | human | todo | [[../40_playbooks/mac-tail]]；auto-sync 拉到 main 后跑 |
| 备份目录改到第二块介质 | human | todo | 默认与 vault 同盘，抗不了单盘损坏 |
| finance-workspace 存量交接转档 | — | skipped | 棘轮：188KB 不动，lint WARN 拦新增堆砌 |

## 交接记录
- 2026-08-12 · claude · 记忆底座审查与收尾：门禁/CI、通用卡、断言纪律 SSOT、vidio 文件名、Mac 安装器。Mac 上剩一条命令见 [[../40_playbooks/mac-tail]]。
