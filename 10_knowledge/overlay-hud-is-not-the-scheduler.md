---
title: 旁路 HUD 不是调度器：先问工具表 / 配置 / 二进制名
type: knowledge
agent: devin
source: 2026-08-22 Devin.app 二进制 + 官方 subagents.mdx + dao acp_augment.js（Windows「强调度」HUD 对照）
date: 2026-08-22
tags: [knowledge, methodology, harness, scheduler, verification, core]
status: verified
related: ["[[evidence-hygiene-three-failure-shapes]]", "[[../20_projects/dao-proxy-pro]]"]
---

# 旁路 HUD 不是调度器

换 Cursor / Claude Code / Windsurf / Devin，这条都成立：**叠在 IDE 上的调度面板，默认不是调度器。** 它多半在数自己的数、注入自己的提示词。

## 结论

Agent「调度」有三档，越往下越硬：

| 档 | 是什么 | 改它靠什么 | 旁路 HUD 通常停在哪 |
|---|---|---|---|
| 1 策略 | `AGENTS.md` / 规则劝模型怎么派活 | 写文件进 context | 几乎都在这里 |
| 2 工具面 | schema 里有没有 `run_subagent` 这类入口 | 官方开关 / 自定义 profile | 声称「打通」时常没注册 |
| 3 路由器 | 说话前由谁选定模型（如 Cognition `AssignModel`） | 云端 RPC / 官方 model picker | 本地叠层碰不到 |

**HUD 上的 spawn 计数不是证据。** 工具没进 schema，那些数字是旁路自己划的。

## 三句证伪（动手前先问）

1. **工具表**：这次会话的 tool schema 里有没有那个派发工具？没有 → 不是官方 spawn。
2. **配置**：`model_config.json` / `subagents_enabled` / 官方 agents 目录改了没有？没改却说「接管调度」→ 假。
3. **二进制/RPC 名**：产品二进制或云端 RPC 里有没有 HUD 发明的 profile 名（`explorer-max`、某 harness 词）？0 hit → 那是叠层自己的词表。

人话：门口贴了「后厨三人流水线」告示，厨房排班系统没改。告示板上的「已派 43 单」是门口自己数的。

## 处方

- 真要改派发：走产品开门的入口（Devin 是 `%APPDATA%\devin\agents\*.md` + `run_subagent` 的 **profile** 参数，prompt 里点名模型无效）。
- 自定义档案不要撞内置名，撞了会被 skip。
- 改上游模型（网关/BYOK）是「谁说话」，不是「谁被派」。两件事正交。
- Dao ACP 中间人明文不改写工具调用/权限；`strawberry-pancake` 是 Cascade **harnessUid** 盖章，不是 Devin 调度器。

## 失败形状

把「对齐了某 harness 词 / 注入了 AGENTS.md / HUD 绿灯」读成「调度内核已替换」。这和 [[evidence-hygiene-three-failure-shapes]] 的「计数不是证据」同一类：看起来合理，但实验能当场证伪。
