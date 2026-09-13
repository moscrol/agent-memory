---
title: 定价先选"按什么收"再选"怎么收"——七种模型与 value metric
type: knowledge
agent: claude
source: "phuryn/pm-skills（MIT）pm-product-strategy/skills/pricing-strategy/SKILL.md；转述者 Paweł Huryn（Product Compass）。2026-09-13 读取"
date: 2026-09-13
tags: [knowledge, business-model, pricing, saas, general]
status: draft
related: ["[[pricing-structure-selection-criteria]]", "[[van-westendorp-price-sensitivity]]", "[[canvas-selection-bmc-lean-startup]]", "[[foresight]]"]
---

# 定价先选"按什么收"，再选"怎么收"

> 来源：Paweł Huryn（Product Compass）转述，pm-skills 仓。**未验证，按对该来源的信任采纳。**

## 判据

**先定 value metric（计价单位），再定 pricing model（收费形态）。** 顺序反了会得到一个结构漂亮但无法解释的价目表。

**value metric = 你按什么单位收钱**（席位 / 事件数 / 存储 / API 调用 / 报告份数）。判据是：**功能分档要按价值度量切，不要按随便设的额度上限切**——后者客户一眼看得出是人为卡的，会引发对整个定价的不信任。

七种模型与适配场景：

| 模型 | 适合 | 例子 |
|---|---|---|
| Flat-rate 单一价 | 简单产品、成本可预期 | Basecamp |
| Per-seat 按席位 | 协作类、团队产品 | Slack、Figma |
| Usage-based 按用量 | 基础设施、API | AWS、Twilio |
| Tiered 分档 | 用户分层明显 | 多数 SaaS（Free/Pro/Enterprise） |
| Freemium | 有病毒传播或网络效应 | Spotify、Notion |
| Freemium + 用量 | 平台型 | Vercel、OpenAI API |
| Value-based 按价值 | 高影响力的企业工具 | Salesforce、Palantir |

两条配套经验值（**经验量纲，不是规律**）：
- **锚定**：让你最想卖的那一档看起来是"显然的选择"
- **年付折扣典型 15–20%**

## 适用条件（原文语境）

- 软件 / SaaS 产品，且存在一个客户能理解的可计量单位
- 已经知道客户的替代方案是什么、那个方案花多少钱

## 什么时候我不用它

- **计价单位口径说不清时。** 口径不清的分档和加购会变成纠纷来源（[[pricing-structure-selection-criteria]] 已写过这条）。
- **单人交付的定制服务**——此时约束是交付工时不是计价单位，见 [[solo-breakeven-needs-founder-hours-column]]。
- **Freemium 那一行尤其要小心**：它的前提是病毒传播或网络效应。个人数据产品通常没有网络效应，见 [[personal-accumulation-is-not-network-effect]]。

## 与已有判据的关系

[[pricing-structure-selection-criteria]] 解决的是**订阅 / 按次 / 混合**三选一，用四个变量判断。本条是它的**上游**（先定计价单位）和**细化**（七种模型而非三种）。两条不冲突，配合使用。

## 与项目的关系（推测）

对 [[foresight]] 的一条可对照读数：`offer.yaml` 里 199 元/月 与 1999 元/年，折合年付折扣 **16.3%**（199×12=2388，(2388−1999)/2388），落在原文说的 15–20% 典型区间内。
**"典型"不等于"对"**——这只说明定价结构没有偏离行业惯例，不说明这个价格成立。价格成立与否仍需付费样本。

## 参考

- 来源 skill：`pm-product-strategy/skills/pricing-strategy/SKILL.md`（pm-skills，MIT）
- 怎么在没有付费用户时测价：[[van-westendorp-price-sensitivity]]
