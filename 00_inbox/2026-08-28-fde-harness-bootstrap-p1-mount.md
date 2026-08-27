---
title: FDE agent 装骨架 · P1 装载面落地与移植实验表（第三领域，n=3）
type: inbox
agent: claude
source: "harness-bootstrap skill 全流程（采访三变量 → P0–P6 厚度 → BUILD 挑零件 → 执行 P1）+ 对 ~/fde-os、~/.claude/skills、~/.codex/skills、settings.json 的实测核查 + 工作区内 headless 会话真实验收"
date: 2026-08-28
tags: [inbox, fde, harness, bootstrap, 移植实验, 装载面]
status: draft
---

# FDE agent 装骨架 · P1 落地

> 承接 `2026-08-27-meta-asset-inventory-and-bootstrap-roadmap.md` 的 Phase B。
> 第一次移植是 knowledge-base-private（PR #94，n=2），本轮是 fde-os（n=3）。
> 本文只记裁决与实验表，厚度判据不抄（SSOT 在 harness-reference `gitea/main:DESIGN.md`）。

## 开工前的实测发现（两条，都是缺口不是漂移）

1. **31 个 skill 对任何 agent 都不可见** [实测·四路核查]：`~/.claude/skills/` 与
   `~/.codex/skills/` 无一条 symlink 指向 fde-os；仓内无 `.claude/`；
   `settings.json` 无引用；会话可用 skill 清单里 `fde-*` 零个。
   建仓日 2026-08-14 → 发现日 2026-08-28，**这 31 个 skill 死了两周，无人察觉**——
   因为仓库本身看起来是完整的。
2. **"借鉴别家做法"这格是空的** [实测]：`templates/industry-priors/` 只有 README +
   `_template.md`，零条真先验，无取数管线。这恰是用户本轮口述的核心诉求
   （"这家公司的困境，别家可能已经解决了"），也是它与金融仓最大的落差——
   金融那格有 kb corpus + RAG + RSS + 搜索，FDE 这格没有 corpus、没有取数口、没有评委。

## 三变量（用户原话）

错误代价 = 中，"伤我自己的时间和判断" · 可验证性 = "少数几条会回填"
（承诺兑现 / 决策 call 实际结果 / 数字的分母窗口评委） · 生命周期 = 长，"年级职业资产"。
先验来源三条全要：公开信源现搜 + 复用 kb corpus + 自己做过的单回填。

## 厚度裁决

P0 契约=厚（缺先验条目证据契约 + 仓根无正门）· P1 底座=**薄，刻意薄**（租 Claude/Codex 的循环；
copilot 四条升级信号今天零条亮）· P2 观测=以后再做（触发：第一次"某条先验害我做错判断但说不清来路"，
或上岗后要向雇主交代结论来路）· P3 量具=薄（只对三条可回填项建，且 `fde_calls.py:115-118`
已实测内置"样本<5 只报计数不报比率"）· P4=以后再做（触发：任一把握桶≥5 笔，或第 3 个同类单）·
P5 战线=薄（唯一的尺是先验进场验证回填率）· P6 资产=厚（私有工作区今天不存在，是第二个真实缺口）。

## 本轮执行：P1 装载面

挂法选型（三选一，用户拍板"项目级"）：全局挂 31 个（实测 description 合计 16256 字符
≈ 4000 tokens 常驻，且 `fde-evals` / `fde-security-review-prefill` 等会在金融仓会话抢戏）
vs 全局只挂 L0（~200 tokens，多一跳）vs **项目级挂在私有工作区**（不在该目录零加载零串台）。
选项三与用户既有惯例一致 [实测：finance `.claude/skills/` 25 个、kb 16 个，全项目级，零个进全局]。

落地：新建 `~/fde-workspace/`（git 仓，**无 remote**）→ `.claude/skills/` 31 条 symlink 指回
`~/fde-os/skills/fde-*` → 正门 `AGENTS.md` + 指针 `CLAUDE.md`。首提交 `5d29035`。

**验收（双向，真实环境）**：正向 = 在工作区内起 headless 会话，31 个 skill 全部在场且名字逐条可核；
反向 = 工作区外会话 `fde-*` 为零，证明挂载有边界。挂载前先核对了目录名与 frontmatter `name`
一致性 31/31（不一致会静默失效），并排除了 `skills/fde-os/`（元目录，无 SKILL.md）。

