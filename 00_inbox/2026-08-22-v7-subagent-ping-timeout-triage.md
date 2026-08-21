# Agent Run Triage Report

## Verdict

- outcome: ROOT_CAUSE_NOT_CONFIRMED
- mode: M1
- failure_criterion: subagent run `dc7242cd-bfcb-4993-b227-4705d6d61ebb`（V7 传感器工作单执行方）以 `turn_ended status=error "[unavailable] PING timed out"` 终止；契约交付物（推送分支、开 PR、最终报告）在 2026-08-21T16:52Z 检查时全部缺席，尽管本地工作已完成
- trace_coverage: 冻结逐轮 transcript（70 事件，含 assistant tool_use 块，不含 tool 结果）；工作树 git 提交与时间戳；8 份 pytest 收据（文件级）；4 份 shell 终端文件（每次尝试的 start/end/exit）；父会话侦查记录。未覆盖：agent 进程侧存活数据（ping 日志、进程退出码、时点系统负载）
- trace_depth: D2
- completion_status: PARTIAL_SUCCESS
- confidence: medium

## Prior prediction closure

no prior report（对「Cursor subagent harness」这一被审系统的首次分诊；按一次性审查豁免暂不建 trace-profile 与账本。今晚同族现象已复发 4 次，若再审同一系统，第一次复审时补建两件，住址建议 `~/agent-memory/10_knowledge/` 同级）

- ledger: 暂缺（见上）
- fix_type_refuted_streak: 0

## Executive finding

第一处错误变换发生在 16:26:27Z 启动全量 pytest 之后、16:34Z 之前：agent 进程对 harness 存活探测失联（PING timeout），而其发出的工具调用仍在执行。工具层随后对同一命令做了不去重的重复投递（共 4 次可见执行，全部成功），结果无人消费。实质工作 100% 完成且验证为绿（含 dirty=false 全量收据），损失的只是交付三步（push/PR/报告）。失联的下层子因（负载饥饿 vs harness IPC 缺陷）证据未分胜负，故不确认根因。

## Expected vs actual path

| L1 step | expected | actual span/action | status | evidence |
|---|---|---|---|---|
| intent | 接 V7 工作单，TDD+变异+全量+交付 | 事件 1-68 按单执行 | ok | E-001 |
| plan | 红→绿→变异→文档→全量→push→PR→报告 | 事件 68 自述「正在写验证文档，并启动全量测试」 | ok | E-001 |
| tool | 提交文档、启动全量 pytest | 16:26:16 commit 落地；16:26:27 pytest 启动 | ok | E-003, E-004 |
| observe | 收到 pytest 结果（5956P/0F） | 结果从未送达 agent；harness 记 PING timeout；3 次无记录重复执行 | fail | E-002, E-004, E-005 |
| stop | 交付后正常收束 | turn_ended status=error；push/PR/报告缺席 | fail | E-002, E-006 |

## Failure detection

| failure span | L0 | L1 | exact L2 | evidence excerpt | confidence |
|---|---|---|---|---|---|
| normalized: dc7242cd/transcript.70 前的存活窗口（16:26:27–16:34Z） | HARNESS | observe | DEPTH_INSUFFICIENT(D3) | `{"type":"turn_ended","status":"error","error":"[unavailable] PING timed out"}` | medium |
| normalized: terminals/244525-27（16:30:50/16:32:02/16:32:42Z 三次重复投递） | HARNESS | tool | repetitive-behavior-category-repetition-tool | 四份终端文件同 cwd 同命令，transcript 无对应 tool_use | high |
| normalized: parent-session/receipt-query（16:57Z） | REASONING | retrieve | incorrect-actions-category-poor-information-retrieval | `ls … \| rg -i "a44cdb3b\|a7b9de8a" \| head -3` → 3 行，七份后续收据被截断 | high |

## Hypotheses

