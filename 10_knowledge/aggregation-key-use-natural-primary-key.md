---
title: 聚合键必须用自然主键，且在聚合域内全局唯一
type: knowledge
agent: cursor
source: knowledge-base-private RAG P0（#305 page_id 消歧）
date: 2026-08-13
tags: [knowledge, methodology, identity, primary-key, rag, core]
status: verified
related: ["[[fast-path-must-not-mint-authority]]", "[[../20_projects/knowledge-base-private]]"]
---

# 聚合键必须用自然主键

按某键把多条记录合成一条时，**这个键必须在整个聚合域里唯一**。最稳的做法是直接用已经有唯一性约束的自然主键（文件系统路径、数据库主键、URL），而不是再发明一层「看起来唯一」的短名。

## 判据

改聚合键之前先问：**域内会不会有两条记录撞到同一个键？** 会，就不能用它做等值聚合。

短名（`path.stem`、文件名、slug）在单目录里唯一，跨目录/跨类型就不唯一。相对路径之所以够用，是因为文件系统本身禁止同一路径上放两个文件。

比「类型前缀 + 短名」更强一档的原因：嵌套子目录里同名文件，类型前缀仍会撞；完整相对路径不会。

## 连带风险

键一改，所有拿旧键做 `==` 的地方都会**静默失效**（排序、去重、优先队列、缓存 lookup）。改键时把等值比较扫一遍，不要只改写入侧。

兼容层可以把旧短名同时注册进解析表，但撞名时必须有**确定性**偏向（按固定目录顺序），不能「谁先出现算谁」。
