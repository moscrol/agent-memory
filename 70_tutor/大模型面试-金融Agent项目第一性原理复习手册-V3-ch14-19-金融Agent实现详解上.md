---
title: "大模型面试：金融 Agent 项目第一性原理复习手册（V3）第4册（章 14–19）"
type: tutor-note
agent: devin
source: "拆自 PR #21（Devin Session deebe5e092fe49579a9983ee14ca02d3）；按章节边界无损拆分自原单文件手册"
date: 2026-07-14
tags: [llm, interview, finance-agent, rag, agent, handbook]
status: draft
related: ["[[大模型面试-金融Agent项目第一性原理复习手册-V3]]"]
---

> 本册为 [[大模型面试-金融Agent项目第一性原理复习手册-V3|V3 手册]] 第 4/6 册（章 14–19），按章节边界无损拆分，正文逐行未改写；分册导航见索引页。

## 14. 端到端实现总览：一个问题怎样穿过三仓

### 14.1 三个仓库的职责边界

```text
agent-memory
  跨 Agent 的长期协作记忆与方法论资产
  Git + Markdown + YAML frontmatter + Obsidian + hooks

knowledge-base-private
  原始材料、结构知识、关系、证据与派生 RAG 索引
  raw → source/concept/entity → relations → .rag_index

finance-workspace-private
  用户问答、路由、研究编排、市场数据、证据审计、输出质检、回放评测
  question_router → answer_orchestrator → ask → review/eval
```

它们不是三个重复的“知识库”：

- Agent Memory 保存的是**用户、项目和方法论的长期上下文**；
- Knowledge Base 保存的是**外部研究材料和结构化知识**；
- Finance Workspace 保存的是**运行时市场数据、控制逻辑和研究结果**。

### 14.2 主路径

以“某公司最近为什么强，逻辑是否可持续？”为例：

```text
1. 输入 query
2. clarify_for_query 检查空问题、歧义和缺参数
3. route_question 判断 known_workflow / planner / data_gap / clarification
4. plan_answer_question 生成 QuestionPlan
5. entity_anchor 解析公司、代码、题材和 graph_query
6. 读取 S：当前盘面候选和市场快照
7. 读取 G：实体—题材暴露关系
8. 读取 R：证据索引
9. 读取 W：narrow/broad/counter 闭环 RAG
10. 按问题类型决定是否补 D0-D9 结构化数据块
11. 可选读取 M：用户历史观点，只作为 prior
12. 可选读取 V：历史预测/回检
13. 可选运行 L：官方公告/互动平台等 L3 证据
14. audit_evidence_chain 做 L1/L2/L3/L4/E 分层
15. build_retrieval_telemetry 记录命中、延迟、降级、新鲜度
16. build_counterevidence_plan 生成反证与 T+1/T+3/T+5 验证
17. 构造 AnswerSpec
18. 默认模板或可选 LLM synthesis
19. review_output 按固定顺序审稿
20. WARN 时把问题回灌给 LLM 定向修订
21. validate_llm_answer 再校验修订结果
22. 输出结论、证据链、反证、缺口、验证点、telemetry、引用
23. 运行记录进入 trace；用户反馈进入 corrections/checkpoints/verdicts
```

### 14.3 一次请求中的核心对象

| 对象 | 作用 |
|---|---|
| `RouteDecision` | 决定走已知工作流、分析规划、数据缺口或澄清 |
| `QuestionPlan` | 规定问题类型、必看视角、检索计划、质量门、输出契约 |
| `EntityAnchor` | 把自然语言实体锚定为公司、ticker、概念和图谱查询 |
| `WikiRagResult` | W 源检索命中、warning 和 telemetry |
| `ClosedLoopRetrievalResult` | narrow/broad/counter 结果及分桶 |
| `EvidenceAudit` | 证据层、缺失层和结论口径 |
| `CounterEvidencePlan` | 最强反证、降级条件和验证排期 |
| `AnswerSpec` | 最终答案必须满足的结构和约束 |
| `ReviewResult` | PASS/WARN、检查明细和修订建议 |

### 14.4 为什么要有这些中间对象

如果只有一段 prompt：

```text
问题 + 一堆 context → LLM → answer
```

你无法回答：

- 路由为什么选择了这个工具；
- 哪个来源没命中；
- 哪条结论是用户记忆，哪条是当前事实；
- 索引是否过期；
- 是检索失败还是生成失败；
- 哪条 warning 导致了修订；
- 历史回放是否用了未来证据。

显式对象的价值是把隐式推理变成可观测状态。

---

## 15. Question Router：为什么先路由，而不是直接让 LLM 自由规划

真实代码：

- `finance-workspace-private/intelligence/services/question_router.py`
- `finance-workspace-private/intelligence/workflows/agent_orchestrator.py`

### 15.1 业务问题

金融工作台收到的问题跨度很大：

- “复盘今天市场”；
- “分析某家公司”；
- “这个题材有没有机会”；
- “帮我执行某个导入命令”；
- “这句话什么意思”；
- “我没有给日期，能不能回测”。

如果所有问题都让 LLM 自由生成计划，会出现：

1. 相同问题每次选不同路径；
2. 明明已有成熟 workflow，却重新发明工具链；
3. 缺参数时仍继续执行；
4. 高风险路径被模型误调用；
5. 路由难以单测；
6. 无法稳定统计各类请求的失败率。

### 15.2 第一性原理

路由的本质不是“让模型想得更聪明”，而是：

> 在一个有限能力集合中，选择满足前置条件且风险可控的下一步。

它更接近编译器前端或 API gateway，而不是开放式写作：

```text
自然语言
→ 识别意图、实体、日期、缺口
→ 映射到有限枚举
→ 产生可检查的执行计划
```

因此确定性规则应该优先处理：

- 空输入；
- 明显歧义；
- 已知触发词；
- 必填参数；
- 风险等级；
- 已注册 workflow。

Planner 只处理规则无法完全覆盖的开放分析问题。

### 15.3 技术选型

当前采用“规则注册表 + 轻量 Planner”的混合方式，而不是纯 LLM Router。

选择理由：

1. 已知工作流数量有限，规则命中更快、更便宜、更稳定；
2. 金融执行有副作用，不能只依赖模型置信；
3. `RouteDecision` 可以单测和记录；
4. 新增 workflow 时只需扩展 registry；
5. 长尾分析问题仍可进入 Planner，不被硬规则完全限制。

没有选择纯关键词路由，因为：

- “为什么涨”和“帮我复盘这个上涨”语义相近但表达多样；
- 实体、日期、目标可能组合出现；
- 长尾问题需要拆解。

没有选择纯 LLM function calling，因为：

- 输出仍可能缺参数或误选；
- 风险门禁不能由模型自证；
- 每次调用增加延迟和成本；
- 路由错误会污染后续全部检索。

### 15.4 真实数据结构

四种路由：

```python
ROUTE_KNOWN = "known_workflow"
ROUTE_PLANNER = "planner_analysis"
ROUTE_DATA_GAP = "data_gap"
ROUTE_CLARIFICATION = "clarification_needed"
```

入口：

