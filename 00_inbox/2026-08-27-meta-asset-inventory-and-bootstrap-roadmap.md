---
title: 元资产盘点与自举复刻路线图（宏观理解四层地图 + meta-skill 复用性裁决）
type: inbox
agent: claude
source: "用户提问（宏观理解是否足够 / meta-skill 能否复用 / 自举复刻 agent 落地）+ 对 harness-reference gitea/main、agent-memory、finance-workspace-private、~/.claude/skills 与 ~/.codex/skills symlink 的实测核查"
date: 2026-08-27
tags: [inbox, meta-assets, bootstrap, harness, code-map, reuse, roadmap]
status: draft
refined_into: ["[[three-forms-of-reuse-pointer-port-generate]]"]
---

# 元资产盘点与自举复刻路线图

> 回答三个判题：① 代码行数多时（实测本仓 425K 行 Python / 3133 个跟踪文件）现有 loop 图 + code map 够不够支撑宏观理解；② harness / agent-run / 组件打分器（= 质量消融评测台 `run_quality_ablation.py`，两轮用户纠偏后钉准）/ trace diff 这批 meta-skill 是否可复用；③ 「以金融 agent 为原型自举复刻其他 agent」怎么落地——这项自举能力同时是用户适配 FDE 岗位的职业资产。
> 本文只做裁决 + 指针，不抄 BUILD/KIT 清单（单一真本源纪律）。

## 判题 1：宏观理解——不是「loop 图 + code map」两件，实际已有五层地图 [实测]

| 层 | 回答什么问题 | 载体 | 防漂移机制 |
|---|---|---|---|
| 概念闭环层 | 系统整体为什么是环不是线 | `10_knowledge/agent-system-closed-loop-first-principles.md` | 稳定方法论，少变 |
| 能力节点层 | 有哪些节点、路径、回路 | `10_knowledge/finance-agent-capability-graph.md` | `scripts/graph_audit.py` 三级断言（路径/符号/分支）|
| 接口层 | 门在哪、接口深浅怎么评 | finance 仓 `docs/agent-product-door.md`（门/引擎/组装/积木）| 人工维护 |
| 符号结构层 | 这个实现在哪、依赖谁 | finance 仓 `scripts/code_map.py`（status/query/build/ask，空图 fail-closed）| status 新鲜度 + SessionStart 播报 |
| 骨架形状层 | 谁拥有循环、六层各管什么 | harness-reference `DESIGN-stack.md`（SSOT 在 gitea/main）| git 版本化 |

**裁决：分层架构是对的，缺口只有两个，均为运维性而非结构性。**

1. **code map 新鲜度无自动化**——SessionStart 只播报 stale（本日实测「落后 12 且触及 intelligence/」），重建靠人跑。已补：launchd 夜间刷新（见 Phase A 落点）。
2. **五层地图没有统一入口**——「宏观理解从哪张图进」散在五处。已补：finance 仓 `AGENTS.md` 代码地图节的路由表（只指针，防第二份清单）。

原理（可迁移）：单张「全景大图」在 40 万行规模必然失真——要么细到没人读，要么粗到骗人。正确形状是**按问题形状分层 + 每层自带防漂移机制**（生成的用生成保鲜，手绘的上断言门禁）。这在任何大仓库都成立；面试讲架构治理可以用「地图不是一张，是一摞，每张钉着自己的保鲜方式」这个说法。

## 判题 2：meta-skill 复用性逐个裁决 [实测 2026-08-27]

复用基建已存在：**SSOT 仓 + symlink 扇出**到 `~/.claude/skills/` 与 `~/.codex/skills/` 双端。

