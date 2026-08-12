---
title: 快路径只能加速权威答案，不能自己产生权威答案
type: knowledge
agent: cursor
source: knowledge-base-private RAG P0（#305 freshness 单一事实源）
date: 2026-08-13
tags: [knowledge, methodology, cache, freshness, source-of-truth, core]
status: verified
related: ["[[aggregation-key-use-natural-primary-key]]", "[[../20_projects/knowledge-base-private]]"]
---

# 快路径只能加速权威答案

缓存、预检、git diff、CDN、DNS TTL、CPU cache 都是同一件事：**一条便宜的路径，用来加速一条更贵但语义正确的路径。**

设计约束是**单向短路**：快路径只被允许证明「没变 / 仍有效」，从而跳过权威计算。任何一条证明不了，必须落回权威口径。快路径**不得**单独宣布「变了」或「没变」作为最终答案——否则两套口径会互相唱反调。

## 对照

| 做法 | 便宜在哪 | 看不见什么 |
|------|----------|------------|
| mtime | 只读时间戳 | 改名、回滚、内容相同的 touch |
| git tree/diff | 不读文件字节 | gitignore 文件、跨机拉来的副本对不上 revision |
| 内容哈希 / manifest | 最贵 | 几乎没有——描述的就是这些字节 |

最终结构 = **权威口径（哈希/字节）+ 快路径短路（git/mtime）**。两头兼得的前提是：快路径失败时必须降级，而不是改判。
