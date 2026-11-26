#!/usr/bin/env python3
"""Initialize a lightweight short-webnovel project (2 core workspace files + clean dirs)."""

from __future__ import annotations

import argparse
from pathlib import Path


MODE_META: dict[str, tuple[str, str, str]] = {
    "flash": (
        "超短篇（知乎盐言 / 番茄短故事 / 强反转爆文）",
        "8,000 - 30,000 字（单篇分节或 4–12 章，单章约 1500–2500 字；明确上传七猫时再按需拆分 500–1500 字/章）",
        """| 节拍 | 进度 / 预计字数 | 冲突与现场戏眼（禁纯筹备章） | 当下情绪刺点 / 活人微感官细节 | 爽感维度（相邻需切换/叠加） | 明牌线索（埋 / 收） | 章末钩子 |
|---|---|---|---|---|---|---|
| 01 黄金入局 | 0%–5%（前300–500字） | 零前情提要，直接砸出反常规则、当下危机或强烈处境反差 |  |  | 埋： |  |
| 02 首次验证 / 小钩子 | 5%–15%（前1500字内） | 亲眼见证规则生效或给出第一次当场小反击/强悬念，兑现点击承诺 |  |  | 埋/收： |  |
| 03 递进爽点 | 15%–45% | 对手按常规认知加码试探/打压，主角用维度 A 反杀并拿到第一份筹码 |  |  | 埋/收： |  |
| 04 假危机 + 中反转 | 45%–70% | 对手亮杀手锏看似逆转，主角切入维度 B（规则漏洞/伏笔回收）反将一军 |  |  | 埋/收： |  |
| 05 终局大掀桌 | 70%–92% | 全场筹码摊牌，回收开头最核心明牌伏笔，完成最高强度情绪释放 |  |  | 收： |  |
| 06 短促落点 / 回马枪 | 92%–100%（300–800字） | 干脆落定新局面、冷幽默或细思极恐回马枪，绝不拖泥带水总结 |  |  | — |  |""",
    ),
    "microdrama": (
        "微短剧式短中篇（10–25 章 · 章章强卡点）",
        "20,000 - 50,000 字（10–25 章，单章约 1600–2400 字；明确上传七猫时再按需拆分 500–1500 字/章）",
        """| 单元 / 章节 | 预计字数 | 本单元核心赌局与情绪落差（禁纯筹备章） | 当下情绪刺点 / 关系张力推进 | 主打爽感维度（每单元须切换/叠加） | 明牌线索（埋 / 收） | 关键章末钩子 |
|---|---|---|---|---|---|---|
| 开篇钩子（第1–2章） | 约 3200–4500 字 | 第1章前500字入局+章末硬悬念；第2章首次痛快小兑现+拉出更大赌局 |  |  | 埋： |  |
| 循环一（第3–6章） | 约 6500–9500 字 | 首个压迫→交锋→反杀循环，同步推进核心关系试探与反差 |  |  | 埋/收： |  |
| 循环二（第7–11章） | 约 8000–12000 字 | 危机升级与卡点爆破，切换爽感维度并拉出后半程新主线 |  |  | 埋/收： |  |
| 循环三（第12–22章，按篇幅伸缩） | 约 8000–18000 字 | 借刀反噬或情感掀桌，反派内讧裂变，严禁车轱辘水戏 |  |  | 埋/收： |  |
| 终局清算（最后2–3章） | 约 3500–6500 字 | 汇合全部明牌线索与筹码，彻底清算并留利落余韵收官 |  |  | 收： |  |""",
    ),
}

NARRATIVE_LABELS: dict[str, str] = {
    "dialogue": "dialogue（强对话交锋型：短促台词交锋 + 动作神态锚点为主引擎）",
    "first_person": "first_person（第一人称强叙述吐槽型：极强主观口吻 + 犀利短评 + 关键台词爆点）",
    "rules": "rules（规则/悬疑信息流型：冷峻观察 + 反常细节 + 规则条目与短句破绽反差）",
}

