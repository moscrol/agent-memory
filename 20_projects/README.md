---
title: 项目总览
type: project
agent: claude
source: 仓库盘点；2026-08-12 收编 dao-proxy-pro / vidio（此前表只列 4 个金融仓，与 20_projects/ 实际 6 份笔记不一致）
date: 2026-08-12
tags: [project, index, moc]
---

# 项目总览 (Projects MOC)

当前纳入记忆底座的项目（均为 `linxiaoqi5111-del` 名下仓库）。笔记文件名 = 仓库短名（`git remote` basename），preflight / SessionStart 按这个名字找文件。

| 项目 | 仓库 | 定位 | 技术栈 |
|---|---|---|---|
| [[finhot]] | finhot (public) | 金融 RSS 信息流阅读器 | Electron + React + TS |
| [[finance-workspace-private\|金融项目]] | finance-workspace-private | A股量化复盘+研究工具集 | Python + DuckDB + 飞书 |
| [[knowledge-base-private\|知识库]] | knowledge-base-private | LLM 维护的金融知识图谱/Wiki | Python + RAG |
| [[finance-research-site\|金融网站]] | finance-research-site | 面向读者+AI检索的研究网站 | Astro + Cloudflare |
| [[dao-proxy-pro]] | dao-proxy-pro | 本地 LLM 网关（多协议路由/缓存/熔断） | Node/JS · VS Code 扩展 |
| [[vidio]] | vidio | 抖音冷启动与内容获客（FinHot + 金融 Agent） | 运营为主 · Remotion 成片 |

## 金融内容矩阵（它们怎么串起来）
```
knowledge-base-private  ──(知识/synthesis)──►  finance-research-site (对外研究文章)
        ▲
        │ ingest/RAG
finance-workspace-private (量化复盘/数据)              finhot (信息流阅读器/采集)
```

另两份不在这条内容链上：`dao-proxy-pro` 是各 agent 共用的本地推理基建；`vidio` 是获客运营，项目 SSOT 在仓内 `ops/`，本 vault 只留 MOC。

> 每个项目的任务看板、关键决策、交接记录都在各自的 MOC 里维护。新项目按 `_templates/project.md` 新建，文件名必须等于仓库短名。
