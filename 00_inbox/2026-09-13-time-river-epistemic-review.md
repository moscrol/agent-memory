---
title: 时间长河投研 Agent 终局的方法论压力测试
type: inbox
agent: codex
source: 2026-09-13 用户愿景讨论；本地终局 spec 与能力图谱；5 份一手论文或作者文档
date: 2026-09-13
tags: [inbox, finance-agent, time-river, research, calibration, epistemology]
status: draft
---

# 时间长河投研 Agent 终局的方法论压力测试

> 原始调研产出，待审阅提炼。本文只评愿景与证据标准，不认定某功能未实现，不代表 8792 部署验收；未改代码、spec、BP 或项目记忆。

## 内容

**[判断] 方向成立，但“可回溯→可验证→有预测增量→改善决策→形成商业壁垒”是五个需要分别举证的箭头。** 底座可以使错误可被发现、被保存、被纠正；它本身不保证方法有超额信息、不保证未来分布不变，也不保证用户愿意付费。新版 spec 已有双时钟、规则候选门、时间外验证、失效监测、个人与共享隔离，不宜把这些重新包装成遗漏。[终局统一 spec](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:165)

范围与版本：以 09-06 统一 spec 为主要设计证据，09-05 终局与 gap-roadmap 为决策沿革；补查能力图谱的相关项。原 spec 的“不得方向”不可当永久用户限制：09-07 BP v1.2 已允许研判大盘、主流板块和题材，当前对外边界是“不荐股、不提供个股买卖建议”。本文对“概率预测”的讨论是新的验收层提议，未替用户修改产品政策。[BP v1.2](/Users/a77/finance-workspace-private/docs/bp/2026-09-finance-agent-bp.md:5)

### 1. 观察树跑通，不等于概率预测得到验证

- **状态：spec 已有观察回检；概率与信息增量评估属延伸。** 情景树目前按覆盖、沿路条件触发和规则样本产出回检；节点不登记概率。这是一个清楚的观察协议，但不是概率预报评分协议。[spec §3.3](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:158)
- **[推断]** 若只奖励覆盖，枚举“涨、跌、平”或极宽条件也容易覆盖世界；覆盖率高不能单独证明提前知道得更多。要称“推演大概率事件”，需冻结事件、期限、概率版本，并单列校准（报 70% 的事件长期约七成发生）、区分能力和相对基准改进。Brier 分数是概率与 0/1 结果差的平方；它与适当评分规则可避免只追逐命中率的激励。[Gneiting & Raftery，§1、§2.3、§3，VERIFIED 2026-09-13](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf)
- **可审验收提议：** 保留观察树的现有职责；另做前向冻结的概率实验，结果与“永远报历史基准率”等朴素基线比较。若继续不用数字概率，则评价提前量、关键变量覆盖、无效告警、复杂度与用户少走了哪些弯路，不称为“概率校准完成”。

### 2. 六轨共振要证明新信息，不能变成六次确认同一条信息

- **状态：已有来源去重与禁止投票的设计；需要强化增量价值实证。** spec 已要求同源事件去重。能力图谱明确已有“同事件合并、反证保底”与产业证据/定价状态二分，禁将共享成交数据的指标投票；因此不能说“系统没有识别重复证据”。[spec §7](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:434)；[能力图谱](/Users/a77/agent-memory/10_knowledge/finance-agent-capability-graph.md:228)
- **[推断]** 新闻、资金、涨停、强度可能都是同一政策冲击的下游反应。不同栏目不等于独立证据，确定性计算也不等于经济解释成立。共振的研究问题应改成“知道盘面后，新增资金/消息还提高多少样本外解释或预测质量”。
- **可审验收提议：** 在相同冻结任务与样本上比较单轨、组合、移除某轨后的结果；按不同事件和环境复验，报告新增收益与成本。代码会算的量先叫特征或观测量，经过验证才称有效因子。这里是对现有契约的统计验收深化，不要求再建一套证据系统。[同一预测情景才可直接比较评分：Gneiting & Raftery §2.3，VERIFIED 2026-09-13](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf)

### 3. 把数据关在过去，仍需区分模型有没有见过未来

