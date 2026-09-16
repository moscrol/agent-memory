---
title: "Knevo 44 轮原文第 15–36 轮蒸馏草稿（图谱/知识库结构 + skill/工具重叠审计）"
type: inbox
agent: claude
source: "60_dialogues/knevo/2026-08-08-工具编排与step上限-44轮原文.md 第 15–36 轮，对照 knevo-engineering-probes-2026-08-07 与 knevo-reverse-engineering"
date: 2026-09-16
tags: [inbox, knevo, reverse-engineering, knowledge-graph, skill-system]
status: draft
---

P=engineering-probes，R=reverse-engineering。[自述*]=转述被日志截断的工具返回。派工单首题「固定/agent RAG」属轮 28，一并收入。

## 1. 第 29–36 轮增量（含轮 28）

**A 检索模式（轮 28）**
- A1 [自述] fundacore 是「agent 编排的固定 RAG」：后端一次做完 `graph_hops=2`，agent 只决定何时查/查什么/几跳，不逐跳导航；改写重试是 finance-mode 指令非工具行为。→ 新增。
- A2 [实测] description 原文 "compact **SQL-backed** finance graph context"（轮 20/24）。→ 修订 P §9.2「graph_hops 是图数据库最强信号 / property graph」。

**B 语义压缩归属（轮 29）**
- B1 [自述] 主 agent 派单前先检索、压成「已收集来源摘要」注入 task；子 agent 全量重查、在分析综合步内压缩、emit 完整报告；主 agent 只串联不二次压缩。→ 部分已有（P §4、R §1.1.3/§1.4）；修订 R §1.1 表「主线程汇总=提炼核心结论」。
- B2 [实测] 纯架构讨论每轮调 `finance_memory_stage_extraction(candidates=[])` 得 `status:"empty"`、`batchId:null`（轮 19/26/29/32/33）= finance-mode「空确认」行为兑现。→ 新增。

**C 图谱返回形态与覆盖（轮 30/31/34/35）**
- C1 [实测] 实体 `{id,name,type,origin,description}`；origin ∈ finmemory/fundacore/merged；id 族 `knevo-ent-<16hex|uuid>`（finmemory）、`fent-fc-<20hex>`/`fent-<8hex>`（fundacore）。同一实体可双 id 并存（中际旭创 `fent-caeb0d69` / `knevo-ent-723445e3c72c469a`），merged 只融合 description。→ 新增。
- C2 [实测] type 观测词表：stock company product industry sector concept person driver industrychain valuationmethod macro_indicator（finmemory 侧）macro_factor（fundacore 侧）；Knevo 自述合写为 macro 并列 event（未观测）。类型噪音：CPO=stock、黄仁勋=concept。→ 新增。
- C3 [实测] 默认值 `graph_hops=2`、`max_facts=12(1–20)`、`max_edges=30(1–60)`、`max_evidence=8(0–16)`（轮 24）；轮 30/31/34 五次返回 `edges` 恒 =30 → 边数是截断值。→ 修订 P §9.2/§10.4（只记范围）。
- C4 [实测] `sourceScope.applied=["finmemory","fundacore"], excluded=["local"]`；对照 P §13.17.1 勾选状态推断 `local`≡user-finmemory 服务端别名。→ 修订 R §3B「sources 三值」。
- C5 [实测] `gaps` ∈ entity_not_found/no_neighbors/no_facts；`agentGuidance` 仅 no_neighbors 时下发 "No graph neighborhood was found; treat this as a coverage gap and fall back to other finance data sources."，entity_not_found 时 null。→ 新增（补 P §13.17.3）。
- C6 [自述*] 边类型 17 种（全表见第 3 节拼接块）；可带量化限定（supplies 50%+、impacts 领先 1–2 季度）；research_meta 级边 `evidenceChunkIds` 可空。→ 修订 R §3B（旧表 supplies_to/strategic_partner 未见）。
- C7 [自述*] facts 挂实体、类型 observation/insight/event；evidence `{sourceTitle, sourceId:"source:md|pdf:<slug>:<hash>", section, chunkIndex, contentPreview}`。→ 新增（R §3.0 只记 evidenceChunkIds）。
- C8 [实测] 覆盖快照 2026-08-08：AI/半导体 34–37 实体、光通信 26–32、新能源 9/8 边、能源大宗 15/16；白酒、政策/制裁 entity_not_found；宏观/人物仅孤点。→ 新增（R §3B 仅泛言「偏头部」）。
- C9 [实测] `finance_entity_resolve` 置信三档 0.98 exact / 0.72 partial / 0.35 create_candidate(entityId null)；代码/通名消歧粗（300308→Share Capital）。→ 新增。
- C10 [实测] 记忆 `entityRefs` 另有精简形态 `{mention,entityId,confidence:0.72(常量),graphConfidence}`。→ 修订 P §13.17.2「稳定字段集」。

