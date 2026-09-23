---
title: 工具依赖必须跨响应约束，工具注册必须验证实际菜单
type: knowledge
agent: all
source: PR868 pi 审查工装修复 324a76f9a；真实 CLI + 本地假服务定向验证
date: 2026-09-23
tags: [agent, tools, protocol, testing]
status: verified
related: ["[[evidence-hygiene-three-failure-shapes]]"]
---

# 工具依赖必须跨响应约束

模型同一响应里的多次工具调用，其参数通常在任何一个工具结果返回前就已生成。把 read、write 按顺序执行，不会让 write 的既有参数自动引用新返回的读取内容。提示词顺序也不是依赖约束。

## 可执行做法

1. 把协议写成状态机：本轮只开放 read，成功结果返回后才在下一轮开放 write，再验证实际落盘后开放终稿。
2. 同时检查整轮调用和工具执行：同批多工具、错误工具、重复调用、跨阶段调用，在副作用前拒绝。只设置 `parallel_tool_calls=false` 不作为唯一保护。
3. 保存请求发出时的阶段，不能只看工具执行时已经推进的当前阶段，否则同批后续调用会借前一个工具结果越过门禁。
4. 在真正 CLI/SDK 初始化后读取实际工具集合。注册表里有工具，不意味着它没有被命令行允许名单过滤。
5. 前置协议拒绝先于外发请求记账。预占、拒绝、实际发出、服务端完成应分开表达，不把尝试补救但本地拦截的调用计为已外发。

## 验证方式

真实 CLI 接脚本化本地 HTTP 假服务，检查菜单、事件顺序、文件副作用、终止后的请求数。至少构造同轮读写、先写、猜测副本、读取失败、提前终稿、遗漏提交工具等反例。

这是工具协议证据，不是模型遵从性或最终内容质量证据。合成 PASS/STAGE_COMPLETE 不可拿到真实审查里做准入收据。封存批次修复应生成新输入，不回改原件。

一手实例：`~/finance-worktrees/adaptive-research-loop/scripts/review_probes/pi_review_protocol.mjs`、`tests/test_pi_review_repair.py`；收据见 `docs/verification/2026-09-23-pi-review-protocol-repair/`，固定代码提交 `324a76f9a`，pi 0.85.1。本结论只外推失败形状和验证方法，不保证其他 SDK 具有同样的事件时序。
