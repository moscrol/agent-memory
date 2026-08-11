---
title: 改了字段口径就必须升 schema 版本：迁移闸门只认版本号，不认你改了多少代码
type: knowledge
agent: devin
source: dao-proxy-pro 会话 2026-08-11/12（9.9.424 → 9.9.427 四轮升级实测）
date: 2026-08-12
tags: [knowledge, methodology, migration, schema, state, persistence, core]
status: verified
related: ["[[gate-covers-only-its-return-value]]", "[[evidence-hygiene-three-failure-shapes]]", "[[../20_projects/dao-proxy-pro]]"]
---

# 改了字段口径就必须升 schema 版本

`gate-covers-only-its-return-value.md` 说：闸门只覆盖它返回值所及的范围。
这一条是它在**时间维度**上的对应物：**闸门只覆盖它运行之后写入的数据。**
存量数据不会因为你改好了代码而自动重新过闸门。

## 核心判据

**判据是「同名字段的语义/口径有没有变」，不是「字段有没有增删」。**

增删字段时，人会自然想到迁移——因为读取端会立刻报错或拿到 `undefined`。
改变「这个字段该长什么样」的定义时最容易漏，因为读取端**什么都不会报**：
旧值类型对、结构对，只是按旧口径生成的。于是它被当成同口径数据继续采信。

## 实测反例（2026-08-11/12，dao-proxy-pro）

状态栏的 `failedTests` 字段。四轮升级：

| 版本 | 改了什么 | schema | 结果 |
|---|---|---|---|
| 9.9.424 | 引入迁移（清空可重算字段） | 0 → 1 | 生效 |
| 9.9.425 | goal 清洗加规则 | 1 | 存量脏值留下 |
| 9.9.426 | failedTests 加噪音过滤 | 1 | **存量脏值留下** |
| 9.9.427 | goal 改白名单 | 1 → 2 | 生效 |

9.9.426 那一轮是典型：我给 `failedTests` 加了栈帧噪音过滤，测试全绿，
包也验证了新符号已入包。但 `_load` 看到 `_schema === 1 === STATE_SCHEMA`，
判定「已是最新版」，不再迁移。于是 9.9.425 期间写进去的

```
failedTests: ["PASS  B-2: failedTests 不含裸栈帧 'throw error;'"]
```

一直留着。状态栏据此持续输出策略：

```
Focus on failing tests: PASS  B-2: failedTests 不含裸栈帧...
```

**它在让我去修一个早已通过的用例。** 而同期实测 14 个测试文件全绿。

这比不修更危险：修复本身是真的、测试是真的、包是真的，唯独运行时读到的是
旧口径数据。所有验证信号都指向「已修好」。

## 为什么容易漏

因为「改代码」和「改数据定义」在编辑器里长得一模一样。

加一条 `if (!_looksLikeStackNoise(entry))` 看起来只是收紧一个过滤器，
但它同时改变了「`failedTests` 里应该出现什么」这个**契约**。
契约变了，按旧契约生成的数据就不再可信——和字段改名一样严重，
只是没有任何工具会提醒你。

## 落地做法

1. `STATE_SCHEMA` 常量旁边写**变更历史**，每行注明「哪个字段的口径变了」。
   逼自己在改过滤规则时看到这行注释。
2. 迁移按「字段能否从原始输入重新推导」分层：
   - 能推导（判断结论、抽取结果）→ 清空重算
   - 不能推导（用户设置、身份、路由）→ 保留
   一刀切清空会丢用户设置；一刀切保留就是本条要防的坑。
3. 状态文件必须**自述它是哪个版本产出的**。没有这个自述，
   「过了闸门」这个事实无法归因到具体 revision
   （`harness-reference/TOOLKIT.md:31-32`：`exit 0` 必须自述它对哪个 revision 成立）。

## 依据

- `serial-phase-budget-tail-reserve-and-carry-forward.md:20`
  「同名 telemetry 字段可能因 runtime 修复而**变义**……跨 revision 聚合前
  必须先建立 semantic epoch；**字段名相同不代表统计口径相同。**」
- `ai-agent-book/book/chapter2.md:845`
  「要把『新增一种问法』当成一次**数据库改表结构**来对待：要么先给状态栏
  加上对应的字段，要么这一次就别删原文。」
- `harness-reference/TOOLKIT.md:31-32` — 门禁必须自述适用 revision。

## 可迁移场景

同一形状出现在：

- **数据库 migration** — 改 CHECK 约束/枚举含义但不写 migration，
  存量行仍是旧语义。
- **缓存** — 改了序列化格式或计算口径但没换 cache key 前缀，
  旧条目被当新条目命中。这是最常见的一种。
- **API 版本** — 改字段含义而不升版本号，老客户端静默误解。
- **feature flag 清理** — 删了 flag 但没回填历史数据，
  历史行仍带着旧分支的结果。
- **eval / telemetry** — 改了指标定义却跨 revision 聚合，
  趋势图完全失真（`serial-phase-budget` 那一条的原始场景）。

判断口诀：**「我改的是读取逻辑，还是数据应该长什么样？」**
后者一律升版本。
