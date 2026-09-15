---
title: Foresight A股投研 Agent 六张地图与生产状态审计快照
type: inbox
agent: codex
source: "finance pinned main 1bcb1ebc6a5b411752cacf30b801769711beb677 + production e40f22b837178322169f47e565282450b4381a3a + /api/health/readiness + six maps"
date: 2026-09-15
tags: [inbox, foresight, finance-agent, product-audit, production]
status: draft
---

# Foresight A股投研 Agent 六张地图与生产状态审计快照

> 读取日期：2026-09-15。本文是日期化审计快照，不替代[能力图谱][graph]；产品正式事实仍在 `/Users/a77/foresight/docs/product.md`，本文判断不自动成为产品决策。未修改金融实现或正式产品材料、未切生产、未运行他人 WIP，也未新跑真实模型/pytest。已修正图谱中有直接证据的旧状态。下文「历史收据记载」与本轮直接观测分开；`VERIFIED` 只表示读到所列正文/片段，不表示复跑通过。

## 一、审计坐标与证据等级

- **源码坐标**：Finance pinned main `1bcb1ebc6a5b411752cacf30b801769711beb677`；Harness `62debded014aac5c9ab6e57efd39776bf31e9ec7`。Finance 默认树仍是 dirty 的 detached `b4a35fa2`，不能拿它代表 main。[版本收据][revisions]
- **生产坐标**：8792 为 `e40f22b837178322169f47e565282450b4381a3a`，是上述 main 的祖先，main 领先 65 个提交。22:52 与收尾复查均 healthy/ready，`source_dirty=false`、`code_matches_repo=true`；22:52 读数为 953 模块。实际代码根 `~/.finance-runtime/finance-workspace-e40f22b83717`，由 `finance-workspace-runtime` 软链指向。[健康收据][health]
- **真实装配**：连续 Agent `on`，工具授权 `all`、研究档位 `max`；FINANCE_WS 指主数据树；KNOWLEDGE_WIKI 指 `/Users/a77/knowledge-base-private/wiki`，索引是该仓 `.rag_index`。当前 KB 为 dirty 的 `8a413cde5`，含未解决内容冲突；不是历史干净隔离树 `kb-wt-cap03-runtime`。健康只说明必要依赖可用，不证明知识正文/索引版本一致或每条研究链成功。[健康收据][health]；[路径解析源码][paths]
- **数据鲜度**：23:28:59 只读查 canonical DuckDB，8 张抽查表最大交易日均为 09-15；包括 `fact_stock_daily`、两张板块 VIEW、`fact_market_daily`、主线板块、题材涨停热度/成分及 `fact_theme_flow_daily`。行数不证明值级正确、所有字段非空或全历史覆盖。[数据收据][db-receipt]
- **模型身份边界**：当前后端自述 `continuous_glm` / `kimi-k3`；启动器保留 `LLM_MODEL=gpt-5.6-sol`。这是配置/可用性声明，不是每次实际调用的模型身份证明，也不是判官稳定性证明。[健康收据][health]
- **main 与生产并非完全一致**：`river.py` 的新增是题材轨生命周期状态对象，复用统一词表及当日状态机，区分 `stage` 与 `segment_hindsight`；不是生产此前缺少整条时间长河。main 还新增全口径 LLM 用量记录/判官 token 计账，及 9–16 补充验收测试。它们不能冒充生产已吸收。[river 差异源码][river]；[验收文档][endstate]
- **校验对象隔离**：路径/符号审计使用干净 Finance `1bcb1ebc` checkout 和新建干净 KB `8a413cde5` checkout；并未清理、更改实际 dirty 工作树或 KB。该检查对象不等于生产正在读的 dirty KB。

## 二、六张地图各自回答什么

