#!/usr/bin/env python3
"""Disable Cockpit auto quota refresh for Codex Plus accounts that are out of quota.

Writes ~/.antigravity_cockpit/codex_account_groups.json with quotaRefreshEnabled=false
for exhausted accounts (skips auto/full refresh). Re-run after quotas reset to rebuild.
"""
import json, time, shutil
from pathlib import Path
from datetime import datetime

HOME = Path.home() / ".antigravity_cockpit"

def main():
    accounts = json.loads((HOME / "codex_accounts.json").read_text())
    plus = [a for a in accounts.get("accounts") or [] if (a.get("plan_type") or "").lower() != "api_key" and "apikey" not in (a.get("id") or "")]
    # Prefer newest full backup for quota snapshot
    exhausted = []
    remaining = []
    bak_used = None
    for bak in sorted((HOME / "backups").glob("cockpit_auto_backup_full_*.json"), reverse=True):
        try:
            d = json.loads(bak.read_text())
            codex = d.get("accounts", {}).get("platforms", {}).get("codex", {}).get("exported_data") or []
            if not codex:
                continue
            bak_used = bak.name
            by_id = {a["id"]: a for a in codex if a.get("id")}
            for a in plus:
                src = by_id.get(a["id"])
                if not src:
                    exhausted.append(a); continue
                q = src.get("quota") or {}
                raw = (q.get("raw_data") or {}).get("rate_limit") or {}
                used = (raw.get("primary_window") or {}).get("used_percent")
                allowed = raw.get("allowed")
                limit_reached = raw.get("limit_reached")
                rem = q.get("hourly_percentage")
                empty = (limit_reached is True) or (allowed is False) or (used is not None and used >= 99) or (rem is not None and rem <= 0)
                (exhausted if empty else remaining).append(a)
            break
        except Exception:
            continue
    if not bak_used:
        # no backup: treat all plus as exhausted (safe for reducing OpenAI polling)
        exhausted, remaining = plus, []

    payload = [{
        "id": "group_plus_exhausted_no_refresh",
        "name": "Plus额度已用尽(不自动刷新)",
        "accountIds": [a["id"] for a in exhausted],
        "quotaRefreshEnabled": False,
        "quotaAutoRefreshMinutes": None,
        "order": 0,
        "writer": "desktop",
        "written_at": int(time.time() * 1000),
        "source": "cockpit-disable-empty-plus-refresh",
    }]
    path = HOME / "codex_account_groups.json"
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + f".bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"))
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    note = {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "backup_used": bak_used,
        "exhausted": [{"id": a["id"], "email": a.get("email")} for a in exhausted],
        "still_refresh": [{"id": a["id"], "email": a.get("email")} for a in remaining],
    }
    (HOME / "codex_refresh_policy.json").write_text(json.dumps(note, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(note, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
