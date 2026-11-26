#!/usr/bin/env python3
"""Distribution-level webnovel pacing, mobile readability, Fanqie precheck, and autopilot-cliché mirror.

Designed as an objective diagnostic mirror (never a hard per-paragraph cage; always exit code 0 on lint runs):
- Checks chapter-wide paragraph length distribution rather than flagging single 70-char lines.
- Adapts narration-wall and dialogue-ratio signals to narrative style (dialogue / first_person / rules).
- Detects reverse-AI-ness (mechanical uniform choppy 'telegraph' paragraphs & staircase micro-paragraphs).
- Includes Fanqie 2026-11 pre-submission typography, stiff-prose, and optional character-name drift checks.
- Flags only a minimal, unambiguous set of true LLM autopilot clichés/translationese outside spoken dialogue.
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
FIRST_CHAPTER_HINT_RE = re.compile(
    r"(?:^|[\\/])(?:第?(?:0*1|一)[章节回]|0*1[_-]|序章|楔子)"
)

# Spoken dialogue spans in Chinese prose (smart quotes, corner brackets, or straight double quotes; 1+ chars)
SPOKEN_SPAN_RE = re.compile(
    r"“[^”\n]{1,}”|「[^」\n]{1,}」|『[^』\n]{1,}』|\"[^\"\n]{1,}\""
)
# Short inline scare quotes (<= 5 chars without speech punctuation) require speech context to count as spoken dialogue
NON_SPEECH_SHORT_QUOTE_RE = re.compile(
    r"^[“「『\"][^”」』\"\s，。！？；：、…—～~!?]{1,5}[”」』\"]$"
)
NON_SPEECH_AFTER_RE = re.compile(
    r"^(?:二字|两字|两个字|三字|三个字|四字|四个字|几个字|这[一两三]?个?字|字样|标签|称号|名头|之类)"
)
BARE_DIALOGUE_RE = re.compile(r"^(?:“[^”\n]+”|「[^」\n]+」|『[^』\n]+』|\"[^\"\n]+\")$")

# Exempt contexts for bare dialogue / staircase / spec-list / parallel sentence checks
SMS_DANMAKU_CROWD_RE = re.compile(
    r"短信|微信|聊天|弹幕|评论|留言|帖子|群聊|朋友圈|手机屏幕|消息弹出|发来|回复道|"
    r"电话那头|听筒里|免提|【弹幕】|\[弹幕\]|围观|众人|七嘴八舌|议论|哄笑|起哄|热搜|"
    r"楼[上主]|1楼|2楼|网友|直播间|公屏|群里"
)
PANEL_OR_STAT_LINE_RE = re.compile(
    r"^(?:【[^】\n]+】|\[[^\]\n]+\]|「系统|“系统|叮[！!，,]|恭喜宿主|提示[：:]|公告[：:]|任务[：:]|系统提示)"
)
PANEL_HEADER_CONTEXT_RE = re.compile(
    r"系统|面板|属性|任务|清单|提示|公告|状态栏|档案|简历|信息栏|【|\["
)
RULE_LIST_LINE_RE = re.compile(
    r"^(?:第?[一二三四五六七八九十百0-9]{1,3}[条点项、\.）\)]|[-•·▪]\s*|【[^】]{1,12}】|\[[^\]]{1,12}\])"
)
SPEC_KV_LINE_RE = re.compile(r"^[^：“”「」『』\n]{1,10}[：:]\s*\S+")

# Typography & Fanqie precheck patterns
URL_RE = re.compile(r"https?://\S+")
ASCII_PUNCT_NEAR_CJK_RE = re.compile(
    r"[\u4e00-\u9fff][,\.?!:;]|(?<![A-Za-z0-9])[,\.?!:;][\u4e00-\u9fff]"
)
DECORATIVE_SYM_RE = re.compile(r"[△★☆♥♡♛♚√✔✕✖●○◆◇■□▲▼►◄※✦✧]")
ERRATIC_CJK_SPACE_RE = re.compile(r"[\u4e00-\u9fff][ \t]+[\u4e00-\u9fff]")
VALID_CHAPTER_END_RE = re.compile(r"[。！？!?…”」』’\"》）\)]$")
CHRONICLE_OPENER_RE = re.compile(r"^(?:接着|然后|后来|随后|紧接着|最后)(?:[，,]|[\u4e00-\u9fff])")
OPENING_WEATHER_CLICHE_RE = re.compile(
    r"清晨的阳光透过|阳光洒在|第一缕阳光|微风拂过|鸟儿叽叽喳喳|从睡梦中醒来|晨光熹微|夜幕降临[，,]华灯初上"
)
ENDING_PREACHING_RE = re.compile(
    r"强者之路注定|弱肉强食的世界|命运的磨砺|力量才是唯一的真理|成长意味着必须舍弃|命运的齿轮|这才是真正的强者|世界从来都是如此残酷"
)
SUBJECTLESS_RANG_RE = re.compile(r"(?:望着|看着|听着|想到|面对)[^。！？；\n]{4,35}让")
PRONOUN_RE = re.compile(r"(?<![其吉他无利排])[他她](?:们|的)?(?![人乡国日处])")
ACTOR_CUE_RE = re.compile(
    r"对方|黑衣人|男人|女人|那人|少年|老者|对手|前任|丈夫|妻子|婆婆|闺蜜|主管|老板|经理|医生|律师|两人|二人"
)
OPENING_TENSION_RE = re.compile(
    r"[！？!?]|摔[碎烂倒在出]|砸[碎烂向在]|扇[了巴耳]|甩开|扯[断下住开]|撕[碎裂毁]|踹[开倒翻]|推[倒开翻搡]|"
    r"鲜血|流血|血迹|死亡|死了|杀[人了死意]|跪[下在地]|离婚|退婚|辞职|倒计时|规则|系统|绑定|遗书|警报|尸体|欠债|出轨|退学|解约|法庭|赔偿|耳光|巴掌|刀锋|枪声|爆炸|举报|开除"
)

# Minimal, unambiguous true LLM autopilot defects (narration only; NEVER ban ordinary Chinese words)
AI_CONTRAST_NOT_BUT_RE = re.compile(r"不是[^，。！？；\n]{1,30}[，,]?\s*而是")
RIGID_NOT_IS_RE = re.compile(r"不是[^，。！？；\n]{1,20}[，,]\s*是(?![的了呢啊吗吧嘛])[^，。！？；\n]{1,25}")
RIGID_IS_IS_RE = re.compile(r"(?:^|[，。！？；\s])是[^，。！？；\n]{1,12}[，,]\s*是(?![的了呢啊吗吧嘛])[^，。！？；\n]{1,12}")

NARRATION_DEFECTS: list[tuple[str, re.Pattern[str], str]] = [
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
        re.compile(r"在(?:这个|那片|这座)[^，。！？；\n]{2,20}的(?:时代|世界|大陆|社会|年代)里"),
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

# Scoped to narration ONLY (outside spoken dialogue) so character speech is never falsely policed
GLOBAL_CLICHES: list[tuple[str, re.Pattern[str], str]] = [
    (
        "cliche_smirk_arc",
        re.compile(r"嘴角(?:勾起|扬起|扯出)(?:一抹|一丝)?[^，。！？\n]{0,8}弧度"),
        "工业神态废料「嘴角勾起弧度」，建议换成本篇角色自然的神情或二次动作。",
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
    (
        "cliche_knuckles_white",
        re.compile(
            r"(?:骨节|指节)(?:微微|猛地|骤然|死死)?(?:发白|泛白)"
            r"|指甲(?:深深|死死)?(?:嵌进|掐进|陷进)(?:掌心|肉里)"
        ),
        "工业疼痛废料「骨节/指节发白、指甲嵌进掌心」，建议换为带生活感与温度差的微动作。",
    ),
]

# Narrowed official/legal document title regex (does not false-flag normal books, movies, or skill names)
LONG_DOC_TITLE_RE = re.compile(
    r"《[^》\n]{8,}(?:声明|协议|合同|通知|裁定|委托书|承诺书|保证书|意见书|报告|办法|条例|规定|清单|明细|确认单|回执)》"
)
BUREAUCRATIC_TERM_RE = re.compile(
    r"公证处?|公证员|存证|电子回执|回执|政务专线|实名专线|备案|核验|专网|"
    r"追踪信标|物联网|镜像备份|加密硬盘|联合签章|签字权|终验|单方撤销|"
    r"协议书|声明书|确认单|确认书|意向书|委托书|裁定书|保全裁定|划扣|"
    r"查封|冻结名单|时间戳|哈希校验|工商变更|预审编号|前置关联"
)

# Helper sets for low-false-positive 2-char Chinese name typo-drift checking
NON_NAME_SECOND_CHARS = set(
    "的了是在有不和就都而及与着过到去来中里上下前后内外间边旁处面手眼头心口声气"
    "道说看听走坐站笑哭问回拿打给把被让向往从对跟替比按像如这那哪每各"
    "一二三四五六七八九十百千多小大高长老新好坏真假"
    "荫立业场子儿们家室楼路街道村镇市省国年天日夜月时分秒"
    "旧述续白纸黑红蓝绿黄青紫灰暗明清亮冷热温凉"
)
COMPOUND_PREFIX_CHARS = set("树森竹山密丛园桂松柏椰杏桃梅复江紫四每大着明黑坦表苍洁")
NAME_BEFORE_CUES = set(
    "，。！？；：、（）「」『』“”\"' \t的着了见与但可却便就才只正刚又再也都还已曾竟"
    "对向看盯喊叫问把被给替跟和让连找等是名冲朝离帮拉推扶拦救骗怕恨爱信"
)
NAME_AFTER_CUES = set(
    "，。！？；：、”」』\"' 的说道笑问看盯点摇转抬低皱冷轻伸拉推走跑站坐蹲跪倒愣顿叹咬眯瞥"
    "嘴手眼眉脸心声身头肩背微猛忽却也没不一才正刚又再还已突直慢立沉开自本早曾竟只便就并仍将要把被给向对跟和与从替帮冲朝挥握捏抓拍敲按抱扶靠停回进出"
)
TABLE_HEADER_WORDS = {
    "角色", "姓名", "名字", "人物", "定位", "主角", "核心对手", "反派", "配角", "官配",
    "编号", "线索", "节拍", "单元", "状态", "阶段", "名称", "说明", "备注",
}

BASE_NOTICE_TEXT = (
    "本报告为网感分布与番茄投稿前自查诊断镜子（纯 ADVISORY，不设单段硬笼子），"
    "有意为之的长段蓄势、毒舌独白、规则清单或短信/弹幕块请直接保留。"
    "平台上传字数硬限（如七猫单章 500–1500 字、标题 ≤18 字）默认关闭，仅在显式传入 --platform qimao 或上下限参数时开启。"
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
        if NON_SPEECH_SHORT_QUOTE_RE.match(tok):
            before = para[: m.start()].rstrip()
            after = para[m.end() :].lstrip()
            if NON_SPEECH_AFTER_RE.match(after):
                continue
            is_speech_ctx = (
                m.start() == 0
                or before.endswith(("：", ":", "，", ","))
                or bool(BARE_DIALOGUE_RE.match(para))
                or bool(re.match(r"^[。！？!?]?[，,]?\s*(?:他|她|我|对方|[\u4e00-\u9fff]{1,3})(?:冷声|轻声|低声|沉声|淡淡)?(?:道|说|问|喊|回|笑|骂|吐出)", after))
            )
            if not is_speech_ctx:
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


def parse_names_arg(raw_names: str) -> list[str]:
    names: list[str] = []
    for part in re.split(r"[,，、;；\s]+", raw_names.strip()):
        clean = part.strip()
        if 2 <= len(clean) <= 4 and all("\u4e00" <= ch <= "\u9fff" for ch in clean):
            if clean not in names:
                names.append(clean)
    return names


def load_names_from_char_card(card_path: Path) -> list[str]:
    text = card_path.read_text(encoding="utf-8-sig", errors="replace")
    names: list[str] = []
    in_char_section = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.match(r"^#{1,6}\s+", line):
            in_char_section = any(k in line for k in ("人物", "角色", "主角", "对手", "配角"))
            continue

        # Parse markdown table rows inside character sections or rows explicitly tagging 主角/对手/反派/盟友/配角
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2 and not all(set(c) <= set("-: ") for c in cells):
                first_cell = re.sub(r"\*\*|__|`|（[^）]*）|\([^)]*\)", "", cells[0]).strip()
                second_cell = cells[1]
                is_role_row = in_char_section or any(
                    k in second_cell for k in ("主角", "对手", "反派", "官配", "盟友", "配角")
                )
                if (
                    is_role_row
                    and first_cell not in TABLE_HEADER_WORDS
                    and 2 <= len(first_cell) <= 4
                    and all("\u4e00" <= ch <= "\u9fff" for ch in first_cell)
                ):
                    if first_cell not in names:
                        names.append(first_cell)
            continue

        # Parse bullet lines like "- 主角名：林枫" or "- 主角：林枫（...）"
        m = re.match(r"^[-*]\s*\*{0,2}(?:主角名?|核心对手|反派|官配|关键盟友|配角)\*{0,2}\s*[：:]\s*(.+)$", line)
        if m:
            val = re.sub(r"（[^）]*）|\([^)]*\)|\*\*|__", "", m.group(1)).strip()
            for part in re.split(r"[,，、/／\s]+", val):
                tok = part.strip()
                if (
                    tok not in TABLE_HEADER_WORDS
                    and 2 <= len(tok) <= 4
                    and all("\u4e00" <= ch <= "\u9fff" for ch in tok)
                    and tok not in names
                ):
                    names.append(tok)
    return names


def is_panel_or_rule_line(para: str, narrative: str) -> bool:
    if PANEL_OR_STAT_LINE_RE.match(para):
        return True
    if narrative == "rules" and RULE_LIST_LINE_RE.match(para):
        return True
    if SPEC_KV_LINE_RE.match(para) and len(para) <= 45:
        return True
    return False


def has_sms_or_crowd_context(para_records: list[tuple[int, int, bool, bool, str, str]], start_idx: int, end_idx: int) -> bool:
    ctx_start = max(0, start_idx - 2)
    for j in range(ctx_start, min(len(para_records), end_idx + 1)):
        if SMS_DANMAKU_CROWD_RE.search(para_records[j][4]):
            return True
    return False


def detect_character_name_drift(
    para_records: list[tuple[int, int, bool, bool, str, str]],
    known_names: list[str],
) -> list[Advisory]:
    if not known_names:
        return []
    full_text = "\n".join(rec[4] for rec in para_records)
    known_set = set(known_names)
    known_counts = {name: full_text.count(name) for name in known_names}

    drift_hits: dict[tuple[str, str], list[int]] = {}
    for known in known_names:
        if len(known) not in (2, 3):
            continue
        surname = known[0]
        name_len = len(known)
        pat = re.compile(re.escape(surname) + r"[\u4e00-\u9fff]{" + str(name_len - 1) + r"}")

        for line_no, _, _, _, para, _ in para_records:
            for m in pat.finditer(para):
                cand = m.group(0)
                if cand in known_set:
                    continue
                # Skip if cand is a prefix of a longer known name at this position
                if any(
                    k.startswith(cand) and para[m.start() : m.start() + len(k)] == k
                    for k in known_set
                    if len(k) > len(cand)
                ):
                    continue

                if name_len == 3:
                    # Exactly 1 character differs after matching surname
                    diff = sum(1 for a, b in zip(known[1:], cand[1:]) if a != b)
                    if diff != 1:
                        continue
                else:
                    # 2-char name: guard tightly against ordinary lexical compounds
                    second = cand[1]
                    if second in NON_NAME_SECOND_CHARS:
                        continue
                    before_ch = para[m.start() - 1] if m.start() > 0 else " "
                    after_ch = para[m.end()] if m.end() < len(para) else " "
                    if before_ch in COMPOUND_PREFIX_CHARS:
                        continue
                    # Require clear name boundary cues on both sides to prevent false-positive lexical splits
                    if not (before_ch in NAME_BEFORE_CUES and after_ch in NAME_AFTER_CUES):
                        continue

                drift_hits.setdefault((known, cand), []).append(line_no)

    advisories: list[Advisory] = []
    for (known, cand), hit_lines in drift_hits.items():
        # Flag low-frequency slips (fewer occurrences than known name, or 1–3 rare occurrences)
        k_cnt = known_counts.get(known, 0)
        if k_cnt > 0 and len(hit_lines) > max(3, k_cnt):
            continue
        if k_cnt == 0 and len(hit_lines) > 3:
            continue
        advisories.append(
            Advisory(
                "character_name_typo_drift",
                hit_lines[0],
                f"疑似人名拼写漂移：「{cand}」（出现 {len(hit_lines)} 次，与已知角色「{known}」仅差一字）",
                f"请核对第 {hit_lines[0]} 行是否为「{known}」的误写（番茄发稿前必查人名一致性）。",
            )
        )
    return advisories


def analyze_file(
    path: Path,
    narrative: str = "dialogue",
    first_chapter: bool = False,
    target_words: int | None = None,
    tolerance: float = 0.20,
    min_raw_chars: int | None = None,
    max_raw_chars: int | None = None,
    platform: str = "none",
    known_names: list[str] | None = None,
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

    body_joined = "\n".join(s for _, s in body_lines)
    non_ws_chars = len(re.sub(r"\s+", "", body_joined))
    raw_chars = len(body_joined)

    total_cjk = 0
    dialogue_cjk = 0
    para_lengths: list[int] = []
    # (line_no, para_cjk, has_dialogue, is_bare_dialogue, para_text, narration_text)
    para_records: list[tuple[int, int, bool, bool, str, str]] = []
    long_speeches = 0
    double_quote_spans = 0
    corner_quote_spans = 0
    long_doc_titles: list[tuple[int, str]] = []
    bureaucratic_terms: list[tuple[int, str]] = []

    not_but_hits: list[tuple[int, str]] = []
    rigid_variant_hits: list[tuple[int, str]] = []
    dash_total = 0
    dash_para_hits: list[tuple[int, int]] = []
    ascii_punct_hits: list[tuple[int, str]] = []
    decorative_sym_hits: list[tuple[int, str]] = []
    erratic_space_hits: list[tuple[int, str]] = []
    broken_wrap_lines: list[tuple[int, str]] = []
    chronicle_openers: list[tuple[int, str]] = []
    subjectless_hits: list[tuple[int, str]] = []
    pronoun_confusion_hits: list[tuple[int, str]] = []

    known_name_list = known_names or []

    for line_no, para in body_lines:
        p_cjk = len(CJK_RE.findall(para))
        if p_cjk == 0:
            continue
        total_cjk += p_cjk
        para_lengths.append(p_cjk)

        for m in LONG_DOC_TITLE_RE.finditer(para):
            long_doc_titles.append((line_no, m.group(0)))
        for m in BUREAUCRATIC_TERM_RE.finditer(para):
            bureaucratic_terms.append((line_no, m.group(0)))

        spoken_spans = extract_spoken_spans(para)
        for sp in spoken_spans:
            if sp.startswith("“"):
                double_quote_spans += 1
            elif sp.startswith(("「", "『")):
                corner_quote_spans += 1
        d_cjk = sum(len(CJK_RE.findall(sp)) for sp in spoken_spans)
        dialogue_cjk += d_cjk
        has_dialogue = d_cjk > 0
        is_bare = bool(BARE_DIALOGUE_RE.match(para))
        narration = strip_spoken_spans(para, spoken_spans)
        para_records.append((line_no, p_cjk, has_dialogue, is_bare, para, narration))

        # Check single-turn lecture speech ("评审会演讲腔")
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

        # Minimal true LLM autopilot defects & clichés (ALL scoped to narration outside spoken dialogue)
        for m in AI_CONTRAST_NOT_BUT_RE.finditer(narration):
            not_but_hits.append((line_no, m.group(0)))
        narration_wo_not_but = AI_CONTRAST_NOT_BUT_RE.sub(" ", narration)
        for m in RIGID_NOT_IS_RE.finditer(narration_wo_not_but):
            rigid_variant_hits.append((line_no, m.group(0).strip()))
        for m in RIGID_IS_IS_RE.finditer(narration_wo_not_but):
            rigid_variant_hits.append((line_no, m.group(0).strip("，。！？； ")))

        for code, pattern, msg in NARRATION_DEFECTS:
            for m in pattern.finditer(narration):
                advisories.append(Advisory(code, line_no, m.group(0), msg))
        for code, pattern, msg in GLOBAL_CLICHES:
            for m in pattern.finditer(narration):
                advisories.append(Advisory(code, line_no, m.group(0), msg))

        # Dash overuse count
        d_cnt = para.count("——")
        if d_cnt > 0:
            dash_total += d_cnt
            if d_cnt >= 3:
                dash_para_hits.append((line_no, d_cnt))

        # Punctuation / typography hygiene
        is_panel = PANEL_OR_STAT_LINE_RE.match(para) is not None
        cleaned_url = URL_RE.sub(" ", para)
        if not is_panel:
            m_ascii = ASCII_PUNCT_NEAR_CJK_RE.search(cleaned_url)
            if m_ascii:
                ascii_punct_hits.append((line_no, m_ascii.group(0)))
            if not para.startswith("|"):
                m_space = ERRATIC_CJK_SPACE_RE.search(cleaned_url)
                if m_space:
                    erratic_space_hits.append((line_no, m_space.group(0)))
        m_dec = DECORATIVE_SYM_RE.search(para)
        if m_dec:
            decorative_sym_hits.append((line_no, m_dec.group(0)))

        # Broken line wrap (paragraph ends with trailing comma / enumeration comma)
        if not is_panel and para.endswith(("，", "、", ",")):
            broken_wrap_lines.append((line_no, para[-18:]))

        # Chronicle filler openers (流水账)
        if (not has_dialogue) and CHRONICLE_OPENER_RE.match(para):
            chronicle_openers.append((line_no, para[:18]))

        # Subjectless run-on narration sentences
        for sent in re.split(r"[。！？；]+", narration):
            s_cjk = len(CJK_RE.findall(sent))
            if s_cjk > 65:
                subjectless_hits.append((line_no, sent.strip()[:40] + "..."))
            elif s_cjk > 45 and SUBJECTLESS_RANG_RE.search(sent):
                subjectless_hits.append((line_no, sent.strip()[:40] + "..."))

        # Local single-paragraph pronoun confusion (replaces noisy global pronoun density)
        if p_cjk <= 120 and narration.strip():
            prons = PRONOUN_RE.findall(narration)
            he_cnt = sum(1 for pr in prons if pr.startswith("他"))
            she_cnt = sum(1 for pr in prons if pr.startswith("她"))
            max_same = max(he_cnt, she_cnt)
            distinct_known_here = sum(1 for nm in known_name_list if nm in para)
            has_actor_cue = bool(ACTOR_CUE_RE.search(para))
            if (max_same >= 4 and (distinct_known_here >= 2 or has_actor_cue)) or max_same >= 5:
                pronoun_confusion_hits.append((line_no, para[:42] + ("..." if len(para) > 42 else "")))

    # Emit ai_contrast_not_but (lenient in first_person: only when >=2 times in one chapter)
    if (narrative != "first_person" and not_but_hits) or (narrative == "first_person" and len(not_but_hits) >= 2):
        for ln, ex in not_but_hits:
            advisories.append(
                Advisory(
                    "ai_contrast_not_but",
                    ln,
                    ex,
                    "旁白二元说教句式「不是……而是……」，建议删去否定前半句直接写事实。",
                )
            )

    # Emit rigid_connector_variants (Fanqie stiff connector repeats: 不是……是 / 是……是)
    if len(rigid_variant_hits) >= 2:
        sample = " / ".join(ex for _, ex in rigid_variant_hits[:3])
        advisories.append(
            Advisory(
                "rigid_connector_variants",
                rigid_variant_hits[0][0],
                f"本章旁白出现 {len(rigid_variant_hits)} 处「不是……是 / 是……是」工整关联句（如：{sample}）",
                "句式偏工整易显 AI 文风呆板；建议打破成对模板，改为具体画面或自然错落语序。",
            )
        )

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

    # 2. Reverse-AI-ness detector: mechanical uniform choppy 'telegraph' paragraphs (exempt rules list items)
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

    for line_no, p_cjk, has_dialogue, _, para, _ in para_records:
        if narrative == "rules" and RULE_LIST_LINE_RE.match(para):
            flush_choppy(choppy_streak)
            choppy_streak = []
            continue
        if (not has_dialogue) and 12 <= p_cjk <= 38:
            choppy_streak.append((line_no, p_cjk))
        else:
            flush_choppy(choppy_streak)
            choppy_streak = []
    flush_choppy(choppy_streak)

    # 2.5 Fanqie: staircase_micro_paras (>=4 consecutive 1–10 CJK char non-dialogue/non-panel paras)
    micro_run: list[tuple[int, int]] = []
    micro_start_idx = 0

    def flush_micro(run: list[tuple[int, int]], start_i: int, end_i: int) -> None:
        if len(run) < 4:
            return
        if has_sms_or_crowd_context(para_records, start_i, end_i):
            return
        advisories.append(
            Advisory(
                "staircase_micro_paras",
                run[0][0],
                f"第 {run[0][0]}–{run[-1][0]} 行连续 {len(run)} 段 1–10 字阶梯式超短非对白碎段",
                "疑似番茄审稿高危「阶梯式假排版」；建议将同一动作/念头合并成自然语流段，仅保留真正情绪爆点单句成段。",
            )
        )

    for i, (line_no, p_cjk, has_dialogue, _, para, _) in enumerate(para_records):
        if (not has_dialogue) and (not is_panel_or_rule_line(para, narrative)) and 1 <= p_cjk <= 10:
            if not micro_run:
                micro_start_idx = i
            micro_run.append((line_no, p_cjk))
        else:
            flush_micro(micro_run, micro_start_idx, i - 1)
            micro_run = []
    flush_micro(micro_run, micro_start_idx, len(para_records) - 1)

    # 2.6 Fanqie: bare_dialogue_stack (>=5 consecutive bare short spoken dialogues <=28 CJK, exempt SMS/danmaku/crowd)
    bare_run: list[tuple[int, int]] = []
    bare_start_idx = 0

    def flush_bare(run: list[tuple[int, int]], start_i: int, end_i: int) -> None:
        if len(run) < 5:
            return
        if has_sms_or_crowd_context(para_records, start_i, end_i):
            return
        advisories.append(
            Advisory(
                "bare_dialogue_stack",
                run[0][0],
                f"第 {run[0][0]}–{run[-1][0]} 行连续 {len(run)} 句无动作/神态穿插的纯短对话（≤28字）",
                "疑似番茄「短对话堆砌」；面对面交锋最多连 2–3 句裸接，随后须穿插二次动作、神态或环境锚点（短信/弹幕/群议除外）。",
            )
        )

    for i, (line_no, p_cjk, has_dialogue, is_bare, para, _) in enumerate(para_records):
        if is_bare and has_dialogue and p_cjk <= 28:
            if not bare_run:
                bare_start_idx = i
            bare_run.append((line_no, p_cjk))
        else:
            flush_bare(bare_run, bare_start_idx, i - 1)
            bare_run = []
    flush_bare(bare_run, bare_start_idx, len(para_records) - 1)

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

    for line_no, p_cjk, has_dialogue, _, _, _ in para_records:
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
        for line_no, p_cjk, has_dialogue, _, para, _ in para_records[:2]:
            if (not has_dialogue) and p_cjk > 130:
                advisories.append(
                    Advisory(
                        "opening_exposition_wall",
                        line_no,
                        para[:50] + "...",
                        f"开篇前两段即出现 {p_cjk} 字纯旁白长段，黄金第一屏阅读门槛偏高；建议直接砸出当下冲突、台词或反常识规则。",
                    )
                )
        opening_chunks: list[str] = []
        opening_para_lens: list[int] = []
        opening_cjk = 0
        opening_has_dialogue = False
        for _, p_cjk, has_dialogue, _, para, _ in para_records:
            opening_chunks.append(para)
            opening_para_lens.append(p_cjk)
            opening_cjk += p_cjk
            if has_dialogue:
                opening_has_dialogue = True
            if opening_cjk >= 500:
                break
        opening_text = "\n".join(opening_chunks)
        opening_median = statistics.median(opening_para_lens) if opening_para_lens else 0.0
        has_punchy_short_lines = len(opening_para_lens) >= 3 and opening_median <= 45.0
        has_tension_marker = bool(OPENING_TENSION_RE.search(opening_text))
        if (
            opening_cjk >= 350
            and (not opening_has_dialogue)
            and (not has_punchy_short_lines)
            and (not has_tension_marker)
        ):
            advisories.append(
                Advisory(
                    "opening_low_energy",
                    para_records[0][0],
                    f"前 {opening_cjk} 字为平铺长说明（中位段长 {opening_median:.0f} 字，无对白且无明显冲突/动作钩子）",
                    "首章黄金 500 字入局偏平缓，建议核对是否及时抛出了奇观规则、当场危机或抓人悬念（无需硬塞感叹号）。",
                )
            )

    # 5.1 Fanqie: opening_weather_cliche (first 2 paras of any chapter)
    for line_no, _, _, _, para, _ in para_records[:2]:
        m_w = OPENING_WEATHER_CLICHE_RE.search(para)
        if m_w:
            advisories.append(
                Advisory(
                    "opening_weather_cliche",
                    line_no,
                    m_w.group(0),
                    "检测到章首天气/晨起模板开篇；建议直接切入人物动作、危机现场或承接上章钩子。",
                )
            )
            break

    # 5.2 Fanqie: ending_empty_preaching (last 4 paras narration)
    for line_no, _, _, _, _, narration in para_records[-4:]:
        m_p = ENDING_PREACHING_RE.search(narration)
        if m_p:
            advisories.append(
                Advisory(
                    "ending_empty_preaching",
                    line_no,
                    m_p.group(0),
                    "检测到章尾上帝视角哲理拔高/说教收口；建议改落在一个具体事件节点、悬念钩子或关系微变化上。",
                )
            )
            break

    # 5.3 Fanqie: dash_overuse
    dash_per_k = (dash_total / (total_cjk / 1000.0)) if total_cjk >= 300 else 0.0
    if (dash_total >= 6 and dash_per_k >= 2.5) or dash_para_hits:
        first_ln = dash_para_hits[0][0] if dash_para_hits else 1
        advisories.append(
            Advisory(
                "dash_overuse",
                first_ln,
                f"全章破折号「——」共 {dash_total} 处（{dash_per_k:.1f}/千字，单段≥3处共 {len(dash_para_hits)} 段）",
                "破折号过多易显文风断裂或翻译腔；建议多数解释与转折改用逗号、句号或拆句表达。",
            )
        )

    # 5.4 Fanqie: punctuation_typography_hygiene
    typo_parts: list[str] = []
    typo_line = 1
    if ascii_punct_hits:
        typo_line = ascii_punct_hits[0][0]
        typo_parts.append(
            f"中英文标点混用 {len(ascii_punct_hits)} 处（如第{ascii_punct_hits[0][0]}行「{ascii_punct_hits[0][1]}」）"
        )
    if decorative_sym_hits:
        if not typo_parts:
            typo_line = decorative_sym_hits[0][0]
        typo_parts.append(
            f"非常规装饰符号 {len(decorative_sym_hits)} 处（如第{decorative_sym_hits[0][0]}行「{decorative_sym_hits[0][1]}」）"
        )
    if erratic_space_hits:
        if not typo_parts:
            typo_line = erratic_space_hits[0][0]
        typo_parts.append(
            f"中文句中异常空格 {len(erratic_space_hits)} 处（如第{erratic_space_hits[0][0]}行「{erratic_space_hits[0][1]}」）"
        )
    if typo_parts:
        advisories.append(
            Advisory(
                "punctuation_typography_hygiene",
                typo_line,
                "；".join(typo_parts),
                "番茄发稿前排版体检项：请统一改为中文全角标点、清除装饰符号与中文句中误插空格。",
            )
        )

    # 5.5 Fanqie: broken_line_wrap & broken_chapter_cut
    if len(broken_wrap_lines) >= 2:
        sample_wraps = " / ".join(f"L{ln}…{ex[-6:]}" for ln, ex in broken_wrap_lines[:3])
        advisories.append(
            Advisory(
                "broken_line_wrap",
                broken_wrap_lines[0][0],
                f"{len(broken_wrap_lines)} 处段落以逗号/顿号结尾强行换行（{sample_wraps}）",
                "疑似句中误敲回车导致「乱分行」；请合并被截断的同一句子或改为完整句末标点。",
            )
        )
    if para_records:
        last_ln, _, _, _, last_para, _ = para_records[-1]
        if not VALID_CHAPTER_END_RE.search(last_para):
            advisories.append(
                Advisory(
                    "broken_chapter_cut",
                    last_ln,
                    f"章末最后一段未以完整句末标点收束：「…{last_para[-20:]}」",
                    "疑似「乱分章」或文本截断；请确认章节在完整节点（小事件收束/悬念/关系变化）处自然收尾并补全句末标点。",
                )
            )

    # 5.6 Fanqie: parallel_short_sentences (>=3 consecutive non-dialogue/non-panel sentences or paras sharing >=3 CJK prefix)
    parallel_flagged = False
    known_3char = {nm for nm in known_name_list if len(nm) == 3}
    # Check consecutive paragraphs
    prev_prefix = ""
    prefix_run: list[tuple[int, str]] = []
    prefix_start_idx = 0

    def flush_parallel(run: list[tuple[int, str]], start_i: int, end_i: int) -> None:
        nonlocal parallel_flagged
        if parallel_flagged or len(run) < 3:
            return
        if has_sms_or_crowd_context(para_records, start_i, end_i):
            return
        parallel_flagged = True
        advisories.append(
            Advisory(
                "parallel_short_sentences",
                run[0][0],
                f"第 {run[0][0]}–{run[-1][0]} 行连续 {len(run)} 处以相同前缀「{run[0][1][:3]}…」起句",
                "检测到连续同构短句排比，易显 AI 句式机械；建议错开起句结构或合并为自然长短句。",
            )
        )

    for i, (line_no, _, has_dialogue, _, para, _) in enumerate(para_records):
        if has_dialogue or is_panel_or_rule_line(para, narrative):
            flush_parallel(prefix_run, prefix_start_idx, i - 1)
            prefix_run = []
            prev_prefix = ""
            continue
        cjk_head = "".join(CJK_RE.findall(para[:8]))[:3]
        if len(cjk_head) == 3 and cjk_head not in known_3char and cjk_head == prev_prefix:
            prefix_run.append((line_no, para))
        else:
            flush_parallel(prefix_run, prefix_start_idx, i - 1)
            prev_prefix = cjk_head if (len(cjk_head) == 3 and cjk_head not in known_3char) else ""
            prefix_start_idx = i
            prefix_run = [(line_no, para)] if prev_prefix else []
    flush_parallel(prefix_run, prefix_start_idx, len(para_records) - 1)

    # Also check intra-paragraph >=3 consecutive sentences with identical >=3 CJK prefix
    if not parallel_flagged:
        for i, (line_no, _, has_dialogue, _, para, narration) in enumerate(para_records):
            if is_panel_or_rule_line(para, narrative) or has_sms_or_crowd_context(para_records, i, i):
                continue
            sents = [s.strip() for s in re.split(r"[。！？；]+", narration) if len(CJK_RE.findall(s)) >= 5]
            if len(sents) < 3:
                continue
            streak = 1
            last_p = ""
            for s in sents:
                hd = "".join(CJK_RE.findall(s[:8]))[:3]
                if len(hd) == 3 and hd not in known_3char and hd == last_p:
                    streak += 1
                    if streak >= 3:
                        parallel_flagged = True
                        advisories.append(
                            Advisory(
                                "parallel_short_sentences",
                                line_no,
                                f"段内连续 {streak} 句均以「{hd}…」起句",
                                "检测到段内连续同构短句排比，易显文风呆板；建议调整句式起伏。",
                            )
                        )
                        break
                else:
                    last_p = hd if (len(hd) == 3 and hd not in known_3char) else ""
                    streak = 1
            if parallel_flagged:
                break

    # 5.7 Fanqie: chronicle_filler_openers (>=3 in a chapter)
    if len(chronicle_openers) >= 3:
        sample = " / ".join(f"L{ln}「{ex[:6]}」" for ln, ex in chronicle_openers[:4])
        advisories.append(
            Advisory(
                "chronicle_filler_openers",
                chronicle_openers[0][0],
                f"本章出现 {len(chronicle_openers)} 段以「接着/然后/后来/随后/最后」开头的流水账过渡（{sample}）",
                "频繁使用时间过渡词易显流水账；建议直接切入下一动作或情绪反应，删去无意义衔接词。",
            )
        )

    # 5.8 Fanqie: structured_spec_list_dump (>=5 consecutive short key:value lines outside system panels & rules mode)
    if narrative != "rules":
        kv_run: list[tuple[int, str]] = []
        kv_start_idx = 0

        def flush_kv(run: list[tuple[int, str]], start_i: int) -> None:
            if len(run) < 5:
                return
            ctx_start = max(0, start_i - 2)
            for j in range(ctx_start, start_i):
                if PANEL_HEADER_CONTEXT_RE.search(para_records[j][4]):
                    return
            if PANEL_HEADER_CONTEXT_RE.search(para_records[start_i][4]):
                return
            advisories.append(
                Advisory(
                    "structured_spec_list_dump",
                    run[0][0],
                    f"第 {run[0][0]}–{run[-1][0]} 行连续 {len(run)} 行工整「键：值」清单式罗列",
                    "疑似大段参数/方案说明书式罗列；若非系统面板或任务弹窗，建议拆散融进人物动作与现场观察中。",
                )
            )

        for i, (line_no, _, has_dialogue, _, para, _) in enumerate(para_records):
            if (not has_dialogue) and len(para) <= 45 and SPEC_KV_LINE_RE.match(para) and not PANEL_OR_STAT_LINE_RE.match(para):
                if not kv_run:
                    kv_start_idx = i
                kv_run.append((line_no, para))
            else:
                flush_kv(kv_run, kv_start_idx)
                kv_run = []
        flush_kv(kv_run, kv_start_idx)

    # 5.9 Fanqie: subjectless_run_on & pronoun_confusion_local
    for ln, ex in subjectless_hits[:3]:
        advisories.append(
            Advisory(
                "subjectless_run_on",
                ln,
                ex,
                "检测到超长旁白句或「望着/看着……让……」缺主语长难句；建议在动作/主语切换处断句，保持主语清晰。",
            )
        )
    for ln, ex in pronoun_confusion_hits[:3]:
        advisories.append(
            Advisory(
                "pronoun_confusion_local",
                ln,
                ex,
                "单段内高频出现同一第三人称代词且涉及多人交互，易导致指代模糊；多人同场请直呼姓名或身份标签。",
            )
        )

    # 5.10 Optional character_name_typo_drift (--names / --char-card)
    if known_name_list:
        advisories.extend(detect_character_name_drift(para_records, known_name_list))

    # 5.11 Mixed / platform quote style check (supports “”, 「」, 『』)
    if double_quote_spans > 0 and corner_quote_spans > 0:
        advisories.append(
            Advisory(
                "mixed_quote_styles",
                1,
                f"同章混用了 “” ({double_quote_spans} 处) 与 「」/『』 ({corner_quote_spans} 处) 对话引号",
                "请全篇统一对话引号格式：知乎盐言统一用直角引号「」（嵌套用『』），其他平台默认用全角双引号“”。",
            )
        )
    elif platform == "zhihu" and double_quote_spans > 0 and corner_quote_spans == 0:
        advisories.append(
            Advisory(
                "zhihu_quote_style_mismatch",
                1,
                f"目标平台为知乎盐言，但本章 {double_quote_spans} 处对话使用了全角双引号 “” 而非直角引号 「」",
                "知乎盐言建议全篇对话统一改用直角引号「」（引号内嵌套用『』）。",
            )
        )

    # 5.12 Bureaucratic / legal-checklist prose density check (refined threshold & narrowed doc title suffixes)
    bureau_per_k = (len(bureaucratic_terms) / (total_cjk / 1000.0)) if total_cjk >= 400 else 0.0
    if (
        len(long_doc_titles) >= 3
        or (len(long_doc_titles) >= 2 and (len(long_doc_titles) * 2 + len(bureaucratic_terms)) >= 10)
        or (total_cjk >= 400 and len(bureaucratic_terms) >= 12 and bureau_per_k >= 9.0)
    ):
        sample_docs = "、".join(dict.fromkeys(tok for _, tok in long_doc_titles[:3]))
        sample_terms = "、".join(dict.fromkeys(tok for _, tok in bureaucratic_terms[:5]))
        first_hit_line = (
            long_doc_titles[0][0]
            if long_doc_titles
            else (bureaucratic_terms[0][0] if bureaucratic_terms else 1)
        )
        advisories.append(
            Advisory(
                "bureaucratic_jargon_density",
                first_hit_line,
                f"超长公文书名号 {len(long_doc_titles)} 处（{sample_docs or '无'}），程序/公文词 {len(bureaucratic_terms)} 处（{sample_terms}，{bureau_per_k:.1f}/千字）",
                "检测到较密集的公文/法务办件说明书腔，易吸干情绪感染力；建议把超长文件名口语化简称、压缩手续描写，把笔墨还给角色当面交锋。",
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

    # 7. Strictly OPT-IN platform upload character limit check (BOTH min & max use unified non_ws_chars!)
    if min_raw_chars and non_ws_chars < min_raw_chars:
        advisories.append(
            Advisory(
                "platform_chapter_length_limit",
                1,
                f"当前单章非空白字符 {non_ws_chars}（净汉字 {total_cjk}）< 平台上传下限 {min_raw_chars}",
                "已显式开启平台上传字数硬限核验：当前章节低于平台最低字数要求，可合并相邻短节或充实当下现场交锋。",
            )
        )
    if max_raw_chars and non_ws_chars > max_raw_chars:
        advisories.append(
            Advisory(
                "platform_chapter_length_limit",
                1,
                f"当前单章非空白字符 {non_ws_chars}（净汉字 {total_cjk}）> 平台上传上限 {max_raw_chars}",
                "已显式开启平台上传字数硬限核验：当前章节超出平台单章上限，建议在自然悬念处拆章或微精简。",
            )
        )

    metrics: dict[str, Any] = {
        "narrative": narrative,
        "platform": platform,
        "cjk_chars": total_cjk,
        "non_ws_chars": non_ws_chars,
        "raw_chars": raw_chars,
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
        "dash_count": dash_total,
        "long_doc_titles": len(long_doc_titles),
        "bureaucratic_terms": len(bureaucratic_terms),
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


def build_notice(platform: str) -> str:
    if platform == "fanqie":
        return (
            BASE_NOTICE_TEXT
            + " 【已启用番茄投稿前专项体检模式】：重点关注裸短对话堆砌、阶梯碎段、破折号/标点排版卫生、乱分行/乱分章与工整模板句（不设人为单章字数硬限）。"
        )
    if platform == "zhihu":
        return (
            BASE_NOTICE_TEXT
            + " 【已启用知乎盐言模式】：同步核验全篇是否统一使用直角引号「」（嵌套用『』）。"
        )
    if platform == "qimao":
        return (
            BASE_NOTICE_TEXT
            + " 【已显式开启七猫上传硬限模式】：按非空白字符核验单章 500–1500 字及书名 ≤18 字。"
        )
    return BASE_NOTICE_TEXT


def main() -> int:
    parser = argparse.ArgumentParser(
        description="网文短篇分布与番茄投稿前体检镜子：检测段长分布、连闷段、百字演讲腔、短对话堆砌、阶梯碎段、标点排版与极简 AI 废料（纯 ADVISORY，非硬考题）。"
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
        help="单文件模式显式启用首章黄金 500 字检查（--dir 模式仅自动对首章 idx==0 启用）",
    )
    parser.add_argument("--target-words", type=int, default=0, help="可选单章参考汉字数")
    parser.add_argument("--tolerance", type=float, default=0.20, help="允许偏差比例（默认 0.20）")
    parser.add_argument(
        "--platform",
        choices=("none", "qimao", "fanqie", "zhihu"),
        default="none",
        help="平台模式：none（默认不启字数硬限）、qimao（核验单章 500–1500 非空白字符与标题 ≤18 字）、fanqie（番茄投稿前体检强调，不卡字数）、zhihu（核验知乎盐言「」引号）",
    )
    parser.add_argument("--min-raw-chars", type=int, default=0, help="按需开启的单章非空白字符下限（默认 0 不开启）")
    parser.add_argument("--max-raw-chars", type=int, default=0, help="按需开启的单章非空白字符上限（默认 0 不开启）")
    parser.add_argument("--check-title", default="", help="按需开启的标题字数核验（配合 --platform qimao 检查是否 ≤18 字）")
    parser.add_argument("--names", default="", help="可选已知核心人物名（逗号分隔，如「林枫,苏婉」），启用一字之差拼写漂移检查")
    parser.add_argument("--char-card", type=Path, default=None, help="可选人物卡或 00_脑洞与节拍.md 路径，自动提取核心人物名做拼写漂移检查")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    if args.target_words < 0:
        parser.error("--target-words 不能为负数。")
    if not 0.0 <= args.tolerance <= 1.0:
        parser.error("--tolerance 必须在 0 到 1 之间。")
    if args.min_raw_chars < 0 or args.max_raw_chars < 0:
        parser.error("--min-raw-chars 和 --max-raw-chars 不能为负数。")

    known_names = parse_names_arg(args.names)
    if args.char_card is not None:
        cc_path = args.char_card.expanduser().resolve()
        if not cc_path.is_file():
            print(f"ERROR: Character card file not found: {cc_path}", file=sys.stderr)
            return 2
        for nm in load_names_from_char_card(cc_path):
            if nm not in known_names:
                known_names.append(nm)

    eff_min_raw = args.min_raw_chars or (500 if args.platform == "qimao" else 0)
    eff_max_raw = args.max_raw_chars or (1500 if args.platform == "qimao" else 0)

    title_advisories: list[dict[str, Any]] = []
    if args.check_title.strip():
        t = args.check_title.strip()
        if args.platform == "qimao" and len(t) > 18:
            title_advisories.append(
                asdict(
                    Advisory(
                        "platform_title_length_limit",
                        0,
                        f"书名《{t}》共 {len(t)} 字（含标点/字母），超出七猫 ≤18 字上传上限",
                        "请将标题精简至 ≤18 字（建议 ≤17 字留安全余量，含标点与字母）。",
                    )
                )
            )

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
        # In --dir mode, ONLY apply first_chapter=True to idx == 0 (never every chapter!)
        for idx, fp in enumerate(files):
            targets.append((fp, idx == 0))

    notice_text = build_notice(args.platform)
    results: list[dict[str, Any]] = []
    total_cjk_all = 0
    for fp, is_first in targets:
        advs, metrics = analyze_file(
            fp,
            narrative=args.narrative,
            first_chapter=is_first,
            target_words=args.target_words or None,
            tolerance=args.tolerance,
            min_raw_chars=eff_min_raw or None,
            max_raw_chars=eff_max_raw or None,
            platform=args.platform,
            known_names=known_names,
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
            "notice": notice_text,
            "platform_limit_check": args.platform,
            "known_names_checked": known_names,
            "files_scanned": len(results),
            "total_cjk_chars": total_cjk_all,
            "title_advisories": title_advisories,
            "results": results,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(notice_text)
        if title_advisories:
            for adv in title_advisories:
                print(f"[TITLE ADVISORY] ({adv['code']}): 「{adv['excerpt']}」 -> {adv['suggestion']}")
        if len(results) > 1:
            print(f"scanned={len(results)} total_cjk_chars={total_cjk_all}")
        for item in results:
            m = item["metrics"]
            print(f"\nfile={item['file']}")
            print(
                "metrics "
                f"narrative={m['narrative']} platform={m['platform']} cjk={m['cjk_chars']} non_ws={m['non_ws_chars']} raw={m['raw_chars']} "
                f"paras={m['paragraphs']} median_para={m['median_para_cjk']} mean_para={m['mean_para_cjk']} p90={m['p90_para_cjk']} "
                f"short<=55={m['short_para_ratio_le55']*100:.1f}% heavy>95={m['heavy_para_ratio_gt95']*100:.1f}% "
                f"dialogue={m['dialogue_ratio']*100:.1f}% walls={m['narration_wall_streaks']} "
                f"long_speeches={m['long_speech_monologues']} dashes={m['dash_count']} "
                f"docs={m['long_doc_titles']} bureau={m['bureaucratic_terms']} advisories={m['advisories']}"
            )
            for adv in item["advisories"]:
                print(
                    f"  [ADVISORY] line {adv['line']} ({adv['code']}): "
                    f"「{adv['excerpt']}」 -> {adv['suggestion']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