```python
def route_question(
    query: str,
    registry: list[PathSpec] | None = None,
) -> RouteDecision:
```

`RouteDecision` 记录：

- `query`
- `route_type`
- `confidence`
- `selected_paths`
- `plan_steps`
- `missing_data_checks`
- `next_action`
- `warnings`

这使路由结果不是一句自然语言，而是下游可消费的协议。

### 15.5 真实路由行为

#### 空问题

```text
route_type = clarification_needed
confidence = 0.1
next_action = ask_user_to_clarify
```

原因：没有足够信息，最正确的行为不是猜。

#### 模糊问题

先调用 `clarify_for_query` 识别：

- 标的是谁；
- 日期是什么；
- 想要复盘、预测还是解释；
- 是快速回答还是深挖。

#### 显式数据缺口

命中 data-gap trigger 时：

```text
route_type = data_gap
```

下游优先检查数据，而不是让模型凭常识补全。

#### 分析型问题

“为什么”“怎么看”“有没有机会”等进入：

```text
route_type = planner_analysis
```

Planner 抽取实体、日期、目标并生成步骤。

#### 已知工作流

已知 trigger 命中：

```text
route_type = known_workflow
```

如果意图较弱，代码给出较低置信度，例如 `0.55`，并建议 preview，而不是直接执行。

### 15.6 与执行编排的连接

命令型路径由：

```python
run_agent_orchestrator(options)
```

管理。

关键配置：

```python
MIN_AUTO_EXECUTION_CONFIDENCE = 0.7
```

真正可自动执行必须同时满足：

```python
bool(item.argv)
and item.auto_execute
and item.risk_level == "low"
and confidence >= MIN_AUTO_EXECUTION_CONFIDENCE
and not item.skip_reason
```

默认：

```python
execute: bool = False
```

所以系统行为是：

```text
先规划
→ 展示 argv / preview
→ 检查风险、参数和置信度
→ 满足门禁才执行
```

### 15.7 异常和降级

| 情况 | 行为 |
|---|---|
| query 为空 | 请求澄清 |
| 实体/日期缺失 | 进入 clarification 或 data_gap |
| 命中 workflow 但置信低 | preview，不自动执行 |
| workflow 缺 argv | 不执行，记录 skip reason |
| 风险不是 low | 不自动执行 |
| confidence < 0.7 | 不自动执行 |
| `execute=False` | 只返回计划和命令 |

关键思想：

> 不确定性不能被流畅文本掩盖，必须转化成显式路由或 skip reason。

### 15.8 评测方式

Router 应评测：

1. route accuracy：人工标注问题应走哪条路；
2. clarification precision：真正缺信息时才追问；
3. unsafe execution rate：不应执行却执行的比例，目标必须接近 0；
4. unnecessary planner rate：已有 workflow 却进入自由规划的比例；
5. coverage：多少问题能映射到稳定路径；
6. latency：规则路径与 Planner 路径的延迟差。

当前代码具备可记录和可单测结构，但不能声称已经有大规模线上标注路由集。

### 15.9 当前边界

已实现：

- 四类路由；
- `RouteDecision`；
- clarification 和 data gap；
- 已知 workflow 注册；
- Planner 路径；
- preview 和自动执行门禁。

不能夸大：

- 不是训练出的专用金融 Router 模型；
- 没有已核实的大规模路由 accuracy 报告；
- 规则与触发词仍可能对长尾表达不够鲁棒；
- Planner 的语义判断仍需通过后续 evidence gate 约束。

### 15.10 面试表达

#### 30 秒

> 我没有让 LLM 一上来就自由规划，而是先做有限状态路由。空问题、缺参数、已知 workflow 和明显 data gap 由确定性规则处理，开放分析问题才进入 Planner。路由输出是结构化 `RouteDecision`，后续执行还要经过低风险、`auto_execute`、置信度大于 0.7 和无缺参等门禁，默认只 preview。这样做的目标不是让模型更自由，而是让行为可预测、可单测、可审计。

#### 2 分钟

> 金融 Agent 既有问答，也可能触发数据导入、复盘等命令路径。如果纯靠 LLM function calling，相同表达可能走不同工具，而且缺参数、高风险和低置信度都可能被一段看似合理的计划掩盖。我先把路由问题形式化成四种状态：`known_workflow`、`planner_analysis`、`data_gap`、`clarification_needed`。规则优先命中确定性强的情况，Planner 只处理长尾分析；输出包含 selected paths、plan steps、missing data checks、next action 和 warnings。命令层默认 `execute=False`，只有 argv 存在、路径声明可自动执行、风险为 low、置信度至少 0.7 且没有 skip reason 才允许执行。这样即使模型判断错了，也不会直接转化成高风险动作。

#### 追问

**问：为什么不用一个强模型直接路由？**
答：路由是有限决策和风险控制问题，不是生成质量问题。强模型可以提高语义覆盖，但不能替代参数检查、权限、风险和确定性门禁。

**问：规则越来越多会不会难维护？**
答：会，所以规则只覆盖稳定高精度意图，长尾进入 Planner；通过 route distribution 和误路由样本决定是否新增规则，而不是无限堆关键词。

**问：0.7 怎么来的？**
答：当前是工程阈值，不应说成统计校准后的最优值。正式上线应在标注集上做 reliability calibration，并按动作风险设置不同阈值。

---

## 16. Answer Orchestrator：把自然语言问题编译成研究计划

真实代码：

- `finance-workspace-private/intelligence/services/answer_orchestrator.py`
- `finance-workspace-private/intelligence/services/ask.py`

### 16.1 业务问题

即使 Router 已判断“这是分析问题”，仍然不知道：

- 是个股深挖、题材分析、市场复盘还是估值；
- 必须看哪些证据；
- 哪些来源优先；
- 是否允许快速回答；
- 数据缺失时怎样表述；
- 最终答案必须包含哪些 section。

如果直接把所有工具结果拼进 prompt：

1. 不同问题拿到相同 context，噪声很大；
2. 估值问题可能没有财务数据；
3. 市场复盘可能被历史 memory 带偏；
4. 快答可能错误地跳过关键检索；
5. 输出结构不可控。

### 16.2 第一性原理

研究型问答可以看成一个受约束查询计划：

```text
Question
→ classify intent
→ determine required evidence lenses
→ plan retrieval
→ declare quality gates
→ declare output contract
→ execute
```

这与数据库 query planner 相似：

- 用户只描述“要什么”；
- Planner 决定“要查哪些源、以什么顺序、满足什么条件”；
- 执行器负责真正取数；
- Validator 检查结果。

### 16.3 技术选型

选择 `QuestionPlan` 作为显式中间表示，而不是把规划藏在 prompt 里。

原因：

1. 可序列化、可记录、可回放；
2. 不同问题类型可复用下游执行器；
3. quality gates 与输出契约不会因模型措辞漂移；
4. 数据缺口策略可提前声明；
5. 可对 plan 本身做单测。

### 16.4 `QuestionPlan`

