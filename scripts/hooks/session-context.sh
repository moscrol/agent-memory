#!/usr/bin/env bash
# 用户级 SessionStart hook：无论从哪个目录起会话都注入「有什么可读」+「断言纪律」。
#
# 与项目级 finance-workspace-private/.claude/hooks/load-memory.sh 的分工：
#   项目级 —— 会话起在 repo 内时，注入偏好全文 + 该项目笔记全文 + git 现状。
#   本脚本 —— 只注入**索引和纪律**，短、幂等、不重复正文。即使两者同时触发也不冗余。
#
# 存在理由（2026-08-04 实测）：会话起在 /Users/a77（非 git repo）时，项目级 settings
# 不加载、hook 不跑，且脚本的 repo 解析会失败导致「本项目笔记」整段缺失。
# 那一次连续三次把「已有能力」和「刻意约束」误判成缺口。
set -euo pipefail

V="/Users/a77/agent-memory"
[ -d "$V" ] || exit 0   # vault 不可达就静默退出，不打扰

echo "# 开工前索引（用户级 SessionStart 注入）"
echo

# --- 1. 有哪些项目笔记可读 ---
if [ -d "$V/20_projects" ]; then
  echo "## 项目笔记（含背景、关键决策、任务看板、交接记录）"
  for f in "$V"/20_projects/*.md; do
    [ -e "$f" ] || continue
    name="$(basename "$f" .md)"
    [ "$name" = "README" ] && continue
    echo "- \`$f\`"
  done
  echo
  echo "**动手前先读对应项目那份。** 很多「缺口」其实已完成或已有结论，交接记录里也常有"
  echo "已确立的可迁移原则。"
  echo
fi

# --- 2. 能力图谱（回答「我们有没有 X」的权威事实源）---
graph="$V/10_knowledge/finance-agent-capability-graph.md"
if [ -f "$graph" ]; then
  echo "## 金融 Agent 能力图谱（机器可读事实源）"
  echo "- \`$graph\`"
  echo "- 校验：\`python3 $V/scripts/graph_audit.py\`（应 exit 0；非 0 说明图谱已漂移）"
  echo "- 改能力后回写它，**不要另建第二份能力清单**——第二事实源会让下一个 agent 读到过期那份。"
  echo
fi

# --- 3. 断言纪律（这是本 hook 的核心，别删）---
# 正文的 SSOT 在 30_conventions/assertion-discipline.md（2026-08-12 提升为约定），
# 本 hook 只做注入器：跳过 frontmatter 后逐字注入正文。此前纪律正文硬编码在这里，
# 云端 agent 读不到、两处必漂——与「镜像必漂」同一条判据。
disc="$V/30_conventions/assertion-discipline.md"
if [ -f "$disc" ]; then
  awk '/^---$/{c++; next} c>=2{print}' "$disc"
else
  # 兜底：约定文件不可达时退回内置文案，hook 不能因 vault 局部缺失而沉默
  cat <<'RULES'
## 断言纪律（强制）

**"我们没有 X" / "X 还没做" 是负面断言，grep 一个文件搜不到证明不了它。**
三步：全树 grep 同义词 → 读能力图谱 → 读项目笔记看板与交接记录，结论写明查过哪些。
提议「建一份 X」之前先搜 X 存不存在。标注 [实测]/[推断]。先问用户比先搜快。
RULES
fi
echo

# --- 4. 若 cwd 在某个 repo 内，指一下它的笔记 ---
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "${repo_root:-}" ]; then
  remote="$(git -C "$repo_root" remote get-url origin 2>/dev/null || true)"
  if [ -n "${remote:-}" ]; then repo="$(basename "${remote%.git}")"; else repo="$(basename "$repo_root")"; fi
  note="$V/20_projects/$repo.md"
  if [ -f "$note" ]; then
    echo "## 当前 repo：$repo"
    echo "对应笔记 \`$note\`（若项目级 hook 已注入全文，此处仅为指针）"
    echo
  fi
fi
