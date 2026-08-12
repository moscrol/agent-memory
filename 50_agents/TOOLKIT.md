> **来源镜像**：canonical 在 `harness-reference/TOOLKIT.md`（`linxiaoqi5111-del/harness-reference` main）。
> 本文件供云端 Agent / agent-memory 拉取使用；改内容请改 harness-reference 后同步。

# 审查工具包

**怎么选**：见 `PLAYBOOK.md` Stage 2 —— 先问「这个现象最小需要多大的系统才能复现」，
**能用 0 档复现的绝不上 4 档**。整条 episode 是诊断单个部件最贵的方式。

全部经 2026-08-10 全树扫描确认存在（`finance-workspace-private` 68 个匹配 +
`agent-memory` 2 个 + `harness-reference` 2 个）。行数为实测。

---

## A. 零成本门禁（exit-code，可挂 CI / pre-commit）

跑一次就有结论，不烧配额。**这些是"永远该先跑"的一档。**

| 工具 | 判定什么 | 行数 |
|---|---|---|
| `pytest.ini` | **本身就是门禁**：`norecursedirs` 钉死收集面。不设它，主树 `tmp/` 下 4 个历史 clone 的同名包会撞成 `1031 errors during collection`，一条测试都跑不了 | — |
| `intelligence/tests/` + `tests/` | 294 个测试文件 | — |
| `scripts/layer_audit.py` | **领域层不得依赖 loop 底座** —— [[harness-layer-split]] 那条原则的可执行版 | 344 |
| `scripts/check_agent_workspace_facts.py` | 提交时把「你在哪棵树、用哪个解释器」摆到 agent 眼前 | 131 |
| `scripts/check_db_lock.py` | 复盘前置闸门：DuckDB 是否被占锁/残留进程，快速失败 | 62 |
| `scripts/check_rag_readiness.py` | 问答前 RAG 就绪自检：向量层能不能当证据用 | 114 |
| `scripts/check_kb_freshness.py` | 知识库证据断更监控，超阈值告警 | 89 |
| `scripts/check_market_snapshot_contract.py` | 快照数据契约 | 26 |
| `scripts/validate_marketing_contracts.py` | 只读校验 `docs/marketing/` 数据契约 | 142 |
| `scripts/validate_agent_cases_grounding.py` | 用例 grounding 校验 | 166 |
| `agent-memory/scripts/graph_audit.py` | 能力图谱防漂移（`finance-agent-capability-graph` 的 exit-code 门） | 231 |
| `agent-memory/scripts/vault_lint.py` | vault 质检门（把维护任务硬化成 exit code） | 179 |
| `scripts/check_unread_fields.py` | **字段契约棘轮**：属性写了但全仓没人读。2026-08-12 那七例「契约与交付不符」里有三例是这个形状（`tel.degraded`/`recall_desc`/`fallback_reason` 记了从没往模型传）。存量 40 文件/100 字段免检，只拦新增 | 219 |
| `harness-reference/scripts/verify_sources.py` | 原文 sha256 与 manifest 一致性（已变异验证：追加一字节 → exit 1） | 62 |

> ⚠ 门禁的通病见 [[gate-assertion-granularity]]：**只钉文件名的审计保不住符号**，
> `exit 0` 必须自述它对哪个 revision 成立。

---

## B. 排查定位（0–1 档，这一档最常被跳过）

| 工具 | 判定什么 | 配额 | 行数 |
|---|---|---|---|
| **变异验证**（手法，非脚本） | 改坏被测逻辑，确认测试真的会红。不做这步，你可能写了一条永远绿的测试 | 0 | — |
| **活性检查**（手法，非脚本） | 改动路径这次有没有被执行到。没执行到 = 无效样本 | 0 | — |
| `intelligence/eval/normalize_harness_trace.py` | 把异构 harness 事件归一成共享的**九步 L1 profile** —— 喂给 `agent-run-triage` skill | 0 | 1029 |
| `agent-run-triage` skill | trace-first 事后分诊，定位第一次出错的 step/span，输出 Evidence→Finding→Path | 0 | — |
| `scripts/run_episode_seam_ladder.py` **offline**（`OFFLINE_PROVIDER="scripted"`） | 整条 episode 装配跑不跑得通 | **0** | 1684 |
| `scripts/baseline_diff.py` **`--mode diff`** | **失败归属**：失败集合按测试 ID 与基线对照，报 新增/消失/共有。只有「新增」是本轮责任 —— 计数相等 ≠ 同一批失败（修好 3 条、引入 3 条，总数不变） | 0 | 357 |
| `scripts/baseline_diff.py` **`--mode probe`** | **「零行为变更」的证伪器**：把 HEAD 改动的测试搬到未改动的基线树上跑。因**断言**变红 ⇒ 同一输入两棵树行为不同，当场证伪；ImportError 单列为「新符号」，不算证据 | 0 | 同上 |
| `scripts/probe_tool.py` | **单个工具的试验场**：多久、返回什么、空结果什么样。独立 120s 预算、默认 `--repeat 2`（本仓检索链有一次性预热成本）。⚠ **路由用 stub、不调模型**——测不了「模型会不会正确构造参数」 | 低 | 356 |
| `scripts/probe_tool_arguments.py` | **模型构造参数的合法率**：给定 schema，模型写出的参数能不能过校验。走生产 registry + prompt builder，校验停在 `_compile_query`（纯 SQL 构造、不碰 DB），所以配额只花在「让模型写一次参数」上。`--follow-up N` 把**生产会发的拒绝消息**喂回去测自愈率；`--dry-run` 零配额验管道 | 低 | 631 |
| `scripts/probe_provider_latency.py` | 中转延迟、稳定性、token 上限行为（episode 量级） | 低 | 276 |
| `scripts/diagnose_compose_monotony.py` | 扫近 N 个 run 统计降级原因 + D 块重合度 | 0 | 215 |
| `scripts/check_db_lock.py` / `check_rag_readiness.py` | 排除环境假红（见下方"三条量具陷阱"） | 0 | — |

