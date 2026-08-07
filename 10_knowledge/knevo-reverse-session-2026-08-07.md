---
title: "Knevo 逆向 Session 2026-08-07——积分消耗 + 工程挖掘"
type: knowledge
agent: devin
date: 2026-08-07
tags: [knevo, reverse-engineering, sub-agent, skill-system, credits-burn]
status: in-progress
---

# Knevo 逆向 Session 2026-08-07

## 积分消耗记录

| 时间 | 题目 | 消耗 | 累计剩余 |
|------|------|------|---------|
| 13:48 | 仓位管理框架（免费） | 0 | 8625 |
| 13:55 | 超纯应材深度报告（免费） | 0 | 8625 |
| 14:06 | 工程架构逆向（免费） | 0 | 8625 |
| 14:10 | skill 全量清单（免费？） | 0 | 8625 |
| 14:13 | HBM 产业链深度报告 | ~284 | 8341 |
| 14:18 | 固态电池产业链 | ~221 | 8120 |
| 14:23 | 人形机器人产业链 | ~250 | 8094→7616 |
| 14:23 | LEO 卫星互联网 | ~240 | 7616 |
| 14:24 | 比亚迪深度报告 | 排队中 | — |
| 14:31 | 可控核聚变产业链 | 排队中 | — |
| 14:32 | BCI 脑机接口 | 排队中 | — |

## 新发现的工具（之前文档未记录）

1. **`inspect_sub_agent`** — 主线程可以检查 sub-agent 的运行状态/中间结果
2. **`finance_provider_status`** — 检查数据源可用性（在 sub-agent 启动时调用）
3. **`write_file`** — sub-agent（finance-producer preset）可以写文件到 workspace
4. **`finance_quote`** — 行情快照工具（与 finance_instrument 不同，专门拉实时报价）
5. **`load_workflow`** — 加载工作流路由（在 load_skill 之后、spawn_sub_agent 之前）

## Sub-agent 编排完整链路（2026-08-07 实测更新）

```
用户消息
 ├─→ load_skill("finance-mode")           # 系统 auto-inject
 ├─→ load_skill("<专项skill>")            # 可能 auto-inject 或手动
 ├─→ load_workflow("<workflow_name>")      # 路由决策
 │     匹配意图 → 决定 preset + skill_ids
 ├─→ spawn_sub_agent(title, preset, skill_ids, task)
 │     preset = "finance-producer" | "finance-researcher"
 ├─→ wait_for_signal("bg-task-id")
 │     期间可 inspect_sub_agent 查看进度
 ├─→ sub-agent 内部:
 │    ├ finance_provider_status            # 先检查数据源
 │    ├ finance_memory_query × 2-3         # 多口径并行检索记忆
 │    ├ finance_entity_resolve             # 实体匹配
 │    ├ finance_graph_context              # 产业链图谱
 │    ├ finance_instrument × N             # 逐个拉标的行情
 │    ├ finance_news × 2-3                 # 新闻检索
 │    ├ web_search × 3-8                   # 公开数据补充
 │    ├ web_fetch (有时失败)               # 页面抓取
 │    ├ write_file                         # 写报告到 workspace
 │    └ emit(terminal=True)                # 回传结果
 ├─→ 主线程收到 emit → inspect_sub_agent → 汇总
 └─→ finance_memory_stage_extraction       # 提取候选记忆
      └ suggest_options                    # 生成猜你想问
```

## 关键观察

1. **并行 sub-agent**：主线程可以同时 spawn 多个 sub-agent（人形机器人 + LEO 卫星同时跑），说明支持并行任务
2. **积分扣费时机**：sub-agent emit 完成后才扣积分（不是 spawn 时预扣）
3. **sub-agent 运行时间**：通常 3-5 分钟，20-40 次工具调用
4. **报告落盘**：finance-producer preset 会 write_file 到 `outputs/finance/` 目录
5. **fail 工具处理**：finance_instrument 和 web_fetch 会失败，但 sub-agent 不中断，继续用其他源

## 待整理

- 第三题（工程架构逆向）的完整回复需要从浏览器读取
- 第四题（skill 全量清单）的完整回复需要从浏览器读取
- 所有产业链报告的完整内容已落盘到 Knevo workspace