| 地图 | 回答什么 | 不能代替什么 |
|---|---|---|
| [产品入口图][door] | 用户从哪进，Workbench/CLI/复盘写入各是什么合同 | 工具目录不是用户入口；CLI 结果不能冒充 Workbench 会话验收 |
| [能力节点图][graph] | 有哪些能力、接在哪、限制是什么 | 图谱也会漂；旧在途文字不能盖过固定源码和部署证据 |
| [代码结构图][code-map] | 实现、调用与测试可能在哪 | ready 索引不等于领域结论；本轮地图索引对应旧默认树 b4a35fa，不是 pinned main |
| [Harness 运行图][harness] | 提示、上下文、工具、安全、韧性、可观测六层如何保障运行 | 有工具不等于预算、取消、恢复和发布控制均完整通过 |
| [闭环原理图][closed-loop] | 输入→处理→质检→输出→评估→沉淀→下次输入 | 不是生成答案后附一个评分；更不是有闭环就能推出方法有效 |
| [数据与台账图][ledger] | 事实从哪来、谁可写、原件与派生物如何追溯 | DuckDB/知识原件/用户收据各有真源，HTML 是渲染物，不另立台账 |

产品门页也需以源码纠偏：本次 pinned main/生产已不注册 `feishu-bot`，原 shim 文件已移除；页中「run() 到不了」是旧说明。它不是问答门，不应恢复。`build_parser`/argparse 对非法子命令的拒绝与旧 shim 是不同机制。[CLI 源码][cli]

## 三、真实产品任务路径

以“这一波农业怎么走出来？找出值得检验的特征”为例。**这是按现有接线组合的任务说明，不声称本轮曾把下述所有步骤在一条真实会话里完整跑通。**[历史研究入口与合同][door]；[跨轮源码][project-code]

1. 用户从 Workbench 对话门进入：创建 conversation，消息交给 `TurnOrchestrator.run_turn`；研究车道默认引擎 A，但仍有确定性快速车道与 B 的分流，不是所有题都跑完整自主循环。
2. `TaskFrame.history_intent` 表示这是事后发现/历史比较，而不是普通概念解释。Episode 在预算、取消、同键去重和证据账本内行动。
3. 盘面侧用 `finance_query`、历史研究工具和 DuckDB 读日期轴、成员、区间特征、类比、支持/失败/缺失样本；知识侧可用 `kb_search` 深读整节，`graph_lookup` 的 `package/view/trace/compare/scope/legacy` 模式承接研究地图与页级定位。
4. 输出必须保留 coverage、codes_seen、Gap/MetricGap、unknown、dropped_dims、来源和知识截止日；不能因为有数值工具就把缺失补成 0，也不能把题材关联写成兑现。
5. 若需要财务比较，`financial_data` 提供结构化观察值；`derived_calculation` 在受限沙箱执行累计转单季、同比/环比、情景表和敏感性计算；记录进入 run telemetry，并可渲染成 JSON/CSV/HTML 产物。脚本化和确定性计算已证明可复现，不等于模型已经稳定会用。
6. 若问题要求多公司排序，`ranking_contract` 要求公司矩阵、财务传导、至少两种竞争解释、区分变量、改判条件和下一步；改判条件可登记为 checkpoint，机械再排序不编造权重或胜率。
7. 如果数据窗超出库覆盖，`tool_hunger` 记录 `window_uncovered`，由 data request 生成/检查/隔离补齐/沿原会话恢复；这不是生产库自动写入，补数 writer 必须在隔离环境。
8. 同一研究继续时，`research_project` 将 run 链、未解问题、引用、追问和裁决投影为研究先验；用户判断/纠偏和方法验证是可选的个人复利层，不是市场事实，也不改变研究-only 保护。
9. 目标交付是带证据边界的报告、数据表/计算件和下一步，不是荐股、目标价、买卖时点或自动下单。历史发现、描述性比较和方法演练不能升级成已验证投资规律。