```python
@dataclass(frozen=True)
class QuestionPlan:
    query: str
    question_type: str
    depth: str
    confidence: float
    required_lenses: list[str]
    retrieval_plan: list[str]
    quality_gates: list[str]
    output_contract: list[str]
    missing_data_policy: list[str]
    warnings: list[str]
    research_spec: ThemeResearchSpec | None
    base_finance_mode: BaseFinanceMode | None
```

注意：

> `QuestionPlan` 不直接执行工具。它告诉下游这是什么问题、必须看什么、优先取什么证据、答案要满足什么约束。

### 16.5 问题类型

```text
stock_deep_dive
theme_analysis
market_review
market_forecast
news_impact
valuation_estimate
financial_analysis
answer_review
methodology_discussion
general_finance_qa
```

为什么要区分：

- 个股深挖要看公司本体、题材暴露、L3 兑现和同链对比；
- 市场复盘要看指数、涨跌家数、题材强度和扩散；
- 估值要看财务、假设、敏感性和数据日期；
- 新闻影响要区分事件、传导链、受益/受损对象和时间窗口；
- 方法论讨论不应假装需要实时行情。

### 16.6 `required_lenses`

它表达“必须从哪些角度看”，例如：

```text
公司本体
题材暴露
证据硬度
盘面验证
同链替代
估值
反证
验证窗口
```

作用是防止模型只沿着最显眼的叙事回答。

比如“某公司是否受益于液冷”，不能只看：

```text
公司名称和液冷同时出现在一篇文章
```

还要看：

- 公司具体产品是什么；
- 是否有订单、认证、量产等 L3；
- 题材涨但公司是否跟涨；
- 同链是否有更纯的标的；
- 估值是否已经反映预期。

### 16.7 `retrieval_plan`

它声明优先访问哪些源，而不是把全部源无差别塞入上下文。

例如：

```text
stock_deep_dive
→ S 当前盘面
→ G 公司—概念暴露
→ R 已登记证据
→ W 语义和上下游扩展
→ L 官方硬证据
→ D 财务/历史结构化数据
→ M/V 只做先验和复盘
```

### 16.8 `BaseFinanceMode`

它进一步记录：

- 是否必须有行情；
- 是否必须有历史记忆；
- 是否必须有新闻；
- 是否必须有图谱；
- 是否必须有财务；
- 是否允许 quick answer。

这里的关键设计是：

> quick answer 只缩短表达，不能跳过已经触发的必要检索。

否则“快答”会变成“少查证据但语气一样确定”。

### 16.9 `quality_gates`

质量门可以包括：

- 本地数据是否新鲜；
- 是否存在支持核心结论的证据；
- 是否区分硬事实和候选；
- 是否写出反证；
- 是否显式说明缺口；
- 是否有验证窗口；
- 是否有引用；
- 是否违反 AnswerSpec。

### 16.10 `output_contract`

输出不是任意 prose，而应包含固定语义区：

```text
结论
证据链
分歧 / 反证
缺口
后续验证点
交易含义或研究含义
引用
```

固定 section 的价值：

1. 用户能快速比较不同回答；
2. reviewer 能按字段检查；
3. 历史结果能结构化评测；
4. 缺口不会被藏在段落末尾。

### 16.11 `missing_data_policy`

真实原则：

```text
缺数字
→ 先明确缺什么
→ 如有合理替代锚点则给区间/代理变量
→ 仍不足时写：
   缺 X
   仍可判断 Y
   不能判断 Z
   验证窗口为 T
```

不能做的是：

```text
没有营收、订单或估值数据
→ 用“行业空间广阔”补成确定性结论
```

### 16.12 在 `ask.py` 中如何落地

`ask.py` 先生成 plan，再据此决定：

- 是否做 entity anchor；
- 是否查 G/R/W；
- 是否启用 compose；
- 要运行哪些 D block；
- 是否需要 L3；
- AnswerSpec 包含哪些字段；
- review 要检查什么。

所以：

```text
answer_orchestrator = 规划层
ask.py = 执行与组装层
output_review = 审稿层
```

### 16.13 异常和降级

| 情况 | 处理 |
|---|---|
| 问题类型置信低 | 加 warning，采用 general plan 或请求澄清 |
| 必要行情缺失 | 标 gap，不伪造实时判断 |
| 财务数据缺失 | 使用假设区间或停止给精确估值 |
| 图谱无实体 | 触发 entity/alias gap |
| W 失败 | S/G/R 继续，W 显式 degraded |
| L3 未开启或失败 | 结论降级为预期交易/候选，不说事实验证 |

### 16.14 评测

可以建立 plan-level gold set：

```json
{
  "query": "某公司现在贵不贵",
  "question_type": "valuation_estimate",
  "required_lenses": ["financial", "valuation", "assumption", "risk"],
  "required_sources": ["D"],
  "must_not": ["use_memory_as_current_fact"]
}
```

指标：

- question type accuracy；
- required lens recall；
- unnecessary source rate；
- missing mandatory source rate；
- plan-to-execution consistency；
- output contract compliance；
- data-gap honesty rate。

当前具备结构化 plan 和代码路径，但不能声称已经完成大规模 plan benchmark。

### 16.15 当前边界

已实现：

- 多种问题类型；
- `QuestionPlan`；
- required lenses；
- retrieval plan；
- quality gates；
- output contract；
- missing data policy；
- `BaseFinanceMode`；
- `ask.py` 消费 plan。

不能夸大：

- 不是经过强化学习训练出的 Planner；
- 不是通用 DAG optimizer；
- 部分问题分类仍依赖规则和启发式；
- plan 质量仍需真实 query set 验证。

### 16.16 面试表达

#### 30 秒

> Router 只决定走哪类路径，进入问答后我还设计了 `QuestionPlan`，相当于把自然语言问题编译成研究执行计划。它显式记录问题类型、必看视角、检索源、质量门、输出契约和缺数据策略。比如估值问题必须要财务和假设，个股深挖必须看公司本体、题材暴露、L3 兑现、盘面和反证。这样快答只能缩短表达，不能偷掉必要检索。

#### 2 分钟

> 我把问答编排拆成规划层和执行层。`answer_orchestrator.py` 产生不可变的 `QuestionPlan`，它不直接调用工具，而是声明 question type、required lenses、retrieval plan、quality gates、output contract 和 missing data policy；`ask.py` 再根据它执行 S/G/R/W/M/V/D/L 多源召回。这样做类似数据库 query plan：先明确要满足什么，再决定访问哪些数据。好处是同一个执行器可服务不同问题，缺数据时也有预先约定的降级口径。例如缺精确估值数字时，不允许模型编造，而要写清缺 X、仍可判断 Y、不能判断 Z、验证窗口是什么。

#### 追问

**问：Plan 会不会过度工程化？**
答：一次简单聊天可能不需要，但金融研究需要跨源证据、风险和回放。显式 plan 带来的可测试性和审计价值高于对象开销。

**问：为什么不用 LangChain/LangGraph？**
答：当前核心需求是轻量、确定性、可读的本地编排，现有 dataclass 和 Python 模块已足够。若工作流演进成大量持久化节点、人工中断和复杂恢复，再评估图编排框架。

---

## 17. 多源证据模型：S/G/R/W/M/V/D/L 为什么必须分开

真实代码和资料：