| ID | ranked hypothesis | falsifiable prediction | evidence/probe | status | probe_if_absent | why |
|---|---|---|---|---|---|---|
| H1 | agent 进程在工具调用在途时失联/死亡；重复执行是基础设施层重投递 | 事件 69 后无任何 assistant 事件；≥2 次相同 shell 执行无对应 tool_use；错误为 PING timeout | E-001, E-002, E-004 | CONFIRMED | — | transcript 与终端文件双向印证 |
| H2 | agent 其实存活，是它自己重发了 pytest（transcript 写入失败掩盖） | 若存活，push/PR/报告至少部分出现；重发应有 tool_use 记录 | E-004, E-006 | REJECTED | — | push/PR 全缺席；重复执行零记录 |
| H3 | 失联子因=并发全量测试的 CPU 饥饿（16:24-16:38 窗口 V4 套件+V7 自身多套并行）导致 ping 无法应答 | 事发窗口 ≥3 个并发 pytest 进程存在（已证）；若为真，失联应只发生在高负载窗口 | E-005, E-008 | INCONCLUSIVE | 下次 subagent 报错时立刻采样：每核负载均值，阈值 >1.5 支持本假设 | 并发已证实但缺进程级存活数据 |
| H4 | 失联子因=Cursor harness IPC 缺陷（与同晚 4 次 spawn 僵死同族：包装层 `snap=$(cat <&3)` 挂起） | 若为真，僵死应在低负载下也可复现 | E-008 | INCONCLUSIVE | 空载复现探针：系统每核负载 <0.5 时仍出现 spawn 僵死即证实 | 4 次僵死均落在有负载时段，与 H3 无法切分 |
| H5 | 网络/代理中断杀死了 agent-harness 连接 | 若为真，同时段其他会话应同样受损 | E-004（孤儿 shell 照常跑完）、V6 冒烟同时段成功 | REJECTED | — | PING 属本机 IPC；同时段本机其他活动正常 |

## Causal findings

### PRIMARY

- failure_span_id: normalized: dc7242cd/liveness-window（transcript 事件 69 与 70 之间，16:26:27–16:34Z）
- root_location: Cursor harness ↔ subagent 进程的存活通道（工具调用在途期间）
- excerpt: `{"type":"turn_ended","status":"error","error":"[unavailable] PING timed out"}`（transcript 第 70 行，文件末次写入 16:34Z）
- l0: HARNESS
- l1: observe
- l2: DEPTH_INSUFFICIENT(D3)（候选 leaf 在 execution-error-category-timeout / -resource-exhaustion / -environment 间未分胜负，需 agent 进程侧 phase 级证据：ping 时刻进程状态与每核负载）
- l3: n/a
- causality: PRIMARY_FAILURE
- propagation_impact: [TASK_TERMINATION, QUALITY_DEGRADATION]
- failure_detection_timing: SEVERAL_STEPS_LATER（父会话 16:52Z 收到通知才发现）
- completion_status: PARTIAL_SUCCESS
- evidence_ids: [E-001, E-002, E-004]
- explanation: agent 发出全量 pytest（预期 ~6 分钟）后，harness 在 ≤16:34Z 判定其失联并以错误终止 turn。工具执行本身全程成功——失败发生在「结果送达/存活维持」边界，不在工具、不在推理。

### SECONDARY / TERTIARY

**F-002（SECONDARY）重复投递不去重**
- failure_span_id: normalized: terminals/244524-27
- root_location: harness 工具执行层的重试路径
- l0: HARNESS / l1: tool / l2: repetitive-behavior-category-repetition-tool
- causality: SECONDARY_FAILURE（由 PRIMARY 的失联触发）
- propagation_impact: [QUALITY_DEGRADATION]（≈24 分钟冗余算力，4×6 分钟全量；结果无人消费）
- evidence_ids: [E-004, E-005]
- explanation: 同一命令 4 次可见执行（16:26:27/16:30:50/16:32:02/16:32:42Z 启动），后三次在 transcript 无 tool_use 对应。与本仓已确立原则「请求去重用 per-key single-flight」正面冲突——该原则再次在真实事故中验证。

