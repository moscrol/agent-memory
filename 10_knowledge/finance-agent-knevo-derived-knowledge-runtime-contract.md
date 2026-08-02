---
title: "金融 Agent 知识运行时契约：从 Knevo 逆向提炼"
type: knowledge
agent: devin
source: "Knevo 只读运行态实测 E-006 + 本地 Agent 架构对照"
date: 2026-08-02
tags: [finance-agent, knowledge-runtime, rag, hybrid-retrieval, knowledge-graph, memory, provenance, evaluation]
status: verified
related: ["[[knevo-reverse-engineering]]", "[[multi-agent-memory-system-design]]", "[[finance-answer-orchestrator]]", "[[finance-answer-self-review-framework]]"]
---

# 金融 Agent 知识运行时契约

> 这不是复制 Knevo 的实现，而是从其运行态行为中提炼出可迁移的类型纯度、检索路由、证据链和记忆状态机。
> 核心目标：让后续 Agent 知道“什么可以查、查到什么、什么时候能下结论、什么必须等待验证”。

## 1. 四类数据平面

不要把所有知识都塞进一个向量库。至少区分四个平面：

| 平面 | 承载内容 | 主要读法 | 是否可直接作为结论 |
|---|---|---|---|
| `graph` | 实体、关系、结构化事实、证据切片 | 实体消歧 → 图谱上下文 | 只有存在 facts + evidence 时才可直接引用 |
| `shared_memory` | 社区/平台沉淀的观察、洞察、推理模式 | 语义/关键词混合检索 | 作为研究线索和先验，不能代替当前事实 |
| `user_memory` | 用户个人判断、偏好、交互史 | 相关记忆检索 | 可作为用户基线，不能冒充客观事实 |
| `provider` | 行情、财务、公告、新闻等当前事实 | 确定性数据查询 | 对易变事实进行最终核验 |

人话版：图谱像地图，文本记忆像图书馆，用户记忆像笔记本，provider 像今天的仪表盘。地图上有一个城市，不代表地图上有道路；图书馆里的观点，也不等于今天的行情。

## 2. 两条检索通路

### 2.1 文本记忆通路

```text
query planner
→ narrow / broad / counter query
→ shared_memory retrieval
→ cross-query dedup
→ relevance / recency / evidence filtering
→ provider verification
→ answer
```

适合：

- 方法论和推理框架；
- 历史观察；
- 用户过去的判断；
- 产业叙事和候选假设。

### 2.2 图谱通路

```text
entity_resolve
→ resolved / candidate / unresolved
→ graph_context(hops)
→ entities + edges + facts + evidence + gaps
→ answer or downgrade
```

适合：

- 公司、产品、行业、人物等实体关系；
- 上下游、客户、竞对、替代关系；
- 可追溯的结构化事实。

硬规则：不能用文本记忆查询接口伪装图谱查询。`sources=["fundacore"]` 返回空，不代表图谱没有数据，只代表调用了错误接口；正确接口也可能返回实体但没有边和事实。

## 3. 记忆卡最小契约

每条知识卡至少保留：

```json
{
  "id": "stable-id",
  "source_plane": "graph|shared_memory|user_memory|provider",
  "kind": "fact|event|observation|insight|relation|reasoning_pattern",
  "content": "...",
  "tags": ["..."],
  "entity_refs": [
    {"mention": "生益科技", "entity_id": "...", "resolution": "resolved"}
  ],
  "confidence": 0.0,
  "source_evidence": ["locator-or-evidence-id"],
  "updated_at": "2026-08-02T00:00:00Z",
  "status": "candidate|accepted|rejected|active|archived"
}
```

`confidence` 必须注明语义：

```text
memory confidence ≠ calibrated event probability
hitCount ≠ prediction win rate
```

不要让一个名为 `confidence` 的字段同时表示记忆质量、实体解析置信度和预测概率。

## 4. 检索规划与去重

一次宽 query 很容易把相邻主题带进主结论。建议至少发三类 query：

```text
窄：实体 + 产品 + 代码
宽：上游 + 下游 + 同业 + 宏观
反：产能过剩 + 需求不及 + 替代 + 竞争恶化
```

必要时加时间 query：

```text
近期变化 / 指定日期 / 过去 30 天
```

每个结果保留检索 provenance（来源链）：

```json
{
  "query_id": "q-001",
  "source_plane": "shared_memory",
  "result_id": "fmr-...",
  "rank": 2,
  "retrieved_at": "...",
  "cross_query_support": 3,
  "score": null
}
```

