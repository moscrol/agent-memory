---
title: "大模型面试：金融 Agent 项目第一性原理复习手册（V3）第1册（章 0–2）"
type: tutor-note
agent: devin
source: "拆自 PR #21（Devin Session deebe5e092fe49579a9983ee14ca02d3）；按章节边界无损拆分自原单文件手册"
date: 2026-07-14
tags: [llm, interview, finance-agent, rag, agent, handbook]
status: draft
related: ["[[大模型面试-金融Agent项目第一性原理复习手册-V3]]"]
---

> 本册为 [[大模型面试-金融Agent项目第一性原理复习手册-V3|V3 手册]] 第 1/6 册（章 0–2），按章节边界无损拆分，正文逐行未改写；分册导航见索引页。

## 0. 面试总故事：你的项目到底是什么

一句话版本：

> 我做的是一个面向 A 股题材研究的个人金融 Agent 工作台。它不是只会聊天的 LLM 包装，而是把盘面数据、知识库、关系图谱、RAG 检索、用户记忆、证据分层、反证审稿和可回放评测组合起来，让模型在有来源、有边界、有降级策略的前提下辅助研究。

架构版本：

```text
agent-memory
  Git + Markdown + YAML frontmatter + Obsidian
  -> 记录用户偏好、项目交接、方法论、Agent 协作规则

knowledge-base-private
  raw 原文 / wiki 知识页 / relations 结构化图谱 / .rag_index 派生检索索引
  -> 负责事实、证据、图谱、RAG 候选页

finance-workspace-private
  DuckDB 市场特征库 + Agent 服务 + Workbench + eval
  -> 负责盘面数据、问题路由、检索编排、回答生成、质检、回放
```

面试时要突出四个工程思想：

1. **LLM 不是事实源**：事实来自 DuckDB、wiki、relations、原文证据；LLM 主要做理解、组织、解释和表达。
2. **RAG 不只是“向量库 + prompt”**：还包括 chunking、BM25、dense embedding、RRF 融合、rerank、图谱扩展、新鲜度门禁、评测。
3. **金融 Agent 必须防幻觉和防前视**：区分事实、推演、预测；历史回测只能用当时可得信息。
4. **记忆要分层**：事实记忆、经验记忆、方法论记忆不能混在一起，否则 RAG 会把旧判断当新事实。

---

## 1. PDF 审计结论：哪些能背，哪些必须更新

附件覆盖很广，但整体更像 2023 年资料，不适合原样背。

### 主要问题

- **重复**：RAG 整章重复两次；Transformer、LoRA、优化器、训练显存等跨章节重复。
- **过时**：模型家族还停在 ChatGLM、Falcon、PaLM、LLaMA 早期；上下文长度仍按 2k/4k 讲。
- **错误或不严谨**：
  - 多次写 `LLaMA-6B`，常见 LLaMA 版本应是 7B/13B/30B/65B 等。
  - “int8 一般比 fp16 慢”是早期 bitsandbytes 经验，2026 语境要结合 AWQ/GPTQ/FP8/INT4 kernel 讲。
  - LangChain 章节有伪 API，不要照抄。
  - “13B 指令精调达到 GPT-4 90%”这类说法没有定义指标，面试中不要引用。

### 优先级

P0：最适合绑定你的金融 Agent 讲
Agent、Memory、RAG、Hybrid 检索、rerank、评测、防幻觉、长上下文 vs RAG、系统设计。

P1：大厂基础高频
Transformer、Self-Attention、RoPE、RMSNorm、SwiGLU、MQA/GQA/MLA、FlashAttention、SFT/RLHF/DPO/GRPO、LoRA/QLoRA、KV cache、vLLM、分布式训练、Tokenizer。

P2：收益较低或陈旧
Prompt Tuning、Prefix Tuning、P-Tuning v1/v2、早期 LangChain API、老模型参数对比、泛泛的蒸馏/多模态章节。

---

## 2. P0 高频题标准答案

### 2.1 什么是 Agent？你的金融 Agent 为什么算 Agent？

#### 一句话结论

Agent 是以 LLM 为推理核心，能围绕目标进行规划、调用工具、使用记忆、根据反馈迭代的系统；它不是一次性文本生成器。

#### 第一性原理

普通 LLM 只有“输入文本 → 输出文本”。现实任务需要：

