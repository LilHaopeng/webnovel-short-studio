---
name: webnovel-short-studio
description: 专为 5 万字以内高概念脑洞短篇网文设计的一体化创作工作室，内置「超短篇（1–3万字，盐选/番茄短故事）」与「微短剧式短中篇（2–5万字，分章强卡点）」两套节奏模板。涵盖脑洞压测、一页高概念规则卡、爽感叠加节拍表、单篇原声定调、手机竖屏短段与语言推进正文写作、分布级网感体检及纯净 DOCX/TXT 导出。默认简体中文。不用于 50 万字厚重世界观推演或传统出版长篇（请使用 story-world-architect / story-outline-architect / story-prose-writer），也不内置扫榜爬虫或洗稿仿写。
metadata:
  version: "1.1.0"
---

# 短篇网文与微短剧爽文创作室

面向手机竖屏阅读与 5 万字以内爆款短篇的高效快反工作流。核心创作定位为**高概念脑洞爽文**：节奏轻快、情绪到位、爽感层层叠加，同时尽量靠**信息差、规则漏洞与错位博弈**破局，不写低幼降智文。

## 核心原则：硬骨架，松表达

为避免“不约束 → 滑回传统出版长段说教腔”和“管太死 → 写成碎段电报体或千文一面 AI 爽文腔”两个极端，本技能严格分层约束：

- **前端硬骨架**：锁定反常识脑洞、清晰规则边界、多维度爽感叠加节拍、前 500 字入局与章末钩子，解决长文生成时中段泄气与套路复读。
- **后端松表达**：写作时仅锚定手机阅读媒介体感与本篇独立的 200–300 字原声切片；**不设单段硬字数红线、不写死固定打脸反应模板、不封杀正常高频词**，保留长短反差与题材多样性。
- **分布镜子体检**：`lint_webnovel.py` 仅作整章分布级诊断，供复核是否滑回出版长段或出现机械切段，**严禁为清零警告硬拆好段或凑水对话**。

## 语言与模式路由

默认**简体中文**（默认全角双引号 `“”`；目标平台为**知乎盐言**或用户指定时自动切为直角引号 `「」`）。按用户当下进度直接进入对应阶段，不强制从头走全流程：

| 阶段 | 适用请求 | 核心动作 | 必读参考 |
|---|---|---|---|
| `hook` | 只有一个想法、梗概或上游雷达/选题简报 | 脑洞 4 问压测、确定体量模板与推进类型、生成一页高概念规则卡（可选产出标题与平台导语） | [concept-and-beats.md](references/concept-and-beats.md) |
| `beat` | 脑洞已定，拆解全篇节奏与爽点 | 按 `flash` 或 `microdrama` 模板排布爽感叠加节拍表并做 4 项快检 | [concept-and-beats.md](references/concept-and-beats.md) |
| `voice` | 开写前定调或避免与前作撞声口 | 围绕开头试写 300–500 字，确认后提取 200–300 字定调原文写入设定卡 | [mobile-prose-and-voice.md](references/mobile-prose-and-voice.md) |
| `draft` | 正式撰写或续写章节/分节正文 | 读本篇设定节拍 + 声口切片 + 轻量状态卡，以手机端网感节奏写纯净正文 | [mobile-prose-and-voice.md](references/mobile-prose-and-voice.md) |
| `check` | 检查网感、段长分布、节奏与连续性 | 运行 `lint_webnovel.py` 复核分布信号，结合体感定向微调并回写状态卡 | [artifact-and-audit.md](references/artifact-and-audit.md) |
| `export` | 汇总交付编辑审阅或平台发布 | 按需补齐/定稿爆款标题与平台导语，运行 `export_short.py` 导出纯净 `.docx` 与 `.txt` | [artifact-and-audit.md](references/artifact-and-audit.md) |

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

### 2. 脑洞压测、一页设定与爽感叠加节拍

读 [concept-and-beats.md](references/concept-and-beats.md)：
1. 对想法做 **4 问脑洞压测**（3 秒画面感、持续冲突能力、反常识切口、不降智博弈依据），若立不住直接提出 2–3 个升级变体供用户拍板。
2. 填完 `00_脑洞与节拍.md` 的**一页纸规则卡**（1 条核心脑洞规则 + 1 个漏洞/约束 + 2–5 个核心人物的真实欲念与底牌）。
3. 按选定模板生成**爽感叠加节拍表**：明确前 500 字入局点、首次小反转点、相邻爽点的维度切换（避免原地复读同款打脸）及明牌伏笔位置，确认后动笔。

### 3. 单篇原声定调（防千文一面）

读 [mobile-prose-and-voice.md](references/mobile-prose-and-voice.md)：
- 围绕前 300–500 字真实开篇试写定调（用户已有明确声口样本时直接沿用）。
- 确认“对味”后，截取 **200–300 字原声切片**写入 `00_脑洞与节拍.md`，作为本篇专属调音叉。每篇新作独立定调，严禁复用固定打脸套话模板。

### 4. 正文撰写、分布体检与状态回写

写前只加载：`00_脑洞与节拍.md`（规则卡 + 当前节拍 + 声口切片）与 `01_轻量状态.md`（前文已明牌的线索、人物当前状态、上章末尾衔接）。
- 正文文件存入 `正文/`，只含标题与纯净小说正文，不夹杂任何工作台编号、字数统计或自检注释。
- 初稿完成后运行分布体检镜子：

```text
python <skill-dir>/scripts/lint_webnovel.py --file <章节文件> --narrative <dialogue|first_person|rules>
```

（首章可加 `--first-chapter` 检查黄金前 500 字；整本复查可用 `--dir <正文目录>`。）
- 按 [artifact-and-audit.md](references/artifact-and-audit.md) 解读体检信号：只修真正的结构跑偏（滑回出版长段、连续闷段、百字演讲腔、明显 AI 翻译腔），保留有意为之的长短反差；完成后用 5–10 行更新 `01_轻量状态.md`。

### 5. 纯净导出（DOCX + TXT）

```text
python <skill-dir>/scripts/export_short.py --chapters-dir <正文目录> --out-docx <交付目录>/<书名>_全文.docx --out-txt <交付目录>/<书名>_平台发布.txt --title <书名>
```

导出默认采用屏幕轻读排版（`screen`），自动拦截残留工程标记；如仅需其中一种格式，传入对应参数即可。
