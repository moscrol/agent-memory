---
title: 知识收录与提炼（资料 → 知识 → 项目）
type: playbook
agent: any
source: 知识外脑基座 v0.1 设计（2026-09-13）
date: 2026-09-13
tags: [playbook, workflow, capture, knowledge, core]
status: draft
related: ["[[ingest.md]]", "[[maintenance.md]]", "[[frontmatter-spec]]"]
---

# 知识收录与提炼

目标不是"存进去"，而是让循环转起来：

```
收集资料 → 整理成知识 → 用知识解决问题 → 把方案与经验再沉淀回来
```

## 三层区分（这是全部规则的地基）

| 层 | 回答什么 | 目录 | 例子 |
|---|---|---|---|
| 资料 `material` | **别人说了什么** | `05_materials/` | 一篇讲订阅制的文章、一份公司案例 |
| 知识 `knowledge` | **我以后能再次使用什么** | `10_knowledge/` | "比较订阅、按次收费与定制服务时，应检查哪些条件" |
| 项目 `project` | **我现在准备怎么做** | `20_projects/` + 各产品仓库 | "Foresight 的三种收费模式比较" |

一条关于定价的认识，可以**同时**关联商业模式、产品与营销。
**不要建"创业知识/营销知识"两套互不相通的目录**——用 `tags` 记多个主题，用双链连接相关笔记，不复制三份。

## 归档判断规则

| 内容性质 | 去哪 | 处理 |
|---|---|---|
| 未提炼的外部输入 | `05_materials/` | 保留原文与来源，`stance: author-view` |
| 跨项目可复用的认识或方法 | `10_knowledge/` | 写清适用条件与失效条件 |
| 针对某个项目的讨论与想法 | `20_projects/<产品>.md` | 未采纳的想法标为"建议/草稿" |
| 项目正式维护的方案或产物 | 该项目约定的权威位置 | 例：`foresight/gtm/` |
| 可反复执行的流程、脚本、模板 | 对应工作流仓库 | 例：`content-ops` 的内容生产流程 |

## 一份输入可以产出三层东西（有来源关系，不是复制）

放进一篇"某公司靠用户社群获客"的文章，可以产出三份**不同**产物：

1. **原始资料**（`05_materials/`）：这个案例讲了什么 —— 保留原文与出处。
2. **通用知识**（`10_knowledge/`）：从中能提炼什么方法，适用条件是什么 —— 记 `source` 指向资料。
3. **项目方案**（产品仓库 `gtm/`）：对我的产品具体怎么做 —— 记引用的知识笔记。

资料上用 `refined_into` 登记它被提炼成了哪几篇知识，形成可回溯的来源链。

> **但不要强制每篇文章都提炼一堆卡片。** 没有值得复用的增量，保存资料 + 简短摘要就够了。

## 自动沉淀：默认轻量，不逐次找你审批

可以让助手自动完成：收集、打标签、建立关联、生成方法草稿、归档到确定的位置。

四条纪律：

1. **分类不确定 → 留在 `00_inbox/`**，不强行归档。留着比归错好。
2. **发现重复 → 先建关联**，不擅自合并或删除已有笔记。
3. **自动归档 ≠ 自动认定为真。** 每条资料/知识保留来源，并用 `stance` 区分：
   `author-view`（作者观点）/ `ai-distilled`（AI 提炼）/ `hypothesis`（待验证假设）/ `evidenced`（有实际证据的经验）。
4. **每次完成只给一条简短回执**，例如：

   > 已保存原始资料；新增一条商业模式知识草稿，关联两条已有笔记。对 Foresight 的适用性仍是推测，没有修改产品方案。

## 用起来的两条硬规则

1. **先检索已有积累，再给建议。** 明确区分"哪些来自你的资料"和"哪些是新的推断"。
   **库里没有依据时就说没有**，不能假装你以前已经形成过这个结论。
2. **沉淀要有选择。** 讨论结束后保存有价值的结论、方案和未决问题，
   不要把聊天逐字倒进知识库。**未被采纳的建议保存为建议或草稿，不直接变成"我的经营原则"。**

## 执行入口

```bash
# 1) 收集（也支持 Obsidian Web Clipper 直接落 00_inbox）
scripts/capture.sh "订阅制的三种定价结构" --url https://example.com/post --tags pricing,saas

# 2) 整理：查重 + 归档建议（机械部分）
python3 scripts/refine_material.py --scan

# 3) 升格（机械部分；提炼内容由助手读写）
python3 scripts/refine_material.py --promote 00_inbox/xxx.md --to material
python3 scripts/refine_material.py --promote 00_inbox/xxx.md --to knowledge

# 4) 登记来源链
python3 scripts/refine_material.py --link 05_materials/xxx.md 10_knowledge/yyy.md

# 5) 收口检查（含 frontmatter / type↔目录 / 死链 / inbox 老化）
python3 scripts/vault_lint.py
```

**失败处理：** 升格失败时脚本不改动、不删除原文件，条目留在 `00_inbox/` 保持待处理状态。

## 红线

- 不把资料原文当知识结论引用；不同 `stance` 不得混用。
- 不擅自合并或删除用户已有笔记。
- 不往 vault 里写密钥 / token。
- 大附件放 `90_attachments/`，不要把二进制大文件提交进 git。