1. 确定用户意图；
2. 拆解子任务；
3. 选择数据源或工具；
4. 检索证据；
5. 执行或生成；
6. 检查结果；
7. 把经验写回长期记忆。

所以 Agent 的本质是：**LLM + 状态 + 工具 + 记忆 + 控制回路**。

#### 标准面试答案

Agent 通常由几部分组成：

- **Planner / Router**：理解任务并决定路径。
- **Tools**：搜索、数据库、代码执行、API、文件系统等外部能力。
- **Memory**：短期上下文和长期知识/经验。
- **Executor**：执行计划或调用工具。
- **Critic / Evaluator**：反思、验收、纠错。
- **State / Trace**：记录每一步，便于恢复和回放。

常见范式：

- ReAct：Reason + Act，把推理和行动交替进行。
- Reflexion：失败后把经验写入记忆，下次改进。
- LangGraph / workflow：把 Agent 流程显式建成状态图，提升可控性。

#### 结合你的项目

你的金融项目可以这样讲：

> 我的 Agent 没有完全交给 LLM 自由规划，而是采用“规则编排 + LLM 精修”的混合方式。问题先经过 `question_router` / `answer_orchestrator` 识别类型，再决定是否调用盘面数据、知识库 RAG、图谱关系、用户记忆、反证审稿等模块。事实由工具和数据源提供，LLM 主要负责把证据组织成可读回答。

可引用代码路径：

- `finance-workspace-private/intelligence/services/question_router.py`
- `finance-workspace-private/intelligence/workflows/agent_orchestrator.py`
- `finance-workspace-private/intelligence/services/answer_orchestrator.py`
- `finance-workspace-private/intelligence/services/ask.py`

#### 不能夸大的部分

- 不要说它是完全自主的多 Agent 生产系统。
- 更准确说法：个人金融研究 Agent 工作台，有路由、工具调用、记忆、质检和可回放机制，但核心仍是受控工作流。

---

### 2.2 RAG 是什么？为什么你的项目需要 RAG？

#### 一句话结论

RAG（Retrieval-Augmented Generation，检索增强生成）是在生成前先从外部知识库检索相关证据，让模型基于证据回答，从而降低幻觉、提升时效性和可追溯性。

#### 第一性原理

LLM 参数里存的是训练时压缩后的统计知识，有三个天然问题：

1. **过期**：训练后发生的新信息不知道。
2. **不可追溯**：不知道某句话依据哪份材料。
3. **容易编造**：模型会补全“看起来合理”的答案。

RAG 把“记住所有知识”改成“需要时检索证据”，本质是把知识从模型参数中外置出来。

#### 标准面试答案

RAG 典型流程：

1. 文档清洗与切块；
2. embedding 建索引；
3. 用户 query 改写或扩展；
4. 召回候选 chunk / page；
5. rerank 精排；
6. 拼 prompt，让 LLM 基于上下文生成；
7. 引用来源、评测忠实度和召回质量。

核心指标：

- 检索侧：Recall@k、MRR、nDCG、命中率、索引新鲜度。
- 生成侧：faithfulness、answer relevance、context relevance、引用覆盖率。
- 业务侧：回答是否能支持决策、是否暴露缺口、是否可复验。

#### 结合你的项目

你的知识库仓不是简单向量库：

```text
raw/ 原文
→ wiki/entities, concepts, sources, synthesis
→ wiki/relations 结构化关系
→ .rag_index 派生索引
→ finance-workspace 的 kb_rag.py 调用 rag_index.py query
```

项目亮点：

- RAG 索引不作为事实源，只是派生索引，可从 wiki 重建。
- 检索结果带 `content_hash`、`index_source_revision`、`index_freshness`。
- finance 仓调用知识库仓时走 subprocess，失败则降级，不让 RAG 故障拖垮整个 Agent。

可引用代码路径：

- `knowledge-base-private/skills/lib/rag/README.md`
- `knowledge-base-private/scripts/rag_index.py`
- `knowledge-base-private/skills/lib/rag/retrieval.py`
- `finance-workspace-private/intelligence/services/kb_rag.py`

#### 不能夸大的部分

- 知识库 RAG README 明确写的是 POC。
- 本次未实测 BGE 索引效果；评测集也存在合成/未校准问题。
- 面试中应说：“工程链路已实现，正式效果还需要真实查询集和人工校准真值验证。”

---

