#!/usr/bin/env python3
"""agent-memory vault 质检门（把 maintenance.md 的「定期维护任务」硬化成 exit-code 门）。

检查项（对应 30_conventions/maintenance.md 写入检查清单）：

1. frontmatter 完整性：title / type / agent / source / date / tags 必填；
2. type 合法且 ↔ 目录一致（frontmatter-spec 的 type 取值表）；
   **不在取值表里的 type 直接 ERROR**——2026-08-05 前是 `TYPE_DIRS.get()` 返回 None
   然后静默放行，`type: reading-queue` 就这么混了进来。认不出来的值必须 fail closed，
   否则「写错 type」和「type 正确」在门禁眼里长得一样；
2b. agent 取值合法（frontmatter-spec 的固定值表，2026-08-12 起）——
   此前只查「有没有」不查「是什么」，`all` / `any` 就这么用了一个半月才被
   收编进规范。与 type 同一条纪律：认不出来的值 fail closed；
3. date 格式 YYYY-MM-DD；
4. 双链死链：`[[笔记名]]` 必须能解析到 vault 内某个 .md 文件名；
5. inbox 老化：`00_inbox/` 中超过 14 天未提炼的条目（仅 WARN，不拦截）；
6. 知识过期：`10_knowledge/` 中 `status: verified` 的笔记，若 `last_verified`
   （缺省回退到 `date`）超过 `stale_after` 天（缺省 90）未复核，降为 WARN，
   提醒复核后刷新 `last_verified` 或把 status 改回 draft。
7. 项目笔记体积：`20_projects/` 单文件超过 80KiB 降为 WARN（交接记录应一行，
   正文在 repo 的 docs/handoffs/；存量按棘轮可不动，但不要继续往里堆）。
8. TOOLKIT.md 镜像钉扎：文件头 `pinned_sha256` 必须等于「去掉 pinned_* 行后」
   的 sha256；sibling `harness-reference` 在本地时再对表 canonical。

用法::

    python3 scripts/vault_lint.py            # 校验整个 vault
    python3 scripts/vault_lint.py --strict   # WARN 也算失败

退出码 0 = 通过，1 = 有 ERROR（--strict 时含 WARN），2 = 用法错误。
只读脚本。建议：改动 vault 后、以及每次回写沉淀前跑一遍。
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]

REQUIRED_FIELDS = ("title", "type", "agent", "source", "date", "tags")
TYPE_DIRS = {
    "inbox": "00_inbox",
    "knowledge": "10_knowledge",
    "project": "20_projects",
    "convention": "30_conventions",
    "playbook": "40_playbooks",
    "agent-card": "50_agents",
    "dialogue": "60_dialogues",
    "tutor-note": "70_tutor",
}
# agent 固定取值（frontmatter-spec）。all/any 用于面向所有/任意 agent 的约定与 playbook。
AGENT_VALUES = {"devin", "codex", "cursor", "grok", "claude", "human", "all", "any"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)
INBOX_MAX_AGE_DAYS = 14
KNOWLEDGE_STALE_DAYS = 90
PROJECT_NOTE_WARN_BYTES = 80 * 1024
PINNED_SHA_RE = re.compile(r"^> pinned_sha256: ([0-9a-f]{64})\s*$", re.M)
PINNED_LINE_RE = re.compile(r"^> pinned_")
# 完全跳过校验的路径——这些不是 vault 笔记，逐条说明为什么：
#   .agents/_templates/_template.md  模板与 Agent 配置，本就没有 frontmatter
#   README.md                        导览页
#   TOOLKIT.md                       **来源镜像**：canonical 在 harness-reference 仓，
#                                    文件头一行就写着「改内容请改 harness-reference 后同步」。
#                                    给它补 frontmatter / 改死链都算本地改内容、会与
#                                    canonical 漂移，所以整体跳过（2026-08-12，
#                                    它曾把本门禁刷红：缺 frontmatter + 指向外仓的死链）
#   可证伪点回检/ .foresight/         **运行时台账**：机器逐 run 写出来的产物，
#                                    永远不会有 frontmatter（.foresight 由
#                                    FORESIGHT_USERS_DIR 指到 vault 内，见项目 MOC 2026-07-07）
# 注意名字：它跳过的是**全部检查**（含死链），不只是 frontmatter。
# 2026-08-05 前 .foresight 不在此列，35 条运行时产物长期把这道门禁刷成红色——
# 一个因无关原因常红的门禁等于没有门禁，真问题会混在噪声里没人看。
SKIP_PATHS = {
    ".agents",
    "_templates",
    "可证伪点回检",
    ".foresight",
    "_template.md",
    "README.md",
    "TOOLKIT.md",
}


def parse_frontmatter(text: str) -> dict[str, str] | None:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip()
    return fm


def should_skip(path: Path) -> bool:
    rel = path.relative_to(VAULT)
    return rel.parts[0] in SKIP_PATHS or rel.name in SKIP_PATHS


def toolkit_body(text: str) -> str:
    """只哈希正文：开头那段「出处声明」不算内容。

    排除两类行，理由相同——它们描述的是"这份文件是谁的镜像"，不是被镜像的内容：

    1. `> pinned_*`：更新 pin 本身不该改变被钉的内容（原有行为）。
    2. **第一个 Markdown 标题之前的所有 `> ` 引用行**：镜像侧比 canonical 多出
       「来源镜像：canonical 在 harness-reference/TOOLKIT.md」这段头。canonical
       自己不带它（它开头就是 `# 审查工具包`），于是按旧定义两边的 body 永远
       不可能相等——sibling 对表是**结构性常红**，只是云端 CI 没 clone
       harness-reference 才看不见，本地跑一次就红一次。

    标题之后的 `> ` 引用行（canonical 的「本文只回答用哪一档审查工具」那段）
    是正文，照常参与哈希。
    """
    out: list[str] = []
    seen_heading = False
    for ln in text.splitlines(True):
        if not seen_heading:
            if ln.startswith("#"):
                seen_heading = True
            elif ln.startswith(">") or not ln.strip():
                continue  # 出处声明与其后空行
        if PINNED_LINE_RE.match(ln):
            continue
        out.append(ln)
    return "".join(out)


def check_toolkit_mirror(errors: list[str], warns: list[str]) -> None:
    path = VAULT / "50_agents" / "TOOLKIT.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    m = PINNED_SHA_RE.search(text)
    if not m:
        warns.append("50_agents/TOOLKIT.md: 缺 pinned_sha256，镜像无法检测漂移")
        return
    actual = hashlib.sha256(toolkit_body(text).encode()).hexdigest()
    if actual != m.group(1):
        errors.append(
            f"50_agents/TOOLKIT.md: pinned_sha256 与正文不符（pin={m.group(1)[:12]}… "
            f"actual={actual[:12]}…）。改镜像必须同步改 pin；"
            "内容应先改 harness-reference 再拷回来"
        )
        return
    sibling = VAULT.parent / "harness-reference" / "TOOLKIT.md"
    if sibling.is_file():
        src = hashlib.sha256(toolkit_body(sibling.read_text(encoding="utf-8", errors="replace")).encode()).hexdigest()
        if src != actual:
            errors.append(
                "50_agents/TOOLKIT.md: 与 ../harness-reference/TOOLKIT.md 正文不一致（镜像已漂）"
            )
    # sibling 不在（云端 CI / 未 clone）就只做 pin 自检，不 WARN——
    # 每次 CI 一条修不了的黄灯 = 常红门禁。


def main() -> int:
    parser = argparse.ArgumentParser(description="agent-memory vault 质检门")
    parser.add_argument("--strict", action="store_true", help="WARN 也算失败")
    args = parser.parse_args()

    md_files = [p for p in VAULT.rglob("*.md") if ".git" not in p.parts]
    basenames = {p.stem for p in md_files}
    directory_names = {p.name for p in VAULT.iterdir() if p.is_dir()}
    errors: list[str] = []
    warns: list[str] = []
    today = dt.date.today()

    for path in md_files:
        rel = path.relative_to(VAULT)
        if should_skip(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")

        # 双链死链（跳过代码块/行内代码里的示例链）
        prose = CODE_RE.sub("", text)
        for link in WIKILINK_RE.findall(prose):
            target = link.strip().rstrip("\\").split("/")[-1]
            if target.endswith(".md"):
                target = target[:-3]
            if target and target not in basenames and target not in directory_names:
                errors.append(f"{rel}: 死链 [[{link.strip()}]]")

        fm = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{rel}: 缺少 frontmatter")
            continue

        for field in REQUIRED_FIELDS:
            if not fm.get(field):
                errors.append(f"{rel}: frontmatter 缺字段 {field}")

        date_val = fm.get("date", "")
        if date_val and not DATE_RE.match(date_val.strip('"')):
            errors.append(f"{rel}: date 格式应为 YYYY-MM-DD，实际 {date_val}")

        last_verified = fm.get("last_verified", "").strip('"')
        if last_verified and not DATE_RE.match(last_verified):
            errors.append(f"{rel}: last_verified 格式应为 YYYY-MM-DD，实际 {last_verified}")
        stale_after = fm.get("stale_after", "").strip('"')
        if stale_after and not stale_after.isdigit():
            errors.append(f"{rel}: stale_after 应为天数整数，实际 {stale_after}")

        agent_val = fm.get("agent", "")
        if agent_val and agent_val not in AGENT_VALUES:
            errors.append(
                f"{rel}: agent={agent_val} 不在固定取值表里"
                f"（{'/'.join(sorted(AGENT_VALUES))}），见 30_conventions/frontmatter-spec.md"
            )

        note_type = fm.get("type", "")
        if note_type and note_type not in TYPE_DIRS:
            # 认不出来的 type 必须失败，不能因为查表落空就当没事——见模块 docstring 第 2 条。
            errors.append(
                f"{rel}: type={note_type} 不在合法取值表里"
                f"（{'/'.join(TYPE_DIRS)}），见 30_conventions/frontmatter-spec.md"
            )
        expected_dir = TYPE_DIRS.get(note_type)
        if expected_dir and rel.parts[0] != expected_dir:
            errors.append(f"{rel}: type={note_type} 应放在 {expected_dir}/")

        # 知识过期：verified 笔记超过 stale_after 天未复核
        if rel.parts[0] == "10_knowledge" and fm.get("status") == "verified":
            anchor = last_verified if DATE_RE.match(last_verified) else date_val.strip('"')
            max_age = int(stale_after) if stale_after.isdigit() else KNOWLEDGE_STALE_DAYS
            if DATE_RE.match(anchor):
                age = (today - dt.date.fromisoformat(anchor)).days
                if age > max_age:
                    warns.append(
                        f"{rel}: verified 笔记已 {age} 天未复核（>{max_age} 天），"
                        "复核后刷新 last_verified 或降回 draft"
                    )

        # inbox 老化
        if rel.parts[0] == "00_inbox" and DATE_RE.match(date_val.strip('"')):
            age = (today - dt.date.fromisoformat(date_val.strip('"'))).days
            if age > INBOX_MAX_AGE_DAYS:
                warns.append(f"{rel}: inbox 条目已 {age} 天未提炼（>{INBOX_MAX_AGE_DAYS} 天）")

        if rel.parts[0] == "20_projects":
            size = len(text.encode("utf-8"))
            if size > PROJECT_NOTE_WARN_BYTES:
                warns.append(
                    f"{rel}: 项目笔记 {size} 字节（>{PROJECT_NOTE_WARN_BYTES}），"
                    "新交接严格一行，正文放 repo 的 docs/handoffs/；存量按棘轮可不动"
                )

    check_toolkit_mirror(errors, warns)

    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    failed = bool(errors) or (args.strict and bool(warns))
    if failed:
        print(f"\nFAIL: {len(errors)} error(s), {len(warns)} warn(s)")
        return 1
    print(f"OK: {len(md_files)} 个文件通过（{len(warns)} warn）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