- `finance-workspace-private/intelligence/services/ask.py`
- `finance-workspace-private/intelligence/services/research_brief.py`
- `finance-workspace-private/intelligence/services/source_credibility.py`
- `finance-workspace-private/intelligence/services/claim_lineage.py`
- `knowledge-base-private/wiki/relations/`

### 17.1 业务问题

“某公司受益于某题材”可能来自完全不同的东西：

1. 今天股价很强；
2. 图谱中公司和题材有关联；
3. 卖方研报说它受益；
4. 公司公告已有订单；
5. 用户以前认为它会受益；
6. 历史上类似判断命中过；
7. DuckDB 显示它连续多日跑赢板块。

这些不能都叫“证据”而不标类型。

否则系统会犯三种典型错误：

- 把**市场表现**当成**基本面事实**；
- 把**研报推演**当成**公司兑现**；
- 把**用户历史观点**当成**当前市场事实**。

### 17.2 第一性原理

证据至少有三个独立维度：

```text
来源是什么？
信息硬度多高？
在当前时点是否新鲜、可得？
```

因此不能用一个无标签的 `context` 字符串承载全部信息。

### 17.3 八类来源

#### S：盘面快照

Snapshot / Screen：

- 当前市场日期；
- 题材候选；
- 强弱、涨跌、热度；
- 盘面是否验证叙事。

它回答：

> 市场现在是否在交易这个逻辑？

它不能单独回答：

> 公司是否真的有订单或产能。

#### G：图谱

Graph：

- 公司—概念；
- 实体暴露；
- 产业链关系；
- 别名与 ticker；
- 结构化候选关系。

它回答：

> 哪些实体可能有关联，关系是什么。

它不一定代表关系已被硬证据验证。

#### R：证据索引

Relations / evidence index：

- 已登记证据；
- source trace；
- evidence layer；
- 关系对应的材料。

它回答：

> 这条关系目前有哪些可追溯依据。

#### W：Wiki RAG

Wiki semantic retrieval：

- 未必已入结构图谱的相关页面；
- 同义表达；
- 上下游、同业、竞争格局；
- 反方线索。

它回答：

> 知识库里还有哪些可能相关的候选材料。

W 命中默认首先是 candidate，不应自动升级成事实。

#### M：用户记忆

Memory：

- 用户历史判断；
- 偏好；
- 纠偏；
- experience card；
- 过往关注框架。

它回答：

> 用户过去怎样理解这个问题，系统应避免重复犯什么错。

它不能回答：

> 今天的价格、订单、产能和公告是什么。

#### V：历史回检

Verification：

- 过去判断；
- checkpoint；
- hit/miss/partial/unverifiable；
- 何种条件下结论曾失败。

它回答：

> 类似推理在历史上表现如何，有什么校准信息。

#### D：DuckDB 数据块

Deterministic structured data：

- 行情；
- 财务；
- 题材热度；
- 市场宽度；
- 历史时序；
- 多日趋势；
- L2 资金等。

它回答：

> 可由 SQL 和确定性计算得到的数字事实是什么。

#### L：L3 官方证据工具

Live / L3 lookup：

- 公司公告；
- 交易所披露；
- 互动易 / e互动；
- 订单、认证、量产、扩产等官方事实。

它回答：

> 公司端兑现是否有硬证据。

### 17.4 为什么不把所有来源放进一个向量库

结构化市场数据放进向量库会损失：

- 精确数值；
- 日期过滤；
- 排序和聚合；
- PIT 截断；
- schema 约束；
- 可重算性。

用户记忆放进同一事实库会造成：

- 旧观点和新事实混召；
- 来源难区分；
- 个性化偏好污染公共事实。

官方公告和研报如果不分层，会造成：

- “券商预计”被写成“公司已经”；
- screenshot 和公告拥有相同权重。

所以你的设计不是“多拿一些 context”，而是“保留来源类型直到最终 claim”。

### 17.5 来源优先级

可以用以下口径解释：

```text
数字事实：
D / 官方结构数据 > W 文本描述 > M 历史记忆

公司兑现：
L3 官方公告/定期报告 > 交易所互动 > 深度研报 > 晨会转述 > 社媒截图

当前盘面：
S / D 当前行情 > 历史 V > M 历史观点

关系发现：
G/R 已登记关系 > W 语义候选 > M 用户假设
```

`source_credibility.py` 中的轻量先验：

```text
official_announcement 0.95
periodic_report       0.90
exchange_interaction  0.80
sellside_deep         0.60
morning_note          0.45
pdf_ocr               0.35
social_screenshot     0.20
```

注意：

> 这只是来源可信度先验，不等同于语义真伪模型，也不能替代具体 claim 核验。

### 17.6 证据层 L1/L2/L3/L4/E

在 `research_brief.py` 中，证据会按来源和文本特征分类。

可用面试口径：

| 层 | 含义 |
|---|---|
| L1 | 方向、主题、逻辑线索 |
| L2 | 产业或公司层的较具体基线/推演 |
| L3 | 公告、订单、中标、量产、认证等公司硬证据 |
| L4 | 当前市场价格与盘面验证 |
| E | 用户经验、历史判断、方法论 prior |

核心裁定：

- 有 L3：可以说“事实验证”，但仍要看时效和口径；
- 有 L1/L2、无 L3：只能说“预期交易”；
- 只有 L4：更像“情绪脉冲”；
- 没有有效证据：说“证据不足”。

真实代码原则：

```python
if has_l3:
    verdict = "事实验证"
elif has_l1_or_l2:
    verdict = "预期交易"
elif only_l4:
    verdict = "情绪脉冲"
else:
    verdict = "证据不足"
```

### 17.7 Memory 只能作为 prior

正确融合：

```text
用户历史观点：
“我之前认为 A 是液冷核心标的”

当前系统：
1. 把它作为待检验 hypothesis；
2. 查 G/R/W/L/D；
3. 若硬证据不支持，明确冲突；
4. 不能因为是用户自己的历史观点就提高为事实。
```

错误融合：

```text
M 中出现“有订单”
→ 直接在答案中写“公司已有订单”
```

### 17.8 Claim lineage

`claim_lineage.py` 将最终 claim 与 evidence refs 连接：

- evidence id；
- source catalog；
- claim manifest；
- field path；
- valid time；
- evidence refs；
- 数字事实与 narrative claim 分离。

本质：

```text
不是只在回答末尾列一堆引用，
而是尽可能知道“哪条 claim 由哪条 evidence 支持”。
```

这比 document-level citation 更强，因为一篇长文可能只支持其中一个数字，不支持整段推论。

### 17.9 数据流示例

问题：

> “某公司是不是液冷核心受益？”

系统可能得到：

```text
G：公司与液冷有 graph exposure
R：证据索引有一篇卖方深度
W：召回公司产品、上游材料和竞争对手
L：没有公告/订单/量产类 L3
S：当天股价跟随板块走强
D：过去 5 日相对强度上升
M：用户过去把它列为候选
V：历史类似判断有一次 partial
```

合理结论：

```text
它是“有产业关联、且当前盘面在交易”的候选，
但缺少 L3 公司兑现证据，不能写成已确认核心受益。
后续看公告/互动、相对强度和板块扩散。
```

