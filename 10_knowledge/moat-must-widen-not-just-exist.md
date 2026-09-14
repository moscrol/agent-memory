---
title: 护城河要变宽，不能只是存在（它是导数，不是状态）
type: knowledge
stance: ai-distilled
agent: claude
source: 巴菲特致股东信反复表述的经理人考核标准——不看护城河在不在，看这一年它是变宽了还是变窄了。2026-09-14 整理，增量在**每条护城河绑一个可读数的量**与季度比较动作
date: 2026-09-14
tags: [knowledge, business-model, buffett, moat, first-principles, general]
status: draft
related: ["[[entry-ticket-is-not-a-moat]]", "[[three-sources-of-positive-feedback]]", "[[pricing-power-test-raise-ten-percent]]", "[[invert-ask-how-it-dies]]", "[[foresight]]"]
---

# 护城河要变宽，不能只是存在

## 判据

**护城河不是"有 / 没有"的状态量，是"这季度比上季度宽还是窄"的导数量。**

库里已有三条都在回答"存不存在"：

- [[entry-ticket-is-not-a-moat]]——它是入场券还是壁垒
- [[three-sources-of-positive-feedback]]——是哪一种正反馈
- [[pricing-power-test-raise-ten-percent]]——定价权在不在

**没有一条在问方向。** 而**一条真实存在、但每季度都在变窄的护城河，比没有护城河更危险**——因为每次体检它都显示"有"，你不会去管它。

## 怎么把它变成能读的数

规则：**每条护城河绑一个量，而且要挑那个"你不作为就会下降"的量。**

| 正反馈类型 | 宽度读数 | 不作为时 |
|---|---|---|
| 网络效应 | 用户之间的互相触达次数 | 停滞，但不倒退 |
| 规模经济 | 单位成本 | 不倒退（成本不会自己涨回去）|
| 学习曲线 | **沉淀被调用的次数**（不是沉淀的条数）| **会倒退** |

**学习曲线那栏是唯一"不作为就变窄"的**，因为它的成立条件里有一条要主动维持：*下一次真的调用了它*（见 [[three-sources-of-positive-feedback]]「学习曲线最容易被高估」）。

**这也是为什么读数必须是"调用次数"而不是"沉淀条数"。** 条数只会涨，是个永远好看的数；库在涨而调用不涨，等于**每条沉淀的平均价值在跌**——护城河在变窄，而计量方式让它看起来在变宽。

## 季度动作（一句话）

> **这条护城河比上季度宽了还是窄了？**

说不出方向 = 没有在测 = **默认按变窄处理**。

## 适用条件

- 已经确认护城河存在之后（先过 [[entry-ticket-is-not-a-moat]] 的三问）
- 季度复盘、决定资源往哪投、判断某项投入该不该继续

## 什么时候我不用它

- 还没验证有人要 → 没有护城河可谈，为时过早
- **只有一个季度的读数** → 看趋势不看单点，连续两季同向才算方向
- **不要为读数优化读数** —— 调用次数能靠无意义调用刷高。读数是代理变量，一旦和它要代表的东西脱钩就该换掉（Goodhart 对本条自身同样适用）
- 生意本来不靠正反馈（项目制、咨询、一次性交付）→ 宽度无意义，该测的是别的

## 与项目的关系（推测）

[[three-sources-of-positive-feedback]] 已判定 [[foresight]] 三条里只剩一条：网络效应不成立（数据不共享），规模经济几乎无效（推理成本本来就只有 0.34 元/次）。

**所以 Foresight 护城河的宽度 ≈ 沉淀被调用的频率，没有第二个量。**

已有的实测读数（[实测]，来源：`agent-memory/scripts/recall.sh` 头部注释与 `venture-ops/README.md`）：

> **2026-09-13：单日入库 17 条判据，全程被调用 1 次。**

按上表判定：**那一天护城河在变窄**——库涨了 17，调用涨了 1。

2026-09-14 建 `scripts/recall.sh` 并挂上用户级 SessionStart hook，是一次**加宽动作**：它把"调用"从靠记性改成了靠机制。这正是上面「不作为就会倒退」的对策。

**下个季度该读的数**：`recall.sh 实际调用次数 / 同期新入库条数`。这个比值持续 < 1 且在下降 = 在变窄，**不管库里累计到了多少条。**

## 参考

- 存不存在：[[entry-ticket-is-not-a-moat]]
- 是哪一种：[[three-sources-of-positive-feedback]]
- 实物形态：[[pricing-power-test-raise-ten-percent]]
- 同批沉淀：[[invert-ask-how-it-dies]]