PLATFORM_META: dict[str, tuple[str, str, str]] = {
    "general": ("通用 / 多平台短篇", "“” 全角双引号", "150–250 字电影预告片式导语（核心高概念 + 爽点预览 + 悬念钩子）"),
    "fanqie": ("番茄短故事 / 番茄短中篇", "“” 全角双引号", "120–260 字冲突前置导语（奇观处境 → 狠话/压迫 → 反杀预告与钩子）"),
    "zhihu": ("知乎盐言故事", "「」 直角引号（嵌套用『』，严禁与“”混用）", "200–500 字独立微小说导语（人物关系 + 核心冲突 + 2–3转折 + 金句/强悬念收口）"),
    "qimao": ("七猫短故事", "“” 全角双引号", "建议 120–300 字，平台上限 ≤500 字（强情绪冲突前置，可含 1 句高张力台词）"),
    "dianzhong": ("点众短篇", "“” 全角双引号", "150–300 字高密度导语（浓缩前1/3核心冲突、信任陷阱与反击暗示）"),
    "heiyan": ("黑岩短篇", "“” 全角双引号", "120–300 字极端冲击导语（公开羞辱/控诉/倒计时 + 隐藏底牌亮刃）"),
}


def safe_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if root.parent == root:
        raise ValueError("Refusing to initialize a filesystem root.")
    return root