### 三条量具陷阱（都实际发生过）

1. **量具必须复刻生产**：手搓 urllib 探针曾 24/24 全红，真因是 UA 被中转拦掉，
   生产在 `llm_refine.py:52` 显式设 `finance-workbench/1.0`。**红灯来自工具。**
2. **高方差量上别低采样**：2–3 次采样的排序是噪声。看 min/P50/P95，
   判据写「预算 X 时有几成完成」不写「平均 Y 秒」。
3. **变异验证前清 `__pycache__`**：同字节长度突变 + 同秒还原，
   `.pyc` 按 `(mtime, size)` 判缓存有效，会伪造出「新回归」。
4. **变异必须先确认真的落盘**（2026-08-12 新增）：一次替换串带了引号前缀、
   没匹配上，是个 no-op，而「测试没红」被当成了结论——那一轮**测的是空气**。
   替换后先 `assert old in s` 再 `assert new != old`，然后才跑测试。
   同族的另一个形状：变异改出来的字符串仍是断言子串（把「方括号包起来」
   改成「方括号」），测试照样绿。**变异要删整句，不要改一半。**
5. **量具必须覆盖被改动的那一步**（2026-08-12 新增，本仓踩了两次）：
   改参数描述却用 `probe_tool.py` 验证——它 stub 掉了模型；
   改「拒绝理由回灌」却用单轮探针验证——回灌在第二轮才发生。
   **动手前先问「我改的这一步，量具走不走得到」**，走不到就先补量具。

---

## C. 端到端运行（3–4 档，烧配额）

| 工具 | 判定什么 | 行数 |
|---|---|---|
| `scripts/run_episode_seam_ladder.py` **live** | 一道真实市场问题跑完增量装配的 Episode。收据落 `~/.finance-runtime/seam-ladder/` | 1684 |
| `scripts/run_agent_episode_ab.py` | bare / current / continuous-episode 三臂隔离对照 —— **消融实验的执行器** | 676 |
| `scripts/run_agent_runtime_benchmark.py` | 冻结用例跑不同 AgentRuntime 后端 | 1942 |
| `intelligence/eval/runtime_backend_benchmark.py` | provider-neutral 结果契约 | 757 |
| `scripts/smoke_workbench_self_use.py` | 脱敏的端到端 Workbench 对话冒烟 | 1184 |
| `scripts/semantic_acceptance.py` | 三道代表性长尾题重放 | 380 |

---

## D. 评测 / 验收（判"达标率"，不判"哪步坏"）

| 工具 | 判定什么 | 行数 |
|---|---|---|
| `intelligence/eval/acceptance.py` | 28 题验收台账（**进度只从这里生成，不从记忆里写**） | 884 |
| `intelligence/eval/acceptance_verdict.py` | fail-closed 判定 | 1046 |
| `intelligence/eval/acceptance_diff.py` | **逐题对比两次运行**，报「28 题里哪几题变了」，不报一个混合分数 ← 方差治理的可执行版 | 203 |
| `intelligence/eval/acceptance_axes.py` | 交付/信息/可信度三轴确定性投影 | 117 |
| `intelligence/eval/acceptance_comparison.py` / `_observations.py` / `_runs.py` | 完整性绑定的对比 / sidecar / run 目录 | 352 / 549 / 116 |
| `intelligence/eval/agent_eval.py` | 确定性打分器（P1+ 评测闸核心） | 330 |
| `intelligence/eval/finance_answer_rubric.py` | 确定性的金融答案结构审查 | 658 |
| `intelligence/eval/presentation_diversity.py` | 反模板度量（结构相似度，**顾问性不是阻断门**） | 105 |
| `intelligence/eval/gold_review.py` + `scripts/gold_review_workbench.py` | 人工 Gold 评审，**不自动批准候选** | 817 / 336 |
| `scripts/research_judge.py` / `scripts/dual_blind_*.{py,sh}` | 双盲对照与判定 | — |

