---
title: "大模型面试：金融 Agent 项目第一性原理复习手册（V3）第6册（章 28–35）"
type: tutor-note
agent: devin
source: "拆自 PR #21（Devin Session deebe5e092fe49579a9983ee14ca02d3）；按章节边界无损拆分自原单文件手册"
date: 2026-07-14
tags: [llm, interview, finance-agent, rag, agent, handbook]
status: draft
related: ["[[大模型面试-金融Agent项目第一性原理复习手册-V3]]"]
---

> 本册为 [[大模型面试-金融Agent项目第一性原理复习手册-V3|V3 手册]] 第 6/6 册（章 28–35），按章节边界无损拆分，正文逐行未改写；分册导航见索引页。

## 28. 一道真实问题的全链路拆解

问题示例：

> “A 公司最近为什么强？是液冷核心受益，还是只在跟题材？”

### 28.1 澄清

需要确认：

- A 公司具体名称/ticker；
- “最近”是 3 日、5 日还是 20 日；
- 用户要快速判断还是深挖；
- 是否关心交易时点。

如果 ticker 唯一且默认窗口可接受，系统可继续；否则请求澄清。

### 28.2 Router

这是：

```text
planner_analysis
```

而不是命令型 known workflow。

### 28.3 QuestionPlan

```text
question_type = stock_deep_dive
required_lenses:
  - company_identity
  - theme_exposure
  - market_validation
  - evidence_hardness
  - peer_comparison
  - counterevidence
  - verification_window

retrieval_plan:
  S/G/R/W/D
  L3 optional
  M/V as prior/calibration
```

### 28.4 Entity Anchor

输出：

```text
entity = A公司
ticker = 000000.SZ
concepts = [液冷, 数据中心...]
graph_query = ...
```

如果只识别到简称但多个公司冲突：

```text
clarification
```

### 28.5 S

查看：

- 当天是否进入题材候选；
- 相对板块强弱；
- 是否连续；
- 是个股独立强还是板块共振。

S 只能证明盘面在交易。

### 28.6 G/R

G：

- 是否有公司—液冷 exposure；
- 关系是 direct、indirect 还是 graph_only。

R：

- 关系对应什么 source；
- evidence layer；
- source trace。

如果只有 graph_only：

```text
只能作为候选，不直接作为基本面依据。
```

### 28.7 W closed-loop

narrow：

```text
A公司 + ticker
```

broad：

```text
A公司 液冷 上下游 同业
A公司 数据中心 竞争格局
```

counter：

```text
A公司 液冷 风险 证伪 不及预期
A公司 替代 竞争 受损
```

结果分为：

- conclusion；
- clues；
- counter clues；
- discarded。

### 28.8 D

可能运行：

- D0：近几日走势和相对强度；
- D1：同链替代队列；
- D4：题材结构；
- D6：多日趋势；
- D7：财务趋势；
- D5：估值；

按问题深度决定。

### 28.9 L3

如果开启：

- 查公告；
- 互动易；
- 公司命令；
- 最近 30 日、limit 5。

没有官方证据时：

```text
不能说公司订单已兑现。
```

### 28.10 M/V

M：

```text
用户过去曾认为 A 是核心
```

作为 hypothesis。

V：

```text
过去类似“graph exposure + 盘面强、无 L3”的判断结果如何
```

用于校准语气，不覆盖当前事实。

### 28.11 Evidence Audit

假设得到：

```text
L1：题材逻辑存在
L2：卖方认为公司有相关产品
L3：无
L4：盘面连续强于板块
E：用户过去看好
```

结论只能是：

```text
预期交易 + 盘面验证
```

不能是：

```text
公司核心受益已确认
```

### 28.12 Counter Plan

最强反证：

- 同链更纯标的更强；
- A 仅跟涨、板块退潮即掉队；
- 公司无订单/量产；
- 估值已经抢跑；
- 客户证据不足。

验证：

```text
T+1：相对强度、是否掉队
T+3：板块扩散和边际量
T+5：是否出现 L3、超额是否维持
```

### 28.13 AnswerSpec

必须输出：

```text
结论：候选/预期交易，不是事实确认
证据链：S/G/R/W/D 分开
反证：至少最强一条
缺口：无 L3
验证点：T+1/T+3/T+5
引用：chunk/revision/source
```

### 28.14 Output Review

Reviewer 检查：

- 是否写成“核心受益已确认”；
- 是否忘记 L3 缺口；
- 是否把用户 memory 当事实；
- 是否没有反证；
- 是否使用 stale W；
- 是否给不可验证泛话。

