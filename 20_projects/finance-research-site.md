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
| 0812-0813 128 篇批量集成 | cursor | 完成 | #157 已合 main；#158 pr-checks 防 llms 冲突；#15 关闭不采用 wechat-adapt |
| 工作流路径对齐 a77 | cursor | 完成 | #159 已合；禁 git add .；仓内 docs/content-matrix；RAW_DIR 回退 |
| 一日一篇：0816 电子特气 → 0818 钛合金 → 0819 ASIC芯片+激光雷达（当日双篇），队列工具 `scripts/publish-queue.mjs` | devin | done | 0819 双篇已上线（104 篇基线），明日 #33 superconductor |

## 交接记录
- 2026-08-19（晚）· devin · **一日一篇第 4 篇（激光雷达）当日加推**：用户反馈 ASIC 公众号稿昨日已自行发表，要求再推一篇——同日第二篇走同一全链：#32 lidar 恢复+redate 0819 → validate 104/104 + lint 0 warn + build 124 页 → merge main + llms 104 篇基线（c9e1b34）+ push gitea + deploy（1f10e3b4）+ 线上 200 + indexnow 200。**排版 html 本次新生成**（此前三份为预生成/复用）：`/Users/a77/公众号/激光雷达-公众号排版.html`（25.6KB），1:1 对齐 ASIC 模板样式（h2 蓝下划线/要点框/卡片框/数字标蓝/FAQ h3/延伸阅读 h3），核验全过：10 处核心数据计数 md=html、Q1-Q5 齐全、敏感词零命中、尾部要件 3/3；html 只落本机不进 git。明日 #33 superconductor。
- 2026-08-19 · devin · **一日一篇第 3 篇（ASIC芯片）全链上线**：`publish-queue.mjs` 推 #31 → `git checkout 9612923` 恢复 + redate 0819 → 通读修复正文硬伤（§六标题混入俄语词«второй»，批量质检漏网）→ validate 103/103 + lint 0 warn + build 123 页 → merge main（3fa75ef）+ llms 103 篇基线（128bcbc）+ push gitea + `wrangler deploy`（37369c81）+ 线上 200 已验 + indexnow 200。公众号排版 html（8/18 预生成）核验：12 个 h2 与 md 十节+FAQ 对齐、7 处核心数据计数全一致、敏感词零命中，直接复用未重生成。GitHub origin 仍 repository not found（预期，日常远程 gitea）。明日 #32 lidar。
- 2026-08-18 · devin · **一日一篇第 2 篇（钛合金）全链上线**：`publish-queue.mjs` 推 #30 → `git checkout 9612923` 恢复 + redate 0818 → validate/lint/build 全绿 → merge main（141e5f8）+ llms 102 篇基线（86e08e0）+ push gitea + `wrangler deploy` + indexnow(200)，线上 200 已验。vault 主 worktree 被 cursor 在途分支占用，回写走临时 worktree main 不干扰；明日 #31 asic-chip。
- 2026-08-14 · cursor · **0812-0813 批量 PR 集成收官 + 约定固化**：开放 PR 曾 131 个，128 个文章 PR（#29–#156）因人人携带 `public/llms*.txt` 无法逐个 merge。集成分支每 PR 只取 4 个独有文件（研究文 + 仓内素材包 + 公众号稿 + handoff），`npm run llms` 统一再生；#157 merge 进 main（228 篇文章）。存量 3 篇（lighthouse-factory / power-chip / thermal-materials）deepen 残留旧附录已去重。#158 上了 `pr-checks`（validate + 禁止 llms 入 PR）；首次 workflow 需 reopen 才触发，且必须显式 `permissions.pull-requests: read`。遗留 #15（wechat-adapt.mjs）关闭不采用——现行走 content-matrix 三件套、平台稿落点是仓内 `docs/content-matrix/` 而非脚本写的仓外目录。#1/#16 已关。约定 PR #159：工作流路径改 a77、`import-research` 认 RAW_DIR、禁止 `git add .`。可复用：共享生成文件不要进功能 PR；GitHub Actions 新仓第一次 `opened` 可能丢事件。
- 2026-08-13 · cursor-cloud · **主站文章批量撰写收官（B20-B44）+ 抽样质检**：raw 249 份 full 主稿全覆盖零遗漏——本轮新增 73 篇（PR #39-#156，每篇独立分支 cursor/research-<slug>-5451，未合 main、未跑 IndexNow）。每篇=主站 17 节文章+素材包+公众号 19 段稿，validate/lint/build 全绿，平台稿已同步 Mac。抽样质检修了 9 处硬伤（教学口令「这在 X 场景也能用」泄漏×4、钌 JM 供需表抄错、天然气发改委/统计局口径张冠李戴等）并回写进对应 PR。两个盘点纠错：超级电容 5 月已上线（误记待写，重复产物已弃）；推理芯片是唯一漏网稿（#156 补齐）。可复用方法论：先全量脚本扫+分层深读抽样；加粗数字三问（谁发布/哪年/实际还是预测）；映射稀缺赛道按「公告级别分级」（研发/送样/中试/量产）写；agent 教学口令必须进禁词表。合并提示：llms-full.txt 各分支均改，后合并者重跑 npm run llms。
- 2026-08-06 · codex · **industry7view 运维与曝光修复**：在 `fix/industry-article-quality`（commit `55edf4b`）删除 `lighthouse-factory`、`power-chip`、`thermal-materials` 的重复附录，合并保留独有相关研究链接，并同步生成 `public/llms-full.txt`；`npm run validate`、`npm run lint:articles:strict` 均通过（83/83），`npm run build` 通过（103 pages）。`public/robots.txt` 在分支上放开 GPTBot/ClaudeBot，继续拦截 CCBot/Bytespider；线上当前仍是旧版本，因 Worker 部署权限/流程未确认，未直接发布。Cloudflare 账户现有 token 可读 Pages 但不能读 Workers，`wrangler whoami` 未登录。仓库 main 当时落后 origin 24 commits 且有用户改动，未 pull/覆盖/合并；分支已推送。
- 2026-06-28 · devin · 初次建档（基于 README/AGENTS）
- 2026-07-02 · devin · 合并收尾：PR #11（thermal-materials 附录三件套去重）直接合并；PR #2（信息长图生成器 scripts/poster/，HBM 5 张 + 被动元件 4 张，chainmap 接题材雷达快照）先把 main 合进分支解 .gitignore 冲突（保留 .chrome-profile 忽略 + main 的 .agent-memory 行），本地 node 22 下 `npm run build`（105 页）与 `npm run validate`（85/85 严格）通过后合并。注意：本仓 Astro 要求 node >=22.12。
- 2026-07-02 · devin · 用户约定（重要）：**网站仓 main 只部署文章类改动**（src/content/research/ 等正文/修补），海报生成器等工具类功能不上 main、不部署。当日 PR #11/#2 合并后已按用户要求 revert（main 回滚到合并前，分支保留：fix/thermal-materials-dup-appendix、site/infographic-poster-generator，需要时可重开 PR）。
- 2026-07-06 · devin · add research: 华为芯片（huawei-chip）：走 import/enrich/deepen 管线，17 节+附录三件套、11 表、加粗数字带来源；lint 0 warn，node 22 下 npm run build 107 页通过。PR #13（research/huawei-chip → main），等用户确认合并；合并后需 npm run indexnow。sourceFile=华为芯片产业新格局深度研究报告：自主可控突破与供应链重构-full.md。
- 2026-07-06 · devin · 华为芯片收尾：PR #13 已合并 main，npm run indexnow 返回 200（含 huawei-chip URL）；另按 content-matrix 工作流产出三件套（内容矩阵/公众号/雪球 各目录下 华为芯片-*.md），敏感词检查全过。
