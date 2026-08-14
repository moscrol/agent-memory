---
title: "大模型面试：金融 Agent 项目第一性原理复习手册（V3）第5册（章 20–27）"
type: tutor-note
agent: devin
source: "拆自 PR #21（Devin Session deebe5e092fe49579a9983ee14ca02d3）；按章节边界无损拆分自原单文件手册"
date: 2026-07-14
tags: [llm, interview, finance-agent, rag, agent, handbook]
status: draft
related: ["[[大模型面试-金融Agent项目第一性原理复习手册-V3]]"]
---

> 本册为 [[大模型面试-金融Agent项目第一性原理复习手册-V3|V3 手册]] 第 5/6 册（章 20–27），按章节边界无损拆分，正文逐行未改写；分册导航见索引页。

## 20. DuckDB 与结构化市场数据：为什么数字事实不应该只进向量库

真实代码和资料：

- `finance-workspace-private/market_feature_store/`
- `finance-workspace-private/intelligence/services/ask.py`
- `finance-workspace-private/intelligence/services/ask_planner.py`
- `finance-workspace-private/intelligence/services/market_timeseries.py`
- `finance-workspace-private/intelligence/services/market_midterm.py`
- `finance-workspace-private/intelligence/services/market_financials.py`
- `finance-workspace-private/intelligence/services/market_analogs.py`
- `finance-workspace-private/intelligence/services/market_moneyflow.py`
- `finance-workspace-private/intelligence/services/valuation_estimate.py`
- `finance-workspace-private/intelligence/services/valuation_gap.py`

### 20.1 业务问题

以下问题需要精确结构化计算：

- 近 20 日涨幅；
- 某题材连续几天进入强势队列；
- 市场上涨家数、涨停数；
- 估值分位；
- 财报季度趋势；
- 同链股票相对强度；
- T 日之前可用的行情。

如果把表格转成文本 embedding：

- 数字近似相似不等于相等；
- 很难 `WHERE date <= T`；
- 很难 group by、排序、窗口函数；
- 更新后旧 chunk 可能残留；
- 模型容易算错。

### 20.2 第一性原理

数据形态决定存储和查询方式：

```text
精确、规则化、可聚合的事实
→ relational / columnar engine

语义、多义、非结构化材料
→ lexical/dense retrieval
```

LLM 不应承担数据库职责。

### 20.3 为什么选择 DuckDB

当前是本地个人研究工作台，DuckDB 的优势：

1. 嵌入式，无独立数据库服务；
2. 列式执行，适合分析查询；
3. 对 Parquet/CSV 友好；
4. SQL 支持完整；
5. 单文件便于本地快照；
6. Python 集成简单；
7. 比 pandas 手写聚合更可审计。

为什么当前不直接用 PostgreSQL：

- 没有多用户并发写需求；
- 不需要长驻数据库服务；
- DuckDB 更适合本地 OLAP 和文件分析。

什么时候要迁移：

- 多用户并发；
- 在线事务写入；
- 权限和租户隔离；
- 高可用；
- 多节点服务。

### 20.4 典型事实表

项目中可见：

```text
fact_sector_daily
fact_theme_limit_heat_daily
fact_limit_advance_daily
```

它们分别承载：

- 板块日度；
- 题材涨停热度；
- 涨停晋级结构。

面试时不需要背全部 schema，而要讲清：

> 表存储可由确定性查询复算的事实；结论和叙事不直接写进事实表。

### 20.5 D0-D9 数据块

`ask` 的 compose/deep-dive 路径按问题需要生成数据块：

| Block | 语义 |
|---|---|
| D0 | 盘面时序直查 |
| D1 | 市场价值与替代队列 |
| D2 | 客户证据硬度 |
| D3 | 二阶导研究队列 |
| D4 | 主线题材结构 |
| D5 | 估值数据 |
| D6 | 多日中期趋势 |
| D7 | 逐季财报 |
| D8 | 历史类比 |
| D9 | L2 大单资金流 |

并非每个问题都运行全部 D block。

例如：

- 方法论问答不需要 D0-D9；
- 快速实体解释可能只用 G/R/W；
- 估值问题需要 D5/D7；
- 市场复盘更依赖 D0/D4/D6。

### 20.6 Planner-worker 并行

独立数据块通过：

```python
ask_planner.run_block_tasks(..., parallel=...)
```

并行执行。

为什么可以并行：

- D0、D1、D4、D5 等读不同工具或查询；
- 彼此没有数据依赖；
- 并行可降低总等待时间。

如果每块耗时 \(t_i\)：

串行约为：

\[
T_{serial}=\sum_i t_i
\]

理想并行约为：

\[
T_{parallel}\approx \max_i t_i + overhead
\]

### 20.7 为什么 D3 串行

D3 是二阶导研究队列，需要使用前面数据块形成的 `evidence_text`。

因此：

```text
D0/D1/D2/D4... 并行
→ 汇总 evidence_text
→ D3 串行生成
```

这是一个真实依赖关系，而不是所有任务盲目并行。

面试可说：

> 我先构建 DAG，再只并行无依赖节点；D3 依赖前序证据汇总，所以作为 barrier 之后的串行收尾。

### 20.8 数据缺口显式化

每个 block 需要区分：

```text
not attempted
empty
error
ok
```

否则：

- 没有数据；
- 没运行；
- SQL 失败；
- 条件无匹配；

都会被错误地解释成同一个空列表。

telemetry 应记录：

- block attempted；
- row count；
- latency；
- error / warning；
- source date；
- freshness。

### 20.9 `ask` 默认不强依赖 DuckDB

项目 README 和代码口径：

> `ask` 默认可以在不依赖 DuckDB 的情况下运行 S/G/R/W 等基础路径；compose、深挖或特定问题才会选择 D block。

不能在面试中说：

> 所有问题都实时查询完整 DuckDB。

准确说法：

> DuckDB 是结构化事实源；是否访问由 QuestionPlan 和 compose path 决定。

### 20.10 结构化数据与 RAG 如何合并

错误方式：

```text
SQL 结果 + wiki chunk + 用户记忆
→ 无标签拼成一个长 prompt
```

正确方式：

```text
D block：
  标明表、日期、字段、计算口径

W hit：
  标明 page、section、chunk、revision、freshness

M：
  标明 user prior / historical

→ 统一进入 evidence audit
→ 按 claim 类型选择合适来源
```

数字 claim 应优先绑定 D evidence，而不是 W 文本中的二手数字。

### 20.11 异常和降级

| 情况 | 行为 |
|---|---|
| DB 不存在 | 对需要 D 的问题标 data gap |
| 表不存在 | block error，不伪造空市场 |
| 查询无行 | empty，并说明日期/实体范围 |
| 某 block 失败 | 其他独立 block 继续 |
| D3 前置 evidence 不足 | 降级或跳过二阶导 |
| 财务字段缺失 | 不给精确估值 |
| 默认 ask 未运行 D | telemetry 写 not attempted |

### 20.12 评测

结构化数据层应评测：

- SQL correctness；
- row-level PIT correctness；
- schema contract；
- 数据完整率；
- 每个 block empty/error rate；
- latency p50/p95；
- 数字 claim match rate；
- 同一输入可复现性；
- 并行前后 wall time；
- D3 是否只在前置完成后执行。

### 20.13 当前边界

已实现：

- DuckDB 特征库；
- 多类事实表；
- D0-D9 数据块；
- planner-worker 并行；
- D3 依赖后置；
- block 级 telemetry；
- 特定问题按需访问。

不能夸大：

