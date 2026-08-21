---
title: vidio · 短视频运营（抖音起号）
type: project
agent: grok
source: 对话共创 + https://github.com/linxiaoqi5111-del/vidio branch ops/short-video
date: 2026-07-10
tags: [project, vidio, douyin, short-video, ops, finhot]
status: active
related: ["[[finhot]]", "[[finance-workspace-private]]"]
---

# vidio 短视频运营 — 项目 MOC

## 概述
- **目标**：为 FinHot + 金融 Agent 做抖音冷启动与内容获客；Grok 任运营顾问。
- **状态**：active。日常 tip 是本机 Gitea `main`（2026-08-14 #9+#10 后快照 `70f67ef`）。`~/vidio` 的 `ops/short-video` 停在 7-11，新活不要从那开。
- **工作仓**：本机 `/Users/a77/vidio`，远程 `gitea` → `http://127.0.0.1:3300/a77/vidio.git`
- **负责**：human 拍发 · grok 策略/脚本/复盘

## 架构决策（重要）
- **不新开 Obsidian vault**。长期记忆继续用本 vault；项目 SSOT 在 `vidio/ops/`。
- 详见仓内：`ops/knowledge/obsidian-decision.md`

## 项目内 SSOT 路径（vidio）
| 路径 | 内容 |
|------|------|
| `ops/knowledge/` | 钩子 playbook、冷启动假设、skill 目录、流水线 |
| `ops/douyin/` | 策略、排期、脚本、复盘、钩子库 |
| `ops/shared/principles.md` | 合规与起号原则 |
| `industry7view-card-lab/` | 成片生产（行业卡/Remotion） |
| `短视频演讲稿/` | 题材母稿 |

## 关键决策（2026-07-10 用户确认）
- 旧号 **弃用** · **开新号**
- 主叙事：**Deep Fomo 研究过程**；FinHot 第 16 条后软植入
- 出镜：**情绪素材 + 屏幕**（约 0–3.5s 硬切）
- 前 10 条：框架优先、少点具体票
- Industry 7View：**偶尔插 1 条**（每 6–8 条 ≤1）
- 前 15 条禁止硬广/外链/报票 CTA
- 完播+评论优先于播放量

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|------|------|------|------|
| 仓库清理 + ops 骨架 | grok | done | branch ops/short-video |
| 知识资产首批入库 | grok | done | hooks/skills/coldstart |
| 全 repo 起号规划 | grok | done | launch-plan.md |
| 决策锁定写入文档 | grok | done | 情绪+屏幕 / 偶插 / 弃旧开新 |
| 新号资料定稿 | human | todo | profile-copy 昵称三选一 |
| 前 7 条可拍脚本 | grok | todo | 等昵称或直接开工 |
| face-hook 素材规范 + 试渲染 | both | todo | kit + 情绪段 |
| 发布后复盘闭环 | both | todo | reviews/ |

## 相关知识
- 项目内全文：vidio `ops/knowledge/README.md`、`ops/douyin/launch-plan.md`
- 产品：[[finhot]] · [[finance-workspace-private]]

## 交接记录
- 2026-08-21 · cursor · 创作 copilot 网页入口落在同一棵树：studio 默认「创作」页，`POST /api/create` 按 `lane-map.json` 认形态（认不出 fail closed）。picture 盘点后无创作能力可吸纳（只剩测试截图），不引用。对象是通用成片，不是自有产品宣传。未提交。
- 2026-08-21 · cursor · 工作区 Copilot 控制面收口（A）：干净树 `/Users/a77/vidio-wt-constitution` 分支 `fix/constitution-lane-whitelist`（基线 `a84c0ec`）。`AGENTS.md` 为唯一宪法；`.claude/CLAUDE.md` 降为入口指针（旧 Industry 7View 主线删掉）。车道白名单真本源 `.agents/skills/vibe-director/lane-map.json`（8 条，`unknown_form=fail_closed`），生成表进导演技能与 `lane-map.md`；`studio/server.mjs` 读 JSON 不再手写 LANES。门禁 `python3 scripts/check_lane_map.py`（已变异验证：写回 `const LANES = [` 会红）。顺手把从未入库的三件自有技能纳入这棵树：`vibe-director` / `promo-film-pipeline` / `openmontage-adapter`。未提交未推；`~/vidio-gitea-main` 脏树未碰。
- 2026-08-20 · cursor · 按锁恢复技能到 `~/vidio-gitea-main`：官方 `experimental_install` 因中文名/缺 SKILL.md 中途失败；改为按源仓 shallow clone 拷入 `.agents/skills/`。锁内 88/88 已有 `SKILL.md`。仓内补回三件（从未进 git）：`vibe-director`、`promo-film-pipeline`、`openmontage-adapter`。三方约 171MB 且 SKILL.md 哈希对不上 lock（上游 HEAD 已漂），不要整树 `git add .agents/skills`。`vendor/openmontage` 未克隆。成片须在 vidio 仓开对话。
- 2026-08-20 · cursor · 吸纳 [emilkowalski/skills](https://github.com/emilkowalski/skills) 11 个技能到 vidio（分支 `feat/emilkowalski-skills`，提交 `a84c0ec` 已推 Gitea）。`emil-design-eng` / `animation-vocabulary` 改挂官方源。未合 main。
- 2026-08-15 · cursor · GitHub 按不解封：日常远程改本机 Gitea。`gitea/main`=`70f67ef`（#10 后内容快照）。本机 `ops/short-video` 不是日常基线。
- 2026-07-10 · grok · 建 MOC；沉淀 hooks/skills/算法假设到 vidio/ops/knowledge
- 2026-07-10 · grok · 用户确认：情绪+屏幕、产业偶插、弃旧开新；更新排期与 strategy
