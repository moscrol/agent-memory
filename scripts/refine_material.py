#!/usr/bin/env python3
"""整理与归档 —— 知识外脑的机械半自动环节（无第三方依赖）。

分工要说清楚：
  · 本脚本做「机械」部分：读 frontmatter、查重、判类型建议、改 type、移动文件、补字段、记关联。
  · 「提炼」是语义工作，由助手（Agent）在读完原文后完成，写进 10_knowledge/。
    脚本不会假装自己能提炼，也不会自动生成知识结论。

用法::

    python3 scripts/refine_material.py --scan
        列出 00_inbox 中待处理条目 + 查重提示 + 归档去向建议。

    python3 scripts/refine_material.py --promote 00_inbox/xxx.md --to material
        升格为外部资料：type 改 material、补 stance、移入 05_materials/。

    python3 scripts/refine_material.py --promote 00_inbox/xxx.md --to knowledge
        升格为知识笔记：type 改 knowledge、移入 10_knowledge/。

    python3 scripts/refine_material.py --link 05_materials/xxx.md 10_knowledge/yyy.md
        在资料上登记 refined_into 关联（资料 → 知识），幂等。

退出码：0=成功，1=有失败（原文件保持不动），2=用法错误。
失败时保留待处理状态——不删、不移动、不改。
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]
INBOX = VAULT / "00_inbox"
MATERIALS = VAULT / "05_materials"
KNOWLEDGE = VAULT / "10_knowledge"

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


def split_note(path: Path) -> tuple[dict, str, str]:
    """返回 (frontmatter 字段, frontmatter 原文, 正文)。无 frontmatter 时字段为空。"""
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        return {}, "", text
    fm_raw = m.group(1)
    fields: dict[str, str] = {}
    for line in fm_raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            fields[k.strip()] = v.strip()
    return fields, fm_raw, text[m.end():]


def render_note(fields: dict, body: str, order: list[str]) -> str:
    lines = ["---"]
    for k in order:
        if k in fields and fields[k] != "":
            lines.append(f"{k}: {fields[k]}")
    for k, v in fields.items():
        if k not in order and v != "":
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n" + body


def cmd_scan() -> int:
    if not INBOX.is_dir():
        print("找不到 00_inbox/")
        return 1
    items = []
    for p in sorted(INBOX.glob("*.md")):
        fields, _, body = split_note(p)
        items.append((p, fields, body))

    if not items:
        print("00_inbox/ 为空，没有待整理条目。")
        return 0

    # 查重：按 source_url 与标题归一化
    by_url: dict[str, list[str]] = {}
    by_title: dict[str, list[str]] = {}
    for p, f, _ in items:
        u = f.get("source_url", "").strip()
        if u:
            by_url.setdefault(u, []).append(p.name)
        t = re.sub(r"[\s\-_·，。、,.]", "", f.get("title", p.stem)).lower()
        by_title.setdefault(t, []).append(p.name)

    # 已有资料与知识，用于给关联建议
    existing_materials = {p.name for p in MATERIALS.glob("*.md")} if MATERIALS.is_dir() else set()
    existing_knowledge = {p.stem for p in KNOWLEDGE.glob("*.md")} if KNOWLEDGE.is_dir() else set()

    print(f"待整理：{len(items)} 条\n")
    age_warn = 0
    for p, f, body in items:
        title = f.get("title", p.stem)
        m = DATE_PREFIX_RE.match(p.name)
        age = ""
        if m:
            d = dt.date.fromisoformat(m.group(1))
            days = (dt.date.today() - d).days
            age = f"，{days} 天前"
            if days > 14:
                age_warn += 1
        print(f"· {p.name}{age}")
        print(f"    标题：{title}")
        if f.get("source_url"):
            print(f"    来源：{f['source_url']}")

        dup = [n for n in by_url.get(f.get("source_url", "").strip(), []) if n != p.name]
        if not dup:
            t = re.sub(r"[\s\-_·，。、,.]", "", title).lower()
            dup = [n for n in by_title.get(t, []) if n != p.name]
        if dup:
            print(f"    ⚠ 疑似重复：{', '.join(dup)}  → 先建关联，不要擅自合并或删除")

        has_body = len(body.strip()) > 60 and "待补" not in body
        # 外部输入（带来源链接或已标 stance）先落资料层；提炼出的方法另建知识笔记。
        is_external = bool(f.get("source_url")) or "stance" in f
        if is_external:
            target = "material"
            hint = "外部资料 → 05_materials/" + (
                "；若有可复用方法，另建一篇 knowledge 并用 --link 登记来源链"
                if has_body else "；正文不足，先补摘录"
            )
        else:
            target = "knowledge" if has_body else "material"
            hint = ("自产产出，可提炼 → 10_knowledge/ 草稿"
                    if has_body else "内容不足 → 先补，或只留资料层")
        print(f"    归档建议：{hint}")
        print(f"    升格命令：python3 scripts/refine_material.py --promote {p.relative_to(VAULT)} --to {target}")
        print()

    print(f"现有资料 {len(existing_materials)} 篇 / 现有知识 {len(existing_knowledge)} 篇")
    if age_warn:
        print(f"注：{age_warn} 条已超过 14 天未整理（vault_lint 会 WARN）。")
    return 0


ORDER = ["title", "type", "agent", "source", "date", "tags", "status",
         "source_url", "author", "stance", "refined_into", "related"]


def cmd_promote(rel: str, to: str) -> int:
    src = (VAULT / rel).resolve()
    if not src.is_file():
        print(f"找不到文件：{rel}")
        return 1
    if to not in ("material", "knowledge"):
        print("--to 只能是 material 或 knowledge")
        return 2

    dest_dir = MATERIALS if to == "material" else KNOWLEDGE
    if not dest_dir.is_dir():
        print(f"目标目录不存在：{dest_dir.name}/")
        return 1

    fields, _, body = split_note(src)
    fields["type"] = to
    fields.setdefault("agent", "claude")
    fields.setdefault("date", dt.date.today().isoformat())
    if to == "material":
        fields.setdefault("stance", "author-view")
        if "tags" not in fields or fields["tags"] in ("[]", ""):
            fields["tags"] = "[material]"
    if to == "knowledge":
        fields["status"] = "draft"

    # 升格后清理不再成立的占位标签
    raw_tags = fields.get("tags", "")
    if raw_tags.startswith("[") and raw_tags.endswith("]"):
        kept = [t.strip() for t in raw_tags[1:-1].split(",") if t.strip()]
        kept = [t for t in kept if t not in ("capture", "inbox", "待整理")]
        if not kept:
            kept = [to]
        fields["tags"] = "[" + ", ".join(kept) + "]"

    # 去掉收集阶段留下的"待整理"提示行
    body = "\n".join(
        line for line in body.lstrip("\n").splitlines()
        if not line.strip().startswith("> 待整理。")
    ).lstrip("\n")

    # 文件名去掉日期前缀（资料/知识层用内容命名）
    stem = DATE_PREFIX_RE.sub("", src.stem)
    dest = dest_dir / f"{stem}.md"
    if dest.exists():
        print(f"目标已存在，未覆盖：{dest.relative_to(VAULT)}")
        return 1

    try:
        dest.write_text(render_note(fields, body.lstrip("\n"), ORDER), encoding="utf-8")
    except OSError as e:
        print(f"写入失败，原文件保持不动：{e}")
        return 1
    try:
        src.unlink()
    except OSError as e:
        print(f"警告：已写入 {dest.relative_to(VAULT)}，但删除原文件失败（{e}）。请手工确认。")
        return 1

    print(f"已升格：{rel} → {dest.relative_to(VAULT)}")
    print(f"  type={to}" + ("，stance=" + fields.get("stance", "") if to == "material" else "，status=draft"))
    return 0


def cmd_link(material_rel: str, knowledge_rel: str) -> int:
    mat = (VAULT / material_rel).resolve()
    kno = (VAULT / knowledge_rel).resolve()
    for p in (mat, kno):
        if not p.is_file():
            print(f"找不到文件：{p.relative_to(VAULT) if p.is_relative_to(VAULT) else p}")
            return 1

    fields, _, body = split_note(mat)
    link = f"[[{kno.stem}]]"
    raw = fields.get("refined_into", "")
    if link in raw:
        print(f"已存在该关联，未重复写入：{material_rel} → {link}")
        return 0
    if raw in ("", "[]"):
        fields["refined_into"] = f"[{link}]"
    else:
        fields["refined_into"] = raw.rstrip("]") + f", {link}]" if raw.endswith("]") else f"[{link}]"

    try:
        mat.write_text(render_note(fields, body.lstrip("\n"), ORDER), encoding="utf-8")
    except OSError as e:
        print(f"写入失败，未改动：{e}")
        return 1
    print(f"已登记关联：{material_rel} → {link}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="知识外脑：整理与归档（机械半自动）")
    ap.add_argument("--scan", action="store_true", help="列出待整理条目与归档建议")
    ap.add_argument("--promote", metavar="FILE", help="升格一个 inbox 条目")
    ap.add_argument("--to", choices=["material", "knowledge"], help="升格去向")
    ap.add_argument("--link", nargs=2, metavar=("MATERIAL", "KNOWLEDGE"), help="登记资料→知识关联")
    args = ap.parse_args()

    if args.scan:
        return cmd_scan()
    if args.link:
        return cmd_link(*args.link)
    if args.promote:
        if not args.to:
            print("--promote 需要同时给 --to material|knowledge")
            return 2
        return cmd_promote(args.promote, args.to)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
