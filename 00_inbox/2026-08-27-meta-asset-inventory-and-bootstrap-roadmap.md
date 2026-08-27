---
title: 元资产盘点与自举复刻路线图（宏观理解四层地图 + meta-skill 复用性裁决）
type: inbox
agent: claude
source: "用户提问（宏观理解是否足够 / meta-skill 能否复用 / 自举复刻 agent 落地）+ 对 harness-reference gitea/main、agent-memory、finance-workspace-private、~/.claude/skills 与 ~/.codex/skills symlink 的实测核查"
date: 2026-08-27
tags: [inbox, meta-assets, bootstrap, harness, code-map, reuse, roadmap]
status: draft
---

# 元资产盘点与自举复刻路线图

> 回答三个判题：① 代码行数多时（实测本仓 425K 行 Python / 3133 个跟踪文件）现有 loop 图 + code map 够不够支撑宏观理解；② harness / agent-run / 组件打分机（FDE 产品化判据，2026-08-27 用户纠偏后钉准）/ trace diff 这批 meta-skill 是否可复用；③ 「以金融 agent 为原型自举复刻其他 agent」怎么落地。
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
| 组件打分机（FDE 产品化判据）[纠偏 2026-08-27] | fde-os 仓 `skills/fde-productization-four-questions/`（四问：≥3 客户共性 / 泛化经济性 / 非工程师可用 / 现场创造力余地，全过才进平台）+ `skills/fde-reflux-to-product/`（回流日志 solo/common 标签 → 组件抽取 → 产品资产）；蒸馏稿 `fde-os/distilled/fde-deep-read.md`（随体系自 harness-reference 迁走，不留双源）；本 vault 只有读书索引 `10_knowledge/fde-guidance-book-reading-index.md` | **可复用，已在独立仓**——fde-os（2026-08-14 迁出，31 skill）就是 KIT 第四层「岗位操作系统」，天生跨项目。它与 BUILD「模式须 ≥2 零件验证才晋级」、本文 Phase C 触发条件是**同一个形状**：重复度达标才准入 |
| 接口深浅判据（初稿曾把它误认成上一行） | 通用形状在 `codebase-design` skill（已共享）；金融仓特化在 `docs/agent-product-door.md`（门/引擎/组装/积木四层，不混着打分）| 形状可复用。与上一行是**两台不同的打分机**：上行判「组件要不要晋级为共享资产」（准入向），本行判「接口做得深不深」（质量向） |
| `divergence-distill`（trace diff）| finance 仓 `.claude/skills/divergence-distill/`，六个沉淀池全绑金融仓（reading_baseline / experience_cards / record-correction CLI / _PENDING_RULES / 视角差分 / 知识库证据层）| **部分复用**：分类判别式（控制面前置、可证伪测试、双用户测试）可带走；池子是领域件，换领域要先建对应池。BUILD.md 已自标「候选模式 n=1，第二实例出现才升格模式」 |

原理（可迁移）：复用有三种形态，成本与漂移风险递增——**① 指针复用**（symlink/子模块指向 SSOT，改一处全端生效，本机已用）→ **② 移植复用**（读源码抄过去 + 换词表，BUILD.md 每条零件写明「移植要改什么」就是为这形态服务）→ **③ 生成复用**（脚手架/模板生成，只有重复次数证明了才值得建，否则维护模板本身成为新负担）。跳过 ② 直接建 ③ 是 premature abstraction 的组织版。

## 判题 3：自举复刻 agent——方向成立，顺序必须尊重已立的纪律

「自举」（bootstrapping）类比：编译器界先用旧工具造出能编译自己的编译器，再脱离旧工具。对应到这里：**用金融 agent 沉淀的三件套（设计/搭建/审计）+ harness-bootstrap 流程，去立第二个领域 agent；第二个立起来的过程反过来验证并磨利三件套本身**——这就是自举回路。

但 BUILD.md 缺口节已写死两条边界 [实测]：「没有脚手架命令，n=1 先不做」「没有跨项目版本管理」。`harness-bootstrap` D 步专门留了「移植实验空表」（抄了哪些 / 改了哪 / 卡在哪 / 哪步重复到值得自动化），等第一次真实跨领域移植来填。**复刻器不是先造框架，而是先攒第二个实例。**

### 三阶段路线

**Phase A（2026-08-27 本轮，已执行）**
- 本盘点文档落 inbox。
- finance 仓分支 `docs/macro-map-and-code-map-refresh`（待用户确认合并）：AGENTS.md 宏观理解路由表 + `scripts/install_code_map_refresh.py`（launchd 夜间 stale→build）。

**Phase B（下一步大活，另开工）：第二领域真实移植（n=1→n=2）**

流程：`harness-bootstrap` 采访三变量 → P0–P6 厚度 → 按失败形状挑零件 → 真实移植 2–3 个零件 → **填 BUILD.md 移植实验空表** → 回写 KIT。试点候选对比：

| 候选 | 三变量预判 | 试点信息量 | 建议 |
|---|---|---|---|
| knowledge-base-private | 错误代价中（污染检索）、可验证性强（lint/审计已有）、生命周期长 | 中——同栈同用户，已半共享纪律，移植阻力最小 | **近端试点，先做**：低风险填出空表第一行真数据 |
| finhot（TS/Electron） | 错误代价低中、可验证性中、生命周期长 | 高——跨语言栈，能检验「模式 vs 零件」分离度（Python 零件抄不动时，模式还剩多少）| **跨栈试点，第二步** |
| vidio（运营为主） | 错误代价低、可验证性弱、生命周期短 | 低——按三变量各层大概率全薄 | 不推荐当试点 |
| 全新领域 agent | 视领域 | 最高，成本也最高 | 等前两个试点摊薄成本后再议 |

**Phase C（条件触发，不排期）：自举工具化**

触发条件写死：**n≥2 且移植实验空表「哪一步重复到值得自动化」非空**。届时才做：脚手架/复刻器（形态到时候按空表定，可能是生成器、可能只是一个 checklist skill）+ 解决「跨项目版本管理」缺口（同一零件多仓副本的同步通知）。触发条件不满足前动手 = 违反自家 BUILD.md 缺口节的边界。

这条触发纪律与 fde-os 的产品化四问**同构**（三客户撞同一缺口才配进平台 ↔ 零件被 ≥2 个领域真实要过才配抽包）；到 Phase C 裁决时可直接套四问表，不必新发明判据。

## 待办指针（不在本轮范围，记下防丢）

- [ ] `agent-run-review` 迁入共享 skill 仓（与 agent-run-triage 同仓或 arts 仓），symlink 双端。
- [ ] harness-reference `KIT.md`/`BUILD.md` 回写「code map 夜间刷新」一行——本地树 2026-08-27 有他人在途改动（BUILD/KIT/PLAYBOOK/TOOLKIT 四份带 M，分支 docs/constraint-three-sieves），等收口后补，或另开干净 worktree。
- [ ] Phase B 开工时先跑 `git -C ~/harness-reference show gitea/main:DESIGN.md` 拿顺序轴 SSOT，勿读脏工作树。

## 成立条件

tree: agent-memory@main（本文）；finance-workspace-private@main fea0633e 起分支；harness-reference 只读了 gitea/main 与工作树对照。interpreter: 宿主 python3（只跑只读门面与 lint）。核查均为静态读取 + symlink 实测，未跑 harness-bootstrap 全流程。dirty: finance 主树 20 个脏文件均为他人 ingest 数据产物，未认领、未提交。