步骤 3–4 的受限查询与原件合同见[历史实现][history-impl]、[river][river]；步骤 5–6 见[计算协议与收据][calc]、[排序契约与收据][ranking]；步骤 7 见[补数收据][data-request]；步骤 8 见[研究项目][project-code]、[台账真源][ledger]。注册表 AST 在本次固定版本数到 18 项，只是目录项数，不是每轮均授权/调用 18 项。[注册表源码][registry]

## 四、能力状态矩阵（截至固定版本和生产快照）

「已进生产代码」以提交祖先关系和对应源码核定，不表示每个函数已被实际调用；本轮未新跑真实模型验收。表中离线/隔离读数均为历史收据，不是本轮新测。[版本收据][revisions]

| 能力 | main / 生产代码 | 已核到的最好证据 | 不得外推的部分 |
|---|---|---|---|
| 历史发现、类比、反例、条件比较 | 两者均有，#716 | 修复后 M1–M5 隔离 Workbench 复验记为 PASS；非法 case 误拒与孤儿 tool 消息旧故障已有修复记录 | M6/UI 的完整复验本轮未核到；仍 research_only，不颁发独立样本/方法认证。[收据][history] |
| 深读检索 02 | 两者均有，#709 | 离线短语可见 14/20→19/20；少量真模型样本可见 1/3→3/3，但答案用上仍 2/3→2/3 | 可见性改善不等于全面答案提升；未重测当前索引/答案质量。[收据][deep-read] |
| 关系地图/材料身份 I2 | 金融侧接线两者均有，#713 | mode 路由、只读 API、超窗澄清/内容 hash 重绑定及机制测试 | 当前 KB dirty；完整关系包→原页→完成研究的干净真实任务收据未核足。[收据][i2] |
| 结构化财务/沙箱/计算产物 04 | 两者均有，#714；沙箱底座也在 | 确定性真实数据：茅台六个单季 6/6 一致，calc_id=68f7e6ba5592ed11；09-09 21:14–21:42 隔离真模型产出 calc-2768da969179e899；另有脚本化端到端/真实下载测试 | 三类证据不能混合为完整真模型题集通过；WP6 与基线差分未核到完整收口。[收据][calc] |
| 跨轮研究项目 09 | 两者均有，#689 及后修 | P1/P2/P3 隔离收据可见追问链、真实对象投影、若干差量表达 | 用过模型覆写/专用重试代理；P2/P3 复跑前改过历史消息，回答效果受到干预，不能当干净自然续研验证；自然跨日/直答先验覆盖未核足。[§3.2–3.3][continuity] |
| 问题驱动补数 08 | 两者均有，#711 | 09-09 隔离真实模型+writer：QA 从缺口到数字级答案且与库一致，失败可重试、同版本幂等 | QB/QC 数字答案和 QD 自然触发当时未达成；不自动写生产。后续 8799 W2 是另一未合分支收据，不能代签当前生产。[原始收据][data-request]；[W2 分支收据][wiring] |
| 多对象排序/情景 10 | 两者均有，#715 | 契约/机械排序/改判点登记的机制测试；Q1 候选可见矩阵与竞争解释 | 判官曾压掉公开答案、配对批有网关污染，不能算六题完整真模型通过。[收据][ranking] |
| 时间长河及历史内容版本 | 两者均有核心；main 多生命周期对象接线 | 日轴/区间聚合、受支持特征、截止门、可选冻结内容版本在；9–16 合同测试文档及补测已入 main | PIT（按当时可知信息回放）覆盖有限；未新测全历史 strict 覆盖。底层 cluster_windows 不等于 Workbench 任意聚类工具。[源码][river]；[冻结源][frozen]；[补测][endstate] |
| 研究进展账 06 | 两者均有，#710；提示默认开、硬收口默认关 | 12+12 题可见建议/换路；复杂题基线 30/32，候选 27/32 | 候选还开了 STALL_FINALIZE=3，不是只改单一提示的实验；既不能宣称成果提升，也不能把下降全部归给生产默认进展提示。[§7][progress06] |
| 方法飞轮 07 | 两者均有，#692/#731 | 固定协议/历史与前向分栏、收据派生 standing、memory_lookup/日报与日步 hook | 接线不等于每日成功，更不等于方法有效；历史发现/方法收据仍 research_only、decision_eligible=false、promotion_eligible=false。[台账][ledger]；[运行日志][method-log] |

