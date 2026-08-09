#!/bin/bash
# Launchd entrypoint for cockpit-codex-auth-watchdog.py
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
exec /usr/bin/python3 /Users/a77/bin/cockpit-codex-auth-watchdog.py
