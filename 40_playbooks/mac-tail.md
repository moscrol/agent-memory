---
title: Mac 一次性收尾（孤本备份 + hook 路径）
type: playbook
agent: human
source: 2026-08-12 收尾；云端 agent 无法操作 launchd，把安装收成 Mac 上的一条命令
date: 2026-08-12
tags: [playbook, mac, backup, launchd, core]
related: ["[[../30_conventions/sync-setup]]", "[[../20_projects/agent-memory]]"]
status: verified
---

# Mac 一次性收尾

auto-sync 把本仓拉到 main 之后，在 **a77 Mac** 上跑：

```sh
bash /Users/a77/agent-memory/scripts/hosts/install-mac-tail.sh
```

它会：把 `untracked-backup.sh` 拷到 `~/bin`、装 `com.a77.agent-memory-backup`（每天 04:10）、立刻备份一次 `60_dialogues/` 和 `.foresight/`、检查用户级 SessionStart hook 是否指向 vault 内的 `scripts/hooks/session-context.sh`（拷贝会让断言纪律漂移）。

成功标志：脚本打印各目录 `ok: … tar.gz`；`launchctl list | grep agent-memory` 能看到 `backup` 和已有的 `sync`。

备份默认写到 `~/Backups/agent-memory-untracked`（与 vault **同盘**）。要抗单盘损坏，把 `AGENT_MEMORY_BACKUP_DIR` 指到 iCloud / 外置盘后重跑本脚本。

不要在云端跑——不是 Darwin 会直接 exit 1。
