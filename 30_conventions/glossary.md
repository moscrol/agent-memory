---
title: 术语表
type: convention
agent: claude
source: 设计约定；2026-08-12 补库内高频自造术语（此前停在建库当天的 4 条）
date: 2026-08-12
tags: [convention, glossary]
status: draft
---

# 术语表

跨 Agent 统一术语，避免同一概念多种叫法。用户非科班，库内文档里反复出现的自造词/行话都应进表。

## 底座结构

| 术语 | 定义 | 别名/勿用 |
|---|---|---|
| 记忆底座 | 本仓库，跨 Agent 共享的可迁移记忆 | memory base |
| vault | Obsidian 的库，即本仓库根目录 | |
| 黑板 | 各 Agent 读写同一份任务状态的共享层；底座是数据层不是调度器 | blackboard |
| 接入约定卡 | `50_agents/` 里告诉某 Agent 如何读写本库的说明 | agent card |
| MOC | Map of Content，内容地图/目录页；`20_projects/<repo>.md` 就是每个项目的 MOC | 目录页 |
| frontmatter | 笔记开头 `---` 包住的 YAML 元数据（title/type/agent/source/date/tags…），是跨 Agent 互相消费内容的前提 | 文件头 |
| 双链 | Obsidian 的 `[[笔记名]]` 引用；引用其他笔记用它、不复制内容，是 SSOT 的实现手段 | wikilink |
| 交接记录 | 项目 MOC 里「日期·agent·做了什么·指向」的一行索引；正文在 repo 的 `docs/handoffs/`，不写在这里 | |
| playbook | `40_playbooks/` 里的可复用工作流：谁负责哪步、交接物什么格式 | |

## 工作流 / 纪律

| 术语 | 定义 | 别名/勿用 |
|---|---|---|
| SSOT | Single Source of Truth，单一事实源：一个事实只在一个地方维护，别处双链过去 | 事实源 |
| 门禁 | 把纪律硬化成脚本、以退出码（exit 0 通过 / 非 0 失败）判定的检查，如 `vault_lint.py`；相对的是「靠人记得守」的软约定 | exit-code 门 |
| fail closed | 认不出来的值/情况按失败处理，不默认放行；`type: reading-queue` 静默混入就是 fail open 的教训 | 宁错杀 |
| 棘轮式收敛 | 新规范只约束新增、存量不动——像棘轮只进不退，避免一次性重构断掉存量引用 | ratchet |
| preflight | 开工前跑的自检脚本（`preflight.sh`）：注入 git 现状、红线、项目笔记摘要 | |
| hook | agent 生命周期上挂的自动脚本：SessionStart（开窗自动注入记忆）、Stop（结束前拦住没做沉淀判断的会话） | 钩子 |
| 能力图谱 | `10_knowledge/finance-agent-capability-graph.md`，回答「我们有没有 X」的权威事实源，配 `graph_audit.py` 防漂移 | |
| 断言纪律 | 负面断言（「没有 X / 还没做 X」）必须三步验证才能出口；正文在 [[assertion-discipline]] | |
| 变异验证 | 故意改坏被测逻辑，确认检查/测试真的会红——防「永远绿的测试」 | mutation test |
| 活性检查 | 确认改动路径这次真的被执行到了；没执行到的样本不能当证据 | |
| 来源镜像 | canonical 在别处、拷进本库供读取的副本（如 `TOOLKIT.md`）；改内容必须改源头再同步，镜像必漂所以要对表 | mirror |

> 随项目补充。新自造词在文档里站稳（被 ≥2 份笔记使用）就该进表。
