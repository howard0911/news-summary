# Design System — Daily Digest

## Product Context
- **What this is:** An AI news briefing. It pulls headlines from Google News / RSS (BBC, Guardian, NYT, WSJ, CNN...) by topic and city, and an LLM writes "Things to Watch Today" plus a one-line "Take Away" in English and Traditional Chinese (繁體中文).
- **Who it's for:** Bilingual EN/中文 readers who want a fast daily briefing. Built as a portfolio piece, so craft and a memorable identity matter.
- **Space/industry:** News briefings and AI news readers (peers: Semafor, Axios, FT, Particle, The Browser).
- **Project type:** Web app with a reading-first home page (`public/index.html`) and three utility pages (`account.html`, `preferences.html`, `notifications.html`).

## Aesthetic Direction
- **Direction:** Swiss Modern. Strict grid, confident sans-serif type, near-white paper, one vermilion accent.
- **Decoration level:** Minimal. Typography and 1px rules do all the work. No cards, no shadows, no gradients, no emoji in headings.
- **Mood:** Calm, precise, quietly confident. The first impression should be "someone set this for me this morning", not "a dashboard".
- **Identity moves (approved):**
  1. **Parallel bilingual text.** English and 中文 are set side by side and aligned point-by-point (key point 2 sits level with 要點 2). Below 900px they interleave: EN paragraph, then 中文 paragraph. Never hide Chinese behind a toggle on the digest.
  2. **Seal red (印章紅).** Vermilion is the only accent color, and the primary action is a seal-shaped "付印 / Go to press" button.
  3. **The form is a sentence.** The edition controls read as one line: "The **Technology** edition, for **Chicago**, from **BBC · Guardian · NYT**." Each bold word is an inline field.
- **Rejected:** Broadsheet/newspaper styling (serif mastheads, double rules, cream paper) and a blackletter nameplate.
- **Reference sites:** semafor.com, particle.news, thebrowser.com, ft.com (researched 2026-11-08).
- **Approved preview:** `~/.gstack/projects/new_summary/designs/design-system-20261108/preview.html` (direction "Swiss 現代", preset "Recommended").

## Typography
- **Display / Headlines / Body:** **Geist**. A neutral grotesk with tight, confident display weights. One family keeps the Swiss look disciplined.
- **Chinese (Traditional):** **Noto Sans TC**. A sans to match Geist's stroke, readable at body sizes, and a full Traditional glyph set (the backend generates 繁體中文).
- **UI labels / Wire layer:** **Geist Mono**, uppercase. Used for anything the machine produced or measured: datelines, source tags, timestamps, form labels, the machine byline, status labels.
- **Data / Tables:** Geist with `font-variant-numeric: tabular-nums`.
- **Code:** Geist Mono.
- **Loading:** Google Fonts:
  `https://fonts.googleapis.com/css2?family=Geist:wght@300..700&family=Geist+Mono:wght@400..600&family=Noto+Sans+TC:wght@400;500;700&display=swap`
- **Font stacks:**
  - `--f-sans: "Geist", system-ui, sans-serif`
  - `--f-zh: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif`
  - `--f-mono: "Geist Mono", ui-monospace, monospace`
- **Scale:**

| Role | Font | Size / line-height | Weight | Tracking |
|------|------|--------------------|--------|----------|
| Nameplate | Geist | clamp(56px, 10vw, 120px) / 0.92 | 650 | -0.055em |
| Edition sentence | Geist | clamp(26px, 3.6vw, 40px) / 1.3 | 400 (fields 600) | -0.02em |
| H2 section | Geist | clamp(30px, 4vw, 44px) / 1.1 | 600 | -0.03em |
| Take Away quote | Geist | clamp(24px, 2.8vw, 32px) / 1.3 | 500 | -0.02em |
| Key-point numeral | Geist | 56px desktop, 44px mobile / 0.9 | 300 | -0.04em |
| Story headline | Geist | 18px / 1.3 | 500 | -0.01em |
| Body (EN) | Geist | 17–18px / 1.6, max 62ch | 400 | 0 |
| Body (中文) | Noto Sans TC | 16.5px / 1.8 | 400 | +0.03em |
| 中文 heading | Noto Sans TC | 0.8× the paired EN heading | 700 | 0 |
| Wire / labels | Geist Mono | 11.5px / 1.4, uppercase | 500 | +0.08em |

- **CJK rules:** Chinese runs about 1–1.5px smaller than the paired English and gets more line-height (1.8 vs 1.6) so the two columns look optically equal. Always set `lang="zh-Hant"` on Chinese blocks.

## Color
- **Approach:** Restrained. Ink, paper, and one red. The accent appears in only a few places per page: key-point numerals, the 付印 button, edition-field underlines, kicker labels, the unread dot, link hover underlines.

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `--paper` | `#FAFAF7` | `#111214` | Page background |
| `--paper-raised` | `#FFFFFF` | `#18191C` | Inputs, alerts |
| `--ink` | `#111111` | `#EDEDEA` | Primary text, primary buttons |
| `--ink-2` | `#5F5F5B` | `#9A9A94` | Secondary text, labels |
| `--ink-3` | `#8C8C86` | `#6E6E69` | Muted metadata only (not body text, about 3.3:1) |
| `--rule` | `#E4E4DF` | `#2A2B2F` | Hairlines between rows |
| `--rule-strong` | `#111111` | `#EDEDEA` | Section rules, column-head underline |
| `--accent` (seal red) | `#C2361C` | `#FF6A4A` | Brand accent (4.8:1 on light paper, 6.5:1 on dark) |
| `--accent-ink` | `#F8F7F3` | `#111214` | Text on the seal button |
| `--wash` | `#FBE4DC` | `#2B1A16` | Selection, focused inline field |
| `--success` | `#2F6B3F` | `#6FBF82` | Saved / done |
| `--warning` | `#8A5A00` | `#E0B050` | Slow / degraded |
| `--info` | `#1F3A5F` | `#8FB3E0` | Notes |