### 生产现场：成功与失败同时保留

- **09-15 sync**：日志 18:30:01 开始、18:35:07 完成（S7 根自述 `418515c03833`）。`finance-workspace-sync` 在收尾时为 `6382c13b`、含运行产物改动；收尾 HEAD 不倒签为 18:30 每个脚本的实际代码版本。[当日日志][sync-log]
- **09-15 finalize**：20:47:51 workflow summary 的 quality-gate exit 2，报 `fact_theme_flow_daily` 无当日数据、最新 09-02；该 workflow 的后续步骤 SKIP，20:47:52 生成段 rc=1、method daily 明确跳过。其他独立产物/队列成功不能升级这次 workflow。[失败收据][nightly]；[method 日志][method-log]
- **晚间复查**：23:28:59 canonical 表中已见 403 行 09-15 题材资金数据。两次不同时间/执行现场的读数都保留；本轮没查明差异是后补、取库根、换库还是筛选口径，也没取得之后 finalize 重跑成功收据。**数据到位 ≠ 已失败任务自动变成功。**[数据收据][db-receipt]
- **恢复合同**：生产 `app.py` 有启动时 requeue 未完成 run 并重新 submit 的代码，`open_episodes` 另为只登记；`ContinuousAgentEpisode.restore`/`restore_episode` 函数存在。这不同于证明原 Episode 在崩溃指令处接续；本轮未做进程崩溃复验。它也不同于跨轮先验、data request resume。[生产 app.py 2235–2410][prod-app]
- **验收记账**：completed/healthy/测试绿分别是终态、可用性和工程检查，不替代研究交付。历史 00 批次曾从 28 completed 重分类为 clean 13/recovered 10/unavailable_final 5，另有 engine_missing 2；过程污染不能抹去。[集成归因 I1][integration]

### 尚不能写成“已证明有效”

外部用户与产品收入目前为 0，尚无独立外部省时、留存或付费证据。首批方法未获得与基准可区分支持；M-001 的 85/15/3 分别涉及事件、交易日和完整时间块，3 不是 3 个独立个股样本。可计算、可回放与可重复读数不赋予投资决策资格。[正式验证台账][validation]

## 五、生产与资本侧风险

以下是**[推断/建议]**，依据 §一/四工程与运行证据及[验证台账][validation]；本轮没有外部市场/竞品/法律意见调查，不能据此给市场规模或融资可投性定论。

1. **模型/网关依赖**：历史多次出现 429、502/503、model cooldown、auth unavailable；当前 health ready 不能代表高并发研究稳定。模型成本、判官成本、重试和并发预算直接影响毛利。
2. **数据授权与供应商依赖**：fupanhui、iFinD、AKShare、同花顺等数据源的授权、登录、CDP 和字段语义不同；不能把源存在写成永久可商用权利。数据源切换还会改变覆盖、复权、时间语义和产品可信度。
3. **数据运维与口径一致性**：09-15 晚主库有当日行，但生成任务先前失败；需分别记录代码/库根/计划/数据版本/执行时间，不能用之后的一张健康表覆盖失败。日期语义、列非空和内容版本是比“有行”更深的约束。
4. **研究可信度风险**：模型输出漂亮、终态 completed、测试全绿和判官通过都不能代替逐题答案、引用、缺口和过程污染审计。应让用户看见数据截止、缺口、计算口径、未完成项和研究用途限制；本轮不新增“可认证”徽章。
5. **合规边界**：不荐股、不提供买卖点/目标价/自动下单只是必要条件；收费产品还要明确数据授权、客户身份、研究用途、免责声明、留痕和人工复核责任。
6. **团队复杂度**：一人团队同时维护数据接入、DuckDB 换库、RAG、Workbench、模型网关、判官、前端、夜跑和验证系统。工程积累有价值，但代码规模不是资本护城河；可授权数据、稳定任务交付和真实用户持续收益（非投资收益）才值得验证。