不合理结论：

```text
公司是液冷核心，订单确定性高。
```

### 17.10 异常和降级

| 缺失 | 结论降级 |
|---|---|
| 无 S/D | 不判断当前市场是否验证 |
| 无 G | 可能是新词、别名或尚未入图 |
| 无 R | 关系缺可追溯证据 |
| W 失败 | 不影响已有确定性源，但减少语义扩展 |
| 无 L3 | 不写“事实验证” |
| M 缺失 | 不影响公共事实回答 |
| V 缺失 | 不能做历史校准 |
| source date 不明 | 标 freshness unknown，不作为强事实 |

### 17.11 评测

多源证据层应看：

- source hit distribution；
- 每类问题的 mandatory source coverage；
- L3 coverage；
- citation coverage；
- claim-evidence alignment；
- unsupported claim rate；
- memory-as-fact violation rate；
- stale evidence rate；
- degraded response rate；
- counterevidence coverage。

### 17.12 当前边界

已实现：

- S/G/R/W/M/V/D/L 的代码与语义分工；
- evidence audit；
- source credibility 先验；
- retrieval telemetry；
- claim lineage 框架；
- 缺 L3 时的降级口径。

不能夸大：

- 不是所有输出 claim 都已完成人工验证的 claim-level 对齐；
- source credibility 分数是启发式先验；
- L3 lookup 默认关闭，并非每次问答都实时查官方来源；
- W 命中仍是候选，检索相关不等于事实成立；
- 完整 Temporal Facts 状态边尚未贯穿 `ask` 全链。

### 17.13 面试表达

#### 30 秒

> 我把上下文按来源拆成 S/G/R/W/M/V/D/L，而不是混成一段 prompt。S 是盘面，G 是图谱，R 是证据索引，W 是 wiki RAG，M 是用户记忆，V 是历史回检，D 是 DuckDB 结构数据，L 是官方 L3 查证。然后再按 L1/L2/L3/L4/E 做证据硬度分层。这样用户记忆只能做 prior，研报推演不能升级成公司事实，盘面上涨也不能等同于基本面兑现。

#### 2 分钟

> 金融场景最大的风险不是没有信息，而是不同语义的信息被混写。例如股价上涨、图谱关联、研报判断、公司公告和用户过去观点都可能指向同一结论，但证据强度完全不同。我让每个来源保留标签直到最终 claim：结构化数字优先由 D 提供，公司兑现优先由 L3 官方证据提供，W 负责语义候选和上下游扩展，M/V 只负责个性化先验与历史校准。`research_brief.py` 再把证据分为 L1/L2/L3/L4/E：只有 L3 才能把口径提升到事实验证，只有盘面就是情绪脉冲，有产业逻辑但无 L3 只能写预期交易。最后通过 claim lineage 把 claim 与 evidence ref 连接，避免回答末尾列了引用但实际没有支持具体结论。

#### 追问

**问：多个来源冲突怎么办？**
答：先按事实类型选权威源，再按时间和 evidence layer 判断；冲突本身进入“分歧/反证”，不能由模型静默平均。

**问：可信度 0.95 是否表示 95% 正确？**
答：不是，它是来源类型先验，不是校准概率。具体 claim 仍需内容、时间和实体一致性检查。

**问：图谱和 RAG 有什么区别？**
答：图谱适合已知实体关系的确定性查询，RAG 适合语义发现和未结构化候选；RAG 可发现线索，图谱提供稳定结构，二者互补。

---

## 18. Knowledge Base RAG：从原始材料到可引用候选页

真实代码和资料：

- `knowledge-base-private/README.md`
- `knowledge-base-private/skills/material-router/SKILL.md`
- `knowledge-base-private/skills/entity-delta-ingest/SKILL.md`
- `knowledge-base-private/skills/lib/rag/chunking.py`
- `knowledge-base-private/skills/lib/rag/retrieval.py`
- `knowledge-base-private/skills/lib/rag/store.py`
- `knowledge-base-private/skills/lib/rag/embedder.py`
- `knowledge-base-private/skills/lib/rag/rerank.py`
- `knowledge-base-private/skills/lib/rag/evaluate.py`
- `knowledge-base-private/scripts/rag_index.py`
- `finance-workspace-private/intelligence/services/kb_rag.py`

### 18.1 业务问题

金融知识库有几个难点：

1. 股票代码、公司名、产品名要求精确匹配；
2. 同一概念有中英文、简称和别名；
3. 研报会用不同措辞描述相同逻辑；
4. 一篇长报告包含多个主题，整页 embedding 噪声大；
5. 直接向量召回容易漏掉代码，纯关键词又漏同义表达；
6. 材料持续更新，旧索引可能引用已变更内容；
7. 检索命中不等于事实成立，还要保留来源和证据层。

### 18.2 第一性原理

RAG 不是：

```text
文档 → embedding → top-k → prompt
```

而是一个信息检索系统：

```text
内容治理
→ 切块
→ 索引
→ 候选召回
→ 融合
→ 扩展
→ 重排
→ 新鲜度检查
→ 引用绑定
→ 离线评测
```

检索的目标也不是“找到看起来相关的文字”，而是：

> 在有限上下文预算内，提高支持当前任务的证据被召回的概率，并保留足够元数据供后续核验。

### 18.3 从 raw 到 wiki

知识库流程：

```text
外部材料
→ raw/ 不可变归档
→ wiki/sources 来源页
→ wiki/concepts 概念页
→ wiki/entities 实体页
→ wiki/synthesis / briefings 综合页
→ wiki/relations 结构关系
→ .rag_index 派生索引
→ finance kb_rag.py 只读消费
```

`material-router` 把内容分层：

- N1：源索引；
- N2：概念层；
- N3：实体层；
- N4：信号轨；
- N5：催化池。

为什么 `raw` 不直接等于事实：

- 原始材料可能是卖方观点、OCR、转述；
- 必须保留 provenance；
- 需要判断哪些内容能进入 entity 硬事实，哪些只能进入 graph candidate；
- source note 与 entity page 的语义等级不同。

### 18.4 为什么 Markdown + YAML frontmatter

选择原因：

1. 人类可读，可在 Obsidian 审阅；
2. Git 可 diff、回滚和审计；
3. YAML 提供机器可解析元数据；
4. Markdown 标题天然适合 section chunking；
5. `[[wikilink]]` 可作为轻量图关系；
6. 不被专用向量数据库格式锁定。

frontmatter 可承载：

- title；
- tags；
- source；
- source type；
- publish/available time；
- evidence layer；
- ticker；
- revision；
- provenance。

### 18.5 Chunking 的真实实现

`Chunk`：

```python
@dataclass
class Chunk:
    id: str
    file_path: str
    page_type: str
    title: str
    tags: list[str]
    section: str
    wikilinks: list[str]
    text: str
    content_hash: str
    mtime: float
    page_id: str
```

`chunk_file(path, vault_root)`：

