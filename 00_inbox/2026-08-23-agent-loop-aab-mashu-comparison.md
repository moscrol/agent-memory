---
title: "Agent Book × 马书：Agent Loop / Harness 设计原则与金融 Workbench 启示"
type: inbox
agent: codex
source: "Agent Book 与马书本地一手原文；finance-workspace-private 当前代码静态核对"
date: 2026-08-23
tags: [inbox, agent-loop, harness, agent-book, mashu, finance-workbench]
status: draft
---

# Agent Book × 马书：Agent Loop / Harness 设计原则与金融 Workbench 启示

> 原始输出/研究说明：本笔记直接读取两份指定原文。`SUMMARY.md`、distilled 笔记和既有结论只用于定位章节，不作为证据。下文把原文事实标为 **VERIFIED（2026-08-23）**，把跨书综合与对当前项目的建议标为 **[推断]**。

## 结论先行

两书没有给出两套相互竞争的 loop。它们描述的是同一件事的两个分辨率：**Agent Book 给出“为什么这样设计”的规范框架，马书给出“一个生产 loop 怎样把它落实成状态机”的实现解剖**。共同底线是：模型负责提出下一步，Harness 负责保存真实状态、执行工具、约束边界、验证结果、有限恢复并决定是否继续；不能让模型仅凭一段流畅文本自行宣布成功。

对 `finance-workspace-private` 最关键的改进不是重写现有 episode loop，而是给“视角是否真的生效”增加一个可验证、可追踪的结构化状态：**回答中的 SPT 标题只能由成功的 `PerspectiveActivation` 凭证产生，不能由用户曾经选择过 SPT 这一请求事实产生。**

## 来源范围与证据状态