## 移植实验表（BUILD 缺口节要的那张，本轮真数据）

**抄了哪些文件**：**零个**。本轮没从 finance 抄任何代码。P1 装载面需要的是接线，不是零件——
这本身是发现：第三个领域的第一步不是移植，是让已有资产能被运行时看见。

**每个文件改了哪几处**：`~/fde-os` **零改动**（工作树仍干净，仍是 `a05aeec`）。
全部新增落在新建的 `~/fde-workspace/`（AGENTS.md 57 行 + CLAUDE.md 6 行 + 31 条 symlink）。

**卡在哪**：**77 处仓内相对路径**（`skills/fde-*/SKILL.md` 51 处、`skills/fde-os/{templates,scripts}/`
26 处，分布在 21 个 SKILL.md）。项目级挂载后这些路径的基准根变了，按字面找会找不到，
而"找不到"极易被误判成"这个文件不存在"。
**选了补基准不选改引用**：改 77 行 = 重写一个已被逐条审计过的体系（PLAN-growth §8/§9 记录了
两轮质检修的十条实伤），风险远大于收益；补一份正门把"以 `/Users/a77/fde-os/` 为根解析"
这条事实投递到保证被读的时刻，一个文件解决全部 77 处。这是 BUILD 模式 3（事实投递>提醒）
在"路径基准"上的新实例。

**哪一步重复到值得自动化**：**尚无。** kb 那次移的是 hook/收据（无挂载步骤），
本次的"挂载 + 名字一致性核对 + 双向验收"三步严格说是 n=1，不构成重复。
唯一 n=2 的是**双向验收纪律**本身（kb 收据链正负双向、本轮挂载正负双向）——
但那是纪律不是工具，不需要脚手架。**结论：脚手架继续冻结**，与 BUILD 缺口节边界一致。

## 下一步（一次一层）

**P0 增量**：① 先验条目证据契约（出处/年份/规模/数字口径/来源等级/验证态）；
② fde-os 仓根正门（今天顶层只有 `.gitignore`/`README.md`/`distilled/`/`skills/`/`upstream/`，
无 AGENTS.md）。**它是先验能力开跑的前置闸**——那格空着就上线 = 无出处生成器，
与"错误代价=中、伤判断"直接对冲。不许与 P1 之外的层并行。

零件清单（按失败形状从 BUILD 挑，待 P0/P6 执行时用）：SessionStart 事实注入 ·
4.2 证据账本族（`evidence_ledger` + `claim_lineage`，`source_credibility` 整表重写：
FDE 版大致是 一手实测>同行私下>会议演讲>厂商官宣>模型记忆）· 4.4 记忆门族
（先验回填必须追加状态行不改原行）· 模式 5 provenance + 确定性披露 ·
`graph_audit.py` 三态（L0 路由表 33 行手抄 31 个 skill 路径，今天无任何门禁校验它）。

不装：episode 全族、`runtime/`（组合根）、`tool_result_budget`/`query_ledger`（无自有工具管线）、
`evidence_window`/`experience_cards`（词表要换但未准备）、脚手架/pip 包（触发条件未满足）。

## 待办指针

- [ ] harness-reference `BUILD.md` 缺口节回写：n=3 已发生，移植实验表见本文；"值得自动化"仍为尚无。
      （与 2026-08-27 路线图那条待办合并处理，需开分支走 PR。）
- [ ] `~/fde-workspace` 无 remote。P6 的"可回滚"已由本地 git 满足，但"跨机/备份"未解决；
      要推 gitea 前先确认它是私有仓——**该目录将存客户数据**。

## 成立条件

tree：`~/fde-os` @ main `a05aeec`（clean，本轮未改）；`~/harness-reference` 只用
`git show gitea/main:` 读（`0afc330e`），未检出工作树；`~/fde-workspace` @ main `5d29035`（新建）。
interpreter：宿主 python3（只跑两个 L3 脚本冒烟，二者只读写本地不联网）+ Claude Code 2.1.220 headless 验收。
design_ssot = present（哨兵"七层生命周期"/"P0 领域契约"命中，非形状轴）。
**未做**：未读 `PLAN.md` 全文（只读 `PLAN-growth.md` 全文 + L0）；21 条 L2 只读 description 未读正文；
`fde_overnight.py` 只跑 `--help`（无账户可跑）。附带小毛病一条：`fde_calls.py --help`
会把 `--help` 当文件路径，输出"无观测源"。
