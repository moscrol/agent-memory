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

## Worktree 隔离不隔离共享 hook 的副作用（2026-09-18 补证）

项目身份与**此次允许写入的工作树**是两层：前者绑定脚本，后者还须验证调用者是否有权
触发该树的维护。多个 worktree 共享 `.git/hooks`，其中一个写死主树绝对路径的 post-checkout，
会在创建“隔离树”时照样更新主树。KB 检索修复实撞两次：旧钩子后台刷新普通生产索引，
虽嵌入零块，构建时间与索引文件仍发生写入。详见知识库
`docs/handoffs/2026-09-18-agent-retrieval-reliability.md`。

- **先审 hook 再建 worktree**，不只看 post-commit；post-checkout/post-merge 也可能写库或外呼。
- 脚本自己的写入根仍由自身位置确定；另将调用树的物理路径与它比较，不一致就跳过。
  cwd 在这里仅用于核验副作用权限，不用于猜项目身份。
- 尚未上线修复时，worktree 内的新脚本不能保护主树旧钩子。只对当前 Git 命令设临时
  `core.hooksPath`，原样保留 pre-commit 等安全检查，隔离有写入副作用的 post-*；不改共享配置。
  环境开关只有旧脚本已实现才有效，不能凭新文档假定它认识 `RAG_AUTO_UPDATE=0`。
- 测试用临时仓和 fake worker；删除跨树 guard 后必须复现“另树被调用”。提交前后另比生产文件
  哈希，判据是副作用目标，不是 Git exit=0。发现越界后立刻披露具体写入，不用“复用缓存”淡化它。

## 钩子隔离不等于写者隔离（2026-09-18 双索引部署补证）

三个已安装 post-* 都改成维护 skip，真实触发六次且目标文件哈希未变，只证明**这三个入口**。
后续另一个会话直接运行 `publish_rag_index.py --build --clobber`，仍改写了生产双索引。
全局维护必须盘点并约束目标的所有写者（hook、ingest、手动build/update、publish），而不是
以一个触发器的成功代替发布目标的互斥。证据：金融仓
`docs/handoffs/2026-09-18-kb-dual-index-deploy-blocked.md`。

- 切换前重验目标指纹；不变窗口只对那段窗口有效，不能外推到后来。
- 发现异主并发写入就阻断提升并协调，不杀别人的进程、不把基线改成新值“恢复绿”。
- 冻结代码、冻结资料、独立索引与消费者切换分开：发现并发时可保留已做的隔离计算，
  但不能据此声称生产受保护或检索已恢复。

## 迁移点

任何「按 cwd / 目录名 / remote 推断自己属于哪个项目」的脚本都可疑。判据一句话：
**把这个仓改个名字放到另一台机器上，它的行为还指向同一个项目吗？**