- 不是所有 ask 都查 DuckDB；
- 不是实时交易系统；
- 不是流式 tick 级基础设施；
- 数据覆盖依赖 fupanhui、iFinD、AKShare 等上游；
- 上游缺失时仍需要显式 data gap；
- 没有证据证明所有 D block 已在大规模历史集上完全校验。

### 20.14 面试表达

#### 30 秒

> 实时和历史市场数据没有放进向量库，而是进入 DuckDB，因为行情、财务和题材热度需要精确日期过滤、聚合和窗口计算。问答按计划选择 D0-D9 数据块，独立块并行执行，依赖汇总证据的 D3 在 barrier 后串行。每块都区分 not attempted、empty、error 和 ok，避免把没运行或查询失败伪装成“没有数据”。

#### 2 分钟

> 我的系统把非结构文本和结构化事实分开。知识材料走 RAG，行情、财务、题材强度和历史时序走 DuckDB。原因是向量相似度不能替代精确数值、日期截断、group by 和窗口函数。`ask.py` 根据 QuestionPlan 和 compose 模式选择 D0-D9，例如 D0 查盘面时序、D5 查估值、D7 查季度财报。无依赖的数据块通过 planner-worker 并行，D3 需要前面 evidence_text 才能生成二阶导研究队列，因此串行收尾。默认 ask 不一定依赖 DuckDB，所以我会明确说它是按需结构化事实源，而不是每次请求都跑完整数据库。

#### 追问

**问：为什么 DuckDB 而不是 pandas？**
答：SQL 口径更显式、聚合和窗口能力更强、对列式分析更高效，也更易回放；pandas 可用于局部处理，但不作为主要事实查询接口。

**问：怎样避免数字被 LLM 改写错？**
答：数字 claim 绑定 D evidence，经过 AnswerSpec 和 claim fidelity 校验；模型主要解释，不重新计算。

---

## 21. Output Review：为什么生成后还要有确定性审稿

真实代码：

- `finance-workspace-private/intelligence/services/output_review.py`
- `finance-workspace-private/intelligence/services/answer_model.py`
- `finance-workspace-private/intelligence/services/ask.py`

### 21.1 业务问题

即使检索正确，LLM 仍可能：

- 忽略数据新鲜度；
- 把 L1/L2 写成 L3；
- 忘记反证；
- 隐藏数据缺口；
- 给出无法验证的泛化结论；
- 把弱证据写成强结论；
- 修订时破坏原有引用和结构。

所以检索质量不等于最终答案质量。

### 21.2 第一性原理

生成模型优化的是：

```text
下一个 token 的条件概率
```

不是：

```text
金融证据契约是否满足
```

因此需要独立 reviewer，检查可形式化的输出要求。

### 21.3 为什么 reviewer 不直接再用同一个 LLM

如果生成和审核都只靠同一模型、同一上下文：

- 会共享盲点；
- 审核结论难以稳定；
- 不能保证检查顺序；
- 容易产生“看起来认真”的空泛自评。

当前做法是：

```text
确定性 review 先发现具体 violation
→ 可选把 violation 回灌 LLM 修订
→ 再由 AnswerSpec 校验
```

### 21.4 固定检查顺序

`CHECK_ORDER`：

1. 本地数据新鲜度；
2. 证据分层；
3. 反证；
4. 缺口显式化；
5. 可验证假设；
6. 弱证据硬写。

顺序有意义：

- 数据已经过期时，后面再讨论表达完整性价值有限；
- 证据层错误会影响结论强度；
- 有了主结论后必须看反证；
- 最后检查是否把弱证据写硬。

### 21.5 `review_output(...)`

输入通常包括：

- answer text；
- evidence audit；
- gap lines；
- freshness；
- counterevidence；
- question plan；
- AnswerSpec。

输出：

- PASS/WARN；
- 每项检查结果；
- warning；
- revision guidance。

### 21.6 Advisory gate

当前：

```text
blocking = False
WARN 不直接阻断输出
```

为什么：

- 个人研究工作台需要在部分数据缺失时仍给草稿；
- 某些 warning 是信息性；
- 完全阻断可能导致系统不可用。

但 advisory 不等于忽略：

- warning 必须展示；
- 有 LLM 时可触发定向修订；
- 修订后再验证。

### 21.7 WARN 修订链路

```text
初始 answer
→ review_output
→ WARN:
   把具体缺陷加入同一对话
→ LLM 定向修订
→ validate_llm_answer
→ 合格则使用修订版
→ 不合格则保留安全模板或 warning
```

为什么是“定向修订”：

错误：

```text
请重新回答得更好
```

正确：

```text
你把 L2 卖方推演写成了公司已确认事实；
请降级措辞，并补充缺失的 L3 验证点和反证。
```

### 21.8 AnswerSpec 的角色

Reviewer 告诉模型哪里错；
AnswerSpec 检查修订结果是否仍满足：

- 固定 section；
- 必要引用；
- 禁止项；
- 缺口和反证；
- claim 类型；
- 格式契约。

这避免模型修一处又破坏另一处。

### 21.9 Review 与自动预测裁判的区别

Output Review 判断：

- 证据和表达是否合规；
- 是否诚实；
- 是否可验证。

它不判断：

- 预测未来最终会不会命中；
- 股票明天会不会涨；
- 当前 thesis 是否一定正确。

后者需要历史 outcome 和 checkpoint verdict。

所以不能说：

> 我实现了自动金融预测裁判。

准确说：

> 我实现了回答的 advisory quality gate，以及独立的历史 checkpoint/verdict 框架。

### 21.10 异常和降级

| 情况 | 行为 |
|---|---|
| 无 LLM | 保留模板答案和 review warning |
| LLM 修订失败 | 不采用坏修订 |
| 修订后结构不合格 | AnswerSpec 拒绝 |
| 数据 stale | 答案降级并显示 freshness warning |
| 无 counter | 明确未找到，不说无风险 |
| gap 未写 | reviewer 触发 warning |
| 弱证据硬写 | 要求降级措辞 |

### 21.11 评测

Reviewer 要单独建立 violation set：

```text
把研报预计写成已实现
引用过期数据
没有反证
没有缺口
数字无来源
把用户 memory 当事实
```

指标：

- violation detection precision/recall；
- false block rate；
- revision success rate；
- post-revision contract pass rate；
- unsupported claim reduction；
- citation coverage improvement；
- review latency；
- 用户是否认为 warning 有用。

### 21.12 当前边界

已实现：

- 固定检查顺序；
- PASS/WARN；
- advisory gate；
- WARN 回灌 LLM；
- AnswerSpec 校验；
- 输出中展示 review。

不能夸大：

- `blocking=False`，当前不是硬阻断安全系统；
- review 规则不能覆盖所有语义幻觉；
- 不是独立训练的 critic model；
- 没有充分大规模数据证明 detection precision/recall；
- 不负责自动判定预测 hit/miss。

### 21.13 面试表达

#### 30 秒

> 检索正确不代表生成正确，所以我在答案后加了确定性 Output Review。它按固定顺序检查数据新鲜度、证据分层、反证、缺口、可验证假设和弱证据硬写。当前是 advisory gate，WARN 不直接阻断，但会把具体 violation 回灌给 LLM 定向修订，再用 AnswerSpec 校验修订版。它审的是证据和表达合规，不是自动判断预测会不会命中。

#### 2 分钟

