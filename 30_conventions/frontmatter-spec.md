---
title: Frontmatter 规范
type: convention
agent: devin
source: 设计约定
date: 2026-06-28
tags: [convention, spec, core]
---

# Frontmatter 规范

每个笔记**必须**以 YAML frontmatter 开头。这是不同 Agent 能互相消费内容的前提。

## 通用字段（所有笔记都要有）

| 字段 | 必填 | 说明 | 示例 |
|---|---|---|---|
| `title` | ✅ | 人类可读标题 | `finhot 数据回填流程` |
| `type` | ✅ | 笔记类型，见下表 | `knowledge` |
| `agent` | ✅ | 创建/最后更新者（按**工具**记：Cursor 里跑的不论底座模型都记 `cursor`，Claude Code 记 `claude`）；面向所有/任意 agent 的约定或 playbook 可用 `all` / `any` | `devin` / `codex` / `cursor` / `grok` / `claude` / `human` / `all` / `any` |
| `source` | ✅ | 信息来源（URL / 工具 / 对话 / 推断） | `https://...` / `grok-search` |
| `date` | ✅ | 创建或更新日期 (YYYY-MM-DD) | `2026-06-28` |
| `tags` | ✅ | 标签数组，便于检索 | `[finhot, data, pipeline]` |
| `status` | ⬜ | `draft` / `verified` / `deprecated` | `verified` |
| `related` | ⬜ | 双链到相关笔记 | `["[[finhot-overview]]"]` |
| `reviewed_by` | ⬜ | 人审者；`70_tutor` 落库时必须为 `human` | `human` |
| `reviewed_at` | ⬜ | 人审日期；`70_tutor` 落库时必填 | `2026-07-10` |

## `type` 取值

| type | 放在哪 | 含义 |
|---|---|---|
| `inbox` | `00_inbox/` | 原始产出，未整理（短期，>14 天未提炼会被 lint WARN） |
| `material` | `05_materials/` | **外部输入资料**（文章、案例、摘录）：别人说了什么。长期留存 |
| `knowledge` | `10_knowledge/` | 已提炼的事实/结论：我以后能再用什么 |
| `project` | `20_projects/` | 项目 MOC / 任务状态：我现在准备怎么做 |
| `convention` | `30_conventions/` | 跨 Agent 约定 |
| `playbook` | `40_playbooks/` | 可复用工作流 |
| `agent-card` | `50_agents/` | Agent 接入约定卡 |
| `dialogue` | `60_dialogues/` | 用户与外部 AI 的原始对话记录（蒸馏语料） |
| `tutor-note` | `70_tutor/` | 经用户检阅批准的科普 / 原理学习资产 |

### `material` 专属字段（可选，建议填）

| 字段 | 说明 |
|---|---|
| `source_url` | 原文链接；无链接则写来源工具 |
| `author` | 原作者 / 机构（**不要与 `agent` 混淆**：`agent` 是写入者，`author` 是内容作者） |
| `stance` | 见下方「认识论标记」一节 |
| `refined_into` | 已提炼成的知识笔记双链，如 `["[[compare-subscription-pricing]]"]`；未提炼则留空 |

> **自动归档不等于自动认定为真。** `material` 是"别人说的"，默认 `stance: author-view`；
> `ai-distilled` 与 `hypothesis` 都必须能被下游区分出来，不得当作已验证结论引用。

## `stance`——认识论标记（`material` 与 `knowledge` 共用）

| 值 | 含义 |
|---|---|
| `principle` | **通用原理**，非某人独有主张，广泛成立 |
| `author-view` | 某人的主张（如巴菲特/芒格原话），未经独立验证 |
| `ai-distilled` | AI 提炼，源为作者观点——**原则是别人的，判定方法是提炼的** |
| `hypothesis` | 待验证假设，含 n=1 归纳 |
| `evidenced` | 有实测证据的经验 |

**`10_knowledge/` 中 `date` 不早于 2026-09-14 的笔记必填**（`vault_lint.py` 检查项 6b，
存量 74 篇按棘轮不动）。

> **为什么判据层也要它。** 此前 `stance` 只是 `material` 专属，于是"这是通用原理还是
> 待验证假设"在 `10_knowledge` 没有字段可放，只能写进正文——实测 8 篇各自即兴写成
> `> **性质：xxx**`，词表混着 `hypothesis` / `通用原理` / `[推断]` / `ai-distilled` 四套。
> **散文里的标记不能筛、不能查、不能被下游区分**，而 `recall.sh` 的引用纪律恰恰要求
> 「谁说的 + 适用条件 + 当前符不符合」。
>
> 这修的是一处倒挂：资料层（别人说了什么）本来就有 `stance` 与
> `_templates/material.md` 的「适用条件 / 失效条件」，**而真正拿去给建议的判据层两样都没有**。

## 校验要点

- 日期统一 `YYYY-MM-DD`。
- **`type` 只能取上表里的值**，`vault_lint.py` 对表外的值直接 ERROR（2026-08-05 起）。
  在此之前查表落空是静默放行的，`type: reading-queue` 就是这么混进 `10_knowledge/` 的。
- `agent` 用小写固定值，方便聚合"谁写了什么"。**表外的值 `vault_lint.py` 直接 ERROR**（2026-08-12 起，与 `type` 同一条 fail-closed 纪律——此前只查有没有、不查是什么）。`cursor` 2026-09-03 入表：此前两篇 Cursor 会话写的笔记只能在「写 `cursor` 被 lint 拦」和「写 `claude` 撒谎」之间选，表要跟着真实写入者走，lint 才有资格 fail-closed。
- `verified` 状态表示有人/某 Agent 核实过，可被下游放心引用；`draft` 表示待核实。
- `70_tutor/` 必须先按 `tutor` skill（手动触发：`@tutor` 或 `@session-tutor`；自然语言“session tutor”也可）帮助用户理解，再给候选摘要；只有用户明确批准后才能写文件。
- 用户批准表示内容可以落库，不自动等于事实已核验；仍有待核点时保留 `status: draft`。
- 引用其他笔记用 Obsidian 双链 `[[文件名]]`，不要用裸文件路径。
