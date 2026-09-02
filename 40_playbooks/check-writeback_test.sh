#!/bin/sh
# Exercise session-delta writeback gate. Run from anywhere.
set -eu

HOOK="/Users/a77/agent-memory/40_playbooks/check-writeback.sh"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/wb-gate.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

git -C "$tmp" init -q
git -C "$tmp" config user.email test@example.com
git -C "$tmp" config user.name test
printf 'base\n' > "$tmp/app.py"
git -C "$tmp" add app.py
git -C "$tmp" commit -qm init
mkdir -p "$tmp/.agent-memory/20_projects"

run() {
  (cd "$tmp" && "$HOOK" "$@")
}

# leftover dirty, no snapshot → fail open
printf 'leftover\n' >> "$tmp/app.py"
out="$(run </dev/null || true)"
if [ -n "$out" ]; then
  echo "FAIL: leftover without snapshot should allow, got: $out" >&2
  exit 1
fi

# snapshot then chat (no new edit) → allow
run snapshot
out="$(run </dev/null || true)"
if [ -n "$out" ]; then
  echo "FAIL: leftover after snapshot should allow, got: $out" >&2
  exit 1
fi

# new code file after snapshot → block
printf 'x = 1\n' > "$tmp/new.py"
out="$(run </dev/null || true)"
case "$out" in
  *'"decision":"block"'*) ;;
  *) echo "FAIL: new .py after snapshot should block, got: $out" >&2; exit 1 ;;
esac

# ack then allow
run ack
out="$(run </dev/null || true)"
if [ -n "$out" ]; then
  echo "FAIL: ack should allow, got: $out" >&2
  exit 1
fi

# leftover code remains; only ingest data added → allow
run snapshot
mkdir -p "$tmp/wiki/raw/x"
printf 'ingest\n' > "$tmp/wiki/raw/x/note.md"
out="$(run </dev/null || true)"
if [ -n "$out" ]; then
  echo "FAIL: leftover code + new wiki/raw should allow, got: $out" >&2
  exit 1
fi

# editing a leftover code file after snapshot → block
run snapshot
printf 'edited-again\n' >> "$tmp/app.py"
out="$(run </dev/null || true)"
case "$out" in
  *'"decision":"block"'*) ;;
  *) echo "FAIL: editing leftover .py after snapshot should block, got: $out" >&2; exit 1 ;;
esac
run ack

# remind prints the positive rule
remind="$(run remind)"
case "$remind" in
  *问答*|*本窗完成*) ;;
  *) echo "FAIL: remind text missing, got: $remind" >&2; exit 1 ;;
esac

echo "ok"