> LLM 很容易在最后一步把弱证据写强，比如把卖方推演写成公司已确认，或者有主结论却忘了反证。我把 reviewer 从生成 prompt 中拆出来，`review_output` 先用确定性检查按顺序审数据新鲜度、evidence layer、counterevidence、gap、可验证假设和 unsupported strong claim。当前 gate 是 advisory，因为个人研究场景允许在部分缺数据时输出带 warning 的草稿。有模型时，系统不会泛泛地要求“重写”，而是把具体 violation 回灌，比如“请把 L2 口径降级，并补 L3 验证点”；修订后再用 AnswerSpec 校验 section、引用和禁止项。这样把 reviewer、reviser 和 validator 分开。

#### 追问

**问：为什么不直接 blocking？**
答：当前规则尚未充分校准，硬阻断会有较高误杀；先 advisory 收集 violation 和用户反馈，达到可靠阈值后再对高风险规则分级阻断。

---

## 22. Agent Memory：从聊天流水到可治理的长期记忆

真实代码和资料：

- `agent-memory/README.md`
- `agent-memory/30_conventions/frontmatter-spec.md`
- `agent-memory/30_conventions/trust-boundary.md`
- `agent-memory/30_conventions/maintenance.md`
- `agent-memory/40_playbooks/devin-writeback.md`
- `agent-memory/40_playbooks/preflight.md`
- `agent-memory/50_agents/claude-hooks.md`
- `agent-memory/preflight.sh`
- `finance-workspace-private/intelligence/userspace.py`
- `finance-workspace-private/intelligence/services/user_memory.py`
- `finance-workspace-private/intelligence/services/corrections.py`
- `finance-workspace-private/intelligence/services/checkpoints.py`
- `finance-workspace-private/intelligence/services/experience_cards.py`
- `finance-workspace-private/intelligence/users/<user>/`

### 22.1 业务问题

把所有历史对话塞进 prompt 有四个问题：

1. 成本随历史线性增长；
2. 旧信息和当前事实混淆；
3. 聊天中有大量寒暄、试错和过期计划；
4. 多个 Agent 之间无法稳定共享同一上下文。

金融场景更危险：

- 半年前的价格、订单、市场判断会过期；
- 用户主观看法可能与当前硬数据冲突；
- 历史预测不能被重新包装成当时已知事实。

### 22.2 第一性原理

Memory 不是“保存所有 token”，而是：

> 从历史交互中提炼对未来任务有用、可追溯、可更新的状态。

需要区分：

```text
原始对话
稳定事实
项目状态
方法论
用户偏好
一次性纠错
预测与回检
```

不同类型必须有不同生命周期。

### 22.3 为什么 Git + Markdown + YAML + Obsidian

选择理由：

- Markdown：人类可读；
- YAML：机器可解析；
- Git：版本、diff、作者、回滚；
- Obsidian：双链、MOC、人工审阅；
- shell/hooks：低成本自动加载和门禁；
- 无专有格式锁定。

没有一开始上向量数据库或记忆服务，是因为：

- 当前规模和协作方式更需要透明审阅；
- 记忆质量问题先于 ANN 性能；
- Git 对项目决策和方法论更适合；
- 事实时效和 trust boundary 需要明确治理。

### 22.4 分层目录

```text
00_inbox       原始、短期、待整理
10_knowledge   稳定事实与结论
20_projects    项目 MOC、任务和交接
30_conventions 跨 Agent 规范与信任边界
40_playbooks   可复用流程
50_agents      Agent 接入约定卡
60_dialogues   外部 AI 原始对话
70_tutor       经用户批准的学习笔记
_templates     标准模板
```

### 22.5 为什么不能只有“短期记忆/长期记忆”两层

因为长期内容内部语义差异很大：

- 项目进度会变化；
- 方法论较稳定；
- 用户偏好可能可更新；
- 单次反馈只是样本；
- raw 对话不应自动变成知识。

如果都进入一个 long-term vector store，检索时很难决定：

- 哪条可信；
- 哪条过期；
- 哪条是指令；
- 哪条是历史观点。

### 22.6 Frontmatter

通用字段：

```text
title
type
agent
source
date
tags
status
related
reviewed_by
reviewed_at
```

为什么 provenance 必须在结构层：

```text
“某结论”
```

只有在知道：

```text
谁写的、什么时候写的、来源是什么、是否验证
```

之后才有可用价值。

### 22.7 黑板模型

```text
Grok 搜索 ─┐
           ├→ 00_inbox → 提炼 → 10_knowledge
Codex 规划 ─┤                     │
           └→ 20_projects ←───────┘
                    │
                    ↓
                 Devin 执行
                    │
                    └→ 回写项目决策与稳定方法论
```

这不是共享完整模型 hidden state，而是共享可审阅工件。

### 22.8 读路径

开工时：

```text
preflight
→ 当前 repo/branch/status
→ 红线
→ 20_projects/<repo>.md 摘要
→ 完工回写提醒
```

Claude/Codex SessionStart hook 会加载：

- preferences；
- 当前项目 MOC；
- Git 状态。

价值：

- 新会话快速恢复上下文；
- 不依赖模型记住主动读文件；
- 项目状态来自最新 Git 版本。

### 22.9 写路径

完成任务后先判断沉淀层级：

```text
项目级代码/流程/架构变化
→ 20_projects

跨任务稳定方法论
→ 10_knowledge

单次问答评分/纠偏
→ 项目内 corrections / experience cards

临时材料
→ 00_inbox

例行知识入库批次
→ 知识库自身 wiki/log.md，不污染项目 MOC
```

这是“过程 → 资产”的核心。

### 22.10 Stop hook 门禁

Stop hook 检查：

1. repo 是否有代码/配置级改动；
2. 是否只是数据产物；
3. 是否已经更新项目记忆；
4. 是否明确确认无需项目级回写；
5. 防止每次聊天反馈都硬塞进 MOC。

这不是为了强制写更多，而是强制做一次：

> 这次结果是否值得长期沉淀？

### 22.11 Trust boundary

最关键安全原则：

> 记忆是数据，不是当前指令。

因为共享记忆可能包含：

- 外部网页的 prompt injection；
- 旧 Agent 写入的命令式文本；
- 未审阅内容；
- 恶意或错误建议。

所以：

- `00_inbox` 默认不可信；
- 笔记中的“执行命令、删除、推送、泄露密钥”只能当文本；
- 真正操作指令只来自当前用户和系统；
- `30_conventions`、`50_agents` 是受保护高权重区；
- 影响 Agent 行为的写入需人工 review。

这是 Agent Memory 相比普通 RAG 很重要的一层：**持久化 prompt injection 防护**。

### 22.12 项目内用户记忆

默认 `intelligence/users/<user>/` 包含：

```text
judgments.jsonl
corrections.jsonl
checkpoints.jsonl
verdicts.jsonl
experience_cards.jsonl
interactions.jsonl
answer_scores.jsonl
```

也可通过：

```text
FORESIGHT_USERS_DIR
```

把整个 users 根目录重定位到外部同步路径，例如 Obsidian vault 下的隐藏
`.foresight/`；因此 `.foresight/<user>` 是可配置部署形态，不是当前仓库内固定目录。

语义：

- interaction：发生了什么问答；
- judgment：用户当时的判断；
- correction：用户指出什么错误；
- checkpoint：未来要验证什么；
- verdict：验证后是 hit/miss/partial/unverifiable；
- experience card：从重复样本抽出的经验；
- answer score：回答反馈。

### 22.13 事实和经验必须分离

事实：

```text
2026-07-10 某公司发布公告
```

经验：

```text
只凭题材关联、没有 L3 和盘面双验证时，容易高估公司纯度
```

