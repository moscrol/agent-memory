---
title: 金融上下文与工具的实际消费审计
type: inbox
agent: codex
source: "/Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e; /Users/a77/.finance-runtime/model-first-harness-1006/prod-1; /Users/a77/fwp-wt-answer-quality-closeout-1007"
date: 2026-10-07
tags: [inbox, finance, harness, context-consumption, research]
status: draft
last_verified: 2026-10-07
---

# 金融上下文与工具的实际消费审计

> 原始调研产出，待提炼。只读源码、已保存健康记录、索引元数据与冻结运行原件；没有新模型请求、网络请求、生产库查询或写入，也没有真实用户台账写入。本文不构成自然效果实验完成或发布验收。

## 内容

### 读取范围与身份

本笔记中的 `VERIFIED · 2026-10-07` 表示当天实际打开了所引本地源码或原件；`[推断]` 单列。代码链接指向固定部署目录，候选链接附所核 SHA。索引存在、健康为绿、菜单可见和作者绑定分别是不同层的证据，不能互相替代。

| 对象 | 实际核对 | 来源状态与边界 |
|---|---|---|
| 部署代码快照 | `d5d7c5f6017e12ce5be9414abe31cf763c161f50`，读取时工作树干净。已保存健康记录的 `source_revision`、`code_root` 与代码/加载指纹一致，模型为 `glm-5.3-flash`。 | **VERIFIED · 2026-10-07**：[健康记录](</Users/a77/.finance-runtime/answer-quality-closeout-1007/production-health-final-observation.json>)，记录时间为 10-07 10:30。没有重新访问服务；root 后续发布不能由这张旧记录代签。 |
| 候选代码 | `afea1daf4daa1f12fa3380e73f11355f0dcf4ed0`，产品改造提交为 `a5feb32b59096ab5357dbc96255191a88c50c534`。候选与 d5 的工具注册表 blob 同为 `824da6c4fc7c0434060f4e5de2a08108a43ef117`；工具工厂和 Episode 输入投影 blob 不同。 | **VERIFIED · 2026-10-07**：本地 Git 对象读取；[候选装配清单](</Users/a77/.finance-runtime/answer-quality-closeout-1007/knevo-assembly-manifest-a5feb32b5.json>)只记录零模型/零工具装配对照，不能证明候选已被自然模型正确消费。 |
| 旧生产 v6 原件 | `prod-1/ledger.jsonl` 登记10题，全部 `health_revision=f3b97499aaff267d34bc69a1ea2bfe09b609ae85`。其中9题有完整 Episode；D8仅见 trace/answer，不纳入下表工具投影分母。 | **VERIFIED · 2026-10-07**：[账本](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/ledger.jsonl>)。这些实际调用是旧 f3b 的观测，不是当前 d5 或候选的自然效果证据。 |
| D6 真实修订 | `live-d7294e3e4-d6-02` 的修订原件用于定位重复装配后的输入损失；它属于 d729 批次。 | **VERIFIED · 2026-10-07**：[Episode](</Users/a77/.finance-runtime/answer-quality-closeout-1007/live-d7294e3e4-d6-02/D6-corrective-followup/continuous-episode.json>)、[trace](</Users/a77/.finance-runtime/answer-quality-closeout-1007/live-d7294e3e4-d6-02/D6-corrective-followup/trace.jsonl>)，不移签为候选修订通过。 |

### 声明、装配、授权、送达、引用必须逐层核对

**VERIFIED · 2026-10-07。** 用 AST 读取带类型注解的 `AnnAssign`，d5 的 `_DEFAULT_TOOL_METADATA` 分母为19个声明工具名。它包含三个共用 `finance_query` capability 的历史工具名，不是19个独立数据源。常见旧生产菜单有16名，历史工具依赖实际 `history_intent/HistorySession`，`sub_research` 依赖运行时 runner；动态 `evidence_read` 不在这个静态分母中。不能把目录数、capability 数、资料总量加在一起评价全面性。[声明表](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/research_tool_registry.py:50>)、[实际工厂](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:1030>)、[动态补读装配](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/runtime/agent_episode.py:3466>)。

**VERIFIED · 2026-10-07。** 装配的几个实际条件：`material_only` 在查根目录、验日期和预取之前返回空注册表；`local_only` 最后仅保留已授权且 `io_effect=local_read` 的 runner；记忆工具还要求真实用户身份，缺身份不会回落去读 default 用户。定义了的工具仍须经 `allowed_capabilities` 与菜单投影，`default_registry` 只为实际传入 runner 建 spec。[空输入早退](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:1046>)、[记忆身份](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:1981>)、[本地注册表收窄](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:2145>)、[授权 spec](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/research_tool_registry.py:1116>)。