**D 非 wiki 的双引擎（轮 31/33/34）**
- D1 [自述] memory_query=向量/混合层，graph_context=图查询层，经 entity_refs 双向枢转。→ 已有 R §3.0/§3B、P §13.17.4；「实体→sourceId→记忆」反向未见佐证。
- D2 [自述] 图 vs wiki 八维对照；wiki 占优：单实体深度、因果叙事、长尾、人读；图给广度、记忆长文给深度。→ 新增。
- D3 [自述] 行业无独立页，行业=子图；图给结构、记忆给判断。→ 新增。

**E ingest（轮 32）**
- E1 [自述·推断] 文档管道程序化 → 抽取 LLM（消歧/关系/fact/摘要/confidence）→ 融合程序+LLM → 记忆层 LLM+人工；自承不知模型/prompt/消歧策略/provenance。→ 修订 R §3B「构建逻辑」：边主体来自文档抽取，非仅记忆候选 relationType。

**F 组成与风远（轮 35/36）**
- F1 [自述] 「金融本体知识库」= fundacore + finmemory + user-finmemory（+ `recall_short_term` 笔记 12 条）；「风远知识库 = finmemory 中 sourceLabel=风远94 的子集」。→ 修订/矛盾：P §13.17.1 UI 把 finmemory 整体命名为风远94，「金融本体图谱」仅指 fundacore。
- F2 [自述] 短期记忆层 = `stm-*` 工作笔记（kind/market/localDate/importance）。→ 修订 R §3「层级」：候选（batchId pending）与 stm 笔记是两个对象。
- F3 [自述] 风远五共性：判断+框架+验证条件；框架优先；带触发/失效边界；自指修正不删旧；具体→机制→模式→迁移。→ 已有 judgment-distillation-six-rules、P §13.17.5(d)；修订：「reasoning_pattern 带 `__core__`」过度概括（P §13.17.7 insight/fact/relation 亦带）；修正链未按 id 复核。

| 判定 | 条目 |
|---|---|
| 新增 10 | A1 B2 C1 C2 C5 C7 C8 C9 D2 D3 |
| 修订 10 | A2 B1 C3 C4 C6 C10 E1 F1 F2 F3 |
| 已有 1 | D1 |

## 2. 第 15–28 轮重叠审计表

| 轮 | 内容项 | P 小节（R 补充） | 判定 |
|---|---|---|---|
| 15 | finance-mode 第 1 段：硬触发五条、执行规则、豁免三条、关键词构造五法 | §1；R §1.1.4、§3.1.1 | 部分：缺「快答=检索后短答」、豁免原文、构造法之多形态/复合拆解/时间维度 |
| 16 | finance-mode 第 2–9 段全文 | §1 来源纪律、§3、§4、§6；R §1.1.2、§3.0、§3.3 | 部分：身份与表达、跨市场时间/盘面日、九步流程、意图→preset→skill 九行表、thesis check 七条、抽取正反例、产物路径、交付契约原文均无；禁止事项 4 条仅 2 |
| 17 | finance-analyze-stock 全文 | §8 仅 ID；R §3C.2 骨架 | 部分：六步流程、框架七项、输出契约无 |
| 18 | earnings-review / industry-report / industry-track 全文 | §8 仅 ID；R §1.1.3、§1.2 | earnings-review 未覆盖；report/track 部分（原文无） |
| 19 | forecast-event / kol-analyze / review-check / associate 全文 | §13.16 仅 review-check 的 workflow payload | 四篇未覆盖：决策者行为模拟+互斥情景树；KOL 双模式；6 维 A–F 阈值、PASS/WARN/FAIL、FAIL 阻塞写回；联想六维+来源标签 |
| 20 | 工具注册表 26→36 + description 原文 | §6、§13.6、§13.8；R §1.2 | 部分：web_cite、read_skill_file、get_bg_task、wait_for_seconds、finance_memory_write 无；「注册表=注入的 function definitions」无 |
| 21 | 茅台案例：硬触发扫描→并行 tool_calls→tool_result→渐进补调 | §10.2、§13.13、§13.16 | 部分：机制已有；「workspace 路由注入」「每步可溯源到规则」自述无 |
| 23 | 36 工具跑测 27/4/5；load_workflow payload；路径重定向；memory_write 直写 | §6、§7、§13.7、§13.10、§13.16；R §11.2 | 部分：`finance_statement` disabled「no provider supports statement」与 §6 路由表矛盾；`finance_memory_write` 直写 durable 未覆盖且与 R §3.0「只有提案权」矛盾；数据集名 valuation-history/constituents/movers/insight 无 |
| 24 | 全部 parameters schema + 渐进披露四设计点 | §9.2、§13.17.6、§4、§5、§2 | 部分：graph_context 默认值、instrument include 段、stage_extraction 入参无；四设计点（dataset 是约定非枚举等）无 |
| 22/25 | 仅指令 / 衍生汇总 | 同 23 | 无新增 |
| 26 | 消融实验：纯 description 重构调用；skill 增量=策略指令/数据陷阱/输出纪律 | 无 | 未覆盖 |
| 27 | harness 级 vs skill 级；自承无 post-gen checker | §13.1、§13.5 | 部分：白名单/隔离已有；「纯靠 skill 文本」与可程序化清单未覆盖 |
| 28 | 固定 RAG vs agent RAG | §9.2；R §3B | 未覆盖（见 A1） |