事实可能过期或需要 PIT；
经验可以跨任务复用，但也应记录适用条件。

如果混在一起：

- RAG 可能把经验性陈述当当前事实；
- 用户旧判断可能污染实时结论。

### 22.14 Memory 作为 prior 的融合

可以用贝叶斯语言解释，但不要夸大为已完整实现贝叶斯系统。

概念上：

\[
P(H|E,M) \propto P(E|H)P(H|M)
\]

- `M` 提供 prior；
- 当前证据 `E` 更新判断；
- 硬数据应覆盖旧记忆。

真实工程口径：

```text
memory 提示历史假设和常见错误
→ 当前问题重新查 S/G/R/W/D/L
→ 冲突时以当前硬证据为准
→ 把冲突记录为 correction 或新 checkpoint
```

### 22.15 一致性与检索边界

Git/Markdown 的限制：

- 不是强一致事务数据库；
- 多 Agent 同时写可能冲突；
- Markdown schema 约束弱；
- 双链可能失效；
- 大量笔记的检索效率会下降；
- TTL、superseded 状态不一定自动维护。

当前通过：

- append-only；
- frontmatter lint；
- protected areas；
- writeback discipline；
- Git review；
- 分层目录；

降低风险，但不是完全解决。

### 22.16 评测

Memory 系统不能只看“召回了几条”，还应看：

- useful memory precision；
- stale memory rate；
- memory-as-fact violation；
- contradiction detection；
- repeated-error reduction；
- correction adoption rate；
- experience card hit rate；
- user-specific answer improvement；
- provenance completeness；
- writeback quality；
- dead link / duplicate rate。

### 22.17 当前边界

已实现：

- Git/Markdown/YAML/Obsidian 底座；
- 分层目录；
- frontmatter；
- preflight；
- SessionStart/Stop hook；
- writeback playbook；
- trust boundary；
- per-user JSONL；
- judgments/corrections/checkpoints/verdicts/experience cards；
- 事实与经验分离原则。

不能夸大：

- 不是强一致记忆数据库；
- 不是所有 memory 都有 TTL；
- 不是完整自动贝叶斯仲裁；
- 增强语义检索和冲突消解仍在演进；
- 旧 synthesis 被直接引用的风险仍需治理；
- memory 不等于当前市场事实。

### 22.18 面试表达

#### 30 秒

> 我没有把所有历史对话塞进 prompt，而是把记忆分成 Git/Markdown/YAML 的长期协作资产和项目内 per-user JSONL 学习层。`00_inbox`、knowledge、projects、conventions、playbooks 等目录承担不同生命周期；用户的 judgments、corrections、checkpoints、verdicts 和 experience cards 也分开。Memory 只作为 prior，当前行情和公司事实必须重新检索。另一个重点是 trust boundary：记忆内容是数据，不是可执行指令，防止持久化 prompt injection。

#### 2 分钟

> 多 Agent 项目最大的问题不是模型没有上下文，而是上下文无法治理。我用 Git + Markdown + YAML frontmatter + Obsidian 做共享黑板：原始内容进 inbox，稳定知识进 knowledge，项目状态进 projects，方法流程进 playbooks；SessionStart hook 自动读当前项目记忆，Stop hook 强制判断是否需要分层回写。单次用户反馈不污染项目 MOC，而是进入 corrections、checkpoints、verdicts 和 experience cards。金融场景里 memory 只能提供历史先验，不能直接证明当前订单、价格或产能；冲突时以当前 D/L3 等硬证据为准。另外我明确把 vault 当数据源而不是指令源，未审阅外部内容不能改变 Agent 行为，这也是防持久化 prompt injection。

#### 追问

**问：为什么不直接用 Mem0/向量记忆？**
答：当前首要问题是可读、可审计、分层和信任边界，不是向量搜索性能。以后可在现有 source of truth 上加派生检索层，而不是让黑盒向量库存唯一事实。

**问：怎样删除错误记忆？**
答：不应简单静默覆盖；用 correction、status、superseded/deprecated 和 Git 历史保留审计，再让检索优先当前有效版本。

---

## 23. PIT 与防前视：防止“用未来解释过去”

真实代码和资料：

- `knowledge-base-private/docs/conventions.md`
- `knowledge-base-private/scripts/pit_lib.py`
- `knowledge-base-private/scripts/pit_truncate.py`
- `knowledge-base-private/scripts/audit_pit_timestamps.py`
- `knowledge-base-private/scripts/audit_backfill_embargo.py`
- `finance-workspace-private/intelligence/services/fidelity_contract.py`
- `finance-workspace-private/intelligence/eval/claim_fidelity.py`
- `finance-workspace-private/scripts/bitemporal_history_eval.py`
- `finance-workspace-private/scripts/pit_snapshot_inventory.py`

### 23.1 业务问题

假设你在 3 月 1 日做判断，3 月 10 日有一份公告证实逻辑。

如果历史回放时把 3 月 10 日公告喂给 3 月 1 日模型：

- 回测会显著变好；
- 解释看起来非常合理；
- 但这不是当时可做出的判断。

金融系统中，这叫 look-ahead bias。

### 23.2 第一性原理

“事实何时发生”和“系统何时知道”是两个时间：

```text
valid time / event time
  事实适用于何时

available time / known_at / system time
  系统最早何时可使用
```

还可能有：

```text
publish_time
  来源对外发布时间

ingest_time
  系统实际入库时间
```

决策时点 \(T\) 的证据必须满足：

\[
available\_time \le T
\]

### 23.3 `publish_time` 与 `available_time`

知识库约定：

```yaml
publish_time: YYYY-MM-DD
available_time: YYYY-MM-DD
```

原则：

\[
available\_time \ge publish\_time
\]

默认：

\[
available\_time = \max(publish\_time, ingest\_time)
\]

即：

> 就晚不就早。宁可保守认为晚一点知道，也不能把信息提前。

### 23.4 `pit_lib.py`

核心：

```python
def source_available_time(path):
    available_time
    → publish_time
    → created
    → source_updated
```

```python
def is_available(available, as_of, include_undated=False):
    return available <= as_of
```

```python
def as_of_filter(items, as_of, get_time, include_undated=False):
    return kept, masked
```

无日期来源默认：

```text
exclude
```

这是保守策略，因为无法证明它在 T 时已可得。

### 23.5 `pit_truncate.py`

给定：

```text
--as-of 2026-03-01
```

输出：

- usable；
- masked；
- undated。

它是只读工具，不修改知识库。

### 23.6 时间戳审计

`audit_pit_timestamps.py` 检查：

A. 缺 `publish_time/available_time`；
B. `available_time < publish_time`；
C. 正文证据日期晚于 available time。

为什么 C 很重要：

即使 frontmatter 日期看起来合法，正文可能后来追加了新证据。

例如：

```text
available_time: 2026-03-01
正文却写“2026-03-10 公司公告……”
```

这仍是未来信息污染。

### 23.7 回填 embargo

历史材料回填时：

- delta 的归属日期不得早于 publish time；
- 违例时夹回 publish time；
- 标 `embargo_violation=true`；
- 保留 `embargo_original_date`；
- 不静默修改。

这解决：

> 后来读到一篇老研报，不能把其中结论伪装成系统在更早日期已经知道。

### 23.8 Finance Fidelity Contract

`fidelity_contract.py` 定义：

```text
report_generated_at
evidence_cutoff
decision_cutoff
snapshot_captured_at
generator_commit
run_id
artifact_sha
manifest_sha
```

检查：

