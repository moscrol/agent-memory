---
title: 两步到达的页面——首批非空不是终态，三态状态码对「内容错」盲
type: knowledge
agent: cursor
source: finance-workspace-private 2026-09-03 实测（web_search 经 CDP 代理抓 Bing：每次拿的都是 JCache 实体缓存壳，status=success；PR #553；收据 docs/verification/2026-09-03-web-search-bing-rdr-shell.md）
date: 2026-09-03
tags: [knowledge, agent, failure-shape, scraping, observability, tools]
status: verified
related: ["[[info-not-delivered-bug-pattern]]", "[[contract-vs-delivery-mismatch]]", "[[../20_projects/finance-workspace-private]]"]
---

# 两步到达的页面：首批非空不是终态

> **失败形状**：一个抓取器以「目标元素出现且非空」为收工判据。页面却分两步到达——
> 第一步是缓存壳 / 骨架 / 上一个实体的占位（`readyState=complete`、元素齐全、内容对不上），
> 第二步才是真结果（往往由页面自己的 JS 重定向或二次渲染触发）。抓取器每次都在第一步收工，
> 返回 `status=success`，内容全错，**没有任何状态码会变红**。

## 为什么活得久

- `ProviderTrace` 那类 success / empty / error 三态量的是「有没有拿到东西」，不量「拿到的对不对」。
  内容错是三态之外的第四种状态，需要语义判断，门禁本来就不打算量它。
- 下游是模型：它拿到五条无关 snippet 会写「未找到相关网页」——一句看起来合理的诚实弃权，把上游故障洗成了「网上没有」。
- 该工具此前零 live 调用（茅台题两臂九次调用零次 web），没人看过它的输出。**零调用的工具等于没测过。**

## 判据怎么定（可迁移）

1. **找页面自己的「到达」信号**，而不是「元素非空」：Bing 是 `location.href` 里出现 `rdr=1`；别处可能是 URL 参数、某个 marker 节点、
   `performance` 里的第二次导航。先逐 0.1–0.3s 采样把两步的时间线画出来再定，不猜。
2. **信号缺席时要有兜底**：会话跑热后 Bing 不再重定向、首屏即真结果——只认信号会永远超时。
   兜底用「结果连续稳定 N 秒」，N 按采样到的最大跳转延迟留余量（本例 0.9–2.1s → 3.0s）。
3. **把走的哪条路径写进产物**（`settled after rdr redirect` / `no rdr redirect; results stable` / `unsettled`）：
   下一次读数才知道兜底有没有被用到、`unsettled` 是不是在变多。
4. 排除假线索：本例先怀疑 `HeadlessChrome` UA、改了 Chrome 启动参数——壳的内容变了、机制没变。**UA/指纹改变能改「给你哪种壳」，
   改不了「先给壳」。** 归因写「不明」，不写「UA 修好了」。

## 一句话纪律

跑任何 live 实验之前，**先直调链路上最便宜的那一环、看内容不看状态码**——本例一次 3 秒的直调省下的是两臂各三分钟外加一份被壳主导、
读不出任何东西的读数。
