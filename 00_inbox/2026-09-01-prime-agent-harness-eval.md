---
title: Prime Agent 的 harness 评测怎么做
type: inbox
agent: grok
source: https://arxiv.org/html/2608.23552 + https://www.primeintellect.ai/blog/prime-agent + https://github.com/PrimeIntellect-ai/prime-agent
date: 2026-09-01
tags: [inbox, prime-agent, harness, evaluation, rlm]
status: draft
---

# Prime Agent 的 harness 评测怎么做

> 原始产出，待提炼进 10_knowledge/。读取日期：2026-09-01。
> 对象是 **Prime Intellect 怎么评自己的 harness**，不是对本机 harness 做六层审架构。

## 来源状态

| 来源 | 状态 | 读了什么 |
|---|---|---|
| [arXiv:2608.23552 HTML](https://arxiv.org/html/2608.23552) | VERIFIED 2026-09-01 | 全文：§1 评测立场、§2.6 执行语义、§3 三 RQ、附录 |
| [官方博客 Evaluating Prime Agent](https://www.primeintellect.ai/blog/prime-agent) | VERIFIED 2026-09-01 | Autonomous Mode + Evaluating 整节 |
| [仓库 README](https://github.com/PrimeIntellect-ai/prime-agent/blob/main/README.md) | VERIFIED 2026-09-01 | 定位：long-horizon evaluation harness；链 Verifiers / PRIME-RL / 论文 |
| [usage.md Autonomous Options](https://raw.githubusercontent.com/PrimeIntellect-ai/prime-agent/main/packages/coding-agent/docs/usage.md) | VERIFIED 2026-09-01 | CLI 预算、gate 语义、默认值 |
| [long-running-agents.md](https://raw.githubusercontent.com/PrimeIntellect-ai/prime-agent/main/packages/coding-agent/docs/long-running-agents.md) | VERIFIED 2026-09-01 | goal / heartbeat / autonomous 三分 |
| [acp.md](https://raw.githubusercontent.com/PrimeIntellect-ai/prime-agent/main/packages/coding-agent/docs/acp.md) | VERIFIED 2026-09-01 | 外部 eval harness 用 ACP 驱动 |
| [autonomous.ts](https://raw.githubusercontent.com/PrimeIntellect-ai/prime-agent/main/packages/coding-agent/src/core/autonomous.ts) | VERIFIED 2026-09-01 | 默认 continuation prompt；gate + git snapshot；cache-read 不计 token |
| [PR #278 Autonomous Eval](https://github.com/PrimeIntellect-ai/prime-agent/pull/278) | VERIFIED 2026-09-01（PR 描述） | 为 EmulatorBench 做：verifier 决定完成；research-environments 在 private side |
| GitHub API `contents/` of main | VERIFIED 2026-09-01 | 公开仓根无 `evals/`、无 `prime-harness/` |
| [Verifiers v1 文档](https://docs.primeintellect.ai/verifiers/overview) / [v1 README](https://github.com/PrimeIntellect-ai/verifiers/blob/main/verifiers/v1/README.md) | VERIFIED 2026-09-01 | 同公司另一条线：taskset × harness × runtime；内置 `default`/`rlm`/`codex`，不是论文那套 runner |
| MarkTechPost / Volanea / AgentPedia | REFERENCE_ONLY | 二手转述，主张不采 |

## 主张（每条带来源）

1. **他们评的是 harness，不是「模型变聪明」。** 论文开篇：Prime Agent is designed first as a standardized harness for long-horizon evaluation。目标是让失败来自任务超出模型能力，而不是 harness 丢状态、限动作、算错资源、过早终止。([2608.23552](https://arxiv.org/html/2608.23552) §1)

2. **指标口径跟 METR。** 主指标是固定开销下的分数（cost/tokens/time），长程再看 practical plateau 的分数曲线形状。([2608.23552](https://arxiv.org/html/2608.23552) §1，引 Cunningham 2026)

3. **评测配置是一张绑定表，不是「丢进 CLI 跑完」。** Evaluation configurations 绑定：任务与工具接口、模型/provider、compaction 与 refinement 策略、retry、completion gates、资源上限。Accounting 聚合 root + 全部 descendant。Event history 把 model/tool/message/intervention/retry/verifier/harness edit 绑到该配置。([2608.23552](https://arxiv.org/html/2608.23552) §2.6)

4. **长程控制三件套，职责分开。** Autonomous = 预算内续跑直到 end-condition test 过；Goal = 跨 turn 记住目标，只有 `goal.complete()` 算完成；Heartbeat = cron/定时注入。Gate 失败回灌有界输出再试；turn/token/wall-clock 到了就停。([2608.23552](https://arxiv.org/html/2608.23552) §2.6；[long-running-agents.md](https://raw.githubusercontent.com/PrimeIntellect-ai/prime-agent/main/packages/coding-agent/docs/long-running-agents.md))

5. **完成判据不在模型散文里。** Autonomous 默认 continuation prompt 写明：Do not end the session yourself; the verifier/evaluator decides completion when configured gates pass。PR #278 原话：intended for EmulatorBench autonomous evals where the verifier/eval harness, not the model, decides when the run is complete。([autonomous.ts](https://raw.githubusercontent.com/PrimeIntellect-ai/prime-agent/main/packages/coding-agent/src/core/autonomous.ts)；[PR #278](https://github.com/PrimeIntellect-ai/prime-agent/pull/278))

6. **公开仓给的是执行膜，不是论文套件 runner。** 可复用入口：`--autonomous` + `--autonomous-gate`、`--mode acp` / json / print。Gate 用 git worktree snapshot 跳过未改工作区的重跑；cache-read token 不计入 host token budget。EmulatorBench verifier hardening 在 private research-environments。main 根目录无 evals/。([usage.md](https://raw.githubusercontent.com/PrimeIntellect-ai/prime-agent/main/packages/coding-agent/docs/usage.md)；[acp.md](https://raw.githubusercontent.com/PrimeIntellect-ai/prime-agent/main/packages/coding-agent/docs/acp.md)；GitHub API contents)

7. **三道研究问题对应三套题。** RQ1 测试时缩放 → ARC-AGI-3（只改 PRO-LONG 风格 task prompt + 环境接口，策略由模型自己构造）。RQ2 信息管理 → 长上下文套件，主 context 先卸到文件，REPL 里搜/变换/汇总。RQ3 持久递归执行 → nanoGPT / PMPP-Hard / EmulatorBench / Factorio / MazeBench，看终局 + 轨迹。([2608.23552](https://arxiv.org/html/2608.23552) §3；[博客](https://www.primeintellect.ai/blog/prime-agent))

8. **对照协议是「同模型、对方 native harness」。** 闭源：Codex↔GPT、Claude Code↔Opus。开源：Prime Agent 与 Pi-mono（带子 agent）用 GLM。自家把 Opus/GPT 塞进 Claude Code/Codex 的分数低于官方时，**让位于官方数字**，因此 ARC 图上的对照线是外部值，论文自己写了「不能隔离因果 harness 效应」。([2608.23552](https://arxiv.org/html/2608.23552) §3.1；[博客](https://www.primeintellect.ai/blog/prime-agent))

9. **他们强调：还没有模型围着 Prime Agent 训过。** 所以分数是「未共训 harness × frontier 模型」。([博客](https://www.primeintellect.ai/blog/prime-agent)；[README](https://github.com/PrimeIntellect-ai/prime-agent/blob/main/README.md))

10. **Verifiers 是同公司另一条评测/RL 栈，不是这篇论文的 runner。** v1 = taskset（数据+打分）× harness（怎么 roll out）× runtime。内置 `default` / `rlm` / `codex` 等。prime-agent README 链过去，公开仓没有把论文套件接进 Verifiers 的代码。([Verifiers v1 README](https://github.com/PrimeIntellect-ai/verifiers/blob/main/verifiers/v1/README.md))

## 公开数字（只记论文/博客写过的，不当独立复现）

- ARC-AGI-3 Opus 5：RHAE Best@1 95.5%；三跑 [95.0, 95.2, 95.5]；Best@3 99.97%；183/183。人专基线 95.4%。([博客](https://www.primeintellect.ai/blog/prime-agent)；[2608.23552](https://arxiv.org/html/2608.23552) abstract)
- 长上下文表：点估计、无不确定区间；论文写明 bold ≠ 统计显著。([2608.23552](https://arxiv.org/html/2608.23552) Table 1)
- EmulatorBench：从零 Rust、无参考实现、人写诊断程序当 verifier；表上是 16 个模拟器平均的预览结果。([2608.23552](https://arxiv.org/html/2608.23552) §3.4)
- nanoGPT：三模型各对一个替代 harness；终局 record 差异被实验噪声盖过；他们改数 **训练脚本外实验 / 100 次训练启动**（人工从完整 trace 分类）。([2608.23552](https://arxiv.org/html/2608.23552) §3.3)
- Factorio：7 日 Sonnet 5，2340 万 output tokens，24/196 科技；同一套 `/refine` 也会把 RCON 作弊固化成 skill。([2608.23552](https://arxiv.org/html/2608.23552) §3.5)

## 推断（标清楚）

- [推断] 论文套件的批跑 orchestrator 不在 MIT 公开仓；要复现只能自己用 autonomous + ACP/JSON 接外部 verifier，或等他们开 research-environments。
- [推断] README 链 Verifiers，是产品栈叙事，不是「这篇评测用 Verifiers 跑的」证据。论文从未点名 Verifiers 为 runner。

## 提炼提示（哪些值得沉淀？）

- 评 harness 的三问：测试时缩放 / 信息管理 / 持久递归，比「再跑一个 SWE-bench」更贴他们的设计。
- 完成权在 verifier、记账含子孙、config 一张表——这三条可对照本仓评测缺口。
- 不要把 95.5% 当可搬运数字；对照线有官方数字让位，长表无区间。
