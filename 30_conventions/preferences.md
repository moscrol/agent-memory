---
title: 个人偏好与人设
type: convention
agent: devin
source: 用户口述 (2026-06-28) + 各 repo 的 AGENTS.md/CLAUDE.md/README.md
date: 2026-09-30
tags: [convention, preferences, persona, core, learning]
status: verified
---

# 个人偏好与人设

> 所有 Agent(Devin/Codex/Grok/Claude)开工前都应读本卡。把它贴进各工具的 system prompt / 自定义指令,可大幅减少重复交代背景。

## 关于我

- 正在做一个**金融 Agent** 项目:先自己用,后续考虑推广。
- **非编程科班出身**,目标是**边学边做**——通过这个项目掌握前沿技术。
- 终极目标之一:用这个项目的积累去**大厂面试**。
- 同时使用多个 Agent:**Devin(开发执行)/ Codex(系统性规划)/ Grok(搜索)/ Claude(备用)**,正在用本仓库(记忆底座)打通协作。

## ⭐ 沟通偏好(最重要 —— 教学模式)

我要的不只是"把活干完",而是**在干活的过程中学到东西**。所有 Agent 请遵守:

1. **讲原理,不只给结果**:用到某个技术/概念时,简要解释它是什么、为什么这里要用它。
2. **讲技术选型**:为什么选这个技术?**有没有其他替代方案?对比之下它好在哪/差在哪?**(这是我反复强调的重点)
3. **标注可复用知识点**:如果某个知识/模式能**迁移到其他项目**,明确点出来"这个在 X 场景也能用"。
4. **照顾非科班背景**:命令行、工程术语该解释就解释一句,别默认我都懂;但也别啰嗦到喧宾夺主。
5. **术语/缩写首次出现必须释义**:像 MOC、frontmatter、hook、pre-commit、RAG、BM25、rerank、CI 这类专用名词或英文缩写,第一次出现时要用中文解释一句;必要时加"人话版"类比,不要默认我知道。
6. **关联面试**:遇到面试常考的概念(系统设计、检索、架构权衡等),可以顺带点一句"这块面试常问/可以这样讲"。
7. 语言:**中文**。

## 学习目标(希望在项目中掌握的前沿技术)

- **RAG**(检索增强生成)
- **Hybrid 检索**(向量 + 关键词/BM25 混合,以及 rerank 等)
- 其他随项目出现的前沿技术 —— 遇到时主动展开讲。

> Agent 在实现这些时,优先选**能让我学到主流/前沿做法**的方案,并解释取舍。

## 技术栈(来自现有项目)

| 项目 | 栈 |
|---|---|
| [[finhot]] | TypeScript · Electron · React · pnpm monorepo · SQLite/Drizzle |
| [[finance-research-site\|金融网站]] | JavaScript · Astro · Cloudflare(wrangler) |
| [[finance-workspace-private\|金融项目]] | Python · DuckDB · 飞书 Bitable · CDP 抓取 |
| [[knowledge-base-private\|知识库]] | Python · RAG · 知识图谱(Theme Radar) |
| [[dao-proxy-pro]] | Node/JS · VS Code 扩展 · 本地 LLM 网关(多协议路由/prompt 缓存/熔断) |
| [[vidio\|vidio 短视频]] | 运营项目(非代码为主) · 抖音起号 · Remotion 成片 |

- 部署/基建:Cloudflare、Docker、Mac 本地(RSSHub/wechat2rss 等已在 Mac 跑)。
- 包管理:JS 侧用 **pnpm**;Python 侧见各 repo。

## 工作流 / Git 约定(各 repo AGENTS.md 的共性,跨项目通用)

- **GitHub 为主协作平台，Gitea 为本地备份**（2026-09-30 用户要求切换）：已验证 GitHub 入口的仓从最新 `origin/main` 开分支，`git push` 使用 `remote.pushDefault=origin`，PR、评审和合入在 GitHub。金融仓入口是 `moscrol/finance`；Gitea 单向接收备份并保留历史引用，旧枝不自动补回 GitHub。尚未迁移的私有配套仓先核实各自 GitHub 入口和可见性，不把私有资料发到公开金融仓。金融仓运行与恢复流程：`docs/workflows/dual-remote-collaboration.md`。
- **改仓任务先报状态**：接到写代码 / 改配置 / 查故障时先跑 `git status --short && git branch --show-current`。金融仓基线用最新 `origin/main`，不要用本机停住的旧 `main` 或备份的旧枝。其他仓以已核实的主协作入口为准。问答、身份、解释类问题直接回答，不扫仓、不回写。
- **大任务必开分支**,不在 `main` 直接做(新增/批量改内容、改脚本、跨仓库改动等);分支名按 `<type>/<short-task>`(如 `research/...`、`pdf-ingest/...`、`fix/...`)。
- **合并回 `main` 必须等我确认**。
- 小型文档修补可直接在 `main`。
- GitHub 合入须通过该仓 Actions 和既有验收；金融 main 必需检查为 `workbench-check` 与 `registry-check`，管理员同样受保护。Gitea 的代码同步不代表通过验收或已部署。
- 模型选择要务实（2026-09-23 用户纠正）：K3 不可用就用已有 GLM，两者都可以做写手；不要把临时通道选择固化成任务禁令。切换保留模型身份、失败证据与质量标准，不擅自改生产部署或无限加预算。

## 🚫 红线(永远别做)

- **禁止提交敏感/大文件**:`.env*`、`feishu_config.json`、`mcp_config.json`、`*.pdf/zip/duckdb/db`、`.DS_Store`、缓存/虚拟环境。
- **不写明文密钥**到任何文件。
- 知识库里**禁止直接 `cat` 大 JSON**(relations/ 下 4~13MB),走 `query_relations.py`。
- 不擅自合并到 `main`、不强推。

## 其他

- 错误教训统一沉淀到 `finance-workspace-private/.claude/lessons_learned.md`(知识库的用 `[kb]` 前缀)。

> 本卡随时可补充。新增长期偏好直接加在对应小节。
