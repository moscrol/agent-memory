---
title: 知识外脑基座 v0.2 —— 设计与落地计划（交执行 agent）
type: playbook
agent: claude
source: 2026-09-13 与用户的基座设计讨论 + 本 vault 现状实测
date: 2026-09-13
tags: [playbook, knowledge-brain, design, handoff, execution-plan]
status: draft
related: ["[[knowledge-capture.md]]", "[[frontmatter-spec]]", "[[maintenance]]", "[[foresight]]"]
---

# 知识外脑基座 v0.2 —— 设计与落地计划

**给谁读：** 接手执行的下一个 agent。
**目标：** 把"个人知识外脑"从 v0.1（已跑通收集→资料→知识→来源链）推进到 v0.2（可日常用、内容构成正确）。
**本文件自包含**：不看历史对话也能执行。

---

## 0 执行前必读（三个陷阱，踩了就白干）

1. **本 vault 是多方并发写入的。** 存在自动提交进程 `kowishiki auto-sync`（约 15–45 分钟一次，message 为 `auto-sync: local edits`），另有自动身份 `linxiaoqi5111-del` 提交 `chore(memory)`。
   → **动手前先 `git log --oneline -5` 看有没有新提交**；改动完成后补一次语义化提交，别让 auto-sync 把你的工作吞成一条匿名提交。
2. **lint 基线不干净。** 2026-09-13 基线 = **7 error / 12 warn**（`50_agents/TOOLKIT.md` 镜像漂移、4 篇知识笔记缺 frontmatter/agent、2 处死链）。
   → 判断自己有没有改坏，**必须对比基线**，不能看绝对条数；也不要把这 7 条当成自己的任务（见 §6 不做清单）。
3. **所有笔记必须带合规 frontmatter**，`type` 与目录必须一致，否则 `vault_lint.py` 直接 ERROR。
   取值表见 `30_conventions/frontmatter-spec.md`；门禁 `python3 scripts/vault_lint.py`。

---

## 1 现状诊断（实测数据，不是印象）

### v0.1 已经落地的东西

| 件 | 位置 | 状态 |
|---|---|---|
| 随手收集入口 | `scripts/capture.sh` | 可用（落 `00_inbox`，同日同 slug 幂等追加） |
| 整理与归档（机械半自动） | `scripts/refine_material.py` | 可用（`--scan` 查重+建议、`--promote` 升格、`--link` 来源链） |
| 收录与提炼规则 | `40_playbooks/knowledge-capture.md` | 已写，`status: draft` 待人审 |
| 外部资料层 | `05_materials/`（+ `material` 类型已入 spec 与 lint） | 已建，1 篇 |
| 附件目录 | `90_attachments/` | 已建，空 |
| 首页 | `首页.md`（3 个 Bases 视图） | 已建，**Bases 渲染未经肉眼验证** |
| 项目入口 | `20_projects/foresight.md` | 已建（只做指针，不复制产品事实） |
| 统一入口说明 | `/Users/a77/venture-ops/README.md` | 已建（薄层，只放指针） |

### 核心问题：内容构成错了

`10_knowledge/` 现有 **56 篇**：

| 构成 | 数量 | 说明 |
|---|---|---|
| agent 工程 / 脚手架经验 | **37** | `gate-*`、`seam-*`、`eval-*`、`agent-*` 等 |
| 投研 / Foresight 项目专属 | **18** | `finance-*`(13)、`knevo-*`(4)、`short-video-*`(1) |
| 商业 · 营销 · 产品类通用知识 | **1** | 仅 2026-09-13 新建的定价判据 |

另：`00_inbox/` 14 条（其中 10 条超 14 天未整理）、`20_projects/` 12 个页面。

**结论：这个 vault 目前是「工程记忆」，不是「通用知识外脑」。** 用户要的是后者——一个能收商业模式/营销/产品知识、并用来做创业判断的外脑。

### 但不要据此大搬家

