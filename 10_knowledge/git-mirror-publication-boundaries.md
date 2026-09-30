---
title: Git 发布边界要沿镜像链核对
type: knowledge
stance: evidenced
agent: codex
source: Gitea 官方镜像说明与 2026-09-30 双远程实查
date: 2026-09-30
tags: [git, collaboration, publication]
status: verified
related: ["[[finance-workspace-private]]"]
---

## 判据

仓库的 private 字段只描述入口访问权限。发布范围还取决于后续镜像、CI 推送与导出目标；只有沿传播链核实最终可见性，才有依据说“只在私有仓归档”。

## 怎么判定

推送前问：这个 remote 会自动把哪些 refs 或产物送到哪里？检查镜像/CI 配置、目标地址与目标可见性。只输出脱敏配置，不打印带凭据的地址。无法核实时保留本地成果，先明确发布边界。

双端协作另问：独有分支和同名分叉如何保留？先 fetch 保全双方，以普通快进推送和事后读回为基本动作。一个方向的强制镜像不能提供双向协作安全；主干一致也不代表云端工作分支或本地未提交内容一致。

还要查本地远程跟踪日志中的推进与 forced-update。2026-09-30 实查出现两端当前头一致、但它们已一起退回旧版本的情况；从之前取回的记录恢复了两个云端新提交。恢复时先建本地引用与 bundle，再普通快进；不能把这种“当前一致”当作没有丢失推进的证明。

单端缺失还可能来自并行清理。先核删除事件和接替记录，再判断是否创建分支；按另一端清单机械补齐会把刚清理的引用复活。

## 适用条件

多远程、云端 agent、迁移或备份镜像，以及向看似私有的仓库发布内部交接。

## 边界

- 没有配置镜像的仓库不能仅凭本案例认定会外传，需查实际配置。
- 已明确获准公开的内容仍可发布；原则不是禁止多远程协作。
- 移除远程引用只证明分支入口撤下，不能据此认定公开对象、缓存或下载副本已消失。
- 一次 refs 相同的快照不证明并发安全，也不构成后台同步验收。

## 参考

- [Gitea push mirror 说明](https://docs.gitea.com/1.25/usage/repository/repo-mirror/)：强制推送可能覆盖目标变更。
- [本次镜像边界处置](https://github.com/moscrol/finance/blob/8f550d1f97d9c0976267601fede355cff0ebaf5b/docs/handoffs/2026-09-30-remote-mirror-boundary.md)。
