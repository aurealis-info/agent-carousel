# Template · 02 — editorial-list

The visual layout for the **list format** (`cloud-agent/formats/02-list.md`): a cover slide + numbered list slides.

- **Colorway:** uniform — uses the same `themes/brand-{dark,light}.css` tokens as every format. Only the type changes.
- **Handle / wordmark:** the cover eyebrow is the brand wordmark `ETHOS`; list-slide eyebrows use the IG handle `@theethosapp`. Keep `@theethosapp` uniform across every deck (only one account for now — `theethosapp`).
- **Fonts (this format's identity):** **Newsreader** (editorial serif — cover headline, items, glosses, italic parenthetical) + **Inter** (the small uppercase wordmark only). These override the theme's `--font-*` because the template's `:root` is concatenated after the theme's.
- **Build a deck:** `cat themes/brand-dark.css templates/02-editorial-list/template.css > ../carousels/<slug>/deck.css` (swap `brand-light.css` for creme).
- **Font link** for each slide's `<head>`:
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&display=swap" rel="stylesheet">
  ```

## Roles
- `<div class="slide cover">` — `.eyebrow` (brand) + `.cover-headline` (wrap the number in `<span class="num">`, which takes the accent colour) + `.cover-rule` + `.cover-sub` (the italic parenthetical).
- `<div class="slide list">` — `.eyebrow` + `<ol class="list-items">` of `.list-item`, each a `.line` (with `<span class="num">N.</span>`) + an optional `.gloss` (use `<span class="ref">` inside it for an italic Scripture reference).

See `example/` for a complete worked deck ("9 Places a Man Actually Meets God").