55 篇"项目内容"里，**有相当一部分其实是可跨项目复用的工程判断**（例如 `gate-covers-only-its-return-value`、`kill-on-timeout-is-an-amplifier`、`judgment-distillation-six-rules`）——它们不该被当成"项目垃圾"清走。
真正需要区分的是**「不看具体项目也成立的判断」**与**「只对某个项目成立的细节」**。因此 v0.2 采用**打标而不搬家**的策略。

---

## 2 v0.2 目标

1. **内容构成纠偏**：让"通用知识"在知识层里可被单独看见，且新进来的内容自动落到正确的一侧。
2. **日常可用**：用户说出"收一下 / 这是什么模式 / 帮这个产品做方案 / 这个方法以后还能用"四类话时，流程都能走通并产出可追溯的结果。
3. **不增加复杂度**：不引入向量库、不引入新平台、不新建知识库。

---

## 3 设计：v0.2 新增的两件事

### 设计 A · 给知识层加 `scope` 属性（打标，不搬家）

在 `10_knowledge/` 的 frontmatter 增加可选字段：

| 值 | 含义 | 例子 |
|---|---|---|
| `general` | 不看具体项目也成立的判断 / 方法 | 定价结构选择判据、断言粒度、判断沉淀规则 |
| `project` | 只对某个项目成立的细节 | 某产品的架构决策、某个 API 的坑、某次实验结论 |

配套：
- `30_conventions/frontmatter-spec.md` 增补字段说明（**不设为必填**，避免历史笔记全线报错）。
- `首页.md` 增一个 Bases 视图「通用知识与方法」：只筛 `scope: general`。**这才是"外脑"该看的视图。**
- `refine_material.py --scan` 的归档建议里提示该字段；`--promote --to knowledge` 时若缺 `scope` 则写 `general` 并提示复核。

**存量打标**：写一个一次性脚本 `scripts/backfill_scope.py`，按前缀初判（`finance-*`/`knevo-*`/`short-video-*` → `project`；其余 → `general`），**输出待复核清单，由人确认后才写盘**。要求：幂等、可回滚、不移动任何文件。

### 设计 B · 区分"项目内容"与"通用知识"的写入规则

写进 `knowledge-capture.md` 的归档判断表（v0.2 修订）：

| 内容性质 | 去哪 |
|---|---|
| 只看这个项目才成立的细节（架构决策、某接口的坑、某次实验结果） | **项目页或产品仓库**，不进 `10_knowledge/` |
| 不看具体项目也成立的判断 / 方法 | `10_knowledge/`，`scope: general` |
| 外部输入原文 | `05_materials/` |

**要点：`10_knowledge/` 不是"所有结论的家"，而是"可复用判断的家"。**

---

## 4 任务清单（按顺序做，每项含验收）

> 顺序有依赖：T1 是地基，T2 依赖 T1。

### T1 · 补齐属性与视图

1. 在 `30_conventions/frontmatter-spec.md` 增补 `scope` 字段说明（可选字段）。
2. 在 `首页.md` 增加 Bases 视图「通用知识与方法」（筛 `file.inFolder("10_knowledge")` 且 `scope == "general"`）。
   > ⚠ **筛选语法需先核对**：本文给出的写法是示意，**撰写者未能在当前环境验证 Bases 的实际语法**（本机 Obsidian 1.12.7、`bases` 插件已启用，但无法运行 Obsidian 做渲染测试）。执行前请对照官方 Bases 语法文档或先做一个最小视图验证，**不要照抄本文的表达式**。
3. 新建 `10_knowledge/` 知识模板补充说明，或在 `_templates/knowledge-note.md` 中加入 `scope:` 占位。

**验收：** `python3 scripts/vault_lint.py` 仍为基线（7E/12W）；`_templates/knowledge-note.md` 含 `scope`；首页新增视图存在。
**注意：** `scope` **不设为必填**——设为必填会让 56 篇存量全部报错。

### T2 · 存量打标（只打标，不搬文件）

