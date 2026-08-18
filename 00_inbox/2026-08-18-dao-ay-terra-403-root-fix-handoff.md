# [交接] Dao 渠道 ay/terra 403 循环 · 根治方案待执行

> **2026-08-19 已取代执行方案**：用户改口保留 ay/terra，改为同模型钉死。收尾见 `2026-08-19-dao-same-model-pin-closeout.md`。本文诊断仍有效，**不要再执行下方 L1 退役 / 关 provider**。

> 交接自：MJ (Devin) · 2026-08-18 深夜 · 诊断已完成，方案已定，**尚未动任何配置**

## 任务目标
根治 Dao Flow 反复弹「渠道熔断: terra/ay HTTP 403 · balance · 拉黑 1800s」（每 30min 一条），并消除 ay/terra 充值后被后台任务持续消耗的风险。

## 根因（已实证，勿重复诊断）
1. **架构性脱节**：Dao 按内部"模型槽位"路由，不看用户 UI 选的模型。12 个槽位引用 ay/terra：`swe-1-6, swe-1-6-fast, swe-1-6-slow, swe-1-7-lightning, swe-1.6, swe-1.6-fast, swe-1.6-slow, swe-1p6, swe-1.7-lightning, dao-gpt-5-6-luna/terra/sol`。
2. ay=`x.ailzd.com`、terra=`kfcoding.codes`，两者余额不足 → 403 → 熔断拉黑 1800s → 到期半开试探又 403 → 循环。**当前 403 被拒不计费，充值后即真实消耗**。
3. 实测流量源（lsof 0.2s 高频采样 8min）：Devin 主进程 (pid 84056) 36 条短连接打两站；Devin summarizer 后台代理；Codex CLI 直连 ay；Cockpit Tools 侧车 (pid 82076, 独立 15+ key 直连 ay, 配额已 0%)。
4. **非 8/16 配置改动引入**：最老备份 vs 当前全量 diff 仅 13 处且全为 grok 接入相关；`route-decision-inbox.json` 的 exhausted 记录 8/10 已出现。

## 待执行的三层方案
配置文件：`~/Library/Application Support/dao-flow-desktop/config/配置.json`（改前先 cp 备份）

**L1 路由退役**（治本核心）：
- 上述 12 槽位的 `channelPriority` 中**删除** ay/terra 项，`provider`/`fallback` 若为 ay/terra 改为 `dp` 或 `glm`（dp=DeepSeek 官方, glm=智谱官方，均按量付费）
- 再设 `providers.ay.enabled=false`、`providers.terra.enabled=false`（双保险）

**L2 入口收敛**：`~/.codex/config.toml` 的 `openai_base_url` 由 `https://x.ailzd.com/v1` 改为 Dao 反代 `http://127.0.0.1:50936/v1`（端口以 `dao-flow-desktop/runtime/endpoint.json` 的 revproxy.base 为准；key 用 GET `http://127.0.0.1:50936/origin/revproxy/status` 返回的 apiKey，或读 `~/.codeium/dao-byok/revproxy.json`）

**L3 关公网隧道**：`kill 1618`（cloudflared，自 8/4 暴露 8955/revproxy 到 trycloudflare，URL 见 endpoint.json.tunnel）

## 验收标准
1. lsof 采样 ≥10min 无新连接打向 `198.18.0.24`/`198.18.0.62`
2. 24h 无新熔断弹窗
3. 改完**重启 Dao Flow**再验证（存在文件配置与运行时读数不一致迹象：文件里 swe-1-6-slow 无 glm，运行时却报 provider: glm——活配置入口是 `GET http://127.0.0.1:50936/origin/ea/config`，改完建议对照它确认生效）

## 坑（必读）
- 本机 DNS 为 Fake-IP 模式（198.18.x.x 是 Surge/Clash 虚拟 IP），nslookup 结果不可当真实服务器 IP；排查打谁用 lsof 看 TCP 对端
- Dao 运行时锁定 DIPS 库，只读需先 cp 快照
- 槽位内渠道路由是动态的（同会话 glm↔ay 漂移过），验收要看多轮读数而非单次
- `grok-session-proxy.py` (pid 14780) 是用户自己的 Grok TUI 链路，**勿动**
- 采样脚本模板在 `/tmp/probe-ay-terra.sh`（lsof 循环 grep Fake-IP），/tmp 重启即失，可按需重建
- 红线：不读取/不输出任何 apiKey 值，只报字段名和长度
