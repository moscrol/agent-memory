#!/usr/bin/env python3
"""能力图谱防漂移审计（finance-agent-capability-graph 的 exit-code 门）。

问题：能力图谱是手工维护的 mermaid + 节点清单，「维护口径」只是散文约定，
没有任何机械校验——节点路径改名/删除后图谱不会报警，久了就变成过期地图。

本脚本把「节点清单表」当作机器可读的事实源，逐行校验：

1. 解析 `10_knowledge/finance-agent-capability-graph.md` 的节点清单 markdown 表；
2. 把「所在仓库」映射到本地 repo 目录（默认在 vault 的同级目录找）；
3. repo 在本地存在时，按「主要路径」单元格里的每条 spec 校验；
4. repo 不在本地 → SKIP（不算失败），断言不成立 → STALE。

「主要路径」单元格的反引号 spec 支持三种粒度（后两种是 2026-08-05 新增）::

    `intelligence/services/cli.py`                     # 只校验路径存在
    `.../research_tool_registry.py::memory_lookup`     # 再校验符号在该文件里
    `.../episode_tools.py::memory_lookup@some/branch`  # 在指定分支上校验（在途能力）

为什么需要后两种：2026-08-05 发现图谱写着 `episode_tools.py` 提供 `memory_lookup`，
而该符号只存在于一条未合并分支；`episode_tools.py` 本身在 main 上是存在的，
所以**只校验路径的旧门禁 exit 0**——门禁的断言粒度比它声称保护的东西粗一档。
`@branch` 行判为 PENDING（不失败）；一旦该符号在默认工作树里也出现，
会打 MERGED 提示把行提升为常规行，避免在途行长期烂在图里。

同样在 2026-08-05 补上的还有 **revision 自述**：旧版输出从不说自己审的是哪个
checkout 的哪个分支，读者只能默认「审的是 main」。现在每个 repo 都会打印
分支/短 sha/是否脏，exit 0 才有确定的含义。

用法::

    python3 scripts/graph_audit.py                       # repos 根默认 = vault 上一级
    python3 scripts/graph_audit.py --repos-root ~/repos

退出码 0 = 无漂移，1 = 有 STALE 节点（图谱需要更新），2 = 用法/解析错误。
只读脚本（只跑 git show / rev-parse / status，不写盘）。
建议：每次改图谱、以及金融/知识库仓的结构性 PR 合并后跑一遍。
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]
GRAPH_NOTE = VAULT / "10_knowledge" / "finance-agent-capability-graph.md"

REPO_ALIASES = {
    "finance": "finance-workspace-private",
    "knowledge": "knowledge-base-private",
    "agent-memory": "agent-memory",
    "finhot": "finhot",
}
PATH_RE = re.compile(r"`([^`]+)`")


class Spec:
    """「主要路径」单元格里的一条断言：路径 [+ 符号] [+ 分支]。"""

    def __init__(self, raw: str) -> None:
        self.raw = raw
        rest, self.branch = (raw.rsplit("@", 1) + [None])[:2] if "@" in raw else (raw, None)
        if "::" in rest:
            self.path, self.symbol = rest.split("::", 1)
        else:
            self.path, self.symbol = rest, None


def parse_node_table(text: str) -> list[tuple[str, str, list[Spec]]]:
    """从「## 节点清单」章节解析 (节点, 仓库, [Spec])。"""
    m = re.search(r"## 节点清单\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
    if not m:
        return []
    rows: list[tuple[str, str, list[Spec]]] = []
    for line in m.group(1).splitlines():
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= {"-", " "}:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("节点", ""):
            continue
        node, repo, path_cell = cells[0], cells[1], cells[2]
        rows.append((node, repo, [Spec(p) for p in PATH_RE.findall(path_cell)]))
    return rows


def git(repo_dir: Path, *args: str) -> str | None:
    """跑一条只读 git 命令；失败返回 None（repo 无 git、分支不存在等都算失败）。"""
    try:
        r = subprocess.run(
            ["git", "-C", str(repo_dir), *args],
            capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def describe_revision(repo_dir: Path) -> str:
    """审计输出必须自述审的是哪个 revision，否则 exit 0 无法解读。"""
    branch = (git(repo_dir, "rev-parse", "--abbrev-ref", "HEAD") or "").strip()
    sha = (git(repo_dir, "rev-parse", "--short", "HEAD") or "").strip()
    if not sha:
        return "非 git 工作树"
    porcelain = git(repo_dir, "status", "--porcelain")
    dirty = "dirty" if (porcelain or "").strip() else "clean"
    return f"{branch}@{sha} {dirty}"


def defines_symbol(source: str, symbol: str, is_python: bool) -> bool:
    """符号是否真的出现在代码里。

    Python 走 AST，命中定义名、引用名、关键字参数名，以及**整串相等的字符串字面量**
    ——工具名这类东西是以 ``name="memory_lookup"`` 注册的，不是 def 出来的。
    这样既能查到注册式符号，又不会被注释/长文档字符串里的顺嘴一提糊弄过去。
    """
    if not is_python:
        return symbol in source
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return symbol in source
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == symbol:
            return True
        if isinstance(n, ast.Name) and n.id == symbol:
            return True
        if isinstance(n, ast.Attribute) and n.attr == symbol:
            return True
        if isinstance(n, ast.arg) and n.arg == symbol:
            return True
        if isinstance(n, ast.keyword) and n.arg == symbol:
            return True
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value == symbol:
            return True
    return False


def read_worktree(repo_dir: Path, path: str) -> str | None:
    f = repo_dir / path
    if not f.is_file():
        return None
    return f.read_text(encoding="utf-8", errors="replace")


def check_spec(repo_dir: Path, repo_name: str, node: str, spec: Spec,
               stale: list[str], notes: list[str]) -> None:
    """校验一条 spec，把结果 append 进 stale（失败）或 notes（信息）。"""
    label = f"{node} → {repo_name}/{spec.raw}"
    is_py = spec.path.endswith(".py")

    if spec.branch:
        # 在途能力：以声明的分支为准。分支不在本地 → 无法证伪，不失败但留痕。
        blob = git(repo_dir, "show", f"{spec.branch}:{spec.path}")
        if blob is None:
            notes.append(f"UNVERIFIED {label}（分支或文件不在本地，未校验）")
            return
        if spec.symbol and not defines_symbol(blob, spec.symbol, is_py):
            stale.append(f"{label}：分支 {spec.branch} 上找不到符号 {spec.symbol}")
            return
        # 已经合并进当前工作树的话，提醒把在途行提升为常规行，防止 @branch 行烂在图里。
        cur = read_worktree(repo_dir, spec.path)
        if cur is not None and (not spec.symbol or defines_symbol(cur, spec.symbol, is_py)):
            notes.append(f"MERGED {label}：当前工作树已具备，可去掉 @{spec.branch} 提升为常规行")
        else:
            notes.append(f"PENDING {label}：仅存在于分支 {spec.branch}，未进当前工作树")
        return

    src = read_worktree(repo_dir, spec.path)
    if src is None:
        if not (repo_dir / spec.path).exists():  # 目录型节点（如 skills/xxx/）
            stale.append(f"{label}：路径不存在")
        elif spec.symbol:
            stale.append(f"{label}：符号断言不能用在目录上")
        return
    if spec.symbol and not defines_symbol(src, spec.symbol, is_py):
        stale.append(f"{label}：文件在，但找不到符号 {spec.symbol}")


def main() -> int:
    parser = argparse.ArgumentParser(description="能力图谱防漂移审计")
    parser.add_argument("--repos-root", default=str(VAULT.parent), help="各 repo 的父目录")
    args = parser.parse_args()

    if not GRAPH_NOTE.is_file():
        print(f"用法错误：图谱笔记不存在 {GRAPH_NOTE}", file=sys.stderr)
        return 2
    rows = parse_node_table(GRAPH_NOTE.read_text(encoding="utf-8", errors="replace"))
    if not rows:
        print("用法错误：未解析到「## 节点清单」表", file=sys.stderr)
        return 2

    repos_root = Path(args.repos_root).expanduser()
    stale: list[str] = []
    notes: list[str] = []
    revisions: dict[str, str] = {}
    skipped = checked = 0

    for node, repo_alias, specs in rows:
        repo_name = REPO_ALIASES.get(repo_alias, repo_alias)
        repo_dir = VAULT if repo_name == "agent-memory" else repos_root / repo_name
        if not repo_dir.is_dir():
            skipped += 1
            continue
        if repo_name not in revisions:
            revisions[repo_name] = describe_revision(repo_dir)
        for spec in specs:
            checked += 1
            check_spec(repo_dir, repo_name, node, spec, stale, notes)

    print("审计对象（exit 0 只对这些 revision 成立）：")
    for repo_name, rev in sorted(revisions.items()):
        print(f"  {repo_name}: {rev}")
    print()

    for n in notes:
        print(n)
    for s in stale:
        print(f"STALE {s}")
    if stale:
        print(f"\nFAIL: {len(stale)} 条断言漂移（图谱需要更新或节点已迁移），已检 {checked} 条。")
        return 1
    print(f"\nOK: 节点清单 {len(rows)} 行、断言 {checked} 条无漂移"
          f"（{skipped} 行因 repo 不在本地跳过，{len(notes)} 条在途/未校验见上）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