```text
evidence_cutoff <= decision_cutoff
evidence_cutoff <= snapshot_captured_at
decision_cutoff <= report_generated_at
snapshot_captured_at <= report_generated_at
```

还把：

- code commit；
- artifact hash；
- manifest hash；
- run id；

绑定到报告。

这让回放不仅知道“用了哪些数据”，还知道“由哪版代码生成”。

### 23.9 Bitemporal replay

严格回放要保存两套视图：

```text
final history
  事后完整、可能有修订

PIT history
  当时真实可见
```

如果只保留最终数据库：

- 后续修正会覆盖当时错误值；
- 回测会用修订后数据；
- 无法证明当时输入。

`bitemporal_history_eval.py` 和 PIT snapshot 相关代码用于构建和比较物理隔离的 PIT 输入。

### 23.10 Claim-level cutoff

`claim_fidelity.py` 为 claim 保存：

- report date；
- location；
- claim type；
- source ref；
- cutoff timestamp；
- verification status；
- cutoff violation。

推荐阈值中：

```text
cutoff_violation_rate == 0
```

说明防前视是硬约束，不是平均指标。

### 23.11 为什么 `unverifiable` 不能算正确或错误

如果历史时点缺乏可验证数据：

```text
unverifiable
```

不能：

- 当 hit；
- 当 miss；
- 为了提高胜率从分母中任意删除；
- 用事后数据补判。

当前回检框架中，`unverifiable` 不计入胜率分母，但仍保留在 due queue 或报告中。

### 23.12 `ask` 当前真实边界

这里必须非常诚实。

知识库和 fidelity/replay 层已经有：

- publish/available time；
- PIT truncate；
- snapshot；
- contract；
- claim cutoff 检查。

但 `ask.py` 当前部分路径仍主要用：

```text
source_date
```

标注 freshness，并明确写出：

> Temporal Facts 层尚未接入；正式版应把会过期/被证伪的事实建成 active/superseded/invalidated 时序边。

所以不能说：

> 整个在线 ask 链路已经完整实现严格 bitemporal retrieval。

准确说法：

> 项目已实现 PIT 工具、时间戳治理、快照和 fidelity contract；但 ask 的所有来源尚未统一贯穿 Temporal Facts，部分仍以 source_date freshness 为主。

### 23.13 异常和降级

| 情况 | 行为 |
|---|---|
| available_time > T | mask |
| 无日期 | 历史回放默认 exclude |
| available < publish | hard issue |
| 正文含未来证据 | audit issue |
| source time > cutoff | cutoff violation |
| 无 PIT source row | unverifiable |
| snapshot/hash 不一致 | contract failure |
| 只有 final history | 不能冒充 PIT |

### 23.14 评测

- timestamp completeness；
- available >= publish violation count；
- future evidence count；
- cutoff violation rate；
- PIT/final partition errors；
- PIT source row coverage；
- snapshot reproducibility；
- artifact/manifest hash validation；
- claim evidence coverage；
- unverifiable rate；
- same input + commit replay consistency。

### 23.15 当前边界

已实现：

- publish/available time 约定；
- audit；
- PIT truncate；
- embargo；
- snapshot；
- fidelity contract；
- bitemporal eval 工具；
- claim cutoff violation；
- unverifiable 语义。

不能夸大：

- ask 全链未完全 Temporal Facts 化；
- 不是所有历史材料都有完整 PIT 快照；
- 后补数据不能自动证明当时可见；
- 完整 valid-time/system-time revision log 仍在演进；
- 有框架不等于所有历史样本都已充分回放。

### 23.16 面试表达

#### 30 秒

> 金融 Agent 必须防前视，所以我区分 `publish_time`、`available_time` 和事实的 valid time。历史决策点 T 只能使用 `available_time <= T` 的来源，无日期默认保守屏蔽。项目里有 PIT truncate、时间戳审计、回填 embargo、每日 snapshot 和 fidelity contract，报告还绑定 code commit、artifact hash 和 evidence cutoff。需要诚实说明：这些能力已在知识库和回放层落地，但在线 ask 还没有把所有来源统一成完整 Temporal Facts。

#### 2 分钟

> 历史研究最容易出现“事后正确、事前不可得”。我先把材料发布时间和系统可得时间分开，要求 available time 不早于 publish time；回放时只保留 available time 小于等于决策点 T 的来源，无日期默认排除。审计不仅看 frontmatter，还检查正文是否后来追加了晚于 available time 的证据。回填历史材料时有 embargo，不能把研报结论归属到发布前。Finance 侧进一步用 fidelity contract 绑定 evidence cutoff、decision cutoff、snapshot time、code commit、run id 和 artifact hash，并在 claim 级检查 cutoff violation。当前边界是 ask 仍有部分路径主要按 source_date 做 freshness，完整 active/superseded/invalidated Temporal Facts 还没有贯穿所有在线来源。

#### 追问

**问：publish time 和 available time 为什么不同？**
答：材料可以早已发布但系统后来才获取；历史回放应按系统真正可使用时间，而不是对外发布时间。

**问：只保存日期够吗？**
答：日频研究可先用日期，但更严格场景要 timestamp、交易时段、时区和 snapshot captured time。

---

## 24. 可观测性与回放：怎样知道一次回答到底发生了什么

真实代码：

- `finance-workspace-private/intelligence/services/run_store.py`
- `finance-workspace-private/intelligence/api/app.py`
- `finance-workspace-private/intelligence/api/stream_events.py`
- `finance-workspace-private/intelligence/services/agent.py`
- `finance-workspace-private/intelligence/services/research_brief.py`
- `finance-workspace-private/intelligence/services/kb_rag.py`
- `finance-workspace-private/intelligence/services/closed_loop_retrieval.py`
- `finance-workspace-private/intelligence/webapp/src/App.tsx`
- `finance-workspace-private/intelligence/webapp/src/api.ts`

### 24.1 业务问题

用户只看到一段答案时，系统故障可能来自：

- Router 选错；
- Planner 漏了必要来源；
- DuckDB 查询失败；
- RAG timeout；
- index stale；
- entity anchor 错；
- LLM 调用失败；
- reviewer 发现 warning；
- 用户取消；
- 进程重启导致中断。

如果不记录中间过程，只能猜。

### 24.2 第一性原理

可观测性至少要回答：

```text
发生了什么？
什么时候发生？
由哪个输入触发？
调用了什么工具？
用了哪版数据和代码？
哪里降级？
最终输出对应哪次运行？
```

对于 Agent，还要区分：

- model decision；
- tool execution；
- final answer；
- user feedback。

### 24.3 Run 目录、append-only Trace 与 Stream

`RunStore` 使用：

```text
intelligence/users/<id>/runs/<run_id>/
  run.json
  trace.jsonl
  stream.jsonl
  answer.md / summary.json / report.json ...
```

其中：

- `run.json` 是当前 run 元数据和 artifacts 清单，由单写入者更新；
- `trace.jsonl` append-only 保存模块步骤；
- `stream.jsonl` append-only 保存有 seq 和 event id 的流事件；
- answer、summary、report 等作为 artifact 保存并记录 SHA-256。

为什么 trace/stream append-only：

- 崩溃后历史仍在；
- 不覆盖旧状态；
- 易审计；
- 每次状态转换有 trace。

为什么 `run.json` 采用当前状态快照：

- 单个 run 的元数据很小；
- 获取当前终态无需扫描整条事件流；
- 详细过程仍由 append-only trace/stream 保留。

### 24.4 状态恢复

如果服务启动时发现：