**F-003（SECONDARY）父会话取证截断产生假阴性**
- failure_span_id: normalized: parent-session/receipt-query@16:57Z
- root_location: 父会话（本 agent）的收据核查命令
- l0: REASONING / l1: retrieve / l2: incorrect-actions-category-poor-information-retrieval
- causality: SECONDARY_FAILURE（抢救路径因 PRIMARY 而存在；错误本身是父会话自造）
- propagation_impact: [QUALITY_DEGRADATION]（多跑一次 6 分钟冗余全量；向用户报告了错误结论「死在全量验证之前」，后更正）
- evidence_ids: [E-005, E-007]
- explanation: `ls | rg | head -3` 把按字典序排在后面的七份收据截掉，得出「无全量绿收据」。实际上 16:38:57Z 的收据就是 5956P/0F/13S、dirty=false 的合格全量绿。教训与本仓既有纪律逐字押韵：「别用 head 截断可能承载结论的输出」。

## Evidence → Finding → Path

### Evidence

### E-001
- title: agent 最后两个动作：写验证文档 + 提交文档
- run_id: dc7242cd-bfcb-4993-b227-4705d6d61ebb
- step_or_span_id: normalized: transcript.68-69
- native_or_normalized: normalized
- source_type: transcript
- source_ref: agent-transcripts/dc7242cd-…/dc7242cd-….jsonl 第 68-69 行
- observed_at: ≈16:26Z
- raw_excerpt: |
    68: "诚实钉已还原为绿。正在写验证文档，并启动全量测试。" + Write(docs/verification/2026-08-21-inputside-sensors.md)
    69: Shell: git add docs/… && git commit … && git status --short && git log --oneline -3
- observation: 事件 69 是 transcript 中最后一条 assistant 消息；其后无任何 agent 发起的事件
- confidence: high

### E-002
- title: harness 终止记录
- run_id: 同上
- step_or_span_id: normalized: transcript.70
- native_or_normalized: normalized
- source_type: transcript
- source_ref: 同上第 70 行；文件 mtime 2026-08-22 00:34(+8)
- observed_at: 16:34Z
- raw_excerpt: |
    {"type":"turn_ended","status":"error","error":"[unavailable] PING timed out"}
- observation: turn 以 harness 侧错误收尾，无 agent 侧收束消息
- confidence: high

### E-003
- title: 两笔实现/文档提交均落地
- run_id: 同上
- step_or_span_id: normalized: git.a7b9de8a+a44cdb3b
- native_or_normalized: normalized
- source_type: file
- source_ref: fwp-wt-v7-inputside-sensors `git log --format='%h %cI'`
- observed_at: 00:24:21 / 00:26:16 (+8)
- raw_excerpt: |
    a44cdb3b 2026-08-22T00:26:16+08:00 docs(V7): 输入侧 KB 传感器验证文档
    a7b9de8a 2026-08-22T00:24:21+08:00 feat(V7): 输入侧 KB 传感器
- observation: 事件 69 的 commit 部分执行成功；树干净
- confidence: high

### E-004
- title: 同一全量 pytest 四次执行，仅首次可能对应 agent 的调用
- run_id: 同上
- step_or_span_id: normalized: terminals.244524-27
- native_or_normalized: normalized
- source_type: log
- source_ref: terminals/244524.txt–244527.txt（头部 started_at、尾部 exit）
- observed_at: 16:26:27–16:38:58Z
- raw_excerpt: |
    cwd 均为 /Users/a77/fwp-wt-v7-inputside-sensors；命令均为 .venv-workbench/bin/python -m pytest -q
    starts: 16:26:27.528 / 16:30:50.232 / 16:32:02.411 / 16:32:42.995；全部 exit_code: 0，输出等长（8728B）
- observation: 四次执行成功；transcript 中只有零或一次对应调用记录（事件 69 后无 tool_use）
- confidence: high

### E-005
- title: 八份 a44cdb3b 收据，末份为合格全量绿
- run_id: 同上
- step_or_span_id: normalized: receipts.a44cdb3b
- native_or_normalized: normalized
- source_type: file
- source_ref: ~/.finance-runtime/test-receipts/20260821T162921Z…163857Z-a44cdb3b.json
- observed_at: 16:29:21–16:38:57Z
- raw_excerpt: |
    163857Z: {"counts":{"passed":5956,"failed":0,"error":0,"skipped":13},"exit_status":0,"dirty":false}
    162921Z: {"counts":{"passed":0,"failed":0,…},"exit_status":0}