### 2.3 Hybrid 检索是什么？BM25、向量、RRF 怎么融合？

#### 一句话结论

Hybrid 检索把关键词检索和语义向量检索结合起来：BM25 擅长精确词面，dense embedding 擅长同义语义，RRF 用排名融合避免分数不可比。

#### 第一性原理

检索的目标是“不要漏掉相关证据”。单一方法有系统性盲区：

- BM25：看到“液冷服务器”能精确命中，但用户问“数据中心散热新方向”可能漏。
- 向量检索：能理解同义语义，但股票代码、公司名、罕见术语、数字很容易不稳。

因此最好让误差不相关的召回器并联。

#### 标准面试答案

BM25：

- 基于词频 TF、逆文档频率 IDF、文档长度归一化；
- 适合精确匹配、专有名词、代码。

Dense retrieval：

- 把 query 和 chunk 编码成向量；
- 用 cosine / dot product 搜相似语义；
- 适合同义、改写、模糊问题。

RRF（Reciprocal Rank Fusion）：

```text
score(d) = Σ 1 / (k + rank_i(d))
```

优点：

- 不要求 BM25 和向量分数在同一尺度；
- 对异常分数鲁棒；
- 工业界常用作简单强基线。

#### 结合你的项目

知识库检索实现：

- dense：BGE-m3 输出 1024 维向量；
- BM25：`rank_bm25` + 轻量中文 tokenizer；
- 两路各取 top-80；
- 用 RRF 融合；
- 对股票代码、公司名、概念名、wikilink 精确命中加 boost；
- 沿 wikilink 做一跳邻居扩展；
- 可选 rerank。

可引用代码路径：

- `knowledge-base-private/skills/lib/rag/config.py`
- `knowledge-base-private/skills/lib/rag/retrieval.py`
- `knowledge-base-private/skills/lib/rag/tokenizer.py`

#### 不能夸大的部分

- 代码里 BGE-m3 的 sparse / lexical_weights 没有接入检索；BM25 是独立 `rank_bm25`，不要说“用了 BGE-m3 dense+sparse 双路”。
- Hybrid 有工程实现，但效果提升需要可信评测集证明。

---

### 2.4 rerank 是什么？bi-encoder 和 cross-encoder 有什么区别？

#### 一句话结论

bi-encoder 快，适合大规模召回；cross-encoder 慢但更准，适合对少量候选重排。

#### 第一性原理

召回阶段要从海量文档中找候选，必须快；精排阶段只面对几十个候选，可以用更贵模型精细判断。

bi-encoder：

```text
q -> vector
d -> vector
score = q · d
```

优点是文档向量可预计算；缺点是 query 和 document 没有深度交互。

cross-encoder：

```text
[query, document] -> model -> relevance score
```

优点是相关性判断更细；缺点是每个候选都要跑模型。

#### 标准面试答案

工业 RAG 常用两阶段：

1. BM25 / dense / hybrid 先召回 top-N；
2. cross-encoder reranker 对 top-N 重打分；
3. 取 top-k 拼上下文。

rerank 只能重排已有候选，不能把没召回的好文档捞回来，所以召回池要足够大。

#### 结合你的项目

你的知识库实现了：

- `mode=rerank`；
- 在 hybrid 候选之上取前 `RERANK_CANDIDATES=50`；
- 使用 `bge-reranker-v2-m3`；
- `AutoModelForSequenceClassification` 输出 logit，再 sigmoid 到 0~1；
- hash reranker 只用于离线冒烟，不用于正式结论。

可引用代码路径：

- `knowledge-base-private/skills/lib/rag/rerank.py`
- `knowledge-base-private/skills/lib/rag/retrieval.py`

#### 不能夸大的部分

- README 提醒 rerank 收益要用 eval A/B 量化后再决定是否默认开启。
- 面试时说“已实现 rerank 管线，是否默认上线取决于延迟、成本和真实评测收益”更稳。

---

### 2.5 文档怎么切块？为什么不能直接固定长度切？

#### 一句话结论

chunk 是 RAG 的最小检索和引用单元；切得太大噪声多，切得太小丢上下文。你的项目用 Markdown section + 标题/tags 面包屑 + overlap 做折中。

#### 第一性原理

检索找的是 chunk，不是完整文档。chunk 决定：

- 能否被召回；
- 召回后语义是否完整；
- 引用是否能追溯；
- prompt 是否被噪声塞满。