## 六、产品理解与暂定判断

**[综合判断，非已批准的新定位]**，依据六图、固定源码与 §四证据：

当前最准确的定位不是“投教 + 判断日记”，而是：**一个以 A 股市场演变为对象、可调用结构化行情/知识/材料/计算工具，并把证据、反例、缺口、假设和后续验证连接起来的研究 Agent；个人判断校准是可选的复利层。**

即时价值的候选来源是：跨源检索与整理、市场变化计算、材料与盘面互相核对、未知/反例显式呈现、计算与研究产物留存。上述是可验证的价值假设，尚无外部省时数据；个人学习闭环不是唯一卖点，也不应被当作“预测准确率已经成立”的替代证据。

但现在仍是**工程能力远超商业验证**：技术面已形成真实产品骨架和若干可复现闭环，产品面尚未证明一组外部用户会持续使用并愿意付费，资本面尚不能凭源码复杂度或历史学员数量得出市场规模/融资结论。

## 七、下一阶段优先级（建议，未实施）

- 先固定 2–3 个可交付研究任务：历史事件考古与反例、材料改变判断的增量研究、隔日/跨轮研究更新；每个任务定义输入、输出、研究-only 边界、耗时和引用质量。
- **用户面与运维面分开**：用户只需看到数据截至哪天、引用/公式从哪来、哪些没完成、下次如何继续；代码版本、网关、判官和夜跑详细状态放运维面。不把整张工程状态矩阵塞给用户，也不只显示 completed。
- 优先复验既有可靠性机制，而不是假设预算/退避/去重不存在后重造：关键任务隔离、数据日期语义、夜跑失败链与重跑结果、生产代码与 KB 版本一致性。
- 用邀请制 3–10 名真实研究用户做外部验证，记录重复使用、节省时间、追问率、完成率、纠偏率、引用抽查和主动保存产物；不把“用户觉得有意思”写成付费或投资效果。
- 在数据授权、输出样本专业评估、成本和留痕边界未确定前，不急于收费、不承诺收益、不把个人方法收据包装成市场规律。

## 八、来源与维护边界

以下正文/指定片段均在 **2026-09-15 实际读取（VERIFIED）**。Git 链接绑定 SHA；历史 progress 中“当时未合/生产未切”只作历史过程，当前状态以版本/部署收据为准。源码检查不代替执行，历史收据不等于本轮复跑。未逐一打开原始 run 的地方明确使用“收据记载”，不声称对每条旧产物重新独立判分。

- 六图：[产品门][door]、[能力图][graph]、[代码图][code-map]、[Harness][harness]、[闭环][closed-loop]、[台账][ledger]。
- 原始结构：[schema][schema]、[历史查询/修订][history-impl]、[registry][registry]、[研究项目][project-code]、[river][river]、[冻结版本][frozen]、[路径解析][paths]。
- 历史测试/真模型收据正文：[历史发现][history]、[02][deep-read]、[I2][i2]、[04][calc]、[06 §7][progress06]、[08][data-request]、[09 §3.2–3.3][continuity]、[10][ranking]、[00 集成归因][integration]、[9–16 验收][endstate]。
- 分支旁证：[8799 W2/W3][wiring] 绑定 e8a63007，非本次 main/生产祖先；不得据 PR #732 标题把后续分支读数追认为生产结果。
- 本轮直接观测：[health/readiness][health]、[DB 行数/日期][db-receipt]、[Git/工具目录][revisions]、[09-15 workflow][nightly]、[sync 日志][sync-log]、[method 日步日志][method-log]。
- [产品验证台账][validation]全文已读。本轮没有调查外部竞品、规模、用户付费意愿、真实留存或取得法律评估，这些仍为待验证，非 VERIFIED 市场结论。

