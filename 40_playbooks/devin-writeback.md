---
title: Agent Memory 分层回写 (任务完成 → 判断沉淀层级)
type: playbook
agent: devin
source: 设计约定
date: 2026-06-28
tags: [playbook, workflow, devin, writeback, core]
status: verified
related: ["[[feature-lifecycle]]", "[[../50_agents/devin]]"]
---

# Agent Memory 分层回写

每次 agent 在某个项目仓库完成任务后，先判断本次产出应该沉淀到哪一层。Agent Memory 负责承接**项目级决策**和**稳定方法论**；单次问答评分、用户纠偏、样本级经验优先进入项目自己的学习层，避免把聊天流水塞进项目交接记录。

## 适用场景
在 `linxiaoqi5111-del` 的任意项目仓库（`finhot` / `finance-workspace-private` / `knowledge-base-private` / `finance-research-site` …）完成一次有项目级产出的任务后，例如开了 PR、改了配置、跑通了流程、排查了问题、改变了数据管线或架构约定。

不适合写入项目交接记录的情况：
- 单次问答打分、一次用户纠偏、一条回答样本。
- 临时对话流水、未验证的主观感受。
- 已经写入项目学习层的经验卡片、纠错样本或评测样本。
- **日常 ingest / 入库批次内容**：年报 baseline、卖方研报、晨汇等例行入库的批次规模、公司清单、log 号、闸门通过情况等均**不沉淀到 vault**——这些已由知识库自身的 `wiki/log.md` 审计层承接。只有当入库过程中产生**可复用经验/流程变更/架构决策**（如 writer 行为坑、merge driver 缺口、log id 撞号教训）时，才写一条只含经验的记录，批次明细用 `wiki/log.md #N` 指向。

这些内容应写到项目内学习层，例如 `experience_cards.jsonl`、`corrections.jsonl`、eval cases；只有当多次验证后沉淀成稳定原则，再提炼进 `10_knowledge/`。

## 前置
- 用有写权限的 GitHub PAT 访问本 vault 仓库 `linxiaoqi5111-del/agent-memory`。
- 按 `30_conventions/frontmatter-spec.md` 写 frontmatter；双链用 `[[文件名]]`，不要裸路径。
- vault 约定**直接 commit 到 `main`**；Mac launchd 每 ~3 分钟双向同步到 Obsidian 库。

## 分层判断
1. **项目层**：代码、配置、流程、架构、数据管线、部署、CI、跨 agent 协作规则的变化 → 写 `20_projects/<repo>.md`。
2. **知识层**：能跨任务复用的稳定方法论、排错范式、系统设计原则 → 写 `10_knowledge/`，并从项目笔记双链过去。
   **文件名必须标明适用范围**（2026-08-12 新增，见下方「知识层的两种粒度」）。
3. **学习样本层**：单次回答评分、用户纠偏、案例样本、问答质量反馈 → 写项目内学习文件，不写项目交接记录。
4. **临时层**：长日志、未整理材料、一次性草稿 → 放 `00_inbox/` 或项目临时目录，不污染 MOC。
5. **ingest 批次层（不写 vault）**：例行入库的批次事实→只记在知识库 `wiki/log.md`；入库中的错误教训→`finance-workspace-private/.claude/lessons_learned.md`（`[kb]` 前缀）；vault 只留可复用经验/决策。

## 知识层的两种粒度（2026-08-12 加）

`10_knowledge/` 里躺着**两类东西**，它们的读者不同：

| 粒度 | 判据 | 命名 | 例 |
|---|---|---|---|
| **跨领域方法论** | **换一个完全不同的领域，这条还成立吗？** 成立 | 无前缀 | `gate-covers-only-its-return-value`、`evidence-hygiene-three-failure-shapes` |
| **领域知识** | 不成立，只在某个项目里有意义 | **`<领域>-` 前缀** | `finance-stock-deep-dive-first-principles` |

**为什么要分**：2026-08-12 实测，31 份里 13 份是 `finance-` 前缀（41%）。现在只有一个领域
在写还看得清；等 kb / dao / video 都往里放，**每个 agent 打开这一层都会先看到一堆
和自己无关的东西**，而它要的方法论淹在里面。

**这不是追认违规**——上面第 2 条写的是「跨**任务**复用」，那 13 份完全合规。
问题是这一层没区分粒度，所以现在补上判据。

### 怎么落

- **只约束新增，存量不动**（棘轮式，见 `harness-reference/BUILD.md` 模式 1）。
  存量重命名会断掉一批 `[[双链]]`，代价大于收益。
- 前缀长在**文件名**上，不另建索引——索引是第二份清单，必漂。
- **这条是判据不是门禁**：「这条知识是不是只在某个领域成立」是语义判断，
  写不成 exit code。所以它靠人守，可靠性天然低于门禁——
  写的时候多问自己一句，比事后审计便宜。