**VERIFIED · 2026-10-07。** 最可靠的消费接缝是事件中保存的 `prompt_assembled.system/user` 和每个 `tool_result.model_content`。后者先留完整 audit，再去重复、裁正文、转 E 编号，随后同一串字节进入工具消息。审计全量不等于模型看到全量。[模型消息与事件共源](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/runtime/agent_episode.py:919>)、[投影顺序](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/research_harness.py:832>)。

### 已有真实 Episode 的消费矩阵

以下均为 **VERIFIED · 2026-10-07**，从完整 Episode 解析 `tool_request`、`tool_result.model_content`、首轮 prompt 和最终 bindings；“绑定数”是去重哈希数，仅证明作者声明支持，不能证明逐句正确或全文完整。9份工具投影分母中没有 `kb_search`、`web_fetch`、`evidence_read` 调用；这不等于能力不存在，也不证明每题都需要调用它们。各行链接指向对应原件。

| 题 | 实际调用与送达 | 最终绑定 / 证据 | 能说明的边界 |
|---|---|---:|---|
| [D1 市场总览](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D1-market-overview-rephrased/continuous-episode.json>) | market_data、mainline_context、finance_query各一次 | 23 / 23 | 市场与主线数据实际进入模型，不只是目录声明。 |
| [D2 华工科技](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D2-stock-rephrased/continuous-episode.json>) | finance_query两次；evidence_search、capital_data、financial_data、news_search各一次 | 41 / 50 | 知识、行情、资本、财务、新闻均有实际消费接缝；未绑定9张卡不等于9张都无关。 |
| [D3 定义查数](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D3-strict-definition-spelled-out/continuous-episode.json>) | finance_query一次 | 14 / 14 | 单工具可合法完成指定口径，不能以工具种类少判浅。 |
| [D4 封板方向](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D4-limit-heat-rephrased/continuous-episode.json>) | finance_query四次 | 55 / 55 | 使用盘面数据；首轮没有 reading_baseline，与已有 market_watch 注入门一致。 |
| [D5 核聚变](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D5-theme-unseen/continuous-episode.json>) | evidence_search两次；finance_query、memory_lookup、news_search各一次 | 72 / 76 | 两次知识召回带时点警示；有真实正文截断，见下一节。 |
| [D6 梯队](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D6-ladder-rephrased/continuous-episode.json>) | finance_query五次 | 24 / 66 | 当前日与前日晋级率都送达，仍发生混用；绑定不是理解证明。 |
| [D7 实体核验](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D7-nonexistent-entity/continuous-episode.json>) | evidence_search、graph_lookup、web_search、l3_lookup、memory_lookup及三次finance_query | 5 / 19 | 图谱和官方查询空/失败不能写成实体全局不存在；搜索摘要不是原文读取。 |
| [D9 次日观察](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D9-temporal-leakage-rephrased/continuous-episode.json>) | finance_query五次，加开场市场预取 | 154 / 154 | 大绑定池不认证样本全集、预测概率或后验未泄漏。 |
| [D10 多日变化](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D10-multiday-evolution-rephrased/continuous-episode.json>) | finance_query两次 | 56 / 56 | 日频表与题材切片送达，不足以证明资金动机或风险出清。 |

### 知识与原文：存在、召回和真正读到是不同事实

**VERIFIED · 2026-10-07。** `episode_tools` 的 KB runner 走 `kb_rag.retrieve(mode=hybrid,k=6,require_fresh=True)`；它可以绑定单独 KB 可执行代码根、索引根与正文根。`evidence_search` 在此之上走窄检索、宽检索与反方检索。直接 `kb_search` 另有节级深读：按段铸 E 证据，投递目录和未读完标记。本次9份原件全部 `deep_read=false`，没有走该节级路径；不能把 evidence_search 的摘要/相邻块视为整篇原文已读。[KB 工厂](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:1110>)、[闭环检索装配](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:1921>)、[节级深读](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/agent_research.py:585>)。

**VERIFIED · 2026-10-07。** D2事件12将12张知识卡写入模型消息，E3/E12来自具名 `20260603` 逻辑卡，最终绑定了其中4张知识卡。事件20资本工具有10张卡；事件27财务工具有10张卡，并明示 `2026-06-30 after_cutoff`；事件28新闻有6条短摘要。该轮没有 web_fetch，新闻标题/摘要不能升级为公告正文已读，Q2历史披露缺口也不能补成0。[D2原件，seq12/20/27/28](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D2-stock-rephrased/continuous-episode.json>)。

**VERIFIED · 2026-10-07，当前页头有限读取。** 当前知识库确有[华工科技具名逻辑卡](</Users/a77/knowledge-base-private/wiki/sources/华工科技_000988_个股逻辑卡_20260603.md:1>)与[核聚变概念卡](</Users/a77/knowledge-base-private/wiki/concepts/可控核聚变.md:1>)；只核对页头、日期与少量已命中段，没有通读26KB逻辑卡。页头日期不证明整篇在过去截止日已经可得；也不能拿当前页存在替代那一轮实际召回与送达。

