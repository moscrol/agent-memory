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

> 读取日期：2026-09-15。本文是日期化审计快照，不替代能力图谱；稳定能力仍以 `/Users/a77/agent-memory/10_knowledge/finance-agent-capability-graph.md` 为唯一事实源。未修改金融仓、未切生产、未运行他人 WIP。

## 一、审计坐标与证据等级

- Finance pinned main：`1bcb1ebc6a5b411752cacf30b801769711beb677`。
- 生产 8792：`e40f22b837178322169f47e565282450b4381a3a`，是 pinned main 的祖先；`git rev-list prod..main` 为 65。生产快照健康检查报告 `source_dirty=false`、`code_matches_repo=true`、953 个模块加载，代码根为 `~/.finance-runtime/finance-workspace-e40f22b83717`。
- 生产 `/api/health` 与 `/api/readiness`：2026-09-15 通过；连续 Agent 为 `on`，工具授权为 `all`，研究档位为 `max`，RAG worker ready，market snapshot ready。健康通过只说明服务、依赖、代码快照和必要数据门可用，不等于每种研究任务的答案效果成立。
- 生产进程环境实际指向：`WORKBENCH_REPO_ROOT=/Users/a77/finance-workspace-runtime`，该路径软链到上述生产快照；`FINANCE_WS=/Users/a77/finance-workspace-private`；`KNOWLEDGE_WIKI=/Users/a77/knowledge-base-private/wiki`；RAG index 为知识库仓 `.rag_index`。不能把历史验收用的 `/Users/a77/kb-wt-cap03-runtime` 直接写成当前生产 KB 根。
- 当前 canonical DuckDB 只读抽查：`fact_stock_daily`、`fact_sector_daily`、`fact_sector_stock_daily`、`fact_market_daily`、`fact_mainline_sector_daily`、`fact_theme_limit_heat_daily`、`fact_theme_flow_daily` 的最大交易日均到 `2026-09-15`。这更新了 09-07 的旧鲜度读数，但没有证明所有列非空或所有历史窗口无缺口。
- 生产环境当前观测到 `continuous_glm` / `kimi-k3`；启动器同时保留 `LLM_MODEL=gpt-5.6-sol` 等变量。回答效果、模型 lane、判官状态仍应以具体 run 收据为准，不从环境变量自述推断稳定性。

## 二、六张地图各自回答什么

1. **代码结构图**：`scripts/code_map.py`。回答“实现可能在哪”，不证明实现已合主线、已部署或真实有效。
2. **能力节点图**：`finance-agent-capability-graph.md`。回答“稳定能力节点、边界和闭环是什么”；维护后需按固定 checkout 跑 `graph_audit.py`。节点表中仍有历史在途行，阅读时必须按 revision 重新核对，不能照旧日期化文字。
3. **产品入口图**：`docs/agent-product-door.md`。真正的人口是 CLI ask/chat/agent、Workbench HTTP/UI、steer 和 daily-full；A 是连续 Episode，B 是固定流程或 ownerless 长尾，不把注册表当产品门。
4. **Harness 运行图**：`DESIGN-stack.md`。用六层看提示、上下文、工具、安全、韧性、可观测；有工具不等于有预算、取消、恢复、发布权和有效性保障。
5. **闭环原理图**：输入→处理→质检→输出→评估→沉淀→下一轮输入。评分、纠偏、方法收据和记忆不是答案末尾的附属字段。
6. **数据/台账图**：`docs/learning/ledger-map.md`、`schema.sql`、数据源和写入脚本。回答“事实从哪来、谁能写、能否追溯”；DuckDB、知识库原件、用户台账和渲染 HTML 不能混为一谈。

## 三、真实产品任务路径

以“这一波农业怎么走出来？找出值得检验的特征”为例：

