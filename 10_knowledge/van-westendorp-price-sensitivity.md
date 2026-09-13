---
title: Van Westendorp 四问——没有付费样本时怎么测价格区间
type: knowledge
agent: claude
source: "phuryn/pm-skills（MIT）pm-product-strategy/skills/pricing-strategy/SKILL.md 第 5 步；转述者 Paweł Huryn。原始方法：Peter van Westendorp 价格敏感度测量表（PSM）。2026-09-13 读取"
date: 2026-09-13
tags: [knowledge, business-model, pricing, research, method, general]
status: draft
related: ["[[pricing-structure-selection-criteria]]", "[[pricing-models-and-value-metric]]", "[[foresight]]"]
---

# Van Westendorp 四问

> 来源：Paweł Huryn 转述（pm-skills 仓），原始方法是 Peter van Westendorp 的价格敏感度测量表（PSM，行业标准方法）。**未验证，按对该来源的信任采纳。**

## 判据

还没有付费用户时，**价格区间可以问出来**，不必等到有人真的掏钱。问四个问题（都问"多少钱"，不是"你愿不愿意"）：

| # | 问法 | 在测什么 |
|---|---|---|
| 1 | 低到什么价格，你会开始怀疑它的质量？ | 质量下界 |
| 2 | 什么价格你觉得便宜、划算？ | 划算点 |
| 3 | 什么价格你会开始犹豫，但还是会考虑？ | 犹豫点 |
| 4 | 高到什么价格，你肯定不会买？ | 上界 |

四条累计曲线的交点，给出一个可接受价格区间。

**为什么这四问有效**：它们都在问**数字**，不在问**意愿**。"你会买吗"人人说会；"多少钱你肯定不买"逼对方给出一个具体的数。

## 适用条件（原文语境）

- 有一批能访谈或能发问卷的目标用户
- 对方**已经理解产品价值**（讲不清价值时，四个数字都是瞎猜）
- 原文把它列在"有调研数据时用"，没有数据时退回按竞品价格与交付价值估算

## 什么时候我不用它

- **样本是个位数时**：只能当定性参考，画不出曲线。四五个人的交点没有统计意义。
- **对方从没用过同类产品**：他没有价格锚，给出的数字反映的是他的收入水平，不是这个产品的价值。
- **访谈本轮明令不谈钱时**——见下。

## 与已有判据的关系

[[pricing-structure-selection-criteria]] 的失效条件写着"**没有付费样本时，这套判据只能生成假设**……应先做小规模付费测试"，但没说怎么测。**本条就是那个"怎么测"的一个具体方法**——虽然它测的是意向价格，仍不等于真实付费。

## 与项目的关系（推测）

对 [[foresight]] 有一条硬约束：招募稿的话术纪律写死了「**不介绍价格、这一小时不涉及任何收费**」。所以**这四问不能塞进第一轮用户研究访谈**——塞进去会破坏那一轮"不是销售"的承诺，也会污染对方对痛点的回答。

可行的做法是分轮：第一轮只问现状与痛点（现有 14 题），价格四问留到 Alpha 体验之后单独一轮，那时对方已经理解价值，也符合本条的适用条件。

## 参考

- 来源 skill：`pm-product-strategy/skills/pricing-strategy/SKILL.md` 第 5 步（pm-skills，MIT）
- 同批沉淀：[[pricing-models-and-value-metric]]、[[canvas-selection-bmc-lean-startup]]
