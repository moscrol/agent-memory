---
title: 金融 Agent 标准数据源与验鲜探针
type: knowledge
agent: pi
source: finance-workspace-private 路径漂移纠偏及 fix/market-date-advisory-0921 的日期来源回归
date: 2026-09-21
stance: evidenced
tags: [finance-agent, duckdb, data-source, freshness, rag]
status: active
---

# 金融 Agent 标准数据源与验鲜探针

数据驱动 Agent 必须区分：

- **canonical data source**：当前唯一标准数据源；
- **legacy source**：历史脚本或旧阶段遗留数据源；
- **freshness probe**：回答前验证数据最大日期和关键表覆盖。

在 `finance-workspace-private` 当前口径中，标准盘面库是：

```text
/Users/a77/finance-workspace-private/db/market_feature_store.duckdb
```

`db/market.duckdb` 是早期飞书同步阶段的 legacy 路径，不应用于当前问答、个股深挖或复盘前瞻。

## 深挖前最低验鲜

涉及“最新盘面”时，先查：

```sql
select count(*), min(trade_date), max(trade_date) from fact_market_daily;
select count(*), min(trade_date), max(trade_date) from fact_stock_daily;
select count(*), min(trade_date), max(trade_date) from fact_sector_daily;
select count(*), min(trade_date), max(trade_date) from fact_sector_stock_daily;
select count(*), min(trade_date), max(trade_date) from fact_mainline_sector_daily;
```

回答中按来源分别说明实际数据日期，例如“总览截至6月30日、板块截至6月29日”。单表或全库最大值不能代替所有证据的日期；没有执行验鲜，就不能声称用了最新盘面。

## 验鲜不是整体拒答

- 日期差异描述资料状态，不自动取消旧事实。已有真实事实按实际日期继续分析，缺失仅限制依赖它的结论；旧值不能冒充今日值。
- 查询上界由用户信息截止决定，不由总览参照日决定。用户严格历史窗口、未来过滤和资料授权仍独立成立，模型自选旧窗口不能自证最新。
- 来源日、事件日、预期交付日是不同字段。元数据经预取、转文本、证据解析逐层保留；明确未知不能靠正文最大日期或参照日补齐。
- 允许异日事实不等于允许异口径计算。期间、单位、可比性和快照质量独立校验；NULL不当0，日期WARN不升级partial质量。

上述读取行为在 `fix/market-date-advisory-0921@c57ec654` 有正式回归与撤保护测试；未合入或部署，真实模型公开答案尚未验收。实现状态见 [[finance-agent-capability-graph]]，证据见该枝 `docs/handoffs/2026-09-21-market-date-advisory.md`。

## 可迁移原则

这个模式适用于 RAG 索引、日志库、特征库、数据仓库、公告抓取缓存：

1. 先声明标准路径/标准索引；
2. 再用元数据探针验证新鲜度；
3. 最后再进入推理；
4. 旧路径只保留 legacy 说明，避免 agent 被历史文档带偏。
