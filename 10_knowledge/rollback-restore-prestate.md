---
title: 回滚恢复操作前状态
type: knowledge
agent: codex
source: finance 工作区发布助手隔离故障注入，2026-10-03
date: 2026-10-03
status: verified
tags: [rollback, deployment, state]
---

回滚目标应来自操作前快照，不能只取中途成功动作的列表。

实证：四个已加载服务依次停止，第二个停止失败；异常清理再停止全部服务，如果只重启“此前成功停止”的列表，就只恢复第一个，剩余三个掉线。改用切换前完整 loaded 集合，四个初始失败位置均恢复四个服务，旧选择策略的负对照仍能检出缺陷。

同理，原子文件替换失败须清理暂存软链，否则回滚可能先被自己的残留挡住。状态快照、清理和恢复分别留证，不因捕获原异常就宣称回滚成功。

适用于服务切换、批量配置替换和多步资源更新。此次验证用临时文件与替身命令，没有证明操作系统真实故障、双重恢复故障或任意部署器的可靠性。复现收据在金融项目私有 `workspace-global-closeout-1003/cutover-rollback-final-verification.json`，正式交接为 `docs/handoffs/2026-10-03-workspace-global-closeout.md`。