### 维护动作与质量门

- 只维护记忆层：本快照、canonical 能力图谱的已核状态，以及项目笔记的一行指针；正式 `product.md`、演讲/PPT/BP、金融实现与运行配置未改。
- 记忆库已有自动同步：草稿已由 d1222f8d、初轮图谱修订由 ca556a33 自动提交；不是本助手执行了合并/部署。后续增量以收尾 Git 状态为准。
- `graph_audit.py` 固定干净 Finance/KB 对象初跑 exit 1，定位两条退役 IM 旧路径；已用实际 CLI parser/退役 README 修正。最终退出结果记录在本节后续收尾行，不用截断输出或 PENDING 冒充通过。
- `vault_lint --strict` 早前输出被截断且报存量问题；完整收尾复跑与本次文件定位另列，不修不相关存量笔记。路径/格式绿也不代签产品效果。

[door]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/agent-product-door.md
[graph]: file:///Users/a77/agent-memory/10_knowledge/finance-agent-capability-graph.md
[code-map]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/scripts/code_map.py
[harness]: http://127.0.0.1:3300/a77/harness-reference/src/commit/62debded014aac5c9ab6e57efd39776bf31e9ec7/DESIGN-stack.md
[closed-loop]: file:///Users/a77/agent-memory/10_knowledge/agent-system-closed-loop-first-principles.md
[ledger]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/learning/ledger-map.md
[schema]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/market_feature_store/schema.sql
[cli]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/intelligence/cli.py#L4133-L4189
[paths]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/intelligence/paths.py
[registry]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/intelligence/services/research_tool_registry.py
[project-code]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/intelligence/services/research_project.py
[prod-app]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/e40f22b837178322169f47e565282450b4381a3a/intelligence/api/app.py#L2235-L2410
[river]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/intelligence/services/river.py
[frozen]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/intelligence/services/river_frozen.py
[history-impl]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/handoffs/2026-09-09-historical-discovery-implementation.md
[history]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/handoffs/inflight/codex-feat-historical-discovery.md
[deep-read]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/superpowers/plans/2026-09-09-capability-upgrade/progress/02.md
[i2]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/handoffs/inflight/feat-capability-i2.md
[calc]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/superpowers/plans/2026-09-09-capability-upgrade/progress/04.md
[progress06]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/superpowers/plans/2026-09-09-capability-upgrade/progress/06.md#L120-L163
[data-request]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/handoffs/inflight/feat-demand-driven-data-requests.md
[continuity]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/superpowers/plans/2026-09-09-capability-upgrade/progress/09.md#L105-L143
[ranking]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/superpowers/plans/2026-09-09-capability-upgrade/progress/10.md
[integration]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/superpowers/plans/2026-09-09-capability-integration/PROGRESS.md
[endstate]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/1bcb1ebc6a5b411752cacf30b801769711beb677/docs/verification/2026-09-15-endstate-acceptance-9-16.md
[wiring]: http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/e8a63007/docs/handoffs/inflight/fix-capability-wiring-closeout.md
[validation]: file:///Users/a77/foresight/docs/validation.md
[health]: file:///Users/a77/.finance-runtime/foresight-six-maps-audit-20260915/health-readiness.json
[db-receipt]: file:///Users/a77/.finance-runtime/foresight-six-maps-audit-20260915/database-freshness.json
[revisions]: file:///Users/a77/.finance-runtime/foresight-six-maps-audit-20260915/revisions-registry.json
[nightly]: file:///Users/a77/.finance-runtime/foresight-six-maps-audit-20260915/nightly-20260915-summary.json
[sync-log]: file:///Users/a77/.finance-runtime/foresight-six-maps-audit-20260915/sync-finalize-20260915.log
[method-log]: file:///Users/a77/.finance-runtime/foresight-six-maps-audit-20260915/method-daily-20260914-15.log
