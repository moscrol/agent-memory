---
title: OPC 任务看板（监工 SSOT）
type: project
date: 2026-09-21
tags: [opc, foreman, task-board]
---

# OPC 任务看板

## SSOT
- 机器可读：`board.json`（程序只改这个）
- 人看：`BOARD.md`（由 board.json 生成，勿手改当真相）
- 运行态（不进 git）：`~/.finance-runtime/supervisor/`（last-nudge、STOP 等）

## 角色
- **总管（Bot）**：写入任务、改派 `owner` / `session`、定 `goal` / `next`
- **监工 Bot**：巡检；可改 `status` / `block` / `updated_at`；仅对真停的 `doing` 在**原会话**发固定催促句

## 催促
- 原文仅：`按最佳方案继续推进`
- 压缩中 ≠ 停；多日僵尸 tab 默认忽略；不新开窗、不群发

## 字段
见 `board.json` 内 tasks[] 元素：
`id` `title` `status`(`todo|doing|blocked|done`) `owner` `session` `goal` `next` `block` `needs_you` `updated_at`
