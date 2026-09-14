---
title: 维护纪律
type: convention
agent: devin
source: 设计约定
date: 2026-08-12
tags: [convention, maintenance, core]
---

# 维护纪律

底座的价值取决于**持续按规范回写**，而不是搭建本身。下面是必须遵守的最小纪律。

## 生命周期：inbox → knowledge

1. 任何 Agent 的原始产出（搜索结果、长篇分析、临时笔记）先落到 `00_inbox/`，`type: inbox`。
2. **定期回顾**（建议每周或每个项目节点）：把 inbox 里有长期价值的内容**提炼**成 `10_knowledge/` 的条目，标 `status: verified`。
3. 提炼后删除或归档 inbox 原件，保持 inbox 短小。

## Single Source of Truth

- 一个事实只在一个地方维护。其他地方用双链 `[[...]]` 指过去，不复制粘贴。
- 发现重复/冲突时，合并到一条，旧的标 `status: deprecated` 或删除。

## 科普学习资产：先检阅，后落库

`70_tutor/` 保存用户理解概念、原理和技术取舍所需的学习笔记，不保存 Agent 的运行知识。会话收尾时使用 `tutor` skill（手动触发：`@tutor` 或 `@session-tutor`；自然语言“session tutor”也可）：

1. Agent 先讲解一个核心概念并确认用户理解，不改文件；
2. 理解后才生成少量候选摘要；
3. “理解了”不等于批准，用户必须明确批准具体候选；
4. 仅把获批候选按 `_templates/tutor-note.md` 写入并更新索引，未获批内容不进入 vault。

## 写入检查清单（每次写笔记前过一遍）

- [ ] frontmatter 完整（title / type / agent / source / date / tags）
- [ ] 放进了正确的目录（type 与目录一致）
- [ ] 用了 `_templates/` 对应模板
- [ ] 引用其他笔记用双链而非复制
- [ ] 如果是结论/事实，标了 `status`
- [ ] **`10_knowledge/` 的新笔记标了 `stance`**（principle / author-view / ai-distilled /
      hypothesis / evidenced），别把「谁的主张」和「已验证结论」写成同一种东西
- [ ] **判据类笔记写了「怎么判定」与「什么时候我不用它」**——想不出它什么时候不成立，
      说明还没想清楚它在主张什么。项目映射放最后一节、标日期与证据等级，
      **删掉它之后正文必须仍然读得通**（项目会变、读数会过期，判据本体不该跟着烂）
- [ ] 若改动会影响其他 Agent 行为（约定/偏好/agent 卡/playbook），已带 provenance 且经人工审阅（见 [[trust-boundary]]）
- [ ] `70_tutor/` 内容已由用户明确批准，且记录 `reviewed_by` / `reviewed_at`

## 定期维护任务（已脚本化为 exit-code 门）

```bash
python3 scripts/vault_lint.py    # frontmatter 完整性 / type 合法且↔目录一致 / agent 取值合法
                                 # / 死链 / inbox 老化(>14天 WARN) / verified 知识过期(>90天 WARN)
                                 # / 项目笔记 >80KiB WARN / TOOLKIT.md 镜像 pin（sibling 在才对表 canonical）
                                 # / 10_knowledge 认识论棘轮：date>=2026-09-14 的新笔记必须有合法 stance
                                 # / agent 历史豁免：date<2026-09-14 的存量缺 agent 降 WARN（只豁免「缺」不豁免「值不合法」）
                                 # 跳过 SKIP_PATHS：模板、导览页、运行时台账、TOOLKIT.md 的 frontmatter/死链
python3 scripts/graph_audit.py   # 能力图谱节点清单路径防漂移（repo 在本地才校验）
```

- 回写沉淀前、改动 vault 后各跑一遍 `vault_lint.py`，exit 0 才算写入合规。
- push 到 `main` 或开 PR 时，GitHub Actions 工作流 `vault-lint` 会再跑一遍（事后告警，不拦 Mac auto-sync；默认不含 `--strict`，WARN 不红）。
- 改能力图谱或相关仓有结构性合并后跑 `graph_audit.py`。
- Mac 孤本备份与 hook 路径：见 [[../40_playbooks/mac-tail]]。
