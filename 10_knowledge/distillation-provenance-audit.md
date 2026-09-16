---
title: 炼化对账：用「可追溯引用」判定一份原料有没有被蒸馏
type: knowledge
agent: claude
source: 2026-09-16 Knevo 资料盘点会话（finance-workspace-private，PR #749 与 docs/knevo-distill-closeout-0916）
date: 2026-09-16
tags: [knowledge, distillation, provenance, audit, method]
status: verified
stance: evidenced
related: ["[[knevo-reverse-engineering]]", "[[knevo-44turn-rounds15-36-distill-2026-09-16]]", "[[knevo-engineering-probes-2026-08-07]]"]
---

# 炼化对账：用「可追溯引用」判定一份原料有没有被蒸馏

## 结论 / 要点

被问「我沉淀的 X 资料还有没有没炼化的」时，不要读正文找感觉，做一张**原料 → 产物**的血统表（provenance / lineage），判据只有一条：

> 这份原料，有没有任何产物用**编号或路径**指回它？

没有指针就记「未炼化」，不管它看起来多眼熟。眼熟往往是因为同一母本被两条路各编译过一次（本例：风远 94 规则卡与 `reading_baseline.py` 的 25 条同源，但卡的编号 R01–R66 在仓、vault、知识库全零引用）。

## 做法（六步，半小时内）

1. **先分层再点名**。原料通常有四层：原始导出（对话原文 / zip / 截图）、整理语料（qN 文件）、实验记录（E / AB / D 系列）、炼化产物（vault 知识页、仓内 spec、代码里的 `source=`）。每层各列一张清单，缺哪层就查哪层。
2. **以合并目标分支为准，不以手边检出树为准**。主树曾落后 729 个提交，目录里看不到最近三批语料和状态台账；先 `git ls-tree -r --name-only <integration-branch> -- <dir>`，再 `git branch -a --list '*<topic>*'` 把未合分支逐条 `git log --oneline main..<b>` 过一遍——最新的原料几乎总在未合分支上。
3. **引用 grep 而不是内容 grep**。原料若有编号（`R01｜`、`E-008`、`s-67be34ff`）就 grep 编号；有文件名就 grep 文件名；两者都没有的（截图）看有没有产物按日期提到它。内容级的相似不算证据。
4. **每层的「未炼化」都标 [实测] 并写出 grep 范围**。负面断言只对 grep 过的范围成立。
5. **按价值排序而不是按发现顺序**：原始导出层的洞最贵（一份 470KB 原文只蒸了 1/44 轮），实验层的洞最便宜（补一条 verdict）。
6. **产出两样东西**：一张带状态列的对账台账进仓（短摘录即可，原文全文不进 git），加一份「明确不吸收 + 理由」——没有这份，下一个人会把同一堆原料再盘一遍。

## 边界与反例

- 有引用 ≠ 炼化到位：q13 有 `degraded_fallback.py` 指回，q14 只有一句「口径抄 Knevo 信源分层」——后者要再按子项拆（判定四档 / 三层拆解 / 数值权重）才知道吸收了几分之几。
- 引用可能指向已删的路径（vault inbox 会清空、worktree 会拆）。归位时把被引用的原件搬进仓、改指针，别只删。
- 同一母本两条编译路径（运行时检索正文 vs 编译成规则集）会让「已炼化」看起来像「未炼化」，先查 `source=` 标注再下结论。

## 可复用检查清单

- [ ] 四层清单各一张，含未合分支
- [ ] 每份原料一行：编号 / 路径 → 指回它的产物 → 判定 → 建议动作
- [ ] 负面断言带 grep 范围与 [实测]
- [ ] 台账进仓，全文不进仓
- [ ] 「明确不吸收」段写理由
