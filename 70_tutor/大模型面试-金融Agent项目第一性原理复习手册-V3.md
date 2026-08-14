---
title: 大模型面试：金融 Agent 项目第一性原理复习手册（V3）
type: tutor-note
agent: devin
source: "Devin Session deebe5e092fe49579a9983ee14ca02d3；三个项目仓库与《大模型面试题与答案.pdf》"
date: 2026-07-14
tags: [llm, interview, finance-agent, rag, agent, handbook]
status: draft
related: ["[[金融Agent面试-循序渐进教学计划]]", "[[金融Agent面试学习]]"]
reviewed_by: human
reviewed_at: 2026-07-14
---

# 大模型面试：结合你的金融 Agent 项目的第一性原理复习手册（V3：金融 Agent 实现详解版）

> 资料来源：已只读分析 `linxiaoqi5111-del/agent-memory`、`finance-workspace-private`、`knowledge-base-private`，并审计附件《大模型面试题与答案.pdf》。
> 目标：不要背 PDF，而是用“第一性原理 → 标准答案 → 你的项目怎么讲 → 不能夸大的边界”准备大厂面试。
> V2 新增：Transformer、训练对齐、PEFT、显存与分布式、推理与量化、Serving 详解，以及口头自测与白板题。
> V3 新增：金融 Agent 从业务问题、技术选型、架构设计到真实代码落地的完整链路；逐项说明输入输出、数据流、失败降级、评测、当前边界，以及 30 秒 / 2 分钟面试表达。

---

## 分册目录（本页为索引，正文在各分册）

原文件正文 9,046 行 / 247,868 字节，超出 vault 单文件 80KB 棘轮阈值；2026-08-14 按章节边界无损拆为 6 册。本页保留原 frontmatter 与导言并充当索引，各分册正文逐行未改写。原始提交见 [PR #21](https://github.com/linxiaoqi5111-del/agent-memory/pull/21)。

| 册 | 章节 | 分册 | 内容概要 |
|---|---|---|---|
| 1 | 0–2 | [[大模型面试-金融Agent项目第一性原理复习手册-V3-ch00-02-面试总故事与P0高频题]] | 面试总故事、PDF 审计结论、P0 高频题标准答案 |
| 2 | 3–4 | [[大模型面试-金融Agent项目第一性原理复习手册-V3-ch03-04-Transformer与训练对齐PEFT]] | P1 详解一/二：Transformer 与模型结构；训练、对齐与 PEFT |
| 3 | 5–13 | [[大模型面试-金融Agent项目第一性原理复习手册-V3-ch05-13-显存推理与面试表达]] | P1 详解三/四：显存/分布式/长上下文、推理/KV Cache/量化/Serving，及速查表、STAR 模板、诚实边界、自我介绍、学习顺序、口径校对、V3 阅读方式 |
| 4 | 14–19 | [[大模型面试-金融Agent项目第一性原理复习手册-V3-ch14-19-金融Agent实现详解上]] | 端到端实现总览、Question Router、Answer Orchestrator、多源证据模型、Knowledge Base RAG、Closed-loop Retrieval |
| 5 | 20–27 | [[大模型面试-金融Agent项目第一性原理复习手册-V3-ch20-27-金融Agent实现详解下]] | DuckDB 结构化数据、Output Review、Agent Memory、PIT 防前视、可观测性与回放、L3 证据与 Research Judge/Queue、风险门控、评测与学习闭环 |
| 6 | 28–35 | [[大模型面试-金融Agent项目第一性原理复习手册-V3-ch28-35-全链路案例与面试收尾]] | 一道真实问题的全链路拆解、选型 trade-off、面试官高频追问、实现证据速查、实现边界声明、讲解四种长度、模拟面试清单与 V3 总结 |

> 无损校对：6 册正文行数合计 9024 行 + 本页保留的原文件头 22 行 = 原文件 9,046 行；每册开头另加 13 行 frontmatter/导航（上表行数已注明）。