1. 解析 YAML frontmatter；
2. 获取 title 和 tags；
3. 提取 wikilinks；
4. 按 Markdown heading 构造 breadcrumb；
5. 按 section 切；
6. 超长 section 再按段落切；
7. 增加约 15% overlap；
8. 给正文增加 title/tags/section 前缀；
9. 计算 SHA-1 content hash；
10. 生成稳定 chunk id。

配置口径：

```text
TARGET_TOKENS ≈ 768
MAX_TOKENS ≈ 1024
OVERLAP_RATIO ≈ 15%
```

### 18.6 为什么按 section 切，而不是固定字符

固定 500 字符可能把：

```text
“风险因素”标题
```

与下一段正文拆开，或者把：

```text
公司产品、客户、风险
```

混在同一块。

按 section 的优势：

- 保留语义边界；
- breadcrumb 给 chunk 上下文；
- 引用时能指出具体 section；
- 对结构化 Markdown 友好。

过长 section 再按段落切，是为了控制 embedding 和 rerank 输入长度。

### 18.7 Dense 召回

`BGEM3Embedder`：

```python
BGEM3FlagModel
return_dense=True
return_sparse=False
return_colbert_vecs=False
```

输出：

- dense 1024 维；
- L2 normalize；
- 查询与 chunk 可用点积做 cosine 等价相似度。

为什么选择 BGE-m3：

- 中文能力较强；
- 支持较长文本；
- 本地可运行；
- 同一模型接口具备 dense/sparse 能力；
- 与 bge reranker 生态兼容。

### 18.8 必须纠正的口径：实际 lexical 是独立 BM25

虽然 `BGEM3Embedder` 实现了：

```python
encode_sparse(...)
```

但当前真实 RAG 主路径中的 lexical 召回是：

```python
rank_bm25.BM25Okapi
```

即：

```text
BGE-m3 dense
+
独立 rank_bm25 lexical
```

不能说成：

> 当前生产链路已经使用 BGE-m3 dense+sparse 联合检索。

准确说法：

> BGE-m3 提供 dense embedding；代码预留了 sparse 接口，但实际 hybrid 的关键词支路由独立 `rank_bm25` 实现。

这是项目深挖时很能体现诚实度的细节。

### 18.9 为什么保留 BM25

Dense 擅长语义，但对以下内容不总稳定：

- `002636`；
- 特定产品型号；
- 生僻公司名；
- 精确公告术语；
- 缩写和 ticker。

BM25 利用词频和逆文档频率，适合精确 lexical signal。

中文 tokenizer 采用：

- 汉字单字；
- bigram；
- 拉丁和数字段保留；
- 不依赖 jieba。

优点：

- 确定性；
- 零额外词典；
- 股票代码不会被破坏；
- CI 可离线运行。

### 18.10 Hybrid pipeline

真实链路：

```text
dense top-80
∪
BM25 top-80
→ exact entity/code/wikilink boost
→ RRF
→ page aggregation
→ one-hop wikilink neighbor expansion
→ optional cross-encoder rerank top-50
→ top-k pages
```

关键配置：

```text
DENSE_TOPN = 80
BM25_TOPN = 80
RRF_K = 60
BOOST_WEIGHT = 0.5
NEIGHBOR_DISCOUNT = 0.25
RERANK_CANDIDATES = 50
```

### 18.11 为什么用 RRF，而不是直接相加分数

Dense score 和 BM25 score 不在同一量纲：

- dense 可能在 cosine 范围；
- BM25 分值取决于语料和词频；
- 不同查询分布也不同。

直接：

```text
dense_score + bm25_score
```

需要复杂归一化。

RRF 只依赖排名：

\[
RRF(d)=\sum_i \frac{1}{k+r_i(d)}
\]

真实代码：

```python
scores[idx] += 1.0 / (RRF_K + rank + 1)
```

优点：

- 简单；
- 对不同分数量纲鲁棒；
- 同时被多个召回器排前的结果自然加权；
- 适合 POC 和中小规模系统。

### 18.12 Exact-match boost

`_query_entities` 会识别：

- `[[wikilink]]`；
- 六位股票代码；
- query 中直接出现的 page id / title。

然后对匹配 title、tag、wikilink 的 chunk 加 boost。

第一性原因：

> 精确实体命中是强先验，不应该被语义相似但主体错误的文档压过。

### 18.13 Wikilink 一跳邻居

Hybrid 先找到 seed pages，再沿 `[[wikilink]]` 扩展一跳。

用途：

- 公司页链接到概念页；
- 概念页链接到产业链；
- source page 链接到 entity；
- 可以补回 lexical/dense 没直接命中的结构相关页。

邻居分数：

```text
seed.score × NEIGHBOR_DISCOUNT
```

为什么只做一跳：

- 多跳很快引入图扩散噪声；
- 一跳保留直接语义关系；
- 计算和解释更简单。

### 18.14 Reranker

默认模型：

```text
BAAI/bge-reranker-v2-m3
```

实现：

```python
AutoModelForSequenceClassification
query + passage
→ single logit
→ sigmoid
```

只重排 hybrid 前 50 个候选。

为什么不是全库 cross-encoder：

- cross-encoder 要对每个 query-document pair 联合编码；
- 精度更高但成本远高于 bi-encoder；
- 先召回再重排是典型两阶段架构。

为什么 rerank 不提高 recall ceiling：

> 它只能重排已召回候选；如果正确页面根本不在候选池，reranker 无法创造它。

### 18.15 两种索引模式

`kb_rag.py` 支持：

```text
structured
  .rag_index
  hybrid

full
  .rag_index_full
  rerank
```

结构版：

- 主要索引结构化 wiki；
- 速度较快；
- 日常问答默认。

全文版：

- 可包含 raw 全文；
- 候选多、噪声大；
- 适合“深挖、看原文、权威、全文”等请求；
- 默认建议 rerank。

### 18.16 索引存储

`.rag_index/`：

```text
chunks.jsonl
dense.npy
meta.json
bm25_tokens.jsonl.gz
```

为什么当前没用专用向量数据库：

- 万级 chunk 可用 NumPy 暴力点积；
- 本地个人工作台；
- 简化依赖和运维；
- 索引是可重建派生产物；
- JSONL/NumPy 易检查。

什么时候应换：

- chunk 到百万级；
- 多用户并发；
- 需要分布式 ANN；
- 需要在线增删与 metadata filter SLA；
- 需要多租户隔离。

### 18.17 增量更新

`store.py` 按：

```text
chunk id + content_hash
```

复用未变化向量，只重嵌新增或变化 chunk。

为什么不能只看 mtime：

- 文件复制可能改变 mtime 但内容不变；
- Git checkout 可能重置 mtime；
- content hash 更接近真实内容变化。

### 18.18 索引新鲜度

新版本使用参与索引文件的 manifest revision：

```text
manifest:v1:<hash>
```

当前内容与 index build 时内容不一致：

```text
stale
```

旧指纹无法安全判定：

```text
unknown
```

原则是 fail-closed：

> 无法证明 fresh，不返回可能错误的 fresh。

`rag_index.py query` 支持：

```text
--stale-policy fail
--stale-policy warn
--stale-policy ignore
```

`kb_rag.retrieve(..., require_fresh=True)` 在正式问答中会：

