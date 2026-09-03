---
title: 一票否决不折进连续分——否决是阶跃函数，会把二值判断的抖动放大成分数抖动
type: knowledge
agent: cursor
source: finance-workspace-private 2026-08-31 rubric v2→v3 方差实测（commit 10018c3c，收据 ~/.finance-runtime/rubric-variance-ab.json）+ 2026-09-03 弃权率一等读数（docs/verification/2026-09-03-abstain-rate-baseline-offline.md）
date: 2026-09-03
tags: [knowledge, eval, llm-judge, ablation, failure-shape, methodology, core]
status: verified
related: ["[[eval-harness-variance-governance]]", "[[misaligned-field-looks-plausible]]", "[[../20_projects/finance-workspace-private]]"]
---

# 一票否决不折进连续分

> **失败形状**：把一个二值判定（编造 / 弃权 / 违规）写成「触发即该维判 0」或
> 「触发即总分归零」，塞进喂给 A/B 分差的连续分里。否决是阶跃函数——判定器对
> 「算不算」摇摆时，分数跟着整段跳；一票的抖动被放大成 4 分、6 分的极差，
> 方差反而比没加否决时更大，A/B 分差读的是判官的犹豫，不是两臂的差别。

书里 rubric 支持 Veto（ch6 准则 ③），但那是用在**安全违规的通过 / 失败决定**上（零容忍），
不是用在喂进 A/B 分差的连续分上。两者混在一起就是本条。

## 实例 1（2026-08-31，rubric v2 被自己的实测证伪）

同一判官、同 5 份答案文本、每版 rubric 重复盲评 3 次，唯一变量是 rubric 版本
（文本逐字相同 → 真值 Δ 必为 0，测的是判官复评散布）：

| 版本 | 合并 sd | 各题极差 |
|---|---:|---|
| v1 抽象判据 | 1.24 | [1,3,3,3,1] |
| v2 可数锚点 **+ truth_boundary 一票否决判 0** | **1.71** | [4,1,2,**6**,0] ← 比 v1 还差 |
| v3 可数锚点 + 否决拆出分数 | **0.77** | [2,1,1,2,1] |

（两轮独立复现；首轮 v1 1.13 → v2 1.44，同一题三次打出 9 / 7 / 13。）

v2 在 4/5 题上确实更紧，却被单独一道题拉爆：`current-mainline` 是**唯一**被判 hallucination
的题，也是**唯一**极差炸到 6 的题。判官对「算不算编造」摇摆，`truth_boundary` 在 0 与 3 之间跳，
总分跟着跳 4 分。拆出去之后 hallucination 反而在 3 道题上都报了——**检测器与惩罚脱钩，
判官更敢报**，而极差全部收进 2 以内。

## 实例 2（2026-09-03，弃权率）

一个 100% 弃权的系统零错误、分数不难看、产品价值为零——四臂 38 题读数里组件臂 11.1 分
背后是未见题 10/10 全弃权。均分把「答错」和「不答」搅在一起，消融 Δ 读不出砍掉的是哪一个。
若把弃权折进分（弃权记 0 分）就回到实例 1：弃权是二值量，比连续分更抖。

落地：逐题 `abstained` + `abstain_reason`，聚合 `abstain_rate` **与均分并列、不合并进总分**，
报告两个数一起念「均分 X / 弃权率 Y%」，单念任一个都不许。变异验证：弃权率折进边际贡献 → 测试红。

回溯基线顺带暴露第二层：生产臂该答的 32 题弃 8，其中 **7 道是判官不可用时的扣稿话术**
（`judge_blocked`），模型自弃只有 1 道——判官可用性是**协变量**，不是模型弃权。
否决类读数不但要单列，还要**分类**，否则把基础设施故障读成产品退化。

## 修法（可带走）

1. **否决项照常检测，单列记录**（`pitfalls` / `abstained`），决策层照用它拦住整份读数；
   但**不改任何维度的分**，连续维度回到自己的连续锚点。
2. **两个数一起念**：均分与否决率并列报告，模板层强制，不靠人记得。
3. **二值量的噪声底现算**：塞一组两臂本该完全相同的样本，否决率的门槛从那组算，
   不套连续分的 |Δ| 门槛（沿用 [[eval-harness-variance-governance]] 的做法）。
4. **否决要分原因**：真弃权 / 证据真空 / 判官不可用 / 超时未交卷，各自归属不同修法，
   协变量（判官不可用）重跑前先看计数。
5. 历史版本原文保留不改（要能当对照臂），默认版本切到拆开后的那版；聚合时**混版拒跑**。

## 怎么认出它

- A/B 分差里**一道题的极差远大于其他题**，且那道题恰好触发了某个二值判定 → 先查 rubric
  里有没有「触发即判 0」，别先去怪判官。
- 「加了更严的判据方差反而变大」——判据更紧但引入了阶跃，两个效应打架，单看合并 sd 会误读。
- 某臂分数不难看但答题数少 → 看弃权率有没有被均分吞掉。

## 不覆盖什么

- 真正的安全 pass/fail 门——那里 Veto 是对的用法，阶跃正是要的效果。
- 连续维度本身的措辞型抖动（数值型断言翻转 0%、措辞型 67%）——那是判据写法问题，
  见 [[eval-harness-variance-governance]]。

## 参考

- finance `scripts/run_quality_ablation.py` `_JUDGE_SYSTEM_V3` 上方注释与 commit `10018c3c`
  （2026-08-31，"rubric v3——实测证伪 v2 的一票否决，把它从分数里拿出来"）
- finance `docs/superpowers/specs/2026-09-02-capability-amplification-output-gate-design.md` §3.2
- finance `docs/verification/2026-09-03-abstain-rate-baseline-offline.md`（38 题回溯基线）
- harness-reference `TOOLKIT.md` D++「弃权率是一等读数」（可迁移写法在那里；本条是教训的出处）
