#!/usr/bin/env bash
# Mac 一次性收尾：部署孤本备份 launchd + 检查用户级 hook 是否指向 vault 内路径。
#
# 必须在 a77 Mac 上跑（需要 launchd 和 /Users/a77）。云端 / Linux 会拒绝执行。
# 幂等，可重复跑。
#
#   bash /Users/a77/agent-memory/scripts/hosts/install-mac-tail.sh
set -euo pipefail

VAULT="${AGENT_MEMORY_VAULT:-$HOME/agent-memory}"
BIN="${HOME}/bin"
LAUNCH="${HOME}/Library/LaunchAgents"
LABEL="com.a77.agent-memory-backup"
PLIST_SRC="${VAULT}/scripts/hosts/${LABEL}.plist"
PLIST_DST="${LAUNCH}/${LABEL}.plist"
HOOK_CANON="${VAULT}/scripts/hooks/session-context.sh"

if [ "$(uname -s)" != "Darwin" ]; then
  echo "必须在 a77 Mac 上跑（需要 launchd）。到 Mac 执行："
  echo "  bash ${VAULT}/scripts/hosts/install-mac-tail.sh"
  exit 1
fi

if [ ! -f "${VAULT}/scripts/hosts/untracked-backup.sh" ] || [ ! -f "${PLIST_SRC}" ]; then
  echo "vault 不完整：${VAULT}/scripts/hosts/ 缺少 untracked-backup.sh 或 ${LABEL}.plist"
  echo "先等 auto-sync 拉到 main，或 git pull。"
  exit 1
fi

mkdir -p "${BIN}" "${LAUNCH}" "${HOME}/Backups/agent-memory-untracked"

cp "${VAULT}/scripts/hosts/untracked-backup.sh" "${BIN}/untracked-backup.sh"
chmod +x "${BIN}/untracked-backup.sh"
cp "${PLIST_SRC}" "${PLIST_DST}"

# 已加载则先卸，再 load -w，与 sync-setup.md 的运维口径一致
launchctl unload "${PLIST_DST}" 2>/dev/null || true
launchctl load -w "${PLIST_DST}"

echo "=== 立刻跑一次备份 ==="
bash "${BIN}/untracked-backup.sh"

echo
echo "=== 用户级 SessionStart hook 路径 ==="
found=0
for f in "${HOME}/.claude/settings.json" "${HOME}/.claude/settings.local.json"; do
  [ -f "${f}" ] || continue
  if grep -q "session-context" "${f}"; then
    found=1
    echo "在 ${f} 找到："
    grep -n "session-context" "${f}" || true
    if grep -F -q "${HOOK_CANON}" "${f}"; then
      echo "OK: 指向 vault 内路径，纪律改动随 auto-sync 生效。"
    else
      echo "⚠ 没有指向 ${HOOK_CANON}"
      echo "  若这是一份拷贝，本机会话注入的断言纪律会和 30_conventions/assertion-discipline.md 漂移。"
      echo "  把 SessionStart hook 改成该路径后重开会话。"
    fi
  fi
done
if [ "${found}" -eq 0 ]; then
  echo "未在 ~/.claude/settings*.json 找到 session-context（可能配在别处）。"
  echo "期望用户级 SessionStart hook 为："
  echo "  ${HOOK_CANON}"
fi

echo
echo "=== 完成 ==="
echo "每日 04:10 备份 → ${HOME}/Backups/agent-memory-untracked（与 vault 同盘）。"
echo "要第二块介质：export AGENT_MEMORY_BACKUP_DIR=... 后重跑本脚本，或改 plist 加 EnvironmentVariables 再 load。"
echo "看任务：launchctl list | grep agent-memory"
echo "看日志：tail -20 ${HOME}/agent-memory-backup.out.log"
