# Webnovel Short Studio · 短篇网文与微短剧爽文创作室

[简体中文](README.md) | **English**

An all-in-one Agent Skill for high-concept short webnovels and micro-drama fiction under 50,000 words. Ships with two battle-tested pacing templates—**Flash Short Fiction (`flash`, 8k–30k words for Zhihu Yanyan / Fanqie Short Stories)** and **Micro-Drama Serialized Shorts (`microdrama`, 20k–50k words across 10–25 cliffhanger chapters)**—covering high-concept stress testing, a one-page rule & cast card, multi-dimensional payoff beat sheets, per-story voice calibration, mobile-first vertical prose, distribution-based pacing diagnostics, and clean DOCX/TXT export. Current version: **v1.1.0**.

By default, the skill writes in **Simplified Chinese (`简体中文`)** and automatically adapts quotation mark conventions (`“”` by default, or `「」` for Zhihu Yanyan).

## Key Capabilities

- **Firm Skeleton, Flexible Expression**: Locks in counter-intuitive hooks, clear rule constraints, escalating payoff dimensions, a fast 500-character opening hook, and chapter-end cliffhangers upfront—while avoiding rigid single-paragraph word caps or recycled slap-in-the-face templates during drafting.
- **Dual Pacing Templates & Three Narrative Modes**:
  - `flash` (8k–30k word single-sitting short stories) and `microdrama` (20k–50k word chaptered micro-drama fiction).
  - Supports `dialogue` (dialogue-driven confrontation), `first_person` (snappy first-person narrator), and `rules` (rule-horror / mystery information-flow) baselines.
- **Per-Story Voice Tuning Fork**: Calibrates a fresh 300–500 character opening sample before full drafting and stores an approved 200–300 character excerpt in `00_脑洞与节拍.md` so each short story maintains its own distinct voice.
- **Distribution-Based Mobile Readability Linter**: `lint_webnovel.py` inspects chapter-wide paragraph length distributions, dialogue momentum, opening 500-character hook density, and cliché clusters as a diagnostic mirror—never forcing mechanical paragraph splitting.
- **Upstream Market Radar Integration**: Directly consumes `选题简报.md` / `扫榜报告.md` from `webnovel-market-radar` while enforcing anti-plagiarism isolation (adopting market-validated emotional hooks and pacing ratios while mandating original premise and character invention).
- **Clean DOCX & TXT Export**: `export_short.py` compiles chapters into screen-friendly `.docx` and platform-ready `.txt` files while blocking internal workbench markers.

## Companion Studio Pipeline

Each skill works standalone or connects into the full six-skill fiction & AI-drama studio ecosystem:

- **Market Radar, High-Concept Short Fiction & AI Drama Suite**
  1. [Webnovel Market Radar](https://github.com/LilHaopeng/webnovel-market-radar): Tri-track market ranking scanner and topic-brief generator across short webnovels, serialized long webnovels, and AI short dramas / comic dramas.
  2. **Webnovel Short Studio**: Turns short-fiction topic briefs or raw high-concept ideas into mobile-first short webnovels under 50k words.
  3. [AI Drama Script Studio](https://github.com/LilHaopeng/ai-drama-script-studio): Adapts short/long webnovels or original premises into MiniMax-H3 AI short dramas, 2D/3D comic dramas, and comedy short drama scripts.
- **Long-Form & Literary Novel Suite (500k+ Words)**
  4. [Story World Architect](https://github.com/LilHaopeng/story-world-architect): Builds causally grounded worlds, social ecosystems, and reader worldbooks.
  5. [Story Outline Architect](https://github.com/LilHaopeng/story-outline-architect): Designs Story DNA, multi-track arcs, sequences, and concrete chapter outlines.
  6. [Story Prose Writer](https://github.com/LilHaopeng/story-prose-writer): Calibrates long-form voice, submerges outline beats into natural prose, and audits cross-chapter continuity.

## Installation

1. **Via `skill-installer` (Codex, etc.)**
   ```text
   $skill-installer Install skills/webnovel-short-studio from https://github.com/LilHaopeng/webnovel-short-studio
   ```
2. **Manual Local Installation (Antigravity / Claude Code / Codex / Cursor)**
   Clone this repository and copy `skills/webnovel-short-studio/` into your client's skills directory:
   - **Antigravity**: `~/.gemini/config/skills/webnovel-short-studio`
   - **Claude Code**: `~/.claude/skills/webnovel-short-studio`
   - **Codex**: `~/.codex/skills/webnovel-short-studio` or `~/.agents/skills/webnovel-short-studio`
   - **Cursor**: `~/.cursor/skills/webnovel-short-studio`

## Helper Scripts

| Script | Purpose |
|---|---|
| `init_short_project.py` | Initializes the lightweight 2-file workbench (`00_脑洞与节拍.md`, `01_轻量状态.md`, `正文/`, `交付/`) with `--mode`, `--narrative`, and `--platform`. |
| `lint_webnovel.py` | Runs distribution-level mobile readability diagnostics (`--narrative`, `--first-chapter`, `--target-words`, `--json`). |
| `export_short.py` | Exports clean screen-formatted `.docx` (`--preset screen\|book`) and platform-ready `.txt` manuscripts. |

Run unit tests:

```bash
python -B -m unittest discover -s tests -v
```

## Privacy & License

All helper scripts operate strictly on local workspace files and never upload manuscripts. Released under the [MIT License](LICENSE) (Copyright © 2026 LilHaopeng).
