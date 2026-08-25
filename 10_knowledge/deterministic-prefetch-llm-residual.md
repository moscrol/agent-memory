---
title: 组件写正文、模型只写边注（确定性预取 + LLM 残差）
type: knowledge
agent: grok
source: finance-workspace-private 核稿 2026-08-25（板块公告扫描 spec v1.1；对照盘面包 component-first）
date: 2026-08-25
tags: [knowledge, methodology, agent-runtime, grounding, fail-closed, core]
status: verified
related: ["[[finance-agent-capability-graph]]", "[[../20_projects/finance-workspace-private]]", "[[fast-path-must-not-mint-authority]]"]
---

# 组件写正文、模型只写边注

常规 RAG 是「检索喂上下文、模型写全文」。名单 / 对账 / 覆盖率这类题，分工应反过来：**可判定部分从生成里整个拿走**——组件写正文，模型只写边注。幻觉面收窄到残差；残差关了，正文仍在。

## 对照

| | RAG 默认 | 本模式 |
|---|---|---|
| 谁写名单/对账表 | 模型（从检索片段拼） | 确定性组件（SQL / 扫描器 / 规则分层） |
| 模型的座位 | 全文作者 | 边注：例外、双重性、标题缺字段 |
| 裁判怎么守名单 | 给每行发「免检证件」让裁判认识它（深耦合） | **合并放在裁判之后**（浅耦合，删句删不到包渲染） |
| 失败形状 | 模型胡编一行代码；或裁判把整段削成空壳 | 组件 `empty` / `partial` 带收据；界面必须亮缺口灯 |

## 适用 / 不适用

适用：输出形状是「列出哪些 X 满足谓词 P」，P 可用规则或查询表达（板块公告名单、双红成分股、仓库里哪些文件缺 license 头、测试哪些 case 没跑）。

不适用：P 本身是判断（「还能不能追」「冲击有多大」）——那是残差或研究 owner 的活，组件只提供已绑定的格子。

## 和「快路径不得产权威」的关系

[[fast-path-must-not-mint-authority]] 说的是：便宜路径只能加速权威答案，不能自己宣布结论。本模式不矛盾——**扫描包就是权威口径**（名单的真源），模型才是便宜边注。不要把模型草稿当成名单权威、再让组件去「加速」它。

## 预算

组件若第一次把网络 IO 放进「盘面包那种同步绑定座位」，分页上限、墙钟、`partial`（已得行 + 缺口灯）必须是一等公民。本地 DuckDB 毫秒级的座位，原样接外呼会把整个 turn 吃光。

## 来源

`finance-workspace-private/docs/superpowers/specs/2026-08-25-sector-disclosure-scan-design.md` v1.1；座位对照 `2026-08-24-market-watch-component-first-design.md`。
