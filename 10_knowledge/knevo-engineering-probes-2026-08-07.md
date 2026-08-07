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

## 4. `spawn_sub_agent` 编排契约

### 完整参数签名

```text
spawn_sub_agent(
  task: string                 # required
  preset: string               # required enum
  title?: string
  skill_ids?: string[]         # finance-mode 入口要求显式传入
  mode?: string                # default: "isolated"
  attachments?: array
  memory_ids?: string[]
)
```

### `preset` 枚举与权限

| preset | 权限/用途 |
|---|---|
| `report-only` | 只读：web、文件、记忆 |
| `producer` | 研究与产出：`report-only` + 文件/记忆写入 |
| `experimenter` | 读写文件 + sandbox；V1 的 sandbox 对 sub-agent 受限 |
| `finance-reviewer` | 金融只读：行情、新闻、财报、投研记忆、图谱 |
| `finance-researcher` | 金融研究：`finance-reviewer` + 写文件 + 记忆候选暂存 |
| `finance-producer` | 金融全能：`finance-researcher` + 组合工具 + 直接写投研记忆 |

`mode`：`isolated`（默认，独立会话）、`snapshot`、`inherit`（继承主会话上下文，按 token 计费）。

### `task` 的实际约定

`task` 是自由格式字符串，而非 JSON schema；它是 sub-agent 唯一可见的任务指令，不会自动获得主会话或用户原始消息。有效任务通常自包含：

1. 研究范围：行业定义、地域、时间范围、目标读者。
2. 结构要求：产业链环节及每环节的标的、壁垒、国产替代、量产时间线等维度。
3. 专题和视角：中国/海外对比、政策、BOM 或特定专题。
4. 输出契约：目标文件路径和报告骨架。

“范围 + 记忆线索 + 输出格式”是实践惯例，而非框架硬约束。

## 5. 投研记忆对象模型

### 写入 schema

必填：

```text
kind: "entity" | "observation" | "relation" | "event" | "insight" |
      "reasoning_pattern" | "fact"
title: string
content: string
```

可选：`entity_refs`、`tags`、`source_refs`、`confidence: 0..1`、`importance: 0..1`。

查询结果包含：`id`、`sourceLabel`、`ownership`（`personal`/`shared`）、`kind`、`title`、`content`、`confidence`、`importance`、`updatedAt`、`hitCount`、`entity_refs`、`tags`。

### `kind` 语义与入库标准

| kind | 入库标准 |
|---|---|
| `fact` | 有明确来源、可交叉验证、非时间敏感的事实陈述 |
| `event` | 包含明确时间、实体、动作且可验证的离散事件 |
| `insight` | 有证据前提和完整逻辑链、可脱离原对话理解的结论；不能是材料复述 |
| `relation` | 有明确 source/target 实体与关系类型，如供应、竞争、客户、投资 |
| `reasoning_pattern` | 可复用的模式，包含触发条件、预期结果、推理链与失效条件 |
| `observation` | 当前状态的描述性、偏定性的观察；不强制要求完整推理链 |
| `entity` | 可被其它条目引用的规范化实体锚点 |

`entity_refs` 可带实体名称、类型、识别置信度、别名、标识符；`relation` 条目还带 `role`（`source`/`target`/`from`/`to`）和 `relationType`。

## 6. Provider 路由与降级

### 已确认的工具路由

| 工具 | 数据源 | 覆盖 |
|---|---|---|
| `finance_instrument` | `datasvc` 融合 | 个股 profile、行情、日线、新闻、资金、两融、研报、一致预期；A/美/港股 |
| `finance_quote` | `datasvc` → 腾讯（A股五档）/ Massive（美股）/ yfinance（港股） | 实时行情、日 K、指数 |
| `finance_news` | `datasvc` 本地 feed | A 股快讯、美股 Benzinga/Massive、SEC、宏观 |
| `finance_options` | Massive / OPRA | 美股期权链 |
| `finance_margin_market` | `datasvc` → iFinD | A 股两融汇总 |
| `finance_northbound` / `finance_hsgt` | `datasvc` → iFinD | 北向成交、陆股通持仓 |
| `finance_shareholders` | `datasvc` → iFinD | A 股股东结构 |
| `finance_statement` | `datasvc` / fundacore | 财报、估值、基本面 |
| `finance_search_data` | `datasvc` / Polymarket / web | 数据集、预测市场、成分股、涨跌榜 |

可确认的 provider：`datasvc` 是主融合服务；`iFinD` 提供 A 股专题数据；`Polymarket` 提供事件概率/赔率；Massive 提供美股行情/期权。`ftshare`、`gangtise`、`mx-finance` 在 tool schema 中未被确认，不能据此断言其职责。

### 降级原则

核心模式是 `datasvc` → `web`。典型例子：

- 个股全景：`finance_instrument` → `finance_quote` + `finance_news` + `finance_search_data`。
- A 股现价：`finance_quote`（datasvc/Tencent）→ web。
- 美股现价：`finance_quote`（datasvc/Massive）→ yfinance → web。
- 财报：`finance_instrument` → web 完整三表。
- 期权：`finance_options`（Massive）无本地兜底。
- 北向净流入已停发：转用 `finance_northbound`（成交）或 `finance_hsgt`（持仓）。

