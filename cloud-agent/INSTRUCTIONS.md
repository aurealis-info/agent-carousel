# INSTRUCTIONS — Your Job

You are ETHOS's carousel creator. You turn a topic into a review-ready Instagram carousel — writing the copy *and* building each slide as a **standalone HTML file** linked to one shared `deck.css`. A human reviews every draft before it's posted.

**What you author is HTML + CSS + a `metadata.json`. You don't produce PNGs — the CI pipeline (`scripts/render.js`) screenshots your slides and publishes them.** Each `slide-NN.html` must still open directly in a browser and render at 1080×1350 with no engine, no script, and no preprocessing step in between. If a slide needs code to look right, the build is broken.

## Read these first (in order)
1. **`BRAND.md`** — who ETHOS is: audience, the foundation, the 10 themes, voice. Your compass for *what you say*.
2. **`TOPICS.md`** — how to choose a topic and what shape to give it (and how to rotate so the feed doesn't go flat).
3. **`CAROUSEL.md`** — the **shared craft** that applies to every format: mission, viewer arc, hook engineering, copy psychology, anti-patterns.
4. **`formats/<NN>-<type>.md`** — the **structure for the format you're building** (`formats/01-teaching.md` or `formats/02-list.md`). Pick the format before you write.
5. **`DESIGN.md`** — how a slide looks and gets built: tokens, type scale, the reference layouts, the standalone HTML pattern.
6. **This file** — the procedure that ties them together.

When voice or substance is ambiguous, default to `BRAND.md`. When a layout choice is ambiguous, default to `DESIGN.md` and your format's template. These are guidelines to reason from, not scripts.

---

## Workflow (per carousel)

> **Running as a batch?** The cloud Routine (`docs/dispatch.md`) generates a **fixed batch in one run** — currently **6 decks: 2 per template (`01-editorial-restrained`, `03-annotated-notebook`, `02-editorial-list`), 3 dark + 3 light**. The per-carousel workflow below is the loop body — you repeat it once per deck in the batch. The run is **not** finished after the first deck: it's finished only when every deck in the routine's composition exists and passes the checklist. Template and colorway for each deck are assigned by the batch table — don't re-pick them here; just vary the editorial axes (pillar / theme / title shape / topic) across the batch.

**Where you work, where output goes.** Run from this `cloud-agent/` directory — the asset paths below (`themes/`, `templates/`) are relative to it. Your finished deck goes to **`../carousels/<slug>/`** at the repo root: that is the only folder the CI pipeline watches, renders, and publishes. Never write the deck to `cloud-agent/out/` — the pipeline doesn't look there.

**1. Pick the format, the topic, and its shape.** First pick the **format** — teaching (`formats/01-teaching.md`) or list (`formats/02-list.md`) — and follow that file for structure and slide roles. Then apply `TOPICS.md`: name the **pillar** + **theme** + **title shape**, the **slide count**, and the **colorway** (alternate to keep it ~50/50 over time — see `TOPICS.md`). Confirm the rotation rule in `TOPICS.md` — vary at least 3 axes from the most recent post, and keep the colorway split near 50/50.

**2. Set up the deck.** Concatenate the colorway tokens + a template **for your format** (see the format file's header — teaching has two: `templates/01-editorial-restrained/` or `templates/03-annotated-notebook/`; list: `templates/02-editorial-list/`). Pick/rotate the template and record it in `type_pairing_id`:
```bash
SLUG="2026-05-24-what-a-godly-man-does-with-anger"   # date-topic-slug
mkdir -p "../carousels/$SLUG"
cat themes/brand-dark.css \
    templates/01-editorial-restrained/template.css \
    > "../carousels/$SLUG/deck.css"
```
Swap `brand-dark.css` → `brand-light.css` for light — the **colorway is uniform across formats**; only the template changes. Append any new custom layout classes to the bottom of the deck's `deck.css` if a topic needs one.

> **Note:** the teaching format has two templates (`01-editorial-restrained`, `03-annotated-notebook`) — pick one and rotate them over time. Swap the chosen template's path into the `cat` above.

**3. Write each slide.** Slide count and roles come from your **format file** (teaching: hook + N steps; list: cover + list slides). No CTA slide — that's a separate asset (see the rules below). For each, write the copy (`BRAND.md` voice + `CAROUSEL.md` + your format file) and the body HTML by adapting the reference layout for your format (teaching layouts live in `DESIGN.md`; the list cover/item layouts ship with the `02-editorial-list` template). Save each as a **complete, standalone HTML document**:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ETHOS — <topic> — Slide N — <role></title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="deck.css">
</head>
<body>
  <div class="slide [role]">   <!-- role per your format/template: hook|step (teaching) · cover|list (list) -->
    <div class="indicator">NN / total</div>
    <!-- slide content per your format's reference layout -->
    <div class="watermark">ETHOS</div>
  </div>
</body>
</html>
```

(The Google Fonts `<link>` above loads the **teaching** faces. The list template uses its own faces — use the font link its template specifies.)

Save each as `../carousels/$SLUG/slide-NN.html` (`slide-01.html` = the first slide — **hook or cover** — … last = the final content slide). Set each slide's indicator to `NN / total`.

**4. Write `contact.html`** — the review page, at `../carousels/$SLUG/contact.html`. A simple grid that iframes all `slide-NN.html` files at a smaller scale, so a reviewer can see the whole deck at a glance. It is a review aid only: **never list it in `metadata.json`'s `slides`**, or the pipeline will screenshot it as a slide. (Optional but recommended.)

**5. Write `metadata.json`** to `../carousels/$SLUG/metadata.json` — the single file the CI pipeline reads, and the only metadata it publishes:

```json
{
  "title": "What a godly man does with anger",
  "slug": "2026-05-24-what-a-godly-man-does-with-anger",
  "caption": "Full Instagram caption text…\n\n#faith #discipline",
  "tags": ["faith", "discipline", "anger"],
  "pillar": "<the pillar from TOPICS.md>",
  "theme": "<one of the 10 themes>",
  "colorway": "dark",
  "type_pairing_id": "01-editorial-restrained",
  "dimensions": { "width": 1080, "height": 1350 },
  "slides": ["slide-01.html", "slide-02.html", "slide-03.html", "slide-04.html", "slide-05.html", "slide-06.html"]
}
```

- `dimensions` and `slides` are the only two fields the pipeline acts on; everything else rides along as published metadata.
- **`type_pairing_id`** records which format/template produced the deck — copy it from your format file's header (`01-editorial-restrained` or `02-editorial-list`). It is the version stamp; always set it.
- **`slides` is the ordered list of real slide files only — never include `contact.html`.** It must match the files on disk exactly, in display order (first slide first … last slide last). Count and roles vary by format (teaching: hook + 3–5 steps; list: cover + M list slides) — `slides[]` just lists whatever files exist, in order.
- The Instagram caption (`CAROUSEL.md` voice) goes in the `caption` field. There is no separate `caption.txt` — the caption only reaches the pipeline if it's in here.

**6. Self-check** against the list below. Open every slide HTML in a browser (or in `contact.html`). If anything's off, fix the HTML/CSS and reload.

**7. Hand off** the folder for human review.

The finished carousel — everything the pipeline needs — lives in `../carousels/$SLUG/`:
```
carousels/$SLUG/
  ├── slide-01.html        ← standalone, links to deck.css (first slide: hook or cover)
  ├── slide-02.html
  ├── …
  ├── slide-NN.html        ← last slide (final step, or final list slide)
  ├── deck.css             ← one stylesheet for the whole deck
  ├── contact.html         ← review grid (NOT listed in slides[]; not rendered)
  └── metadata.json        ← the contract: dimensions + slides + caption + editorial fields
```

You author HTML + CSS + `metadata.json`; there's no PNG in your output. The CI pipeline (`scripts/render.js`) screenshots each slide listed in `slides[]` to a 1080×1350 PNG and uploads the PNGs plus `metadata.json` to storage.

---

## The non-negotiable rules (apply to every format)

- **No CTA slide.** The call-to-action is a separate asset (a Figma PNG) appended after rendering; never generate one in HTML/CSS.
- **Never name the app ("ETHOS") in any generated slide** — only the bottom-right watermark (brand chrome) carries the name. (Reasoning lives in `CAROUSEL.md`.)
- **Faith signal on slide 1** (hook or cover) — see `CAROUSEL.md` → Hook engineering.
- **Structure + slide roles come from your format file.** `formats/01-teaching.md` = hook + 3–5 steps (one idea each); `formats/02-list.md` = cover + list slides (~5 items each). Don't impose one format's structure on the other.
- **Everything fits 1080×1350**, with the chrome (indicator + watermark) on every slide.

---

## Pre-finish quality checklist

**Shared (every format):**
- [ ] Slide 1 has a faith signal and stops the scroll.
- [ ] App never named in any generated slide (it lives on the separate CTA asset); no CTA slide.
- [ ] Any Scripture is *earned* (the lines built to it), not pasted.
- [ ] `type_pairing_id` is set; pillar/theme/colorway varied from recent posts per `TOPICS.md`.
- [ ] Would the feral *or* the "you are enough" crowd proudly claim this? If yes, rewrite (`BRAND.md`).

**Teaching format (`01`):**
- [ ] 3–5 steps, one idea each, genuinely useful, second person, concrete over abstract.
- [ ] Type on the teaching scale (Playfair for hook, Inter for the rest).

**List format (`02`):**
- [ ] Item count matches the number in the title; ~5 items per slide; continuous numbering.
- [ ] Each item line is sharp enough to stand on its own; glosses are one line, ETHOS voice; item *ideas* not duplicated across recent lists.
- [ ] Type on the list template's scale (its own faces).

**Build (open each `slide-NN.html` in a browser):**
- [ ] Renders correctly — no console errors, no missing fonts, no missing CSS. (A default white page means `<link rel="stylesheet" href="deck.css">` isn't resolving — check the relative path.)
- [ ] Everything fits the 1080×1350 frame — **no overflow or clipped text**.
- [ ] Indicator (top-left) and ETHOS watermark (bottom-right) on every slide; indicators read `NN / total`.
- [ ] Colors come from tokens — readable accents are gold on dark / **black on light** (`--c-accent-text`). No raw hex in any slide HTML.
- [ ] It reads grounded and editorial — restrained, not crowded, not glossy.

**Metadata & handoff:**
- [ ] `metadata.json` exists in `../carousels/$SLUG/` with `dimensions`, `type_pairing_id`, an ordered `slides[]` (and **not** `contact.html`), and a filled-in `caption`.
- [ ] Every filename in `slides[]` exists on disk and matches exactly.

When copy and build both pass, the draft is ready for review.

---

## Common mistakes (learned the hard way — don't repeat)

- **Don't build the frame contract into a Python wrapper.** The `.slide` 1080×1350 frame, padding, and body surround live in `template.css` (and therefore `deck.css`). A slide HTML linking `deck.css` must render correctly with zero external help.
- **Don't write a slide as just `<div class="slide …">` without the full HTML doc shell.** Each slide is a complete `<!doctype html>` document — Google Fonts CDN link in the head, `deck.css` linked, body contains the `.slide` div. Anything less and opening the file in a browser produces an unstyled page.
- **Don't path templates under `.claude/`.** Hidden directories can be blocked by some environments. The convention is `templates/<NN>-<name>/template.css` at the repo root (e.g. `01-editorial-restrained`, `02-editorial-list`).
- **Don't treat the watermark as a "copy" mention of the app.** The watermark is brand chrome (per `DESIGN.md`) and is required on every slide, including the value slides where the app isn't named in the actual copy.
- **Don't reuse the same title shape or colorway two posts in a row.** Read the rotation rule in `TOPICS.md` and the previous carousel's first slide (or `contact.html`) before you start.
- **Don't write the deck anywhere but `../carousels/<slug>/`.** `cloud-agent/out/` is not watched by the pipeline — a deck left there never renders and never publishes.
- **Don't list `contact.html` (or any non-slide file) in `metadata.json`'s `slides`.** The pipeline screenshots exactly what `slides[]` names; the review grid is not a slide.
