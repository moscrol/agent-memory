# 本机 launchd 脚本快照（`~/bin`）

`~/bin` 下这批脚本驱动本机的定时任务，2026-08-09 之前**不在任何版本控制下、
也没有任何备份副本**（逐个搜过全机）。其中 `agent-memory-sync.sh` 的注释里带着
10777 次冲突、325 个提交、647 个文件这类只能靠事故现场取得的实测读数——
那种内容一旦丢失就无法重建，而它当时是全机单副本。

本目录是它们的**快照**，用途是保住内容与注释，不是执行位置。

## 边界（重要）

- **运行位置仍是 `~/bin`**，launchd 的 `ProgramArguments` 指向那里，未改。
- 本目录是 `cp` 出来的副本，**不是软链**：改了 `~/bin` 的脚本，这里不会自动跟上。
  改完请手动同步（见下），否则这里会静默变成旧版本——那比没有副本更糟，
  因为它看起来是可信的。
- 未纳管 `cockpit-codex-auth-watchdog.py.bak-devin`：它与正本仅在
  `session-affinity` 的真假上完全相反（正本 disable，它 enable），是一份
  **逻辑被反转过的旧备份**而非有效副本。留在 `~/bin` 供追溯，不进共享历史。

## 纳管前已做的检查

字面量密钥扫描（赋值右侧为常量字符串）与 20+ 位高熵串扫描均为空。
`cockpit-*.py` 里出现的 `experimental_bearer_token`、`api-keys` 是**读取配置的
变量名与正则模式**，不是硬编码凭证——两个 watchdog 都从 Cockpit 的配置文件里取值。

## 快照同步

```bash
cd /Users/a77/agent-memory-answer-spec   # 或任何持有 main 的 worktree
for f in scripts/hosts/*.sh scripts/hosts/*.py; do
  cp "/Users/a77/bin/$(basename "$f")" "$f"
done
git diff --stat -- scripts/hosts   # 有 diff 就说明 ~/bin 改过而这里没跟上
```

## 清单

| 脚本 | 作用 |
|---|---|
| `agent-memory-sync.sh` | 本 vault 的定时同步（launchd `com.a77.agent-memory-sync`，180s） |
| `cdp-chrome.sh` | 启动带 CDP 调试端口的 Chrome（web-access / 抓数前置） |
| `cockpit-codex-auth-watchdog.py` | Cockpit codex 上游鉴权看护，含账号池与 routing 修正 |
| `cockpit-codex-auth-watchdog.sh` | 上面那个 py 的 launchd 包装 |
| `cockpit-disable-empty-plus-refresh.py` | 关掉额度耗尽的 Plus 账号的刷新组 |
| `finhot-exec-watchdog.sh` | finhot 执行看护 |
| `untracked-backup.sh` | vault 内仍不入 git 的孤本（`.foresight/`；`60_dialogues/` 已于 2026-10-08 进 git，脚本仍会顺带打一份 tar）每日 tar 快照 |
| `com.a77.agent-memory-backup.plist` | 上面那个脚本的 launchd 定义（每天 04:10） |
| `install-mac-tail.sh` | **Mac 一次性安装器**：拷脚本 + 装 plist + 立刻跑一次 + 检查 hook 路径。auto-sync 拉到 main 后在 Mac 上跑这一条即可 |