- 丢弃 stale；
- 丢弃 unknown；
- 只让 fresh hit 进入证据；
- 记录 degraded warning。

### 18.19 跨仓调用

Finance Workspace 不复制 RAG 实现，而是：

```text
kb_rag.py
→ subprocess
→ knowledge-base/scripts/rag_index.py query --json
```

为什么这样做：

- 知识库拥有索引和 chunking 的 single source of truth；
- 金融仓只做消费；
- 两个仓可独立演进；
- 失败可以局部降级，不破坏 S/G/R。

代价：

- subprocess 有启动延迟；
- 环境和路径需配置；
- JSON 协议必须稳定；
- 多次 aperture 检索会重复启动进程。

### 18.20 真实失败处理

`kb_rag.py` 显式处理：

- 知识库路径缺失；
- `rag_index.py` 缺失；
- index 不存在；
- subprocess timeout；
- non-zero exit；
- stdout 非 JSON；
- JSON 不是列表；
- hit 缺 `chunk_id`；
- hit 缺 `content_hash`；
- hit 缺 revision；
- revision 混杂；
- freshness 非法；
- stale / unknown；
- 无 fresh hit。

这些失败不会伪装成 W 成功。

输出会包含：

- `ok`
- `warning`
- `hits`
- `telemetry.status`
- `latency_ms`
- `hit_count`
- `neighbor_hits`
- score max/min/mean
- index revision/freshness。

### 18.21 为什么不能“W 失败就让 LLM 自己答”

因为这会把：

```text
检索失败
```

伪装成：

```text
没有相关证据，但模型凭参数知识生成了一个答案
```

正确行为是：

- S/G/R 等来源照常使用；
- W 标 degraded；
- 如果问题依赖 W，则降低置信；
- 明确“语义知识库检索未成功”；
- 不补造引用。

### 18.22 评测

`evaluate.py` 支持：

- Recall@k；
- hit@k；
- MRR；
- BM25 / dense / hybrid / rerank 对比；
- aliases；
- 逻辑卡 suffix normalization；
- recall ceiling。

#### Recall@k

\[
Recall@k = \frac{|Relevant \cap TopK|}{|Relevant|}
\]

适合一个问题有多个应召回页面。

#### Hit@k

Top-k 只要命中至少一个相关页记 1。

适合判断：

> 系统是否至少找到了一个可用入口。

#### MRR

\[
MRR = \frac{1}{N}\sum_i \frac{1}{rank_i}
\]

衡量第一个相关结果是否靠前。

#### Recall ceiling

如果一题有 20 个 expected pages，而 `k=5`：

```text
完美排序的 recall@5 上限也只有 5/20
```

把 ceiling 显式算出，避免错误解读指标。

### 18.23 评测集为什么比模型选择更重要

如果 expected pages 是自动生成或错误标注：

- hybrid “提升”可能只是对标签过拟合；
- aliases 可能把不同概念误合并；
- suffix normalization 可能虚增命中；
- 真实用户问题分布没有被覆盖。

因此正式结论需要：

1. 真实用户 query；
2. 人工判断哪些页面真正支持答案；
3. 区分必需页和可选页；
4. 记录标注分歧；
5. 按问题类型切片；
6. 对检索失败做 error analysis。

### 18.24 当前边界

已实现：

- raw/wiki/relations 分层；
- section-aware chunking；
- BGE-m3 dense；
- 独立 BM25；
- exact boost；
- RRF；
- wikilink neighbor；
- optional cross-encoder rerank；
- content hash 增量；
- index freshness；
- subprocess timeout/non-zero/JSON 校验；
- Recall/hit/MRR 评测框架。

不能夸大：

- README 明确写的是 **Hybrid 检索 POC**；
- BGE sparse 接口存在，但实际主检索 lexical 是 `rank_bm25`；
- HashEmbedder / HashReranker 只是 CI 冒烟，不能证明质量；
- 没有充分证据证明当前参数对真实金融问题最优；
- 需要人工标注 query set 才能宣称 hybrid 或 rerank 的真实收益；
- 不是大规模生产向量服务。

### 18.25 面试表达

#### 30 秒

> 我的 RAG 不是单向量 top-k，而是从 Markdown/YAML 知识治理开始：按 section 切块，BGE-m3 做 dense，独立 `rank_bm25` 做关键词召回，再用 RRF 融合，对公司名、股票代码和 wikilink 精确命中加 boost，沿 wikilink 扩一跳，必要时用 bge cross-encoder 重排。索引按 content hash 增量更新，并要求 hit 绑定 chunk、content hash、source revision 和 freshness；过期或无法证明新鲜的结果不会进入正式证据。

#### 2 分钟

> 金融检索既要语义，又要精确实体。纯 BM25 会漏同义表达，纯 dense 又可能漏股票代码和专有名词，所以我做了两阶段 hybrid：dense top-80 与 BM25 top-80 合并，用 RRF 避免不同分数量纲的归一化问题，再给实体、代码和 wikilink 精确匹配加 boost，并沿知识库双链做一跳邻居扩展。全文索引噪声更大时，对前 50 个候选用 bge-reranker-v2-m3 重排。工程上索引是 JSONL、NumPy 和 gzip token corpus，按 chunk id + content hash 增量更新；Finance Workspace 通过 subprocess 调知识库 CLI，显式处理超时、非零退出、坏 JSON、revision 混杂和 stale/unknown freshness。评测支持 Recall@k、hit@k、MRR 和 recall ceiling，但 README 仍把它定义为 POC，真实收益要用人工标注 query set 验证。

#### 追问

**问：为什么 RRF 的 k 是 60？**
答：这是常用经验值和当前配置，不应宣称是最优；应在标注集上搜索，并观察不同 query slice。

**问：为什么不用 FAISS？**
答：当前万级 chunk、本地单机，NumPy 暴力搜索足够简单；规模和并发上升后再引入 ANN。

**问：如何评测 reranker？**
答：先固定召回候选池，比较 rerank 前后的 MRR/nDCG/Recall@k；还要看延迟和错误类型，避免只看均值。

---

## 19. Closed-loop Retrieval：为什么检索要有 narrow、broad、counter

真实代码：

- `finance-workspace-private/intelligence/services/closed_loop_retrieval.py`
- `finance-workspace-private/intelligence/services/ask.py`

### 19.1 业务问题

一次 query 往往只能找到“最像用户问题”的材料，但研究任务还需要：

- 主体的精确证据；
- 上下游和同业；
- 替代表达；
- 宏观需求与竞争格局；
- 风险和证伪。

只做一次 top-k 容易产生确认偏误：

```text
用户问“为什么看好 A”
→ 检索器只找“看好 A”的材料
→ 模型总结成更强的看好结论
```

### 19.2 第一性原理

研究不是“找到支持材料”，而是：

```text
提出假设
→ 找直接证据
→ 扩展相关变量
→ 主动寻找反证
→ 决定结论强度
```

所以检索本身也要反映研究方法。

### 19.3 三个孔径

#### narrow

目标：找到主体的精确证据。

有 entity anchor 时会构造：

```text
公司名 + ticker
公司名 + 原始六位代码
graph_query
```