| 资产 | 物理位置 | 裁决 |
|---|---|---|
| `harness-bootstrap` / `harness-architecture-review` | symlink → `~/arts-gitea-main/skills/`；判据 SSOT 是 harness-reference 三件套（gitea/main 已全部收口：DESIGN.md 顺序轴 2026-08-20 + DESIGN-stack.md + BUILD.md + TOOLKIT.md）| **可复用**。移植新领域时零件按 BUILD「移植要改什么」逐条换词表 |
| `agent-run-triage` | symlink → `~/projects/agent-run-triage-skill/skills/`，自述 Harness 无关 | **可复用** |
| `agent-run-review` | `~/.claude/skills/agent-run-review/` 本地实体目录，未迁共享仓 | **待迁**（见待办） |
| **组件打分器（质量消融评测台）**[经两轮纠偏钉准 2026-08-27：初判深模块判据 → 误判 FDE 产品化 → 实为本行] | finance 仓 `scripts/run_quality_ablation.py`（默认盒基线臂 vs 每颗组件一个关断臂，关断用**真实生产旋钮** env/flag 不经开关板；真 LLM 答案 + **独立盲评**五维 rubric /20，输出组件边际贡献；judge 解析失败记 unscored 不编造）+ `scripts/rejudge_quality_ablation.py`（判官断链只补 judge 不重跑 ask，聚合 `aggregate_components()` 单一真本源）；方差纪律：gated 子集当噪声底、\|Δ\|≳2.4/20 才算信号（`10_knowledge/eval-harness-variance-governance.md` + 项目 MOC 2026-08-27 条）；live 打在 8796 解耦树 sidecar | **方法论完全可迁移**（消融 = 通用手法，「结构层拧得动吗」与「质量层关了差几分」两份读数分开是 DESIGN P4 的标准落法）；**rig 半特化**：三颗旋钮、rubric 维度、题集是金融仓的，换领域逐项换。已在 main |
| 接口深浅判据（另一台打分，勿混） | 通用形状在 `codebase-design` skill（已共享）；金融仓特化在 `docs/agent-product-door.md`（门/引擎/组装/积木四层，不混着打分）| 形状可复用。与上一行正交：上行量「组件对答案质量的边际贡献」（消融向），本行评「接口设计深不深」（设计向） |
| fde-os 岗位层（31 skill + `distilled/fde-deep-read.md`；本 vault 读书索引 `10_knowledge/fde-guidance-book-reading-index.md`）| 独立仓（2026-08-14 迁出），KIT 第四层「岗位操作系统」| **可复用，天生跨项目**。定位澄清（2026-08-27）：它不是组件打分器；它是用户 FDE 职业目标的操作系统——**整套自举能力（三件套 + meta-skill + 本路线图）就是用户适配 FDE 岗位的作品集资产**，fde-os 的产品化四问与 Phase C 触发条件同构（见下） |
| `divergence-distill`（trace diff）| finance 仓 `.claude/skills/divergence-distill/`，六个沉淀池全绑金融仓（reading_baseline / experience_cards / record-correction CLI / _PENDING_RULES / 视角差分 / 知识库证据层）| **部分复用**：分类判别式（控制面前置、可证伪测试、双用户测试）可带走；池子是领域件，换领域要先建对应池。BUILD.md 已自标「候选模式 n=1，第二实例出现才升格模式」 |

原理（可迁移）：复用有三种形态，成本与漂移风险递增——**① 指针复用**（symlink/子模块指向 SSOT，改一处全端生效，本机已用）→ **② 移植复用**（读源码抄过去 + 换词表，BUILD.md 每条零件写明「移植要改什么」就是为这形态服务）→ **③ 生成复用**（脚手架/模板生成，只有重复次数证明了才值得建，否则维护模板本身成为新负担）。跳过 ② 直接建 ③ 是 premature abstraction 的组织版。

## 判题 3：自举复刻 agent——方向成立，顺序必须尊重已立的纪律

「自举」（bootstrapping）类比：编译器界先用旧工具造出能编译自己的编译器，再脱离旧工具。对应到这里：**用金融 agent 沉淀的三件套（设计/搭建/审计）+ harness-bootstrap 流程，去立第二个领域 agent；第二个立起来的过程反过来验证并磨利三件套本身**——这就是自举回路。