### 28.15 最终回答示例

> **结论**：当前更适合定义为“液冷链条的预期交易候选，且盘面已有验证”，还不能定义为“公司端兑现已确认的核心受益”。
> **支持**：公司与液冷存在图谱暴露，知识库有产品关联材料，近 5 日相对板块强度提升。
> **关键缺口**：尚未命中订单、量产、认证或公告类 L3，公司纯度和收入弹性仍待验证。
> **反证**：若同链更纯标的持续更强、A 在板块回落时快速掉队，则当前上涨更可能是题材跟随。
> **验证**：T+1 看相对强度；T+3 看板块扩散和量价持续；T+5 查官方证据与超额收益。

### 28.16 这道题体现的系统能力

- Router 没有自由乱跑工具；
- Planner 确保看公司、盘面、硬度和反证；
- 多源标签防止 memory/研报/盘面混写；
- RAG 负责发现，不负责直接认证；
- DuckDB 负责数字；
- L3 负责公司兑现；
- Review 负责降级口径；
- Checkpoint 负责未来验证。

---

## 29. 项目选型的核心 trade-off

### 29.1 自研轻量编排 vs Agent 框架

选择当前 Python dataclass/module：

- 调试透明；
- 依赖少；
- 控制风险；
- 本地工具适配直接。

代价：

- 状态机和持久化要自己写；
- DAG 可视化弱；
- 节点规模增大后维护成本上升。

何时考虑 LangGraph 等：

- 大量持久化节点；
- 复杂人工中断；
- 多分支恢复；
- 跨进程 worker；
- 图级可观测性。

### 29.2 Markdown/Git vs 数据库知识管理

选择 Markdown/Git：

- 人工审阅和审计强；
- 与 Obsidian 协作；
- 适合低并发。

代价：

- schema 弱；
- 并发写冲突；
- 查询效率有限。

### 29.3 NumPy RAG vs 向量数据库

选择 NumPy：

- 当前规模足够；
- 简单可重建；
- 零服务运维。

代价：

- 全量暴力搜索；
- metadata filter 能力弱；
- 并发和水平扩展弱。

### 29.4 Subprocess 跨仓调用 vs Python package

选择 subprocess：

- 仓库解耦；
- CLI 是稳定边界；
- 环境隔离；
- 易 graceful degrade。

代价：

- 启动开销；
- JSON 协议；
- 路径和依赖复杂；
- 多次 aperture 重复加载模型/索引风险。

改进方向：

- 长驻 retrieval service；
- 或将知识库 RAG 发布为版本化 Python package；
- 批量接收 narrow/broad/counter queries；
- 缓存模型和 index。

### 29.5 Rule-first vs LLM-first

Rule-first 用于：

- 风险；
- schema；
- 日期；
- freshness；
- evidence gate。

LLM-first 用于：

- 开放语义；
- 解释；
- query rewrite；
- synthesis。

代价：

- 规则可能漏长尾；
- LLM 路径仍需维护。

混合方式是当前更合理平衡。

### 29.6 Advisory vs blocking review

当前 advisory：

- 可用性高；
- 便于收集误报。

代价：

- warning 后仍可能输出；
- 高风险场景不够强。

演进：

```text
规则分级
→ 高精度硬错误 blocking
→ 语义弱告警 advisory
```

### 29.7 本地个人工作台 vs 生产 SaaS

当前适合：

- 单人研究；
- 本地数据；
- 快速迭代；
- 可审阅。

生产化仍需要：

- auth；
- tenant isolation；
- secret management；
- rate limit；
- job queue；
- durable database；
- object storage；
- observability backend；
- SLO；
- disaster recovery；
- data license/compliance。

---

## 30. 面试官高频项目追问与标准回答

### 30.1 “你的项目里 LLM 到底负责什么？”

> LLM 负责开放语义理解、问题改写、证据组织、反证表达和最终语言；事实查询、风险门禁、日期、新鲜度、数值、证据层和输出契约由确定性代码负责。默认 ask 甚至可以不依赖外部 LLM，用模板输出真实检索结果；LLM synthesis 是可选增强。

### 30.2 “如果不用 LLM，为什么还叫 Agent？”

> Agent 的关键是目标驱动的规划、工具调用、记忆和反馈，不是每一步都必须由 LLM。我的系统有规则/Planner 路由、按计划调用多源工具、保存运行状态、review 和回检；LLM 是其中的概率推理组件，不是系统全部。

### 30.3 “你的 RAG 比普通向量库强在哪里？”

