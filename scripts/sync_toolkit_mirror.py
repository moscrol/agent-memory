#!/usr/bin/env python3
"""把 harness-reference 的 TOOLKIT.md 同步进 vault 镜像 50_agents/TOOLKIT.md 并重钉 pin。

解决的失败形状：镜像靠人手拷贝 + 手算 sha256，harness-reference 每合一批固化就漂一次；
2026-08-14 钉 pin 之后 08-19 就漂了，之后两周 `vault_lint.py` 一直红着「pinned_sha256 与正文不符」，
红灯常亮等于没有灯。lint 的报错文案本身就是操作步骤（「先改 harness-reference 再拷回来」），
这里只是把它做成一条命令。

正文来源默认是 SSOT `gitea/main`（`git show`），不读 harness-reference 的工作树——
那棵树常停在别人的特性分支上，文件都在、内容是旧的。哈希口径复用 vault_lint.toolkit_body，
不另写第二份归一化。

用法：
  python3 scripts/sync_toolkit_mirror.py              # 从 ../harness-reference 的 gitea/main 取
  python3 scripts/sync_toolkit_mirror.py --ref main   # 换 ref
  python3 scripts/sync_toolkit_mirror.py --source-file /path/TOOLKIT.md   # 直接给文件
退出码：0 已写入或已一致；1 取不到来源。写完请跑 vault_lint.py 复核。
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vault_lint import PINNED_SHA_RE, toolkit_body  # noqa: E402

VAULT = Path(__file__).resolve().parent.parent
MIRROR = VAULT / "50_agents" / "TOOLKIT.md"
DEFAULT_REPO = VAULT.parent / "harness-reference"

HEADER_TEMPLATE = (
    "> **来源镜像**：canonical 在 `harness-reference/TOOLKIT.md`（`linxiaoqi5111-del/harness-reference` main）。\n"
    "> 本文件供云端 Agent / agent-memory 拉取使用；改内容请改 harness-reference 后同步"
    "（`python3 scripts/sync_toolkit_mirror.py`）。\n"
    "> pinned_sha256: {sha}\n"
    "> pinned_at: {date}\n"
    "\n"
)


def load_canonical(repo: Path, ref: str, source_file: Path | None) -> str:
    if source_file is not None:
        return source_file.read_text(encoding="utf-8")
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"{ref}:TOOLKIT.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        sys.stderr.write(f"取不到 {repo} 的 {ref}:TOOLKIT.md：{proc.stderr.strip()}\n")
        sys.exit(1)
    return proc.stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="harness-reference 仓根")
    ap.add_argument("--ref", default="gitea/main", help="取正文的 git ref（默认 SSOT gitea/main）")
    ap.add_argument("--source-file", type=Path, default=None, help="绕过 git，直接给 TOOLKIT.md 路径")
    args = ap.parse_args()

    canonical = load_canonical(args.repo, args.ref, args.source_file)
    new_sha = hashlib.sha256(toolkit_body(canonical).encode()).hexdigest()

    old_text = MIRROR.read_text(encoding="utf-8") if MIRROR.is_file() else ""
    old_pin = PINNED_SHA_RE.search(old_text)
    old_sha = old_pin.group(1) if old_pin else None
    old_body_sha = hashlib.sha256(toolkit_body(old_text).encode()).hexdigest() if old_text else None

    if old_sha == new_sha and old_body_sha == new_sha:
        print(f"镜像已与来源一致（pin {new_sha[:12]}…），未改动")
        return 0

    header = HEADER_TEMPLATE.format(sha=new_sha, date=dt.date.today().isoformat())
    MIRROR.write_text(header + canonical, encoding="utf-8")
    source = str(args.source_file) if args.source_file else f"{args.repo.name} {args.ref}"
    print(
        f"已刷新 {MIRROR.relative_to(VAULT)} ← {source}\n"
        f"  pin  {(old_sha or '(无)')[:12]}… → {new_sha[:12]}…\n"
        f"  正文 {(old_body_sha or '(无)')[:12]}… → {new_sha[:12]}…"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
