# 短篇网文与微短剧爽文创作室 · Webnovel Short Studio

**简体中文** | [English](README_EN.md)

专为 5 万字以内高概念脑洞短篇网文设计的一体化创作 Agent Skill：内置**超短篇（0.8–3 万字，知乎盐言 / 番茄短故事）**与**微短剧式短中篇（2–5 万字，10–25 章强卡点）**两套节奏模板，涵盖脑洞 4 问压测、一页高概念规则卡、爽感叠加节拍表、单篇原声定调、手机竖屏短段与语言推进正文写作、分布级网感体检及纯净 DOCX/TXT 导出。当前版本 **v1.1.0**。

默认采用**简体中文**起笔（默认全角双引号 `“”`；目标平台为**知乎盐言**或显式指定时自动切换为直角引号 `「」`）。

## 核心特性

- **硬骨架，松表达（拒绝千文一面 AI 爽文腔）**：前端锁死反常识脑洞、清晰规则边界、多维度爽感叠加节拍、黄金前 500 字入局与章末硬钩子；后端仅锚定手机竖屏阅读媒介体感与本篇独立的 200–300 字原声切片，不设单段硬字数红线、不写死固定打脸反应模板。
- **双体量节奏模板与三类叙事推进**：
  - `flash`（0.8–3 万字超短篇，适合盐选专栏/番茄短故事一口气读完）与 `microdrama`（2–5 万字微短剧式分章爽文，章章卡钩子）。
  - 支持 `dialogue`（强对话交锋型）、`first_person`（第一人称强叙述吐槽型）与 `rules`（规则怪谈/悬疑信息流型）三档网感基准。
- **爽感维度错位叠加**：强制相邻爽点在“信息差碾压 → 规则漏洞反杀 → 身份/筹码错位 → 公开处刑/认知颠覆”之间切换，杜绝原地复读同款打脸。
- **单篇原声调音叉**：正式批量动笔前先围绕开篇试写 300–500 字，确认对味后截取 200–300 字原声切片写入 `00_脑洞与节拍.md`，防止多篇短篇撞声口。
- **整章分布级网感体检**：内置 `lint_webnovel.py`，仅做整章段长分布、对话推进占比、前 500 字入局速度与套话密度的客观镜子诊断，严禁为清零警告硬拆好段或凑水对话。
- **无缝衔接上游扫榜雷达与防洗稿隔离**：原生直读 `webnovel-market-radar` 产出的 `选题简报.md` / `扫榜报告.md`，只吸收市场验证过的情绪痛点与节奏骨架，强制重写具体奇观脑洞、规则机制与人物。
- **双格式纯净导出**：内置 `export_short.py`，一键导出屏幕轻读版 `.docx` 与平台直发 `.txt`，自动剥离内部工作台标记并支持知乎盐言 `「」` 引号规范。

## 配套创作工作流

同系列六大技能既可独立使用，也可按体量与媒介串联成完整的小说与短剧创作管线：