- observation: 全量绿收据在事发当晚 16:38:57Z 即已存在
- confidence: high

### E-006
- title: 交付三步缺席
- run_id: 同上
- step_or_span_id: normalized: parent-session/salvage-check@16:5xZ
- native_or_normalized: normalized
- source_type: tool_return
- source_ref: 父会话 `git branch -a`（分支仅本地）、Gitea PR 列表（无 V7 PR）、无最终报告
- observed_at: 16:52–16:57Z
- raw_excerpt: |
    remotes/gitea/ 下无 feat/v7-inputside-kb-sensors；PR 列表 311-315 无 V7 单
- observation: push/PR/报告三步均未发生
- confidence: high

### E-007
- title: 父会话截断查询与冗余重跑
- run_id: parent（本会话）
- step_or_span_id: normalized: parent-session/receipt-query@16:57Z
- native_or_normalized: normalized
- source_type: tool_request
- source_ref: 父会话命令 `ls ~/.finance-runtime/test-receipts/ | rg -i "a44cdb3b|a7b9de8a" | head -3`；重跑收据 20260821T170356Z-a44cdb3b.json
- observed_at: 16:57–17:03Z
- raw_excerpt: |
    查询仅回 3 行（162509Z/162534Z/162921Z）；父会话据此重跑全量，得 5956P/0F（与 163857Z 完全一致）
- observation: 截断查询漏掉七份收据；重跑结果证明既有收据当时即为真
- confidence: high

### E-008
- title: 同晚 harness 侧 4 次 spawn 僵死 + 事发窗口测试并发
- run_id: parent + V1/V2 executor
- step_or_span_id: normalized: terminals.58360/58363/58364/813968 + receipts.782a3278
- native_or_normalized: normalized
- source_type: log
- source_ref: 对应终端文件头部；一次 `ps` 取证见父会话（包装层停在 `snap=$(command cat <&3)`，cat 子进程存活 113 秒）
- observed_at: 16:57:36 / 17:05:40 / 17:15:31 / 17:31:58Z；V4 全量收据 16:29:23Z（与 V7 窗口重叠）
- raw_excerpt: |
    四次：命令本体零输出、wrapper 卡在环境快照读取；kill 后重试均立即成功
    事发窗口 V4 套件（16:24-16:29）与 V7 多套全量并行
- observation: 同晚存在独立的 harness spawn 缺陷证据，也存在高测试并发证据；两者时间上纠缠
- confidence: medium

### Findings

（正文见「Causal findings」：F-001 PRIMARY、F-002/F-003 SECONDARY；status 均 validated，confidence：F-001 medium、F-002 high、F-003 high）

### Path

### P-001
- title: 从 commit 落地到假阴性再到抢救闭环
- start: 16:26:16Z 文档提交落地、树干净（最后已知正确状态）
- goal: run 以 error 终止且交付缺席；父会话一度误判「未跑全量」
- steps:
  1. 16:26:27Z agent 启动全量 pytest（在途 ~6 min） — evidence: E-004 — finding: none
  2. ≤16:34Z agent 失联，harness 记 PING timeout（第一处错误变换） — evidence: E-002 — finding: F-001
  3. 16:30-16:33Z 工具层三次重复投递同一命令，无去重 — evidence: E-004 — finding: F-002
  4. 16:32-16:38Z 四次执行全部绿，收据落盘，无人消费 — evidence: E-005 — finding: none
  5. 16:57Z 父会话截断查询 → 假阴性「无全量收据」 — evidence: E-007 — finding: F-003
  6. 17:03-17:07Z 父会话冗余重跑（绿）、代推分支、开 PR #316（抢救闭环） — evidence: E-007 — finding: none
- residual_uncertainty: PRIMARY 的子因（CPU 饥饿 vs IPC 缺陷）未分胜负；162921Z 空收据（0 test、exit 0）的产生方未定位

## Fix recommendations

