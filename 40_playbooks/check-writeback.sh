#!/bin/sh
# Shared Stop hook for agent-memory writeback.
# Gates only project-level work produced in THIS session.
# Usage:
#   check-writeback.sh           # Stop hook (reads stdin)
#   check-writeback.sh snapshot  # SessionStart: record current git state
#   check-writeback.sh remind    # print the session writeback reminder
#   check-writeback.sh ack       # mark current git state as writeback-ok
set -u

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
repo="$(basename "$repo_root")"

git_dir="$(git -C "$repo_root" rev-parse --path-format=absolute --git-dir 2>/dev/null)" \
  || git_dir="$(git -C "$repo_root" rev-parse --absolute-git-dir 2>/dev/null)" \
  || git_dir="$repo_root/.git"

V="$repo_root/.agent-memory"
[ -d "$V" ] || V="/Users/a77/agent-memory"

stamp_dir="$git_dir/agent-memory"
stamp="$stamp_dir/writeback-ok"
snap="$stamp_dir/session-start-state"
snap_files="$stamp_dir/session-start-files"

state_key() {
  # Status names alone miss "already dirty, then edited again".
  # Hash HEAD + porcelain + patch + untracked mtime/size.
  {
    git -C "$repo_root" rev-parse HEAD 2>/dev/null || true
    git -C "$repo_root" status --porcelain=v1 2>/dev/null || true
    git -C "$repo_root" diff 2>/dev/null || true
    git -C "$repo_root" diff --cached 2>/dev/null || true
    git -C "$repo_root" diff --name-only '@{u}..HEAD' 2>/dev/null || true
    (
      cd "$repo_root" || exit 0
      git ls-files --others --exclude-standard -z 2>/dev/null \
        | perl -0 -ne 'chomp; next unless length; @s=stat $_; print "$s[9] $s[7] $_\n" if @s'
    )
  } | cksum | awk '{print $1 ":" $2}'
}

list_file_fps() {
  python3 - "$repo_root" <<'PY'
import os, subprocess, sys

root = sys.argv[1]

def zsplit(data):
    return [p.decode() for p in data.split(b"\0") if p]

paths = []
cmds = (
    ["ls-files", "-m", "-o", "--exclude-standard", "-z"],
    ["diff", "--cached", "--name-only", "-z"],
)
for args in cmds:
    try:
        paths.extend(zsplit(subprocess.check_output(
            ["git", "-C", root, *args], stderr=subprocess.DEVNULL
        )))
    except subprocess.CalledProcessError:
        pass
try:
    paths.extend(zsplit(subprocess.check_output(
        ["git", "-C", root, "diff", "--name-only", "-z", "@{u}..HEAD"],
        stderr=subprocess.DEVNULL,
    )))
except subprocess.CalledProcessError:
    pass

seen = []
for path in paths:
    if path not in seen:
        seen.append(path)

for path in seen:
    full = os.path.join(root, path)
    try:
        st = os.lstat(full)
        print(f"{path}\t{st.st_mtime_ns} {st.st_size}")
    except OSError:
        print(f"{path}\tmissing")
PY
}

write_snapshot() {
  mkdir -p "$stamp_dir"
  state_key > "$snap"
  list_file_fps > "$snap_files"
}

if [ "${1:-}" = "snapshot" ]; then
  write_snapshot
  exit 0
fi

if [ "${1:-}" = "remind" ]; then
  echo "本窗完成了项目级任务之后，再按 $V/40_playbooks/devin-writeback.md 判断沉淀。问答、身份、只读排查不回写；开窗时已有的脏文件不是本窗任务。"
  exit 0
fi

if [ "${1:-}" = "ack" ]; then
  mkdir -p "$stamp_dir"
  state_key > "$stamp"
  write_snapshot
  exit 0
fi

input="$(cat 2>/dev/null || true)"
case "$input" in *'"stop_hook_active":true'*) exit 0 ;; esac

[ -d "$V" ] || exit 0

note="$V/20_projects/$repo.md"

dirty="$(git -C "$repo_root" status --porcelain 2>/dev/null)"
ahead="$(git -C "$repo_root" rev-list --count '@{u}..HEAD' 2>/dev/null || echo 0)"
if [ -z "$dirty" ] && [ "${ahead:-0}" = "0" ]; then
  exit 0
fi

state="$(state_key)"

# No session baseline → cannot prove this window produced the dirt. Fail open.
if [ ! -f "$snap" ]; then
  exit 0
fi

# Tree unchanged since SessionStart → leftover dirt / chat. Allow.
if [ "$(cat "$snap" 2>/dev/null || true)" = "$state" ]; then
  exit 0
fi

if [ -f "$stamp" ] && [ "$(cat "$stamp" 2>/dev/null || true)" = "$state" ]; then
  exit 0
fi

# Project note recently updated: treat as project-level writeback done.
if [ -f "$note" ] && [ -n "$(find "$note" -mmin -10 2>/dev/null)" ]; then
  exit 0
fi

# Only files this window added or edited count. Leftover dirt is ignored.
now_files="$stamp_dir/session-now-files"
list_file_fps > "$now_files"
if [ -f "$snap_files" ]; then
  changed="$(python3 - "$snap_files" "$now_files" <<'PY'
import sys
start = {}
with open(sys.argv[1], encoding="utf-8") as fh:
    for line in fh:
        line = line.rstrip("\n")
        if not line or "\t" not in line:
            continue
        path, fp = line.split("\t", 1)
        start[path] = fp
with open(sys.argv[2], encoding="utf-8") as fh:
    for line in fh:
        line = line.rstrip("\n")
        if not line or "\t" not in line:
            continue
        path, fp = line.split("\t", 1)
        if start.get(path) != fp:
            print(path)
PY
)"
else
  changed="$( { git -C "$repo_root" status --porcelain 2>/dev/null | sed 's/^...//; s/^.* -> //'; \
               git -C "$repo_root" diff --name-only '@{u}..HEAD' 2>/dev/null; } | sort -u )"
fi

if [ -n "$changed" ]; then
  data_re='(^|/)data/|(^|/)wiki/raw/|(^|/)market_feature_store/exports/|\.(parquet|duckdb|db|sqlite|csv|tsv|jsonl|ndjson|arrow|feather|xlsx|h5|pkl)$'
  non_data="$(printf '%s\n' "$changed" | grep -Ev "$data_re" || true)"
  if [ -z "$non_data" ]; then
    exit 0
  fi
else
  exit 0
fi

ack_cmd="$V/40_playbooks/check-writeback.sh ack"
reason="本窗在 $repo 新增了代码/配置级改动，但还没完成记忆分层处理。请先判断沉淀层级：1) 项目级代码、配置、流程、架构、数据管线决策 → 按 .agent-memory/40_playbooks/devin-writeback.md 追加到 .agent-memory/20_projects/$repo.md 的「交接记录」；2) 稳定且可跨任务复用的方法论 → 提炼进 .agent-memory/10_knowledge/；3) 单次问答评分、用户纠偏、经验样本 → 写入项目内学习层（如 experience_cards.jsonl / corrections.jsonl），不要塞进项目交接记录。问答/身份/只读排查、以及开窗时已有的脏文件，都不回写。若本次已写入学习层或确认无需项目级 agent-memory 回写，请运行：$ack_cmd"
printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')"
exit 0
