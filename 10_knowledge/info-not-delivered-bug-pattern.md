---
title: 信息没送到——先问「它看没看到」，再问「它为什么没用」
type: knowledge
agent: cursor
source: finance-workspace-private 实测五例（2026-08-01 反面样本 / 08-08 memory_lookup 未注册 / 08-12 三字段记了没传 / 08-21 预取证据丢号 / 09-02 授权表与生效模型不落盘），此前被 finance 三份文档与本 vault MOC 以本文件名引用而无正文
date: 2026-09-03
tags: [knowledge, agent, failure-shape, observability, debugging, core]
status: verified
related: ["[[contract-vs-delivery-mismatch]]", "[[misaligned-field-looks-plausible]]", "[[mutation-test-before-claiming-silent]]", "[[../20_projects/finance-workspace-private]]"]
---

# 信息没送到

> **失败形状**：某份信息在系统里**存在**（注册表里、遥测里、配置里、日志里），
> 但从未抵达会用它的那个消费者（模型的 prompt、判官的 payload、门禁的输入）。
> 排查者看见它「存在」，就把「没被用」解释成消费者的选择或能力问题，
> 得出几条自洽而全错的结论。

与 [[contract-vs-delivery-mismatch]] 的关系：契约不符问「承诺 vs 交付」；本条只问一件更前置的事——
**消费者的输入面上到底有没有这份信息**。多数契约不符案例走到最后都是这一问。

## 排查顺序（只有这一条纪律）

1. **它看没看到？** 把消费者**实际收到的输入**打出来（渲染后的 prompt 字节、注册表快照、
   工具菜单、判官 payload），在里面找这份信息。不要读代码推断「应该传了」。
2. 看到了，再问 **它为什么没用**。跳过第一问直接答第二问，是本条所有实例的共同起点。
3. 反向也成立：**先证明这份信息真能回答那个问题，再说它「没送到」**——送到也没用的东西，
   送到了也不是修复。

## 实例（finance 2026-08 → 09，按发现顺序）

| 日期 | 表面结论 | 实际 | 四种子形状 |
|---|---|---|---|
| 08-01 | 「做暴露选择器时没用 mention_frequency → 又一次信息没送到」 | **撤回**：粒度错（题材间 vs 题材内）、覆盖 2.6%、目标题材缺失——**送到也没用** | 反面样本 |
| 08-08 | 「模型有 `memory_lookup` 但没选」「预算竞争挤掉了」「required=False 给了跳过理由」 | 工具**压根没注册**，模型看不见；三条解释共同前提不成立。真修复是把 user 身份穿透到注册链，不是那行 prompt 指引 | ① 没注册 / 没授权 |
| 08-12 | 「遥测里 `tel.degraded` / `recall_desc` / `fallback_reason` 都记了」 | 记了，**从没往模型传**；七例契约不符里三例是这个形状 → 门禁 `scripts/check_unread_fields.py` 由此而生 | ② 记了没传 |
| 08-21 | 「预取事实进了证据账本，稳拿 E1/E2」 | 渲染开场消息只拼 `title + detail`，**号丢了**；模型如实写「无证据序号」，判官按「数字要有 evidence_id」把真话删掉 | ③ 传了没把手 |
| 09-02 | 「产物里有 `tool_set`，能看出模型用了什么工具」 | 产物没记**授权了哪些**，分不清「授权但没选」与「压根没授权」；`model` 字段是 `providers[0].model` **配置值**，响应体的生效模型全仓无人落盘 | ④ 记的是配置值不是生效值 |

四种子形状的修法各不同（注册链 / 传参 / 渲染 / 读数落盘），但第一步诊断相同：**看输入面**。

## 为什么它难被发现

- 「存在」和「送达」在代码里是两个地方，在人脑里是一个词。审计脚本 grep 到字段就发绿。
- 消费者往往会**编出合理行为**：模型不选没注册的工具、判官删没号的数字、门禁放过没读到的字段——
  每一步都符合各自的规则，所以整条链没有一处报错。
- 注入的内容可能不进运行产物（user 消息不是 tool 事件），去产物里 grep 会得出「没生效」的假象；
  **直接调渲染函数看输出**。
- 反面形状同样隐蔽：「没送到」是一个太顺手的解释，会替代「这份信息本来就答不了这题」。

## 修法（可带走）

- **断言送达面，不断言配置**：测试/门禁读的是渲染后的 prompt、实际注册表、实际菜单、响应体字段
  ——「验证要断言生效值，不是配置值」（finance spec 2026-09-02 §3.5.4 / §3.7）。
- **字段契约棘轮**：写了但全仓没人读的属性，新增即拦（`check_unread_fields.py`；存量免检只拦新增）。
- **收据要能区分「没给」与「没用」**：产物同时记授权集与实际调用集（`authorized_capabilities` 与
  `tool_set` 并列）；请求模型名与 `served_model` 并列。
- **注入点与校验点共用同一张号表**（harness-reference BUILD 模式 9）：渲染时就把引用把手打进去，
  别放宽校验器。
- 排查报告里写明**用什么证据回答了第一问**（哪份输入面、怎么取到的）；没写的结论按未回答第一问处理。

## 不覆盖什么

- 送到了、格式也对、但**写进了另一栏**——那是 [[misaligned-field-looks-plausible]]。
- 送到了、消费者也用了、但用法与承诺不符——那是 [[contract-vs-delivery-mismatch]] 的主体部分。

## 参考

- finance `docs/verification/2026-08-01-frequency-longtail-probe.md`（反面样本的撤回原文）
- finance `docs/handoffs/2026-08-08-prior-recall-and-runtime-fixes.md`「撤回的说法 / 实际」表
- finance `docs/superpowers/specs/2026-09-02-capability-amplification-output-gate-design.md` §3.5.4、§3.7
- finance `docs/verification/2026-08-21-gate1-prefetch-evidence-id.md`
- harness-reference `BUILD.md` 模式 3「事实投递 > 提醒」、模式 9「投递事实连同引用把手」；
  `TOOLKIT.md` A 档 `scripts/check_unread_fields.py`