> 它包括内容治理、section chunking、BM25+dense、RRF、精确实体 boost、wikilink 邻居、可选 cross-encoder、新鲜度和 snapshot binding；并且 W 只作为候选源，后面还有证据层、反证和 claim lineage。

### 30.4 “怎么防止幻觉？”

> 不靠一句“请勿幻觉”的 prompt，而是分层：事实来自 D/G/R/L，W 是候选，M 是 prior；缺 L3 就降级措辞；引用绑定 chunk/hash/revision；Output Review 检查弱证据硬写；数字 claim 做 fidelity；检索失败显式 degraded。

### 30.5 “怎么防止前视？”

> 区分 publish time、available time 和 valid time，T 时点只用 available time 不晚于 T 的来源；无日期默认排除；保存 PIT snapshot 和 evidence cutoff，并检查 claim source time 是否越界。当前边界是在线 ask 尚未把所有来源统一成完整 Temporal Facts。

### 30.6 “Memory 怎么避免污染事实？”

> Memory 的 provenance 和类型必须保留；用户 judgment、experience card 只作 prior，当前行情和公司事实重新查 D/L3；冲突时硬证据优先，并把冲突写 correction。

### 30.7 “为什么不微调一个模型解决？”

> 项目主要问题是实时事实、工具、PIT、引用和审计，不是仅靠参数知识能解决。微调可改善风格、分类或工具选择，但不能替代不断变化的数据和 deterministic control。当前也没有已核实的 LoRA/QLoRA 训练。

### 30.8 “项目最大技术难点是什么？”

> 不是接一个模型 API，而是让多源证据在语义上不混写：盘面、图谱、研报、官方事实、用户记忆和历史 outcome 都可能支持同一叙事，但权限和时效不同。我通过 source tag、evidence layer、freshness、PIT、review 和 claim lineage保持边界。

### 30.9 “怎样证明项目有价值？”

> 当前最能证明的是工程可审计性：可以看到每个来源、检索尝试、warning、引用、反证和回放；RAG 有离线指标框架，回答有 claim fidelity 和 review，预测有 checkpoint/verdict。不能声称已经证明持续投资 alpha，真实效果仍需更长历史盲测和人工标注。

### 30.10 “如果给你三个月继续做，会做什么？”

优先顺序：

1. 建真实 query + evidence 人工 gold set；
2. 把 ask 所有来源统一接入 PIT/Temporal Facts；
3. 校准 Router、Review 和自动执行阈值；
4. 把跨仓 subprocess RAG 改为长驻服务或批量接口；
5. 建 claim-level citation correctness eval；
6. 扩展严格历史盲测；
7. 建 memory TTL/superseded/conflict resolution；
8. 再考虑生产 auth、queue 和 observability。

---

## 31. 真实实现证据速查表

| 能力 | 关键文件 | 面试可说 | 不能说 |
|---|---|---|---|
| Question Router | `intelligence/services/question_router.py` | 四类路由、clarification/data gap/planner | 已训练专用 Router |
| Answer Planner | `intelligence/services/answer_orchestrator.py` | `QuestionPlan`、lenses、gates、contract | 通用自主 DAG 优化器 |
| Ask 主链 | `intelligence/services/ask.py` | 多源检索、组装、review | 每次都运行全部来源 |
| 风险门控 | `intelligence/workflows/agent_orchestrator.py` | preview、low risk、0.7、execute false | 完整生产权限系统 |
| Hybrid RAG | `skills/lib/rag/retrieval.py` | BGE dense + 独立 BM25 + RRF | BGE dense+sparse 已联合生产 |
| Chunking | `skills/lib/rag/chunking.py` | section、breadcrumb、overlap、hash | 自动保证事实正确 |
| Rerank | `skills/lib/rag/rerank.py` | bge cross-encoder top-50 | 提高候选池召回上限 |
| KB bridge | `intelligence/services/kb_rag.py` | subprocess、timeout、freshness | W 失败时仍算成功 |
| Closed loop | `intelligence/services/closed_loop_retrieval.py` | narrow/broad/counter | 已训练 multi-hop retriever |
| Evidence audit | `intelligence/services/research_brief.py` | L1/L2/L3/L4/E | 自动判投资结论正确 |
| L3 lookup | `intelligence/services/l3_evidence.py` | opt-in、公告/互动、降级 | 每次问答都查官方 |
| Research Judge | `intelligence/services/research_judge.py` | 研究成熟度 | 自动预测裁判 |
| Research Queue | `intelligence/services/research_queue.py` | 缺口转任务 | 自动完成所有研究 |
| Output Review | `intelligence/services/output_review.py` | advisory WARN + revision | 已硬阻断所有幻觉 |
| DuckDB | `market_feature_store/`、`db/` | 结构数据和时序分析 | 所有 ask 都查 DB |
| Run/Trace | `intelligence/services/run_store.py`、`intelligence/api/app.py` | run snapshot、append-only trace/stream、recovery、SSE | 分布式 tracing 平台 |
| Claim lineage | `intelligence/services/claim_lineage.py` | evidence id、claim manifest | 所有历史答案均人工核验 |
| PIT KB | `scripts/pit_lib.py` | available_time <= T | 在线全链已 bitemporal |
| Fidelity | `intelligence/services/fidelity_contract.py` | cutoff、hash、commit | 已证明全部历史正确 |
| Memory vault | `agent-memory/README.md` | 分层 Git/Markdown 黑板 | 强一致数据库 |
| User memory | `.foresight/<user>/*.jsonl` | correction/checkpoint/verdict | memory 是当前事实 |