## 交接分两层：一行索引 + 在途正文

**为什么分层**（2026-08-10 实测校准）：本仓交接记录长成了 34 条、平均 **4,836 字节**、
最长单条 **72,795 字节**，占整份项目笔记的 90%——而本规范原本只要求一行（约 50-80 字节），
实际漂了 60-100 倍。同期 `docs/handoffs/` 有 63 份文件 944K 是真的在被 agent 读。

问题不是「写太多」，是**两种用途挤在一个文件里**：

| | 交接记录（本 vault） | `<repo>/docs/handoffs/inflight/<分支>.md` |
|---|---|---|
| 定位 | 索引 / 时间线 | 在途状态 / 接手手册 |
| 长度 | **一行** | 短（≤3K 字节，会被 SessionStart 注入） |
| 内容 | 日期·agent·做了什么·关键决策·指向 | 卡在哪、哪些改动未提交、已验/未验、下一步 |
| 可变性 | 只追加，不覆盖 | **每次覆写**（活文档） |
| 谁读 | 人翻历史、跨 agent 对账 | 接手干活的 agent（**自动注入，不靠记性**） |
| 生命周期 | 永久 | 分支合并即转档为日期快照 |

判据（可迁移）：**一份文档该多长，看它被读的方式，不看它记了多少事。**
只写不读的文档，每个字节都是纯成本——收窄前的交接记录正是「只写不读」（
SessionStart 已明确把它切出注入）。

**为什么按分支分片、而不是一个共享的 `CURRENT.md`**：本仓多棵 worktree 共享同一个
`.git`，同一棵树可有两个 agent 并发、共用一个 git 索引（见各 repo `AGENTS.md` 的
2026-08-07 事故：一次 commit 吞掉另一个 agent 的 4 个在途文件）。单个共享可变文件
就是争用点，后写覆盖先写且冲突发生在 git 层、内容上看不出丢了什么。
按写者分片让并发天然无冲突，与 DB sharding / per-process 日志 / CRDT per-replica log 同理。
白送的好处：`ls inflight/` 就是「当前几件事在飞」，不必另建索引。

## 项目层步骤
1. **定位项目笔记**：`20_projects/<repo>.md`（`<repo>` = 仓库短名）。不存在就用 `_templates/project.md` 新建。
2. **更新任务看板**：在「任务看板」表格里更新本次任务行，`状态` 用 `todo / doing / done / blocked`，PR 链接放「备注」列。
3. **追加交接记录（严格一行）**：在「交接记录」末尾加一行，**正文不写在这里**
   `YYYY-MM-DD · devin · 做了…（关键决策一句）→ PR 链接 / docs/handoffs/<文件>`
   超过两三行就说明该写进 `docs/handoffs/`，这里只留指针。
4. **更新在途交接**：覆写 `<repo>/docs/handoffs/inflight/<分支名，/ 换成 ->.md`，
   只写「接手者需要的」：当前卡点、未提交改动、已验证/未验证、下一步、踩过的坑。
   ≤3K 字节（会被 SessionStart 注入，超出会被截断并声明）。
   分支合并后把它转档成 `docs/handoffs/YYYY-MM-DD-<task>.md` 并删除 inflight 那份。
4. **提炼可复用知识**（仅当有跨任务复用价值时）：在 `10_knowledge/` 用 `_templates/knowledge-note.md` 建条目，`status: verified`，并从项目笔记双链过去。
5. **原始/临时产出**：长日志、未整理的中间结果放 `00_inbox/`，不要塞进项目 MOC。
6. **提交**：只改必要文件，commit message 形如
   `chore(memory): <repo> 回写 <一句话任务>`，push 到 `main`。

## Stop Hook 放行
如果 hook 因为代码/配置改动拦截，但你已经确认本次只需要写项目学习层、或确实没有项目级 Agent Memory 价值，可以按 hook 提示在 repo 根目录写入 `.git/agent-memory/writeback-ok` 的状态戳。本状态戳只对当前 git 状态有效；下一次改动会重新要求判断。

## 红线
- 不写任何密钥/token 到 vault（PAT、CC_REMOTE_EXEC_TOKEN 等一律不落库）。
- 不要把整段代码 diff 贴进笔记——记**结论和决策**，代码看 PR。
- 不要把单次问答评分、用户纠偏和聊天流水写进项目交接记录；这些是学习样本，不是项目 MOC。
- 不要把 ingest/入库批次内容（批次规模、公司清单、闸门结果等）写进交接记录；明细归 `wiki/log.md`，交接只留可复用经验/决策。
- 不删别的 agent 的交接记录；只追加，不覆盖历史。

## 失败/回退
- 任务未完成或被阻塞 → 看板标 `blocked` 并在交接记录写明原因和下一步，不要假装 done。
- 拿不到 vault 写权限 → 在本项目 PR 描述里写清回写内容，并提示人工补录，不要静默跳过。
