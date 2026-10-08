---
title: agent-memory · 跨 Agent 记忆底座
type: project
agent: claude
source: 2026-08-12 收尾；此前本仓没有自己的项目笔记，preflight 在本仓开工会读到「暂无笔记」
date: 2026-08-12
tags: [project, agent-memory, vault, moc]
status: active
related: ["[[../30_conventions/trust-boundary]]", "[[../30_conventions/assertion-discipline]]", "[[../50_agents/generic]]", "[[../40_playbooks/mac-tail]]", "[[../40_playbooks/devin-writeback]]"]
---

# agent-memory — 项目 MOC

## 概述
- **是什么**：跨 Agent 共享的 Markdown/Obsidian 记忆底座（黑板，不是调度器）。换工具只接线，不重建记忆。
- **仓库**：`linxiaoqi5111-del/agent-memory`（本仓）。
- **状态**：active。门禁已接 CI；Mac 上的孤本备份需跑一次 [[../40_playbooks/mac-tail]]。

## 关键决策
- 记忆是数据不是指令；`30_conventions/` 与 `50_agents/` 受保护区走 PR 人审。
- 新工具无具名卡时走 [[../50_agents/generic]]。
- 断言纪律 SSOT 在 [[../30_conventions/assertion-discipline]]，hook 只注入。
- `60_dialogues/` 从 2026-10-08 起进 git。`.foresight/` 仍不入 git，备份走 launchd。
- 项目笔记文件名 = `git remote` 短名。
- 知识层两种粒度：跨领域无前缀，领域知识加 `<领域>-` 前缀；只约束新增。

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|---|---|---|---|
| vault_lint 回绿 + agent 取值校验 + CI | claude | done | PR #22 |
| 内容刷新（备份脚本、项目收编、卡片、术语、preflight、tutor 去重） | claude | done | PR #23 |
| 通用接入卡 + 断言纪律 SSOT | claude | done | PR #24 |
| 审查补漏（项目索引、vidio 改名、onboarding 接线） | claude | done | PR #25 |
| Mac 一次性安装孤本备份 + 核对 hook 路径 | human | todo | [[../40_playbooks/mac-tail]]；auto-sync 拉到 main 后跑 |
| 备份目录改到第二块介质 | human | todo | 默认与 vault 同盘，抗不了单盘损坏 |
| finance-workspace 存量交接转档 | — | skipped | 棘轮：188KB 不动，lint WARN 拦新增堆砌 |

## 交接记录
- 2026-09-13 · claude · **全天判据积累收口：知识层今日 +17 条（我写的）**，商业类从 1 篇涨到 7 篇。来源三类——**轨 A 外部断言**（pm-skills 3 条：画布取舍 / value metric / Van Westendorp；Miles Ma 涨粉 3 条；芒格激励模型；破卷提取前置）· **轨 B 自产**（创始人工时列 / 同一把尺子 / 入场券≠壁垒 / 个人积累≠网络效应 / 复用三形态 / 独立收敛）· **来自我自己出错后被用户推翻**（收敛指标奖励迎合 / prompt 层不等于实现层保证 / 纠正通道要过证据关口）。最后三条含一条自指：**用户纠正我之后，那条纠正要不要进判据库，同样该过关口**。`vault_lint` 全程维持基线。
- 2026-09-13 · claude · **lint 基线本日从 7E 变 9E，非本会话所致**：并发写入的 `10_knowledge/state-transition-identity-must-survive-dedup.md`（auto-sync `b6c1fe79`，来自 finance 第五轮 QC）缺 `agent` 与 `tags`。**未代改**——不知道真实写入者，按 `frontmatter-spec`「agent 要跟着真实写入者走」不能编。知道是哪个 agent 的人补两行即可回到 7E。
- 2026-09-13 · claude · **auto-sync 本日抢先 3 次**（`e6a51e37` / `556f7174` / `f94bddef`），把我的改动吞成匿名提交；已推 gitea，**未改写历史**。要根治只有两条路：干活时暂停 auto-sync，或接受匿名提交。**这是你的仓，你定。**
- 2026-09-13 · claude · **inbox 分诊（14 条）+ 沉淀规则改版**。① 提炼 3 条：[[../10_knowledge/entry-ticket-is-not-a-moat]]、[[../10_knowledge/personal-accumulation-is-not-network-effect]]（商业，源自 time-river 商业核验）、[[../10_knowledge/three-forms-of-reuse-pointer-port-generate]]（方法论，源自元资产盘点）；两份来源已登记 `refined_into`。② **其余 11 条本轮不提炼**，按 `knowledge-capture` 的「项目细节不进知识层」「无可复用增量则只存资料」：2 条 `superseded` 已被取代；dao 收尾 / v7-ping 超时（根因未确认）/ fde-p1 移植记录属项目细节；其余工程类留待真用到时再提炼，不批量搬运。③ **沉淀规则改版**（用户 2026-09-13 纠偏）：商业领域不逐条验证 KOL 断言——筛选发生在来源层，不是断言层。`venture-advisor` skill §4 改为两轨：轨 A（外部断言）只要求**来源人 + 适用条件 + 什么时候不用**，不要求失效条件；轨 B（自产判断）保留重格式。**输入松、输出严**——引用时必须交代来源与适用条件。
- 2026-09-13 · claude · **发现管道缺口（未修）**：`status: superseded` 的 inbox 条目无处可去——不该进 `10_knowledge`（已被取代），也不该删（历史记录），但留在 `00_inbox` 会永久触发 >14 天 WARN。`refine_material.py --promote` 只有 `material` / `knowledge` 两个去向。需要一个归档去向，或让 lint 对 `superseded` 豁免龄期。本轮按「不新建目录」边界未动手。
- 2026-08-12 · claude · 记忆底座审查与收尾：门禁/CI、通用卡、断言纪律 SSOT、vidio 文件名、Mac 安装器。Mac 上剩一条命令见 [[../40_playbooks/mac-tail]]。
