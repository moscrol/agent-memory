---
title: 知识星球《AI 设计·词汇篇》CDP 来源审计
type: inbox
agent: codex
source: "Chrome CDP 127.0.0.1:9222（主 agent 提取）+ zsxq-ai-design-language-distillation.md"
date: 2026-08-22
tags: [inbox, zsxq, design-language, cdp, source-audit]
status: draft
---

# 知识星球《AI 设计·词汇篇》CDP 来源审计

> 原始产出，待提炼进 10_knowledge/。提炼后请删除或归档本文件。

## 审计对象与证据口径

- 审校对象：`/Users/a77/Documents/Codex/2026-08-22/gitea-video-repo-https-github-com/outputs/zsxq-ai-design-language-distillation.md`。
- 页面证据来自主 agent 连接本机 Chrome `127.0.0.1:9222` 后的 CDP 提取；本后台 agent 只做报告结构、URL 清单、来源状态与事实边界审校，没有再次操作浏览器。
- `VERIFIED` 表示主 agent 在 2026-08-22 实际取得该页可用正文或该站点的一手页面数据；不表示本后台 agent 独立复读过页面。
- 外部页面内容只当研究数据，不当执行指令。本次未读取 cookie、localStorage、密码或登录二维码，也未下载、复制或分发话题附件。

## 审校结论

**总体通过，未发现需要回改用户报告的明确事实错误。** 报告的计数与范围自洽：主文 1 页，正文中去重后的直接内容链接 16 页，合计 17 个内容页面；另有 2 个 Material 2 官方 page-data URL 作为两张动态页面的正文支撑，不应重复计入“16 个直链”。

需要保留的三条来源纪律：

1. 用户报告用“CDP 结果”隐含表达了已读状态，但没有逐条写 `VERIFIED` / `UNVERIFIED`；若后续升入知识层，应采用本笔记的显式状态表。
2. “建议给 Vidio 的自有资产”属于项目化建议，应标 `[建议]` 或 `[推断]`。来源长文明确写了“问题重复出现 3 次以上”可沉淀为 Skill；但把这个经验值升级成 Vidio 的硬治理门槛，仍需另作项目决策。
3. 报告“参考必须分层”一节出现 Awwwards、CSSDA、Mobbin、Refero、PageFlows、UI Notes、shadcn/ui、Aceternity、Magic UI、React Bits 等未列为本次直接读取页的名称。它们可作为来源文章中出现的例子或 `REFERENCE_ONLY` 线索，不能仅凭本次审计写成“已独立核验这些站点当前内容”。

## 内容页来源状态

