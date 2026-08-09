#!/usr/bin/env python3
"""Watchdog: keep Cockpit Codex local-access proxy schedulable.

Symptoms this targets:
  unexpected status 503 ... auth_unavailable: no auth available
  url: http://localhost:57244/v1/responses

Strategy:
  1) Probe /v1/models (cheap) every run
  2) Periodically probe /v1/responses (min payload) to catch "models ok, responses dead"
  3) On auth_unavailable / proxy down / repeated upstream 503: harden config + restart Cockpit
  4) Back off restarts to avoid thrashing when the real upstream is down
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
COCKPIT = HOME / ".antigravity_cockpit"
SIDECAR = COCKPIT / "codex_local_access_sidecar"
CFG_PATH = SIDECAR / "config.json"
MAN_PATH = SIDECAR / "manifest.json"
SRC_PATH = COCKPIT / "codex_local_access.json"
CODEX_TOML = HOME / ".codex" / "config.toml"

LOG_PATH = Path("/tmp/cockpit-codex-auth-watchdog.log")
STATE_PATH = Path("/tmp/cockpit-codex-auth-watchdog-state.json")

PROXY_PORT = 57244
PROXY_BASE = f"http://127.0.0.1:{PROXY_PORT}"

# Don't restart more often than this when failures persist
MIN_RESTART_INTERVAL_SEC = 600  # 10 min; avoid storming ChatGPT quota on restart
# Full responses probe interval (token cost)
RESPONSES_PROBE_INTERVAL_SEC = 900  # 15 min
# How many consecutive soft failures before restart
FAIL_THRESHOLD = 3


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def log(msg: str) -> None:
    line = f"[{now_iso()}] {msg}"
    print(line, flush=True)
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass
    try:
        subprocess.run(
            ["/usr/bin/logger", "-t", "cockpit-codex-watchdog", msg[:200]],
            check=False,
            capture_output=True,
        )
    except OSError:
        pass


def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "consecutive_fails": 0,
        "last_restart_ts": 0,
        "last_responses_probe_ts": 0,
        "last_ok_ts": 0,
        "last_error": "",
    }


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def client_token() -> str | None:
    if not CODEX_TOML.exists():
        return None
    text = CODEX_TOML.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'experimental_bearer_token\s*=\s*"([^"]+)"', text)
    if m:
        return m.group(1)
    # fallback: cockpit config api-keys
    if CFG_PATH.exists():
        try:
            cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
            keys = cfg.get("api-keys") or []
            if keys and isinstance(keys[0], str):
                return keys[0]
        except Exception:
            pass
    return None


def http_json(method: str, url: str, token: str, body: dict | None = None, timeout: float = 20.0):
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                parsed = json.loads(raw.decode("utf-8", errors="replace"))
            except Exception:
                parsed = {"_raw": raw[:300].decode("utf-8", errors="replace")}
            return resp.status, parsed, ""
    except urllib.error.HTTPError as e:
        raw = b""
        try:
            raw = e.read()
        except Exception:
            pass
        text = raw.decode("utf-8", errors="replace")
        try:
            parsed = json.loads(text) if text else {}
        except Exception:
            parsed = {"_raw": text[:400]}
        return e.code, parsed, text
    except Exception as e:
        return 0, {}, str(e)


def classify(status: int, payload: dict, err: str) -> str:
    blob = json.dumps(payload, ensure_ascii=False) + " " + (err or "")
    low = blob.lower()
    if status == 0 and ("refused" in low or "timed out" in low or "timeout" in low):
        return "proxy_down"
    if "auth_unavailable" in low or "no auth available" in low:
        return "auth_unavailable"
    if status in (401, 403):
        return "auth_rejected"
    if status == 503 and "auth" in low:
        return "auth_unavailable"
    if status == 503:
        return "upstream_503"
    if status and status >= 500:
        return "upstream_5xx"
    if status and 200 <= status < 300:
        return "ok"
    return f"other_{status or 'err'}"


def port_open(port: int) -> bool:
    import socket

    s = socket.socket()
    s.settimeout(1)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()


def cliproxy_running() -> bool:
    out = subprocess.getoutput("pgrep -f 'cockpit-cliproxy.*codex_local_access' || true")
    return bool(out.strip())


def harden_sidecar_config() -> list[str]:
    """Best-effort config repairs that reduce false auth_unavailable after long runs."""
    actions: list[str] = []
    if not CFG_PATH.exists():
        return actions
    try:
        cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        actions.append(f"config_read_fail:{e}")
        return actions

    changed = False
    if cfg.get("disable-auth-auto-refresh") is True:
        cfg["disable-auth-auto-refresh"] = False
        changed = True
        actions.append("enable_auth_auto_refresh")

    if int(cfg.get("max-retry-credentials") or 0) < 4:
        cfg["max-retry-credentials"] = 6
        changed = True
        actions.append("max_retry_credentials=6")

    if int(cfg.get("request-retry") or 0) < 2:
        cfg["request-retry"] = 2
        changed = True
        actions.append("request_retry=2")

    routing = cfg.get("routing") or {}
    if routing.get("session-affinity") is not True:
        routing["session-affinity"] = True
        cfg["routing"] = routing
        changed = True
        actions.append("enable_session_affinity")

    for item in cfg.get("codex-api-key") or []:
        if isinstance(item, dict) and not item.get("disable-cooling"):
            item["disable-cooling"] = True
            changed = True
            actions.append("disable_cooling_on_api_keys")

    # Ensure client token maps to currently listed API accounts (both id styles)
    token = client_token()
    api_ids: list[str] = []
    if MAN_PATH.exists():
        try:
            man = json.loads(MAN_PATH.read_text(encoding="utf-8"))
            for a in man.get("accounts") or []:
                if a.get("authKind") == "api_key" or a.get("planType") == "API_KEY":
                    if a.get("id"):
                        api_ids.append(a["id"])
            # also short ids from existing mapping if any
            for k in man.get("apiKeys") or []:
                for aid in k.get("accountIds") or []:
                    if aid not in api_ids:
                        api_ids.append(aid)
        except Exception:
            pass

    # Only patch account-id mapping when empty/missing for this client token.
    # Cockpit often uses short ids like "codex:apikey:xxxx"; overwriting them
    # with full ids can break routing until the next Cockpit restart.
    if token:
        aki = cfg.get("api-key-account-ids") or {}
        cur = list(aki.get(token) or [])
        if not cur and api_ids:
            aki[token] = list(api_ids)
            cfg["api-key-account-ids"] = aki
            changed = True
            actions.append("fill_empty_api_key_account_ids")

    if changed:
        bak = CFG_PATH.with_name(CFG_PATH.name + f".bak-watchdog-{int(time.time())}")
        try:
            bak.write_text(CFG_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception:
            pass
        CFG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        actions.append("config_written")

    # Source of truth: keep API-only pool if already API-only; clear stale bound oauth
    if SRC_PATH.exists():
        try:
            src = json.loads(SRC_PATH.read_text(encoding="utf-8"))
            src_changed = False
            if src.get("boundOauthAccountId"):
                # only clear if pool has no oauth accounts
                ids = src.get("accountIds") or []
                if ids and all("apikey" in str(i).lower() for i in ids):
                    src["boundOauthAccountId"] = None
                    src_changed = True
                    actions.append("clear_bound_oauth")
            if src.get("sessionAffinity") is True:
                src["sessionAffinity"] = False
                src_changed = True
            if int(src.get("maxRetryCredentials") or 0) < 4:
                src["maxRetryCredentials"] = 6
                src_changed = True
            for k in src.get("apiKeys") or []:
                if isinstance(k, dict) and k.get("boundOAuth") is True:
                    # if only api keys in pool, unbind oauth requirement
                    ids = src.get("accountIds") or []
                    if ids and all("apikey" in str(i).lower() for i in ids):
                        k["boundOAuth"] = False
                        src_changed = True
                        actions.append("apiKeys.boundOAuth=false")
            if src_changed:
                src["updatedAt"] = int(time.time() * 1000)
                SRC_PATH.write_text(json.dumps(src, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                actions.append("source_written")
        except Exception as e:
            actions.append(f"source_repair_fail:{e}")

    return actions


def restart_cockpit() -> bool:
    """Restart Cockpit Tools so cliproxy reloads config and clears sticky bad state."""
    log("restart: quitting Cockpit Tools")
    subprocess.run(
        ["osascript", "-e", 'tell application "Cockpit Tools" to quit'],
        check=False,
        capture_output=True,
    )
    # ensure processes die
    time.sleep(2)
    subprocess.run(["pkill", "-f", "Cockpit Tools.app/Contents/MacOS/cockpit-tools"], check=False)
    subprocess.run(["pkill", "-f", "cockpit-cliproxy.*codex_local_access"], check=False)
    time.sleep(2)
    log("restart: opening Cockpit Tools")
    subprocess.run(["open", "-a", "Cockpit Tools"], check=False)
    # wait for proxy
    for i in range(30):
        if cliproxy_running() and port_open(PROXY_PORT):
            log(f"restart: cliproxy up after {i+1}s")
            return True
        time.sleep(1)
    log("restart: cliproxy did not come up in time")
    return False


def main() -> int:
    state = load_state()
    token = client_token()
    if not token:
        log("skip: no client bearer token in ~/.codex/config.toml")
        return 0

    if not cliproxy_running() or not port_open(PROXY_PORT):
        log("detect: cliproxy/port down")
        state["consecutive_fails"] = int(state.get("consecutive_fails") or 0) + 1
        state["last_error"] = "proxy_down"
        actions = harden_sidecar_config()
        if actions:
            log("repair: " + ",".join(actions))
        now = time.time()
        if now - float(state.get("last_restart_ts") or 0) >= MIN_RESTART_INTERVAL_SEC:
            if restart_cockpit():
                state["last_restart_ts"] = now
                state["consecutive_fails"] = 0
        save_state(state)
        return 0

    # cheap probe
    st, payload, err = http_json("GET", f"{PROXY_BASE}/v1/models", token, timeout=10)
    kind = classify(st, payload, err)
    log(f"probe models -> {kind} http={st}")

    # occasional responses probe
    now = time.time()
    do_resp = (now - float(state.get("last_responses_probe_ts") or 0)) >= RESPONSES_PROBE_INTERVAL_SEC
    resp_kind = None
    if do_resp or kind != "ok":
        # Use a tiny request; if models already auth-fail, skip spending
        if kind == "ok" or kind.startswith("other") or kind == "upstream_503":
            st2, payload2, err2 = http_json(
                "POST",
                f"{PROXY_BASE}/v1/responses",
                token,
                body={"model": "gpt-5.6-sol", "input": "ping", "store": False},
                timeout=45,
            )
            resp_kind = classify(st2, payload2, err2)
            state["last_responses_probe_ts"] = now
            log(f"probe responses -> {resp_kind} http={st2}")
            if resp_kind != "ok":
                # Prefer responses classification when models looked fine
                if kind == "ok":
                    kind = resp_kind

    needs_restart = False
    if kind == "ok":
        state["consecutive_fails"] = 0
        state["last_ok_ts"] = now
        state["last_error"] = ""
        # Do NOT rewrite config on healthy path — Cockpit regenerates sidecar
        # and fighting it can recreate auth_unavailable after a while.
        save_state(state)
        return 0

    state["consecutive_fails"] = int(state.get("consecutive_fails") or 0) + 1
    state["last_error"] = kind

    # Avoid restart storms (each Cockpit boot bulk-refreshes Plus quotas → wham/usage).
    if kind == "proxy_down":
        needs_restart = state["consecutive_fails"] >= 2
    elif kind in {"auth_unavailable", "auth_rejected"}:
        needs_restart = state["consecutive_fails"] >= FAIL_THRESHOLD
    elif kind in {"upstream_503", "upstream_5xx"}:
        # Sustained upstream failures can leave cooling / sticky bad accounts
        needs_restart = state["consecutive_fails"] >= max(FAIL_THRESHOLD + 1, 3)
    else:
        needs_restart = state["consecutive_fails"] >= FAIL_THRESHOLD

    if needs_restart:
        actions = harden_sidecar_config()
        if actions:
            log("repair: " + ",".join(actions))
        if now - float(state.get("last_restart_ts") or 0) >= MIN_RESTART_INTERVAL_SEC:
            log(f"action: restart due to {kind} fails={state['consecutive_fails']}")
            ok = restart_cockpit()
            state["last_restart_ts"] = now
            if ok:
                # re-probe once
                time.sleep(2)
                st3, payload3, err3 = http_json("GET", f"{PROXY_BASE}/v1/models", token, timeout=10)
                k3 = classify(st3, payload3, err3)
                log(f"post-restart models -> {k3} http={st3}")
                if k3 == "ok":
                    state["consecutive_fails"] = 0
                    state["last_ok_ts"] = time.time()
        else:
            log(
                f"backoff: skip restart ({kind}); "
                f"next in {int(MIN_RESTART_INTERVAL_SEC - (now - float(state.get('last_restart_ts') or 0)))}s"
            )

    save_state(state)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