- **Errors do not use red.** Red is the brand. Errors use `--ink` text, a 5px double left rule, and a mono "✕ Error" / "✕ Failed" label. Invalid inputs get a 2px ink bottom border plus a message.
- **Dark mode ("Night edition"):** Redesigned surfaces, not inverted. Neutral near-black paper, warm off-white ink, and a brighter red to keep contrast. Toggle with a class on `<html>`; respect `prefers-color-scheme` on first load.

## Spacing
- **Base unit:** 4px.
- **Density:** Comfortable on the digest, compact on utility pages.
- **Scale:** 2xs(2) xs(4) sm(8) md(12) base(16) lg(24) xl(32) 2xl(48) 3xl(64) 4xl(96)
- Section padding: 48–64px vertical on the digest; 24px inside utility panels.

## Layout
- **Approach:** Grid-disciplined, left-aligned. Nothing centered except the seal button's own label.
- **Grid:** 12 columns, max content width 1240px; side gutters 16px (mobile), 40px (≥720px).
- **Digest key points:** at ≥900px each point is a row of `56px | 1fr | 1fr` (numeral | English | 中文) with 32px gaps and a 1px rule between rows. Below 900px: `52px | 1fr` (a 44px numeral needs the width) with 中文 under English in `--ink-2`.
- **The wire (source headlines):** two columns at ≥900px, one below, 1px rules between stories, mono source tag and time above each headline.
- **Edition controls:** sentence on the left; the seal button sits bottom-right of the same row on desktop and below the sentence on mobile.
- **Machine byline:** a mono strip between rules, e.g. `● COMPILED BY MACHINE · 06:42 CST · 14 DISPATCHES READ · GROQ · LLAMA-3.1-8B`.
- **Page names:** Home, Back Issues (`preferences.html`), Dispatches (`notifications.html`), Settings (`account.html`).
- **Border radius:**
  - `sm`: 2px for buttons, inputs, tabs
  - `seal`: 6px, for the 付印 button only
  - `full`: 9999px, for unread dots and switch tracks only
  - No other radii.
- **No horizontal scroll** at 390px width.

## Components
- **Primary button:** `--ink` fill, `--paper` text, Geist Mono 12px uppercase +0.1em, padding 14×20, radius 2px.
- **Secondary:** transparent with a 1px ink border. **Ghost:** text with underline (offset 4px).
- **Seal button (付印 / Go to press):** 112×112px, `--accent` fill, `--accent-ink` text, inner double ring (`inset 0 0 0 3px accent, inset 0 0 0 5px accent-ink`), rotated -3deg. Noto Sans TC 700 28px "付印" over mono "GO TO PRESS". Hover scales to 1.03 and press to 0.97, keeping the rotation.
- **Sentence fields:** inherit the sentence font, weight 600, 2px `--accent` bottom border, `field-sizing: content`. Focus shows a `--wash` background. Every field needs an `aria-label`.
- **Inputs (utility pages):** `--paper-raised` fill, 1px `--rule` border with an `--ink-2` bottom border, Geist 17px, mono uppercase label above. Focus outline is 2px `--accent`.
- **Alerts:** `--paper-raised`, 3px left rule in the semantic color, mono label + sentence.
- **Lists (Back Issues, Dispatches):** rows separated by 1px rules, with mono metadata on the right. Unread rows get a 6px `--accent` dot.

## Motion
- **Approach:** Minimal-functional, with one signature moment.
- **Press run:** when a digest is generated, the key points reveal in order: fade from 0 plus a 2px rise, 220ms, 40ms stagger. It replaces the skeleton loader.
- **Easing:** enter `cubic-bezier(.2,.7,.2,1)`; exit ease-in; move ease-in-out.
- **Duration:** micro 100–120ms (button press), short 150–250ms (theme, hover underlines, reveal).
- Link hover: a 1px accent underline grows left to right in 250ms.
- Respect `prefers-reduced-motion: reduce`: no reveal animation.

## Implementation Notes
- The parallel layout needs both languages for every digest. `generate_takeaway()` in `backend/app.py` currently produces one language per call (`lang="zh"` or English), so it must return both, either as two calls or as one bilingual prompt.
- Replace the current Inter + `#6366f1` indigo tokens in all four `public/*.html` files with the tokens above, and remove the 📰 emoji from the H1.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-11-08 | Initial design system created | Created by /design-consultation from product context plus research on Semafor, FT, Particle and The Browser |
| 2026-11-08 | Swiss Modern direction chosen over Broadsheet, Book and Wire | User compared all four in a live preview and rejected the newspaper feel |
| 2026-11-08 | Parallel EN/中文 text, seal-red accent, sentence-form controls adopted | Makes the bilingual output the product's identity; no AI news reader does parallel text |
| 2026-11-08 | Blackletter nameplate rejected | Reads as newspaper pastiche |
| 2026-11-08 | Noto Sans TC (Traditional) for Chinese | Backend generates 繁體中文; a sans pairs with Geist |
| 2026-11-08 | Errors use ink and a double rule, not red | Keeps red exclusive to the brand |
