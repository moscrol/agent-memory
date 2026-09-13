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

- 2026-09-13 · claude · **全天收口**。分支 `feat/advisory-loop`（8 提交，**未合，等你确认**）：`docs/advisory/` 两份 + `docs/specs/` 一份。① 商业模式 advisory：结论**单一订阅 + 分阶段交付 + 测阶段移动**（初版建议分两套价目，被你以"好用就会变资深、是路径两段不是两类人"推翻，已撤回）。关键实测：`offer.yaml` 的 `unit_economics` **无创始人工时列**，131–153 人属现金约束口径，回答不了路线题；且该区间推导过程不在文件内，无法复核。② 提取前置 spec 已到 **rev.3**，你已认可方向、同意进入小规模体验验证（**仅 P0 入口一步**）。③ 未决问题 1（产品同一性）已由你口头关闭，**台账未回写**。
- 2026-09-13 · claude · **spec rev.2 六处修订全部源于你的复核**，每处保留原文并标注为什么错：差异收敛指标**奖励迎合**（与 D-002 方向相反）· `judgment-card` **读反了**（它是要判的，二分改三分：事实必核错 / 框架判断注明定义与适用条件 / 未来假设登记回检）· coverage 只证"讲到了"不证"学会了"（**学习效果归 `validation.md` A 段，缺的是工具不是指标**）· 结构化数据不自动给出教学清单（中间缺内容选择规则）· 跳过率不可直接解释（改事件级记录）· 参考实现的引用校验是**软标记不是硬门禁**（已自核 `socratic-lens` `fidelity.ts@655b1ec`：归一化子串匹配、空引文算通过、`computeCoverage` 不读 `quoteUnverified`）。rev.3 另新增 §4.5「协同进化的另一半」——AI 侧要改变什么 + 用户纠正同样需过证据关口 + 帮助递增打扰递减。

- 2026-09-13 · claude · 建创业顾问回路：`venture-advisor` skill（输出八段契约 + 披露门禁 + 边用边攒沉淀规则）落 `~/.claude/skills/`；开张用例「一人事业 vs 融资路线」落 foresight 仓 `docs/advisory/2026-09-13-one-person-vs-vc-route.md`，门禁通过、变异验证 6/6。核心发现：`offer.yaml` 的 `unit_economics` 无创始人工时列，131–153 人属现金约束口径，**结构上回答不了路线题**；且该区间推导过程未在文件内给出，无法复核。判据已沉淀 [[../10_knowledge/solo-breakeven-needs-founder-hours-column]]。未改 offer.yaml / decisions.md / commitments.md。