---

## E. 对账与历史审计（读已完成的 run，零配额）

**这一档最容易被忘，但它常常不用跑新实验就能给出答案。**

| 工具 | 判定什么 | 行数 |
|---|---|---|
| `intelligence/eval/capability_monotonicity.py` | **约束有没有让 agent 变得更没能力**。确定性、无副作用、不调 LLM 也不调 runtime | **899** |
| `intelligence/eval/synthesis_health.py` | 合成健康度**四态**：`full_pass` / `released_unverified` / `template_fallback` / `not_synthesized`。旧产物计入 `unknown` 而非默认算好 | 346 |
| `scripts/scan_grounded_composer_runs.py` | 离线扫 shadow 产物，报**删除率 / 假绿 / 必需输出存活** | 133 |
| `scripts/reconcile_tool_outputs.py` | 对账历史 run：实际 fulfilled 的 `output_id` 及绑它的工具 | 710 |
| `intelligence/eval/grounded_replay.py` | **冻结输入重放**：读已完成 run 的产物，重建生产 `AnswerSpec`，复用生产 registry/prompt builder，跳过检索 | 808 |
| `intelligence/eval/fidelity_replay.py` + `scripts/fidelity_replay_eval.py` | 确定性保真与严格 PIT 重放 | 1144 / 224 |
| `scripts/replay_operator_routing.py` | 用真实历史提问回放 operator 路由判别 | 359 |
| `scripts/verify_l2_recovery_artifacts.py` | L2 恢复产物只读审计 | 216 |
| `scripts/loop_health_report.py` | 把散在两仓的评估/沉淀/入库信号聚合成一页周报 | 205 |

---

## F. Agent 评审闭环（独立子系统，**我一次都没用过**）

`scripts/agent_review/`，约 2300 行，含 `gate.py` / `contract.py` / `worker.py` /
`submit.py` / `validate_verdict.py` / `bootstrap.py` / `REVIEWER_PROMPT.md` /
`reviewer_worker.sh`。有独立的 worktree 目录
（`~/.finance-runtime/agent-review-loop/worktrees/review-ARL-00xx`）。

⚠ **全部无 docstring**，我没读过它的语义。**列在这里是提醒它存在，不是推荐使用** ——
按纪律，没读过的不进结论。要用之前先读 `gate.py` 和 `contract.py`。

---

## G. 参照系维护

| 工具 | 判定什么 |
|---|---|
| `harness-reference/scripts/verify_sources.py` | 原文与 manifest 的 sha256 |
| `harness-reference/scripts/restore_sources.sh` | 按 pin 的 commit 稀疏恢复三本书 |
| `grep -n 关键词 INDEX.md` → `grep -rn sources/ upstream/` → **Read 整章** | 检索三步，不做向量化 |

---

## H. 通用手法（不是脚本，但漏了就白做）

| 手法 | 防的是什么 |
|---|---|
| **活性检查** | 无效样本被读成信号 |
| **变异验证** | 永远绿的测试 |
| **干净对照** | 跨修复比较 = 测到「修复效果 + 噪声」的混合 |
| **全树 grep + 读能力图谱 + 读项目笔记** | 负面断言（"我们没有 X"）搜一个文件证明不了 |
| **标注证据等级** `[实测]` / `[推断]` | 把推断说成事实 |
| **`--collect-only` 验收集面** | 门禁自己坏了却发绿光 |
| **测试计数必须同时写明解释器路径** | 宿主 `python3` 与 `.venv-workbench` 依赖不同：**同一棵树同一时刻，前者 71 failed，后者 14 failed**。不写解释器的计数不可复核（2026-08-10 实测，57 条环境噪声差点被写进提交记录） |
| **「零行为变更」不能由测试全绿推出** | 全绿只说明���没有测试钉住修复前的语义」。异常类型不变 ≠ 抛不抛不变。要证伪用 `baseline_diff.py --mode probe` |
| **失败归属要比名字，不比计数** | 修好 3 条 + 引入 3 条 = 总数不变。用 `baseline_diff.py --mode diff` |
| **契约体检：标签承诺的 == 实际交付的？** | 见下节。2026-08-12 一天里在**五个互不相干的模块**各命中一次 |

