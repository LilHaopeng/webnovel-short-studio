---
name: webnovel-short-studio
description: 专为 5 万字以内高概念脑洞短篇与微短剧爽文设计的一体化创作工作室，内置「超短篇（0.8–3万字，知乎盐言/番茄短故事）」与「微短剧式短中篇（2–5万字，分章强卡点）」两套节奏模板。涵盖脑洞5问压测、一页高概念规则卡、爽感叠加节拍、原声定调、手机竖屏写作、番茄投稿前排版/语病分布体检、B轨感染力审读、纯净 DOCX/TXT 导出及平台投稿建书清单。默认简体中文。>5万字商业连载长篇网文转 webnovel-long-studio；传统出版/厚重世界观长篇转 story-world-architect / story-outline-architect / story-prose-writer；AI短剧剧本转 ai-drama-script-studio。
metadata:
  version: "1.3.0"
---

# 短篇网文与微短剧爽文创作室

面向手机竖屏与 **≤5 万字**爆款短篇（番茄短故事、知乎盐言、七猫、点众、黑岩）的高效快反创作室。定位**高概念脑洞与强情绪爽文**：靠信息差、规则漏洞与错位博弈破局，拒绝低幼降智与无痛觉说明书腔。

> **跨技能路由**：`≤5万字` 短篇留在本技能；`>5万字` 商业连载长篇转 `webnovel-long-studio`；传统出版/厚重世界观长篇转 `story-world-architect` / `story-outline-architect` / `story-prose-writer`；AI 短剧/漫剧脚本转 `ai-drama-script-studio`。不内置扫榜爬虫或洗稿仿写。

## 核心原则：硬骨架，松表达，活人感

- **硬骨架**：锁反常识脑洞、清晰规则边界、人物反差与现实动机（反派讲逻辑、配角不工具化）、脉冲式现场戏眼，禁前大半篇纯筹备与冲突秒杀断档。
- **松表达**：锚定手机滑读体感、单篇原声切片与场景/动作写活技法；强情绪赛道留真实痛觉与生活体感，戒公文说明书腔，不设单段硬字数笼子。
- **双轨体检**：`lint_webnovel.py` 仅作分布与番茄投稿前诊断镜子（纯 `ADVISORY`）；**平台上传字数/标题硬限默认关闭，仅在用户明确要求核查时启用**；写后须叠加 B 轨感染力审读。

## 语言、闸门与阶段路由

- **引号**：默认简体中文 `“”`（嵌套 `‘’`）；**知乎盐言**或用户指定时统一用 `「」`（嵌套 `『』`），禁混用。
- **Gate 1 试写闸门**：默认顺畅写完全文；仅当用户明确要求“先试写”时，写完前 2 章附 B 轨自评后暂停确认。
- **按进度直入阶段**：

| 阶段 | 适用请求 | 核心动作 | 必读参考 |
|---|---|---|---|
| `hook` | 想法、梗概或上游选题简报 | 脑洞 5 问压测、一页规则与关系卡、人物命名与异构书名 | [concept-and-beats.md](references/concept-and-beats.md)、[emotion-and-tension.md](references/emotion-and-tension.md)、[naming-and-titling.md](references/naming-and-titling.md) |
| `beat` | 拆解全篇节奏与爽点 | 排 `flash` / `microdrama` 节拍表、锁章名体制、过 6 项快检 | [concept-and-beats.md](references/concept-and-beats.md)、[naming-and-titling.md](references/naming-and-titling.md) |
| `voice` | 开写前定调防撞声口 | 开篇试写 300–500 字校准语感，固化 200–300 字原声切片 | [mobile-prose-and-voice.md](references/mobile-prose-and-voice.md)、[emotion-and-tension.md](references/emotion-and-tension.md) |
| `draft` | 正式撰写或续写正文 | 读设定卡、声口切片与状态卡，写手机网感纯净正文 | [mobile-prose-and-voice.md](references/mobile-prose-and-voice.md)、[emotion-and-tension.md](references/emotion-and-tension.md)、[naming-and-titling.md](references/naming-and-titling.md) |
| `check` | 网感、排版、感染力体检 | 跑 `lint_webnovel.py` + 反向查错 + B 轨编辑审读精修 | [artifact-and-audit.md](references/artifact-and-audit.md)、[emotion-and-tension.md](references/emotion-and-tension.md)、[naming-and-titling.md](references/naming-and-titling.md) |
| `export` | 定稿交付或平台投稿 | 定书名导语、竖扫章名、导出 DOCX/TXT 及投稿建书清单 | [artifact-and-audit.md](references/artifact-and-audit.md)、[naming-and-titling.md](references/naming-and-titling.md)、[platform-submission-tags.md](references/platform-submission-tags.md) |

## 上游对接（可选）

兼容 `webnovel-market-radar` 的 `选题简报.md` / `扫榜报告.md` 及外部 `拆文库/{书名}/`（仅读 `拆文报告.md` / `_meta.json` / `写作手法.md`）：只取情绪痛点、节奏占比与导语规律，**隔离他人 `原文/`**，入 `hook` 后强制原创重写核心设定与反转。

## 快速工作流

1. **初始化（仅 2 份工作文件 `00_脑洞与节拍.md` / `01_轻量状态.md`）**：
   ```text
   python <skill-dir>/scripts/init_short_project.py --root <项目根> --title <书名> --mode <flash|microdrama> --narrative <dialogue|first_person|rules> --platform <general|fanqie|zhihu|qimao|dianzhong|heiyan>
   ```
2. **脑洞压测与节拍**：读 [concept-and-beats.md](references/concept-and-beats.md) 与 [emotion-and-tension.md](references/emotion-and-tension.md)，完成 5 问压测、一页规则关系卡（2–5 人）与脉冲式节拍 6 项快检。
3. **原声定调**：读 [mobile-prose-and-voice.md](references/mobile-prose-and-voice.md)，试写开篇并将 200–300 字原声切片存入 `00_脑洞与节拍.md`。
4. **写正文与双轨体检**：正文存 `正文/`（只含 `# 标题` 与正文）。写后跑体检并按 [artifact-and-audit.md](references/artifact-and-audit.md) 完成 A/B 审读，10 秒回写 `01_轻量状态.md`：
   ```text
   python <skill-dir>/scripts/lint_webnovel.py --file <章节文件> --narrative <dialogue|first_person|rules>
   ```
   （首章可加 `--first-chapter`；整本用 `--dir <正文目录>`；按需传 `--platform fanqie|zhihu|qimao` 与 `--names`/`--char-card`。）
5. **纯净导出与投稿清单**：
   ```text
   python <skill-dir>/scripts/export_short.py --chapters-dir <正文目录> --out-docx <交付目录>/<书名>_全文.docx --out-txt <交付目录>/<书名>_平台发布.txt --title <书名>
   ```
   目标平台为 `qimao` / `fanqie` 或用户要求投稿信息时，读 [platform-submission-tags.md](references/platform-submission-tags.md) 严格从原词库生成《投稿建书填表清单》。