- **市场雷达、高概念短篇与 AI 短剧工作流**
  1. [网文与短剧市场雷达 · Webnovel Market Radar](https://github.com/LilHaopeng/webnovel-market-radar)：短篇网文、长篇网文与 AI 短剧/漫剧三轨实时扫榜与选题简报生成。
  2. **短篇网文与微短剧爽文创作室 · Webnovel Short Studio**：承接短篇选题简报或脑洞创意，完成 5 万字以内高概念短篇与微短剧向爽文创作。
  3. [AI 短剧与沙雕短剧编剧室 · AI Drama Script Studio](https://github.com/LilHaopeng/ai-drama-script-studio)：将短篇网文、长篇小说或原创脑洞改编为 MiniMax-H3 AI 短剧、2D/3D 漫剧与沙雕短剧剧本。
- **长篇与精品小说三件套（50 万字+厚重推演）**
  4. [小说世界观架构师 · Story World Architect](https://github.com/LilHaopeng/story-world-architect)：构建深层世界规则、社会生态与读者向世界设定集。
  5. [小说大纲架构师 · Story Outline Architect](https://github.com/LilHaopeng/story-outline-architect)：构建 Story DNA、五轨故事架构、故事弧与具象章纲。
  6. [小说正文写作 · Story Prose Writer](https://github.com/LilHaopeng/story-prose-writer)：长篇声口校准、大纲消融正文撰写与跨章连续性审校。

## 安装方式

1. **通过 `skill-installer` 安装（Codex 等）**
   ```text
   $skill-installer 请从 https://github.com/LilHaopeng/webnovel-short-studio 安装 skills/webnovel-short-studio
   ```
2. **手动复制到本地技能目录（Antigravity / Claude Code / Codex / Cursor）**
   克隆本仓库，将 `skills/webnovel-short-studio/` 完整复制到对应客户端的技能目录：
   - **Antigravity**：`~/.gemini/config/skills/webnovel-short-studio`
   - **Claude Code**：`~/.claude/skills/webnovel-short-studio`
   - **Codex**：`~/.codex/skills/webnovel-short-studio` 或 `~/.agents/skills/webnovel-short-studio`
   - **Cursor**：`~/.cursor/skills/webnovel-short-studio`

核心初始化与体检脚本仅使用 Python 3.10+ 标准库；如需导出 `.docx` 文档，可执行 `python -m pip install -r requirements.txt` 安装 `python-docx`。

## 快速上手

**从脑洞直接开写超短篇（盐言 / 番茄短故事）**：

```text
$webnovel-short-studio
我想写一篇 1.5 万字左右的知乎盐言悬疑脑洞短篇：主角能看到每个人头顶的“谎言剩余额度”。
先帮我做脑洞 4 问压测、一页规则卡和爽感叠加节拍表，并给出 3 个爆款备选标题与平台导语。
```

**承接上游扫榜简报开写微短剧式分章爽文**：

```text
$webnovel-short-studio
读取 扫榜/20261121_fanqie_short/选题简报.md 里的选题 1，按 microdrama 模板初始化项目，先定一页规则卡并试写前 400 字校准声口。
```

## 配套辅助脚本

| 脚本 | 功能说明 |
|---|---|
| `init_short_project.py` | 轻量初始化 `00_脑洞与节拍.md`、`01_轻量状态.md`、`正文/` 与 `交付/`（支持 `--mode flash\|microdrama`、`--narrative dialogue\|first_person\|rules`、`--platform`）。 |
| `lint_webnovel.py` | 手机端网感分布体检镜子：统计段长分布、对话推进占比、前 500 字入局要素与套话密度（支持 `--narrative`、`--first-chapter`、`--target-words`、`--json`）。 |
| `export_short.py` | 将 `正文/` 下的章节汇总导出为屏幕轻读版 `.docx`（`--preset screen\|book`）与平台发布版 `.txt`，自动拦截工程标记泄露。 |

常用命令示例：

```bash
python skills/webnovel-short-studio/scripts/init_short_project.py --root <项目根> --title "谎言额度" --mode flash --narrative rules --platform zhihu
python skills/webnovel-short-studio/scripts/lint_webnovel.py --file <项目根>/正文/第01节.md --narrative rules --first-chapter
python skills/webnovel-short-studio/scripts/export_short.py --chapters-dir <项目根>/正文 --out-docx <项目根>/交付/谎言额度.docx --out-txt <项目根>/交付/谎言额度.txt --title "谎言额度"
```

运行回归测试：

```bash
python -B -m unittest discover -s tests -v
```

## 参考文档

- [高概念脑洞压测与爽感节拍表](skills/webnovel-short-studio/references/concept-and-beats.md)：脑洞 4 问压测、一页规则卡、`flash`/`microdrama` 双轨节拍模板与爆款标题/导语公式。
- [手机竖屏语感与单篇原声定调](skills/webnovel-short-studio/references/mobile-prose-and-voice.md)：竖屏短段与语言推进、三类叙事通道、200–300 字原声切片与防套路复读。
- [产物契约与分布级体检指南](skills/webnovel-short-studio/references/artifact-and-audit.md)：极简双文件工作台、`lint_webnovel.py` 指标解读与纯净导出规范。

## 隐私与许可证

所有辅助脚本均在本地工作区内读写文件，不会上传任何原稿。本仓库采用 [MIT License](LICENSE) 开源（Copyright © 2026 LilHaopeng）。