未覆盖计 8 项：轮 18 earnings-review、轮 19 四篇、轮 26、轮 27 后半、轮 28。

## 3. 建议拼接块

追加到 `knevo-reverse-engineering.md` §3B 末尾：

```markdown
### 3B.2 2026-08-08 会话：图谱与知识库结构自述

来源 `60_dialogues/knevo/2026-08-08-工具编排与step上限-44轮原文.md` 轮 28–36。

- **检索模式**（轮 28，[自述]）：agent 编排的固定 RAG，后端一次做完 `graph_hops=2`，agent 不逐跳导航。description 自称 "SQL-backed"（轮 24，[实测]），P §9.2 property graph 推断待裁决。
- **实体对象**（轮 30/31，[实测]）：`{id,name,type,origin,description}`；origin ∈ finmemory/fundacore/merged；id 族 `knevo-ent-*` 与 `fent-fc-*`/`fent-*`；同名实体可双 id 并存，merged 只融合 description。
- **type 词表**（[实测]）：stock company product industry sector concept person driver industrychain valuationmethod macro_indicator macro_factor；类型噪音常见。
- **边类型**（轮 30/33/34，[自述*]）：competes_with supplies customer_of generates part_of belongs_to impacts exposed_to drives complements uses_method same_sector related_to upstream_of substitutes constrains affects_demand；可带量化限定；research_meta 级边可无 evidence。
- **默认截断**（[实测]）：graph_hops 2 / max_facts 12 / max_edges 30 / max_evidence 8；五次返回 edges 恒 30，边数是截断值。
- **scope 与 gaps**（[实测]）：`excluded=["local"]`，local≡user-finmemory（待裁决）；gaps ∈ entity_not_found/no_neighbors/no_facts，agentGuidance 仅 no_neighbors 时下发。
- **facts/evidence**（轮 32/35，[自述*]）：facts 挂实体、类型 observation/insight/event；evidence `{sourceTitle, sourceId:"source:md|pdf:<slug>:<hash>", section, chunkIndex, contentPreview}`。
- **覆盖快照 2026-08-08**（[实测]）：AI/半导体、光通信最密（30+ 实体）；新能源、能源大宗浅；白酒、政策 entity_not_found，宏观仅 CPI 孤点。
- **ingest**（轮 32，[自述·推断]）：文档管道程序化 → 抽取 LLM → 融合程序+LLM → 记忆层 LLM+人工；边主体来自文档抽取。
- **非 wiki**（轮 31/33/34，[自述]）：图给广度，记忆长文给深度；行业=子图。
- **组成**（轮 35/36，[自述]）：fundacore + finmemory + user-finmemory + stm 笔记；「风远=finmemory 子集」与 P §13.17.1 矛盾，待裁决。
```

追加到 `60_dialogues/INDEX.md`：

`| 2026-08-08 | [[2026-08-08-工具编排与step上限-44轮原文]] | 工具编排与 step 上限：skill/工具全文检阅、图谱与知识库结构、风远记忆共性 | 探针, 图谱, skill系统 | partial |`

## 4. 采信提醒

声明面：C6/C7 为截断返回的转述；E1 为推断；D1 反向枢转、F3 修正链无佐证；轮 33/34 ASCII 图边方向前后不一（5G↔中际旭创），勿按图录边。

需人裁决：
1. 风远 = finmemory 子集（轮 36）vs UI 把 finmemory 整体命名为「风远94共享数据库」（P §13.17.1）；Knevo 把「金融本体知识库」扩义为三库之和。
2. `finance_memory_write` 直写 durable `fmr-8a0513d6`→user-finmemory（轮 23 [实测]）vs R §3.0「agent 只有提案权」：提案是 skill 纪律非 harness 限制。
3. 主 agent 只串联不二次压缩（轮 29）vs R §1.1「主线程汇总=提炼核心结论」。
4. 次级：SQL-backed vs P §9.2；`local` vs `user-finmemory`；`finance_statement` disabled vs P §6；「reasoning_pattern 带 `__core__`」过度概括。
