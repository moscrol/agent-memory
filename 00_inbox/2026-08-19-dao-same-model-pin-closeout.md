---
title: "[收尾] Dao 同模型钉死已执行 · ay/terra 保留"
type: inbox
agent: grok
source: Cursor Grok 会话 2026-08-19 01:54（已改配置并对照活读数）；取代 2026-08-18-dao-ay-terra-403-root-fix-handoff.md 的 L1 退役方案
date: 2026-08-19
tags: [inbox, handoff, dao, provider, closeout]
status: draft
---

# [收尾] Dao 同模型钉死已执行 · ay/terra 保留

> 交接自：Cursor Grok · 2026-08-19 01:54 · **已改配置并对照活读数**
> 取代：`2026-08-18-dao-ay-terra-403-root-fix-handoff.md` 里的 L1「退役 ay/terra」。那份诊断仍有效，方案已改口。

## 用户拍板（勿再改回退役）
- ay/terra **继续可用**，不要 `providers.*.enabled=false`
- 同模型换渠：点 Terra 可 ay↔terra（及同跑 `gpt-5.6-terra` 的渠），不落到 GLM/Sol
- 内置 `swe-*` 拿掉 ay/terra；额度只出现在显式 `dao-gpt-5-6-terra/luna/sol`
- 本轮：Dao 槽位 + Codex 入口收到本机反代。Cockpit / 公网隧道 / `grok-session-proxy` 不动

## 已做
配置（改前备份后缀 `bak-same-model-pin-20260819-014058`）：
- `~/Library/Application Support/dao-flow-desktop/config/配置.json`
- `~/.codeium/dao-byok/配置.json`

钉死后（活配置 `GET http://127.0.0.1:8955/origin/ea/config` 已对照，与桌面文件 primary 一致）：
- `swe-1-6` / `swe-1.6` / `swe-1p6` → `glm/glm-5.2`
- `swe-1-6-fast` → `luna/gpt-5.6-luna`
- `swe-1-6-slow` → 桌面 `dp/deepseek-v4-flash`；codeium 文件 `glm/glm-5.3`
- `swe-1-7-lightning` → `kfcsol`↔`soll`（同模型 sol，无 ay）
- `dao-gpt-5-6-terra/luna/sol` 仍 ay 主渠 + 同模型备渠
- 新增 `gpt-5.6-sol` 别名（完整副本，供 Codex 模型名）
- `providers.ay.enabled=true`、`terra.enabled=true`

Codex：
- `~/.codex/config.toml` `openai_base_url=http://127.0.0.1:8955/v1`（以活 `endpoint.json` 为准；重启后 Dao 从 50936 改听 **8955**）
- `~/.codex/auth.json` 的 `OPENAI_API_KEY` 已换成桌面反代 key（与 `GET /origin/revproxy/status` 同 sha8；旧 key 在同后缀 bak）
- **已开着的 Codex 会话必须重开** 才走新入口

Dao Flow 已重启：pid **7785** 听 `127.0.0.1:8955`。`grok-session-proxy.py` pid **14780** `:18765` 未动。

## 质检（2026-08-19 01:52–01:54）
| 项 | 结果 |
|---|---|
| 两份文件 swe-* 无 ay/terra/grokk，无 fallback 泄漏 | 过 |
| 两份文件 dao-gpt-* 同模型且仍含 ay/terra | 过 |
| 无其它槽位挂 ay/terra | 过 |
| 活配置 69 槽 = 文件；swe primary 与桌面文件一致 | 过 |
| Codex base_url = 活 `revproxy.base`；auth key = 活反代 key | 过 |
| 备份四件在 | 过 |
| `route-decision-inbox` lastSeen 均早于 01:40 钉死 | 过 |
| lsof 90s / 197 次：Dao/Codex **零命中** `198.18.0.24`/`62` | 过 |
| Cockpit `pid 82076` 仍打 `198.18.0.24:443`（本轮故意不动） | 残留 |
| 24h 无熔断弹窗 | 未到点，未验 |
| 原交接 10min 采样 | 本轮只做了 90s |

## 回滚
- 两份 `配置.json.bak-same-model-pin-20260819-014058` 拷回后等 Dao `fs.watch` 热重载，或重启 Dao Flow
- `~/.codex/config.toml.bak-same-model-pin-20260819-014058` + `auth.json.bak-same-model-pin-20260819-014058`

## 坑
- 活端口会变：以 `~/Library/Application Support/dao-flow-desktop/runtime/endpoint.json` 的 `revproxy.base` 为准，不要写死 50936
- 桌面与 `~/.codeium/dao-byok/配置.json` 是两份；Devin 起来后读 codeium 那份（slow 已是 glm-5.3，无 ay）
- Fake-IP：`198.18.x.x` 不是真实服务器 IP；打谁看 lsof
- `swe-route-guard.json` desired/degraded 仍空，lastProbe 停在 2026-08-08；模板空则不会写回路由
- 红线：不读/不输出 apiKey，只报字段名和长度
- 不要再执行旧交接的 L1 退役或关 ay/terra

## 未做
- L3 关 cloudflared / trycloudflare
- 24h 弹窗观察

## Cockpit 空烧已收（2026-08-19 09:51）
用户改口：Cockpit 也不许空烧。

已做：
- `launchctl bootout` 并停用 `com.cockpit.codex-auth-watchdog`（原每 5min 探 `/v1/models`、每 15min 打 `gpt-5.6-sol` ping，失败会 `open -a Cockpit Tools`）。plist 停在 `~/Library/LaunchAgents/com.cockpit.codex-auth-watchdog.plist.bak-idle-pin-20260819-0950`
- `~/.antigravity_cockpit/codex_local_access.json` `enabled=false`
- 侧车 `config.json` 去掉 55 条 `x.ailzd.com` 上游（留 1 条 fenno；备份 `*.bak-idle-pin-20260819-0950`）
- 退出 Cockpit Tools / cliproxy；`:57244` 已关

质检：60s / 134 次 lsof，ay/terra Fake-IP **0 命中**，Cockpit 未拉起。Dao `:8955`、`grok-session-proxy` `:18765` 未动。

再开 Cockpit 可能从账号池重生侧车。要空烧继续为零：别开 Cockpit，也别把 watchdog plist 移回去。Dao 的 `cockpit-codex`（`:8080`）本来就没在听，Terra 同模型链少这一备渠。