1. 写 `scripts/backfill_scope.py`：扫描 `10_knowledge/*.md`，按规则初判，**默认 dry-run 输出清单**，加 `--apply` 才写盘。
2. 先跑 dry-run，把清单交给用户复核；确认后再 `--apply`。
3. 幂等：已含 `scope` 的文件跳过；提供 `--revert`（把 `scope:` 行删掉）。

**验收：** dry-run 输出 56 条分类建议；`--apply` 后 `vault_lint.py` 仍为基线；随机抽 5 篇确认 frontmatter 未被破坏（`title`/`type`/`agent`/`source`/`date`/`tags` 均在）。
**高风险提示：** 这是**批量改 56 个文件**的操作。必须先 dry-run + 人工确认；改前 `git status` 确认工作区干净，改后立刻提交，便于回滚。

### T3 · 修订收录规则文档

把 §3 设计 B 的判断表并进 `40_playbooks/knowledge-capture.md`，并把 `status` 保持 `draft` 等待人审（不要自行改成 `verified`）。

**验收：** 规则表含"项目细节不进知识层"一行；文件仍为 `type: playbook`。

### T4 · 端到端复跑一次（用真实内容，不要造假）

用 `00_inbox/` 里**已有的真实条目**跑一遍完整链路（推荐用 codex 写的 `2026-09-13-time-river-commercial-research.md` 或 `2026-09-13-time-river-epistemic-review.md`）：

```
refine_material.py --scan  →  --promote … --to material  →  （提炼）→  --promote … --to knowledge  →  --link  →  vault_lint
```

**验收：**
- 资料层多出条目，知识层多出对应笔记，`refined_into` 正确登记（格式 `["[[note-name]]"]`，**不是** `[[[note]]]`）。
- 提炼出的知识笔记 `scope: general` 或 `project` 判断正确，且**区分了 stance**。
- 没有真实用户反馈时，**不得**写入任何虚构的结果数据。
- `vault_lint.py` 维持基线。

### T5 · 提交与交接

补一次语义化提交（别留给 auto-sync），并在 `20_projects/agent-memory.md` 的交接记录补一行。

---

## 5 未决问题（需要人决定，不要自行拍板）

1. **`scope` 是否要成为必填？** 建议先不设必填，用观察一段时间后再收口。**这是产品决策，不是技术决策。**
2. **18 篇投研专属笔记长期怎么处理？** 三个选项：留在知识层打 `project` 标 / 逐步迁到 `20_projects/foresight.md` 或产品仓库 / 保持现状。**建议先打标观察，不急着迁。**
3. **Bases 渲染是否正常？** 需要在 Obsidian 里肉眼确认一次（执行 agent 无法在此环境验证；`obsidian` CLI 要求 Obsidian 正在运行）。
4. **Web Clipper 模板**是否要固化到 `_templates/`？需要有人在 Obsidian UI 里配一次并回填。
5. **`40_playbooks/knowledge-capture.md` 是否升级为 `verified`？** 需要人审。

---

## 6 明确不做（边界）

- **不动那 7 条存量 lint error**（`TOOLKIT.md` 镜像漂移、缺 frontmatter 的 4 篇、2 处死链）——它们是历史欠账，混进来会把这次改动的影响面搅浑。要修另开一轮。
- **不搬文件、不改目录结构。** v0.2 只打标。大规模移动会牵动 Obsidian 内部链接与 git 历史。
- **不引入向量检索 / 不改检索方案。** 等真的出现"找不到已存知识"再判断。
- **不新建知识库、不新建平台、不加常驻服务。**
- **不自动发布、不对外发送、不改个人画像。**
- **不为跑通流程而编造内容**：没有真实反馈就不写结果，缺失信息就写"暂无"。

---

## 7 给执行 agent 的一句话

**这一轮要证明的不是"又加了一个功能"，而是：一条外部资料进来，能被正确地分成"资料 / 通用知识 / 项目细节"三层，且其中通用知识能在下次做创业判断时被找出来引用。**
做不到这一点，加多少视图都是装饰。
