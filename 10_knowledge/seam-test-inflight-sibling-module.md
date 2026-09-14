---
title: 并行轨道联测：上游模块未合入时，用 PYTHONPATH 跨 worktree 跑真函数产出样本
type: knowledge
date: 2026-09-13
tags: [seam, contract, worktree, fixtures, parallel-agents]
status: verified
source: finance-workspace-private feat/research-priority（研究进化 02 消费 01）
---

# 并行轨道联测：别等上游定稿

## 失败形状

多 agent 并行各写一轨，消费方按 spec 手写「合同夹具」开发，等上游合入 main 再联测。
手写夹具与上游真实现的字段形态天然一致的概率不高——2026-09-13 实测三处差异：`knowledge_cutoff` spec 写时刻、上游实现是**日期**；`condition_result` 是字符串 `"true"/"false"/"unknown"` 而非布尔；item 多出四个 spec 未列的键。
差异等到合入后才红，那时两边都定稿，改哪边都要重开分支。

## 做法

1. `git worktree list` 找上游轨的树；`ls <树>/intelligence/services/<包>/` 看它有没有可跑的入口和自带夹具。
2. 只读、子进程、不 import 进自己进程：
   `cd <上游树> && PYTHONPATH=<上游树> <主树 venv python> -B -c "from … import assess; …; json.dump(report.to_dict(), …)"`
3. 在自己的树里把产物喂给自己的适配层；能零改动通过就冻结为夹具，`_provenance` 记录上游每个文件的 sha256 前缀（运行前列出的那组；上游可能一分钟内又改）。
4. BLOCKED 写「上游定稿后用最终 revision 重跑替换」的完整命令；定稿后若测试红，先怀疑上游改了枚举 / 键名，改自己的适配表，不改测试期望。

## 判据

- 消费方的合同层要按「宽进」写：日期与时刻都收、字符串枚举归一、忽略未知键——这样上游真产物才可能零改动通过；严进只会把差异推迟到联测。
- 冻结产物必须标 synthetic（输入是合成的），不得据此宣称任何用户效果。

相关：`intelligence/tests/fixtures/research_evolution/02/from_01_inflight_assess_report_synthetic.json`；待写 `checker-producer-contract-is-where-the-bugs-live` —— 2026-09-14 核：该名在 git 全 history 里从未存在过，是作者预留的坑位而非改名，写出来后改回双链。
