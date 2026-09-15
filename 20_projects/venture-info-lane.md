---
title: 创业商业信息聚合车道
date: 2026-09-15
agent: grok-bot-chief
status: draft
stance: hypothesis
---

# 创业商业信息聚合车道（草案）

目标：复用 FinHot「多源 → 打分 → 摘要 → 时间线」壳体，开一条与金融轨分离的**创业 / 商业模式**车道。Bot 不做爬虫；FinHot（或薄仓）负责聚+滤，Bot 负责晨报进 `agent-memory`、路由给创业顾问 / 内容运营。

## 与金融轨的边界

| | 金融轨（现有 FinHot） | 创业商业轨（本草案） |
|---|---|---|
| 源 | 巨潮/RSS、微博、雪球、公众号、偏交易/产业的 X | 创业者、VC、产品/GTM、OPC 经营、平台算法 |
| 打分 | 披露相关、交易敏感度 | 可复用经营判据、GTM 可验证性、噪音（喊单/情绪）下沉 |
| 下游 | 投研工头、卖方入库、KB | 创业顾问、agent-memory 判据、内容运营（过门禁才发） |

现有 `~/finhot/finhot/watchlist.json` 的 `x` 列表以交易/产业账号为主，**不要直接混进创业车道**；新车道用独立 watchlist 或 `lane: venture` 字段。

## 建议首批源（待你勾选）

### X / Twitter（handle，不带 @）

- `paulg` — Paul Graham
- `levie` — Box CEO / 创业评论
- `andrewchen` — 增长 / a16z
- `lennysan` — Lenny 产品增长
- `shl` — Sahil Lavingia / Gumroad
- `levelsio` — indie hacker
- `swyx` — AI eng / 创业叙事
- `danielgross` — AI 投资
- `garrytan` — YC
- `jason` — Jason Calacanis（噪声高，打分要严）
- `tobyshohag` — 产品
- `jose_perez6` / 可换成你常读的中文创业者账号
- `0xCodez` — Grok Bot / AI agent 实操（你已在跟）
- 预留 5 个你点名的中文创业 / 一人公司账号：`________`

### Newsletter / RSS（填 URL 后进车道）

- Stratechery（若你有订阅源）
- Lenny's Newsletter
- The Generalist / Not Boring（选一个你真读的）
- 你的 Substack 关注列表里「商业模式 / GTM」类 3–5 个

### 明确不进本车道

- 荐股、复盘喊单、纯行情博主（留在金融 FinHot）
- 未过 `assert_published` / content-ops 门禁的对外口径

## 落地步骤（下一刀）

1. 你勾选 / 改掉上面的 handle 与 Newsletter
2. 在 FinHot 增加 `lane: venture`（或独立 `watchlist-venture.json`）
3. 总管例程：工作日早上把高分创业条目摘要写入 `agent-memory/00_inbox/`
4. 需要经营判断时 @创业顾问；可发素材时丢给内容运营起草（发布仍停等你）

## 红线

- 聚合与摘要可自动；**对外发布、改定价、写进「我的经营原则」必须人确认**
- 库内无依据时创业顾问必须说没有，不能把时间线热帖当成已沉淀判据