def build_templates(
    title: str,
    mode: str,
    narrative: str,
    platform: str,
    quote_style: str,
    target_words: str,
    source_brief: str,
) -> dict[str, str]:
    mode_label, default_words, beat_table = MODE_META[mode]
    words_display = target_words.strip() or default_words
    narrative_label = NARRATIVE_LABELS[narrative]
    platform_label, default_quote, blurb_hint = PLATFORM_META[platform]
    if quote_style == "corner":
        quote_display = "「」 直角引号（嵌套用『』，严禁与“”混用）"
    elif quote_style == "double":
        quote_display = "“” 全角双引号（嵌套用‘’）"
    else:
        quote_display = default_quote
    brief_line = source_brief.strip() or "无（原创脑洞直接立项；若接入 webnovel-market-radar 的 选题简报.md / 扫榜报告.md 可在此记录路径与摘要）"

    concept_doc = f"""# {title} · 脑洞、规则卡与爽感节拍

- 书名：{title}
- 目标平台：`{platform}` · {platform_label}
- 对话引号规范：{quote_display}
- 节奏模板：`{mode}` · {mode_label}
- 目标体量：{words_display}
- 推进叙事类型：`{narrative}` · {narrative_label}
- 命名题材分支：[待填：分支 A 现代 / B 民国年代 / C 古代朝堂 / D 武侠仙侠 / E 科幻 / F 西幻；遵循 references/naming-and-titling.md]
- 章节命名体制：[待填：体制 A 极简词眼（2–4字） / B 单元+序号 / C 轻短语切片（4–8字） / D 纯序号无副标题]
- 上游雷达 / 选题简报来源：{brief_line}

---

## 0. 脑洞 5 问压测（含情感刺点与关系拉力）

1. **3 秒画面感**：[待填]
2. **持续冲突制造机**：[待填]
3. **反常识错位点**：[待填]
4. **智商与现实人欲动机（禁卡通恶人自爆）**：[待填]
5. **情感刺点与人物关系拉力（按题材适配：强情绪题材看痛点与拉扯，脑洞/规则题材看生存张力与钩子）**：[待填]

---

## 1. 一页高概念规则与关系卡

- **一句话高概念（≤30字，3秒懂画面）**：[待填]
- **唯一核心规则 / 核心关系死结**：[待填]
- **规则边界、代价或情感羁绊（制造拉扯与反转张力）**：[待填]
- **反常识错位点（与常见套路拧半圈的地方）**：[待填]

### 核心人物（精简 2–5 人 · 表里反差 + 反派四原则 + 反工具人配角）

| 角色 | 定位（主角/核心对手/官配或盟友） | 明面处境 | 表里反差与生活体感 | 情感软肋 / 关系拉扯（含非主角隐秘联系） | 真实欲念、道德支点与底牌/盲区 |
|---|---|---|---|---|---|
|  | 主角 |  |  |  |  |
|  | 核心对手 |  |  |  |  |
|  | 官配 / 关键盟友 |  |  |  |  |

---

## 2. 脉冲式爽感节拍表

> 规则：前 500 字直接入局；每章当下必有现场戏眼（禁纯筹备水章）；相邻大爽点切换新维度；冲突走「受阻—尝试—再受阻—转折」防过快见底。

{beat_table}

---

## 3. 单篇原声定调切片（200–300 字 · 本篇专属调音叉）

> 围绕开篇 300–500 字试写校准语感与温度后，粘贴最对味的 200–300 字原文在此；默认直写全文，仅在用户要求“先试写”时于第 2 章后暂停确认。

[待试写确认后填入]

---

## 4. 异构备选书名与平台导语 / 简介

> 适配参考：{blurb_hint}（跨型谱给 3 个不同气质方案，严禁直接把内部梗概当正式书名）

- **备选标题 1（意象/概念/人物短名型，2–8 字）**：
- **备选标题 2（半句对白/情绪悬念型，6–12 字，不剧透结局）**：
- **备选标题 3（信息流直述强钩子型，10–18 字，适配番茄/七猫/点众/黑岩点击，避开千篇一律陈旧复句）**：
- **平台导语 / 简介草稿**：
"""

    state_doc = f"""# {title} · 轻量写作状态

- 目标平台：`{platform}` ｜ 引号规范：{quote_display}
- 当前模式：`{mode}` ｜ 推进类型：`{narrative}`
- 已完成章节/分节：无
- 当前累计净汉字数：0
- 下一待写节拍：01 黄金入局

## 明牌线索与情感物象追踪

| 编号 | 线索/感官物象 | 首次亮出位置 | 计划回收位置 | 状态（已埋/已回收） |
|---|---|---|---|---|

## 核心人物当前筹码与情绪位置

- 主角（筹码 / 情绪温度）：
- 核心对手（盲区 / 破防进度）：
- 官配或关键盟友（关系拉扯进度）：

## 最近一节末尾衔接（1–2 句原文）

> （完成首节后粘贴章末 1–2 句，方便下一节无缝起笔）
"""

    return {
        "00_脑洞与节拍.md": concept_doc,
        "01_轻量状态.md": state_doc,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="初始化短篇网文轻量项目（仅建 2 份核心工作文件 + 正文/交付目录）。"
    )
    parser.add_argument("--root", required=True, help="项目根目录")
    parser.add_argument("--title", default="未命名短篇", help="作品名")
    parser.add_argument(
        "--mode",
        choices=("flash", "microdrama"),
        default="flash",
        help="节奏模板：flash（超短篇 0.8–3万字）或 microdrama（微短剧短中篇 2–5万字）",
    )
    parser.add_argument(
        "--narrative",
        choices=("dialogue", "first_person", "rules"),
        default="dialogue",
        help="推进叙事类型：dialogue / first_person / rules",
    )
    parser.add_argument(
        "--platform",
        choices=("general", "fanqie", "zhihu", "qimao", "dianzhong", "heiyan"),
        default="general",
        help="目标平台（默认 general；zhihu 自动启用「」直角引号与知乎盐言导语提示）",
    )
    parser.add_argument(
        "--quote-style",
        choices=("auto", "double", "corner"),
        default="auto",
        help="对话引号风格：auto（随平台）、double（“”）、corner（「」）",
    )
    parser.add_argument("--target-words", default="", help="可选自定义目标字数说明")
    parser.add_argument("--source-brief", default="", help="可选上游选题简报/雷达路径或摘要")
    parser.add_argument("--dry-run", action="store_true", help="仅预览不写入文件")
    args = parser.parse_args()

    try:
        root = safe_root(args.root)
    except ValueError as exc:
        parser.error(str(exc))

    dirs = [root / "正文", root / "交付"]
    if not args.dry_run:
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    title = args.title.strip() or "未命名短篇"
    files = build_templates(
        title=title,
        mode=args.mode,
        narrative=args.narrative,
        platform=args.platform,
        quote_style=args.quote_style,
        target_words=args.target_words,
        source_brief=args.source_brief,
    )

    created: list[Path] = []
    skipped: list[Path] = []
    for rel, content in files.items():
        dest = root / rel
        if dest.exists():
            skipped.append(dest)
            continue
        created.append(dest)
        if not args.dry_run:
            dest.write_text(content.rstrip() + "\n", encoding="utf-8")

    print(f"root={root}")
    print(f"platform={args.platform} mode={args.mode} narrative={args.narrative} quote_style={args.quote_style}")
    print(f"created={len(created)}")
    for p in created:
        print(f"  + {p.relative_to(root)}")
    print(f"skipped={len(skipped)}")
    for p in skipped:
        print(f"  = {p.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
