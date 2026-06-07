# Template · 03 — annotated-notebook

A **second visual look for the TEACHING format** (`cloud-agent/formats/01-teaching.md`) — same copy structure (hook → numbered steps, one idea each + body), different style: a graph-paper grid, hand-drawn **gold** circle annotations, and gold "next" pills.

> Format ↔ template is **one-to-many**: a teaching deck can be built with `01-editorial-restrained` *or* this `03-annotated-notebook`. The `type_pairing_id` in `metadata.json` records which look produced the deck.

- **Colorway:** uniform — same `themes/brand-{dark,light}.css` tokens as every format. The grid uses `color-mix()` so it's faint on both dark and creme; gold annotations are `#D4B668` (identical both colorways).
- **Fonts (this template's identity):** **Lora** (serif — hook headline, step titles, closer question) + **Inter** (sans — eyebrow, step body). Overrides the theme's font tokens.
- **Build a deck:** `cat themes/brand-dark.css templates/03-annotated-notebook/template.css > ../carousels/<slug>/deck.css` (swap `brand-light.css` for creme).
- **Font link** for each slide's `<head>`:
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,500;0,600;0,700;1,500&display=swap" rel="stylesheet">
  ```

## Roles
- `<div class="slide hook">` — `.eyebrow` (brand/series, top-center) + `.hook-headline` (wrap one keyword in `<span class="circled">` for a gold marker-ring) + `.hook-sub` (uppercase sans).
- `<div class="slide step">` — `.eyebrow` + `<span class="step-num">01</span>` (auto gold ring) + `.step-title` (serif) + `.step-body` (sans). One idea per slide, per the teaching format.
- `<div class="slide closer">` *(optional)* — `.eyebrow` + `<span class="step-num">?</span>` + `.closer-q` (a reflective question + "save this"; no app mention). A teaching "closer" that drives saves/comments.

The "next" pill (`›`) is added automatically by CSS on hook + step slides. See `example/` for a complete deck.
