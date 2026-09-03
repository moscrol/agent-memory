---
title: 墙钟推导值不进逐字比较——「同一台机器」断言里的伪差
type: knowledge
agent: cursor
source: finance-workspace-private 2026-09-03 实测（test_tool_hidden_for_too_small_window_is_the_same_machine 在 gitea/main 干净树 6/6 红，would_grant 14.999 vs 15.0；同一用例在另一棵树的整仓跑里又是绿的；PR #551）
date: 2026-09-03
tags: [knowledge, testing, flaky, failure-shape]
status: verified
related: ["[[eval-harness-variance-governance]]", "[[../20_projects/finance-workspace-private]]"]
---

# 墙钟推导值不进逐字比较

> **失败形状**：断言「两条实现产出相同结构」时，把一个由 `time.monotonic()` 推导出来的量
> （剩余秒数、授予窗、`round(…, 3)` 后的秒）放进了逐字相等的字典比较。两条实现各建一个
> deadline、各走几毫秒到读数点，`15.0` 对 `14.999` 就红了；机器快一点又绿。**红绿由负载决定，
> 不由代码决定**，而它长得像一条确定性失败。

## 怎么认

- 差值只在最后一位小数，且两边的其它键全等。
- 同一提交、同一环境，连跑数次全红，换一台/换一次整仓跑又绿——「6/6 红」也不等于确定性红，
  只等于「这台机器此刻稳定慢了那零点几毫秒」。
- 用例名或注释里写着「同一台机器 / byte-for-byte」——它的本意是**裁决结构**相同，不是时钟相同。

## 修法（只改测试，不碰运行时）

- 把裁决键（谁可见、谁被藏、门槛、原因）保留逐字相等；把墙钟推导的那个键**单独按容差比**
  （本例 `|Δ| < 0.05s`），并断言事件条数一致，别让容差变成漏洞。
- 不要为了它冻结全局 `time.monotonic`：会波及被测代码里所有计时逻辑，修一个伪差引入一片假绿。
- 也不要「去掉那个键」：容差比仍能抓到 15 对 30 这种真差（一边用了 reserve 一边没用）。

## 门禁侧的启示

红集要按 **id 集合**比，不按计数比：这条红把整仓从 5F 变 6F，只看数字会以为「又多了一条环境红」，
看 id 才知道换了一条、且是新的。（finance `scripts/run_main_gate.sh --baseline` 就是为此按 `failed_ids` 比。）
