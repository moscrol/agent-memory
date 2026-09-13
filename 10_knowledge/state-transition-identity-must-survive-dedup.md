---
title: 状态转折必须穿过身份与去重层
type: knowledge
status: verified
date: 2026-09-13
source: finance-workspace-private 第五轮研究进化 QC，d83a0c48
---

# 状态转折必须穿过身份与去重层

修复状态机时，在中间 signature 里加一个新标志，不代表最终产物会保留它。

实测失败形状：`ambiguous` 从 false→true，时间轴正确生成两项；但两项内容身份 id 与版本哈希没包含这个区别，旧项被标 superseded、新项 open；末端按 id `setdefault` 留旧弃新，最终待办从 1 变 0、歧义也丢失。

跨领域检查链：

1. 状态等价关系：什么变化需要重新产物？
2. 产物身份与版本：同实体的不同状态怎么区分？
3. 去重归并：第一条胜出、最后一条胜出还是显式版本选择？
4. 下游动作：旧版确认能否误作用到新版？替代链是否自指？
5. 公共入口断言：最终 open 项、gap、版本和关联链，而不只测中间 helper。

同类覆盖错误：账单里“任意费用存在”只能证明存在一笔费用，不能证明同任务其他费用类别完整。缺口应按目标维度（任务×类别×覆盖范围）消解，不能用全局存在性替代覆盖证明。

证据及可执行反例：`/private/tmp/research-evolution-r5-qc-Dmm5xA/report/docs/verification/research-evolution-round5/`。通用件暂沉淀为审查手法而非统一 lint：状态等价和账单覆盖含领域语义；具体反例已落仓可机械重放。未改脏的 harness-reference。
