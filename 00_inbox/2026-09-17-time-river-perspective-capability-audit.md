---
title: 时间长河与 SPT／风远视角：生产能力核查及优化顺序
type: inbox
agent: codex
source: 2026-09-17 本机生产健康接口、部署源码、DuckDB 只读查询、用户画像与流程收据
date: 2026-09-17
tags: [inbox, finance, time-river, perspective, capability-audit]
status: draft
---

# 时间长河与 SPT／风远视角：生产能力核查及优化顺序

> 原始调查材料，待审阅；不替代能力图谱，不是实现完成声明。核查时间：2026-09-17 晚间。所有 VERIFIED 指本次确实读取源码／数据／收据，不代表全入口验收通过。

## 范围与版本

- **VERIFIED**：8792 健康接口报告生产 revision `bf662e9310ff751a4c31763815ee78fb7d6d5122`，代码目录 `/Users/a77/.finance-runtime/finance-workspace-bf662e9310ff`，loaded/repo fingerprint 一致，用户根目录 `/Users/a77/.local/share/finance-workbench/users`。[健康接口](http://127.0.0.1:8792/api/health)
- **VERIFIED**：主检出树存在其他会话大量未提交改动，本次没有修改项目代码、行情库、用户台账或视角；只在共享记忆新增本笔记。主要调查部署代码，不把脏树候选实现冒充生产能力。部署目录代码地图 status=empty，未用空图得出架构结论。
- **限制**：执行了生产服务函数的只读探针，读取了入口装配代码；没有向真实 Workbench 新建会话并完成模型问答，因此不声明自然语言路由、工具选用、最终答案质量已端到端验收。

## 核心判断

**[推断] 底座已能做多维历史研究，但尚不能称作完整自动执行 SPT／风远全部判据的研究闭环。** 必须区分：数据存在 → 确定性计算可用 → 本轮工具可达 → 实际调用并展示 → 判据通过前向验证。支持这一判断的逐层证据如下。

### 1. 时间长河是读取与对齐层，不是新建的事实库

- **VERIFIED**：`slice_river` 按观察日／实体／信息截止读取盘面、题材、舆论、资金、个股、判断六轨。对象有来源引用、内容哈希、有效时间与记录时间，缺轨返回 `Gap`。[部署源码 river.py](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/river.py)
- **VERIFIED**：2026-09-15 的机器人、算力租赁、半导体 live 切片均得到前五轨，判断轨均无该日该题材可证伪点。重复读取机器人切片的 `to_dict()` 完全一致。这里不是在声称判断账本全空，也不是每个题材每一天六轨完整。
- **VERIFIED**：机器人资金轨出现两个对象：`sector_constituent_flow` 与 `theme_flow`，都标注 `em-main-net`，均为14只成分，净额约 -0.814、成交额约44.7419，后者来源 `local:sector-basket:em-main-net`。**[推断] 同一批成分股的加总与其题材汇总，不应当作两份独立资金证据。** 来源：同次 `slice_river` 返回与[主库](file:///Users/a77/finance-workspace-private/db/market_feature_store.duckdb)。
- **VERIFIED**：传入 `frozen_snapshot_root=/Users/a77/fidelity-replay/pit-snapshots` 后，09-15 机器人严格切片与 live 不同：题材轨缺、资金轨仅1个对象；返回仍为 strict。冻结读取是参数选择，不是所有消费者默认使用。[river_frozen.py](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/river_frozen.py)、[封印目录](file:///Users/a77/fidelity-replay/pit-snapshots/)
- **[推断]** `pit_grade=strict`（时间约束等级）不等于数据完整，也不等于历史所有内容都已有不可变版本。要回答“当时能知道什么”，必须检查实际使用的是何时捕获的哪个快照，而非只看等级字符串。

### 2. 多维联立与特征计算已存在，并已实跑

- **VERIFIED**：`HistoryQuery` 支持 inspect／compute／analogues／compare，板块特征目录包含区间涨幅、首尾成交额比、严格双红天数及连续长度、成分股上涨占比、涨停占比、首次强涨时间差、相对大盘收益。个股支持其适用子集。[query.py](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/historical_research/query.py)、[features.py](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/historical_research/features.py)
- **VERIFIED**：实际计算窗口 `2026-09-01..2026-09-15`，共11个交易日，代码 `990219.FP / 990306.FP / 990122.FP`，读取板块、大盘、当日成分股、热度四张事实表；区间累计涨幅采用每日涨幅连乘。

| 对象 | 区间涨幅 | 日均成分上涨占比 | 严格双红天数 | 相对上证收益（百分点） |
|---|---:|---:|---:|---:|
| 机器人 | -7.996721752192004% | 35.61438561438561% | 0 | -4.935761432617292 |
| 算力租赁 | -4.798056599179457% | 35.26084422823553% | 0 | -1.737096279604744 |
| 半导体 | -7.352833313290508% | 31.67903525046382% | 1 | -4.291872993715796 |

- **口径**：严格双红为 `pct_chg>0 AND diff_ratio>10 AND amount>500`（金额单位亿元）；成分上涨占比是逐日去重成分中的上涨比例再取均值，不是期末成分区间上涨比例；`amount_ratio` 是窗口末日／首日成交额，不是成交额／20日均额。
- **VERIFIED**：三个板块的 `limit_up_share` 都返回 null／missing；机器人、算力的 `first_surge_lag` 返回 null／not_observed。缺数和未出现事件不当作零。该结果 `query_id=bae7529ec9715495b2ea119e2ec1e049f2372597beee57c456a14198fbfaafec`，`pit_grade=hindsight_reconstruction`、`research_only=true`、`decision_eligible=false`。
- **VERIFIED**：半导体 `compare_cases` 实跑：搜索07-01..09-15，5日窗／5日步长，条件至少1天严格双红，结果后5日收益>0；11个窗口、1个未成熟，四格为2／5／1／2。独立性未建立、certification_eligible=false，不能据此声称交易规律。来源同上；`query_id=1b6608339372ea315202c0934712ebacc94d7ea5f6ce7ecad9b21da0de323722`。
- **VERIFIED**：River 还有横截面扫描、条件组比较、区间聚合、窗口特征与聚类积木。**源码存在不等于全部注册到对话工具菜单。**[river_query.py](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/river_query.py)、[river_window.py](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/river_window.py)
- **VERIFIED**：通用派生计算工具也已存在：对本轮绑定证据运行受限 Python，保留输入哈希、公式、参数、脚本与计算产物，可挂只读 DuckDB；不是只能算固定8个特征。它受能力和证据账本装配约束。[derived_calculation.py](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/derived_calculation.py)、[agent_episode.py](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/runtime/agent_episode.py)

### 3. 视角已接提示，尚不能等同完整量化执行

- **VERIFIED**：用户画像 `sptfei`、`fengyuan` 真实存在；`build_runtime_context(... mode='single', query=...)` 成功，分别产生10537、13341字符的上下文，包含量能状态机／供给侧通胀镜头。[SPT画像](file:///Users/a77/.local/share/finance-workbench/users/linxiaoqi5111/perspectives/profiles/sptfei.json)、[风远画像](file:///Users/a77/.local/share/finance-workbench/users/linxiaoqi5111/perspectives/profiles/fengyuan.json)、[perspective_lab.py](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/perspective_lab.py)
- **VERIFIED**：Workbench 的 `conversation_orchestrator.py:2233` 传入所选视角提示；`episode_tools.py:1467` 在历史意图且非 local_only 时接历史研究工具，`history_tool_specs` 还要求授权 finance_query。普通受限“仅本地”合同目前会跳过此历史附加工具，不能用一条提示词保证可达。[入口装配](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/runtime/conversation_orchestrator.py)、[工具装配](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/episode_tools.py)、[历史工具](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/historical_research/episode.py)
- **[推断] SPT适用程度**：日线量价、广度、阶段、相对强度可基于现有事实与计算继续落实；30／60分钟背离、产业渗透率、四天时不能由日线量价替代。需要逐条声明可测变量、时间尺度、阈值及缺证据状态，不能把“严格双红”代替整个SPT量能状态机。
- **[推断] 风远适用程度**：双锚走势、出清量价、强股补跌等可拆成研究代理指标；供给弹性、设备交期／良率爬坡、谁在买、基金持仓、一致预期差，需要对应来源与时点，资金净额不等于A／B／C／D／E资金身份。结构性供需可走公告／财报／知识库取证，但不能因此宣称已有完整连续可回测序列。
- **VERIFIED**：`river_projection` 已记录选择／省略／限制，但当前自身只有默认规则及测试TopN规则；每对象渲染最多6个payload键。**[推断] 库里有字段不等于选定视角一定看到了该字段。**[投影源码](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/river_projection.py)

### 4. 每日复盘共用事实底座，但闭环不是每晚全绿

- **VERIFIED**：生产编排与 `daily-full` 写 canonical DuckDB；River从这份事实库读。同步侧跑窗口特征；报告侧可接带读；finalize终极门通过才尝试方法验证日步。冻结快照另有定时任务。[同步编排](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/skills/daily-full-review/scripts/run_review_sync.py)、[安装的夜跑脚本](file:///Users/a77/.local/bin/nightly_full_review.sh)、[冻结定时配置](file:///Users/a77/Library/LaunchAgents/com.financeworkspace.pit-snapshot.plist)
- **VERIFIED**：本次主库 max(trade_date)：大盘／板块／成分／个股／热度／题材资金均09-15；大单资金09-16、量化单09-15；外盘指数及个股09-02。首页 `served_trade_date=2026-09-15`。**最大日期只证水位，不能证明中间无缺日、所有字段完整。**[主库](file:///Users/a77/finance-workspace-private/db/market_feature_store.duckdb)、[首页快照](file:///Users/a77/finance-workspace-private/market_snapshot/latest.json)
- **VERIFIED**：09-15 daily-workflow 收据为FAIL（当次题材资金缺失，后续SKIP），当前该表已补到09-15，不能把旧错误当当前仍缺，也不能因当前补好就把旧失败收据说成通过。09-15 daily-agent 摘要为WARN。[流程收据](file:///Users/a77/finance-workspace-private/market_feature_store/exports/2026-09-15-daily-workflow-summary.json)、[agent摘要](file:///Users/a77/finance-workspace-private/market_feature_store/exports/2026-09-15-daily-agent-summary.json)
- **VERIFIED**：方法日步日志09-15因生成／终门失败跳过，09-16因数据门失败跳过。[日志](file:///Users/a77/finance-workspace-private/logs/method-validation-daily.log)
- **VERIFIED**：本次指定用户默认带读解析为False（已有历史台账）；教学旁路库需显式参数或 `FORESIGHT_TEACHING_LABELS_DB`。`db/history_labels.duckdb` 中常规 `history_labels` 有1736327行到09-15，但 `history_teaching_labels` 与 `history_teaching_gaps` 均0行。这里只核查这一个旁路库，不声称其他路径无教学产物。[带读源码](file:///Users/a77/.finance-runtime/finance-workspace-bf662e9310ff/intelligence/services/guided_reading.py)、[标签库](file:///Users/a77/finance-workspace-private/db/history_labels.duckdb)
- **VERIFIED**：安装夜跑脚本生成段仍 `cd "$WORKSPACE"` 后 `-m intelligence.cli`，源码注释明确其可能从共享主检出加载，与已钉住的质检／方法脚本根不同。**[推断] 运行代码根统一是优化项之一。**[安装脚本](file:///Users/a77/.local/bin/nightly_full_review.sh)

### 5. 已有规则验证，不等于已有有效优势

- **VERIFIED**：读取09-15最新共享规则收据：边际量转正、首板+一年新高、热度排名跃升三条为 `not_distinguishable`（与基准不可区分）；连续三日严格双红+上行阶段为 `insufficient_n`。均是探索性scan，不是已证明有效。规则来源均为系统内置，不能称SPT／风远全框架验证。[规则收据目录](file:///Users/a77/finance-workspace-private/methodology/receipts/)
- **VERIFIED**：读取用户方法验证最近standing（生成于09-11）：`first_real_cycle_completed=false`，唯一已捕获09-10事件为stage_not_applicable；`research_only=true`、decision/promotion均false。不是宣称整个系统没有回检，只说明此方法协议尚无完整真实有效循环。[方法研究目录](file:///Users/a77/.local/share/finance-workbench/users/linxiaoqi5111/method_validation/475597e2e017a2eedd3886700cd41d394d3694eba3487e205b8ddc91723b5a2f/)

## 优化建议（均为提案，未实施）

1. **先齐水位与证据血缘**：复用现有质量门／收据，按维度显示事实、特征、标签、快照、报告和方法日步状态；避免只报“总流程成功”。计算注明有效日与可知日，历史学习优先用可核验冻结源。同源题材／成分资金合并为一条证据链。
2. **把视角逐条落成证据需求合同**：复用画像、特征目录和方法规则，而非另建第二套系统。每条有定义、输入字段／单位／时间尺度、阈值版本、适用阶段、缺口、可反驳结果；状态为可计算／代理指标／需要定性证据，未知不补零。
3. **先做可证伪的小闭环**：SPT选“大盘量能×板块份额×广度×连续性”，风远选“方向锚×高度锚×强股补跌”；研究代理定义需用户审阅，不擅定成作者原意。输出每个判据命中／不命中／不可判及原始证据引用。
4. **复用现有算子并统一定义**：历史研究、River窗口和方法标签都已有实现；以共享定义防漂移，不再造并列特征库。高频稳定公式做版本化特征；临时假设走现有派生计算沙箱。DuckDB适合当前结构化联立；向量检索用于找文字证据，不负责精确时间／实体连接。
5. **从画像措辞转向验收答案**：在真实Workbench入口测试一组题，确认本轮菜单、实际调用、输入日期、结果产物和公开答案都一致。历史类比仅报告研究结果；规律升级须预先登记、未来观测、到期回检，不因一次回测好看自动晋级。

## 可立即尝试的问题（不保证每次自然语言路由成功）

- 2026-09-01到09-15，机器人、算力租赁、半导体哪个相对大盘更强？列出涨幅、成分上涨占比、双红天数及缺失指标。
- 选SPT：当前数据支持轮动还是主升？逐条给读数与口径；分钟结构或产业水位缺证据就明确写缺。
- 选风远：这次下跌更像放量恐慌还是缩量阴跌？哪项支持、哪项反证？不要仅凭资金净额给资金身份贴标签。
- 找与指定区间在涨幅、量能和广度上相似的历史窗口，列反例及阶段差异，不把相似性当收益预测。
- 检验“双红后更易上涨”：给样本／基准／缺失／未成熟／重叠依赖，结果只用于研究。

## 文档检查状态

已执行 `python3 scripts/vault_lint.py`：exit 1，全库19个错误、17个警告；输出未指向本次新笔记，错误位于既有项目笔记、知识笔记和TOOLKIT镜像。未修改其他会话文件，不能声称全库检查通过或本次产物已完成全库合规验收。

## 提炼提示

- 可迁移原则：**存了 → 算得出 → 本轮够得着 → 确实用上 → 经得起验证**，五项不能互相冒充。
- 日志历史失败、当前数据已补、流程尚无重跑成功收据，可以同时为真。
- 不把框架语言的成熟度误当成数据工程与统计验证的成熟度。