固定长度窗口可能把一个产业链逻辑切断，也可能把标题和正文拆开。

#### 标准面试答案

常见切块策略：

- 固定 token 窗口：简单，但易切断语义；
- 递归字符切分：按段落、句子逐级切；
- 结构化切分：按 Markdown 标题、HTML 标签、PDF section；
- 语义切分：用 embedding 相似度检测主题变化；
- overlap：保留边界信息，但会增加冗余。

#### 结合你的项目

知识库 RAG：

- 按 `##/###` section 切；
- 每块前面拼标题、tags、section 面包屑；
- 超过 `MAX_TOKENS=1024` 再按段落切到 `TARGET_TOKENS=768`；
- overlap 约 15%；
- chunk 带 `file_path/page_type/title/tags/section/wikilinks/content_hash`。

可引用代码路径：

- `knowledge-base-private/skills/lib/rag/chunking.py`
- `knowledge-base-private/skills/lib/rag/config.py`

---

### 2.6 如何保证 RAG 索引新鲜度？为什么这是防幻觉的一部分？

#### 一句话结论

过期索引会让模型引用“看似有来源但已经过时”的证据，所以 RAG 必须有 freshness gate，默认 fail-closed。

#### 第一性原理

RAG 幻觉不只来自模型，也来自检索系统：

- 文档更新了，索引没更新；
- raw 原文变了，chunk hash 没对齐；
- 用旧 index 回答新问题；
- 评测集和索引版本不一致。

这类错误最危险，因为回答有引用，看起来更可信。

#### 标准面试答案

索引新鲜度可以检查：

1. index build time 是否超过阈值；
2. 源文件 git revision 是否变化；
3. working tree 是否有未入索引改动；
4. chunk content_hash 是否一致；
5. index metadata 是否记录 include_raw、模型名、构建参数。

默认策略：

- fresh：允许作为证据；
- stale：拒绝或显式降级；
- unknown：保守处理，不当正式证据。

#### 结合你的项目

知识库做了：

- `content_hash` 增量更新；
- `manifest_revision` 记录参与索引的文件内容；
- `rag_freshness.py` 检查 git diff、working tree、age；
- `rag_index.py query` 默认 `stale-policy=fail`，过期直接拒绝作为证据；
- finance 仓 `kb_rag.retrieve(require_fresh=True)` 会丢弃 stale/unknown 命中。

可引用代码路径：

- `knowledge-base-private/scripts/rag_freshness.py`
- `knowledge-base-private/scripts/rag_index.py`
- `knowledge-base-private/skills/lib/rag/store.py`
- `finance-workspace-private/intelligence/services/kb_rag.py`

---

### 2.7 怎么防止 LLM / RAG 幻觉？

#### 一句话结论

不要只靠 prompt 说“不要幻觉”。成熟系统要把事实来源、证据分层、反证、缺口、程序化检查、回放评测都做出来。

#### 第一性原理

幻觉来自三类问题：

1. **模型内在生成错误**：语言模型目标是预测下一个 token，不是保证事实真。
2. **检索错误**：召回错文档、旧文档、低质量文档。
3. **推理越权**：事实是真的，但结论或预测跳得太远。

防幻觉不是让模型“更听话”，而是限制它能把什么升级成事实或决策。

#### 标准面试答案

防幻觉方法：

- RAG 引入外部证据；
- 引用必须绑定 source / chunk；
- 事实、推理、预测分层；
- 反证检索；
- 没证据时拒答或降级；
- LLM-as-judge + 程序化 gate；
- claim-level verification；
- 离线评测与线上 trace。

#### 结合你的项目

你的项目有多层防线：

1. `ask.py` 要求事实行带 `[S#]/[G#]/[R#]/[W#]/[M#]` 引用；
2. `answer_quality.py` 做 prompt 层质检；
3. `output_review.py` 做程序化 gate：新鲜度、证据分层、反证、缺口、可验证假设、弱证据硬写；
4. `red_team.py` 找过去错误和反方；
5. `claim_fidelity.py` 做 claim-level 抽取与验证；
6. 知识库写入时区分 L1/L2/L3 证据和 fact_hardness。

可引用代码路径：

- `finance-workspace-private/intelligence/services/output_review.py`
- `finance-workspace-private/intelligence/eval/claim_fidelity.py`
- `finance-workspace-private/intelligence/services/red_team.py`
- `knowledge-base-private/skills/lib/knowledge_graph.py`

