---
title: 同花顺官方 API 未充分使用的数据与接入优先级
 type: inbox
agent: codex
source: https://fuyao.aicubes.cn/llms-full.txt
 date: 2026-09-21
tags: [inbox, finance, hithink, data-source, research]
status: draft
---

# 同花顺官方 API 未充分使用的数据与接入优先级

> 原始调研产出，待审阅。调查时间为 2026-09-21 01:39-01:45 Asia/Shanghai。没有改业务代码、密钥、账户权限、生产库或定时任务。

## 范围与方法

- [VERIFIED 2026-09-21] 本次针对 `hithink-finance`，官方服务 `https://fuyao.aicubes.cn`，不是另一个 `IWENCAI_API_KEY` 问财入口，也不是旧 iFinD MCP auth_token。官方说明各接入方式共用 API key，但账户权限逐能力判断。来源：[官方 README](https://github.com/HiThink-Tech/Financial-API/blob/main/README.md)。
- [VERIFIED 2026-09-21] 现有主树为旧的 detached HEAD 且有他人未提交改动。实现核对使用本地 `gitea/main@728f327160bbd2485cb635e7ef09d040d718d7b5`，不把旧主树缺文件当成未实现。代码来源：[hithink_client.py](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/market_feature_store/hithink_client.py)、[同步器目录](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/market_feature_store/sync)、[finance_query.py](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/intelligence/services/finance_query.py)。未逐一审遍所有在途分支，不声称穷尽整个账户授权清单。
- [VERIFIED 2026-09-21] 完成 13 次串行只读 GET，间隔至少 0.5 秒，不重试、不下载全市场文件、不请求文档明确未开放能力。13 次均 HTTP 200 / code=0；12 次有业务行或指标，异动为空。实际请求摘要见本文末尾，临时复现脚本 `/tmp/probe_hithink_unused_20260921.py`，机器读数 `/tmp/hithink-unused-probe-20260921.json`。密钥只在内存和官方请求头中使用，未写入文件或打印。来源：[官方 API 规范](https://fuyao.aicubes.cn/llms-full.txt)及下方逐请求 request_id。

## 已经接入但需要保持更新的部分

[VERIFIED 2026-09-21] 对 canonical `/Users/a77/finance-workspace-private/db/market_feature_store.duckdb` 以 `read_only=True` 查询实际行数与日期；结果如下，不从最大日期推断中间日期完整。现有表设计及写者来源：[schema.sql](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/market_feature_store/schema.sql)、[同步器目录](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/market_feature_store/sync)。

| 数据 | 表 | 实际行数 | 最大日期 |
|---|---|---:|---|
| 总盘面 | fact_market_daily | 425 | 2026-09-18 |
| 同花顺个股日 K | fact_stock_daily_hithink | 10,271,528 | 2026-09-08 |
| 同花顺板块/指数日 K | fact_sector_kline_daily | 816,297 | 2026-09-08 |
| 当前成分采集 | fact_sector_constituent_hithink | 119,974 | 2026-09-08 |
| 涨跌停/炸板池 | fact_limit_pool_hithink | 97,388 | 2026-09-08；跌停池最后有行日为 09-07 |
| 龙虎榜 | fact_dragon_tiger_hithink | 17,614 | 2026-09-08 |
| 游资榜 | fact_dragon_hot_money_hithink | 15,699 | 2026-09-08 |
| 历史热股榜 | fact_hot_stock_rank_hithink | 7,260 | 2026-09-08 |
| 竞价 | fact_auction_hithink | 6,554 | 2026-09-08 |

- [VERIFIED 2026-09-21] 竞价已含 5,569 条 snapshot（仅 09-08）及 985 条 benchmark（01-05 至 09-08），不应再把整个竞价接口称作未接。复权表 57,136 条，最大除权日 09-16；除权日可以在未来，不等于该表最近采集时间。来源同上及 [公司行动说明](https://fuyao.aicubes.cn/docs/api-reference/corporate-actions/)。
- [VERIFIED 2026-09-21] `finance_query.py` 已登记热榜、龙虎榜、竞价、同花顺日线读取，`teaching_framework/source_views.py` 有新源与旧源按日补齐。因此分类应为“已接入、当前主库更新落后”，不能说成“没有消费者”。来源：[finance_query.py](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/intelligence/services/finance_query.py)、[source_views.py](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/intelligence/services/teaching_framework/source_views.py)。

## 值得新增的六组数据

以下“未接”限定为上述 main 的业务源码，按端点族检索未发现调用；本轮亦检查了两条财务在途候选的 `market_financials.py` 和 `valuation_estimate.py`，未找到 hithink 接线，不外推全部分支。源码对照：[同步器目录](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/market_feature_store/sync)、[服务目录](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/intelligence/services)。用途、优先级均为 [建议]，不是已建成产品功能。

### 1. 财务三表与五类财务指标

- [VERIFIED 2026-09-21] 利润表、资产负债表、现金流量表均取到真实样本；宁德时代利润表 4 期，资产负债与现金流各 2 期，最新报告期 2026-06-30，带报告期末和披露日。财务指标接口返回成长、盈利、偿债、营运、现金流 5 类共 24 项，其中 23 项非空。来源：[财务三表](https://fuyao.aicubes.cn/docs/api-reference/financials/)、[财务指标](https://fuyao.aicubes.cn/docs/api-reference/financial-indicators/)及请求 income/balance/cashflow/financial_indicators。
- [VERIFIED 2026-09-21] 我们已有财务能力，主来源为东财 F10、后备新浪与 AKShare，不是“项目没有财务数据”。同花顺属于新增正规数据源与交叉核验源。来源：[market_financials.py](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/intelligence/services/market_financials.py)。
- [建议] 用于检验利润增长是否有经营现金流支持、应收增长是否高于收入、研发及资本开支的边际变化，接已有个股深挖与财报回答链。保留两家供应商差异，不静默覆盖。
- [VERIFIED 2026-09-21] 金额为原币元，EPS 为元/股；`total_debt` 实际是负债合计，不等于有息债务。`quarterly` 表示季度末报告期，不证明利润和现金流是单季度值；应先与原报表核对累计/单季口径。只依据披露日还不足以证明历史版本没有被重述。来源：[财务三表](https://fuyao.aicubes.cn/docs/api-reference/financials/)。

### 2. 当前估值快照

- [VERIFIED 2026-09-21] 两只股票各 5 个估值字段均非空：市盈率 PE 的 TTM（最近十二个月）与 MRQ（最近披露季度）口径，市净率 PB、市销率 PS、市现率 PCF。一次默认最多 100 个代码，没有历史估值。响应时间是指标元数据最大时间，不代表所有指标同刻刷新。来源：[估值说明](https://fuyao.aicubes.cn/docs/api-reference/valuations/)及请求 valuation。
- [VERIFIED 2026-09-21] 已有估值计算与东财取数；新增的是此 key 的估值备源，不是重建估值引擎。来源：[valuation_estimate.py](http://127.0.0.1:3300/a77/finance-workspace-private/src/commit/728f327160bbd2485cb635e7ef09d040d718d7b5/intelligence/services/valuation_estimate.py)。
- [建议] 每天留快照，供同业比较与未来的历史分位。今天拿到当前 PE，不能立即宣称拿到了该股过去五年 PE 分位。

### 3. 注意力演变：个股排名走势与飙升榜

- [VERIFIED 2026-09-21] 历史热股榜是 Top30；新增 `hot-stock-rank-trend` 不做 Top30 截断。本次宁德时代 09-01 至 09-18 取到 18 个自然日点，前两日排名为 142、107；飙升日榜取到 30 条，均有热度、名次变动和方向字段。来源：[热榜接口](https://fuyao.aicubes.cn/docs/api-reference/hot-list-data/)及请求 heat_trend/skyrocket。
- [建议] 与价格、成交额、题材消息时刻联立，研究“关注度先升还是价格先涨”“放量突破是否已高度拥挤”。名次是关注度，不是资金流；没有消息时序核验，不能称作因果解释。
- [VERIFIED 2026-09-21] 个股排名一年窗，最新榜可选小时或日级。自然日点须与交易日对齐，不能把周末复制点算成新交易样本。来源同上。

### 4. 当日异动归因文本

- [VERIFIED 2026-09-21] 文档提供 `anomaly-analysis-list/stock`，字段含异动标签及 `analysis_content`；仅当天，无历史参数。本次 01:42 请求 code=0 但 0 行，故仅确认鉴权与接口可达，未确认本轮有可用正文。来源：[异动说明](https://fuyao.aicubes.cn/docs/api-reference/anomaly-analysis/)及请求 anomaly。
- [建议] 首先安排交易日盘后小样本验证，然后从当日开始存原文、供应商时间、实际采集时间。供题材发酵回溯、异动解释和晨间关注，不将供应商解读提升为公司公告级事实。

### 5. 公募持仓与 ETF 跟踪指数估值分位

- [VERIFIED 2026-09-21] 沪深300ETF `510300.SH` 当前披露持仓返回 10 条，历史股票持仓请求 2026-06-30 返回 15 条。当前持仓有披露时间字段，但顶层 timestamp=0；历史返回的 `thscode` 缺少交易所后缀，与文档完整代码契约不一致。15 行不能视为沪深300全部成分。来源：[重仓持仓](https://fuyao.aicubes.cn/docs/api-reference/fund-holdings/)、[历史持仓](https://fuyao.aicubes.cn/docs/api-reference/fund-portfolio/)及请求 fund_holdings/fund_history。
- [VERIFIED 2026-09-21] `fund/performance/indicators-historical` 返回 18 个自然日点，其中跟踪指数 PE TTM 五年分位 18 点非空，RSI 与趋势指标各 14 点非空。它是基金跟踪指数的分位，不是该基金所持每只股票的历史估值。来源：[基金业绩指标](https://fuyao.aicubes.cn/docs/api-reference/fund-performance/)及请求 fund_indicators。
- [建议] 用于公募拥挤度、披露期行业配置变化、板块行情的估值背景。基金持仓是披露期事实，不是实时持仓；要看“主动机构偏好”应选主动基金样本，不能用一个被动ETF代表主动机构。
- [建议] “当前公开接口可读”与“可靠入库”分开验收：代码先用权威目录补齐并消歧，核对报告类型、持仓数量和发布时间，缺值不补零。

### 6. 商品联动：期货基差、仓单及持仓

- [VERIFIED 2026-09-21] 官方 CHANGELOG 09-10 新增公开期货与期权能力，晚于我们 09-08 的旧调研。来源：[官方 CHANGELOG](https://github.com/HiThink-Tech/Financial-API/blob/main/CHANGELOG.md)。
- [VERIFIED 2026-09-21] 最新基差接口返回 144 条记录，135 条基差非空；同一主连代码会有多个现货来源，144 不是 144 个独立品种。沪铜 `CU2610.SHF` 09-01 至 09-18 历史仓单返回 14 条，数量及变化均非空。来源：[基差](https://fuyao.aicubes.cn/docs/api-reference/futures-basis/)、[仓单](https://fuyao.aicubes.cn/docs/api-reference/futures-warehouse-receipts/)及请求 futures_basis/futures_warehouse。
- [建议] 基差是现货与期货的价格差，仓单是交易所登记可用于交割货物的凭证；两者帮助交叉观察供需，不能把仓单等同社会总库存。与铜、铝、锂、钢铁、化工等产业链股联立，研究商品价格、交割库存与股票表现是否一致。
- [建议] 按品种核验单位、现货地点/品级、基差正负定义、期货主连换月规则和日夜盘时刻。按 `(合约, 现货指标/来源, 日期)` 留证，不只用 `(合约, 日期)` 覆盖多来源。本轮未做这些经济口径核对，接口成功不代表可直接用于信号。
- [VERIFIED-DOC 2026-09-21] 还有公开期货持仓、日K、分时，以及期权资料、日K、分时；本轮未逐项用 key 实测，不推断隐含波动率、希腊值或完整期权链均可得。来源：[期货总览](https://fuyao.aicubes.cn/docs/api-reference/futures/)、[期权总览](https://fuyao.aicubes.cn/docs/api-reference/options/)、[完整一手文档](https://fuyao.aicubes.cn/llms-full.txt)。

## 后排能力与明确边界

- [VERIFIED-DOC 2026-09-21] 基金净值、收益/回撤、行业配置、经理风格、持有人结构、基金资讯、QDII额度也在公开契约；本轮未逐端点实测。对当前A股复盘主线，优先级低于上述六组，适合以后扩展基金研究。来源：[基金总览](https://fuyao.aicubes.cn/docs/api-reference/funds/)、[完整文档](https://fuyao.aicubes.cn/llms-full.txt)。
- [VERIFIED-DOC 2026-09-21] 主力资金和高频动向明确“暂未开放外部接入”，本轮未尝试。不能拿文档中的路径或示例当成现有 key 可用能力。来源：[主力资金](https://fuyao.aicubes.cn/docs/api-reference/capital-flow/)、[高频动向](https://fuyao.aicubes.cn/docs/api-reference/high-frequency/)。
- [VERIFIED-DOC 2026-09-21] A股分钟K、tick、海外行情、宏观、新闻公告原文和研报不在公开范围。期货/期权公开分时不等于A股分钟K；基金资讯列表不等于全市场公告正文。股票基础信息和按股反查同花顺指数仍是规划页。来源：[官方 README](https://github.com/HiThink-Tech/Financial-API/blob/main/README.md)、[基础信息](https://fuyao.aicubes.cn/docs/api-reference/stock-basics/)、[反查板块](https://fuyao.aicubes.cn/docs/api-reference/ths-index-membership/)。
- [建议] ETF持有人份额、基金净值与二级市场成交额不能代替每日申赎份额变化；本轮未验证到能支撑“ETF当天净流入”的份额序列。供应商源码 MIT 许可不等于行情数据可以商用分发，产品化前单独核服务授权。来源：[官方 README 安全与合规](https://github.com/HiThink-Tech/Financial-API/blob/main/README.md)。

## 建议落地顺序

1. [建议] 先查清同花顺已接数据停在 09-08 的夜跑/部署状态，沿已有 `daily-full` 写入门恢复，不另造第二条写库链。本轮仅发现结果差距，没有诊断停更根因。
2. [建议] 交易日盘后验证并尽早归档当日异动，因为错过后不能回补；并补个股完整排名走势，形成“消息 + 关注度 + 量价”证据。
3. [建议] 财务三表与估值作为现有东财/新浪链的并跑来源，重点验报告期、披露日、累计/单季、单位，不直接切主。
4. [建议] ETF跟踪指数估值分位和少量公募持仓做研究样本；期货先选少量与现有题材相关的品种验证基差与仓单，不一次铺全部资产。
5. [建议] 继续使用项目已有 HTTP 客户端与 DuckDB 数据治理。官方 SDK/marketdb 可作开发参考，但本次没有必要安装并启用另一套数据库，避免双数据根。产品 agent 的权限边界独立审批，不因外部接口可用就直接开放任意外呼。

## 本轮请求收据

所有 URL 基于 `https://fuyao.aicubes.cn`，均 HTTP=200/code=0。只代表列出的标的、参数与时间，不证明全市场覆盖或其他账户权限。

| 名称 | 路径 | 结果 | request_id |
|---|---|---|---|
| valuation | /api/a-share/valuations/snapshot | 2股，5字段全非空 | 6c38553065d2422aa8d397373b121e7f |
| income | /api/a-share/financials/income-statements | 4期 | 008c8d5d50aa419ebfb560d268993f46 |
| balance | /api/a-share/financials/balance-sheets | 2期 | a3c35b46ca6444c6b9530fefb7c07e9c |
| cashflow | /api/a-share/financials/cash-flow-statements | 2期 | 9aaa92d886a74e2e81a6af94eb15250a |
| financial_indicators | /api/a-share/financials/indicators | 24项，23非空 | 5b840c6d019c407ea7b4cf0a79b06622 |
| anomaly | /api/a-share/special-data/anomaly-analysis-list | 0行；凌晨 | 71e755f4499946ffad7d70557e5b8a6b |
| skyrocket | /api/a-share/special-data/skyrocket-list | 30行 | 7deef6bf5e804ce1ace67a3b85b70970 |
| heat_trend | /api/a-share/special-data/hot-stock-rank-trend | 18自然日点 | 8317810ddae6426fa0206e26fdd093e8 |
| fund_holdings | /api/fund/portfolio/holdings | 10行 | 14ee5135c7b84334b78bcc57b937081d |
| fund_history | /api/fund/portfolio/stock-history | 15行，代码缺后缀 | a430de0f039649269134b108572a863c |
| fund_indicators | /api/fund/performance/indicators-historical | 18点，估值分位非空 | 3c8a0ea482124851acd1190bdb3c9e9a |
| futures_basis | /api/futures/basis/main-continuous-latest | 144行，135基差非空 | 8976823c3aee4098b0f6158460a2c7cd |
| futures_warehouse | /api/futures/warehouse-receipts/historical | 14行 | aeba9ff7c757477ab9ba77d053478064 |

## 提炼提示

- 通用审计顺序：供应商契约支持、账户授权可取、字段有值、数据日期正确、代码已接、生产持续更新、真实消费者使用，七件事分别留证。
- 旧清单只是历史快照，新接口可能已上线；反之文档新增页面可能仍是未开放能力。更新前应核官方变更记录和原始契约。