### `finance_provider_status` 状态语义

状态是 provider 级可用性摘要：`enabled`/`disabled`、`missing_config`、`degraded`、`NO_DATA_FOR_QUERY`。它不是固定路由表；当前 ready/degraded 状态必须在运行时调用此工具或从具体 provider 结果读取。响应对用户须脱敏表达，不能将 `disabled`、配置缺失、限流等混为一般 `failed`。

## 7. `load_workflow` 黑盒边界

### 可见 schema

```text
load_workflow(workflow_id: string) -> workflow payload
```

调用侧只能按固定 ID 查询，未暴露 `inputs`、`version`、`mode`、`memory_ids` 或 `skill_ids` 参数。工作流 payload 可观察到稳定字段：`label`、`domain`、`executionKind`、`preset`、`primarySkillId`、`internalSkillIds`、`spawn`、`instructions`；其中 `spawn` 会向调用侧传递子代理的 preset、mode、skill_ids 和 title。

示例行为路由：

```text
spawn.preset = spawn.preset
spawn.mode = spawn.mode
spawn.skill_ids = spawn.skill_ids
task = 用户需求 + executorInstructions
```

### 行为观察与未知项

- 工作流可观察到的执行顺序通常是：`load_skill` → 工具调用（可并行）→ `write_file` → `emit`。
- `inspect_sub_agent` 至少能观察到 `running`、`done`；内部状态枚举和转移未暴露。
- `load_workflow` 本身更像“按 ID 返回编排指令”，而不是由调用侧直接提交 DAG。
- workflow 的内部注册存储、完整 ID 清单、YAML/JSON 定义格式、DAG 表示、run_id、checkpoint、重试和幂等机制均未确认。
- 行为上观察到 timeout 后不会自动重启，部分产物也不保证自动保存；这是当前调用观察，不等同于引擎内部规范。
- 不能把 `workflow = skill(s) + preset + mode + routing` 当成已公开的数据结构；它是当前行为的架构抽象。

## 8. Skill 注册、加载与权限边界

### 加载入口与 ID 形态

已确认的入口：

```text
load_skill(skill_id: string)
spawn_sub_agent(skill_ids: string[])
```

已成功观察到的 ID 包括 `finance-mode`、`finance-industry-report`、`finance-analyze-stock`、`finance-earnings-review`、`finance-industry-track`、`finance-forecast-event`、`finance-kol-analyze`、`finance-associate`、`finance-review-check`。命名规律是 `{domain}-{function}`，小写连字符，无版本号、路径或扩展名；别名、路径格式和显式 `@version` 尚未确认。

`search_skills` 在金融模式返回空列表，但 `load_skill("finance-mode")` 与 `load_skill("finance-industry-report")` 可用。这表明 user-selectable skill 列表与 workspace preset / 内部 skill 注册存在分离，不能把“可选列表为空”理解成 skill 不存在。

### 加载顺序与版本优先级

经验上 `finance-mode` 位于 `finance-industry-report` 之前，作为基础层；后者是领域层。系统提示明确：当前 workspace preset 的 skill 版本优先于此前加载版本和压缩摘要，因此至少存在某种版本/缓存优先级。具体版本号、TTL 和缓存实现未暴露。

### 内容优先级与权限

可观察的注入层可抽象为：

1. 基础模型规则：工具权限、安全限制、平台级约束。
2. Workspace preset：例如自动注入的 `finance-mode`。
3. `load_skill` 加载的 skill body：行为、来源和输出纪律。
4. 当前系统上下文：会话规则与短期记忆。
5. 用户消息。

Skill body 可以覆盖默认语言、研究风格和输出结构，也可以进一步收紧工具使用纪律；但不能授予 preset 未开放的新工具，不能撤销平台安全限制，不能把禁止实盘交易等约束改成允许。多个 skill 冲突时的精确解决算法未确认。

### UI 与错误处理

“选择技能，当前无技能”更可能表示 user-selectable 列表为空；workspace preset 注入的 `finance-mode` 仍然可以被内部加载。是否只附加当前消息、是否持久化到整个会话、是否改变 provider 配置，均未直接确认。

已询问的失败类别包括 404、不匹配版本、加载超时、冲突和权限拒绝，但调用侧未获得稳定错误码或公开回退协议。可推断存在“当前 workspace preset 版本 → 之前加载版本 → 压缩摘要”的降级顺序；registry、version lock、缓存 TTL、审计日志和冲突算法均是黑盒。

### 最小组合抽象

```json
{
  "preset": "report-only",
  "mode": "isolated",
  "skill_ids": ["knowledge-readonly", "database-query"],
  "task": "读取知识库相关条目，查询允许的数据集，输出带来源的摘要；不得写文件、修改记忆或执行交易。"
}
```

该示例表达组合关系，不代表 `knowledge-readonly` 和 `database-query` 是已确认存在的真实 ID。skill_ids 能组合指令和已开放能力，但不能突破 preset 的工具权限、平台安全限制或数据访问控制。
