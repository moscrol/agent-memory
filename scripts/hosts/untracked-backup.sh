#!/usr/bin/env bash
# 孤本备份：vault 内「不入 git 但不可再生」目录的每日 tar 快照。
#
# 为什么存在（2026-08-12）：60_dialogues/（44 轮外部 AI 对话原文）与 .foresight/
# （活进程持续追加的运行时台账）都被 .gitignore 排除——排除的判据成立（见
# .gitignore 内注释），但代价是 vault 的同步链路（launchd auto-sync 只推 git 内容）
# 覆盖不到它们，磁盘即单副本。本脚本补上那条独立备份路径。
#
# 「可证伪点回检/」不在备份清单里：它每晚由 verdicts.jsonl 重新生成，可再生的
# 视图丢了就丢了，不值得占快照。
#
# 设计取舍：用日期命名的 tar 快照（append-only），不用 rsync --delete 镜像——
# 镜像会把误删同步进备份；快照多占点空间（两个目录合计 <10MB 量级），换来
# 「任意一天的状态都能回去」。同日重跑幂等覆盖当日份。
#
# 部署（Mac，一次性）：
#   cp scripts/hosts/untracked-backup.sh ~/bin/ && chmod +x ~/bin/untracked-backup.sh
#   然后建 ~/Library/LaunchAgents/com.a77.agent-memory-backup.plist，
#   ProgramArguments 指向 ~/bin/untracked-backup.sh，StartCalendarInterval 定每天
#   04:10（避开 03:50 的回检任务），launchctl load -w 生效。
#   注意 scripts/hosts/ 的边界（见本目录 README）：运行位置是 ~/bin，这里是快照；
#   改了 ~/bin 的版本要手动同步回来。
#
# 环境变量（均有默认值）：
#   AGENT_MEMORY_VAULT        vault 根，默认 ~/agent-memory
#   AGENT_MEMORY_BACKUP_DIR   备份目的地，默认 ~/Backups/agent-memory-untracked
#                             （建议指到 iCloud/外置盘等第二块介质，否则仍是同盘）
#   AGENT_MEMORY_BACKUP_KEEP  每个目录保留的快照份数，默认 30
set -euo pipefail

V="${AGENT_MEMORY_VAULT:-$HOME/agent-memory}"
DEST="${AGENT_MEMORY_BACKUP_DIR:-$HOME/Backups/agent-memory-untracked}"
KEEP="${AGENT_MEMORY_BACKUP_KEEP:-30}"
STAMP="$(date +%Y-%m-%d)"

mkdir -p "${DEST}"

for d in 60_dialogues .foresight; do
  src="${V}/${d}"
  [ -d "${src}" ] || { echo "skip: ${src} 不存在"; continue; }
  name="${d#.}"
  out="${DEST}/${name}-${STAMP}.tar.gz"
  # 先写临时文件再原子改名，避免中断留下半截快照被当成完整备份
  tar -czf "${out}.tmp" -C "${V}" "${d}"
  mv "${out}.tmp" "${out}"
  # 按份数裁剪（保最近 KEEP 份），不按日期算——机器停跑几周也不会把仅有的快照删光
  ls -1t "${DEST}/${name}"-*.tar.gz 2>/dev/null | tail -n +"$((KEEP + 1))" | while read -r old; do
    rm -f "${old}"
  done
  echo "$(date '+%F %T') ok: ${d} -> ${out} ($(du -h "${out}" | cut -f1))"
done
