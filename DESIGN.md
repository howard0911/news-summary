---
# gstack: design-md-format=spec
name: Daily Digest
description: Calm, plain Swiss type on near-white paper, one seal-red action, English and 中文 set side by side.
colors:
  paper: "#FAFAF7"
  paper-raised: "#FFFFFF"
  ink: "#111111"
  ink-2: "#5F5F5B"
  ink-3: "#8C8C86"
  rule: "#E4E4DF"
  rule-strong: "#111111"
  accent: "#C2361C"
  accent-hover: "#A82E17"
  accent-ink: "#F8F7F3"
  wash: "#FBE4DC"
  success: "#2F6B3F"
  warning: "#8A5A00"
  info: "#1F3A5F"
  error: "#111111"
  dark-paper: "#111214"
  dark-paper-raised: "#18191C"
  dark-ink: "#EDEDEA"
  dark-ink-2: "#9A9A94"
  dark-ink-3: "#6E6E69"
  dark-rule: "#2A2B2F"
  dark-accent: "#FF6A4A"
  dark-accent-hover: "#FF8466"
  dark-accent-ink: "#111214"
  dark-wash: "#2B1A16"
typography:
  nameplate:
    fontFamily: Geist
    fontWeight: 650
    fontSize: clamp(40px, 6vw, 64px)
    lineHeight: 0.95
    letterSpacing: -0.04em
  nameplate-zh:
    fontFamily: Noto Sans TC
    fontWeight: 700
    fontSize: clamp(18px, 2.2vw, 22px)
    letterSpacing: 0.08em
  h2:
    fontFamily: Geist
    fontWeight: 600
    fontSize: clamp(28px, 3.6vw, 40px)
    lineHeight: 1.1
    letterSpacing: -0.03em
  takeaway:
    fontFamily: Geist
    fontWeight: 500
    fontSize: clamp(22px, 2.6vw, 30px)
    lineHeight: 1.3
    letterSpacing: -0.02em
  numeral:
    fontFamily: Geist
    fontWeight: 300
    fontSize: 56px
    lineHeight: 0.9
    letterSpacing: -0.04em
  body:
    fontFamily: Geist
    fontSize: 17px
    lineHeight: 1.6
  body-zh:
    fontFamily: Noto Sans TC
    fontSize: 16.5px
    lineHeight: 1.8
    letterSpacing: 0.03em
  label:
    fontFamily: Geist
    fontWeight: 500
    fontSize: 14px
    lineHeight: 1.4
  button:
    fontFamily: Geist
    fontWeight: 600
    fontSize: 16px
    letterSpacing: -0.005em
  mono:
    fontFamily: Geist Mono
    fontWeight: 500
    fontSize: 11.5px
    letterSpacing: 0.08em
    fontFeature: tnum
rounded:
  sm: 2px
  full: 9999px
spacing:
  2xs: 2px
  xs: 4px
  sm: 8px
  md: 12px
  base: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px
  4xl: 96px
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-ink}"
    rounded: "{rounded.sm}"
    height: 48px
    padding: 0 24px
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  button-secondary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.sm}"
  input:
    backgroundColor: "{colors.paper-raised}"
    borderColor: "{colors.rule}"
    rounded: "{rounded.sm}"
    height: 48px
---

# Daily Digest

## Overview

**Creative North Star:** Swiss Modern made plain. Strict grid, one sans family, near-white paper, and a single seal-red action, so a first-time visitor knows what to do without reading instructions.

**Product context:** An AI news briefing. It pulls headlines from Google News / RSS (BBC, Guardian, NYT, WSJ, CNN...) by topic and city, and an LLM writes "Things to Watch Today" plus a one-line "Take Away" in English and Traditional Chinese (繁體中文). For bilingual EN/中文 readers who want a fast daily briefing; also a portfolio piece. Peers: Semafor, Axios, FT, Particle, The Browser. Web app with a reading-first home page (`public/index.html`) and three utility pages (`account.html`, `preferences.html`, `notifications.html`).

**What people should remember:** it is clean and obvious to use. Every simplification decision serves that first.

**Mode per surface:**
- Home, edition form: Operate. Labeled fields, one clear button.
- Home, digest: Read. Parallel EN / 中文, generous line-height.
- Back Issues, Dispatches, Settings: Operate, compact.

**Reference sites:** semafor.com, particle.news, thebrowser.com, ft.com (researched 2026-11-08).

**Key characteristics:**
- Near-white paper, black ink, and red used only for the one primary action and the key-point numerals.
- English and 中文 aligned point by point in the digest.
- Plain labels in sentence case. No decorative metaphors in UI copy.
- No cards, shadows, gradients or emoji. Typography and 1px rules do the work.

