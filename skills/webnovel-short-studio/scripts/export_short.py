#!/usr/bin/env python3
"""Export clean short-webnovel Markdown chapters to screen/book DOCX and/or platform-ready plain TXT."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


CJK_RE = re.compile(r"[\u4e00-\u9fff]")
SCENE_BREAK_RE = re.compile(r"^\s*(?:\*\s*\*\s*\*|-{3,}|⸻|✦\s*✦\s*✦)\s*$")
WORKBENCH_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:RULE|INST|FAC|HIST|CON|SEED|WS|WCR|REG|CHAR|ARC|SEQ|EVT|CH|LOOP|WLOOP|CR|F|T|S)-\d{2,3}(?![A-Za-z0-9_])"
    r"|@(?:CHAR|LOC|PROP|VOICE)-\d{2,3}(?![A-Za-z0-9_])"
    r"|\[(?:待确认|待补充|待填|待试写确认后填入)[^\]\n]*\]"
    r"|\{\{[^{}\n]+\}\}"
)
CHAPTER_NUM_RE = re.compile(r"第\s*([0-9]+|[零〇一二两三四五六七八九十百千]+)\s*[章节回]")
EXCLUDED_STEMS = {"00_脑洞与节拍", "01_轻量状态", "写作状态", "00_文风与声口卡", "readme", "license"}

PAGE_SIZES_MM: dict[str, tuple[float, float, tuple[float, float, float, float]]] = {
    "a4": (210.0, 297.0, (24.0, 22.0, 26.0, 26.0)),
    "b5": (176.0, 250.0, (20.0, 19.0, 21.0, 21.0)),
    "a5": (148.0, 210.0, (17.0, 16.0, 18.0, 18.0)),
}

CN_DIGITS: dict[str, int] = {
    "零": 0,
    "〇": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}
CN_UNITS: dict[str, int] = {"十": 10, "百": 100, "千": 1000}


def parse_chapter_num_token(token: str) -> int | None:
    if token.isdigit():
        return int(token)
    total = 0
    current = 0
    seen_unit = False
    for ch in token:
        if ch in CN_DIGITS:
            current = CN_DIGITS[ch]
        elif ch in CN_UNITS:
            unit = CN_UNITS[ch]
            seen_unit = True
            if current == 0 and unit == 10 and total == 0:
                current = 1
            total += current * unit
            current = 0
        else:
            return None
    val = total + current
    if val == 0 and not seen_unit and token not in ("零", "〇"):
        return None
    return val


def extract_chapter_number(title: str) -> int | None:
    m = CHAPTER_NUM_RE.search(title)
    if not m:
        return None
    return parse_chapter_num_token(m.group(1))


def natural_sort_key(path: Path) -> list[int | str]:
    parts = re.split(r"(\d+)", path.name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def discover_chapters(chapters_dir: Path) -> list[Path]:
    if not chapters_dir.is_dir():
        raise ValueError(f"Chapters directory does not exist: {chapters_dir}")
    candidates: list[Path] = []
    for path in sorted(chapters_dir.glob("*.md"), key=natural_sort_key):
        stem_lower = path.stem.lower()
        if stem_lower in EXCLUDED_STEMS or stem_lower.startswith("00_"):
            continue
        candidates.append(path)
    if not candidates:
        raise ValueError(f"No chapter Markdown files found in: {chapters_dir}")
    return candidates


def parse_chapter(path: Path, default_index: int) -> tuple[str, list[tuple[str, str]]]:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = raw.splitlines()
    chapter_title = ""
    blocks: list[tuple[str, str]] = []

    for line in lines:
        s = line.strip()
        if not s:
            continue
        if not chapter_title and not blocks and s.startswith("# "):
            chapter_title = re.sub(r"\s+#+\s*$", "", s[2:]).strip()
            continue
        if SCENE_BREAK_RE.match(s):
            blocks.append(("scene_break", "* * *"))
            continue
        if re.match(r"^#{2,6}\s+", s):
            sub = re.sub(r"^#{2,6}\s+|\s+#+\s*$", "", s).strip()
            blocks.append(("subheading", sub))
            continue
        # Treat every non-empty body line as its own paragraph (matching lint_webnovel.py)
        blocks.append(("paragraph", s))

    if not chapter_title:
        chapter_title = path.stem.replace("_", " ") or f"第{default_index}节"
    return chapter_title, blocks


def strip_inline_md(text: str) -> str:
    return re.sub(r"\*\*([^*]+)\*\*|\*([^*]+)\*", lambda m: m.group(1) or m.group(2), text)


def check_chapter_sequence_warnings(
    parsed: list[tuple[Path, str, list[tuple[str, str]]]]
) -> list[str]:
    warnings: list[str] = []
    seen: dict[int, str] = {}
    prev_num: int | None = None
    prev_name: str = ""

    for ch_path, ch_title, _ in parsed:
        num = extract_chapter_number(ch_title)
        if num is None:
            continue
        if num in seen:
            warnings.append(
                f"章节序号重复：第{num}章（{ch_path.name} 与 {seen[num]} 重复）"
            )
        elif prev_num is not None and num != prev_num + 1:
            warnings.append(
                f"章节序号跳号或乱序：第{prev_num}章（{prev_name}）-> 第{num}章（{ch_path.name}）"
            )
        seen.setdefault(num, ch_path.name)
        prev_num = num
        prev_name = ch_path.name
    return warnings


def parse_and_validate(
    chapter_paths: list[Path], allow_workbench_tokens: bool
) -> tuple[list[tuple[Path, str, list[tuple[str, str]]]], int, list[str]]:
    parsed: list[tuple[Path, str, list[tuple[str, str]]]] = []
    leaks: list[str] = []
    total_cjk = 0

    for idx, ch_path in enumerate(chapter_paths, start=1):
        ch_title, blocks = parse_chapter(ch_path, idx)
        parsed.append((ch_path, ch_title, blocks))
        if not allow_workbench_tokens:
            for m in WORKBENCH_TOKEN_RE.finditer(ch_title):
                leaks.append(f"{ch_path.name}(标题): {m.group(0)}")
        for _, b_text in blocks:
            total_cjk += len(CJK_RE.findall(b_text))
            if not allow_workbench_tokens:
                for m in WORKBENCH_TOKEN_RE.finditer(b_text):
                    leaks.append(f"{ch_path.name}: {m.group(0)}")

    if leaks:
        preview = ", ".join(leaks[:5])
        raise ValueError(
            f"检测到标题或正文残留内部工程标记（{preview}）。请清理后再导出，或传入 --allow-workbench-tokens。"
        )

    warnings = check_chapter_sequence_warnings(parsed)
    return parsed, total_cjk, warnings


def export_txt(
    parsed: list[tuple[Path, str, list[tuple[str, str]]]],
    out_txt: Path,
    title: str,
    include_title_header: bool = True,
) -> dict[str, Any]:
    lines: list[str] = []
    if include_title_header:
        lines.append(title)
        lines.append("")

    multi = len(parsed) > 1
    for ch_idx, (_, ch_title, blocks) in enumerate(parsed):
        if ch_idx > 0:
            lines.append("")
        if multi or (ch_title and ch_title != title):
            lines.append(ch_title)
            lines.append("")
        for kind, b_text in blocks:
            if kind == "scene_break":
                lines.append("———")
                lines.append("")
            elif kind == "subheading":
                lines.append(strip_inline_md(b_text))
                lines.append("")
            else:
                lines.append(strip_inline_md(b_text))
                lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    out_txt.write_text(content, encoding="utf-8")
    return {"txt_output": str(out_txt.resolve())}


def set_style_fonts(style: Any, ascii_font: str, east_asia_font: str, qn: Any) -> None:
    style.font.name = ascii_font
    rfonts = style._element.get_or_add_rPr().get_or_add_rFonts()
    for slot in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme", "csTheme"):
        rfonts.attrib.pop(qn("w:" + slot), None)
    rfonts.set(qn("w:ascii"), ascii_font)
    rfonts.set(qn("w:hAnsi"), ascii_font)
    rfonts.set(qn("w:cs"), ascii_font)
    rfonts.set(qn("w:eastAsia"), east_asia_font)


def add_inline_runs(paragraph: Any, text: str) -> None:
    pattern = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*)")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos : m.start()])
        token = m.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            run.bold = True
        else:
            run = paragraph.add_run(token[1:-1])
            run.italic = True
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def add_page_number_field(paragraph: Any, OxmlElement: Any, qn: Any) -> None:
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def export_docx(
    parsed: list[tuple[Path, str, list[tuple[str, str]]]],
    total_cjk: int,
    out_docx: Path,
    title: str,
    subtitle: str = "",
    author: str = "",
    preset: str = "screen",
    page_size: str = "a4",
) -> dict[str, Any]:
    try:
        from docx import Document
        from docx.enum.style import WD_STYLE_TYPE
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Mm, Pt, RGBColor
    except ImportError as exc:
        raise RuntimeError(
            "导出 DOCX 需要 python-docx，请先安装：python -m pip install python-docx"
        ) from exc

    doc = Document()
    section = doc.sections[0]
    w_mm, h_mm, (top_mm, bot_mm, left_mm, right_mm) = PAGE_SIZES_MM[page_size]
    section.page_width = Mm(w_mm)
    section.page_height = Mm(h_mm)
    section.top_margin = Mm(top_mm)
    section.bottom_margin = Mm(bot_mm)
    section.left_margin = Mm(left_mm)
    section.right_margin = Mm(right_mm)
    section.different_first_page_header_footer = True

    body_ascii, body_ea = ("Segoe UI", "微软雅黑") if preset == "screen" else ("Georgia", "宋体")
    head_ascii, head_ea = ("Segoe UI", "微软雅黑")
    body_pt = 11.0 if preset == "screen" else 11.5

    ink_color = RGBColor(0x22, 0x22, 0x22)
    title_color = RGBColor(0x1B, 0x26, 0x3B)
    muted_color = RGBColor(0x5C, 0x67, 0x7D)

    normal = doc.styles["Normal"]
    set_style_fonts(normal, body_ascii, body_ea, qn)
    normal.font.size = Pt(body_pt)
    normal.font.color.rgb = ink_color

    novel_body = doc.styles.add_style("Short Body", WD_STYLE_TYPE.PARAGRAPH)
    novel_body.base_style = normal
    set_style_fonts(novel_body, body_ascii, body_ea, qn)
    novel_body.font.size = Pt(body_pt)
    novel_body.font.color.rgb = ink_color
    pf = novel_body.paragraph_format
    pf.space_before = Pt(0)
    if preset == "screen":
        pf.line_spacing = 1.55
        pf.space_after = Pt(7.5)
        pf.first_line_indent = Pt(0)
    else:
        pf.line_spacing = 1.48
        pf.space_after = Pt(2.0)
        pf.first_line_indent = Pt(body_pt * 2)

    h1 = doc.styles["Heading 1"]
    set_style_fonts(h1, head_ascii, head_ea, qn)
    h1.font.size = Pt(15.5)
    h1.font.bold = True
    h1.font.color.rgb = title_color
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(12)
    h1.paragraph_format.first_line_indent = Pt(0)
    h1.paragraph_format.keep_with_next = True
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT if preset == "screen" else WD_ALIGN_PARAGRAPH.CENTER

    hdr_p = section.header.paragraphs[0]
    hdr_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr_run = hdr_p.add_run(title)
    hdr_run.font.size = Pt(9)
    hdr_run.font.color.rgb = muted_color

    ftr_p = section.footer.paragraphs[0]
    ftr_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_number_field(ftr_p, OxmlElement, qn)
    for r in ftr_p.runs:
        r.font.size = Pt(9)
        r.font.color.rgb = muted_color

    # Clean Title Header / Compact Cover
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(84)
    ct = doc.add_paragraph()
    ct.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ct.paragraph_format.first_line_indent = Pt(0)
    ct.paragraph_format.space_after = Pt(10)
    ct_run = ct.add_run(title)
    ct_run.bold = True
    ct_run.font.size = Pt(24)
    ct_run.font.color.rgb = title_color

    if not subtitle:
        if len(parsed) == 1:
            subtitle = f"约 {total_cjk:,} 字"
        else:
            subtitle = f"共 {len(parsed)} 节 · 约 {total_cjk:,} 字"
    cs = doc.add_paragraph()
    cs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cs.paragraph_format.first_line_indent = Pt(0)
    cs_run = cs.add_run(subtitle)
    cs_run.font.size = Pt(11.5)
    cs_run.font.color.rgb = muted_color

    meta_parts = [p for p in (author.strip(), date.today().isoformat()) if p]
    cm = doc.add_paragraph()
    cm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cm.paragraph_format.first_line_indent = Pt(0)
    cm.paragraph_format.space_before = Pt(28)
    cm_run = cm.add_run(" · ".join(meta_parts))
    cm_run.font.size = Pt(9.5)
    cm_run.font.color.rgb = muted_color

    total_paragraphs = 0
    for idx, (_, ch_title, blocks) in enumerate(parsed):
        hp = doc.add_paragraph(style="Heading 1")
        if idx == 0 or preset == "book":
            hp.paragraph_format.page_break_before = True
        hp.add_run(ch_title)

        for kind, b_text in blocks:
            if kind == "scene_break":
                sp = doc.add_paragraph(style="Short Body")
                sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                sp.paragraph_format.first_line_indent = Pt(0)
                sp.paragraph_format.space_before = Pt(6)
                sp.paragraph_format.space_after = Pt(6)
                sr = sp.add_run("* * *")
                sr.font.color.rgb = muted_color
            elif kind == "subheading":
                sub_p = doc.add_paragraph(style="Short Body")
                sub_p.paragraph_format.first_line_indent = Pt(0)
                sub_p.paragraph_format.space_before = Pt(8)
                sub_p.paragraph_format.space_after = Pt(4)
                sub_p.paragraph_format.keep_with_next = True
                sr = sub_p.add_run(b_text)
                sr.bold = True
            else:
                bp = doc.add_paragraph(style="Short Body")
                add_inline_runs(bp, b_text)
                total_paragraphs += 1

    out_docx.parent.mkdir(parents=True, exist_ok=True)
    doc.core_properties.title = title
    doc.core_properties.author = author
    doc.core_properties.subject = subtitle
    doc.save(out_docx)
    return {"docx_output": str(out_docx.resolve()), "paragraphs": total_paragraphs}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将短篇网文纯净正文导出为屏幕/审阅友好 DOCX 和/或平台发布用纯文本 TXT。"
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--source", type=Path, help="单个正文 Markdown 文件")
    src.add_argument("--chapters-dir", type=Path, help="正文章节目录")
    parser.add_argument("--out-docx", type=Path, default=None, help="输出 .docx 路径")
    parser.add_argument("--out-txt", type=Path, default=None, help="输出纯文本 .txt 路径")
    parser.add_argument("--title", default="", help="作品标题")
    parser.add_argument("--subtitle", default="", help="可选副标题")
    parser.add_argument("--author", default="", help="可选作者名")
    parser.add_argument(
        "--preset",
        choices=("screen", "book"),
        default="screen",
        help="DOCX 排版预设：screen（默认，无缩进清爽段距，贴近手机/屏幕审阅）或 book（传统首行缩进）",
    )
    parser.add_argument(
        "--page-size",
        choices=("a4", "b5", "a5"),
        default="a4",
        help="页面尺寸（默认 a4）",
    )
    parser.add_argument(
        "--allow-workbench-tokens",
        action="store_true",
        help="允许残留内部标记继续导出",
    )
    args = parser.parse_args()

    if not args.out_docx and not args.out_txt:
        parser.error("请至少指定 --out-docx 或 --out-txt 之一。")

    try:
        if args.source:
            s_path = args.source.expanduser().resolve()
            if not s_path.is_file():
                parser.error(f"Source file not found: {s_path}")
            chapters = [s_path]
            inferred_title = args.title.strip() or s_path.stem.replace("_", " ")
        else:
            c_dir = args.chapters_dir.expanduser().resolve()
            chapters = discover_chapters(c_dir)
            inferred_title = args.title.strip() or c_dir.parent.name or "短篇网文"

        parsed, total_cjk, warnings = parse_and_validate(chapters, args.allow_workbench_tokens)
        result: dict[str, Any] = {
            "title": inferred_title,
            "chapters": len(parsed),
            "cjk_chars": total_cjk,
            "warnings": warnings,
        }
        if args.out_docx:
            result.update(
                export_docx(
                    parsed=parsed,
                    total_cjk=total_cjk,
                    out_docx=args.out_docx.expanduser().resolve(),
                    title=inferred_title,
                    subtitle=args.subtitle,
                    author=args.author,
                    preset=args.preset,
                    page_size=args.page_size,
                )
            )
        if args.out_txt:
            result.update(
                export_txt(
                    parsed=parsed,
                    out_txt=args.out_txt.expanduser().resolve(),
                    title=inferred_title,
                )
            )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for w in warnings:
        print(f"[WARNING] {w}", file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