用户定位（2026-08-27 口述）：这项自举能力**本身就是适配 FDE 岗位的职业资产**——FDE 的核心动作恰是「带着可复用组件进新领域、快速立起能交付价值的系统」，与本路线图 Phase B 的移植试点是同一个动作；做完的每次移植都是面试可讲的现场案例。

但 BUILD.md 缺口节已写死两条边界 [实测]：「没有脚手架命令，n=1 先不做」「没有跨项目版本管理」。`harness-bootstrap` D 步专门留了「移植实验空表」（抄了哪些 / 改了哪 / 卡在哪 / 哪步重复到值得自动化），等第一次真实跨领域移植来填。**复刻器不是先造框架，而是先攒第二个实例。**

### 三阶段路线

**Phase A（2026-08-27 本轮，已执行并合入）**
- 本盘点文档落 inbox。
- finance 仓 PR #469 已合 main（`61dd5f79`，用户确认）：AGENTS.md 宏观理解路由表 + `scripts/install_code_map_refresh.py`（launchd 夜间 stale→build）+ registry 存量漂移顺手修。合并等价检查读数见 `docs/handoffs/2026-08-27-code-map-refresh-and-macro-map.md`。

**Phase B：第二领域真实移植（n=1→n=2）——近端试点已执行（2026-08-27 深夜）**

知识库仓 PR #94（`harness/session-facts-and-receipts`）待用户确认合并：装骨架报告 + **移植实验表首行真数据**在 kb 仓 `docs/superpowers/specs/2026-08-27-harness-bootstrap-report.md`。要点：三变量=中高/强/年级；P0/P3/P6 厚、P1 刻意薄、P2 升级全配、P4/P5 以后再做（触发条件已写死）；移植四件（session_facts 全配升级、conftest 收据、check_test_receipt、test-environment.json）；全量 543P/0F ×2、收据链正负双向实测。**移植事故已如实入表**：在错树上误判「脚本缺失」覆盖了 2026-08-12 减配版、误删活的 stale 段，第二提交恢复——教训「跨树断言 X 不存在前先 `git log --all -- <path>`」。「值得自动化」当前=尚无（两处换词表是领域判断），脚手架继续冻结。

流程（供第三领域复用）：`harness-bootstrap` 采访三变量 → P0–P6 厚度 → 按失败形状挑零件 → 真实移植 2–3 个零件 → **填移植实验表** → 回写 KIT。试点候选对比：

| 候选 | 三变量预判 | 试点信息量 | 建议 |
|---|---|---|---|
| knowledge-base-private | 错误代价中（污染检索）、可验证性强（lint/审计已有）、生命周期长 | 中——同栈同用户，已半共享纪律，移植阻力最小 | **近端试点，先做**：低风险填出空表第一行真数据 |
| finhot（TS/Electron） | 错误代价低中、可验证性中、生命周期长 | 高——跨语言栈，能检验「模式 vs 零件」分离度（Python 零件抄不动时，模式还剩多少）| **跨栈试点，第二步** |
| vidio（运营为主） | 错误代价低、可验证性弱、生命周期短 | 低——按三变量各层大概率全薄 | 不推荐当试点 |
| 全新领域 agent | 视领域 | 最高，成本也最高 | 等前两个试点摊薄成本后再议 |

**Phase C（条件触发，不排期）：自举工具化**

触发条件写死：**n≥2 且移植实验空表「哪一步重复到值得自动化」非空**。届时才做：脚手架/复刻器（形态到时候按空表定，可能是生成器、可能只是一个 checklist skill）+ 解决「跨项目版本管理」缺口（同一零件多仓副本的同步通知）。触发条件不满足前动手 = 违反自家 BUILD.md 缺口节的边界。

这条触发纪律与 fde-os 的产品化四问**同构**（三客户撞同一缺口才配进平台 ↔ 零件被 ≥2 个领域真实要过才配抽包）；到 Phase C 裁决时可直接套四问表，不必新发明判据。

## 判题 4：新领域 agent 的形态——沉淀成 copilot，还是在通用 agent 里调组件（2026-08-27 用户追问）