**VERIFIED · 2026-10-07。** D5事件12的 E4/E5/E9、事件22的 E76 原 detail 长度为882/857/914/892，模型副本各为800；连同省略标记预留，共349字符未送达。尾段涉及薄膜电容业务关系、江苏神通订单段及“主营与核聚变交易主题偏离”的反证。逐个与该轮全部工具 `model_content` 的 observation/detail 字符串核对，完整尾段未在其他工具副本出现。标题仍保留“晚于问句日2026-06-11”，因此不能为恢复这些文字绕过时点资格；这只是送达缺口，不是已经批准可用的历史事实。[D5原件，seq12/22](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D5-theme-unseen/continuous-episode.json>)、[实际裁剪规则](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/tool_result_budget.py:123>)。

**VERIFIED · 2026-10-07。** D2事件12另有 observation 被截370字符，但知识卡详情仍另有通道，不能把370直接算作独立事实损失。当前限额已在模型优先改造中放宽为 observation4000、detail800；本审计不重新提出旧上限补丁。记录中的 context_budget 是模型副本的真实标记，而非由原件长度猜测。[D2 seq12](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D2-stock-rephrased/continuous-episode.json>)、[两通道遥测](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/agent_research.py:482>)。

### 图谱、方法、纪律与源身份

**VERIFIED · 2026-10-07。** graph_lookup 默认是概念/暴露索引，输出关系线索，不是兑现事实；另支持研究地图 package/view/trace/compare/scope。evidence_lookup 读本地证据索引。D7实际图谱调用返回空，不能由此断言知识库不存在关系。工厂还用 entity_anchor 形成检索定位，因此“没有调用graph_lookup”不等于图谱完全未参与装配。[图谱工厂](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/agent_research.py:1318>)、[实体定位](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_tools.py:1097>)、[D7 seq10](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D7-nonexistent-entity/continuous-episode.json>)。

**VERIFIED · 2026-10-07。** 9份首轮 prompt 中，8份有798字符的 reading_baseline，D4没有；D6可见 FY-A09 等方法标记。D2/D5另有 retrieval_stages 与723字符题型指导，D9有1028字符情景/研究指导。模型输入证明方法被提供，不证明模型遵守或使用得当。基线明确允许跳过无关方法、证据推翻方法；D4的不注入是已存在的门控，不是本次新发现的丢失。[首轮输入投影](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/episode_protocol.py:504>)、[基线门控](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/knowledge_injection_policy.py:83>)、[D6 prompt_assembled](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D6-ladder-rephrased/continuous-episode.json>)。

**VERIFIED · 2026-10-07。** D6事件9的当日华银卡为1/1，事件24的前日华银卡为1/6；两张卡详情未被裁剪。原稿把前日比例写进当日4板段，后文又写100%；原 draft 与公开答案完全相同，0 invalid_actions，semantic记录为passed。故这项失败不是“相关信息没到模型”或输出删句造成，而是已送达信息的日期归属/推理使用错误；passed与绑定不认证全文。[D6 seq9/24与outcome](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D6-ladder-rephrased/continuous-episode.json>)、[原公开答案](</Users/a77/.finance-runtime/model-first-harness-1006/prod-1/D6-ladder-rephrased/answer.md>)。

**VERIFIED · 2026-10-07。** d729真实修订的 trace 在 assembly 有旧轮身份，controller/plan 的 timeframe 却为空；首轮 prompt 有历史对话，没有 material_grounding 或 prior_tool_evidence，证据池最终为0。事件9/10把07-21/22查询拒为未授权历史窗口；事件15拒绝把直接判断改为 model_reasoning，最终以gap交付。旧答文本和E编号不能替代已登记的原始卡。这证明需要区分“上下文里有旧答”与“原始工具证据合法承接”，不是扩大权限、绕过日期门的理由。[修订trace，controller/plan](</Users/a77/.finance-runtime/answer-quality-closeout-1007/live-d7294e3e4-d6-02/D6-corrective-followup/trace.jsonl:2>)、[修订Episode，seq9/10/15](</Users/a77/.finance-runtime/answer-quality-closeout-1007/live-d7294e3e4-d6-02/D6-corrective-followup/continuous-episode.json>)。

### 索引状态与可复用活性接口

**VERIFIED · 2026-10-07，元数据而非检索实验。** 本地结构索引 meta 记14448源文件/169650块，构建于09-29；全文索引记15350源文件/230573块，构建于09-18。这不是知识全面性分数，也不证明新正文全部可检索。[结构索引meta](</Users/a77/knowledge-base-private/.rag_index/meta.json>)、[全文索引meta](</Users/a77/knowledge-base-private/.rag_index_full/meta.json>)。

