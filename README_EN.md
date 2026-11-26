![Webnovel Short Studio · 短篇网文创作室](assets/short-studio-hero.png)

# Webnovel Short Studio · 短篇网文与微短剧爽文创作室

[简体中文](README.md) | **English**

An all-in-one Agent Skill for **high-concept short webnovels and micro-drama fiction under 50,000 words**. Ships with two battle-tested pacing templates—**Flash Short Fiction (`flash`, 8k–30k words for Zhihu Yanyan / Fanqie / Qimao)** and **Micro-Drama Serialized Shorts (`microdrama`, 20k–50k words across 10–25 cliffhanger chapters)**—covering 5-question premise stress testing, emotional resonance & anti-bureaucratic-jargon craft, anti-AI character naming & non-spoiler titling, per-story voice calibration, Fanqie 2026-11 pre-submission diagnostics, Track-B editor review, single-newline clean DOCX/TXT export, and platform-ready submission metadata checklists. Current version: **v1.3.0**.

By default, the skill writes in **Simplified Chinese (`简体中文`)** and automatically adapts quotation mark conventions (`“”` by default, or `「」` for Zhihu Yanyan).

> **Word-Count Routing**: Use this skill for `≤50k` high-concept shorts; for `>50k` commercial serialized webnovels, use [Webnovel Long Studio](https://github.com/LilHaopeng/webnovel-long-studio).

## Key Capabilities

- **Emotional Resonance & Anti-Bureaucratic Prose**: Preserves micro-sensory temperature contrasts, lived-in physical action, human vulnerability, realistic villain desires, and immediate scene stakes—preventing dry legal-report prose (`bureaucratic_jargon_density`) and filler prep chapters.
- **Dual Pacing Templates & Three Narrative Modes**:
  - `flash` (8k–30k word single-sitting short stories) and `microdrama` (20k–50k word chaptered micro-drama fiction with end-of-chapter hooks).
  - Supports `dialogue` (dialogue-driven confrontation), `first_person` (snappy first-person narrator), and `rules` (rule-horror / mystery information-flow) baselines.
- **Fanqie 2026-11 Pre-Submission Linter & Opt-In Gates**: `lint_webnovel.py` checks paragraph length distribution, consecutive monotonous stretches, 100+ char speeches, stacked short-dialogue ping-pong, staircase choppy fragments, punctuation hygiene, opening 500-char hook density, and `--names` / `--char-card` character-name spelling drift as a pure `[ADVISORY]` mirror. Both Gate 1 pauses and Qimao upload length/title limits (`≤18` chars via `--platform qimao --check-title`) remain **off by default** unless requested.
- **Anti-AI Naming & Diversified Titling**: Enforces six genre-calibrated surname quotas, blocks overused cliché character combos, outputs 3 heterogeneous title styles, and keeps chapter titles concise and spoiler-free.
- **Per-Story Voice Tuning Fork**: Calibrates a fresh 300–500 character opening sample before full drafting and locks an approved 200–300 character voice excerpt in `00_脑洞与节拍.md` so each short story maintains its own distinct voice.
- **Upstream Radar Intake & Clean Platform-Ready Export**: Directly consumes `选题简报.md` / `扫榜报告.md` from `webnovel-market-radar` with anti-plagiarism isolation; `export_short.py` parses every single-newline line as an independent paragraph (never gluing single-newline prose) and outputs screen-friendly `.docx` plus platform-ready `.txt` and verified preset-vocabulary submission checklists for `qimao` and `fanqie`.

## What's New in v1.3.0

- **Fanqie 2026-11 Pre-Submission Craft Checks**: Added monotonous-stretch, long-speech, dialogue-stacking, staircase-fragment, punctuation-hygiene, and `--char-card` / `--names` character-name drift diagnostics plus `--platform fanqie|zhihu|qimao` modes.
- **Non-Gluing Export & Platform Alignment**: Updated `export_short.py` to treat every single-newline line as a distinct paragraph, scan both titles and body for workbench-token leaks and chapter sequence gaps, align Qimao's title cap to `≤18` characters, and standardize Zhihu Yanyan (`知乎盐言`) naming.
- **Clean 7-Skill Handoffs**: Streamlined routing to `webnovel-long-studio` for >50k commercial serials and trimmed `SKILL.md` prompt overhead.

## Companion Studio Pipeline (7-Skill Ecosystem)

Each skill works standalone or connects into the full fiction & AI-drama studio ecosystem:

- **Commercial Webnovel & AI Drama Suite**
  1. [Webnovel Market Radar](https://github.com/LilHaopeng/webnovel-market-radar): Tri-track live ranking scanner & topic-brief generator across short webnovels, serialized long webnovels, and AI short/comic dramas.
  2. **Webnovel Short Studio**: Turns short-fiction topic briefs or raw high-concept ideas into mobile-first short webnovels under 50k words.
  3. [Webnovel Long Studio](https://github.com/LilHaopeng/webnovel-long-studio): Commercial serialized long-form webnovels (50k–2M+ words) with lean 4-ledger continuity & anti-collapse reviews.
  4. [AI Drama Script Studio](https://github.com/LilHaopeng/ai-drama-script-studio): Adapts short/long webnovels or original premises into MiniMax-H3 AI short dramas, 2D/3D comic dramas, and comedy short dramas.
- **Traditional & Literary Long-Form Novel Suite**
  5. [Story World Architect](https://github.com/LilHaopeng/story-world-architect): Builds causally grounded worlds, social ecosystems, and book-grade reader worldbooks.
  6. [Story Outline Architect](https://github.com/LilHaopeng/story-outline-architect): Designs Story DNA, multi-track arcs, sequences, and concrete chapter outlines.
  7. [Story Prose Writer](https://github.com/LilHaopeng/story-prose-writer): Calibrates literary/long-form voice, submerges outline beats into natural prose, and audits cross-chapter continuity.

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

Core scripts use Python 3.10+ standard library only; install `python-docx` via `python -m pip install -r requirements.txt` for `.docx` export.

## Quick Start

```text
$webnovel-short-studio
I want to write a 15k-word Zhihu Yanyan suspense short story where the protagonist can see everyone's remaining lifetime "lie quota" above their head.
Run the 5-question premise stress test, build the one-page rule & cast card, draft the beat sheet, and propose 3 heterogeneous title options with platform hooks.
```

## Helper Scripts

| Script | Purpose |
|---|---|
| `init_short_project.py` | Initializes the lightweight 2-file workbench (`00_脑洞与节拍.md`, `01_轻量状态.md`, `正文/`, `交付/`) with `--mode`, `--narrative`, `--platform`, and `--quote-style`. |
| `lint_webnovel.py` | Runs distribution-level readability & Fanqie pre-submission diagnostics (`--narrative`, `--first-chapter`, `--platform none\|fanqie\|zhihu\|qimao`, `--names`, `--char-card`, `--check-title`, `--json`). |
| `export_short.py` | Exports clean screen-formatted `.docx` (`--preset screen\|book`) and platform-ready `.txt` manuscripts with single-newline paragraph parsing and leak detection. |

Run unit tests:

```bash
python -B -m unittest discover -s tests -v
```

## Reference Guides

- [Concept Stress-Test & Beat Sheets](skills/webnovel-short-studio/references/concept-and-beats.md)
- [Emotional Resonance & Character Tension](skills/webnovel-short-studio/references/emotion-and-tension.md)
- [Mobile Prose & Per-Story Voice Calibration](skills/webnovel-short-studio/references/mobile-prose-and-voice.md)
- [Anti-AI Naming & Titling Standards](skills/webnovel-short-studio/references/naming-and-titling.md)
- [Artifacts & Dual-Track Audit Guide](skills/webnovel-short-studio/references/artifact-and-audit.md)
- [Platform Submission & Verified Tag Vocabularies](skills/webnovel-short-studio/references/platform-submission-tags.md)

## Privacy & License

All helper scripts operate strictly on local workspace files and never upload manuscripts. Released under the [MIT License](LICENSE) (Copyright © 2026 LilHaopeng).
