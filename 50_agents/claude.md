---
title: Claude 接入约定卡
type: agent-card
agent: claude
source: 设计约定；2026-08-12 按实际用法重写（旧卡还写着「备用、使用较少」，与 [[../30_conventions/agent-division]] 的核心定位矛盾）
date: 2026-08-12
tags: [agent-card, claude]
related: ["[[claude-hooks]]", "[[../30_conventions/agent-division]]"]
---

# Claude / Claude Code — 学习型实现（核心开发节点）

## 角色
用户要**亲手学**的核心开发由 Claude 承担并**边做边讲**：RAG/检索、前端、重构（见 [[../30_conventions/agent-division]]——想学会的用会讲解的亲自做，只想搞定的丢给 Devin）。也承担长文写作、代码审阅、`00_inbox/` → `10_knowledge/` 的整理提炼。

## 读
- 本机直跑 repo，经软链 `.agent-memory/` 直读 vault；SessionStart hook 每次开窗自动注入偏好 + 项目笔记（见 [[claude-hooks]]），不依赖模型主动开文件。
- 需要历史结论时查 `10_knowledge/`，回答「有没有 X」先读能力图谱。

## 写
- 遵守通用规则：frontmatter + 模板 + 正确目录；改动后跑 `python3 scripts/vault_lint.py`。
- 完工按 [[../40_playbooks/devin-writeback]] 分层沉淀；Stop hook 会在有代码/配置改动却没做沉淀判断时拦截（见 [[claude-hooks]]）。
- 会话中产生可迁移的科普讲解 → 收尾走 `tutor` skill，人审批准后才进 `70_tutor/`。

## 接入方式
- Claude Code：在 repo 目录启动（hook 是项目级，home 目录起会话不触发），`CLAUDE.md` + SessionStart hook 双保险加载偏好。
- 网页端 / Project：把 `30_conventions/` 和相关笔记作为 Project 知识上传，回写手动落库。