```text
queued / running
```

`requeue_incomplete_runs(...)` 会：

```text
标记 degrade reason = service_restarted
→ 状态改回 queued
→ 追加 run_recovered stream event
→ 尝试恢复 conversation run
→ 否则重新提交任务
```

因此当前真实语义是“可重排队恢复”，不是简单标成 `interrupted`。

### 24.5 SSE

API：

```text
GET /api/runs/{run_id}/events
```

以 SSE 推送：

```text
trace events
run snapshot
```

前端 `App.tsx`：

- 打开 `EventSource`；
- 解析事件；
- 更新结构化消息和 run；
- 收到 completed/failed/cancelled 后关闭；
- 同时每 2 秒 polling reconcile；
- SSE error 时标记 reconnecting，并立即做状态对账。

为什么 SSE 而不是 WebSocket：

- 当前主要是服务端单向推送；
- HTTP 语义简单；
- 浏览器原生 EventSource；
- 自动重连能力；
- 比双向 WebSocket 更轻。

什么时候需要 WebSocket：

- 双向实时交互；
- 高频控制消息；
- 多路复用复杂协议；
- 更低延迟交互。

### 24.6 Workbench step trace 与 Agent tool-call trace

Workbench 的 `api/app.py` 用：

```text
append_step(
  step_id,
  name,
  status,
  input_summary,
  output_summary,
  warnings,
  retrieval
)
```

记录：

- `ask_retrieve_compose`；
- `render_artifacts`；
- `foresight_followups`；
- 每步开始/结束、warning、retrieval 摘要。

独立的 `AgentSession` 则在工具调用循环中保存：

```text
AgentStep(
  tool,
  args,
  result_preview
)
```

默认：

```python
DEFAULT_MAX_STEPS = 6
```

每轮把 assistant tool call 和 tool result 加回 messages。步数用完后，系统会发送 tool-free final nudge 强制收尾。

步数限制的意义：

- 防止工具循环；
- 控制成本；
- 明确失败。

### 24.7 Retrieval telemetry

W 源 telemetry：

- mode；
- recall description；
- index kind；
- index dir；
- latency；
- status；
- hit count；
- neighbor hits；
- score max/min/mean；
- index built time；
- revision；
- freshness；
- degraded；
- warning。

Research telemetry：

- source distribution；
- wiki pages；
- top/mean score；
- L3 lookup items；
- L3 coverage；
- final verdict。

Closed-loop telemetry：

- aperture；
- query；
- attempt status；
- hit count；
- bucket counts；
- warnings。

D block telemetry：

- attempted；
- empty/error/ok；
- rows；
- latency；
- warning。

### 24.8 决策与最终输出分离

必须保存：

```text
QuestionPlan / route / tool calls / evidence audit
```

而不仅是最终文本。

原因：

同一证据可能被两个模型写成不同答案；
同一答案也可能来自不同证据。

如果只存文本，无法做：

- planner error analysis；
- retrieval replay；
- model A/B；
- reviewer evaluation；
- source-level attribution。

### 24.9 日志中不能有什么

不能记录：

- PAT；
- LLM API key；
- cookie；
- 完整敏感 header；
- 用户不应持久化的隐私内容。

tool args 也应做脱敏。

### 24.10 异常和降级

| 情况 | 行为 |
|---|---|
| 服务重启 | active run requeue，记录 `run_recovered`，尝试恢复/重提 |
| SSE 断开 | 标 reconnecting，同时 polling reconcile |
| 用户取消 queued run | future.cancel + cancelled |
| 用户取消 running run | cancellation signal + status cancelled |
| backend exception | run failed + error trace |
| trace/stream JSONL 坏行 | 视为数据完整性错误；当前读取并非逐行容错 |
| LLM 达到默认 6 步上限 | 强制 tool-free 收尾；无答案才失败 |
| retriever degraded | telemetry 记录，不伪装 ok |

### 24.11 评测

可观测性本身也要测：

- trace completeness；
- run terminal-state correctness；
- restart recovery；
- SSE reconnect；
- polling fallback；
- event ordering；
- correlation id coverage；
- secret leakage scan；
- telemetry schema stability；
- replay reproducibility。

### 24.12 当前边界

已实现：

- per-run `run.json` + append-only `trace.jsonl` / `stream.jsonl`；
- incomplete run requeue/resume；
- SSE；
- polling reconciliation；
- tool-call trace；
- retrieval telemetry；
- D block 统计；
- degraded reason。

不能夸大：

- JSONL 不是高并发日志数据库；
- 没有完整分布式 tracing backend；
- 没有证据表明所有内部操作都已统一 OpenTelemetry；
- 多进程并发写入和 retention 仍需更强治理；
- Workbench 默认本地，不是生产可观测平台。

### 24.13 面试表达

#### 30 秒

> 我把 Agent 运行过程作为一等数据保存，而不是只存最终答案。每个 run 有 `run.json` 当前状态、append-only 的 `trace.jsonl` 和 `stream.jsonl`，以及带 hash 的 answer/report artifacts；服务重启后未完成 run 会重新排队并记录 `run_recovered`。前端通过 SSE 看实时事件，同时用 polling 对账。这样可以区分是规划错、检索失败、模型失败还是 reviewer 降级。

#### 2 分钟

> Agent 的难点是错误会跨越路由、工具和生成多个阶段，所以最终文本不足以排障。我的 RunStore 为每个 run 保存当前 `run.json`，把模块步骤 append 到 `trace.jsonl`，把带 seq/event id 的实时事件 append 到 `stream.jsonl`，artifacts 记录 SHA-256。服务重启时 queued/running 会 requeue，并尝试恢复 conversation 或重提任务，同时追加 `run_recovered`。API 用 SSE 推送 trace 和结构化事件，前端同时定时 polling 做状态对账。检索侧还记录 mode、index revision、freshness、延迟、score、neighbor hits 和每个 narrow/broad/counter attempt，D block 记录 attempted/empty/error/ok。

---

## 25. L3 官方证据、Research Judge 与 Research Queue

真实代码：

- `finance-workspace-private/intelligence/services/l3_evidence.py`
- `finance-workspace-private/intelligence/services/research_judge.py`
- `finance-workspace-private/intelligence/services/research_queue.py`
- `finance-workspace-private/intelligence/services/forecast_preflight.py`

### 25.1 业务问题

知识库中命中“某公司受益”不代表公司已经兑现。

研究需要进一步判断：

- 是否有公告、订单、中标、量产、认证；
- 目前证据层到哪；
- 下一步最值得补什么；
- 是否可以生成正式复盘；
- 还是只能输出草稿。

### 25.2 L3 lookup 的设计

接口：

```python
def lookup_l3_evidence(
    query: str,
    plan: QuestionPlan,
    local_evidence_text: str,
    *,
    config: L3LookupConfig | None = None,
) -> L3EvidenceBundle:
```

配置：

```python
@dataclass(frozen=True)
class L3LookupConfig:
    enabled: bool = False
    company_cmd: str | None = ...
    cninfo_cmd: str | None = None
    sse_einteract_cmd: str | None = None
    timeout: int = 480
    limit: int = 5
    days: int = 30
```

### 25.3 为什么默认关闭

官方查证可能：

- 需要外部命令和环境；
- 延迟高；
- 上游不稳定；
- API 覆盖不完整；
- 不适合所有问题。

因此采用 opt-in：

- `ask --l3-lookup`；
- 或环境变量开启。

没有开启时，系统应降级结论，而不是假装查过。