**Approved previews:**
- 2026-11-12 simplification: `~/.gstack/projects/new_summary/designs/design-system-20261112/preview.html` (簡化版, button 「產生今日摘要」, 標準欄位, 印章紅).
- 2026-11-08 original system: `~/.gstack/projects/new_summary/designs/design-system-20261108/preview.html`.

## Colors

**Strategy:** Restrained. Ink, paper and one red. Red appears only on the primary button, key-point numerals, the Take Away label, the unread dot and link-hover underlines. One red element per screen region, so the primary button is always the loudest thing on the form.

**Light or dark:** Light by default (people read this in the morning, often on a phone in daylight). Night edition follows `prefers-color-scheme` on first load and a toggle after that.

| Role | Light | Dark |
|------|-------|------|
| Page background | `paper` | `dark-paper` |
| Inputs, alerts | `paper-raised` | `dark-paper-raised` |
| Primary text | `ink` | `dark-ink` |
| Labels, secondary text | `ink-2` | `dark-ink-2` |
| Muted metadata only (about 3.3:1, never body text) | `ink-3` | `dark-ink-3` |
| Hairlines | `rule` | `dark-rule` |
| Section rules | `rule-strong` (= ink) | `dark-ink` |
| Primary button, numerals | `accent` (4.8:1 on paper) | `dark-accent` (6.5:1) |
| Primary button hover | `accent-hover` | `dark-accent-hover` |
| Text on the primary button | `accent-ink` | `dark-accent-ink` |
| Selection, focused field | `wash` | `dark-wash` |

- **Errors do not use red.** Red is the brand and the primary action. Errors use ink text, a 5px double left rule, and a "✕ Error" label. Invalid inputs get a 2px ink bottom border plus a message under the field.
- **Dark mode** is redesigned, not inverted: neutral near-black paper, warm off-white ink, a brighter red to keep contrast.

## Typography

- **Geist** for everything Latin: nameplate, headings, body, labels and buttons. Kept from 2026-11-08. Geist is a very common face right now, so it gives the page less personality as a display voice; the user chose to keep it because this round simplifies rather than restyles.
- **Noto Sans TC** for all Chinese. It matches Geist's stroke and has the full Traditional set the backend generates. Always set `lang="zh-Hant"` on Chinese blocks.
- **Geist Mono** only for machine data: timestamps, source tags, the machine byline. Uppercase with +0.08em tracking. It is no longer used for form labels, column heads or buttons.
- **Loading:** `https://fonts.googleapis.com/css2?family=Geist:wght@300..700&family=Geist+Mono:wght@400..600&family=Noto+Sans+TC:wght@400;500;700&display=swap` (verified 2026-11-12: all three families served).
- **Stacks:** `"Geist", system-ui, sans-serif` · `"Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif` · `"Geist Mono", ui-monospace, monospace`.
- **Scale:** the `typography` tokens above. The nameplate is now 40–64px instead of 56–120px, so the form sits in the first screen.
- **CJK rule:** Chinese runs about 1–1.5px smaller than the paired English with more line-height (1.8 vs 1.6) so the two columns look optically equal.

## Layout

- **Grid:** 12 columns, max content width 1240px; side gutters 16px (mobile), 40px (≥720px). Left-aligned; nothing centered.
- **Edition form:** one row at ≥900px: Topic | Location | Source | button (`1.2fr 1.2fr 1fr auto`, 16px gap, bottom-aligned). Two columns with a full-width button at 720–899px. One column below 720px. "Detect my location" and "Save preferences" sit under the row as underlined text links.
- **Digest key points:** at ≥900px each point is `56px | 1fr | 1fr` (numeral | English | 中文), 32px gaps, a 1px rule between rows. Below 900px: `52px | 1fr`, 中文 under English in `ink-2`.
- **The wire (source headlines):** two columns at ≥900px, one below, 1px rules between stories.
- **Top bar:** a plain dateline in Geist 14px `ink-2` on the left ("2026 年 11 月 12 日 · 星期四"), the account button on the right.
- **Page names:** Home, Back Issues (`preferences.html`), Dispatches (`notifications.html`), Settings (`account.html`).
- **Density:** comfortable on the digest (48–64px section padding), compact on utility pages (24px inside panels).
- **No horizontal scroll** at 390px width.

## Elevation & Depth

Flat. No shadows. Separation comes from 1px rules (`rule` between rows, `rule-strong` under section heads) and the `paper-raised` fill on inputs and alerts. The account menu is a `paper-raised` panel with a 1px `rule-strong` border.

