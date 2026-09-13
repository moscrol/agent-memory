#!/usr/bin/env bash
# 随手收集入口 —— 把外部输入落成 00_inbox 里一条合规的 material 草稿。
#
# 这一版只做「存对」，不做「提炼」。提炼由 40_playbooks/knowledge-capture.md 的流程接手。
#
# 用法:
#   scripts/capture.sh "标题" --url <链接> [--text "正文/摘录"] [--file 路径] [--tags a,b]
#   scripts/capture.sh "标题" --text "……"        # 无链接的粘贴内容
#
# 例:
#   scripts/capture.sh "订阅制的三种定价结构" --url https://example.com/post --tags pricing,saas
#
# 幂等：同一天同一 slug 已存在时追加内容，不覆盖。

set -uo pipefail

VAULT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INBOX="${VAULT}/00_inbox"
AGENT_NAME="${CAPTURE_AGENT:-claude}"

TITLE=""; URL=""; TEXT=""; FILE=""; TAGS=""
[ $# -ge 1 ] || { sed -n '2,12p' "$0"; exit 2; }
TITLE="$1"; shift

while [ $# -gt 0 ]; do
  case "$1" in
    --url)  URL="${2:-}";  shift 2 ;;
    --text) TEXT="${2:-}"; shift 2 ;;
    --file) FILE="${2:-}"; shift 2 ;;
    --tags) TAGS="${2:-}"; shift 2 ;;
    *) echo "未知参数: $1"; exit 2 ;;
  esac
done

[ -n "${TITLE}" ] || { echo "标题不能为空"; exit 2; }

# slug：中文保留，空格与标点转 -
SLUG=$(printf '%s' "${TITLE}" \
  | tr '[:upper:]' '[:lower:]' \
  | sed -e 's/[[:space:]]\+/-/g' -e 's/[^0-9a-z一-龥-]//g' -e 's/-\{2,\}/-/g' -e 's/^-//' -e 's/-$//')
[ -n "${SLUG}" ] || SLUG="capture"
DATE=$(date +%Y-%m-%d)
TARGET="${INBOX}/${DATE}-${SLUG}.md"
NOW=$(date +%Y-%m-%dT%H:%M:%S%z)

if [ -n "${FILE}" ]; then
  [ -f "${FILE}" ] || { echo "文件不存在: ${FILE}"; exit 1; }
  [ -n "${TEXT}" ] || TEXT="$(cat "${FILE}")"
fi

TAGLIST='[capture, inbox'
if [ -n "${TAGS}" ]; then
  IFS=',' read -r -a _t <<< "${TAGS}"
  for t in "${_t[@]}"; do TAGLIST="${TAGLIST}, $(printf '%s' "${t}" | tr -d ' ')"; done
fi
TAGLIST="${TAGLIST}]"

if [ -f "${TARGET}" ]; then
  {
    echo ""
    echo "---"
    echo ""
    echo "## 追加捕获 ${NOW}"
    echo ""
    [ -n "${TEXT}" ] && printf '%s\n' "${TEXT}"
    [ -n "${URL}" ]  && printf '\n来源：%s\n' "${URL}"
  } >> "${TARGET}"
  echo "已追加到既有条目：${TARGET#${VAULT}/}"
else
  {
    echo "---"
    printf 'title: %s\n' "${TITLE}"
    echo "type: inbox"
    printf 'agent: %s\n' "${AGENT_NAME}"
    if [ -n "${URL}" ]; then printf 'source: %s\n' "${URL}"; else printf 'source: %s\n' "用户粘贴"; fi
    printf 'date: %s\n' "${DATE}"
    printf 'tags: %s\n' "${TAGLIST}"
    echo "status: draft"
    [ -n "${URL}" ] && printf 'source_url: %s\n' "${URL}"
    echo "stance: author-view"
    echo "---"
    echo ""
    printf '# %s\n\n' "${TITLE}"
    echo "> 待整理。提炼后按 40_playbooks/knowledge-capture.md 归档。"
    echo ""
    if [ -n "${URL}" ]; then
      printf '**来源**：%s\n\n' "${URL}"
    fi
    if [ -n "${TEXT}" ]; then
      echo "## 摘录"
      echo ""
      printf '%s\n' "${TEXT}"
    else
      echo "## 摘录"
      echo ""
      echo "（待补：正文或要点。也可以直接把原文粘到这里。）"
    fi
  } > "${TARGET}"
  echo "已收集：${TARGET#${VAULT}/}"
fi

echo
echo "下一步："
echo "  1) 打开 Obsidian 首页「待整理」视图确认";
echo "  2) 让助手跑「整理与归档」：python3 scripts/refine_material.py --scan";
