#!/usr/bin/env python3
"""Distribution-level webnovel pacing, mobile readability, and autopilot-cliché mirror.

Designed as an objective diagnostic mirror (never a hard per-paragraph cage):
- Checks chapter-wide paragraph length distribution rather than flagging single 70-char lines.
- Adapts narration-wall and dialogue-ratio signals to narrative style (dialogue / first_person / rules).
- Detects reverse-AI-ness (mechanical uniform choppy 'telegraph' paragraphs).
- Flags only a minimal, unambiguous set of true LLM autopilot clichés/translationese.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


CJK_RE = re.compile(r"[\u4e00-\u9fff]")
SCENE_BREAK_RE = re.compile(r"^\s*(?:\*\s*\*\s*\*|-{3,}|⸻|✦\s*✦\s*✦)\s*$")
SUBHEADING_RE = re.compile(r"^\s*#{2,6}\s+.+$")
FIRST_CHAPTER_HINT_RE = re.compile(r"(?:^|[\\/])(?:第?0*1章|0*1[_-]|序章)")

# Spoken dialogue spans in Chinese prose (smart quotes, corner brackets, or straight double quotes)
SPOKEN_SPAN_RE = re.compile(
    r"“[^”\n]{2,}”|「[^」\n]{2,}」|『[^』\n]{2,}』|\"[^\"\n]{2,}\""
)
# Short inline scare quotes (<= 5 chars without speech punctuation) are NOT treated as spoken dialogue
NON_SPEECH_SHORT_QUOTE_RE = re.compile(
    r"^[“「『\"][^”」』\"\s，。！？；：、…—～~!?]{1,5}[”」』\"]$"
)
BARE_DIALOGUE_RE = re.compile(r"^(?:“[^”\n]+”|「[^」\n]+」|『[^』\n]+』|\"[^\"\n]+\")$")

# Minimal, unambiguous true LLM autopilot defects (NEVER ban ordinary Chinese words)
NARRATION_DEFECTS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "ai_contrast_not_but",
        re.compile(r"不是[^，。！？；\n]{1,30}[，,]?\s*而是"),
        "旁白二元说教句式「不是……而是……」，建议删去否定前半句直接写事实。",
    ),
    (
        "ai_contrast_rather_than",
        re.compile(r"与其说[^，。！？；\n]{1,30}[，,]?\s*不如说"),
        "旁白思辨腔「与其说……不如说……」，建议改为直给画面或感受。",
    ),
    (
        "ai_not_only_but_also",
        re.compile(r"这?不仅仅[是是一场次][^，。！？；\n]{1,30}[，,]?\s*更[是是一场次]"),
        "汇报拔高腔「这不仅仅是……更是……」，建议删除旁白拔高，用赌注或结果说话。",
    ),
    (
        "ai_era_opening",
        re.compile(r"在(?:这个|那片|这座)[^，。！？\n]{2,20}的(?:时代|世界|大陆|社会|年代)里"),
        "纪录片解说开场「在这个……的时代/世界里」，建议直接切入当下冲突现场。",
    ),
    (
        "ai_named_metaphor",
        re.compile(r"名为[「“\"']?[^」”\"'，。！？\n]{1,8}[」”\"']?的(?:种子|火焰|毒蛇|情绪|野心|恐惧|嫉妒|枷锁|深渊)"),
        "翻译腔隐喻「名为XX的种子/火焰/情绪」，建议换成具体念头或当下反应。",
    ),
    (
        "ai_wheel_of_fate",
        re.compile(r"命运的齿轮(?:开始|悄然|在这一刻)?转动"),
        "高频总结套话「命运的齿轮开始转动」，建议删去，让画面直接停在钩子上。",
    ),
    (
        "ai_indefinite_calque",
        re.compile(
            r"(?:一种|一股)(?:难以言喻|莫名|无形|说不出|奇异|异样|前所未有)的[^，。！？\n]{1,8}"
            r"|带着一种[^，。！？\n]{1,12}的(?:语气|神情|目光|姿态|口吻)"
        ),
        "英文不定冠词翻译腔「一种难以言喻的……/带着一种……语气」，建议直白写出。",
    ),
    (
        "ai_explanatory_tail",
        re.compile(r"[，,]\s*(?:仿佛在(?:证明|昭示|诉说|宣告|掩饰)|这(?:无疑)?意味着|显然已经说明)"),
        "画蛇添足的句尾解释尾巴，事实写清即可，不必替读者做阅读理解。",
    ),
]

GLOBAL_CLICHES: list[tuple[str, re.Pattern[str], str]] = [
    (
        "cliche_smirk_arc",
        re.compile(r"嘴角(?:勾起|扬起|扯出)(?:一抹|一丝)?[^，。！？\n]{0,8}弧度"),
        "工业神态废料「嘴角勾起弧度」，建议换成本篇角色自然的神情或一句话。",
    ),
    (
        "cliche_eye_flash",
        re.compile(r"眼(?:底|中|眸中|里)(?:闪过|掠过|划过)(?:一丝|一抹)(?:不易察觉的)?"),
        "工业眼神废料「眼底闪过一丝……」，建议换为可见停顿、动作或台词反击。",
    ),
    (
        "cliche_pupil_earthquake",
        re.compile(r"瞳孔(?:猛地|骤然|剧烈)?(?:一缩|地震|收缩)"),
        "工业应激废料「瞳孔一缩/地震」，建议换成贴合当下场景的具体反应。",
    ),
    (
        "cliche_air_froze",
        re.compile(r"空气(?:仿佛|似乎)?(?:在这一刻)?(?:凝固|冻结)了|死一般的寂静"),
        "偷懒氛围概括「空气凝固/死一般的寂静」，建议用具体声响停止或人物反应呈现。",
    ),
]

NOTICE_TEXT = (
    "本报告为网感分布体检镜子，不是必须清零的硬考题；"
    "有意为之的长段蓄势、毒舌独白或规则清单请直接保留，严禁机械切段或凑水对话。"
)


@dataclass
class Advisory:
    code: str
    line: int
    excerpt: str
    suggestion: str


def natural_sort_key(path: Path) -> list[int | str]:
    parts = re.split(r"(\d+)", path.name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def extract_spoken_spans(para: str) -> list[str]:
    spans: list[str] = []
    for m in SPOKEN_SPAN_RE.finditer(para):
        tok = m.group(0)
        # Filter out short inline emphasis terms like “规矩” unless preceded by speech colon
        if NON_SPEECH_SHORT_QUOTE_RE.match(tok):
            before = para[: m.start()].rstrip()
            if not (before.endswith("：") or before.endswith(":") or m.start() == 0):
                continue
        spans.append(tok)
    return spans


def strip_spoken_spans(para: str, spans: list[str]) -> str:
    if BARE_DIALOGUE_RE.match(para):
        return ""
    out = para
    for sp in spans:
        out = out.replace(sp, " ", 1)
    return out


def percentile(sorted_vals: list[int], q: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    idx = (len(sorted_vals) - 1) * q
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return round(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac, 1)


def analyze_file(
    path: Path,
    narrative: str = "dialogue",
    first_chapter: bool = False,
    target_words: int | None = None,
    tolerance: float = 0.20,
) -> tuple[list[Advisory], dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    advisories: list[Advisory] = []

    body_lines: list[tuple[int, str]] = []
    for idx, raw in enumerate(lines, start=1):
        s = raw.strip()
        if not s:
            continue
        if not body_lines and s.startswith("# "):
            continue
        if SCENE_BREAK_RE.match(s) or SUBHEADING_RE.match(s):
            continue
        body_lines.append((idx, s))

    total_cjk = 0
    dialogue_cjk = 0
    para_lengths: list[int] = []
    # (line_no, para_cjk, has_dialogue, is_bare_dialogue, para_text)
    para_records: list[tuple[int, int, bool, bool, str]] = []
    long_speeches = 0
    double_quote_spans = 0
    corner_quote_spans = 0

    for line_no, para in body_lines:
        p_cjk = len(CJK_RE.findall(para))
        if p_cjk == 0:
            continue
        total_cjk += p_cjk
        para_lengths.append(p_cjk)

        spoken_spans = extract_spoken_spans(para)
        for sp in spoken_spans:
            if sp.startswith("“"):
                double_quote_spans += 1
            elif sp.startswith("「"):
                corner_quote_spans += 1
        d_cjk = sum(len(CJK_RE.findall(sp)) for sp in spoken_spans)
        dialogue_cjk += d_cjk
        has_dialogue = d_cjk > 0
        is_bare = bool(BARE_DIALOGUE_RE.match(para))
        para_records.append((line_no, p_cjk, has_dialogue, is_bare, para))

        # Check single-turn lecture speech ("评审会演讲腔"): unbroken >110 chars OR combined same-para speech >125 chars
        max_span_cjk = max((len(CJK_RE.findall(sp)) for sp in spoken_spans), default=0)
        if max_span_cjk > 110 or d_cjk > 125:
            long_speeches += 1
            sample_span = spoken_spans[0] if spoken_spans else para
            advisories.append(
                Advisory(
                    "long_speech_monologue",
                    line_no,
                    sample_span[:55] + "...",
                    f"单回合角色发言达 {d_cjk} 字（最长单句 {max_span_cjk} 字），易显站桩演讲腔；若非刻意长独白，建议拆成“抛半截信息→对手打断→反手补刀”的多轮交锋。",
                )
            )

        # Minimal true LLM autopilot defects (check narration only for rhetoric; full para for clichés)
        narration = strip_spoken_spans(para, spoken_spans)
        for code, pattern, msg in NARRATION_DEFECTS:
            for m in pattern.finditer(narration):
                advisories.append(Advisory(code, line_no, m.group(0), msg))
        for code, pattern, msg in GLOBAL_CLICHES:
            for m in pattern.finditer(para):
                advisories.append(Advisory(code, line_no, m.group(0), msg))

    sorted_lens = sorted(para_lengths)
    mean_para = round(statistics.mean(para_lengths), 1) if para_lengths else 0.0
    median_para = round(statistics.median(para_lengths), 1) if para_lengths else 0.0
    p90_para = percentile(sorted_lens, 0.90)
    short_ratio = round(
        sum(1 for n in para_lengths if n <= 55) / len(para_lengths), 3
    ) if para_lengths else 0.0
    heavy_paras = sum(1 for n in para_lengths if n > 95)
    heavy_ratio = round(heavy_paras / len(para_lengths), 3) if para_lengths else 0.0
    dialogue_ratio = round(dialogue_cjk / total_cjk, 3) if total_cjk else 0.0

    # 1. Chapter-wide paragraph distribution check (NO single-paragraph 70-char hard rule!)
    heavy_ratio_limit = 0.25 if narrative == "dialogue" else 0.35
    if len(para_lengths) >= 8 and (median_para > 68.0 or heavy_ratio > heavy_ratio_limit):
        advisories.append(
            Advisory(
                "heavy_paragraph_distribution",
                1,
                f"中位段长 {median_para} 字，P90={p90_para} 字，>95字重度段占 {heavy_ratio*100:.1f}%",
                "整章段落分布偏重，有滑回传统出版长段密度的迹象；手机竖屏读感易发沉，可挑纯叙述长段在动作或气口处拆分。",
            )
        )

    # 2. Reverse-AI-ness detector: mechanical uniform choppy 'telegraph' paragraphs
    choppy_streak: list[tuple[int, int]] = []
    choppy_flagged = False

    def flush_choppy(run: list[tuple[int, int]]) -> None:
        nonlocal choppy_flagged
        if choppy_flagged or len(run) < 12:
            return
        sizes = [sz for _, sz in run]
        stdev = statistics.stdev(sizes) if len(sizes) >= 2 else 0.0
        if stdev <= 5.5:
            choppy_flagged = True
            advisories.append(
                Advisory(
                    "choppy_telegraph_uniformity",
                    run[0][0],
                    f"第 {run[0][0]}–{run[-1][0]} 行连续 {len(run)} 段非对白短段均挤在 12–38 字（标准差 {stdev:.1f}）",
                    "检测到疑似机械切段（AI 电报排骨体）；建议合并同类动作或留出 1–2 个完整强段，恢复自然长短反差。",
                )
            )

    for line_no, p_cjk, has_dialogue, _, _ in para_records:
        if (not has_dialogue) and 12 <= p_cjk <= 38:
            choppy_streak.append((line_no, p_cjk))
        else:
            flush_choppy(choppy_streak)
            choppy_streak = []
    flush_choppy(choppy_streak)

    # 3. Consecutive pure-narration wall streak (adaptive by narrative type)
    wall_min_paras, wall_min_cjk = (5, 260) if narrative == "dialogue" else (7, 400)
    wall_run: list[tuple[int, int]] = []
    wall_streaks = 0

    def flush_wall(run: list[tuple[int, int]]) -> None:
        nonlocal wall_streaks
        if len(run) >= wall_min_paras:
            sum_cjk = sum(sz for _, sz in run)
            if sum_cjk >= wall_min_cjk:
                wall_streaks += 1
                advisories.append(
                    Advisory(
                        "narration_wall_streak",
                        run[0][0],
                        f"第 {run[0][0]}–{run[-1][0]} 行连续 {len(run)} 段纯旁白无对白（共 {sum_cjk} 字）",
                        "局部出现较长纯叙述闷段；如非刻意蓄势、第一人称连珠炮吐槽或规则清单，可考虑切入对白交锋或压缩过场。",
                    )
                )

    for line_no, p_cjk, has_dialogue, _, _ in para_records:
        if not has_dialogue:
            wall_run.append((line_no, p_cjk))
        else:
            flush_wall(wall_run)
            wall_run = []
    flush_wall(wall_run)

    # 4. Dialogue ratio check (ONLY in 'dialogue' narrative mode — first_person/rules are exempt!)
    if narrative == "dialogue" and total_cjk >= 500 and dialogue_ratio < 0.28:
        advisories.append(
            Advisory(
                "low_dialogue_ratio",
                1,
                f"当前对话推进占比 {dialogue_ratio*100:.1f}%（dialogue 模式下偏低）",
                "若本篇定位为强对话交锋型，建议把部分旁白转述改成角色当场对峙、甩证据与回怼；若实际是第一人称吐槽体，可改用 --narrative first_person。",
            )
        )

    # 5. Opening golden 500-char hook scan (first chapter only)
    if first_chapter and para_records:
        # Check first 2 paragraphs for immediate exposition wall
        for line_no, p_cjk, has_dialogue, _, para in para_records[:2]:
            if (not has_dialogue) and p_cjk > 130:
                advisories.append(
                    Advisory(
                        "opening_exposition_wall",
                        line_no,
                        para[:50] + "...",
                        f"开篇前两段即出现 {p_cjk} 字纯旁白长段，黄金第一屏阅读门槛偏高；建议直接砸出当下冲突、台词或反常识规则。",
                    )
                )
        # Check first ~500 CJK chars for hook energy (dialogue or strong punctuation)
        opening_chunks: list[str] = []
        opening_cjk = 0
        opening_has_dialogue = False
        for _, p_cjk, has_dialogue, _, para in para_records:
            opening_chunks.append(para)
            opening_cjk += p_cjk
            if has_dialogue:
                opening_has_dialogue = True
            if opening_cjk >= 500:
                break
        opening_text = "\n".join(opening_chunks)
        has_punch = bool(re.search(r"[！？!?]", opening_text))
        if opening_cjk >= 350 and (not opening_has_dialogue) and (not has_punch):
            advisories.append(
                Advisory(
                    "opening_low_energy",
                    para_records[0][0],
                    f"前 {opening_cjk} 字内既无角色对白，也无问号/感叹号情绪张力",
                    "首章黄金 500 字偏平缓，建议核对是否及时抛出了奇观规则、当场危机或抓人悬念。",
                )
            )

    # 5.5 Mixed Chinese dialogue quote styles check (e.g. mixing “” and 「」 in Zhihu draft)
    if double_quote_spans > 0 and corner_quote_spans > 0:
        advisories.append(
            Advisory(
                "mixed_quote_styles",
                1,
                f"同章混用了 “” ({double_quote_spans} 处) 与 「」 ({corner_quote_spans} 处) 对话引号",
                "请全篇统一对话引号格式：知乎盐言统一用直角引号「」（嵌套用『』），其他平台默认用全角双引号“”。",
            )
        )

    # 6. Optional target word range reminder
    if target_words and target_words > 0:
        min_w = int(target_words * (1.0 - tolerance))
        max_w = int(target_words * (1.0 + tolerance))
        if total_cjk < min_w:
            advisories.append(
                Advisory(
                    "word_count_under_target",
                    1,
                    f"当前净汉字 {total_cjk} < 参考下限 {min_w}（目标 {target_words}）",
                    "低于预设目标区间；若爽点与钩子已干脆落地可保留精炼篇幅，切勿注水。",
                )
            )
        elif total_cjk > max_w:
            advisories.append(
                Advisory(
                    "word_count_over_target",
                    1,
                    f"当前净汉字 {total_cjk} > 参考上限 {max_w}（目标 {target_words}）",
                    "高于预设目标区间；可检查是否有过场水戏或可拆分到下一章的钩子。",
                )
            )

    metrics: dict[str, Any] = {
        "narrative": narrative,
        "cjk_chars": total_cjk,
        "paragraphs": len(para_lengths),
        "mean_para_cjk": mean_para,
        "median_para_cjk": median_para,
        "p90_para_cjk": p90_para,
        "short_para_ratio_le55": short_ratio,
        "heavy_para_count_gt95": heavy_paras,
        "heavy_para_ratio_gt95": heavy_ratio,
        "dialogue_ratio": dialogue_ratio,
        "narration_wall_streaks": wall_streaks,
        "long_speech_monologues": long_speeches,
        "advisories": len(advisories),
    }
    return advisories, metrics


def discover_md_files(directory: Path) -> list[Path]:
    excluded = {"00_脑洞与节拍", "01_轻量状态", "readme", "license"}
    files: list[Path] = []
    for p in sorted(directory.glob("*.md"), key=natural_sort_key):
        if p.stem.lower() in excluded or p.stem.startswith("00_"):
            continue
        files.append(p)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="网文短篇分布体检镜子：检测段长分布、连续闷段、百字演讲腔、对话占比、机械碎段反模式与极简 AI 废料（非硬考题）。"
    )
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--file", type=Path, help="单个正文 Markdown 文件")
    target_group.add_argument("--dir", type=Path, help="正文目录（批量体检全部章节）")
    parser.add_argument(
        "--narrative",
        choices=("dialogue", "first_person", "rules"),
        default="dialogue",
        help="推进叙事类型（默认 dialogue）",
    )
    parser.add_argument(
        "--first-chapter",
        action="store_true",
        help="显式启用首章黄金 500 字开篇检查（--dir 模式自动对首章启用）",
    )
    parser.add_argument("--target-words", type=int, default=0, help="可选单章参考汉字数")
    parser.add_argument("--tolerance", type=float, default=0.20, help="允许偏差比例（默认 0.20）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    if args.target_words < 0:
        parser.error("--target-words 不能为负数。")
    if not 0.0 <= args.tolerance <= 1.0:
        parser.error("--tolerance 必须在 0 到 1 之间。")

    targets: list[tuple[Path, bool]] = []
    if args.file:
        p = args.file.expanduser().resolve()
        if not p.is_file():
            print(f"ERROR: File not found: {p}", file=sys.stderr)
            return 2
        is_first = args.first_chapter or bool(FIRST_CHAPTER_HINT_RE.search(p.name))
        targets.append((p, is_first))
    else:
        d = args.dir.expanduser().resolve()
        if not d.is_dir():
            print(f"ERROR: Directory not found: {d}", file=sys.stderr)
            return 2
        files = discover_md_files(d)
        if not files:
            print(f"ERROR: No chapter Markdown files found in: {d}", file=sys.stderr)
            return 2
        for idx, fp in enumerate(files):
            targets.append((fp, idx == 0 or args.first_chapter))

    results: list[dict[str, Any]] = []
    total_cjk_all = 0
    for fp, is_first in targets:
        advs, metrics = analyze_file(
            fp,
            narrative=args.narrative,
            first_chapter=is_first,
            target_words=args.target_words or None,
            tolerance=args.tolerance,
        )
        total_cjk_all += int(metrics["cjk_chars"])
        results.append(
            {
                "file": str(fp),
                "first_chapter_checked": is_first,
                "metrics": metrics,
                "advisories": [asdict(a) for a in advs],
            }
        )

    if args.json:
        payload = {
            "notice": NOTICE_TEXT,
            "files_scanned": len(results),
            "total_cjk_chars": total_cjk_all,
            "results": results,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(NOTICE_TEXT)
        if len(results) > 1:
            print(f"scanned={len(results)} total_cjk_chars={total_cjk_all}")
        for item in results:
            m = item["metrics"]
            print(f"\nfile={item['file']}")
            print(
                "metrics "
                f"narrative={m['narrative']} cjk={m['cjk_chars']} paras={m['paragraphs']} "
                f"median_para={m['median_para_cjk']} mean_para={m['mean_para_cjk']} p90={m['p90_para_cjk']} "
                f"short<=55={m['short_para_ratio_le55']*100:.1f}% heavy>95={m['heavy_para_ratio_gt95']*100:.1f}% "
                f"dialogue={m['dialogue_ratio']*100:.1f}% walls={m['narration_wall_streaks']} "
                f"long_speeches={m['long_speech_monologues']} advisories={m['advisories']}"
            )
            for adv in item["advisories"]:
                print(
                    f"  [ADVISORY] line {adv['line']} ({adv['code']}): "
                    f"「{adv['excerpt']}」 -> {adv['suggestion']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