- **Agent Book**：本地仓库 `/Users/a77/ai-agent-book`，读取时 HEAD 为 `761352efdcf938c8d47c5c134045088a1db7fd84`，`main` 干净。canonical 为 [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book/tree/761352efdcf938c8d47c5c134045088a1db7fd84)。
- **马书**：本地仓库 `/Users/a77/harness-reference` 的 `sources/mashu/` 原文，读取时 HEAD 为 `c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d`。该书是对 Claude Code 恢复源码的逆向分析，不是 Anthropic 官方规范；Agent Loop 章自述主要依据一个具体版本快照，并只声称后续相邻版本未见结构性变化（`/Users/a77/harness-reference/sources/mashu/part1/ch03.md:615-617`，[canonical](https://github.com/linxiaoqi5111-del/harness-reference/blob/c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d/sources/mashu/part1/ch03.md#L615-L617)）。因此本笔记迁移其**结构模式**，不搬运其中的环境量纲、阈值或次数。
- **当前项目**：仅静态读取 `/Users/a77/finance-workspace-private` 的四个相关源码文件；这些文件相对 HEAD `5f236d7863291c2d3830ca0bb0e9354b973c3ba3` 无未提交修改。本轮没有运行真实 SPT 请求或做故障注入。

## 八条关键设计原则

### 1. Loop 是带外部反馈的状态转移系统，不是“反复问模型” — VERIFIED（2026-08-23）

**事实。** Agent Book 把 ReAct 明确写成“思考—行动—观察”的闭环，并指出工具结果缺失会让 Agent 盲跑甚至循环；每次调用所见上下文由静态前缀与持续累积的轨迹组成（`/Users/a77/ai-agent-book/book/chapter1.md:137-147`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter1.md#L137-L147)）。马书进一步把 loop 定义为每轮都会改变消息、模型、压缩与恢复状态的“自修改状态机”，而非无状态 REPL（`/Users/a77/harness-reference/sources/mashu/part1/ch03.md:9-24`，[canonical](https://github.com/linxiaoqi5111-del/harness-reference/blob/c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d/sources/mashu/part1/ch03.md#L9-L24)）。

**[推断]** 一轮输出是否完成，必须由“当前状态 + 新观察 + 转移规则”决定。模型生成了一篇像答案的文本，只证明生成成功，不证明工具、证据、视角或业务目标成功。

### 2. Continue / Stop 必须有类型化原因，跨轮状态要完整重建 — VERIFIED（2026-08-23）

**事实。** Agent Book 将流程状态管理、熔断、回滚、重试与人工接管列为生产 Harness 的核心机制，并把 Loop Engineering 的问题表述为“谁发现下一件事、何时验证、何时才算真正完成”（`/Users/a77/ai-agent-book/book/chapter1.md:257-273`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter1.md#L257-L273)）。马书展示了显式 `State`、`Continue.reason` 与 `Terminal.reason`；每个 continue 点重建完整状态，并把上次转移原因留给测试和调试，而不是散落地修改多个变量（`/Users/a77/harness-reference/sources/mashu/part1/ch03.md:49-98`、`:568-578`，[canonical](https://github.com/linxiaoqi5111-del/harness-reference/blob/c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d/sources/mashu/part1/ch03.md#L49-L98)）。

**[推断]** “是否继续”不应由若干互不相识的布尔值共同暗示。一个 iteration 应产出单一、可枚举的 transition receipt，并携带下一轮需要的完整状态；这既防忘记 reset，也让回放能够回答“为什么又跑了一轮”。

### 3. 行为指导放 Prompt，结构性承诺放代码；不确定时失败关闭 — VERIFIED（2026-08-23）

**事实。** Agent Book 的 Harness 原则要求约束使用故障安全默认值，能力必须显式开放；工具层还要求模型感知的世界与真实操作世界一致，禁止静默改写输入（`/Users/a77/ai-agent-book/book/chapter1.md:279-291`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter1.md#L279-L291)；`/Users/a77/ai-agent-book/book/chapter4.md:88-98`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter4.md#L88-L98)）。马书把边界划得更具体：风格、策略、偏好等行为约束适合 Prompt；权限、预算等结构性约束由代码保证；新工具在并发与只读属性不明时采用保守默认值（`/Users/a77/harness-reference/sources/mashu/part7/ch25.md:50-75`、`:119-166`，[canonical](https://github.com/linxiaoqi5111-del/harness-reference/blob/c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d/sources/mashu/part7/ch25.md#L50-L75)）。

**[推断]** “请按 SPT 视角回答”是行为指导；“本轮是否有资格挂 SPT 标题”是结构性承诺。后者不能靠模型自觉，也不能从用户选择反推，必须由代码验证成功激活后才能开放。

### 4. 恢复要从轻到重、有界、单调；可恢复错误可暂时扣留，但语义降级必须披露 — VERIFIED（2026-08-23）

**事实。** Agent Book 要求在确认无法恢复前不暴露中间失败，同时使用重试、回退与熔断（`/Users/a77/ai-agent-book/book/chapter1.md:257-263`、`:283-291`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter1.md#L257-L263)）。马书展示了三件互相配套的机制：可恢复错误先扣留、恢复耗尽后释放；恢复从信息损失小的动作逐级升级；每类恢复都有尝试守卫，避免 death loop。模型切换时还会清理孤立中间态并通知用户（`/Users/a77/harness-reference/sources/mashu/part1/ch03.md:419-425`、`:468-508`、`:580-605`，[canonical](https://github.com/linxiaoqi5111-del/harness-reference/blob/c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d/sources/mashu/part1/ch03.md#L468-L508)）。

**[推断]** 扣留只适用于“恢复后仍兑现原合同”的故障。如果 SPT 激活失败后系统改交数据中立答案，合同已经发生语义变化；此时即使文字生成成功，也必须显式标记降级，或以 `perspective_unavailable` 终止。恢复过程还必须保留上一轮最佳有效产物，不能用一个更流畅但语义更弱的候选覆盖它。

### 5. Context 要作为代码维护的工作状态管理，而非无限堆聊天历史 — VERIFIED（2026-08-23）

**事实。** Agent Book 要求把时间、工具计数、TODO、错误与系统状态等隐式信息变成框架确定性维护的状态栏，明确反对让 LLM 批量总结这些控制状态；状态读数还要配套行动策略，否则模型看见读数也未必改变行为（`/Users/a77/ai-agent-book/book/chapter2.md:782-875`、`:937-949`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter2.md#L782-L875)）。同书把“装得下但找不到”定义为 context rot，并要求压缩时保存架构决策、约束、验证状态、TODO、回滚点与标识符（`/Users/a77/ai-agent-book/book/chapter2.md:957-1082`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter2.md#L957-L1082)）。马书的压缩管线额外使用互斥守卫、失败计数与熔断，防止压缩本身形成递归故障（`/Users/a77/harness-reference/sources/mashu/part3/ch09.md:151-219`、`:496-522`、`:578-606`，[canonical](https://github.com/linxiaoqi5111-del/harness-reference/blob/c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d/sources/mashu/part3/ch09.md#L151-L219)）。

**[推断]** finance loop 的状态栏应直接携带“剩余预算、必需输出缺口、当前证据层、视角激活凭证、最近转移/失败”及对应动作策略；不能期待模型从长 Prompt 或 warnings 中自己归纳出控制状态。

### 6. Tool 不是一个函数名，而是一份端到端运行契约 — VERIFIED（2026-08-23）

**事实。** Agent Book 要求工具描述说明何时用、不能做什么、参数例子、返回结构和代价，并要求参数传递透明（`/Users/a77/ai-agent-book/book/chapter4.md:72-98`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter4.md#L72-L98)）。马书中的工具契约还包含运行时 schema 校验、持续权限检查、结果大小、并发安全、只读性、启用条件；属性可以依输入而变，结果预算同时限制单工具与聚合输出（`/Users/a77/harness-reference/sources/mashu/part1/ch02.md:13-41`、`:217-244`、`:346-354`，[canonical](https://github.com/linxiaoqi5111-del/harness-reference/blob/c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d/sources/mashu/part1/ch02.md#L13-L41)）。

**[推断]** 同样的契约思想应扩展到“视角能力”：它不只是 prompt 字符串，而应声明可用性、输入、解析结果、证据要求、失败类型、降级政策与 provenance。否则 loop 只能知道“传进去一段文本”，不知道能力是否真的成立。

### 7. Verification 是独立发布门，必须优先读取环境真值，并能审计验证器自身 — VERIFIED（2026-08-23）

**事实。** Agent Book 把评估环境定义为数据集、可变环境状态、工具、Rubric 与终止协议的组合，并要求保留可复现轨迹（`/Users/a77/ai-agent-book/book/chapter6.md:67-104`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter6.md#L67-L104)）。它还要求结果验证优先读取测试、数据库或工具日志等环境真值，过程与质量分别验证；验证器本身也需要校准，不能同一个模型既当裁判又直接改规则（`/Users/a77/ai-agent-book/book/chapter8.md:21-49`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter8.md#L21-L49)）。马书对应的运行原则是先建立状态快照、差分与解释，再决定修复（`/Users/a77/harness-reference/sources/mashu/part7/ch25.md:199-223`，[canonical](https://github.com/linxiaoqi5111-del/harness-reference/blob/c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d/sources/mashu/part7/ch25.md#L199-L223)）。

**[推断]** 对视角模式，verification 的 veto 条件应包含“标题—激活—证据层一致性”。语言质量再高，只要 `requested=SPT`、`activated!=SPT` 却仍显示 SPT 标题，就应判失败；这比一般的“答案有没有引用”更靠前。

### 8. Trace、评估、灰度与回滚共同闭合跨运行学习环 — VERIFIED（2026-08-23）

**事实。** Agent Book 明确要求评估 `Model + Harness` 组合，并用模型替换、组件消融、特性开关和确定性 Prompt 快照定位改进来源（`/Users/a77/ai-agent-book/book/chapter6.md:1-23`、`:634-670`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter6.md#L634-L670)）。在线执行只记录证据，离线循环才做根因诊断、候选修改、独立验证、灰度与回滚；“完成”不等于“进步”（`/Users/a77/ai-agent-book/book/chapter8.md:229-295`，[canonical](https://github.com/bojieli/ai-agent-book/blob/761352efdcf938c8d47c5c134045088a1db7fd84/book/chapter8.md#L229-L295)）。马书则把 trace 层级直接映射为 interaction → LLM/tool，并保留请求、结果、重试和 prompt replay 旁路；行为变更先观测、再内测/灰度，而非一次性全量发布（`/Users/a77/harness-reference/sources/mashu/part7/ch29.md:370-472`、`:809-849`，[canonical](https://github.com/linxiaoqi5111-del/harness-reference/blob/c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d/sources/mashu/part7/ch29.md#L370-L472)；`/Users/a77/harness-reference/sources/mashu/part7/ch25.md:170-223`，[canonical](https://github.com/linxiaoqi5111-del/harness-reference/blob/c5a06ebec7a07cc5c09fd6b197ed3e56a92f564d/sources/mashu/part7/ch25.md#L170-L223)）。

**[推断]** 每个生产失败应先成为可回放 trace，再成为回归 case，最后才可能成为规则或代码补丁。直接把一次失败总结进长期 Prompt，会把偶发故障、错误归因或提示注入固化成系统行为。

## 两书异同

以下是对上述 VERIFIED 事实的 **[推断] 综合**：

| 维度 | 共同点 | Agent Book 更强调 | 马书更强调 |
|---|---|---|---|
| Loop 本体 | 模型提出动作；Harness 保存状态、执行、观察、继续或停止 | ReAct、Workflow/Autonomy 取舍、Loop/Graph 的规范边界 | `State`、Continue/Terminal、整对象重建的具体拓扑 |
| 可靠性 | 约束、验证、纠正必须在模型外形成闭环 | 为什么环境真值、输入隔离与 evaluator 校准重要 | 扣留—释放、轻到重恢复、单次守卫、锁存的落地手法 |
| Context | 动态状态要显式、信息密度要管理 | 状态栏、时间感、context rot、任务内外两个时间尺度 | 压缩互斥、失败计数、熔断和具体生命周期 |
| Tools | 清晰契约、失败关闭、渐进披露 | ACI、参数保真、主动发现的通用原则 | 工具接口字段、输入感知权限/并发/只读、结果预算 |
| Eval / 演进 | trace 必须支持归因，改变要可回滚 | 模型替换、消融、留出集、在线/离线双循环 | 生产遥测、span 层级、prompt replay、灰度与 latch |

一句话概括：**Agent Book 偏“设计法则 + 评价科学”，马书偏“生产状态机 + 故障操作学”。** 前者更适合判定“架构是否少了一层”，后者更适合把那一层落实成字段、转移、守卫和 trace。

## 对 finance-workspace-private 当前 loop 的静态核对

### 已有的正确基础 — VERIFIED（2026-08-23）

- episode 已有明确的 continuation state，携带 task、context、registry、messages、ledger 与 evidence ledger（`/Users/a77/finance-workspace-private/intelligence/runtime/agent_episode.py:448-457`，[canonical](https://github.com/linxiaoqi5111-del/finance-workspace-private/blob/5f236d7863291c2d3830ca0bb0e9354b973c3ba3/intelligence/runtime/agent_episode.py#L448-L457)）。
- 主循环已有外部取消、工具/模型轮次预算、deadline 与可解释的 finalization/stop reason，不是一个无界 ReAct（`/Users/a77/finance-workspace-private/intelligence/runtime/agent_episode.py:558-620`，[canonical](https://github.com/linxiaoqi5111-del/finance-workspace-private/blob/5f236d7863291c2d3830ca0bb0e9354b973c3ba3/intelligence/runtime/agent_episode.py#L558-L620)）。
- repair loop 已实行“修复不得倒退”：候选草稿为空时保留上一轮有效草稿与 bindings，同时保留候选失败的 status / stop reason / gaps（`/Users/a77/finance-workspace-private/intelligence/runtime/continuous_turn_adapter.py:920-950`，[canonical](https://github.com/linxiaoqi5111-del/finance-workspace-private/blob/5f236d7863291c2d3830ca0bb0e9354b973c3ba3/intelligence/runtime/continuous_turn_adapter.py#L920-L950)）。

因此，改进重点应是**加深现有 loop 的状态契约**，不是另建一套并行 orchestrator。

### 视角激活目前缺少同一份 receipt — VERIFIED 事实 + [推断] 风险

**VERIFIED（2026-08-23）事实。** `active_runtime_prompt()` 在选中视角的 prompt 构建发生 `ValueError` / `FileNotFoundError` 时返回与 neutral 相同的空串（`/Users/a77/finance-workspace-private/intelligence/services/perspective_lab.py:611-636`，[canonical](https://github.com/linxiaoqi5111-del/finance-workspace-private/blob/5f236d7863291c2d3830ca0bb0e9354b973c3ba3/intelligence/services/perspective_lab.py#L611-L636)）。continuous 主路径只收到这个 `perspective_context` 字符串（`/Users/a77/finance-workspace-private/intelligence/runtime/conversation_orchestrator.py:1851-1867`，[canonical](https://github.com/linxiaoqi5111-del/finance-workspace-private/blob/5f236d7863291c2d3830ca0bb0e9354b973c3ba3/intelligence/runtime/conversation_orchestrator.py#L1851-L1867)）。回答标题则在后面独立地根据请求模式和选中 ID 生成；视角 fallback notice 的触发条件是 `result.synthesis is None`，不是“视角 prompt 是否成功激活”（`/Users/a77/finance-workspace-private/intelligence/runtime/conversation_orchestrator.py:2768-2792`、`:2851-2874`，[canonical](https://github.com/linxiaoqi5111-del/finance-workspace-private/blob/5f236d7863291c2d3830ca0bb0e9354b973c3ba3/intelligence/runtime/conversation_orchestrator.py#L2768-L2792)）。

**[推断] 风险。** 请求态、激活态、标题态与 fallback 态由不同信号计算，代码中没有一个 invariant 强制“标题只来自成功激活”。这就是静默语义降级的结构性入口。它不等于本轮已经动态复现“删 profile 后仍显示 SPT 标题”：当前 `runtime_answer_header()` 会再次加载 profile，某些缺失场景可能在后段直接抛错；本轮也未运行 live 故障注入。可靠结论是：**当前状态模型无法直接证明某份挂着视角标题的答案确实消费了该视角 prompt。**

## 最值得落到当前 loop 的五条改进

### 1. 增加 `PerspectiveActivation`，标题只消费 activation receipt

**[推断] 建议。** 在进入 episode 前构造一次不可变对象，至少包含：

```text
requested_mode / requested_ids
resolved_ids / display_names
status = neutral | active | unavailable | failed | degraded
prompt / prompt_hash
evidence_contract
reason
```

`active` 才允许生成对应视角标题；`neutral` 使用中立标题；其余状态只能显式降级或终止。header、prompt、trace、fallback notice 与最终 verifier 全部读取同一对象，删除现在“分别重算”的路径。

### 2. 把 iteration 结果统一成一个 `TransitionReceipt`

**[推断] 建议。** 在现有 episode/repair state 上增加统一枚举，例如 `next_tool`、`repair_gap`、`finalize_budget`、`perspective_unavailable`、`verified_complete`、`cancelled`，并携带 perspective activation、best-known draft/bindings、evidence gaps、预算与尝试计数。这样当前已有的 stop reasons 不再只在各子层局部可见，trace 与测试也能断言走过哪条边。

### 3. 把“修复不得倒退”扩展到语义合同，而不只 draft

**[推断] 建议。** 当前 adapter 已保住上一轮 draft，这是很好的棘轮。下一步应给 `perspective_activation`、证据层、来源身份与已验证 claim 同样的单调性：候选可以新增证据或明确降级，但不能保留漂亮文本的同时悄悄丢失视角/证据保证。若恢复后合同变弱，必须改变 status 并产生用户可见 disclosure。

### 4. 注入代码维护的 control/status block，并给读数配动作规则

**[推断] 建议。** 每轮末尾注入短而确定的状态：剩余时间/调用预算、未覆盖 required outputs、当前激活视角及其 prompt hash、最后 transition、最近 failure、best-known artifact。旁边写明动作规则，例如“activation != active 时不得生成该视角标题”“证据缺口未关闭时只能 partial”。不要让 LLM 从 trace 或 warnings 自己总结控制状态。

### 5. 建一组语义 provenance 故障注入回归，并用 feature flag 灰度

**[推断] 建议。** 最小矩阵应覆盖：profile 不可用、prompt 构建异常、视角上下文为空而通用 synthesis 可用、工具在部分证据后超时、repair provider 超时、上下文过长。每例断言：

1. transition / terminal reason 正确；
2. activation、header、fallback notice 一致；
3. 不丢失上一轮有效 draft，但失败状态仍留痕；
4. trace 能重建请求态 → 激活态 → synthesis → verifier → 发布态；
5. semantic provenance veto 能拦截“视角未激活却挂视角标题”。

先以 feature flag 或内部流量运行，同时做组件消融：固定模型，分别开关 activation receipt / verifier；再固定 Harness 比较模型。这样才能区分“SPT 画像能力不够”与“Harness 没把 SPT 接上”。

## 不确定性与边界

1. 马书是版本化逆向分析；本笔记只采用跨版本更稳健的结构模式，不把书中的组件数量、阈值、重试次数或生产统计迁移成 finance 项目参数。
2. 本轮只做静态代码核对，没有执行 SPT live case、trace 回放或故障注入。因此“缺 activation invariant”是静态可证结论；某个具体异常是否在当前运行时表现为静默降级、后段报错或其他 fallback，仍需测试确认。
3. Agent Book 若干段落会引用论文或外部产品案例；本笔记只把作者在书中明确提出的设计原则视为 Agent Book 原文主张，没有把其转述的外部实验数字纳入结论。
4. 当前项目已具备 episode 状态、预算、repair 与 verifier 的大量基础，最小改动路线是新增结构化 activation/transition receipt 与 invariant，不足以支持“需要重写整个 loop”的结论。

## 待提炼

- 将跨项目可复用部分提炼为“语义能力激活凭证（Capability Activation Receipt）”模式：请求态、解析态、激活态、披露态、发布态必须由同一 receipt 串联。
- 将 finance 专属部分转成一份实现 brief：字段、transition 枚举、故障注入用例、灰度指标与回滚条件。
