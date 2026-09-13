---
title: prompt / 文档层的措辞不能当实现层的保证
type: knowledge
agent: claude
source: 2026-09-13 读 socratic-lens 时，prompt 写「synthQuote 必须逐字、编造会被标红」，补核 lib/fidelity.ts@655b1ec 发现实现远弱于此
date: 2026-09-13
tags: [knowledge, agent-engineering, evidence, code-reading, general]
status: draft
related: ["[[convergence-to-reference-rewards-mimicry]]", "[[independent-convergence-is-stronger-evidence]]"]
---

# prompt / 文档层的措辞不能当实现层的保证

> **性质：`hypothesis`（基于一次实测）。**

## 判据

读一个系统的 prompt、README 或设计文档得到的**约束强度，上限是意图，不是保证**。实现层可能弱得多，而且差距不会写在文档里。

**最常见的差距形态：标记 ≠ 拦截。** 系统"发现"了问题、"标注"了问题，但**下游统计和决策照常放行**。

## 实例（2026-09-13 实测）

`socratic-lens` 的 `fidelity_reconcile.md` 写着：

> `synthQuote` 必须是合成节里**逐字**出现的片段（后续会做逐字校验，编造会被标红）。

读 `lib/fidelity.ts` @ `655b1ec`：

| prompt 说的 | 实现做的 |
|---|---|
| 逐字校验 | `normalizeForMatch`（仅全角→半角标点映射）后 `includes` **子串匹配** |
| 编造会被标红 | 只给渲染层加一句警告文字 |
| （未提及空引文） | `if (!r.synthQuote) return { quoteUnverified: false }`，空串 `needle.length === 0 ? true` → **直接算通过** |
| （未提及统计口径） | `computeCoverage` **完全不读 `quoteUnverified`**——未命中的 `landed` 照样进分子 |

**结论：是软标记，不是硬门禁。** "编造会被标红" 与 "编造无法通过" 是两件事。

## 怎么用

引用一个外部系统的约束当依据之前，问三句：

1. 这条写在 **prompt 里**还是**代码里**？
2. 校验**结果**影响不影响下游统计 / 决策？
3. **缺值**怎么处理——算通过还是算失败？（这一条最容易出事）

三问答不上来，就把该结论标成"意图"，不要当"机制"引用。

## 适用条件

- 读开源项目、读别人的 agent 设计、读供应商文档，并打算**照抄其约束**时
- 尤其当那条约束是你准备拿来当门禁的

## 什么时候我不用它

- 只想学**设计意图**——那 prompt 层就够，不必读实现
- 系统本身就没有实现层（纯 prompt 产品 / 纯 skill）
- 时间成本不允许，且该结论不承重——此时标注"仅读 prompt 未核实现"即可，不必真去读

## 反向自用

自己写的门禁同样适用：**我写的"必须逐字"，脚本真的在逐字查吗？未命中真的会让退出码变 1 吗？**
这正是变异验证要回答的问题——**没被红过的门禁，可能一直在空转。**

## 参考

- 实例：`socratic-lens` `lib/fidelity.ts` / `lib/citations.ts` @ `655b1ecf`
- 同类形状：[[independent-convergence-is-stronger-evidence]] 的失效条件（"独立性"本身也要先核）
