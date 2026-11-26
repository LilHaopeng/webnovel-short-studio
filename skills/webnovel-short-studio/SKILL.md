---
name: webnovel-short-studio
description: 专为 5 万字以内高概念脑洞短篇网文设计的一体化创作工作室，内置「超短篇（1–3万字，盐选/番茄短故事）」与「微短剧式短中篇（2–5万字，分章强卡点）」两套节奏模板。涵盖脑洞压测、一页高概念规则卡、爽感叠加节拍表、单篇原声定调、手机竖屏短段与语言推进正文写作、分布级网感体检及纯净 DOCX/TXT 导出。默认简体中文。不用于 50 万字厚重世界观推演或传统出版长篇（请使用 story-world-architect / story-outline-architect / story-prose-writer），也不内置扫榜爬虫或洗稿仿写。
metadata:
  version: "1.2.0"
---

# 短篇网文与微短剧爽文创作室

面向手机竖屏阅读与 5 万字以内爆款短篇的高效快反工作流。核心创作定位为**高概念脑洞爽文**：节奏轻快、情绪到位、爽感层层叠加，同时尽量靠**信息差、规则漏洞与错位博弈**破局，不写低幼降智文。

## 核心原则：硬骨架，松表达，活人感

为避免“不约束 → 滑回传统出版长段说教腔”、“管太死 → 写成碎段电报体或千文一面 AI 爽文腔”以及**“重流程轻情绪 → 写成没有痛觉神经的法务/取证说明书”**三个极端，本技能严格分层约束：

- **前端硬骨架 + 关系张力**：锁定反常识脑洞、清晰规则边界、**人物表里反差与真实人欲动机**、脉冲式微戏眼节拍，禁止前大半篇纯隐忍取证、禁止卡通降智反派与零铺垫工具人盟友。
- **后端松表达 + 活人感染力**：写作时锚定手机阅读体感、本篇专属原声切片与 `references/emotion-and-tension.md`；**保留真实痛觉与具象微感官（味觉、体温、旧物、冷幽默反讽），戒除密集公文/办件说明书腔**；不设单段硬字数红线、不写死固定打脸反应模板、不封杀正常高频词。
- **分布镜子体检 + 编辑双轨审稿**：`lint_webnovel.py` 仅作整章分布与公文腔诊断镜子，**平台上传字数硬限（如七猫单章 500–1500 字、标题 <18 字）默认不开启，仅在用户明确要求按平台上传硬限排查时才启用，绝不用侧边硬限制打断 AI 正常写作流**；写后须结合 B 轨签约编辑感染力视角复核。

## 语言与模式路由

默认**简体中文**（默认全角双引号 `“”`；目标平台为**知乎盐言**或用户指定时自动切为直角引号 `「」`）。按用户当下进度直接进入对应阶段，不强制从头走全流程；**默认顺畅写出完整全文，仅在用户明确要求“先试写”时，开启 Gate 1 试写停顿闸门（写完前 2 章即暂停交由用户拍板文风与情绪）**：

| 阶段 | 适用请求 | 核心动作 | 必读参考 |
|---|---|---|---|
| `hook` | 只有一个想法、梗概或上游雷达/选题简报 | 脑洞 5 问压测（含情感刺点与关系拉力）、确定体量模板与推进类型、生成一页高概念规则卡与人物反差表（人物命名与书名型谱按去 AI 味规范核对） | [concept-and-beats.md](references/concept-and-beats.md)、[emotion-and-tension.md](references/emotion-and-tension.md)、[naming-and-titling.md](references/naming-and-titling.md) |
| `beat` | 脑洞已定，拆解全篇节奏与爽点 | 按 `flash` 或 `microdrama` 模板排布脉冲式节拍表（每章有现场戏眼、禁纯筹备章），锁定全篇章节命名体制并做 6 项快检 | [concept-and-beats.md](references/concept-and-beats.md)、[naming-and-titling.md](references/naming-and-titling.md) |
| `voice` | 开写前定调、试写或避免撞声口 | 围绕开头试写 300–500 字校准温度感与语感，截取 200–300 字原声切片写入设定卡；若用户要求“先试写”则写完前 2 章停顿待审 | [mobile-prose-and-voice.md](references/mobile-prose-and-voice.md)、[emotion-and-tension.md](references/emotion-and-tension.md) |
| `draft` | 正式撰写或续写章节/分节正文 | 读本篇设定节拍 + 声口切片 + 轻量状态卡，以手机网感与活人感细节写纯净正文（临场龙套降噪、章名不剧透；默认连贯写完全文） | [mobile-prose-and-voice.md](references/mobile-prose-and-voice.md)、[emotion-and-tension.md](references/emotion-and-tension.md)、[naming-and-titling.md](references/naming-and-titling.md) |
| `check` | 检查网感、感染力、公文腔与连续性 | 运行 `lint_webnovel.py` 复核分布与公文腔信号，并按 B 轨签约编辑感染力与命名/标题清单审读精修（平台上传字数硬限仅按需开启） | [artifact-and-audit.md](references/artifact-and-audit.md)、[emotion-and-tension.md](references/emotion-and-tension.md)、[naming-and-titling.md](references/naming-and-titling.md) |
| `export` | 汇总交付编辑审阅或平台发布 | 跨型谱定稿正式书名（或给 3 风格异构备选）与平台导语，竖扫目录章名后运行 `export_short.py` 导出纯净 `.docx` 与 `.txt` | [artifact-and-audit.md](references/artifact-and-audit.md)、[naming-and-titling.md](references/naming-and-titling.md) |

