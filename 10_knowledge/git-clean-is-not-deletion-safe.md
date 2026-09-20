---
title: Git 干净不等于可以删除工作树
type: knowledge
agent: coding-agent
source: finance-workspace-private 2026-09-20 PR803收尾清理，docs/verification/2026-09-20-pr803-merge-cleanup/README.md
date: 2026-09-20
tags: [git, cleanup, data-safety, evidence, fail-closed]
status: verified
---

# Git 干净不等于可以删除工作树

`git status`只承诺它管理范围内的当前改动情况，不承诺目录内所有文件都可再生，也不承诺本地操作历史都已进入main。

## 两种实际反例

1. HEAD已合且status为空，ignored路径仍有用户SQLite、检查点、方法验证收据等。2026-09-20初筛125棵“干净已合”树，74棵因未知忽略内容被保留。不能仅凭存放于旧验收树就断言这些是可丢弃夹具。
2. HEAD已被main包含，reflog（本地Git历史操作记录）中的旧提交却未被main包含。一个候选因此拒删；拆树也会移除私有reflog，不能把HEAD可恢复偷换为历史可恢复。

## 删除边界

- 看板和补丁等价只用来初筛；精确HEAD、全树状态、ignored完整清单、隐藏index标记、子模块、Git锁/操作、reflog的old/new对象都需另查。
- 进程参数、打开文件/工作目录、已加载定时任务、启动器和软链引用必须排除。不存在打开文件不是唯一条件，任务可能尚未启动。
- 未知即保留：不要扩大缓存白名单来提高“清理成功率”。身份稳定再做逐blob核对，移除前重新验证，保持`git worktree remove`不带force、不删分支。
- 先保全私有Git元数据、恢复命令及文件清单，后删除；分批比较refs和工作树注册差集。恢复抽验只证明抽到的样本，不外推为全量演练。
- 生产回滚记录缺端口等归属字段时，多留候选，不替记录猜归属。

## 适用与成本

适合多agent工作树/旧验收检出/运行快照回收，也适合任何“当前版本可重建，所以目录可删”的清理决策。完整逐文件验证成本高于status，但发生在不可逆动作前值得支付；对数据无法认领的目录，拒删比证明无害更便宜。

这是一套风险判据，不是永久删除授权。金融实例的有界执行器、清单、拒删原因、44份元数据和恢复抽验见来源路径；未安装通用或定时prune任务。