#### 不能夸大的部分

- `output_review.py` 文档明确说：当前是 advisory review，不是自动硬阻断，也尚未通过历史盲测证明能区分 hit/miss。
- 面试时说“它提升可审计性和错误暴露能力，不等于证明预测更准”。

---

### 2.8 RAG 怎么评测？为什么只看最终答案不够？

#### 一句话结论

RAG 要分层评测：检索有没有找到证据、证据是否相关、生成是否忠实、系统是否可追溯、业务是否有用。

#### 第一性原理

一个错误回答可能来自：

- query 改写错；
- chunk 切错；
- embedding 召回漏；
- rerank 排错；
- prompt 拼接错；
- LLM 忽略上下文；
- 引用不支持结论。

只看最终答案无法定位问题。

#### 标准面试答案

评测维度：

检索：

- Recall@k：标准答案页是否进入 top-k；
- MRR：第一个正确结果排第几；
- nDCG：排序质量；
- coverage：证据覆盖。

生成：

- faithfulness：答案是否被上下文支持；
- answer relevance：是否回答问题；
- context relevance：上下文是否相关；
- citation precision/recall：引用是否准确。

系统：

- latency、cost、索引新鲜度、失败降级率、trace 完整度。

#### 结合你的项目

知识库：

- `rag_index.py eval` 支持 `recall@k`、`MRR`；
- 支持 bm25/dense/hybrid/rerank 多模式 A/B；
- 有 aliases 和逻辑卡 suffix 归一；
- 有 freshness gate。

金融仓：

- `agent_eval.py` 评估引用、免责声明、过期标记；
- `finance_answer_rubric.py` 评估金融回答质量；
- `claim_fidelity.py` 做 claim 级验证；
- `pit_snapshot.py` / `bitemporal_history.py` 关注无前视回放。

可引用代码路径：

- `knowledge-base-private/skills/lib/rag/evaluate.py`
- `finance-workspace-private/intelligence/eval/agent_eval.py`
- `finance-workspace-private/intelligence/eval/finance_answer_rubric.py`
- `finance-workspace-private/intelligence/eval/claim_fidelity.py`

#### 不能夸大的部分

- 知识库当前 eval queries 有合成痕迹，真实问题集仍需用户校准。
- 要说“评测框架已具备，但正式指标需要可信 golden set”。

---

### 2.9 长上下文能替代 RAG 吗？

#### 一句话结论

不能简单替代。长上下文解决“塞得下”，RAG 解决“找得准、可更新、可追溯、可评测”。二者互补。

#### 第一性原理

长上下文的代价：

- token 成本高；
- latency 高；
- lost-in-the-middle；
- 无法保证资料版本新鲜；
- 引用和评测更难。

RAG 的优势：

- 只取相关证据；
- 外部知识可实时更新；
- 可绑定来源；
- 可单独评测检索环节。

#### 标准面试答案

长上下文适合：

- 单份长文总结；
- 法律合同/代码仓上下文完整阅读；
- 多材料但数量可控。

RAG 适合：

- 知识持续更新；
- 文档规模大；
- 需要引用、权限、新鲜度和审计；
- 需要低成本高并发。

最佳实践是：RAG 先筛选，再用长上下文读少量高价值材料。

#### 结合你的项目

你的金融知识库有几千个实体/概念/来源页和大 relations JSON。如果全部塞进 prompt，不现实。项目明确使用：

- AGENTS.md 定义上下文加载纪律；
- 大 JSON 禁止直接 cat；
- 关系查询走 `query_relations.py`；
- RAG 先选页，再读相关内容。

可引用代码路径：

- `knowledge-base-private/AGENTS.md`
- `knowledge-base-private/scripts/query_relations.py`
- `knowledge-base-private/skills/lib/rag/README.md`

---

### 2.10 Memory 怎么设计？为什么不用直接把所有历史对话塞给模型？

#### 一句话结论

记忆系统的关键不是“存得越多越好”，而是分层、可追溯、可遗忘、不会污染事实源。

#### 第一性原理

历史对话有三类问题：

1. 噪声多：聊天流水不等于知识。
2. 会腐烂：旧判断可能过时。
3. 会自我强化：模型把自己以前生成的错误当事实。

所以记忆要区分：

