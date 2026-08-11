---
title: 闸门覆盖不了旁路副作用：检查函数的返回值之外，它还写了什么
type: knowledge
agent: devin
source: dao-proxy-pro 会话 2026-08-11（同一形状在四个缺陷里各出现一次）
date: 2026-08-11
tags: [knowledge, methodology, verification, gate, side-effect, core]
status: verified
related: ["[[evidence-hygiene-three-failure-shapes]]", "[[../20_projects/dao-proxy-pro]]"]
---

# 闸门覆盖不了旁路副作用

`evidence-hygiene-three-failure-shapes.md` 形状三说：**一个我没见它失败过的检查，不能信。**
这一条是它的下一层：**一个我见它成功过的检查，也只覆盖它返回值所及的范围。**

## 核心判据

**给一段逻辑加防错闸门时，先问「这段逻辑除了返回值，还写了什么」。**
写在别处的副作用，不受返回值路径上的闸门管辖。

## 三个实例（2026-08-11，dao-proxy-pro）

### 1. `_errorType` 闸门 vs `isError` 旁路

给工具结果做「防投毒」：输出长得像代码就放行（`looksLikeCode`），有运行期信号才记错。
闸门加在 `_errorType()` 的**返回值**上，测试也验了「该放行时放行」。全绿。

但 `isError` 在**上游**独立计算，它写了三个字段：
`lastToolOk`、`consecutiveFailures`、`sameCallFailureStreak`。这三个都不经过闸门。

结果是：`lastError` 干净了，状态栏照旧在说假话——工具成功返回含 `ENOENT` 字面量的
源码时，被记成失败，`strategy` 据此建议「verify path」（方向反了）。

### 2. 消息级断点有门槛，system/tools 断点没有

同一个 4 槽预算，消息级断点做了最小 token 过滤，`system`/`tools` 断点无条件打标。
实测 system 1 token + tools 3 token，模型下限 4096 → 两个必然 no-op 的断点各占一个槽位，
挤掉了真正够大的候选。同池两套判据，只有一套上了闸门。

### 3. 测试判据被自己要测的改动污染

写 `prompt-cache-min-tokens` 测试时，用 `breakpointCount >= 2` 当「消息级断点是否授予」
的代理指标，隐含假设 system 断点总占 1 个。而 system 断点正是本次要加门槛的对象——
判据被被测改动改变的量，报出的失败方向是反的：看着像分档表错了，实际是代理指标错了。

## 处方

1. **审计副作用**：给函数加闸门时，列出它写的**所有**字段/状态，闸门必须覆盖全部，
   或明确标注哪些字段不受保护。测试断言要覆盖被写字段，不是只看返回值。
2. **代理指标要验证正交性**：测试里用「总量」当「分量」的代理时，确认总量不会因被测改动
   而变化。`breakpointCount` 就是反例——它本身就是被测逻辑的输出。
3. **同一资源池的判据要一致**：4 个槽位、同一个门槛，不该一段有过滤一段没有。
   一致性缺失本身就是 bug，且通常藏在「顺手」里。

## 可迁移场景

- 任何「净化/校验/分类」函数（正则、白名单、去重），先找它除了 return 还改了什么
- 测试断言面：只断言返回值 + 不测副作用字段 = 闸门在，旁路敞开
- 仪表/监控数字：读数来自多条写入路径时，一条路径上了闸门不等于全部路径干净