没有 anchor 时尝试：

```text
原 query
query + 实体 代码
query + 公司 题材
```

#### broad

目标：扩展上下文和替代解释。

查询：

```text
subject + context + 上下游 同业
subject + context + 产业链 替代表达
subject + context + 宏观 需求 竞争格局
```

其中 context 会吸收：

- anchor concepts；
- narrow hits 中抽取的高信息词。

#### counter

目标：主动找反方。

查询：

```text
subject + terms + 风险 证伪 不及预期
subject + terms + 替代 竞争 受损
subject + terms + 反方 下滑 失败
```

### 19.4 核心对象

```python
@dataclass(frozen=True)
class RetrievalAttempt:
    aperture: Literal["narrow", "broad", "counter"]
    query: str
    status: str
    hit_count: int
```

```python
@dataclass(frozen=True)
class BucketedHit:
    aperture: ...
    hit: WikiHit
```

```python
@dataclass
class ClosedLoopRetrievalResult:
    conclusion: list[BucketedHit]
    clues: list[BucketedHit]
    discarded: list[BucketedHit]
    counter_clues: list[BucketedHit]
    attempts: list[RetrievalAttempt]
    warnings: list[str]
    telemetry: RetrievalTelemetry | None
```

### 19.5 为什么要记录 attempt

最终没命中可能有不同原因：

- query 写得差；
- narrow 为空，但 broad 有结果；
- 索引超时；
- 索引 stale；
- 有 hit 但被 freshness gate 丢弃；
- 反证孔径没有任何材料。

只记录最终 `hits=[]` 无法排障。

`RetrievalAttempt` 让系统知道：

```text
哪个 aperture
用了什么 query
retriever status 是什么
命中了几条
```

### 19.6 最多三次空尝试

```python
MAX_EMPTY_ATTEMPTS = 3
```

每个孔径会按候选 query 尝试，命中后返回；连续空结果最多尝试三个。

这在 recall 和 latency 之间做了工程折中：

- 一次失败不立即放弃；
- 也不无限改写 query。

### 19.7 分桶逻辑

结果不是全部进入 conclusion。

#### counter hit

正分 counter hit：

```text
counter_clues
同时进入 clues
```

不会作为主结论支持证据。

#### conclusion

需要：

- score > 0；
- 且 hard source 或与相关词直接重叠。

hard source 可以来自：

- `fact_hardness` 为 hard/verified/canonical；
- `evidence_layer` 为 L3/L4/canonical。

#### clues

有正分但不满足硬度/直接相关条件。

#### discarded

无有效分数或不足以作为候选。

### 19.8 为什么“相关”还不够

Dense retrieval 的相关可能只是：

```text
都在谈服务器散热
```

但用户问的是：

```text
某公司的液冷订单是否兑现
```

所以 conclusion 还要求：

- 主体直接重叠；
- 或证据硬度足够。

### 19.9 `ask.py` 中的真实调用

```python
loop = retrieve_closed_loop(
    options.query,
    anchor=anchor,
    retrieve=lambda retrieval_query: kb_rag.retrieve(
        retrieval_query,
        resolved_kb_wiki,
        k=options.wiki_rag_k,
        mode=options.wiki_rag_mode,
        timeout=options.wiki_rag_timeout,
        excerpt_chars=options.wiki_rag_excerpt,
        index_dir=options.wiki_rag_index_dir,
        require_fresh=True,
    ),
)
```

注意：

- 每个 aperture 都继承 freshness gate；
- warning 不被丢弃；
- hit 保留 aperture；
- counter clues 单独进入反证区域。

### 19.10 数据流

```text
原 query
→ entity anchor
→ narrow query candidates
→ W retriever
→ narrow hits
→ 从 narrow hit 抽取概念词
→ broad queries
→ broad hits
→ counter queries
→ counter hits
→ dedupe
→ conclusion / clue / counter / discarded
→ AnswerSpec 和反证计划
```

### 19.11 异常和降级

| 情况 | 行为 |
|---|---|
| narrow 三次为空 | warning，继续 broad/counter |
| broad 为空 | 缺少上下游/同业扩展 |
| counter 为空 | 明确反证检索未命中，不等于没有风险 |
| retriever timeout | attempt status=timeout，记录 warning |
| stale hits 被丢弃 | degraded，不进入正式证据 |
| hit 相关但硬度不足 | 进入 clue，不进 conclusion |
| 同一 chunk 重复 | 按 aperture/path/chunk 去重 |

关键口径：

> “没有找到反证”不等于“反证不存在”，只能说当前知识库和检索查询未命中。

### 19.12 评测

除了普通 Recall@k，还应按 aperture 评测：

- narrow entity precision；
- narrow evidence recall；
- broad novelty；
- broad useful expansion rate；
- counterevidence hit rate；
- conclusion precision；
- clue-to-evidence promotion rate；
- discarded false-negative rate；
- 每个 aperture latency；
- empty-after-3-attempts rate。

需要人工判断：

- broad 结果是否真正增加决策信息；
- counter 是否构成有效反证，而非只含“风险”字样。

### 19.13 当前边界

已实现：

- narrow/broad/counter；
- query expansion；
- 三次尝试；
- attempt 记录；
- conclusion/clue/counter/discarded 分桶；
- warning 和 telemetry；
- 与 `ask.py` 集成。

不能夸大：

- query expansion 主要是启发式词模板，不是训练出的 multi-hop retriever；
- counter retrieval 不能保证找到真实最强反证；
- 分桶依赖 score、字符串重叠和 metadata，仍需人工评测；
- 当前 subprocess 多次查询可能带来明显延迟。

### 19.14 面试表达

#### 30 秒

> 我没有把 RAG 做成一次 top-k，而是实现了 narrow、broad、counter 三孔径闭环。narrow 找公司和代码的直接证据，broad 根据 anchor 和初始命中扩展上下游、同业、宏观和替代表达，counter 主动搜风险、证伪和竞争。每次尝试都记录 query、status 和 hit count，结果再分成 conclusion、clue、counter clue 和 discarded，避免所有语义相关文本都直接支持结论。

#### 2 分钟

> 单次 RAG 很容易强化用户原始假设，所以我把研究流程编码进检索。先用实体和 ticker 做 narrow，确保主体正确；再从 narrow hits 抽取概念，扩展产业链、同业和竞争格局；最后构造风险、失败和替代类 counter query。每个 aperture 最多尝试三个 query，并保存 `RetrievalAttempt`。命中后也不直接全进 context：有硬证据或直接实体重叠的才进入 conclusion，相关但证据弱的进入 clue，反方结果单独进入 counter clues。这样检索失败、证据不足和反证缺失都能被显式看到，而不是在 LLM 的答案里消失。

#### 追问

**问：这算 multi-hop RAG 吗？**
答：有基于前一阶段 hit 抽词再检索的迭代特征，但当前主要是启发式闭环，不应夸成复杂训练式 multi-hop reasoning。

**问：怎样证明 counter 有用？**
答：构造带已知反证的人工集，评估 counter hit rate 和最终 unsupported confidence 是否下降；同时人工判断反证质量。

---

