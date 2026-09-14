---
title: 分片存的状态对同题并行轨不可见，而唯一的全局索引会被预算静默砍掉
type: knowledge
agent: claude
source: finance-workspace-private 会话 2026-09-15（judge-calibration-validity 同题双轨，Task 1 被重做一遍）
date: 2026-09-15
tags: [knowledge, methodology, handoff, memory, injection-budget, parallel-work, core]
status: verified
related: ["[[workorders-index-is-a-hot-file-scan-branches-before-numbering]]", "[[../20_projects/finance-workspace-private]]"]
---

# 分片存的状态对同题并行轨不可见

## 实测到的形状

同一份 plan（`docs/superpowers/plans/2026-09-14-judge-calibration-validity.md`）被两条轨各实施了一遍：

| 轨 | 进度 | 交接 |
|---|---|---|
| `codex/judge-calibration-validity` | Task 1–5 完成，全量 9766/0，四门反证 | 有 |
| `feat/judge-calibration-validity` | Task 1 + Task 2 上半，还在问「三处待裁决」 | 无 |

两边**各自独立新建了同一个文件** `intelligence/eval/judge_validity.py`（540 行 vs 614 行），
设计还不同构。后一条轨的 agent 全程不知道前一条存在。

## 为什么没被发现——两道通道各自失效

**通道一：inflight 按分支名索引，这是设计。**
`session_facts.sh` 找的是 `docs/handoffs/inflight/<当前分支>.md`。
codex 那份叫 `codex-judge-calibration-validity.md`，feat 轨找 `feat-...md` ——
名字不匹配，hook **如实**报「本分支无」。hook 没坏，它就不是设计来跨分支看的。

**通道二：唯一的跨分支索引被预算截断，且截断不报错。**
项目笔记「交接记录」是唯一能看见「同题已有人做」的地方。那条索引确实写了（第 162 行），
但 SessionStart 注入自报：

```
必读段被预算截断（注入 5713 / 必读段 16423 / 全文 371741 字节）
```

注入止于「## 任务看板」表头——**交接记录段在被砍的 10710 字节里**。
截断只报字节数，不报**砍掉了哪些类别**，所以读的人不知道自己缺的正是这一段。

## 可迁移的判断

换任何项目都成立：**只要状态按某个键分片存（branch / session / user / tenant），
分片之间就互不可见；此时唯一的全局索引是单点，而"按预算截断"是它最安静的失效方式。**

三条做法：

1. **截断要报类别，不只报字节。** 「砍了 10710 字节」读不出信息；
   「砍掉了：交接记录(14 条)、任务看板」能让人自己去补读。
   `inflight` 自己已经做对了这件事——它按 `## ` 切段、把回顾性小节挪到末尾优先砍。
   上层的项目笔记注入没有这个逻辑。
2. **开工前对同题做一次全分支扫描**，别只信本分支注入。
   一条命令：`git branch -a --list '*<关键词>*'` + `git worktree list`。
   同样的纪律在取号场景已经踩过一次（见 related）。
3. **判断"是不是没人做过"属于负面断言**，适用断言纪律：全树 grep 同义词 + 读能力图谱
   + 读项目笔记任务看板，三样都做过才能说。本例里只要做了第一样就能避免整轮重做。

## 不要做的

**不要为此把 inflight 改成全局共享。** 它按分支私有是对的——接手者要的是「这个分支卡在哪」，
混进别的分支会淹掉。要修的是**索引层的截断可见性**和**开工时的扫描纪律**，不是分片本身。
