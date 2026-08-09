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
# 60_dialogues/ holds verbatim transcripts exported from external AI products
# (single files reach ~470KB / 6800 lines).  Those are raw source material, not
# distilled memory: they belong in the vault for reading, but a 3-minute timer
# should not be the thing that decides they enter shared git history.
# 2026-08-09 14:24 (b50db773) did exactly that with two knevo exports before
# anyone had reviewed them.
#
# The db patterns are here as well as in main's .gitignore on purpose: a feature
# branch can be parked on an older .gitignore (this one was), and then `add -A`
# happily commits a 802KB workbench.sqlite3 again.  The staging rule must not
# depend on which branch's ignore file happens to be checked out.
#
# Already-tracked files under these paths stay tracked — this only stops *new*
# and *modified* ones from riding along.
EXCLUDES=(
  ':!60_dialogues'
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

# 2) pull remote with rebase; abort cleanly on conflict (leave for manual fix)
if ! git -c user.name="$NAME" -c user.email="$EMAIL" pull --rebase --autostash origin main; then
  echo "$(ts) [err] pull/rebase failed (conflict?) -- aborting, needs manual resolution"
  git rebase --abort 2>/dev/null
  exit 1
fi

# 3) push if we have unpushed commits
if [ -n "$(git log origin/main..HEAD --oneline 2>/dev/null)" ]; then
  if git push origin main; then
    echo "$(ts) [push] pushed local commits"
  else
    echo "$(ts) [err] push failed"
  fi
fi

echo "$(ts) [ok] sync complete"
