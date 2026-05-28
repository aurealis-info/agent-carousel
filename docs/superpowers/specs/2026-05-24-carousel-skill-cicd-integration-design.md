# Carousel skill → CI/CD integration

**Date:** 2026-05-24
**Status:** Approved

## Problem

The repo has two halves that don't yet meet:

1. **The CI/CD pipeline** (`.gitlab-ci.yml` + `scripts/render.js`) renders carousel slides
   to PNG and uploads them to Cloudflare R2. It only ever looks at `carousels/<slug>/`,
   reads a `metadata.json` from each folder, screenshots each listed slide, and uploads the
   PNGs plus `metadata.json` to R2.
2. **The cloud-agent skill** (`cloud-agent/*.md`) authors Instagram carousels as standalone
   HTML + a shared `deck.css`, but writes them to `cloud-agent/out/drafts/<slug>/` with a
   `metadata.json` of a completely different (editorial) shape, plus a separate `caption.txt`.

Nothing the skill produces today is in a location the pipeline watches, and the
`metadata.json` it writes is not the shape the pipeline reads. We are also carrying a mock
carousel (`carousels/mock-carousel-1/`) that was only built to bootstrap the pipeline, and a
Python PNG helper that the pipeline makes redundant.

## The pipeline contract (what `render.js` actually requires)

Derived by reading `scripts/render.js`:

- **Trigger / location:** only paths under `carousels/<name>/` are considered
  (`render.js:95`). Git diff of that folder is what selects which carousels render.
- **Gate:** a folder with no `metadata.json` is skipped (`render.js:113`).
- **Fields read from `metadata.json`:**
  - `dimensions.width` / `dimensions.height` → Playwright viewport (defaults 1080×1350,
    `render.js:130`).
  - `slides` → ordered array of HTML filenames to screenshot (`render.js:135`). **If absent,
    every `.html` in the folder is auto-scanned and rendered** (`render.js:139`) — which would
    wrongly screenshot `contact.html`.
- **Output:** each slide → `dist/<slug>/<basename>.png`; uploaded to R2 as
  `carousels/<slug>/<basename>.png` (`render.js:194`).
- **Sidecar:** the whole `metadata.json` is uploaded verbatim to `carousels/<slug>/metadata.json`
  (`render.js:256`). **It is the only non-PNG file uploaded** — anything not in `metadata.json`
  or a rendered PNG never reaches R2. (So `caption.txt` would not.)

`render.js` ignores any fields it doesn't recognize, so one `metadata.json` can serve both as
the render config and as the published metadata sidecar.

## Design

### 1. The `metadata.json` contract (the linchpin)

The skill writes one `metadata.json` per carousel that carries both the render config and the
editorial/publish metadata:

```json
{
  "title": "What a godly man does with anger",
  "slug": "2026-05-24-what-a-godly-man-does-with-anger",
  "caption": "Full Instagram caption text…\n\n#faith #discipline",
  "tags": ["faith", "discipline", "anger"],
  "pillar": "<from TOPICS.md>",
  "theme": "<one of the 10 themes>",
  "colorway": "dark",
  "dimensions": { "width": 1080, "height": 1350 },
  "slides": ["slide-01.html", "slide-02.html", "slide-03.html", "slide-04.html", "slide-05.html", "slide-06.html"]
}
```

- `dimensions` and `slides` are the only fields the pipeline reads.
- `slides` is **explicit and ordered**, and deliberately **omits `contact.html`** so the review
  grid is never rendered as a slide. This is the safety rail that replaces auto-scan.
- `slides` filenames must match the files on disk exactly (a listed-but-missing file is logged
  and skipped, `render.js:158`).
- `caption` is embedded here (no more `caption.txt`), so it travels to R2 via the existing
  metadata upload with **zero `render.js` changes**.

### 2. Skill output relocation

- The skill's working directory stays `cloud-agent/` — all its asset paths (`themes/`,
  `templates/`, the companion `.md` files) remain valid.
- The **deliverable** moves from `cloud-agent/out/drafts/<slug>/` to the repo-root
  `../carousels/<slug>/` — the only folder the pipeline watches. `INSTRUCTIONS.md` states the
  working directory explicitly so an autonomous agent cannot guess wrong.
- Final folder shape:

  ```
  carousels/<slug>/
    ├── slide-01.html        ← standalone, links to deck.css (hook)
    ├── slide-02.html … slide-NN.html   ← last is CTA
    ├── deck.css             ← themes/<colorway> + template.css, concatenated
    ├── contact.html         ← review grid (NOT in slides[]; not rendered/uploaded)
    └── metadata.json        ← the contract object above
  ```

- Slide filenames standardize on `slide-NN.html`; `slides[]` is the source of truth for order.

### 3. `render.js`

**No changes.** The caption-in-metadata decision keeps the pipeline code untouched.

### 4. Cleanup

- Delete `carousels/mock-carousel-1/` (the pipeline-bootstrap mock). Leaves `carousels/` empty
  and ready for real output; `render.js` handles a missing/empty `carousels/` gracefully.
- Delete `cloud-agent/bin/` (`render_slide.py` + `__pycache__`). The pipeline now renders all
  PNGs, so the skill no longer needs a PNG helper — reinforcing "skill emits HTML+CSS+metadata;
  pipeline renders."
- In `cloud-agent/out/drafts/*`: strip the rendered byproducts (`*.png`, `.__render__*.html`,
  `_verify-*.png` — 29 files). Keep each draft's `*.html`, `deck.css`, `caption.txt`,
  `copy.json`, `metadata.json`, and `themes/` as design references in their original location
  and (old) format.

### 5. Doc scrubs

- `DESIGN.md`: replace the `bin/render_slide.py` "optional PNG export" note with a note that
  PNGs are produced by the CI pipeline (`scripts/render.js`).
- `TOPICS.md`: the rotation note that says "look at the most recent draft in `out/drafts/`"
  becomes `../carousels/`.

## Out of scope / non-goals

- No change to brand voice, copy rules, design tokens, or layouts.
- No example/seed carousel is added to `carousels/` (avoids creating a new mock to clean up
  later). The contract is documented in `INSTRUCTIONS.md` instead.
- The example drafts' editorial `metadata.json`/`copy.json` are left as-is (reference only);
  they are not migrated to the new schema.

## Verification

- Static: confirm `metadata.json` schema matches the fields `render.js` reads; grep
  `cloud-agent/*.md` for stale `out/drafts`, `render_slide`, `caption.txt`.
- Dynamic (if the Node/Playwright toolchain is present locally): build a representative
  `carousels/<slug>/` from an example draft + a new-schema `metadata.json`, run
  `npm run render -- --dry-run --folder carousels/<slug>`, confirm one PNG per slide lands in
  `dist/<slug>/` and `contact.html` is **not** rendered, then delete the temp folder.