## Shapes

- `sm` 2px: buttons, inputs, tabs, the account button, menus.
- `full`: unread dots, switch tracks, the loading spinner only.
- No other radii. The 6px seal radius is retired with the seal button.

## Components

- **Primary button (產生今日摘要 / Get today's digest):** `accent` fill, `accent-ink` text, Geist 16px 600, sentence case, 48px tall, 0 24px padding, 2px radius. No rotation, no inner ring.
  - Hover: `accent-hover` fill, 120ms.
  - Active: scale 0.98, 100ms.
  - Focus-visible: 2px `ink` outline, 2px offset.
  - Loading: disabled, `cursor: progress`, opacity 0.75, a 14px spinner before the text "產生中… / Generating…". The label returns when the digest renders or an error shows.
  - Copy lives in the `submit-btn` translation key: zh 「產生今日摘要」, en "Get today's digest". The `aria-label` follows the visible text.
- **Secondary button:** `ink` fill, `paper` text, same size and radius. **Outline:** transparent with a 1px ink border. **Text link:** underline, 4px offset.
- **Fields (edition form and utility pages):** label above in Geist 14px 500 `ink-2`, sentence case. Input 48px tall, `paper-raised` fill, 1px `rule` border with an `ink-2` bottom border, Geist 17px, 2px radius. Focus: 2px `accent` outline. Placeholder `ink-3`. Every field has a visible `<label for>`.
- **Alerts:** `paper-raised`, 3px left rule in the semantic color, label plus sentence.
- **Lists (Back Issues, Dispatches):** rows separated by 1px rules, metadata in mono on the right. Unread rows get a 6px `accent` dot.
- **Machine byline:** a mono strip between rules, e.g. `● COMPILED BY MACHINE · 06:42 CST · 14 DISPATCHES READ · GROQ · GPT-OSS-120B`.

## Do's and Don'ts

- Do write button text as the outcome the click buys ("產生今日摘要"), not a metaphor.
- Do give every input a visible label above it.
- Do keep exactly one red button per form.
- Do set `lang="zh-Hant"` on every Chinese block and keep EN / 中文 aligned point by point.
- Do design the loading and error states of the primary button.
- Don't bring back the rotated seal, "付印 / GO TO PRESS", or a sentence-shaped form.
- Don't use uppercase mono for labels, buttons or headings; it is for machine data only.
- Don't use red for errors.
- Don't add cards, shadows, gradients, emoji, or a kicker label above headings.
- Don't hide Chinese behind a toggle on the digest.

## Motion

- **Approach:** minimal-functional.
- **Easing:** enter `cubic-bezier(.2,.7,.2,1)`, exit ease-in, move ease-in-out.
- **Duration:** micro 100–120ms (button press, hover), short 150–250ms (theme, link underline, reveal).
- **The one authored moment:** when a digest arrives, key points reveal in order (fade from 0 plus a 2px rise, 220ms, 40ms stagger), replacing the skeleton.
- Link hover: a 1px accent underline grows left to right in 250ms.
- `prefers-reduced-motion: reduce`: no reveal animation, no spinner rotation.

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-11-08 | Initial design system created | /design-consultation from product context plus research on Semafor, FT, Particle and The Browser |
| 2026-11-08 | Swiss Modern chosen over Broadsheet, Book and Wire | User compared all four in a live preview and rejected the newspaper feel |
| 2026-11-08 | Parallel EN/中文 text and seal-red accent adopted | Makes the bilingual output the product's identity |
| 2026-11-08 | Blackletter nameplate rejected | Reads as newspaper pastiche |
| 2026-11-08 | Noto Sans TC (Traditional) for Chinese | Backend generates 繁體中文; a sans pairs with Geist |
| 2026-11-08 | Errors use ink and a double rule, not red | Keeps red exclusive to the brand |
| 2026-11-12 | Seal button "付印 / GO TO PRESS" replaced by a plain button "產生今日摘要 / Get today's digest" | User found the seal button unclear; the label now names what the click produces |
| 2026-11-12 | Sentence-form edition controls replaced by labeled fields | Memorable goal set to "clean, obvious to use"; first-time visitors should not guess which words are editable |
| 2026-11-12 | Nameplate reduced to 40–64px; uppercase mono limited to machine data | Simplification pass; the form now fits in the first screen |
| 2026-11-12 | Geist kept as display face despite being common | User chose to adjust, not restyle; tradeoff noted |
| 2026-11-12 | DESIGN.md converted to the spec format with front-matter tokens | Lets /design-review and QA check tokens mechanically |
