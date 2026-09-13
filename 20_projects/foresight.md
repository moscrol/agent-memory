---
title: Foresight（A 股投研 Agent）
type: project
agent: claude
source: Foresight-BP-v1.2-2026-09-07；产品事实源 2026-09-13 建立
date: 2026-09-13
tags: [project, foresight, finance-agent, product]
status: draft
related: ["[[finhot]]", "[[finance-workspace-private]]"]
---

# Foresight

和你协同进化的 A 股投研 Agent。终局定位是**个人研究校准系统**，不是荐股 App，也不是回答型 Agent。

本页只是**项目入口与索引**。产品事实不在本 vault——避免出现第二套口径。

## 权威位置（改事实改这里，不要改本页）

| 是什么 | 在哪 |
|---|---|
| **产品事实**（用户、能力、对外表达边界） | `/Users/a77/foresight/docs/product.md` |
| **套餐与价格** | `/Users/a77/foresight/docs/offer.yaml`（当前 `status: draft`，**无生效报价**） |
| 决策记录 | `/Users/a77/foresight/docs/decisions.md` |
| 验证记录 | `/Users/a77/foresight/docs/validation.md` |
| 承诺台账 | `/Users/a77/foresight/docs/commitments.md` |
| 营销与销售产物 | `/Users/a77/foresight/gtm/` |
| 对外口径闸门 | `/Users/a77/foresight/scripts/assert_published.sh` |
| **商业建议与路线**（建议，非决策） | `/Users/a77/foresight/docs/advisory/`；门禁与规则在 `venture-advisor` skill |
| BP 与路演材料 | `/Users/a77/Desktop/01-Foresight-BP与路演/` |
| 产品代码 | `finance-workspace-private`（未迁移） |
| 内容执行系统 | `content-ops` 仓库 |

## 当前状态（截至 2026-09-13）

- 外部用户：**0**；产品收入：**0**
- 生效报价：**无**（价格仍属未获批准生效的测试假设）
- 已有自用 Demo；正准备邀请制 Alpha（3–10 人）
- 首批三条内部种子规则**均未获得与基准可区分的支持**，未对外提供

## 未决问题

- [x] ~~content-ops 登记的 `finance_agent` 与 Foresight 是同一产品吗？~~ → **是同一产品**（2026-09-13 用户口头确认）。待办：content-ops 登记名与 `foresight/docs/decisions.md` 尚未回写，招募稿 §3 待确认问题 1 可据此关闭
- [ ] 产品仓库是否入 Gitea 为 `a77/foresight`；代码是否迁移
- [ ] `commitments.md` 中 3 条"待分类"条目：是承诺还是申请陈述
- [ ] 招募草稿的 5 个待确认问题
      → `foresight/gtm/2026-09-13-interview-recruit-draft-v0.1.md`

## 相关知识

- 方法类笔记在 `10_knowledge/`，标签 `finance-agent`
- 商业模式类资料在 `05_materials/`，标签 `business-model` · `pricing`

## 交接记录

（一行一条：`YYYY-MM-DD · <agent> · <一句话>`）

- 2026-09-13 · claude · 建创业顾问回路：`venture-advisor` skill（输出八段契约 + 披露门禁 + 边用边攒沉淀规则）落 `~/.claude/skills/`；开张用例「一人事业 vs 融资路线」落 foresight 仓 `docs/advisory/2026-09-13-one-person-vs-vc-route.md`，门禁通过、变异验证 6/6。核心发现：`offer.yaml` 的 `unit_economics` 无创始人工时列，131–153 人属现金约束口径，**结构上回答不了路线题**；且该区间推导过程未在文件内给出，无法复核。判据已沉淀 [[../10_knowledge/solo-breakeven-needs-founder-hours-column]]。未改 offer.yaml / decisions.md / commitments.md。