## 上游扫文雷达 / 拆文产物对接接口（可选）

本技能不内置扫榜与拆文工具，但原生兼容独立扫文技能 **`webnovel-market-radar`** 及常见外部拆文产物：
- **支持直读的上游文件**：`选题简报.md` / `扫榜报告.md`（来自 `webnovel-market-radar`）、`选题决策.md`（来自 `story-long-scan`）、`拆文库/{书名}/`（仅读 `拆文报告.md`、`_meta.json` 及可选 `写作手法.md`）。
- **防洗稿隔离纪律**：只吸收市场验证过的情绪痛点、节奏占比、反转类型、平台篇幅与导语规律；**默认隔离他人 `原文/` 不直喂正文写作**，进入 `hook` 后必须强制重写具体的奇观脑洞、规则机制、人物与反转路径。

## 快速工作流

### 1. 初始化轻量项目（仅 2 份核心工作文件）

放弃重型世界观与六层大纲，每篇短篇仅维护 `00_脑洞与节拍.md` 和 `01_轻量状态.md`：

```text
python <skill-dir>/scripts/init_short_project.py --root <项目根> --title <书名> --mode <flash|microdrama> --narrative <dialogue|first_person|rules> --platform <general|fanqie|zhihu|qimao|dianzhong|heiyan>
```

- `--mode`：`flash`（超短篇 0.8–3 万字，盐选/番茄短故事）或 `microdrama`（微短剧式短中篇 2–5 万字，10–25 章）。
- `--narrative`：`dialogue`（强对话交锋型）、`first_person`（第一人称强叙述吐槽型）或 `rules`（规则/悬疑信息流型）。
- `--platform`：可选指定目标平台以预置标题/导语公式与标点规范（`zhihu` 默认启用 `「」` 直角引号）。

### 2. 脑洞 5 问压测、一页设定与脉冲式节拍

读 [concept-and-beats.md](references/concept-and-beats.md) 与 [emotion-and-tension.md](references/emotion-and-tension.md)：
1. 对想法做 **5 问脑洞压测**（3 秒画面感、持续冲突能力、反常识切口、不降智博弈依据、**情感痛点与人物关系拉力**），若立不住直接提出 2–3 个升级变体。
2. 填完 `00_脑洞与节拍.md` 的**一页纸规则与关系卡**（核心规则/处境 + 漏洞/约束 + 2–5 个核心人物的**表里反差切面、情感软肋/关系拉扯点**及真实利益诉求）。
3. 按选定模板生成**脉冲式爽感节拍表**：明确前 500 字入局点、每章当下戏眼与情绪刺点（严禁纯收集证据/等明天的筹备水章）、相邻爽点维度切换及明牌伏笔位置。

### 3. 单篇原声定调（按需启用 Gate 1 试写停顿）

读 [mobile-prose-and-voice.md](references/mobile-prose-and-voice.md) 与 [emotion-and-tension.md](references/emotion-and-tension.md)：
- 围绕前 300–500 字真实开篇试写定调，核对既有手机滑读手感，也有**活人温度、微感官痛点与语言辨识度**，截取 **200–300 字原声切片**写入 `00_脑洞与节拍.md`。
- **Gate 1 试写闸门（按需开启，默认直写全文）**：若用户明确说了“先试写 / 先看前两章”，则写完前 2 章并附 B 轨编辑自评后暂停交由用户确认文风；未指定时默认顺畅写完全文。

### 4. 正文撰写、分布与感染力双轨体检

写前只加载：`00_脑洞与节拍.md`（规则与关系卡 + 当前节拍 + 声口切片）与 `01_轻量状态.md`（前文已明牌的线索、人物当前筹码与情绪位置、上章末尾衔接）。
- 正文文件存入 `正文/`，只含标题与纯净小说正文，不夹杂任何工作台编号、字数统计或自检注释。
- 初稿完成后运行分布与公文腔体检镜子（**平台上传字数硬限参数 `--platform` / `--max-raw-chars` / `--check-title` 默认不开启，仅在用户明确要求排查平台上传字数限制时才附加**）：

```text
python <skill-dir>/scripts/lint_webnovel.py --file <章节文件> --narrative <dialogue|first_person|rules>
```

（首章可加 `--first-chapter` 检查黄金前 500 字；整本复查可用 `--dir <正文目录>`；用户明确要求核查七猫上传单章 500–1500 字或标题 <18 字硬限时，再额外传入 `--platform qimao --check-title "<书名>"`。）
- 按 [artifact-and-audit.md](references/artifact-and-audit.md) 完成 **A 轨工程体检 + B 轨签约编辑感染力审读**，只修真正的跑偏（出版长闷段、百字演讲腔、公文流程单腔、情绪真空、人物工具化），保留自然长短反差与感官温度；完成后用 5–10 行更新 `01_轻量状态.md`。

### 5. 纯净导出（DOCX + TXT）

```text
python <skill-dir>/scripts/export_short.py --chapters-dir <正文目录> --out-docx <交付目录>/<书名>_全文.docx --out-txt <交付目录>/<书名>_平台发布.txt --title <书名>
```

导出默认采用屏幕轻读排版（`screen`），自动拦截残留工程标记；如仅需其中一种格式，传入对应参数即可。