### 25.4 “查不到 L3”不等于“题材没有驱动”

L3 lookup 主要判断：

> 公司端兑现度。

题材驱动可能来自：

- 行业政策；
- 上游价格；
- 竞争格局；
- 主题资金；
- 预期变化。

所以：

```text
没有公司公告
≠
没有题材逻辑
```

正确口径：

```text
题材可能存在，但公司端缺少官方兑现证据。
```

### 25.5 Research Judge

`judge_research_target(...)`：

- 查 entity exposure；
- 读取 evidence；
- 可注入 L4 market signal；
- 归类 L0-L4；
- 计算已有/缺失层；
- 给不可升级原因；
- 给下一步动作。

它不是预测裁判，而是：

> 研究成熟度和证据状态判断器。

### 25.6 Research Queue

队列：

```text
today_do_ima
today_find_official_evidence
today_wait_market_validation
today_downgrade_or_watch
```

典型逻辑：

```text
有盘面、没有基础证据
→ today_do_ima

有 L1，缺 L2/L3
→ today_find_official_evidence

有 L2/L3，缺 L4
→ today_wait_market_validation

生命周期转弱
→ today_downgrade_or_watch
```

这把“下一步研究什么”从自然语言建议变成队列。

### 25.7 Forecast Preflight

状态：

```text
ready
needs_deepdive
missing_daily_agent
```

如果：

- 没有 daily-agent research queue；
- 或仍有 `today_do_ima`；
- 或仍有 `today_find_official_evidence`；

则：

```text
can_generate_formal = False
can_generate_draft = True
```

即：

> 可以生成带缺口的草稿，但不能生成正式复盘。

### 25.8 为什么这是好的 Agent 设计

普通聊天模型会：

```text
证据不足
→ 仍给完整结论
```

Research Queue 会：

```text
证据不足
→ 转化成明确任务
→ 补证据
→ 等市场验证
→ 再升级结论
```

这使 Agent 从“答案机器”变成“研究流程系统”。

### 25.9 异常和降级

L3 subprocess 处理：

- timeout；
- OSError；
- non-zero；
- parse failure；
- no evidence；
- cache；
- warning。

Research Judge 缺关系或证据时：

- 输出 blocking reason；
- 不升级研究阶段。

Preflight 缺 daily-agent 时：

- 阻止 formal；
- 允许 gap-aware draft。

### 25.10 评测

- L3 lookup coverage；
- L3 false-positive rate；
- judge layer accuracy；
- queue action usefulness；
- formal report gate precision；
- draft-to-formal promotion time；
- unresolved blocking gap；
- 同一 target 的状态转移正确性。

### 25.11 当前边界

已实现：

- opt-in L3 lookup；
- timeout/cache/degrade；
- Research Judge；
- Research Queue；
- Forecast Preflight；
- formal vs draft gate。

不能夸大：

- L3 默认关闭；
- 外部官方数据覆盖不完整；
- Judge 不是自动预测正确性裁判；
- Queue 分类仍有启发式；
- formal gate 不代表投资结论正确，只代表研究前置条件满足。

### 25.12 面试表达

#### 30 秒

> 我把“有没有证据”进一步转成研究状态机。L3 工具可选查公告和交易所互动，用来验证公司端兑现；Research Judge 判断当前有 L1/L2/L3/L4 哪些层，Research Queue 再把缺口转成今天做 IMA、找官方证据、等盘面验证或降级观察。Forecast Preflight 在关键任务未完成时只允许生成带缺口草稿，不允许正式复盘。

#### 2 分钟

> RAG 命中只是线索，金融研究还要判断证据是否成熟。我把公司官方证据做成 opt-in L3 lookup，因为它延迟高且依赖外部命令，失败时只 warning，不影响其他来源；同时明确“查不到公告”只表示公司端未确认，不等于题材没驱动。之后 Research Judge 对目标做证据层盘点，Research Queue 把缺口转成可执行任务，比如有盘面无基础证据就做 IMA，有 L1 但缺 L2/L3 就找官方材料，有硬证据但无盘面就等市场验证。正式复盘前还有 Forecast Preflight，阻塞项未清时只能出草稿。这样系统不会把证据不足包装成完整结论。

---

## 26. 编排与风险门控：金融 Agent 为什么不能完全自由执行

真实代码：

- `finance-workspace-private/intelligence/workflows/agent_orchestrator.py`
- `finance-workspace-private/intelligence/api/app.py`
- `finance-workspace-private/intelligence/services/agent.py`
- `finance-workspace-private/intelligence/services/run_store.py`

### 26.1 业务问题

Agent 工具可能：

- 读本地文件；
- 运行脚本；
- 调外部 API；
- 生成数据；
- 导入知识；
- 修改状态。

自然语言理解出错时，如果直接执行：

- 可能使用错日期；
- 运行耗时命令；
- 写错目标；
- 重复导入；
- 产生不可逆影响。

### 26.2 第一性原理

模型的置信度不是权限。

执行权应由：

```text
意图
∩ 参数完整
∩ 工具声明
∩ 风险等级
∩ 策略阈值
∩ 用户授权
```

共同决定。

### 26.3 默认 preview

`OrchestratorOptions`：

```python
execute: bool = False
```

默认只：

- 生成计划；
- 展示命令；
- 标记风险；
- 说明 skip reason。

这是 safe-by-default。

### 26.4 自动执行门

```python
MIN_AUTO_EXECUTION_CONFIDENCE = 0.7
```

且要求：

```text
argv 存在
auto_execute = true
risk_level = low
confidence >= 0.7
skip_reason 为空
```

任何一项不满足都不执行。

### 26.5 为什么不能只看 confidence

模型可能对错误工具高度自信；
低风险工具和高风险工具也不应共用一个决策。

例如：

```text
读取只读市场快照
```

与：

```text
写知识库、删除数据、触发外部动作
```

风险完全不同。

### 26.6 Tool schema

工具有：

- name；
- description；
- JSON schema；
- handler。

schema 负责：

- 参数类型；
- required fields；
- enum；
- 默认值。

模型只产生结构化 args，真正执行前仍由程序解析。

### 26.7 取消与可恢复

Run API 支持：

- queued 取消；
- running 设置 cancellation signal；
- run 终态立即写 cancelled；
- 尝试 `future.cancel()` 取消尚未开始的任务；
- 最终 cancelled/failed/completed；
- 重启后 active run requeue/resume。

为什么不是强杀线程：

- Python 线程强杀不安全；
- 工具可能正持有文件或 subprocess；
- cooperative cancellation 更可控。

### 26.8 金融系统的风险分层建议

| 风险 | 例子 | 建议 |
|---|---|---|
| read-only low | 查询行情、读 wiki | 可在高置信时自动 |
| compute medium | 大规模重建索引、长回测 | preview + 资源限制 |
| write medium/high | 写 relations、写记忆 | dry-run + schema + review |
| external high | 发消息、交易、资金动作 | 明确人工确认 |

当前项目仍处研究员阶段，没有接交易执行。

### 26.9 当前边界

已实现：

- preview/dry-run；
- `execute=False`；
- low risk gate；
- auto_execute；
- confidence threshold；
- skip reason；
- tool schema；
- cooperative cancel。

不能夸大：

- 0.7 未必经过统计校准；
- 不是完整 RBAC/ABAC；
- 没有生产级 sandbox；
- 没有交易执行；
- 不能把研究建议说成可自动下单动作。

### 26.10 面试表达

#### 30 秒