1. 用户从 Workbench 对话门进入：创建 conversation，消息交给 `TurnOrchestrator.run_turn`，默认进入引擎 A；不要用 CLI 输出冒充 Workbench 的 conversation/run 合同。
2. `TaskFrame.history_intent` 表示这是事后发现/历史比较，而不是普通概念解释。Episode 在预算、取消、同键去重和证据账本内行动。
3. 盘面侧用 `finance_query`、历史研究工具和 DuckDB 读日期轴、成员、区间特征、类比、支持/失败/缺失样本；知识侧可用 `kb_search` 深读整节，`graph_lookup` 的 `package/view/trace/compare/scope/legacy` 模式承接研究地图与页级定位。
4. 输出必须保留 coverage、codes_seen、Gap/MetricGap、unknown、dropped_dims、来源和知识截止日；不能因为有数值工具就把缺失补成 0，也不能把题材关联写成兑现。
5. 若需要财务比较，`financial_data` 提供结构化观察值；`derived_calculation` 在受限沙箱执行累计转单季、同比/环比、情景表和敏感性计算；记录进入 run telemetry，并可渲染成 JSON/CSV/HTML 产物。脚本化和确定性计算已证明可复现，不等于模型已经稳定会用。
6. 若问题要求多公司排序，`ranking_contract` 要求公司矩阵、财务传导、至少两种竞争解释、区分变量、改判条件和下一步；改判条件可登记为 checkpoint，机械再排序不编造权重或胜率。
7. 如果数据窗超出库覆盖，`tool_hunger` 记录 `window_uncovered`，由 data request 生成/检查/隔离补齐/沿原会话恢复；这不是生产库自动写入，补数 writer 必须在隔离环境。
8. 同一研究继续时，`research_project` 将 run 链、未解问题、引用、追问和裁决投影为研究先验；用户判断/纠偏和方法验证是可选的个人复利层，不是市场事实，也不改变研究-only 保护。
9. 最终结果是带证据边界的研究报告，不是荐股、目标价、买卖时点或自动下单。历史发现、描述性比较和方法演练一律不能升级成已验证投资规律。

## 四、能力状态矩阵（截至固定版本和生产快照）

### 已进入生产代码，且有机制/离线或隔离验收

- **历史发现**：`historical_research`、`history_query`、`read_history_result`、`save_history_research` 已在生产祖先中；注册表固定版本 AST 有 18 个条目。历史 M1–M5 等隔离 Workbench 收据证明了若干真实路径，M6/UI 曾受网关/判官条件影响，不能把整套六题写成完整通过。
- **02 深读检索**：命中后整节读取、表头保留、过期原页恢复、证据分段等代码已进生产。历史离线/少量 live 读数改善了模型可见证据，但当前生产索引新鲜度和答案提升没有重新做完整测量。
- **研究项目/跨轮续研（09）**：研究项目投影、追问 continuation、先验块和 UI 面板已在生产代码。P1/P2/P3 隔离验收证明机制和研究差量在若干轮成立；自然日跨天覆盖和“直答车道不带先验”的边界仍存在。
- **关系地图/材料身份（I2）**：模式路由、只读研究地图 API、超窗澄清和内容 hash 重绑定已在生产代码；真实“关系包→原页→完成研究”的全链路没有取得完整通过收据。当前生产 KB 根是主知识库工作树，不是历史隔离的干净 03 runtime，故需把运行配置/数据一致性单独验收。
- **结构化财务/沙箱/产物（04）**：生产代码和下载产物链存在；隔离真模型曾生成过计算产物，确定性茅台六个单季对照 6/6 一致；完整真模型题集和稳定使用效果未证明。
- **问题驱动补数（08）**：缺口事件、请求、覆盖检查、隔离填充和 resume 代码在生产祖先中；隔离 W2 已证明“hunger 1→0、补齐后逐位重算一致”。这不等于生产环境自动补库，也不等于 fupanhui 在风控/登录条件下可无脑重试。
- **排序/情景（10）**：表达契约、矩阵、竞争解释、改判条件和 mechanical scenario apply 已在生产代码。隔离批跑曾看到结构化答案差分，但完整配对批受共享网关/判官污染，不能宣称六题完整 live 通过。
- **时间长河**：日频六轨、区间聚合、窗口特征、可选冻结快照和 PIT/knowledge cutoff 门在代码中；当前生产数据库新鲜到 09-15，但没有重新测得所有历史 strict 覆盖。冻结快照是有限、可选覆盖，不是全产品全历史无前视回放。

### 已有代码/默认接线，但效果或运行合同不能升级

