---
title: 合并冲突「两边都保」的判据：两边改的是不是同一个事实的不同侧面
type: knowledge
agent: claude
source: finance-workspace-private `codex/judge-calibration-validity` 并 `gitea/main` 2026-09-16（`llm_refine.py` / `grok_cli_judge.py` 两处冲突）
date: 2026-09-16
tags: [knowledge, methodology, merge-conflict, ledger, single-source-of-truth, core]
status: verified
related: ["[[../20_projects/finance-workspace-private]]", "[[gate-covers-only-its-return-value]]", "[[pitch-materials-need-one-spine-cross-count-detects-drift]]"]
---

# 合并冲突「两边都保」的判据

两条分支在**同一个数据结构上各加各的字段**时，冲突标记只告诉你「这几行打架」，不告诉你
该合还是该选。默认动作有三种，两种是错的：

1. 选一边 —— 丢掉另一边已经验收过的能力。
2. 各留各的（新开一个并行结构 / 第二本账） —— 冲突消失了，**代价推迟到运行期**。
3. 合成一条 —— 只有当两边描述的是**同一个事实的不同侧面**时才对。

## 判据：它们会不会被同一个人在同一时刻一起问

现场：主干给 `LLMCallRecord` 加了 **token 计费**（这次调用花了多少），分支给同一个结构加了
**调用身份证据**（这次调用是谁应答的）。看起来是两件事，但「这一轮花了多少 / 是谁给的答案」
永远是同一次对账里的两列——**分开记，第一次追账就要做跨表 join，而 join 键正是最容易错的那个**。

所以：合成一条记录，`input_tokens` / `output_tokens` / `usage_source` 与身份字段并存，
注释写明 `None` 表示**未上报**而不是 0。没有新开第二本账本。

反过来，如果两边加的是「这次调用花了多少」和「这个用户本月的套餐档位」，那就不是同一个事实
的两侧——后者不随每次调用变化，合进去会让每条记录都带一份会漂的副本。

## 推论一：合完要检查投影出口有没有变成两个

合并常见的副作用是**一份数据、两个序列化函数**（两边各带来一个）。这次两边各有
`_call_record_snapshot` 与另一套字段裁剪，留着就是两个出口各自演化。收口成唯一的
`_record_to_dict`，让 `records_for_call()` 与 `summary()` 共用，并加断言钉住
`summary()["records"] == [record]`。

这条不是洁癖。同仓早有实证：**一份覆盖率台账两个渲染出口**，一个用 `scored is True`、
一个用 `_score_is_numeric`，平时读数一样，遇到 `scored=True` 但总分非有限数就劈开——
人读报告写「已评分 4」、JSON 收据写 `scored=3`。谁先看到哪个出口，谁就得到不同的事实。

## 推论二：保契约优先于保类名

分支侧有个 `GrokCliResponse` 专门装身份元数据，主干侧的返回类型是 `GrokCliText`——一个
**`str` 子类**，全仓的测试替身、`json.loads(content)`、三元组解包都建立在「它还是个 str」上。
解法是把元数据并进 `GrokCliText`、删掉 `GrokCliResponse`：**被广泛依赖的是契约（还是 str），
不是哪个类名活下来**。

## 推论三：解冲突不发明新行为，验收要分别打红

解冲突时只做「两边意图的并集」，不顺手改语义。验收也要**按意图分别反证**：把服务层的身份
状态误标成已上报 → 未上报那组用例转红；把评测层的常量拼错 → 已上报那组不再合格。两次各 3 红、
还原后全绿，才说明这条合并记录的两侧都真的被读、被检查。

## 一个自测陷阱

新写的跨层测试最初 4 项失败，原因是**把 CLI 用例接到了只处理 HTTP 的入口**。
先归因到自己的测试，改测试入口；**没有为了让测试变绿去动生产路由**。
测试红了先问「我是不是问错了对象」，再问「代码是不是错了」。
