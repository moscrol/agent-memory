#!/usr/bin/env bash
# 判据召回 —— 开工前查库里已经有什么。
#
# 为什么有这个脚本：2026-09-13 单日入库 17 条判据，全程只被调用 1 次。
# 「先检索已有积累再给建议」这条规则早就写在 venture-ops/README.md 里，
# 失效的不是规则，是**没有任何东西触发它**。规则靠记性，机制靠命令。
#
# 用法:
#   scripts/recall.sh 定价 商业模式          # 关键词 OR 搜（标题 / 标签 / 正文）
#   scripts/recall.sh --tag business-model   # 按标签筛
#   scripts/recall.sh --list                 # 列出全部判据标题
#
# 搜索面三层，缺一层就答不全：
#   10_knowledge/   判据——以后能再用什么
#   05_materials/   资料——别人说了什么
#   30_conventions/ 约束与约定——在什么前提下经营 / 怎么协作
#
# （2026-09-14 补第三层：建完当天就发现查不到刚落的经营约束卡。）
#
# **一条都没命中时会明确打印「库内无依据」——那是合法结果。**
# 照实说，不要用模型先验补一个听起来有道理的答案。

set -uo pipefail

VAULT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIRS=("${VAULT}/10_knowledge" "${VAULT}/05_materials" "${VAULT}/30_conventions")

usage() { sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

# 从一篇笔记里取 frontmatter 字段
field() { sed -n "/^---$/,/^---$/p" "$1" | grep -m1 "^$2:" | sed "s/^$2: *//" | tr -d '"'; }

# 打印一条命中：标题 / 标签 / 路径（相对 vault）
show() {
  local f="$1"
  local title tags
  title="$(field "$f" title)"
  tags="$(field "$f" tags)"
  [ -n "$title" ] || title="$(basename "$f" .md)"
  printf '  • %s\n' "$title"
  [ -n "$tags" ] && printf '    %s\n' "$tags"
  printf '    %s\n\n' "${f#${VAULT}/}"
}

[ $# -ge 1 ] || usage 2

MODE="search"
case "$1" in
  -h|--help) usage 0 ;;
  --list)    MODE="list" ;;
  --tag)     MODE="tag"; shift; [ $# -ge 1 ] || { echo "--tag 需要一个标签"; exit 2; } ;;
esac

HITS=0
TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT

case "$MODE" in
  list)
    for d in "${DIRS[@]}"; do
      [ -d "$d" ] || continue
      find "$d" -name '*.md' -type f | sort >> "$TMP"
    done
    ;;
  tag)
    for d in "${DIRS[@]}"; do
      [ -d "$d" ] || continue
      grep -rl --include='*.md' -E "^tags:.*\b$1\b" "$d" 2>/dev/null >> "$TMP"
    done
    ;;
  search)
    for kw in "$@"; do
      for d in "${DIRS[@]}"; do
        [ -d "$d" ] || continue
        grep -rl --include='*.md' -iF -- "$kw" "$d" 2>/dev/null >> "$TMP"
      done
    done
    ;;
esac

sort -u "$TMP" -o "$TMP"
HITS="$(wc -l < "$TMP" | tr -d ' ')"

echo
if [ "$HITS" -eq 0 ]; then
  echo "════ 库内无依据 ════"
  echo
  echo "没有命中任何判据或资料。这是**合法结果**——在输出里如实写「库内无依据」，"
  echo "不要用模型先验冒充已有积累。"
  echo
  echo "如果这次判断值得留下，收工时按 venture-advisor SKILL.md §4 的两轨沉淀："
  echo "  轨 A 外部断言：来源人 + 适用条件 + 什么时候不用（读完顺手写，不验证）"
  echo "  轨 B 自产判断：判据 → 适用条件 → 失效条件 → 与项目的关系"
  exit 0
fi

echo "════ 命中 ${HITS} 条 ════"
echo
while IFS= read -r f; do show "$f"; done < "$TMP"

echo "引用纪律：轨 A 的判据必须同时给出**谁说的 + 适用条件 + 当前情况符不符合**。"
echo "只写「根据库内判据」而不交代来源与适用条件，等于把别人的观点洗成自己的结论。"
