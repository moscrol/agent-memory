#!/bin/bash
# Auto bidirectional sync for the agent-memory Obsidian vault.
# Commits local edits, rebases on remote, pushes. Run periodically by launchd.
set -uo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

VAULT="/Users/a77/agent-memory"
LOG="/Users/a77/agent-memory-sync.log"
LOCKDIR="/tmp/agent-memory-sync.lockdir"
NAME="kowishiki"
EMAIL="barufaldicoscia341@outlook.com"

ts(){ date "+%Y-%m-%d %H:%M:%S"; }

mkdir "$LOCKDIR" 2>/dev/null || { echo "$(ts) [skip] another run holds lock"; exit 0; }
trap 'rmdir "$LOCKDIR" 2>/dev/null' EXIT

cd "$VAULT" || { echo "$(ts) [err] vault missing: $VAULT"; exit 1; }

# The branch this job is allowed to **push**.  pull/push below name it
# explicitly, so HEAD pointing elsewhere is not a variation — it is a different
# operation with a different blast radius.
SYNC_BRANCH="main"
BRANCH="$(git symbolic-ref --quiet --short HEAD || echo '<detached>')"

# Paths this job must never auto-commit.  Kept as one pathspec list so the
# dirty-check and the staging step can never disagree with each other.
#
# 60_dialogues/ was excluded on 2026-08-09.  On 2026-10-08 the user put it
# back into git so cloud clones can read the Knevo transcripts, including the
# 44-round export that holds the old skill text and tool definitions.
#
# The db patterns are here as well as in main's .gitignore on purpose: a feature
# branch can be parked on an older .gitignore (this one was), and then `add -A`
# happily commits a 802KB workbench.sqlite3 again.  The staging rule must not
# depend on which branch's ignore file happens to be checked out.
#
# 可证伪点回检/ is nightly-generated prose whose own first line says the verdicts
# of record live in verdicts.jsonl — a derived view, regenerable, so it is not
# git content (2026-08-09 user decision; untracked in main by c9f5017c).  It also
# never had frontmatter and only passed vault_lint via SKIP_PATHS, i.e. it was a
# hole in the spec rather than a citizen of it.
#
# .foresight/ is the agent's live runtime ledger: answer_scores / interactions /
# corrections / verdicts / checkpoints append on every question, plus per-run
# trace/stream dumps.  614 files under it were modified in August alone.  A
# 3-minute timer committing an append-only ledger produces one commit per tick
# and nothing anyone will ever diff; worse, the branch-parked copies of these
# files were stale enough that checking out another branch would have *reverted*
# live ledgers (main's corrections.jsonl was 16,686B against 37,574B on disk).
# Untracked in main by dc7282d7 — the files stay on disk, which is what
# FORESIGHT_USERS_DIR in ~/.zshrc points at.
#
# Already-tracked files under these paths stay tracked — this only stops *new*
# and *modified* ones from riding along.
EXCLUDES=(
  ':!可证伪点回检'
  ':!.foresight'
  ':!*.sqlite' ':!*.sqlite3' ':!*.db' ':!*.duckdb'
)

# 1) Snapshot local edits — on WHATEVER branch is checked out.
#
# This deliberately runs before the branch gate.  The first version of that gate
# (2026-08-09 16:36) skipped committing too, and for the next 54 minutes every
# run logged `[skip]` while the Obsidian vault accumulated edits with no local
# snapshot at all.  That traded a visible problem (not pushed) for an invisible
# one (not even versioned).  Losing an edit is worse than carrying an extra
# local commit, so the snapshot is unconditional and only the remote is gated.
if [ -n "$(git status --porcelain -- "${EXCLUDES[@]}")" ]; then
  # 截断告警。**不拦提交，只喊一声**——拦提交会重蹈上面那段修过的错
  # （不提交=编辑没被版本化，比多一个本地提交贵）。内容本来就还在 HEAD 里，
  # 真正的损失从来不是内容，是没人知道。
  #
  # 实测事故 2026-09-04 12:54:42：一次批量内容丢失把 6 个文件写成纯删除
  # （`70_tutor/README.md` → 0 字节，另三个 → 单个 \n），本脚本 **2 秒后
  # 连提交带推送**（12:54:42 [commit] / 12:54:44 [push]）。日志显示同步全程正常，
  # 12:00–12:51 每 3 分钟一次 [ok]——所以这不是同步卡死，是**忠实地把磁盘现状
  # 放大成了共享历史**。四个文件里两个是判据笔记、一个是 sync_toolkit_mirror.py
  # （它一死 TOOLKIT 镜像立刻漂，把 vault_lint 刷红，真信号又被埋进红灯里）。
  # 十天后才被发现。被清掉的那两条笔记之一，标题正是「超时即杀是放大器」。
  emptied="$(git diff --name-only HEAD -- "${EXCLUDES[@]}" 2>/dev/null | while read -r f; do
    [ -f "$f" ] || continue
    [ -n "$(tr -d '[:space:]' < "$f" 2>/dev/null)" ] && continue          # 现在非空白 → 正常
    git cat-file -e "HEAD:$f" 2>/dev/null || continue                     # HEAD 里没有 → 新文件
    [ -z "$(git show "HEAD:$f" 2>/dev/null | tr -d '[:space:]')" ] && continue  # 本来就是空的
    echo "$f"
  done)"
  if [ -n "$emptied" ]; then
    echo "$(ts) [warn] 被追踪文件变成空白，内容仍在 HEAD：git checkout HEAD -- <路径>"
    printf '%s\n' "$emptied" | sed "s|^|$(ts) [warn]   |"
  fi
  git add -A -- "${EXCLUDES[@]}"
  if git -c user.name="$NAME" -c user.email="$EMAIL" commit -q -m "auto-sync: local edits $(ts)"; then
    echo "$(ts) [commit] local edits committed on '$BRANCH'"
  fi