| ID | finding | fix_type | recommendation | verification prediction | regression guard |
|---|---|---|---|---|---|
| R-001 | F-001 | HARNESS_FIX | 派单纪律：执行方运行 >2 分钟的命令（全量 pytest 等）一律立即后台化 + 轮询收据/终端文件，不做长阻塞前台调用——把「工具在途」窗口里 agent 的应答能力保出来 | 下一波多执行方并发时，无 PING-timeout 死亡；终端文件无「同 cwd 同命令」重复对 | 波次收尾例行检查 terminals 目录重复命令对 |
| R-002 | F-002 | HARNESS_FIX | 重投递需 per-key single-flight（对同一 tool call id 不重复 spawn）；在无法改 Cursor 内部时，以 R-001 的后台化把长命令移出重投递暴露面 | 同类事故中不再出现多份等值全量执行 | 同上 |
| R-003 | F-003 | HARNESS_FIX | 抢救清单固化：按 revision 全量列收据（禁 head 截断），或直接 `check_test_receipt.py` 对 tip 判定；「收据缺席」结论必须引用未截断查询 | 未来抢救不再冗余重跑已有绿收据的套件 | 抢救步骤模板加一行「查询不得截断」 |

## Observability prescription

| blind_spot | 挡住了哪个判定 | 最小埋点（一个变量+阈值） | 埋在哪 | 埋完能判定什么 | 成本 |
|---|---|---|---|---|---|
| 失联时刻的系统负载 | H3（饥饿）vs H4（IPC 缺陷） | subagent 报错时立即采样每核负载均值；>1.5 支持 H3 | 父会话「收到 subagent error 通知」的固定首步 | PRIMARY 子因归属 | 一条 uptime 命令 |
| 空载下能否复现 spawn 僵死 | H4 独立性 | 每核负载 <0.5 时执行 20 次标准 spawn；出现 ≥1 次僵死即证实 H4 | 空闲时段一次性探针 | IPC 缺陷是否与负载无关 | 5 分钟 |
| 162921Z 空收据产生方 | 事发窗口未记录会话的存在性 | 收据增记调用方 pid/ppid（conftest 一行） | conftest.py 收据字段 | 每份收据可归属到会话 | 一行代码 |

## Limits and counterevidence

- agent 进程侧证据完全缺失（无 ping 日志、无进程退出记录、无时点负载采样），PRIMARY 子因只能停在 D2 层。
- 四次执行中哪一次对应 agent 的原始调用无法逐一配对（transcript 不含 tool 结果与 call id）。
- 反证据：同晚 4 次 spawn 僵死均发生在有负载时段，无法用现有材料切分 H3/H4——两者也可能是同一缺陷在不同负载下的两种显影。
- 本报告不含对 Cursor harness 内部实现的断言；所有 harness 侧机制均为从外部观测反推（code_reading 级以下），故 PRIMARY confidence 封顶 medium。

## Next-step menu

1. 空载复现探针（5 分钟，直接裁决 H4 独立性——信息增益最高）
2. 把「subagent 报错即采负载快照」写进父会话固定动作（裁决 H3，成本一条命令）
3. R-001 后台化纪律写进下一份派单简报（已可执行，防复发）
4. conftest 收据增记 pid/ppid（归属每份收据，消掉 162921Z 类悬案）
5. 若 H4 证实，整理最小复现报给 Cursor（含 wrapper `cat <&3` 取证）

---

## Addendum 2026-08-22 01:52 (+8)

E-009（新证据，事后补录）：V1/V2 执行方 shell 813969（17:39:48Z 起，`git commit` V2 实现）运行 238 秒后被标 failed、正文零输出，但 commit `15e4d8ec` 实际落地、树干净。据此今晚僵死家族分出两个亚型：

- **A 型（未执行）**：wrapper 卡在环境快照读取，命令本体零副作用（58364 的 `ps` 取证：`snap=$(cat <&3)` 挂起）。
- **B 型（已执行未回传）**：命令副作用落地，结果未送回调用方，shell 被标 failed/超时（V7 event-69、813969）。

含义：B 型下「shell 报错」不能当「动作未发生」用——抢救/重试前必须先查副作用（git log、收据、文件 mtime）。V7 的 PRIMARY 属 B 型合并存活失联；两型是否同根（同一 IPC 缺陷在不同时长下的显影）仍归 H3/H4 探针裁决。