- 工作记忆：本轮上下文；
- 情景记忆：发生过什么；
- 语义记忆：稳定知识；
- 程序记忆：可复用流程；
- 用户偏好/经验：只作为 prior，不是市场事实。

#### 标准面试答案

Memory 设计原则：

- 分层存储；
- 每条记录有 source、agent、date、status；
- 事实和经验分开；
- 过期知识要 stale / deprecated；
- 检索到记忆后要和当前数据交叉验证；
- 关键记忆需要人工确认或评测闭环。

#### 结合你的项目

`agent-memory` 是 Git + Markdown 的共享黑板：

- `10_knowledge`：长期方法论；
- `20_projects`：项目 MOC 和交接；
- `30_conventions`：偏好、规范；
- `40_playbooks`：可复用流程；
- `70_tutor`：人工审阅教学材料。

金融仓还有用户记忆：

- `corrections.jsonl`：纠偏；
- `judgments.jsonl`：用户判断；
- `experience_cards.jsonl`：回答经验；
- `checkpoints/verdicts`：回检校准。

可引用代码路径：

- `agent-memory/README.md`
- `agent-memory/30_conventions/frontmatter-spec.md`
- `finance-workspace-private/intelligence/services/user_memory.py`
- `finance-workspace-private/intelligence/services/experience_cards.py`
- `finance-workspace-private/intelligence/services/corrections.py`

#### 不能夸大的部分

- Agent Memory 目前主要是 Markdown/Git 黑板，对 vault 本身还没有完整 Hybrid 检索。
- 贝叶斯记忆仲裁在金融 Workbench 里仍有未落地缺口。

---

### 2.11 多 Agent 共享记忆怎么保证一致性？

#### 一句话结论

你的系统选择“Git + Markdown 黑板 + 约定 + lint + pre-commit”的轻量最终一致，而不是强一致数据库。

#### 第一性原理

多 Agent 协作需要共享状态，但过早引入中心数据库/调度器会增加复杂度。对个人项目来说：

- 写入频率低；
- 人类要能审阅；
- 工具要可迁移；
- Git 冲突可接受。

所以最终一致比强一致更划算。

#### 标准面试答案

一致性策略：

- 单一事实源 SSOT；
- append-only 交接记录；
- Git diff / review；
- pre-commit 拦截密钥和大文件；
- lint 检查 frontmatter、死链、老化；
- 冲突时人工裁决，不让 Agent 强行合并。

#### 结合你的项目

Agent Memory：

- README 定义纯文本、frontmatter、Git 托管；
- `frontmatter-spec.md` 规定 agent/source/date；
- `devin-writeback.md` 定义写回层级；
- `vault_lint.py` 检查结构。

可引用路径：

- `agent-memory/40_playbooks/devin-writeback.md`
- `agent-memory/30_conventions/maintenance.md`
- `agent-memory/scripts/vault_lint.py`

---

### 2.12 金融场景为什么特别强调 point-in-time 和无前视？

#### 一句话结论

金融研究里，正确答案不等于当时可得答案。历史回放只能使用决策时点之前已经可得的信息。

#### 第一性原理

如果 6 月 20 日才发布的研报被拿去解释 6 月 10 日的交易决策，就是前视泄露。模型会看起来很聪明，但回测无效。

需要区分：

- `publish_time`：信息产生时间；
- `available_time`：系统实际可使用时间；
- `created/updated`：知识库写入/更新日期。

#### 标准面试答案

金融 Agent 的评测要做：

- point-in-time 数据截断；
- 不可变快照；
- as-known-at 回放；
- 预测和结果分离；
- 样本外验证；
- 防止 hindsight bias。

#### 结合你的项目

知识库约定：

- `docs/conventions.md` 定义 `publish_time` 和 `available_time`；
- `pit_lib.py` / `pit_truncate.py` 做 PIT 截断；
- `audit_backfill_embargo.py` 防止回填早于发布日期。

金融仓：

- `pit_snapshot.py`；
- `bitemporal_history.py`；
- `fidelity_contract.py`；
- `claim_fidelity.py`。

可引用路径：

- `knowledge-base-private/docs/conventions.md`
- `knowledge-base-private/scripts/pit_lib.py`
- `finance-workspace-private/intelligence/eval/pit_snapshot.py`
- `finance-workspace-private/intelligence/eval/bitemporal_history.py`

---