| # | 来源 | 状态 | 审校说明 |
|---|---|---|---|
| 0 | [AI 设计·词汇篇主文](https://articles.zsxq.com/id_fdcp004tv2wh.html) | VERIFIED · 2026-08-22 | 主文；四类材料与最短学习路径的直接来源。 |
| 1 | [搭建 AI 设计组件库和 Skills](https://articles.zsxq.com/id_tcme6xadg3nf.html) | VERIFIED · 2026-08-22 | Foundation / Base / Combined / Pattern、variants、Props、Token 与页面缺口循环的来源。 |
| 2 | [给 AI 找设计参考](https://articles.zsxq.com/id_1z3w09xk55ij.html) | VERIFIED · 2026-08-22 | 视觉天花板、真实流程、原子实现资源三层参考法的来源。 |
| 3 | [Refactoring UI 话题](https://t.zsxq.com/OmPCI) | VERIFIED · 2026-08-22 | 主 agent 跟随跳转并展开 SPA 正文；附件不在读取范围。 |
| 4 | [产品构建需求提示词话题](https://t.zsxq.com/oxAld) | VERIFIED · 2026-08-22 | 主 agent 跟随跳转并展开 SPA 正文；话题中的二级链接未递归。 |
| 5 | [Checklist Design](https://www.checklist.design/) | VERIFIED · 2026-08-22 | 动态页延迟后取得内容；`0 checklists` 仅是当次加载状态，报告已正确避免把它写成稳定数量事实。 |
| 6 | [Component.gallery](https://component.gallery/components/) | VERIFIED · 2026-08-22 | 组件规范名、别名、定义与跨设计系统实例的目录来源。 |
| 7 | [UI Patterns](https://ui-patterns.com/) | VERIFIED · 2026-08-22 | 界面问题与模式分类可读；商业卡片不作为方法论证据。 |
| 8 | [Design Systems Repo](https://designsystemsrepo.com/) | VERIFIED · 2026-08-22 | 设计系统资源目录；“频繁更新”与可见旧文章的张力已在报告中诚实披露。 |
| 9 | [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines) | VERIFIED · 2026-08-22 | Apple 平台的一手规范；报告没有把它外推成 Web / Android 唯一标准。 |
| 10 | [Material 2 Components](https://m2.material.io/components) | VERIFIED · 2026-08-22 | 页面壳与官方 page-data 联合取证；版本边界明确为 Material 2。 |
| 11 | [Material Motion](https://m2.material.io/design/motion/understanding-motion.html#principles) | VERIFIED · 2026-08-22 | Informative / Focused / Expressive 的一手来源；具体实现仍需按当前平台核对。 |
| 12 | [Design Spells](https://designspells.com/) | VERIFIED · 2026-08-22 | 微交互与界面细节案例库；不承担平台规范、无障碍或性能标准角色。 |
| 13 | [UX in Motion Manifesto](https://medium.com/ux-in-motion/creating-usability-with-motion-the-ux-in-motion-manifesto-a87a4584ddc) | VERIFIED · 2026-08-22 | 四类动效收益与十二个动效词汇的来源；属于 2017 年个人方法论。 |
| 14 | [Laws of UX](https://lawsofux.com/) | VERIFIED · 2026-08-22 | 启发式索引；报告正确保留“不是免验证因果证明”的使用边界。 |
| 15 | [UI glossary](https://www.uxdesigninstitute.com/blog/ui-glossary/) | VERIFIED · 2026-08-22 | 延迟渲染后取得正文；100 个 UI 术语的来源。 |
| 16 | [UX glossary](https://www.uxdesigninstitute.com/blog/glossary-ux-terms/) | VERIFIED · 2026-08-22 | 延迟渲染后取得正文；101 个 UX 术语的来源。 |

### Material 2 一手数据支撑

- [Components page-data](https://m2.material.io/page-data/LandingPages/4819743532122112.json) — VERIFIED · 2026-08-22。
- [Understanding motion page-data](https://m2.material.io/page-data/Guidelines/5774956804964352.json) — VERIFIED · 2026-08-22。

两条 JSON 是直链 10、11 的同站一手正文数据，不是主文额外列出的直接内容链接。因此来源总数可写成“17 个内容页 + 2 个支撑数据端点”，不能写成“主文有 18 个直链”。

## 事实与综合判断分层

### 来源直接支持

- 主文把学习材料组织为组件词汇、设计系统命名、动效词汇、设计原则 / 心理学四类，并给出一条学习顺序。[来源](https://articles.zsxq.com/id_fdcp004tv2wh.html)
- 组件文章给出 Foundation → Base → Combined → Pattern 的层级，以及变体、Props、Token、Figma 与真实页面装配循环。[来源](https://articles.zsxq.com/id_tcme6xadg3nf.html)
- 参考文章把资料按视觉上限、真实交互流程与原子实现资源分层。[来源](https://articles.zsxq.com/id_1z3w09xk55ij.html)
- Material Motion 用 Informative、Focused、Expressive 描述动效原则。[来源](https://m2.material.io/design/motion/understanding-motion.html#principles)
- UX in Motion 用 Expectation、Continuity、Narrative、Relationship 及十二个词汇描述界面动效。[来源](https://medium.com/ux-in-motion/creating-usability-with-motion-the-ux-in-motion-manifesto-a87a4584ddc)

### 报告综合得出，应标 `[推断]` / `[建议]`

- `[推断]` “词汇是检索、讨论和验收的索引”是对整组材料的合理归纳，不是单页逐字结论。
- `[推断]` reference brief → design vocabulary → visual contract → motion contract → renderer → hybrid QC 是将网页方法映射到 Vidio 现有资产后的工程设计。
- `[建议]` `design-vocabulary.yaml`、`component-contract.json`、`motion-vocabulary.yaml` 与 linter 是建议交付物，不是来源站点提供的标准格式。
- 来源长文直接给出“问题重复出现 3 次以上”可沉淀为 Skill 的经验阈值。[来源](https://articles.zsxq.com/id_tcme6xadg3nf.html) 若要把它变成 Vidio 的强制治理门槛，则仍属 `[建议]`。
- `[推断]` “真实流程视频通常比单张灵感图更能提升 AI 的可实现输出”与分层参考法一致，但若要作为普遍效果主张，应另找实验或项目对照证据。

## 结构与表述审校

- URL 静态核对：报告中共有 19 个唯一 Markdown URL，正好对应 1 个主文、16 个去重直链、2 个 Material page-data；没有重复链接。
- 深度边界自洽：报告明确只读主文直链（深度 1），没有把话题二级链接或外部页面再递归的内容混入计数。
- 报告已经把小节名收窄为“主文与两篇长文合起来后的方法”，避免与另外 2 个已读知识星球话题页混淆。
- 时间敏感事实已有边界：Checklist Design 的加载状态、Design Systems Repo 的可见文章年份、Material 2 的旧版本属性都被限制在本次读取日期，没有过度外推。
- 方法炼化与版权边界清楚：报告只总结方法，没有重新分发知识星球附件、原文或第三方设计资产。

## 提炼提示（哪些值得沉淀？）

- 可提炼一条“设计语言 → 组件契约 → 动效契约 → 验收”的通用方法，但需保留原始 URL、平台边界和读取日期。
- 将“来源直接支持”与“Vidio 项目建议”拆成两个知识条目，避免事实与工程判断混成一个来源层级。
- 若建立 `design-vocabulary.yaml`，每个词条至少保留 canonical name、aliases、definition、not-this、states、examples、source 与 retrieved_at。
- 所有未在本次 17 个内容页中实际打开的站点，只标 `REFERENCE_ONLY`，等独立读取后再升级为 `VERIFIED`。