**VERIFIED · 2026-10-07。** RAG当前指针为 `readiness-20260927-43430ddd`，其 manifest 状态为validated，包含冻结 code/source/standard/full 路径及 consumer_checks。它与可变知识库目录是不同身份。健康记录只给 rag_runtime/vector_index 等依赖布尔值；本审计未读取生产进程环境或凭据，不能独立认证生产进程此刻绑定了哪个RAG generation。[当前指针](</Users/a77/.finance-runtime/kb-rag-generations/current.json>)、[冻结manifest](</Users/a77/.finance-runtime/kb-rag-generations/generations/readiness-20260927-43430ddd/manifest.json>)、[绑定校验接缝](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/kb_rag.py:568>)。

| 可复用接口 | 它能验证什么 | 不能偷换成什么 | 来源 |
|---|---|---|---|
| `scripts/audit_tool_reachability.py` | 声明→实际工厂→授权→schema的结构可达性，使用临时fixture；需要按准确代码根运行 | 不是已调用、已阅读或自然回答质量 | **VERIFIED · 2026-10-07**：[脚本说明与实现](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/scripts/audit_tool_reachability.py:1>)；本轮未执行工厂或fixture。 |
| `scripts/audit_tool_admission_branches.py` | 源码 admission 分支、允许/拒绝接线 | 不是供应商真值、实际模型消费证明 | **VERIFIED · 2026-10-07**：[脚本](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/scripts/audit_tool_admission_branches.py:531>)。 |
| `tool_menu` / `prompt_assembled` / `tool_result.model_content` | 真正菜单、初始输入、预算后工具正文，可逐卡对原件 | 不以runner返回或审计全量冒充模型看见 | **VERIFIED · 2026-10-07**：[事件写入](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/runtime/agent_episode.py:925>)。 |
| `kb_delivery_telemetry` | observation/detail、命中页/深读段、恢复或剥指针状态分别记录 | 不按一条摘要长度评估正文完整度 | **VERIFIED · 2026-10-07**：[遥测](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/agent_research.py:482>)；最终送达仍以model_content为准。 |
| `EvidenceReadCoverage` + 可选 `evidence_read` | 对已呈现E卡的字面片段/区间做覆盖去重，补读不新造来源或权限 | 不是任意路径的原文读取，也不是理解/蕴含证明 | **VERIFIED · 2026-10-07**：[覆盖对象](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/evidence_read.py:219>)、[双重启用条件](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/runtime/agent_episode.py:3466>)；本轮没有启用它。 |
| `kb_rag` freshness / generation / readiness | 索引、代码、正文绑定及命中恢复/丢弃状态 | 不是“更新命令一定自动成功”，不是健康布尔值证明取证面完整 | **VERIFIED · 2026-10-07**：[freshness fail-closed](</Users/a77/.finance-runtime/finance-workspace-d5d7c5f6017e/intelligence/services/kb_rag.py:2180>)。 |

### 推断与仍未验证

- **[推断]** 更有价值的比较单位是“这条具体相关信息是否以合法日期/来源到达、作者是否正确使用”，不是工具数或prompt长度。D2送达跨知识/财务/新闻，D6两张关键卡完整送达仍误用，已经区分了输送与使用两类问题。依据为上表与相应原件，不主张所有类似题都如此。
- **[推断]** D5可能有值得补读的反证尾段，但必须先解决该段在历史截止日前的资格与索引/原件身份，再通过已有节级检索或已授权补读送达。不能把“当前库有材料”直接升级为当时可用事实。依据为D5实际model_content、当前页头有限读取及freshness门。
- **未验证**：候选自然模型是否主动使用可选研究维度、是否比Pi更正确，生产RAG进程当前精确绑定、生产各fact最新日期与非空覆盖、provider真值、历史PIT完整性。本轮没有发模型或SQL查询，也没有更改root的实验协议。
- **REFERENCE_ONLY**：未访问任何外部网页原文；旧运行的web/news URL只是记录中的线索，本文不认证对应网页正文。文内公开来源日期与财务数值均引用冻结原件，不构成新的金融建议。

## 提炼提示（哪些值得沉淀？）

- 保留“可见菜单→预算后model_content→最终绑定/正文→是否正确使用”的审计链；每层独立标状态，不由后一张绿灯倒推前层。
- 原件按CodeSource、run、task_frame_hash和读取日期固定。发布以后另核身份，不能将f3b的旧消费轨迹、d729的失败修订或a5feb的零调用装配收据混成当前生产质量。
- 若root后续做有限真实A/B，复用已有事件与这些已见失配作诊断；不扩建新评分平台、不自动把本笔记推断写成产品词表或正式能力清单。
