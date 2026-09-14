#!/usr/bin/env python3
"""agent-memory vault 质检门（把 maintenance.md 的「定期维护任务」硬化成 exit-code 门）。

检查项（对应 30_conventions/maintenance.md 写入检查清单）：

0. **空文件**：任何 `.md` 被写成空/纯空白即 ERROR。这一项**跑在 SKIP_PATHS 之前**，
   因为「文件是不是空的」与「它是不是一篇合规笔记」无关；只豁免运行时台账
   （`.foresight/`、`可证伪点回检/`）。2026-09-04 一次批量内容丢失把 4 个文件写成
   0~1 字节、auto-sync 两秒后连提交带推送，`70_tutor/README.md` 空了十天无人知——
   旧检查看不见它，是因为 should_skip 按 basename 匹配，"README.md" 跳过的是
   全库任意目录下的 README，而不只是本意的根层导览页；
1. frontmatter 完整性：title / type / agent / source / date / tags 必填；
1b. **缺 agent 的历史豁免**：`date` 早于 2026-09-14 的存量笔记缺 `agent` 降为 WARN。
   4 篇 09-09~13 的 finance QC 笔记写入者已不可考，而 provenance 字段填猜测值
   比缺着更坏——它唯一的用途就是聚合「谁写了什么」。只豁免「缺」不豁免「值不合法」，
   日期缺失或格式坏时不豁免（认不出日期就当它是新的）；
2. type 合法且 ↔ 目录一致（frontmatter-spec 的 type 取值表）；
   **不在取值表里的 type 直接 ERROR**——2026-08-05 前是 `TYPE_DIRS.get()` 返回 None
   然后静默放行，`type: reading-queue` 就这么混了进来。认不出来的值必须 fail closed，
   否则「写错 type」和「type 正确」在门禁眼里长得一样；
   `material`（05_materials，外部资料层）2026-09-13 入表——收集来的外部输入
   与提炼后的知识分开存放，前者回答「别人说了什么」，后者回答「我以后能再用什么」；
2b. agent 取值合法（frontmatter-spec 的固定值表，2026-08-12 起）——
   此前只查「有没有」不查「是什么」，`all` / `any` 就这么用了一个半月才被
   收编进规范。与 type 同一条纪律：认不出来的值 fail closed；
3. date 格式 YYYY-MM-DD；
4. 双链死链：`[[笔记名]]` 必须能解析到 vault 内某个 .md 文件名；
5. inbox 老化：`00_inbox/` 中超过 14 天未提炼的条目（仅 WARN，不拦截）；
6. 知识过期：`10_knowledge/` 中 `status: verified` 的笔记，若 `last_verified`
   （缺省回退到 `date`）超过 `stale_after` 天（缺省 90）未复核，降为 WARN，
   提醒复核后刷新 `last_verified` 或把 status 改回 draft。
6b. **认识论棘轮**：`10_knowledge/` 中 `date` 不早于 2026-09-14 的笔记必须声明
   `stance`（principle / author-view / ai-distilled / hypothesis / evidenced）。
   此前这件事只能写进正文，实测 8 篇各自即兴写成 `> **性质：xxx**`、四套词表混用；
   散文里的标记不能筛也不能查，而 recall.sh 的引用纪律要求「谁说的 + 适用条件」。
   存量 74 篇按棘轮不动；
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
    "material": "05_materials",
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
# 10_knowledge 认识论棘轮（2026-09-14 起）：新知识笔记必须声明 stance。
#
# 事由：`stance` 原本是 material 专属字段（frontmatter-spec「material 专属字段」表），
# 于是「这是通用原理 / 待验证假设 / AI 提炼 / 有实测证据」在 10_knowledge 层没有
# 字段可放，只能写进正文——实测 8 篇各自即兴写成第 14 行的 `> **性质：xxx**`，
# 词表还混着 `hypothesis` / `通用原理` / `[推断]` / `ai-distilled` 四套写法。
# 散文里的标记不能筛、不能查、不能被下游区分，而 recall.sh 的引用纪律恰恰要求
# 「谁说的 + 适用条件 + 当前符不符合」。这是**资料层比判据层更严**的倒挂：
# _templates/material.md 有「适用条件 / 失效条件」，knowledge-note.md 没有。
# 棘轮只管新笔记，存量 74 篇不动（与「项目笔记体积」同一条棘轮纪律）。
KNOWLEDGE_STANCE_RATCHET = "2026-09-14"
STANCE_VALUES = {"principle", "author-view", "ai-distilled", "hypothesis", "evidenced"}
# agent 缺失的历史豁免：2026-09-14 前的笔记缺 agent 只 WARN，不拦截。
#
# 事由：4 篇 2026-09-09~13 的 finance QC 笔记缺 agent，写入者已不可考——git author
# 是同一个人，但那几天 claude / codex / cursor 都在往这个 vault 写。provenance 字段
# 的唯一用途就是聚合「谁写了什么」，**填一个猜测值等于把它变成噪声，比缺着更坏**。
# 注意豁免范围：只豁免「缺」，不豁免「值不合法」；只豁免棘轮日之前，新笔记照常 ERROR。
AGENT_REQUIRED_FROM = "2026-09-14"
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
# 空文件检查（第 0 项）唯一豁免的路径：机器逐 run 写出来的台账。
# 只排这两个，不复用 SKIP_PATHS——因为 SKIP_PATHS 存在的理由是「这些文件本就
# 没有 frontmatter / 是外仓镜像」，而「文件是不是空的」跟它是不是一篇合规笔记无关，
# **空文件在任何一类里都不是有意为之**。
#
# 2026-09-04 12:54 实测：一次批量内容丢失把 6 个文件写成纯删除（4 个到 0~1 字节），
# auto-sync 在 2 秒后连提交带推送，而其中 `70_tutor/README.md` 被清成 0 字节整整
# 十天没有任何机制报过一声——因为 should_skip 是按 **basename** 匹配的，
# SKIP_PATHS 里的 "README.md" 跳过的是全库任意目录下的 README，而 docstring
# 写的是「README.md 导览页」（本意只指根层那一个）。
# 把空文件检查提到 should_skip 之前，这个盲区不必改 SKIP_PATHS 就关上了。
RUNTIME_LEDGERS = {".foresight", "可证伪点回检"}


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
        text = path.read_text(encoding="utf-8", errors="replace")

        # 0) 空文件。**跑在 should_skip 之前**——见 RUNTIME_LEDGERS 处的事由。
        if not text.strip() and rel.parts[0] not in RUNTIME_LEDGERS:
            errors.append(
                f"{rel}: 文件是空的（{len(text.encode())} 字节）。"
                "内容通常还在 git 里：先 `git log --follow -- <路径>` 找最后一个非空版本，"
                "再 `git show <sha>:<路径> > <路径>` 取回，别当新笔记重写"
            )
            continue

        if should_skip(path):
            continue

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

        date_val = fm.get("date", "")
        date_iso = date_val.strip('"')
        dated_before_agent_ratchet = bool(DATE_RE.match(date_iso)) and date_iso < AGENT_REQUIRED_FROM

        for field in REQUIRED_FIELDS:
            if fm.get(field):
                continue
            # 棘轮前的存量缺 agent 降为 WARN——见 AGENT_REQUIRED_FROM 处的事由。
            # 日期缺失或格式坏时不豁免：认不出日期就当它是新的，fail closed。
            if field == "agent" and dated_before_agent_ratchet:
                warns.append(
                    f"{rel}: 缺 agent（{date_iso} < {AGENT_REQUIRED_FROM} 存量豁免）——"
                    "如果还记得是谁写的就补上，不记得别猜"
                )
            else:
                errors.append(f"{rel}: frontmatter 缺字段 {field}")

        if date_val and not DATE_RE.match(date_iso):
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
        # 根层导览页（首页.md）豁免「type↔目录」这一项，但**不豁免** frontmatter 与死链检查：
        # 首页是滚动更新的导航页，必须放在 vault 根才能在 Obsidian 里当入口用，
        # 而它又大量使用双链，整文件跳过会丢掉死链这道最有价值的检查（2026-09-13）。
        is_root_page = len(rel.parts) == 1
        if expected_dir and not is_root_page and rel.parts[0] != expected_dir:
            errors.append(f"{rel}: type={note_type} 应放在 {expected_dir}/")

        # 认识论棘轮：棘轮日起的新知识笔记必须声明 stance——见 KNOWLEDGE_STANCE_RATCHET 处的事由。
        if rel.parts[0] == "10_knowledge" and DATE_RE.match(date_iso) and date_iso >= KNOWLEDGE_STANCE_RATCHET:
            stance = fm.get("stance", "").strip('"')
            if not stance:
                errors.append(
                    f"{rel}: 缺 stance（{KNOWLEDGE_STANCE_RATCHET} 起的新知识笔记必填，"
                    f"取值 {'/'.join(sorted(STANCE_VALUES))}）——"
                    "别把「谁的主张」和「已验证结论」写成同一种东西"
                )
            elif stance not in STANCE_VALUES:
                errors.append(
                    f"{rel}: stance={stance} 不在取值表里（{'/'.join(sorted(STANCE_VALUES))}），"
                    "见 30_conventions/frontmatter-spec.md"
                )

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
