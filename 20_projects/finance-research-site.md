---
title: 金融网站 (finance-research-site)
type: project
agent: devin
source: https://github.com/linxiaoqi5111-del/finance-research-site (README/AGENTS)
date: 2026-06-28
tags: [project, 金融网站, astro, cloudflare, seo, geo, javascript]
status: active
related: ["[[knowledge-base-private]]", "[[finhot]]"]
---

# 金融网站 — 项目 MOC

## 概述
- **是什么**：面向**读者与 AI 检索（GEO）**的金融产业研究网站。
- **仓库**：`linxiaoqi5111-del/finance-research-site`（private，JavaScript/Astro，分支 `main`）
- **注意**：`main` 是共享基线但**仍在持续修缮**，不代表已稳定。

## 技术栈
- **Astro** 静态站（`astro.config.mjs`）
- **Cloudflare** 部署（`wrangler.jsonc`）
- 内容用 Markdown frontmatter 管理（标题/摘要/分类/标签/日期）

## 目录导览
- `src/content/research/` — 研究文章（Markdown）
- `src/` — Astro 页面/组件；`public/` — 静态资源
- `scripts/` — 导入/生成脚本（含 `llms-full.txt` 等 GEO 文件）
- `docs/` `AGENTS.md` `CLAUDE.md`

## 关键命令
```bash
npm install
npm run dev
npm run build
```

## 强制规则（来自 AGENTS.md）
- 开工先 `git status --short && git branch --show-current` 并汇报。
- **大任务不在 `main` 直接做**：新增/批量导入文章、改 `src/content/research/`、改 SEO/GEO 文件、改 Astro 页面/组件、改导入脚本、批量生成 `llms-full.txt` 等，必须从最新 `main` 新建任务分支；合并回 `main` 需用户确认。
- 分支命名：`research/<文章/主题>`、`content/<主题>`、`seo/<问题>`、`site/<页面/组件>`、`fix/<问题>`。
- 禁止提交：`.env*`、`mcp_config.json`、`feishu_config.json`、`*.pdf/zip/duckdb/db` 等。

## 关联
- 研究内容与 [[knowledge-base-private]] 的 wiki/synthesis 互为上下游（知识 → 文章）。
- 与 [[finhot]] 同属金融内容矩阵：site 是**研究文章网站**，FinHot 是**信息流阅读器**。

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|---|---|---|---|
|  |  |  |  |