> 我把模型规划和执行权限分开。Orchestrator 默认 `execute=False`，先输出 preview；只有工具有 argv、声明可自动执行、风险为 low、置信度至少 0.7 且没有缺参或 skip reason 时才执行。高风险或写操作需要更强的人工确认。当前系统停留在研究员层，不接交易，所以不会把自然语言观点直接转成下单。

#### 2 分钟

> Agent 的模型置信度不能等同于权限。我让每条路径有风险等级、auto_execute 声明和参数 schema，Orchestrator 默认只生成计划和命令。自动执行必须同时满足低风险、置信度阈值、参数完整和无 skip reason；用户也可取消，running 任务通过 cooperative flag 停止。这个设计把“模型认为应该做”与“系统允许做”分开。尤其金融场景里，研究、写入和交易必须是不同权限层级；当前只实现研究工作台，没有自动下单。

---

## 27. 评测与学习闭环：从一次回答到长期改进

真实代码和数据：

- `knowledge-base-private/skills/lib/rag/evaluate.py`
- `finance-workspace-private/intelligence/eval/claim_fidelity.py`
- `finance-workspace-private/intelligence/services/checkpoints.py`
- `finance-workspace-private/intelligence/services/checkpoint_resolvers.py`
- `finance-workspace-private/intelligence/services/checkpoint_recall.py`
- `finance-workspace-private/intelligence/services/corrections.py`
- `finance-workspace-private/intelligence/services/experience_cards.py`
- `finance-workspace-private/intelligence/services/user_memory.py`
- `finance-workspace-private/intelligence/users/<user>/*.jsonl`

### 27.1 业务问题

一个回答“看起来不错”无法证明：

- 检索找对了；
- 引用支持 claim；
- 没用未来信息；
- 预测后来命中；
- 用户纠偏被吸收；
- 系统没有重复犯错。

必须按层评测。

### 27.2 分层评测框架

```text
Router evaluation
→ Plan evaluation
→ Retrieval evaluation
→ Evidence evaluation
→ Generation/review evaluation
→ Historical outcome evaluation
→ Memory calibration
```

如果只看最终用户评分，无法知道改哪里。

### 27.3 检索评测

已有：

- Recall@k；
- hit@k；
- MRR；
- BM25/dense/hybrid/rerank；
- aliases；
- suffix normalization；
- recall ceiling。

建议再补：

- nDCG；
- aperture-specific recall；
- L3 source recall；
- stale hit rate；
- latency；
- no-hit reason distribution。

### 27.4 回答评测

可以看：

- citation coverage；
- citation correctness；
- evidence layer coverage；
- unsupported claim rate；
- faithfulness；
- answer spec compliance；
- counterevidence coverage；
- gap disclosure；
- output review violation rate。

### 27.5 Claim fidelity

Claim 类型：

```text
number
entity
classification
fact
inference
forecast
```

verification status：

```text
matched
mismatch
missing
unverifiable
needs_review
```

推荐阈值示例：

```text
numeric_match_rate >= 0.99
entity_classification_accuracy >= 0.95
evidence_coverage_rate >= 0.95
cutoff_violation_rate == 0
fact_inference_confusion_rate <= 0.05
```

这些是推荐契约目标，不等于当前所有历史样本已经达到。

### 27.6 历史盲测

正确盲测：

```text
冻结 T 时点输入
→ 生成 prediction/checkpoint
→ 等待 T+1/T+3/T+5
→ 获取真实 outcome
→ 记录 verdict
```

不正确：

```text
先看到结果
→ 再选择当时“看起来合理”的证据
```

### 27.7 Checkpoint

Checkpoint 应包含：

- claim；
- metric；
- operator；
- threshold；
- target date/window；
- data source；
- status。

例如：

```text
T+3 板块相对强度仍为正
T+5 出现 L3 公告或互动确认
若跌破某相对强度条件则 thesis 降级
```

可验证假设比：

```text
“后续继续关注”
```

更有评测价值。

### 27.8 Verdict

```text
hit
miss
partial
unverifiable
```

`unverifiable`：

- 数据缺失；
- 指标无法获得；
- 条件定义不清；
- PIT 无法证明。

它不应进入胜率分母。

### 27.9 Experience Card

从多次结果提炼：

```text
trigger
context
mistake pattern
evidence
lesson
applicable conditions
counterexamples
```

好的 experience card：

> 当题材强、公司只有 graph exposure 而无 L3 时，把它写成核心受益容易产生 miss；下次必须同时检查公司兑现和相对强度。

坏的 experience card：

> 不要犯错，要多看数据。

### 27.10 Correction calibration

用户纠错不应只保存原句，还要判断：

- 属于事实错误；
- 口径错误；
- 用户偏好；
- 过度自信；
- 缺反证；
- 时效问题。

然后观察后续相同 error tag 是否下降。

### 27.11 Checkpoint calibration

检查：

- checkpoint 是否按时到期；
- metric 是否可取得；
- 自动 resolver 是否可靠；
- `unverifiable` 是否过多；
- threshold 是否过宽/过窄；
- hit/miss 是否存在口径漂移。

### 27.12 评测闭环

```text
query
→ plan/retrieval/answer
→ user score/correction
→ checkpoint
→ outcome verdict
→ experience card
→ 更新 prompt/rule/retrieval/queue
→ 下一轮对比
```

注意：

> 写入 experience card 不等于系统已经自动学会。还要确保检索和策略实际会消费它。

### 27.13 指标不能混用

高 Recall@k 不等于回答可靠：

- 可能召回对页但模型没用；

高 faithfulness 不等于结论正确：

- 可能忠实复述了一篇错误研报；

高历史 hit rate 不等于无前视：

- 可能用了未来证据；

用户喜欢不等于事实正确：

- 可能只是表达符合偏好。

必须同时看：

```text
检索
× 来源质量
× claim fidelity
× PIT
× outcome
```

### 27.14 当前边界

已实现：

- RAG eval；
- output review；
- claim fidelity；
- cutoff violation；
- checkpoints；
- verdicts；
- experience cards；
- correction/checkpoint calibration 框架；
- historical replay 脚本。

不能夸大：

- 有评测框架不等于已有充分样本；
- RAG 真实效果仍需人工标注；
- 预测胜率没有充分、无偏、长期统计证明；
- 自动 verdict 只适合可确定解析的条件；
- 大量语义判断仍需人工 gold；
- unverifiable 不能被隐藏。

### 27.15 面试表达

#### 30 秒

> 我按层评测，而不是只看最终回答。检索层有 Recall@k、hit@k、MRR 和 BM25/dense/hybrid/rerank 对比；答案层看引用覆盖、证据层、claim fidelity 和 output review；历史层把结论转成 T+1/T+3/T+5 checkpoint，再记录 hit、miss、partial、unverifiable，其中 unverifiable 不进胜率分母。用户纠偏会进入 correction 和 experience card，但我会区分“已实现闭环框架”和“已有充分统计证明”。

#### 2 分钟

> Agent 评测必须拆层。Router 错和 retriever 错需要不同修复；检索命中也不代表生成忠实。因此知识库用 Recall@k、hit@k、MRR 和 recall ceiling 比较 BM25、dense、hybrid、rerank；生成侧把文本拆成 number/entity/fact/inference/forecast claim，检查证据覆盖、数字匹配和 cutoff violation；研究结论再转成有指标、阈值和窗口的 checkpoint，未来记录 hit/miss/partial/unverifiable。用户纠偏按错误类型校准，重复模式再提炼 experience card。当前我有这套工程框架，但不会声称已经有足够大的无偏样本证明预测 alpha。

---

