#!/bin/bash
# Restart exec-server if it is unresponsive (hang) or down.
# Liveness: any HTTP reply (even 401) = alive; curl non-zero exit (refused/timeout) = dead.
UID_N=$(id -u)
curl -s -o /dev/null --max-time 8 http://localhost:28080/api/ping
if [ $? -ne 0 ]; then
  /bin/launchctl kickstart -k gui/$UID_N/com.industry7view.exec-server
  /usr/bin/logger -t finhot-watchdog "exec-server unresponsive -> kickstarted"
fi
# Ensure tunnel process alive
if ! /usr/bin/pgrep -f "cloudflared.*a77-exec" >/dev/null 2>&1; then
  /bin/launchctl kickstart -k gui/$UID_N/com.industry7view.exec-tunnel
  /usr/bin/logger -t finhot-watchdog "cloudflared down -> kickstarted tunnel"
fi
