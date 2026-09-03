---
title: 宣称「没红所以没事」之前先做变异——沉默不是证据，除非你证明它会叫
type: knowledge
agent: cursor
source: finance-workspace-private 实测（2026-08-12 变异串没落盘「测的是空气」/ 08-27 抽数正则与判官死代码 / 08-31 rubric 变异 / 09-03 audit_tool_reachability 恒真初版）+ harness-reference TOOLKIT B 档三条量具陷阱；此前被本 vault MOC 以本文件名引用而无正文
date: 2026-09-03
tags: [knowledge, testing, mutation, gate, methodology, core]
status: verified
related: ["[[evidence-hygiene-three-failure-shapes]]", "[[info-not-delivered-bug-pattern]]", "[[veto-inside-a-continuous-score]]", "[[../20_projects/finance-workspace-private]]"]
---

# 宣称「沉默」之前先做变异

> **失败形状**：把「检查没响」当成「没问题」——测试没红、门禁没拦、判分器没扣分、
> 改动后行为「没变」。沉默有两种来源：确实没问题，或**检查根本没在看**。
> 不做变异（故意改坏、确认它会红），两种沉默长得一模一样。

术语见 [[../30_conventions/glossary]]：变异验证 = 故意改坏被测逻辑，确认检查/测试真的会红——防「永远绿的测试」。
本条讲的是**什么时候必须做**、以及变异本身怎么做假。

## 什么时候必须先变异再下结论

| 你要说的话 | 先做的变异 |
|---|---|
| 「这条测试覆盖了它」 | 把被测行为改坏，测试要红，**并且红在这条** |
| 「门禁上岗了」 | 造一条违规，门禁要拦**并指名哪一条**；带理由的豁免放行、不带理由的仍拦（四项，缺一不可，见 [[evidence-hygiene-three-failure-shapes]]） |
| 「判分器 / 分类器读数可信」 | 把真值打乱，分数要掉；把系统改成「永不触发」，相关计数要归零 |
| 「这次重构是纯等价 / no-op」 | 反向变异：底座忽略领域申请要红，领域回焊底座也要红（双向） |
| 「改了标签就是改了行为」 | 把**真实产出值**喂进消费者、打印结果；不要读代码推断走哪个分支 |

## 实例（都实际发生过）

- **08-12「测的是空气」**：变异用的替换串带了引号前缀、没匹配上，是个 no-op；「测试没红」被当成结论。
  纪律：替换后先 `assert old in s` 再 `assert new != old`，然后才跑测试。同族：变异改出来的字符串
  仍是断言的子串（「方括号包起来」改成「方括号」），测试照样绿——**变异要删整句，不要改一半**。
- **08-27 抽数正则**：`\d{1,3}(?:,\d{3})*|\d+` 这种「千分位在前」的有序交替，在 `26531.66` 上先吃掉
  `265` 就宣告成功，真值永远匹配不上，D1 被判 0.429（修后 0.714 / 打乱 0.286）。读代码看不出来，
  变异抓的。**判分器自身必须先过变异再上岗**，否则所有分数作废。
- **08-27 判官修复第一版是死代码**：改了 `_failure_reason` 保留异常种类，但下游读的是另一个串，
  异常正文根本不进去——生产路径一行行为都没变，而拼串自测的测试跟着同一个误解一起绿。
  判据只有一条：**用真实产出值起判**。
- **08-31 rubric v2**：变异（同文本重复盲评）证伪了自己的第一版——一票否决塞进连续分，方差反而变大，
  见 [[veto-inside-a-continuous-score]]。
- **09-03 `audit_tool_reachability.py` 初版恒真**：实测 0.2s，「快是因为它什么也没验」；
  同日 `audit_dataset_registration.py` 的判据若取自被审计的注册表本身，「没注册的表」按定义是空集，
  门禁恒真。**门禁上岗前自己先过变异**，且判据要独立于被审计物。
- **参照系自己的门禁**：harness-reference `verify_sources.py`（追加一字节 → exit 1）、
  `check_refs.py`（路径改坏 → exit 1，行数改坏 → 报漂移）都是先变异再登记。

## 变异本身怎么做假（量具陷阱）

1. **先清 `__pycache__`**：同字节长度突变 + 同秒内还原，`.pyc` 按 `(mtime, size)` 判缓存有效，
   会伪造出「新回归」——红也可能是假的。
2. **变异必须真的落盘**（见 08-12 实例）。
3. **量具必须覆盖被改的那一步**：消融壳走 legacy 管线，改 episode 链的刀在它上面读不到；
   变异改在量具看不见的地方，永远绿。
4. 变异恢复不用 `git checkout --`（会连别人的在途改动一起冲掉）；用备份文件或精确逆替换。

## 与「信息没送到」的关系

[[info-not-delivered-bug-pattern]] 是「存在 ≠ 送达」；本条是「没响 ≠ 没事」。
两者常一起出现：字段记了没传（没送到），而覆盖率审计 grep 到字段就发绿（没响）——
先变异（把字段删掉，审计该红却不红）就同时暴露两件事。

## 参考

- harness-reference `TOOLKIT.md` B 档「变异验证」与「三条量具陷阱」3/4/5、D+ 消融护具第 3 条
- finance `scripts/run_quality_ablation.py` v3 注释（rubric 变异）；
  `20_projects/finance-workspace-private.md` 2026-08-27 两条 claude 记录（抽数正则 / 判官死代码）
- finance `scripts/audit_tool_reachability.py`、`scripts/audit_dataset_registration.py`（2026-09-03 入 pre-commit）