- **研究进展账（06）**：进展块默认开，停滞自动收口默认关。双臂 12+12 题完成，但复杂题基线 30/32、候选 27/32，不能说新机制提高了研究成果；它证明了建议/换路行为，不证明答案质量提升。
- **方法飞轮（07）**：工程、memory_lookup/[M] 消费和夜跑 hook 已存在，前向与历史演练分栏，固定 research_only。当前日志显示 09-14、09-15 因生成段/最终硬门失败而跳过 method daily；所以“接入了”成立，“每天成功运行”不成立，“方法有效”更不成立。
- **生产全量复盘**：09-15 sync、daily-agent、snapshot 有成功记录，但 finalize 退出 1；错误包括 feature staging 为空、历史日志中的 CDP/fupanhui 故障和旧脚本 plan 不兼容。健康接口 ready 不等于当天日报/研究队列/方法日步全链成功。
- **运行恢复**：Episode restore、研究项目先验、data request resume 是三个不同合同。跨日先验已在 Workbench 接线；数据请求恢复有隔离收据；生产进程崩溃后的自动重启恢复是否实际启用，不能从这三者外推。

### 尚不能写成“已证明有效”的部分

- 外部用户价值、付费、留存、研究完成率、时间节省和投资结果：没有独立外部实证；外部用户与收入目前为 0。
- 方法有效性、胜率、Alpha 或可用于投资决策：没有资格证据；历史可回放/可计算/两次读数一致只说明相同数据版本与口径下可复现。
- 关系地图全链路、计算完整真模型六题、排序完整配对批、历史 M6/UI、整包 after/00 对照：已有局部机制/收据，但未取得可覆盖全题的干净生产级收据。

## 五、生产与资本侧风险

1. **模型/网关依赖**：历史多次出现 429、502/503、model cooldown、auth unavailable；当前 health ready 不能代表高并发研究稳定。模型成本、判官成本、重试和并发预算直接影响毛利。
2. **数据授权与供应商依赖**：fupanhui、iFinD、AKShare、同花顺等数据源的授权、登录、CDP 和字段语义不同；不能把源存在写成永久可商用权利。数据源切换还会改变覆盖、复权、时间语义和产品可信度。
3. **数据运维脆弱性**：09-15 盘面主库 fresh，但 finalize 因上游生成段失败；实时/历史窗覆写、空壳非空、日期语义错位是比“表有没有行”更危险的故障。
4. **研究可信度风险**：模型输出漂亮、终态 completed、测试全绿和判官通过都不能代替逐题答案、引用、缺口和过程污染审计。商业化前必须把“研究-only/可认证/未知”做成用户可见状态。
5. **合规边界**：不荐股、不提供买卖点/目标价/自动下单只是必要条件；收费产品还要明确数据授权、客户身份、研究用途、免责声明、留痕和人工复核责任。
6. **团队复杂度**：一人团队同时维护数据接入、DuckDB 换库、RAG、Workbench、模型网关、判官、前端、夜跑和验证系统；这可能形成工程护城河，也可能先成为交付和运营瓶颈，不能直接当资本护城河。

## 六、客观产品判断

当前最准确的定位不是“投教 + 判断日记”，而是：**一个以 A 股市场演变为对象、可调用结构化行情/知识/材料/计算工具，并把证据、反例、缺口、假设和后续验证连接起来的研究 Agent；个人判断校准是可选的复利层。**

即时价值来自：减少跨源检索和整理成本、让历史市场变化可计算、能在材料和盘面之间往返、能显式呈现未知与反例、能把计算和研究产物留存。个人学习闭环不是唯一卖点，也不应被当作“预测准确率已经成立”的替代证据。

但现在仍是**工程能力远超商业验证**：技术面已形成真实产品骨架和若干可复现闭环，产品面尚未证明一组外部用户会持续使用并愿意付费，资本面尚不能凭源码复杂度或历史学员数量得出市场规模/融资结论。

## 七、下一阶段优先级

- 先固定 2–3 个可交付研究任务：历史事件考古与反例、材料改变判断的增量研究、隔日/跨轮研究更新；每个任务定义输入、输出、研究-only 边界、耗时和引用质量。
- 在 UI 显示分层状态：代码存在、生产可达、数据 fresh、模型完成、判官可用、研究结果完整、是否可认证。不要只显示 completed。
- 先修可靠性而不是继续横向加模块：网关退避/并发预算、关键任务隔离、数据源 fallback 与日期语义、夜跑失败可见、生产快照和 KB revision 固定。
- 用邀请制 3–10 名真实研究用户做外部验证，记录重复使用、节省时间、追问率、完成率、纠偏率、引用抽查和主动保存产物；不把“用户觉得有意思”写成付费或投资效果。
- 在数据授权、输出样本专业评估、成本和留痕边界未确定前，不急于收费、不承诺收益、不把个人方法收据包装成市场规律。
