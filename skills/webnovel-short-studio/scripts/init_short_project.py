#!/usr/bin/env python3
"""Initialize a lightweight short-webnovel project (2 core workspace files + clean dirs)."""

from __future__ import annotations

import argparse
from pathlib import Path


MODE_META: dict[str, tuple[str, str, str]] = {
    "flash": (
        "超短篇（盐选 / 番茄短故事 / 强反转爆文）",
        "12000 - 25000 字",
        """| 节拍 | 进度 / 预计字数 | 冲突与爽点任务 | 爽感维度（相邻需切换/叠加） | 明牌线索（埋 / 收） | 章末或节末钩子 |
|---|---|---|---|---|---|
| 01 黄金入局 | 0%–10%（前1500字） | 前500字砸出奇观规则/当场危机，1500字内首次小验证 |  | 埋： |  |
| 02 递进反杀 | 10%–45% | 对手加码打压，主角用维度A破局并拿实质筹码 |  | 埋/收： |  |
| 03 假危机+中反转 | 45%–70% | 对手搬出更硬底牌看似翻盘，主角切维度B反将一军 |  | 埋/收： |  |
| 04 终局大掀桌 | 70%–92% | 回收开篇核心明牌线索，彻底掀翻局面 |  | 收： |  |
| 05 短促收束 | 92%–100%（300–800字） | 干脆落定新局面或留一记回马枪 |  | — |  |""",
    ),
    "microdrama": (
        "微短剧式短中篇（10–25 章 · 章章强卡点）",
        "25000 - 45000 字（单章约 1800–2200 字）",
        """| 单元 / 章节 | 预计字数 | 本单元核心赌局与情绪落差（压→扬 / 悬→破） | 主打爽感维度（每单元须切换/叠加） | 明牌线索（埋 / 收） | 关键章末钩子 |
|---|---|---|---|---|---|
| 开篇钩子（第1–2章） | 约 3600–4400 字 | 第1章前500字入局立奇观并卡硬悬念；第2章首次痛快兑现+拉大主线 |  | 埋： |  |
| 循环一（第3–6章） | 约 7500–8500 字 | 首个完整压迫→布局→反杀循环，拿到新筹码 |  | 埋/收： |  |
| 循环二（第7–10章） | 约 7500–8500 字 | 危机升级、对手换招，切换爽感维度破局 |  | 埋/收： |  |
| 循环三（第11–14章） | 约 7500–8500 字 | 假绝境+规则反噬/底牌亮明，叠加更强情绪释放 |  | 埋/收： |  |
| 终局清算（最后2–3章） | 约 4000–6000 字 | 回收全部明牌线索，彻底清算并利落收官 |  | 收： |  |""",
    ),
}

NARRATIVE_LABELS: dict[str, str] = {
    "dialogue": "dialogue（强对话交锋型：短促台词一来一回 + 当下反应为主引擎）",
    "first_person": "first_person（第一人称强叙述吐槽型：极强主观口吻 + 犀利短评 + 关键台词爆点）",
    "rules": "rules（规则/悬疑信息流型：冷峻观察 + 反常细节 + 规则条目与短句破绽反差）",
}

PLATFORM_META: dict[str, tuple[str, str, str]] = {
    "general": ("通用 / 多平台短篇", "“” 全角双引号", "150–250 字电影预告片式导语（核心高概念 + 爽点预览 + 悬念钩子）"),
    "fanqie": ("番茄短故事 / 番茄短中篇", "“” 全角双引号", "120–260 字冲突前置导语（奇观处境 → 狠话/压迫 → 反杀预告与钩子）"),
    "zhihu": ("知乎盐言故事", "「」 直角引号（嵌套用『』，严禁与“”混用）", "200–500 字独立微小说导语（人物关系 + 核心冲突 + 2–3转折 + 金句/强悬念收口）"),
    "qimao": ("七猫短篇", "“” 全角双引号", "120–260 字强情绪导语（日常被破 → 最伤人一句对白 → 态度反转与钩子）"),
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
- 上游雷达 / 选题简报来源：{brief_line}

---

## 1. 一页高概念规则卡

- **一句话高概念（≤30字，3秒懂画面）**：[待填]
- **唯一核心规则（脑洞 / 金手指 / 极端机制）**：[待填]
- **规则边界或漏洞（防止无敌平推，制造反转张力）**：[待填]
- **反常识错位点（与常见套路拧半圈的地方）**：[待填]

### 核心人物（精简 2–5 人）

| 角色 | 定位（主角/核心对手/关键配角） | 明面身份与处境 | 真实底牌 / 贪欲盲区 | 说话与行事底色 |
|---|---|---|---|---|
|  | 主角 |  |  |  |
|  | 核心对手 |  |  |  |
|  | 关键配角 |  |  |  |

---

## 2. 爽感叠加节拍表

> 规则：前 500 字直接入局；相邻大爽点至少切换或叠加 1 种新爽感维度（信息差 / 规则漏洞 / 身份实力 / 利益反噬 / 情绪掀桌 / 伏笔反转）；反转关键线索提前明牌埋设。

{beat_table}

---

## 3. 单篇原声定调切片（200–300 字 · 本篇专属调音叉）

> 围绕开篇 300–500 字试写定调并经确认后，粘贴最对味的 200–300 字原文在此。后续每节/每章动笔前仅读此切片校准语感，不跨篇复用固定打脸套话。

[待试写确认后填入]

---

## 4. 爆款标题与平台导语 / 简介（可选转化交付件）

> 适配参考：{blurb_hint}

- **备选标题 1（事件反杀型）**：
- **备选标题 2（反差脑洞型）**：
- **备选标题 3（精短钩子型）**：
- **平台导语 / 简介草稿**：
"""

    state_doc = f"""# {title} · 轻量写作状态

- 目标平台：`{platform}` ｜ 引号规范：{quote_display}
- 当前模式：`{mode}` ｜ 推进类型：`{narrative}`
- 已完成章节/分节：无
- 当前累计净汉字数：0
- 下一待写节拍：01 开篇入局

## 明牌线索与伏笔追踪

| 编号 | 线索/规则细节 | 首次亮出位置 | 计划回收位置 | 状态（已埋/已回收） |
|---|---|---|---|---|

## 核心人物当前筹码与认知盲区

- 主角：
- 核心对手：

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
        help="节奏模板：flash（超短篇 1–3万字）或 microdrama（微短剧短中篇 2–5万字）",
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
        help="目标平台（默认 general；zhihu 自动启用「」直角引号与盐言导语提示）",
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
