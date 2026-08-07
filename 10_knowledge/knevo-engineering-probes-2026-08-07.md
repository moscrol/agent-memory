---
title: "Knevo 工程探针发现 2026-08-07——skill 硬规则/API 参数/编排逻辑"
type: knowledge
agent: devin
date: 2026-08-07
tags: [knevo, reverse-engineering, skill-system, api, engineering, system-prompt]
status: verified
---

# Knevo 工程探针发现（2026-08-07 直接引用）

## 1. finance-mode 硬规则段（原文引用）

### ⚡ 检索硬触发 T1-T5

```
只要用户消息命中下列任一条件，回答前必须先调用对应工具——
即使是快答、即使用户没说"查一下"、即使你自认为已经知道答案：

T1. 出现具体标的（公司名/股票代码/ETF/指数/板块/行业）
→ 必须 finance_memory_query + finance_quote
→ 个股概览优先用 finance_instrument(symbol=…) 一次拿全

T2. 涉及「最近/现在/今天/最新/近期/这两天」+ 行情/消息/事件/公告/异动
→ 必须 finance_news（带 days）

T3. 涉及产业链/上下游/竞争对手/关联公司
→ 必须 finance_entity_resolve + finance_graph_context

T4. 涉及财报/营收/利润/现金流/估值/PE/PB
→ 必须 finance_statement 或 finance_instrument 的 profile 段

T5. 用户给出观点/持仓/看多看空/目标价/止损线
→ 必须 finance_memory_query 取历史基线 + provider 核验当前状态
```

额外硬规则：
- **并行发起**——记忆+行情+新闻同一轮一起调，不要串行
- **必须实际调用**——"想到要查"不算；空结果也是信息，要如实披露

### 来源标注纪律
```
- 不在通用研究模式下主动调用金融专属 provider
- 不把 provider 缺口、模型推断或历史记忆包装成实时事实
```

## 2. suggest_options 生成机制

**结论：100% LLM 推理生成，不是模板拼接。**

证据：
1. 工具 schema 只定义了 `{description, content}[]` 数组结构 + 长度约束（2-4 个），**没有预置模板/分类标签/静态选项池**
2. 生成时机：要求在回答末尾 **INLINE 调用**，意味着在完整推理后实时生成
3. 生成信号来源：
   - 当前对话主题（最核心信号）
   - 报告的结构性缺口（从「证据缺口与补证清单」中抽取最高优先级转成 follow-up）
   - 产业链关联（横向联想）
   - 时间维度（催化节点即将到来的事件转成"持续跟踪"类选项）
   - 历史记忆（用户金融记忆中已有框架/关注点）

输出格式约束：
- content 写得更长更具体
- 内容写为用户会自己输入的自然语言 follow-up

## 3. finance_memory_query API 参数

### 参数列表
| 参数 | 类型 | 说明 |
|------|------|------|
| `query` | string（自然语言） | 语义检索，非结构化关键词 |
| `days` | int（可选） | 时间窗口，做时间衰减过滤 |
| `ownership` | string（可选） | `personal` / `shared`，区分来源 |
| `limit` | int | 召回上限 30 条 |

### 排序算法
- 后端实现：**hybrid search（dense embedding + sparse/keyword 双路召回再融合排序）**
- 排序信号：**相关度 + 重要性混合加权**
- 使用方不能假设 top-1 就是"最相关的"——需要人工分层和去噪

### 检索词构造规则（窄/宽/反三口径）
- **窄口径**：核心实体 + 核心产品 + 代码（多形态覆盖）
- **宽口径**：上游 + 下游 + 同业 + 宏观/主题
- **反方向**：主动加反方/风险词（"减产 库存 杀估值 竞争加剧"）

### 空结果改写重试（硬规则）
- 首次调用 + 最多 2 次改写 = 总共 3 次
- 改写手段：中英切换 → 简称↔全称 → 公司名↔代码

### 使用纪律
- 单条命中只能作为 prior
- 先区分来源层，再分层解读
- 宽问题要拆检索：从命中结果中抽 2-5 个关键触发器改写查询
- 不能一次搜索后直接下结论