**裁决：不是二选一，是先后。copilot 是某些约束出现后的结果，不是起点。** 金融 agent 自己的成长史就是模板：先在 Claude Code 里以「仓库 + 契约 + skills + 门禁」形态跑了很久，Workbench/Episode runtime（copilot 形态）是后来被真实约束逼出来的。

两种形态的本质差别是 **DESIGN-stack 第一问「谁拥有循环」**（≈ library vs framework 的控制反转）：

| | 通用 agent 里调组件 | 自建 copilot（runtime 拥有循环） |
|---|---|---|
| 循环归谁 | Claude/Codex/Cursor 的 harness | 自己的 runtime（如 episode loop） |
| 约束怎么落 | 提示词 + exit-code 门禁（pre-commit/CI/CLI） | 代码里 fail-closed（预算 settle、判官、证据编号、披露义务） |
| 够用条件 | 单用户、人在环、会话制、错误代价可控 | —— |
| 成本 | 近零（symlink skills + 抄零件） | P1–P2 整层（loop/恢复/trace/部署身份） |

**升级成 copilot 的触发信号（马书判据：行为指导放 prompt，结构性承诺放代码）——出现任何一条再动手，且只把出现的那层长出来：**
1. 有约束**必须** fail-closed 在代码里，提示词到达率不够（例：答案必须过判官才能发布、预算耗尽要优雅降级不是硬失败）；
2. 要给**别人**用（多用户、UI、会话合同 run_id/配额）；
3. 需要**可重放审计**的 trace（收据、台账、事后归因）；
4. agent 循环本身要**无人值守**跑（不是 launchd 定时脚本那种，是循环内自主决策的）。

三变量与形态的映射（`harness-bootstrap` A 步采访的正是这个）：错误代价高 → 约束进代码的压力大；可验证性强 → 值得建 P3 量具（两种形态都能建，组件打分器方法论不依赖 copilot）；生命周期长 → 资产会积累，厚底座才回本。三变量都低（如 vidio）→ 通用 agent 里调组件就是终态，不必升级。

**警告**：金融仓的 runtime（`episode protocol`、`GLMAgentRuntime` 等）是**组合根**，BUILD 明说不当零件搬；新领域若真要 copilot 化，按 DESIGN-stack 六层重新长，抄的是形状不是代码。

对 FDE 岗位的映射：这个决策框架本身就是 FDE 现场的核心判断（给客户装独立 copilot，还是把组件嵌进客户既有栈），面试可直接讲。

## 待办指针（不在本轮范围，记下防丢）

- [ ] `agent-run-review` 迁入共享 skill 仓（与 agent-run-triage 同仓或 arts 仓），symlink 双端。
- [ ] harness-reference `KIT.md`/`BUILD.md` 回写——本地树 2026-08-27 深夜仍在途（BUILD/KIT/PLAYBOOK/TOOLKIT 四份带 M，分支 docs/constraint-three-sieves），等收口后补两条（内容已备好，直接贴）：① BUILD「会话骨架」备注 code map 夜间刷新零件（finance `scripts/install_code_map_refresh.py`）；② BUILD 缺口节「没有脚手架命令…目前 n=1，先不做」更新为「n=2 已发生（2026-08-27 kb 移植，PR #94），移植实验表首行见 kb `docs/superpowers/specs/2026-08-27-harness-bootstrap-report.md`，『值得自动化』=尚无，脚手架继续冻结」。
- [ ] Phase B 开工时先跑 `git -C ~/harness-reference show gitea/main:DESIGN.md` 拿顺序轴 SSOT，勿读脏工作树。

## 成立条件

tree: agent-memory@main（本文）；finance-workspace-private@main fea0633e 起分支；harness-reference 只读了 gitea/main 与工作树对照。interpreter: 宿主 python3（只跑只读门面与 lint）。核查均为静态读取 + symlink 实测，未跑 harness-bootstrap 全流程。dirty: finance 主树 20 个脏文件均为他人 ingest 数据产物，未认领、未提交。