## 交接记录
- 2026-08-06 · codex · **industry7view 运维与曝光修复**：在 `fix/industry-article-quality`（commit `55edf4b`）删除 `lighthouse-factory`、`power-chip`、`thermal-materials` 的重复附录，合并保留独有相关研究链接，并同步生成 `public/llms-full.txt`；`npm run validate`、`npm run lint:articles:strict` 均通过（83/83），`npm run build` 通过（103 pages）。`public/robots.txt` 在分支上放开 GPTBot/ClaudeBot，继续拦截 CCBot/Bytespider；线上当前仍是旧版本，因 Worker 部署权限/流程未确认，未直接发布。Cloudflare 账户现有 token 可读 Pages 但不能读 Workers，`wrangler whoami` 未登录。仓库 main 当时落后 origin 24 commits 且有用户改动，未 pull/覆盖/合并；分支已推送。
- 2026-06-28 · devin · 初次建档（基于 README/AGENTS）
- 2026-07-02 · devin · 合并收尾：PR #11（thermal-materials 附录三件套去重）直接合并；PR #2（信息长图生成器 scripts/poster/，HBM 5 张 + 被动元件 4 张，chainmap 接题材雷达快照）先把 main 合进分支解 .gitignore 冲突（保留 .chrome-profile 忽略 + main 的 .agent-memory 行），本地 node 22 下 `npm run build`（105 页）与 `npm run validate`（85/85 严格）通过后合并。注意：本仓 Astro 要求 node >=22.12。
- 2026-07-02 · devin · 用户约定（重要）：**网站仓 main 只部署文章类改动**（src/content/research/ 等正文/修补），海报生成器等工具类功能不上 main、不部署。当日 PR #11/#2 合并后已按用户要求 revert（main 回滚到合并前，分支保留：fix/thermal-materials-dup-appendix、site/infographic-poster-generator，需要时可重开 PR）。
- 2026-07-06 · devin · add research: 华为芯片（huawei-chip）：走 import/enrich/deepen 管线，17 节+附录三件套、11 表、加粗数字带来源；lint 0 warn，node 22 下 npm run build 107 页通过。PR #13（research/huawei-chip → main），等用户确认合并；合并后需 npm run indexnow。sourceFile=华为芯片产业新格局深度研究报告：自主可控突破与供应链重构-full.md。
- 2026-07-06 · devin · 华为芯片收尾：PR #13 已合并 main，npm run indexnow 返回 200（含 huawei-chip URL）；另按 content-matrix 工作流产出三件套（内容矩阵/公众号/雪球 各目录下 华为芯片-*.md），敏感词检查全过。
- 2026-08-12 · grok · add research 电子特气（electronic-specialty-gas）手写17节+石英砂骨架公众号稿 → https://github.com/linxiaoqi5111-del/finance-research-site/pull/29
- 2026-08-12 · grok · add research 钛合金（titanium-alloy）raw full 主稿经隧道取回+2025 年报更新，高端认证 vs 中低端内卷主线 → https://github.com/linxiaoqi5111-del/finance-research-site/pull/30
- 2026-08-12 · grok · add research ASIC芯片（asic-chip）raw 主稿+博通FY2025/寒武纪海光2025年报更新，剔除主稿投顾表达；用户定：不跑 IndexNow、三分支独立按天推 → https://github.com/linxiaoqi5111-del/finance-research-site/pull/31
- 2026-08-12 · grok · add research 激光雷达（lidar）raw 提纲式主稿+禾赛/速腾2025年报更新，主线：降价99%→智驾平权+机器人第二曲线→盈利拐点 → https://github.com/linxiaoqi5111-del/finance-research-site/pull/32
- 2026-08-12 · grok · add research 超导（superconductor）并行子agent撰写+主agent终审，供给曲线×聚变需求曲线框架 → https://github.com/linxiaoqi5111-del/finance-research-site/pull/33
- 2026-08-12 · grok · add research 信创（xinchuang）并行子agent撰写+主agent终审，政策雄心vs报表现实主线 → https://github.com/linxiaoqi5111-del/finance-research-site/pull/34
- 2026-08-12 · grok · add research 折叠屏（foldable-screen）并行子agent撰写+主agent终审，苹果入局+增收不增利排雷框架 → https://github.com/linxiaoqi5111-del/finance-research-site/pull/35
- 2026-08-12 · grok · 方法论沉淀：3 篇并行 = git worktree 隔离 + 任务书写死规范（17节/lint/红线/清洗）+ 主agent终审闸门；质量与串行相当
- 2026-08-12 · grok · add research 稳定币（stablecoin）并行批次2，真产业假题材+三问排雷框架，新增「金融」分类 → https://github.com/linxiaoqi5111-del/finance-research-site/pull/36
- 2026-08-12 · grok · add research 固态变压器（solid-state-transformer）并行批次2，纠正主稿英伟达路线表述+三级验证框架 → https://github.com/linxiaoqi5111-del/finance-research-site/pull/37
- 2026-08-12 · grok · add research 制冷剂（refrigerant）并行批次2，配额=类牌照资产+R22 反例风控 → https://github.com/linxiaoqi5111-del/finance-research-site/pull/38
- 2026-08-12 · grok · add research GPU/先进封装/磷酸铁锂（B5 并行批次），差集队列共 43 批约 110 主题已落盘（/Users/a77/内容矩阵/主站选题队列.md）→ PR #39/#40/#41
- 2026-08-12 · grok · add research 稀土/铀矿/MiniLED（B6 并行批次）→ PR #42/#43/#44；队列 B7 起继续
- 2026-08-12 · grok · add research 一体化压铸/盾构机/模拟芯片（B7 并行批次）→ PR #45/#46/#47
- 2026-08-12 · grok · add research 英伟达供应链/锂电池/航运（B8 并行批次，两个双主稿合并主题）→ PR #48/#49/#50
- 2026-08-12 · grok · add research 卫星导航/毫米波雷达/车路协同（B9 并行批次）→ PR #51/#52/#53
- 2026-08-12 · grok · add research 超充(三稿合并)/海底电缆(两稿合并)/风电（B10 并行批次）→ PR #54/#55/#56
- 2026-08-12 · grok · add research 抛光液/电子束光刻/芯片IP（B11 并行批次）→ PR #57/#58/#59
- 2026-08-12 · grok · add research SoC芯片/电源管理芯片/忆阻器（B12 并行批次）→ PR #60/#61/#62
- 2026-08-12 · grok · add research 磁悬浮压缩机(两稿合并)/铜母线/HVDC（B13 并行批次）→ PR #63/#64/#65
- 2026-08-12 · grok · add research 硅产业/铜箔/石墨电极（B14 并行批次）→ PR #66/#67/#68
