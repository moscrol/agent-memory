---
title: 字段错位比缺失更难发现——看着合理的错数
type: knowledge
agent: cursor
source: 2026-08-14 finance-workspace-private fix/tool-observability 实测（traces 成功路上把工具真名藏进 provider、capability 改写成 agent_loop）
date: 2026-08-14
tags: [knowledge, agent, failure-shape, observability, audit, core]
status: verified
related: ["[[contract-vs-delivery-mismatch]]", "[[agent-tool-design-principles]]"]
---

# 字段错位比缺失更难发现

> **失败形状**：同一事实在不同代码路径写进**不同字段**。缺失会露出 `None`；
> 错位会给你一个**看着合理的错数**。

这是 [[contract-vs-delivery-mismatch]] 的近亲，但诊断入口不同：
契约不符问的是「承诺 vs 交付」；本条问的是「你按哪个字段分组」。

## 实例（2026-08-14 实测）

问「某个工具成功率多少」，三个源各瞎一半：

| 源 | 看起来有 | 实际 |
|---|---|---|
| `metrics.tool_calls` | 有调用次数 | 只有总数，没有按工具名 |
| 事件流 | 有 `tool_request` / `tool_result` | 整条分支路径一条事件都不发 |
| `traces` | 每条都有 `capability` / `provider` | 成功路上把工具真名藏进 `provider`，把 `capability` 改写成 `agent_loop` |

按 `capability` 分组：成功全被扫进 `agent_loop`，工具自身错误率看起来接近 0。
数字自洽、没有 `None`、没有红灯——错的是分组键。

先断言「events 被截断」被证伪（sequence 连续 1..N）；
再断言「错误率算不出来」也被证伪（traces 里有，只是写错栏）。

## 四个让它难被发现的性质

1. **有数比没数更危险**——缺失会逼你换源；错位让你用错的数做决策
2. **分组键是隐式契约**——没人写「成功率按 capability 聚合」，但审计脚本默认这么干
3. **成功路径与失败路径写入不一致**——失败时真名还在 capability，成功时被改写。按路径抽样会得到互相矛盾的「正常」
4. **量具同盲**——手搓五遍的临时脚本如果复制了同一套字段映射，五次都会读出同一个错数

## 修法（可带走）

- **单一归一化口径**，运行时与审计脚本共用同一个函数，不另立第二份映射。
  本轮是 `provider_observability.provider_trace_tool_name()`，
  `scripts/audit_episode_tool_outcomes.py` 读它，不自己猜。
- 审计脚本归位成 0 档只读工具，不要留在 `tmp/` 循环里——下一轮排查还会手搓，还会再踩同一套错位。
- 发现「某个仪表读数为 0 / 100%」时，先问：**这是真的没有，还是写进了另一栏？**
  对照同一事实在失败路径上的字段；两条路径不一致就是本条，不是「偶发空值」。

## 不覆盖什么

- 字段**缺失**（那是契约不符 / fail-open 的亲戚，会露出 `None`）
- 事件根本没埋点（本轮分支路径属于这一类，修法是补事件，不是换分组键）