---

## H+. 契约体检：一条审查项，一天里抓到五个实例

**失败形状**：某处向模型（或向下游审计）**承诺**了一件事，实际交付的是另一件，
**且模型无法自行诊断**。它不是 bug 的一种，是 bug 的一**类**——五个实例分散在
五个模块、由不同时间的不同改动引入，彼此没有共同代码。

| # | 承诺 | 实际 | 后果 |
|---|---|---|---|
| 1 | schema `limit.maximum = 1000` | runner `min(limit, 25)` | 189 次调用里 55 次（29%）在错误信念下工作，把 25 行截断结果当全集 |
| 2 | `{"error": "invalid_arguments", "detail": ""}` | 原因**有**，只是没往下传 | 15 次失败里 14 次是同一个错**一模一样地重复**——模型没有可据以修正的信息 |
| 3 | `无命中（error）` | 20/22 是工具故障，不是知识库为空 | 模型把「查不到」写成「不存在」；且 trace 记 `empty`，**按状态计数的审计看到零错误** |
| 4 | 标题「较早消息**摘要**」 | 尾部截断，最早的部分静默丢弃 | 模型以为「已概括全部较早内容」 |
| 5 | 检索结果（形态完全正常） | hybrid 已降级为纯 BM25，语义那路没跑 | **最危险的一种：成功外观下的能力降级**，无任何报错 |

### 为什么它特别难被发现

- **静默**：没有异常、没有红灯，输出形态正常
- **自洽**：模型据此写出的结论内部一致，只是前提是假的
- **量具同盲**：#5 走 eval 也发现不了——合成 eval 集判别不了 hybrid 与 BM25。
  **量具盲区与生产盲区重合时，缺陷可以长期存在而两边都发绿**
- **契约反向加固**：#3 里我们**自己写的**行为契约说「无命中只说明知识库没有回填过」
  ——在 status=error 时这句话是错的，契约在主动教模型误读

### 怎么查（按成本从低到高）

0. **先跑 `scripts/check_unread_fields.py`**（A 档，零成本）——「填了但没人读」这一支
   已经机械化了，七例里占三例。剩下几步才需要人。
1. **对每个「广告值」找它的「执行值」**，两个都是机器可读的数就写成硬断言。
   例：`test_agent_finance_schema_limit_matches_enforced_cap`
2. **grep 所有「兜底文案」**：`or f"无..."` / `or "没有..."` / `else "empty"`——
   这类 `or` 右侧的默认串，正是把多种原因压成一句话的地方
3. **看结构体里有没有「填了但没人读」的字段**：`detail`、`degraded`、
   `fallback_reason`、`warning`。**遥测诚实但不往上传**是本类的高发形态
4. **对每个降级分支问一句：模型看得出来吗？** 看不出来就补一句告知——
   ai-agent-book ch4「必须在工具描述中加以说明，并在工具返回中明确告知模型」

### 修的时候的两条纪律

- **成对改**：既改行为也改声明。只拆不说 = 静默输入转换（书里点名的反模式）
- **别每次都说**：没降级时返回空串。每次都挂一句「本次正常」会训练模型忽略这一行，
  比不说更糟——与契约表「没依据宁可留空」同一条纪律

---

## 附：当前问题（`episode_protocol` 二值销毁）最该用的三个

按 `PLAYBOOK.md` Stage 2 选档，**全部零配额**：

1. **`capability_monotonicity.py`** —— 它的设计目标一字不差就是当前的问题：
   *"Offline checks that constraints do not make an agent less capable."*
   「加了约束之后，Workbench 还答不答得了用户真正的任务」。
   **这是本仓最对口的工具，而我此前的排查里一次都没提到它。**
2. **`synthesis_health.py`** —— 它已经把「有没有走完合成链」**从二分改成四分**，
   并且明确写着「『没测到』和『测到是好的』混为一谈，正是这次要修的毛病本身」。
   **9.7「恢复的目标是继续工作」在本仓已有先例实现** —— 门禁那边照抄这个四态口径即可，
   不必从零设计。
3. **`scan_grounded_composer_runs.py`** —— 报删除率 / 假绿 / 必需输出存活，
   零配额扫历史产物，直接量化"销毁"发生了多少次。

---

## 附：整改项（docstring 缺失，说明语义没被记录）

以下有实质逻辑但无 docstring，**下次动到谁就给谁补**：
`agent_review/*.py`（6 个）、`check_daily_review_data.py`、`fidelity_runtime_status.py`、
`research_judge.py`、`validate_agent_cases_grounding.py`、
`validate_strategy_matrix_forward_returns.py`、`eval/gold_review.py`、
`eval/runtime_status.py`、`eval/forward_acceptance.py`。