`cross_query_support` 可以表示主题覆盖稳定性，但不能直接表示预测正确率。

推荐的排序层次：

```text
候选召回
→ 相关性排序
→ 时间/当前性过滤
→ 来源与证据分层
→ 跨 query 去重
→ 反方覆盖检查
→ provider 核验
```

即使底层最终采用 Hybrid Retrieval（向量 + BM25 + rerank），这些质量层也不能省。面试表达可以说：检索器负责找候选，证据裁决器负责决定能不能引用，生成器只负责组织已裁决内容。

## 5. 图谱质量门槛

图谱工具的返回不能只有 `entities`。必须保留：

```text
entities
edges
edge_claims
facts
evidence
gaps
```

状态判断：

| 返回状态 | 允许的回答 |
|---|---|
| 有实体 + 有边 + 有事实 + 有证据 | 可以引用具体关系，并附证据 |
| 有实体但无边/事实 | 只能说存在实体节点，不能推断关系 |
| 只有 candidate | 只能说实体未确认，不能当作图谱实体 |
| `no_neighbors` / `no_facts` | 明确图谱缺口，转文本记忆或 provider 核验 |

这是一个通用防幻觉规则：实体名称相近、同属一个行业、或同时出现在同一篇文章中，都不能自动生成关系。

## 6. 记忆推荐状态机

候选记忆和长期记忆是两个不同的状态：

```text
conversation
→ extraction candidate
→ pending batch
→ per-item recommendation
→ user accept / reject
→ active long-term memory / discarded
```

推荐项必须保存来源会话和 batch：

```text
recommendation_id
batch_id
conversation_id
conversation_title
content
created_at
status
```

禁止以下捷径：

- UI 出现“待处理”就当作已写入长期记忆；
- 看到推荐数量增加就当作写回成功；
- 把一次回答自动抽出的判断直接放进核心记忆；
- 把用户拒绝/接受和模型自动提炼混在一个操作里。

建议写权限分层：

```text
shared_memory / graph：Agent 默认只读
user_memory：Agent 只能提出候选，用户确认后写入
prediction_ledger：系统可追加验证结果，但不能回写原始判断
```

## 7. 预测验证单独建台账

知识记忆解决“以后可以参考什么”；预测台账解决“过去判断是否被验证”。二者不要合并。

```json
{
  "forecast_id": "forecast-001",
  "claim": "...",
  "created_at": "...",
  "horizon": "T+3",
  "verification_conditions": [
    {"field": "...", "op": ">=", "value": 0}
  ],
  "outcome": "hit|miss|unverifiable",
  "error_class": "...",
  "verified_at": "..."
}
```

只有经过时间窗验证的 `hit/miss` 才能进入胜率统计。记忆 `hitCount` 只能衡量被引用频率，不能当作模型预测能力。

## 8. 运行一致性验收

异步 Agent 不能只以 HTTP 200 或单个 completed 字段判定成功。验收至少检查：

```text
1. turn 创建成功
2. 用户 payload 已持久化
3. 工具调用事件实际出现
4. assistant output 已持久化
5. conversation index 已刷新
```

任一不一致，写入：

```text
execution_consistency_warning
```

这类检查在任何 UI 自动化、SSE 流式任务、异步 sub-agent、队列 worker 中都适用。

## 9. Agent 吸收优先级

### P0：先做类型纯度

给每条召回结果加 `source_plane`、`kind`、`evidence`、`status`，并在回答前执行来源隔离。

### P0：先做图谱空结果门控

没有边、事实或证据时，必须结构化降级，禁止 LLM 自由补关系。

### P1：加入检索 provenance 与跨 query 支持度

为未来做 Hybrid Retrieval、rerank 和离线评测保留可解释输入。

### P1：推荐和长期 memory 分库/分状态

用户确认是写入长期记忆的显式 seam（可替换点），不要让提炼器直接拥有写权限。

### P2：把运行一致性纳入 harness

对 UI、SSE、worker、sub-agent 统一做 payload、事件、持久化和索引四层验收。

## 10. 不应直接复制的部分

以下内容只能作为待验证假设，不能直接迁移成规则：

- Knevo 的具体排序权重；
- memory confidence 的数值含义；
- recommendation 自动去重和淘汰公式；
- `fundacore` 的全库覆盖程度；
- UI transcript 不同步的后端根因；
- 任何“命中计数高所以判断可靠”的推论。
