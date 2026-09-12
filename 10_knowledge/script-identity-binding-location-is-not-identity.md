---
title: "脚本身份绑定：目录名 / git common-dir / origin URL 都是位置不是身份（仓内脚本通用）"
type: knowledge
agent: claude
source: "finance-workspace-private PR #742 三轮质检（registry 仓根、记忆钩子项目笔记）+ 2026-09-08 origin 改指事故"
date: 2026-09-13
tags: [agent-hooks, tooling, worktree, identity-vs-location, fail-closed]
status: verified
related: ["[[finance-workspace-private]]", "[[agent-tool-design-principles]]"]
---

# 位置不是身份：checked-in 脚本的项目/仓身份必须绑定，不许从位置猜

## 结论

仓内 checked-in 的脚本（钩子、生成器）需要知道「我属于哪个仓 / 哪个项目」时，
**答案只能是常量**——脚本随哪个仓分发，身份就是哪个仓（`__file__` 的仓根）。
目录名、git common-dir 父目录名、origin URL basename 全都是**存放或网络位置**，
会随 clone 改名、worktree 布局、remote 改指而变化；拿它们当身份，失败形状一律是
**读写落到另一棵树/另一个项目，退出码 0，输出看起来完全正常**。

## 三次实撞（同一形状，三种猜法）

1. **2026-09-08** `load-memory.sh` 按 origin URL basename 猜项目名：origin 改指
   `github.com/moscrol/finance.git` 后推出 "finance"，项目笔记整段静默缺席。
2. **2026-09-12** `build_registry.py` 按 `REPOS_DIR / 仓名` 解析：附属 worktree 里
   解析到主检出树，scan 照别树重写注册表、backfill 改写别树 AGENTS.md，exit 0。
   第一修改用 common-dir 父目录名——只修好了标准名主树。
3. **2026-09-13**（质检）独立 clone 改名 `finhot`：registry 与记忆钩子双双按
   common-dir 父目录名失配，注入/回写指向 finhot 项目笔记，两个入口 exit 0。

## 修法（两处已落地，可照抄）

- 仓根/项目身份 = 模块级常量（`_SELF_REPO_NAME = "finance-workspace-private"` /
  `repo="finance-workspace-private"`），删掉全部位置推断代码与 subprocess 探测。
- 同级仓发现等**位置逻辑只用于「别的仓」**，永远不用来回答「我是谁」。
- 行为判据：改名 clone + 同级有效别树/别项目笔记，断言读写只对当前树生效、
  别树哈希不变；**先在缺陷在场时跑红再修**（两轮的失败输出正是生产里那种
  「看起来正常、只是属于另一棵树」的形状）。

## 迁移点

任何「按 cwd / 目录名 / remote 推断自己属于哪个项目」的脚本都可疑。判据一句话：
**把这个仓改个名字放到另一台机器上，它的行为还指向同一个项目吗？**
