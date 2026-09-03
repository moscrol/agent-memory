---
title: run 级 id 进 prompt，请求就不可复现——分词噪声会伪装成「loop 差」
type: knowledge
agent: cursor
source: finance-workspace-private 2026-09-03 上午（PR #542：首轮 user 消息含 research_contract.task_id=run_<ts>:msg_<hex>，hex 分词随机差 2–4 token，两天里两次被读成两条 loop 的差；摘掉后同题首轮 13658==13658）。上午交接建议入库、本条补写
date: 2026-09-03
tags: [knowledge, agent, prompt, reproducibility, eval, failure-shape]
status: verified
related: ["[[eval-harness-variance-governance]]", "[[info-not-delivered-bug-pattern]]", "[[../20_projects/finance-workspace-private]]"]
---

# run 级 id 进 prompt，请求就不可复现

> **失败形状**：某个只对**这一次运行**有意义的标识（run_id、消息 id、时间戳、随机 hex）被序列化进了模型看到的 prompt。
> 模型用不上它、协议也不解析它，但它让**同一道题的两次请求字节不同**：token 数随机抖动、缓存命中率归零，
> 而做 A/B 的人把这几 token 的差读成了两条实现的差。

## 怎么认

- 两臂 / 两次的首轮 `input_tokens` 差一个很小的整数（2–4），且每次不一样。
- diff 两份渲染后的 prompt，唯一不同的是一段十六进制或时间戳。
- 有人已经在为它「放宽容差」（±3 → ±8）——那是在给噪声让路。

## 修法

- **摘掉**：模型不需要的 id 不进 prompt；需要关联就放到产物/trace 里，不放到模型输入里。
- 摘掉之后，「请求逐字节稳定」本身成为一条可测的性质：同题两次渲染的 prompt 字节相等（finance 的 ±3 硬门在 #542 之后才开始量真差）。
- 不要放宽容差：容差是给真实噪声底留的（见 [[eval-harness-variance-governance]]），不是给可消除的确定性差留的。

## 顺带的收益

请求稳定 → provider 侧前缀缓存能命中；A/B 的 token 差回到 0，读数里少一个混杂变量。
