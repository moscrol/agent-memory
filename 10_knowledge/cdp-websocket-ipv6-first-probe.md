---
title: Chrome DevTools (CDP) WebSocket 探测：IPv6 优先
type: knowledge
agent: devin
source: finance-workspace-private 7.31 复盘 CDP proxy 排障（2026-08-02 实测）
date: 2026-08-02
tags: [knowledge, cdp, chrome, websocket, ipv6, debugging, infrastructure, core]
status: verified
related: ["[[../20_projects/finance-workspace-private]]"]
---

# Chrome DevTools (CDP) WebSocket 探测：IPv6 优先

Chrome 的 remote debugging TCP 端口在 IPv4 和 IPv6 上都能探测到，
但 WebSocket 端点可能只在 IPv6 `::1` 上可达。探测顺序写反会导致
"TCP 通、WebSocket 必失败" 的幽灵故障。

## 结论 / 要点

### 1. TCP 探测 ≠ WebSocket 可达

Chrome 151 on macOS（实测 Chrome/151.0.7922.71）：
- `net.createConnection(9222, '127.0.0.1')` → 连接成功 ✓
- `net.createConnection(9222, '::1')` → 连接成功 ✓
- `new WebSocket('ws://127.0.0.1:9222/devtools/browser/...')` → **失败** ✗
- `new WebSocket('ws://[::1]:9222/devtools/browser/...')` → 成功 ✓
- `new WebSocket('ws://localhost:9222/devtools/browser/...')` → 成功 ✓

两层 TCP 都通，但 WebSocket 只走 IPv6。如果探测逻辑先选 `127.0.0.1`
（因为 IPv4 探测先成功），后续所有 WebSocket 操作必然失败。

### 2. 排查特征

- CDP proxy 的 `/targets`（HTTP 列表端点）正常返回 → 说明 TCP 通
- `/eval`（WebSocket eval 端点）持续返回 `{"error":"连接失败"}` → WS 断
- proxy 日志反复输出 `连接错误: 连接失败（端口缓存已清除）`
- 重启 proxy 不解决，因为重启后探测逻辑不变、仍选 IPv4

### 3. 修复

探测顺序改为 IPv6 优先：`['::1', '127.0.0.1']`。

这在 macOS 上是安全的——`::1` 在所有现代 macOS 上默认可用，
且如果 Chrome 只在 IPv4 监听，回退到 `127.0.0.1` 仍然有效。

### 4. launchd 管理的 proxy 需先 unload

如果 CDP proxy 被 launchd 管理（如 `com.financeworkspace.cdp-proxy`），
kill 进程后 launchd 会自动重启新实例，但新实例继承了同样的探测 bug。
排查时先 `launchctl unload` 再手动启动，避免干扰。

## 背景 / 依据

- 实测环境：macOS Darwin 25.4.0, Chrome 151.0.7922.71
- 故障表现：finance-workspace-private `daily-full` 的 `sync-limit-heat` 步骤 100% 失败
- 验证方法：用 Node.js 原生 WebSocket 分别测 `127.0.0.1` / `[::1]` / `localhost` 三个 host
- 修复后 17 步 daily-full 全部 OK，sync-limit-heat 写入 248 题材 / 1247 涨停明细

## 适用场景

- 任何通过 CDP proxy 操控 Chrome 的工具（fupanhui API、Puppeteer、Playwright）
- 本地开发环境中 Chrome remote debugging 的 WebSocket 连接排障
- macOS 上 IPv4/IPv6 双栈服务的探测顺序设计原则

## 参考

- 修复文件：`~/.claude/skills/web-access/scripts/cdp-proxy.mjs` `checkPort()` 函数
- 项目交接：[[../20_projects/finance-workspace-private]] 2026-08-02 条目
