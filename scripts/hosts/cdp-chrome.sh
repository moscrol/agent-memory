#!/bin/zsh
# 启动独立 profile 的 Chrome（--remote-debugging-port）并把当前 DevTools ws 路径
# 写入默认 profile 的 DevToolsActivePort，使 web-access cdp-proxy 能自动发现并连上。
# Chrome 149+ 禁止对默认 profile 用 --remote-debugging-port，故用独立 profile。
# 环境变量：CDP_HEADLESS=1 无头（默认），=0 有头（便于交互登录）；CDP_CHROME_PORT 默认 9222。
set -uo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROF="$HOME/.chrome-cdp-profile"
PORT="${CDP_CHROME_PORT:-9222}"
DTAP="$HOME/Library/Application Support/Google/Chrome/DevToolsActivePort"
PROXY="$HOME/.claude/skills/web-access/scripts/cdp-proxy.mjs"

mkdir -p "$PROF"
if ! curl -s --max-time 3 "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then
  pkill -f "user-data-dir=$PROF" 2>/dev/null; sleep 1
  HEADLESS_FLAG=""
  [ "${CDP_HEADLESS:-1}" = "1" ] && HEADLESS_FLAG="--headless=new"
  nohup "$CHROME" $HEADLESS_FLAG --remote-debugging-port="$PORT" \
    --user-data-dir="$PROF" --no-first-run --no-default-browser-check \
    "--remote-allow-origins=*" >/tmp/chrome-cdp.log 2>&1 &
  disown
fi
WSPATH=""
for i in $(seq 1 20); do
  V=$(curl -s --max-time 3 "http://127.0.0.1:$PORT/json/version" 2>/dev/null)
  if [ -n "$V" ]; then
    WSPATH=$(printf "%s" "$V" | python3 -c "import sys,json,urllib.parse as u;print(u.urlparse(json.load(sys.stdin)[\"webSocketDebuggerUrl\"]).path)" 2>/dev/null)
    [ -n "$WSPATH" ] && break
  fi
  sleep 1
done
if [ -z "$WSPATH" ]; then echo "chrome $PORT 未就绪" >&2; exit 1; fi
printf "%s\n%s\n" "$PORT" "$WSPATH" > "$DTAP"
echo "DevToolsActivePort -> $PORT $WSPATH"
if ! curl -s --max-time 3 http://127.0.0.1:3456/targets >/dev/null 2>&1; then
  pkill -f "cdp-proxy.mjs" 2>/dev/null; sleep 1
  nohup node "$PROXY" >/tmp/cdp-proxy.log 2>&1 &
  disown
fi
sleep 3
echo "health: $(curl -s --max-time 5 http://127.0.0.1:3456/health)"
