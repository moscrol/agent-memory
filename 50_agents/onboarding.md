---
title: 开场白 (接入任意新会话)
type: agent-card
agent: devin
source: 设计约定
date: 2026-08-12
tags: [agent-card, onboarding, bootstrap, core]
related: ["[[generic]]", "[[devin]]", "[[grok]]", "[[claude]]", "[[codex]]", "[[../30_conventions/preferences]]"]
---

# 开场白 — 让任意新会话立刻进入状态

复制对应版本粘到对话开头即可。先搞清一个关键区别 ↓

## 关键：agent 在「哪台机器」上读文件

- **Claude Code / Cursor**：跑在**你的 Mac 本机**、在 repo 目录里 → 能直接用 repo 内软链 `.agent-memory/`（软链只在 Mac 本地、已 gitignore）。
- **Devin**：它的**工作文件系统在自己的云端 VM**——会把 repo 单独 clone 到那台 VM，**那里没有 `.agent-memory` 软链**（软链没提交进仓库）。
  - 即使你用 `rx.py` 把 Devin「穿透」到 Mac，那也只是让 Devin **能远程在 Mac 上跑命令读到 vault**；Devin 真正编辑的 repo 仍在云端 VM 上。所以 Devin **不要假设工作目录里有 `.agent-memory/`**。
  - Devin 读 vault 的两条路：①（已配 rx.py 隧道时）远程读 Mac 的 `/Users/a77/agent-memory/...`；② GitHub 账号已暂停，PAT clone `linxiaoqi5111-del/agent-memory` **不可用**。在 Mac 本机改读 Gitea：`git clone http://127.0.0.1:3300/a77/agent-memory.git`。云端 VM 到不了 localhost，只能走① 或仓库内 `AGENTS.md` 内联偏好。
  - ⚠️ 注意：`rx.py` 文件和 `CC_REMOTE_EXEC_TOKEN`（org 级）**不随一次性 Devin 账号持久**；换新账号若还没重建隧道，就走②。而 **`AGENTS.md` 永远在仓库里**，顶部已内联核心偏好——这是 Devin 最稳的底线。

---

## ① Claude Code / Cursor（Mac 本机）

> Claude Code 自动读 `CLAUDE.md`、Codex 自动读 `AGENTS.md`，核心偏好通常已加载；下面这句用于点项目背景 + 兜底强化。

```
按本仓库 CLAUDE.md 的偏好来（中文、教学模式：讲原理+技术选型对比+标可复用点；Git：大任务开分支、合并 main 等我确认）。先读 .agent-memory/20_projects/<repo>.md 了解背景，然后做：<任务>。
```

## ② Devin（云端 VM）

```
先读本仓库 AGENTS.md，顶部「用户偏好（核心）」务必严格遵守：中文、教学模式（讲原理 + 给技术选型/替代方案对比 + 标注可复用知识点）。
需要完整偏好/项目背景时：① 若本会话已配 rx.py 隧道：python3 rx.py -- 'cat /Users/a77/agent-memory/30_conventions/preferences.md'（及 20_projects/<repo>.md）；② GitHub PAT clone 已不可用。在 Mac 上读本机 Gitea `http://127.0.0.1:3300/a77/agent-memory.git`，云端只靠① 或本仓 AGENTS.md 内联偏好。
Git：开工先报 git status --short && git branch --show-current；大任务开分支，合并 main 必须等我确认，不强推。
任务：<任务>。
完工后把关键结论/决策回写到 agent-memory 的 20_projects/<repo>.md（按 40_playbooks/devin-writeback.md 的步骤）。
```

## ③ Grok（读不到文件）

> 先粘下面这句，再把 `30_conventions/preferences.md` 全文贴进去。

```
以下是我的长期偏好与人设，本次对话请全程严格遵守（尤其"教学模式"：讲原理、给技术选型对比、标注可复用知识点、用中文）。读完确认后再开始：

<把 preferences.md 全文粘贴到这里>
```

## ④ 其他任何工具（云端 Cursor / 新 IDE / 没有具名卡）

> 不要套上面 ①——① 假定 Mac 本机软链存在。按 [[generic]] 执行：clone 本仓库，按卡上的读顺序逐条读，写入过 lint、受保护区走 PR。

## 备注
- `<repo>` 替换成实际短名（= `20_projects/<repo>.md` 文件名）：`finhot` / `finance-workspace-private` / `knowledge-base-private` / `finance-research-site` / `dao-proxy-pro` / `vidio`。
- 这些都是「软指令」：能强烈引导模型但非 100%，长对话跑偏时重贴一次即可。