- **状态：双时钟和模型截止分栏已设计；真实前向证据需长期强化。** spec 过滤 recorded_at 并隔离 hindsight；gap-roadmap G-11 已记模型截止日表，故“补模型训练截止”不是新发明。[spec §4.1](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:169)；[G-11](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-05-time-river-gap-roadmap.md:200)
- **外部事实：** Glasserman & Lin 的金融新闻情绪实验区分模型训练知识带来的前视偏差与公司背景干扰，并用实体匿名化比较；其样本中匿名化表现改善不等于所有 LLM 都同方向泄漏。[论文 §1–§2，VERIFIED 2026-09-13](https://arxiv.org/pdf/2309.17322)
- **[推断] 可审验收提议：** 分开报告“确定性规则历史回放”“LLM 历史演练”“模型与判断版本冻结后的真实前向观察”。匿名化可做诊断，不当绝对隔离保证；新材料 PK 能验研究流程，真正未来表现仍要等待未发生样本。未来的经验卡、检索记忆和验证反馈也不应倒灌进历史实验。

### 4. 横截面扩大数据量，不能按行数扩大独立证据量

- **状态：已有对象去重；用户本轮还报告相关样本统计已合并。此项是强化验收，不是另立缺口。** spec §5.4 写每天约 400 板块可作横截面样本，§6.2 写 Wilson 区间；多块同日、重叠成分股、同轮宏观冲击之间却可能高度相关。[spec 样本墙](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:389)；[评估口径](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:413)
- **外部事实：** Petersen 作者文档区分按一个维度与两个维度聚类，并说明存在组内相关时逐行 bootstrap 会产生有偏标准误，应按组抽样。[作者文档“Two dimensions”“Bootstrapped Standard Errors”，VERIFIED 2026-09-13](https://www.kellogg.northwestern.edu/faculty/petersen/htm/papers/se/se_programming.htm)
- **[推断] 可审验收提议：** 同时报行数、独立事件/时期数、聚类定义和不确定性方法，审计已合入的相关样本统计是否覆盖同日冲击、成分重叠和时间窗重叠。不能用“新增四百行”叙述为“四百次独立历史”；有效样本量依赖统计问题，没有万能换算式。

### 5. 自进化越勤快，越要防止把验证集也学会

- **状态：发现/验证/Holdout 与多重检验已有；自适应复用规则需强化。** 所有候选计入分母、失败保留、Holdout 不得被探索读取均已在 spec；这是正确底座。[spec §7](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:433)；[G-13](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-05-time-river-gap-roadmap.md:206)
- **外部事实：** Dwork 等说明按先前验证结果不断修改候选，会对重复使用的 Holdout 过拟合；固定候选的多重检验处理不能自动覆盖自适应选择。其可复用 Holdout 的理论条件也不能未经检查直接搬到金融相关时序。[论文 §1.1，VERIFIED 2026-09-13](https://arxiv.org/pdf/1506.02629)
- **[推断] 可审验收提议：** 每条方法维护“看过哪些数据与评分”的实验谱系；验证窗/题集设置用途与访问预算；公布结果后将其视为已消耗，下一轮靠新时期前向样本。维护冻结的现行方法与候选方法对照，确认改进再晋升。候选越来越多只能说明探索活跃，不能直接证明能力越来越强。

### 6. 更懂用户与更接近事实，应是两个分开的学习目标

- **状态：个人/共享隔离、三类判断归因、反馈只生候选已覆盖；偏好与真值双评价需强化。** spec 已明确用户判断、Agent 判断、观察剧本分列，框架决定怎么看而不伪装事实轨。[spec §4.2](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:216)；[§5.2](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:334)；[§12](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:549)
- **[推断]** 用户喜欢短解释、偏好某题材是有效偏好；“这个宏观规律是真的”仍需独立事实判定。完全顺着用户方法选上下文，可能越用越少看到反例；用户看了 Agent 后的正确回答也不能全归为用户独立能力。
- **可审验收提议：** 把展示偏好、研究约束、可检验方法、世界事实分开；比较辅助前原判断、辅助后修改与后续结果，定期用用户没看过的新实体/新环境考迁移。保留反方窗口，衡量用户是否减少重复错误，而非只看满意度。此项是基于既有两套评估的产品实验提议，不是已证明出现了偏差。[用户价值现有指标](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:393)

### 7. 研判准确与决策有用，还隔着期限、损失与机会成本

- **状态：spec 已禁止用收益/命中率作唯一价值；决策效用是可选延伸。** 当前目标包括省时、理解、迁移、修正和负担，已比“只看胜率”完整。[spec §1.2](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:29)；[§6.1](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:397)
- **[推断]** 80% 小赚、20% 大亏的决策可有负期望；同一研判对一日观察者与半年研究者价值不同。反过来，少做一次无必要的研究、及早识别证据过期、承认不知道也可能很值钱。预测分布与行动效用需要分别定义。[概率评分与效用关系：Gneiting & Raftery §2.2，VERIFIED 2026-09-13](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf)
- **可审验收提议：** 在不改当前不荐股边界下，记录这条判断改变了什么研究动作、节省了多少时间、哪些假设被放弃、错过了什么；用户实际成交若未来经授权接入，只用于行为复盘与归因。没有真实动作时，不能把事后模拟的最优路线叫用户本来能赚的钱。

### 8. 历史类比要能承认机制变了，也要识别“正确但已定价”

- **状态：阶段漂移与失效已有；因果与反身性是延伸。** spec 已监测环境、数据源、实体宇宙与规则适用范围变化；事件定价设计已有非事件基准、预期内外分表，能力图谱要求无事前预期源只报价格状态，因此不该提议“从零补定价认知”。[spec §6.3](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-06-personal-research-calibration-endstate-design.md:423)；[终局事件定价](/Users/a77/finance-workspace-private/docs/superpowers/specs/2026-09-05-time-river-endstate-design.md:295)；[能力图谱](/Users/a77/agent-memory/10_knowledge/finance-agent-capability-graph.md:229)
- **外部事实：** Perdomo 等把预测经行动影响未来结果的现象形式化；简单反复重训的收敛需要条件，并非数据增加就必然更稳。论文是一般理论，不证明本项目已影响 A 股价格。[论文 §1–§2，VERIFIED 2026-09-13](https://proceedings.mlr.press/v119/perdomo20a/perdomo20a.pdf)
- **[推断] 可审验收提议：** 每条重要规律附机制假说、适用环境、竞争解释和能区分解释的下一项证据；保留“事实正确、方向判断也对，但市场早已反映”的分类。产品规模扩大后再评估方法拥挤与用户互相影响；更早就要记录 Agent 的展示如何改变用户登记与关注对象，避免把自己造成的选样变化误读成学习进步。

## 来源核验收据

以下五份一手来源均于 **2026-09-13 实际打开并读到正文相关章节**。`VERIFIED` 仅指这次来源读取，不指建议已实施或效果已验证。

| 来源 | 读取范围与直接用途 | 状态 |
|---|---|---|
| [Gneiting & Raftery, Strictly Proper Scoring Rules, Prediction, and Estimation (2007)](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf) | §1、§2.2–2.3、§3；概率评分、效用、比较集合一致 | VERIFIED 2026-09-13 |
| [Glasserman & Lin, Assessing Look-Ahead Bias… (2023)](https://arxiv.org/pdf/2309.17322) | §1–§2；训练知识前视与匿名化实验边界 | VERIFIED 2026-09-13 |
| [Petersen, Programming Advice—Finance Panel Data Sets](https://www.kellogg.northwestern.edu/faculty/petersen/htm/papers/se/se_programming.htm) | 作者文档一维/二维聚类及按组 bootstrap；未把被拦论文 PDF 标为读过 | VERIFIED 2026-09-13 |
| [Dwork et al., Generalization in Adaptive Data Analysis and Holdout Reuse (2015)](https://arxiv.org/pdf/1506.02629) | §1.1 及重复 Holdout 讨论；自适应验证污染 | VERIFIED 2026-09-13 |
| [Perdomo et al., Performative Prediction (ICML 2020)](https://proceedings.mlr.press/v119/perdomo20a/perdomo20a.pdf) | §1–§2；预测引发行动后的分布变化及收敛条件 | VERIFIED 2026-09-13 |

未采用的线索：Harvey–Liu–Zhu、Petersen 论文 PDF 的数个 NBER/作者网址本轮抓取失败，故不将搜索摘要作为已读正文引用。

## 提炼提示（哪些值得沉淀？）

- 可以把后续提升的验收分成五张收据：当时可知、增量信息、概率/情景质量、用户决策效用、付费与复用。上一张过关不替下一张过关。
- 更值得积累的资产是失败规则、有效环境、改判条件与真实前向判断；候选数量和聊天数量只说明活动量。
- 本轮未核验部署版本、数据质量或全部已合入实现；实际工单应先核现行代码与测试，避免把“需强化证据”误写成“能力不存在”。

写入校验：2026-09-13 调用原 `scripts/vault_lint.py` 的规则，将本文件单独放入临时 vault 执行 `--strict`，结果 `OK: 1 个文件通过（0 warn）`、exit 0。全 vault lint 另跑过，因 4 个既有知识笔记 frontmatter 问题与 TOOLKIT 镜像漂移共 5 errors / 12 warns 返回 exit 1；本轮未修改这些他人文件。
