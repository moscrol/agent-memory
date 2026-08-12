---
title: 断言纪律（负面断言的三步验证）
type: convention
agent: claude
source: 2026-08-04 实测教训；2026-08-12 从 scripts/hooks/session-context.sh 提升为约定——此前纪律正文只活在 Mac 的 hook 脚本里，云端 agent 读不到，违反 SSOT
date: 2026-08-12
tags: [convention, assertion, evidence, core]
related: ["[[frontmatter-spec]]", "[[trust-boundary]]", "[[../10_knowledge/finance-agent-capability-graph]]"]
status: verified
---

# 断言纪律（强制）

**「我们没有 X」/「X 还没做」是负面断言，grep 一个文件搜不到证明不了它。**

说这句话之前三样都做，并在结论里写明查过哪些：

1. 全树 `grep` 同义词（不是只搜一个你猜的文件）
2. 读能力图谱 `10_knowledge/finance-agent-capability-graph.md`——回答「有没有 X」的权威事实源；改能力后回写它，**不要另建第二份能力清单**，第二事实源会让下一个 agent 读到过期那份
3. 读对应项目笔记（`20_projects/<repo>.md`）的任务看板与交接记录

同理，**提议「建一份 X」之前先搜 X 存不存在**。

标注证据等级：**[实测]**（跑过/读过代码）/ **[推断]**（推理得出）。
把推断说成事实，是这类错误的共同外壳。

这类问题**先问用户比先搜快**——「我们有没有编排层」用户两秒能答。

> 起源：2026-08-04 会话起在非 repo 目录、项目级 hook 未加载，连续三次把「已有能力」和「刻意约束」误判成缺口。本文正文是 SSOT；`scripts/hooks/session-context.sh` 只负责把它注入 Mac 本机会话，云端 agent 直接读本文件。