---

## 32. 面试中必须主动声明的实现边界

### 32.1 已实现但仍需要更多验证

- Question Router 和 QuestionPlan；
- S/G/R/W/M/V/D/L 多源分工；
- Hybrid RAG 工程链路；
- closed-loop retrieval；
- DuckDB 数据块；
- evidence audit；
- output review；
- run/trace；
- Agent Memory；
- PIT 与 claim fidelity 框架；
- checkpoint/verdict/experience card。

这些可以说“已实现代码和基本工作流”，但评测充分性要分开说。

### 32.2 POC 或原型属性

- Knowledge Base README 明确称 RAG 为 POC；
- `ask` 是可运行原型和研究工作台；
- Workbench 默认本地；
- L3 是 opt-in；
- Review 是 advisory；
- 自动执行阈值尚未充分校准。

### 32.3 尚未完整落地

- 全链 Temporal Facts；
- 每个事实的 active/superseded/invalidated；
- 所有历史日期的严格 PIT snapshot；
- 充分人工标注的 RAG query set；
- 大规模无偏历史盲测；
- 完整生产 auth、多租户、SLO；
- 强一致 Memory 和自动冲突仲裁；
- 生产交易执行。

### 32.4 明确没有核实的能力

- 基础模型预训练平台；
- RLHF；
- DPO；
- GRPO；
- LoRA/QLoRA 微调；
- FSDP/ZeRO 分布式训练；
- vLLM/SGLang/TensorRT-LLM/LMDeploy 生产服务；
- 自动化交易下单；
- 已证明持续 alpha。

这些属于你应掌握的面试知识，不属于当前金融 Agent 的真实落地。

---

## 33. V3 项目讲解的四种长度

### 33.1 15 秒

> 我做了一个可审计的 A 股研究 Agent：规则和 Planner 负责路由，DuckDB、图谱、Hybrid RAG、用户记忆和官方证据负责多源检索，LLM 负责组织表达，最后再做 evidence layer、反证、PIT、output review 和历史 checkpoint。

### 33.2 30 秒

> 我的金融 Agent 不是一次 LLM 调用。问题先经过 clarification、Router 和 `QuestionPlan`，再按需访问 S/G/R/W/M/V/D/L：盘面、图谱、证据索引、wiki RAG、用户记忆、历史回检、DuckDB 和官方 L3。RAG 采用 BGE dense、独立 BM25、RRF、实体 boost、wikilink 和可选 rerank；最终结论还要经过证据分层、反证、PIT、新鲜度和 Output Review。当前是个人研究工作台，框架已实现，但 RAG 和预测效果仍需更充分人工评测和历史盲测。

### 33.3 2 分钟

> 我做的是一个面向 A 股题材研究的本地 Agent 工作台。最初的问题是，大模型可以生成很流畅的结论，但会把行情、研报、用户观点和公司事实混在一起，也无法解释检索失败和历史前视。
>
> 所以我先做控制层：Question Router 把请求分成已知 workflow、Planner、data gap 和 clarification，命令默认 preview，只有低风险、可自动执行、置信度大于 0.7 且无缺参才执行。进入问答后，Answer Orchestrator 生成 `QuestionPlan`，规定问题类型、必看视角、检索源、质量门和输出契约。
>
> 数据层分成 S/G/R/W/M/V/D/L。结构化行情和财务走 DuckDB；知识材料走 Hybrid RAG，真实链路是 BGE-m3 dense 加独立 BM25，经 RRF、实体 boost、wikilink 一跳扩展和可选 cross-encoder rerank；用户记忆只做 prior，官方 L3 用于验证公司兑现。W 还做 narrow、broad、counter 三孔径，主动找上下游和反证。
>
> 最后 evidence audit 区分 L1/L2/L3/L4/E，没有 L3 就不能把研报推演写成公司事实；Output Review 检查 freshness、evidence layer、反证、缺口和弱证据硬写；历史研究按 available time 做 PIT，结论转成 T+1/T+3/T+5 checkpoint。当前系统已具备可运行链路和评测框架，但 RAG README 仍是 POC，在线 ask 的 Temporal Facts 也没有完全贯穿，我不会夸大成已证明预测 alpha 的生产系统。