fi

# 2) Only SYNC_BRANCH may talk to the remote.
#
# 实测事故（2026-06-29 21:56 起，launchd 日志累计 10777 次同一错误）：vault worktree 的
# HEAD 停在 `docs/session-tutor-first-principles`，而 pull/push 写死 `origin main`。
# 于是每 3 分钟发生的是「把该 feature 分支的全部本地提交 rebase 到远端 main」——撞
# `20_projects/finance-workspace-private.md` 冲突后 abort，下一轮再撞同一处。
#
# 两个后果都不显眼：① 本地攒到 325 个提交（其中 317 个是本脚本自己产生的
# `auto-sync: local edits <时间戳>`）；② `git push origin main` 推的是**本地 main
# 分支**，不是 HEAD，所以那 325 个提交从机制上就没有被推送过——"同步在跑" 与
# "内容到了远端" 从来不是同一件事。
#
# 更要紧的是这条 feature 分支相对 main 引入了 647 个文件 / 124,431 行，含三份
# vault 红线禁止的 `.foresight/**/workbench.sqlite3`（最大 802KB，已在其提交历史里）。
# 定时任务不能是决定这些内容进入共享历史的那一环。
#
# 恢复指引必须可执行：SYNC_BRANCH 常常是被**另一棵 worktree**占着（git 不允许两棵树
# 同时 checkout 同一分支），此时在本目录 `git switch main` 会直接 fatal。所以这里报出
# 占用者路径，而不是笼统地说"切回 main 即可恢复"。
if [ "$BRANCH" != "$SYNC_BRANCH" ]; then
  holder="$(git worktree list --porcelain 2>/dev/null \
    | awk -v b="branch refs/heads/$SYNC_BRANCH" '/^worktree /{p=substr($0,10)} $0==b{print p; exit}')"
  echo "$(ts) [skip] HEAD 在 '$BRANCH'：已在本地提交快照，但不 pull/push（只有 '$SYNC_BRANCH' 允许碰远端）"
  if [ -n "$holder" ]; then
    echo "$(ts) [skip] '$SYNC_BRANCH' 被 worktree '$holder' 占用，本目录 switch 不过去；要恢复远端同步就在那棵树上同步，或先释放它"
  else
    echo "$(ts) [skip] 恢复：git switch $SYNC_BRANCH"
  fi
  exit 0
fi

# 远端取自仓库自己的约定 remote.pushDefault（30_conventions/preferences.md，2026-08-15 起
# 日常远程是本机 Gitea），不再写死 origin。实测（2026-09-03）：GitHub origin 自 08-14 封禁后
# 一直 404，本脚本每 3 分钟收到 "Repository not found"，[err] 行却写着 "(conflict?)"——
# 把死远端读成了冲突，出错原因从没进过 out.log；gitea/main 停在 08-28，本地 main 攒到
# 81 个未推提交才被人发现。教训同上面那段：「同步在跑」与「内容到了远端」不是一件事，
# 而且错误文案若替 git 猜原因，猜错的那次就是最贵的那次。
REMOTE="$(git config --get remote.pushDefault || echo origin)"

# 2) pull remote with rebase; abort cleanly on failure (leave for manual fix).
#    失败时把 git 自己的 stderr 打进日志，不再替它归因。
if ! pull_out="$(git -c user.name="$NAME" -c user.email="$EMAIL" pull --rebase --autostash "$REMOTE" main 2>&1)"; then
  echo "$(ts) [err] pull/rebase from '$REMOTE' failed -- aborting, needs manual resolution:"
  printf '%s\n' "$pull_out" | tail -n 5 | sed "s/^/$(ts) [err]   /"
  git rebase --abort 2>/dev/null
  exit 1
fi

# 3) push if we have unpushed commits
if [ -n "$(git log "$REMOTE/main..HEAD" --oneline 2>/dev/null)" ]; then
  if git push "$REMOTE" main; then
    echo "$(ts) [push] pushed local commits"
  else
    echo "$(ts) [err] push failed"
  fi
fi

echo "$(ts) [ok] sync complete"