### 33.4 5 分钟白板

按以下顺序画：

```text
User
  ↓
Clarify
  ↓
Question Router
  ├─ known workflow
  ├─ planner
  ├─ data gap
  └─ clarification
  ↓
QuestionPlan
  ↓
Entity Anchor
  ↓
┌───────────────────────────────────────┐
│ S  G  R  W  M  V  D  L               │
│       W: narrow/broad/counter          │
│       D: parallel blocks → D3 barrier  │
└───────────────────────────────────────┘
  ↓
Evidence Audit + Telemetry
  ↓
Counter Plan + AnswerSpec
  ↓
Template / Optional LLM
  ↓
Output Review → Revision → Validation
  ↓
Answer + Citation + Trace
  ↓
Checkpoint → Verdict → Experience
```

画完主动补三条：

1. Memory 不是事实源；
2. W 命中不是事实确认；
3. PIT 和 Temporal Facts 尚未完全贯穿在线 ask。

---

## 34. V3 学习与模拟面试清单

### 34.1 必须能不看稿讲出的 12 项

1. Question Router；
2. QuestionPlan；
3. S/G/R/W/M/V/D/L；
4. raw→wiki→relations→RAG；
5. BM25 + dense + RRF；
6. narrow/broad/counter；
7. DuckDB D blocks；
8. evidence layer；
9. Output Review；
10. Agent Memory；
11. PIT；
12. checkpoint/verdict 闭环。

### 34.2 每项都问自己

- 当时遇到什么业务问题？
- 为什么 LLM 单次调用不够？
- 为什么选这个技术？
- 替代方案是什么？
- 代码入口在哪里？
- 输入输出是什么？
- 失败怎样降级？
- 用什么指标评测？
- 现在最大的边界是什么？

### 34.3 最容易被抓住的夸大

- 把 BGE sparse 说成已用于 hybrid；
- 把 W 相关命中说成事实；
- 把 L3 说成默认开启；
- 把所有 ask 说成都查 DuckDB；
- 把 Output Review 说成自动预测裁判；
- 把 PIT 工具说成在线全链完整 Temporal Facts；
- 把 RAG POC 说成生产质量；
- 把 memory 说成自动贝叶斯学习；
- 把通用 P1 训练/Serving 知识说成项目实装。

### 34.4 最能体现工程深度的主动表达

> 我会区分框架是否实现、是否跑通、是否有评测、是否有充分统计证据。这四件事不是一回事。

---

## 35. V3 总结

你的金融 Agent 最值得在面试中讲的，不是“用了很多技术”，而是以下因果链：

```text
金融事实会变化、来源会冲突
→ 不能让 LLM 直接做事实源

问题类型不同、动作有风险
→ 先 Router 和 QuestionPlan

数字与文本形态不同
→ DuckDB 与 RAG 分工

关键词与语义各有盲区
→ BM25 + dense + RRF + rerank

单次召回会确认偏误
→ narrow + broad + counter

来源相关不代表事实硬
→ S/G/R/W/M/V/D/L + evidence layer

模型会把弱证据写强
→ AnswerSpec + Output Review

历史容易用未来信息
→ publish/available time + PIT + fidelity

Agent 会跨会话遗忘
→ 分层 Memory + provenance + writeback

系统需要真正改进
→ checkpoint + verdict + correction + experience
```

最标准的项目定位：

> 这是一个把 LLM 放在受约束研究流程中的个人金融 Agent。它已经实现多源检索、结构化规划、证据分层、反证、输出质检、运行追踪和回检框架；但它不是基础模型训练平台，不是生产交易系统，也还没有充分证据证明稳定预测收益。项目当前最强的价值是把金融研究从不可审计的聊天，推进到有来源、有时间边界、有失败降级、可回放的工程流程。
