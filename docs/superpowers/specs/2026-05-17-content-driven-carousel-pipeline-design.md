# Content-Driven Carousel Pipeline — Design Spec

**Date:** 2026-05-17
**Status:** Draft — pending review
**Supersedes:** Current `strategist → designer → critic` pipeline in `aurealis_carousel/`

---

## 1. Problem statement

The current carousel pipeline produces output that feels flat across every dimension the user evaluated:
- Topics feel safe and predictable.
- Hooks read as formulaic.
- Full narratives feel like AI summaries rather than human-with-skin-in-the-game writing.
- Visuals look the same carousel-to-carousel because every brand has fixed CSS tokens and a default type pairing.

The root cause is two-fold:

1. **Single-shot creative authorship.** The strategist makes the entire creative decision in one Claude call, then the designer renders within fixed brand constraints. The model collapses to mode early.
2. **Brand identity is encoded as configuration rather than context.** `brand.css` prescribes exact hex values; the brief lists allowed pairings. Each carousel uses the same look because the look is hard-coded, not derived.

## 2. Goals

- Make carousels *interesting*: distinct topics, hooks that stop the thumb, narratives with voice, visuals that vary per piece.
- Co-conceive copy and visual treatment in the same creative act (one writer chooses the hook word *knowing how it will be set*).
- Derive styling from brand context per-carousel rather than applying a fixed brand template.
- Preserve brand recognition across carousels through context references, not enforcement.
- Keep cost in the same order of magnitude as the current pipeline.

## 3. Non-goals

- Per-slide creative authorship by a separate art director (rejected — single creative center is the architectural choice).
- Hard-enforced allowlists for fonts, colors, or banned phrases (rejected — pure prose context, judgment-based).
- Open-ended iteration on visual critique (capped at 2 revision rounds — bounded cost).
- Multi-user collaboration / web UI / production deployment beyond the existing CLI.

## 4. Architecture overview

Five components, executed in sequence with one bounded loop at the end:

```
BRAND BRIEF (prose) + recent topic slugs + recent visual references
        |
        v
+--------------------------+
| 1. ANGLE GENERATOR       |  ONE Claude call -> JSON array of 10 angles
+--------------------------+
        |
        v
+--------------------------+
| 2. ANGLE CRITIC          |  ONE Claude call -> winning_index + reasoning
+--------------------------+
        |
        v
+--------------------------+
| 3. SCRIPT + STYLE WRITER |  ONE Claude call -> full blueprint JSON:
|   (the creative center)  |    per-slide copy + invented hex palette
|                          |    + chosen type pairing + per-slide
|                          |    layout move + hero-word treatment
+--------------------------+
        |
        v
+--------------------------+
| 4. DESIGNER (compiler)   |  N Claude calls -> HTML per slide
+--------------------------+
        |
        v
+--------------------------+
| 5. VISUAL CRITIC --------+  ONE multimodal Claude call -> SHIP | REVISE
+--------+-----------------+
         | REVISE
         +------> Designer re-renders flagged slides (max 2 rounds)
```

All five components use Claude Opus. Per-carousel cost: ~$4.90 (vs ~$3-4 today).

## 5. Components

### 5.1 Angle Generator (`aurealis_carousel/angles.py`)

**Inputs:** full brand brief, hooks + voice playbook excerpts, recent 14 topic slugs from history, optional user topic hint.

**Output:** JSON array of 10 angles. Each angle is a short object:
```json
{
  "topic": "...",
  "topic_slug": "kebab-case",
  "hook_intent": "...",        // a sentence describing the hook angle, not the literal hook
  "arc_thesis": "...",
  "frame": "PAS|BAB|AIDA|principle-stack|reveal|story|ladder",
  "voice_mode": "guide|expert|storyteller",
  "emotional_register": "..."  // free-form: monumental, urgent, contemplative, etc.
}
```

**Prompt framing:** adversarial creative-director persona. Explicit instruction that no two angles should share a frame, voice mode, or emotional register. The 10 should pull from genuinely different drawers of the brand's repertoire.

**Validation:** valid JSON, array length >= 5 (accept) or retry once. No content validation — the angle critic is the next gate.

### 5.2 Angle Critic (`aurealis_carousel/angle_critic.py`)

**Inputs:** 10 angles, brand voice playbook, recent topic slugs.

**Output:**
```json
{ "winning_index": 0, "reasoning": "..." }
```

**Prompt framing:** carries forward the existing critic's "reject 80%" framing. Picks one winner and explains why; does not rewrite. Reasoning is logged for debugging — not used downstream.

**Validation:** winning_index is in `[0, len(angles))`. On failure, default to 0 and log.

### 5.3 Script + Style Writer (`aurealis_carousel/writer.py`)

**The creative center.** This is the call where prompt investment matters most.

**Inputs:**
- Winning angle (from angle critic)
- Full brand brief (prose)
- Font library (~25 pairings, each tagged with emotional register)
- All 6 playbook files
- 10-layout-moves guide (currently in `designer.py:19-78`, moved to a shared constant)
- Recent visual references: most recent 5 carousels' hook + climax PNGs from `history/<brand>/visual_refs/`
- Curated "golden" PNGs from `history/<brand>/golden/` (always included if present)

The reference images are passed as absolute paths; the writer is granted the `Read` tool to open them as images. This is the counter-drift mechanism.

**Output:**
```json
{
  "topic": "...",
  "topic_slug": "kebab-case",
  "frame": "...",
  "voice_mode": "...",
  "pairing_id": "cinzel-josefin",      // must exist in fonts/library.yaml
  "palette": {
    "bg": "#0A0A0A",
    "text": "#F0E6D6",
    "accent": "#A67C2E",
    "accent_alt": "#C4501A"            // optional, may be omitted
  },
  "slides": [
    {
      "i": 1,
      "type": "hook|body|climax|cta|bridge",
      "headline": "...",
      "body": "...",
      "label": "...",
      "hero_word": "GOVERNED",          // optional; word to receive emphasis
      "layout_move": "MEGA-WORD REST",  // one of the 10 named moves
      "hero_word_treatment": {
        "italic": true,
        "color_shift": "accent",
        "scale_shift": "mega",
        "weight_shift": null,
        "family_shift": null
      },
      "color_role": "bg=palette.bg, accent_on=hero_word",
      "inverted": false                 // true = palette.text becomes bg, palette.bg becomes text
    },
    ...
  ],
  "caption": {
    "first_125_chars": "...",
    "full": "...",
    "hashtags": ["#tag", ...]
  },
  "creative_notes": "Why this pairing, this palette, this hero-word treatment given the angle and the brand's visual register."
}
```

**Validation (mechanical, post-output):**
- Valid JSON.
- `pairing_id` exists in font library.
- `palette` colors all parse as hex.
- Contrast ratio between `palette.text` and `palette.bg` >= 4.5:1 (WCAG AA for body text).
- Hook headline (slide 1) <= 6 words.
- Hashtag count in brand's `hashtag_count_range`.
- Slide count in brand's `slide_count_range`.
- First and last slide types are `hook` and `cta`.
- CTA slide headline contains the app name (case-insensitive).
- Caption first 125 chars contains the trigram (first 3 content words) of the hook.
- Topic slug not in last 14 entries of `history/<brand>.yaml`.

**Retry policy:** one retry with specific violation feedback. No fallback — if the second attempt fails validation, raise. This is the creative anchor and bad output here invalidates the carousel.

### 5.4 Designer (`aurealis_carousel/designer.py`, slimmed)

**No more creative decisions.** Becomes a compiler from the writer's blueprint to renderable HTML.

**Inputs per slide:**
- The slide blueprint (from writer output)
- The carousel's pairing + palette
- The 10-layout-moves guide (for the grammar of each named move)

**Output:** HTML body fragment for one slide. The CSS variables are the writer-invented palette tokens, injected at render time.

**Palette -> CSS handoff:** A small helper (e.g. `writer.compile_css(palette, pairing) -> str`) generates the per-carousel CSS block from the writer's `palette` dict + `pairing_id`. The orchestrator writes that string to a temp file and passes the path to `render.render_slide(brand_css_path=...)` — preserving `render.py`'s current signature so it stays unchanged.

**Prompt framing:** "compile this blueprint into HTML using the named layout move. Use only the provided palette tokens. The blueprint already named the hero word and its treatment — apply that exactly."

**Validation:** the slimmed `token_validate.check` confirms HTML uses only the writer-provided palette CSS vars and the layout-move's expected class set. One retry on violation. Fallback to `_safe_minimal_html` after second failure (kept from current designer).

### 5.5 Visual Critic (`aurealis_carousel/critique.py`, expanded)

**Inputs:** rendered PNG paths (multimodal Read), winning angle, writer's `creative_notes`, all playbook files.

**Output:** same JSON shape as current critic, expanded:
```json
{
  "carousel_assessment": {
    "cohesion": "PASS|REVISE",
    "motif_consistency": "PASS|REVISE",
    "narrative_arc_clarity": "PASS|REVISE",
    "cta_bridge_effectiveness": "PASS|REVISE",
    "type_pairing_appropriateness": "PASS|REVISE",
    "palette_appropriateness": "PASS|REVISE",        // NEW
    "brand_recognizability": "PASS|REVISE",          // NEW — compared against visual_refs
    "creative_notes_honesty": "PASS|REVISE"          // NEW — does the writer's notes justify or backfill?
  },
  "subtraction_test_findings": "...",
  "peer_test_verdict": "PASS|REVISE",
  "algorithm_test_verdict": "PASS|REVISE",
  "per_slide": [ { "i": int, "verdict": "PASS|REVISE", "violations": [...] } ],
  "must_revise_slides": [int, ...],
  "overall_recommendation": "SHIP|REVISE"
}
```

**Revision loop:** max 2 rounds. Each round, the designer re-renders the slides in `must_revise_slides` and the critic is invoked again. After round 2, auto-ship best-effort and flag in `metadata.yaml.warnings` for human review.

## 6. Brand brief format

Single prose `brief` block + minimal numeric/operational config. No structured lists for voice attributes, banned words, color palettes, type-pairing allowlists, app-surfaces taxonomy, or variety rules — all of that goes into the prose.

```yaml
brand_name: ETHOS
app_name: ETHOS

brief: |
  [Multi-paragraph creative brief covering: product elevator pitch; reader
  psychology; voice register; voice anti-patterns; lines the brand never
  crosses; visual register and visual don'ts; CTA bridge and app surfaces;
  carousel norms.]

slide_count_range: [5, 6]
hashtag_count_range: [8, 12]
content_guidelines_files:
  - marketing/guidelines/GENERAL_CONTENT_GUIDELINES
  - marketing/guidelines/CAROUSEL/guidelines.md
```

See `brands/ethos/brief.yaml` after migration for a full example (drafted in the brainstorming transcript).

## 7. Font library expansion

`fonts/library.yaml` grows from 6 pairings to ~20-25, sourced from the Canva pairings reference + existing entries. Each entry adds an `emotional_register` tag the writer uses to map brief context to pairing choice.

Example tagged entries:
```yaml
- id: cinzel-josefin
  emotional_register: monumental
  pairs_well_with: [faith, scripture, history, ceremony, architecture]
  vibe: "Roman engraved-in-stone authority. Josefin for the modern body."

- id: bebas-roboto
  emotional_register: urgent-compressed
  pairs_well_with: [sports, gaming, fitness, news, alarm]
  vibe: "Condensed caps shout. Roboto carries the explanation."

- id: source-serif-source-sans
  emotional_register: instructional
  pairs_well_with: [technical, governance, protocol, education, finance]
  vibe: "Editorial-grade serif + matched humanist sans. Governed."
```

The full ~25-entry list is part of implementation, not this spec. Grouping principle: cover the emotional range monumental / urgent / contemplative / kinetic / editorial / instructional / sermon / rebellious / classic-editorial / tribal.

## 8. Counter-drift mechanism: visual references

The single most important non-architectural feature.

**On every accepted carousel** (visual critic returns SHIP or hits the round-2 cap), `persist.py` copies the rendered hook slide and climax slide PNGs to:
```
history/<brand>/visual_refs/<YYYY-MM-DD-topic-slug>/
  slide-01.png
  slide-NN.png      // the climax slide, by index
```

**On every Script + Style Writer call**, the orchestrator collects:
- The 5 most recent `visual_refs/*/` directories' PNGs (~10 images total).
- All PNGs in `history/<brand>/golden/` (human-curated platonic examples; optional).

These paths are passed to the writer, granted Read access, with the instruction:
> "Open these images. They show how this brand has looked in recent carousels. Your style choices should be recognizably from the same brand family — same temperature, gravity, restraint level. You may shift register to serve the topic, but the carousel should not look like it came from a different brand."

**Bootstrap:** first ~5 carousels have no `visual_refs/`. Writer prompt gracefully degrades — relies on `brief` prose alone. Drift correction kicks in automatically as the brand accumulates references.

**Token cost:** ~$0.20-0.40 added to the Writer call (multimodal images are expensive). Already baked into the $4.90 estimate.

## 9. Cost analysis

Per carousel, Opus everywhere:

| Step | Model | Calls | Estimated cost |
|---|---|---|---|
| Angle Generator | Opus | 1 | ~$0.30 |
| Angle Critic | Opus | 1 | ~$0.20 |
| Script + Style Writer | Opus | 1 (multimodal) | ~$1.00 |
| Designer | Opus | 5-7 (one per slide) | ~$1.40 |
| Visual Critic | Opus | 1 (multimodal) | ~$1.40 |
| Revision Designer passes | Opus | up to 6 (2 rounds × ~3 flagged slides) | ~$0.60 |
| **Total** | | | **~$4.90** |

Comparison: current pipeline runs ~$3-4 per carousel. New architecture is ~1.5× current cost. The user explicitly chose Opus for every step over the cheaper Haiku/Sonnet split.

## 10. Code changes (file-by-file)

```
aurealis_carousel/
├── claude_cli.py            UNCHANGED
├── cli.py                   UNCHANGED  (entry stays --brand <name>)
├── orchestrator.py          REWRITTEN  (5-step pipeline + revision loop)
├── strategist.py            DELETED    (replaced by angles + writer)
├── angles.py                NEW        (Section 5.1)
├── angle_critic.py          NEW        (Section 5.2)
├── writer.py                NEW        (Section 5.3)
├── designer.py              SLIMMED    (compiler only; 10-moves constant
│                                       moved to shared module)
├── critique.py              EXPANDED   (Section 5.5: new judgment axes,
│                                       revision-loop interface)
├── render.py                UNCHANGED  (HTML + tokens -> PNG)
├── font_faces.py            UNCHANGED  (Google Fonts URL builder)
├── layout_check.py          UNCHANGED  (post-render geometry check)
├── token_validate.py        REWORKED   (validates writer-output palette
│                                       contrast + a11y; no fixed allowlist)
└── persist.py               MODIFIED   (saves hook + climax PNGs to
                                        history/<brand>/visual_refs/)

brands/
├── ethos/
│   ├── brief.yaml           MODIFIED   (prose brief + 3 config fields)
│   └── brand.css            DELETED
├── lokin/                   SAME treatment
└── _test/                   SAME treatment (first to migrate; smoke testbed)

fonts/
└── library.yaml             EXPANDED   (6 -> ~25 pairings, register-tagged)

history/
├── <brand>.yaml             UNCHANGED  (slug + meta per carousel)
└── <brand>/                 NEW DIR
    ├── visual_refs/         AUTO-POPULATED  (recent carousels' hook + climax PNGs)
    └── golden/              MANUAL  (human-curated platonic examples; optional)
```

Shared 10-layout-moves constant: extract from `designer.py:19-78` into a new module (e.g. `aurealis_carousel/layout_moves.py`) imported by both `writer.py` (to make the menu visible to the writer) and `designer.py` (to compile each move's grammar).

## 11. Migration plan (strangler-fig, 4 phases)

**Phase 1 — Build alongside.** New files (`angles.py`, `angle_critic.py`, `writer.py`, `layout_moves.py`, `orchestrator_v2.py`) added. CLI gains a `--v2` flag. `strategist.py` and existing pipeline untouched. New code is reachable only when `--v2` is passed.

**Phase 2 — Test brand first.** Convert `brands/_test/brief.yaml` to the new prose format. Run 5-10 carousels via `--v2 --brand _test`. Iterate on the Script+Style Writer prompt until output quality is consistently above current baseline.

**Phase 3 — Production brand A/B.** Convert `brands/ethos/brief.yaml`. Delete `brands/ethos/brand.css`. Run 5-10 carousels via `--v2 --brand ethos`. Render the same 5 topics via both v1 (current) and v2 (new); compare side-by-side. Stakeholder review before promoting.

**Phase 4 — Promote and clean up.** Convert remaining brands (`lokin`). Rename `orchestrator_v2.py` -> `orchestrator.py`. Delete `strategist.py`. Delete remaining `brand.css` files. Remove `--v2` CLI flag. Update README.

## 12. Error handling

| Step | Failure | Response |
|---|---|---|
| Angle Generator | Invalid JSON | One retry with structured feedback |
| Angle Generator | <5 angles | Retry once; if still <5, raise |
| Angle Critic | Invalid winning_index | One retry; fallback to index 0 on second failure |
| Script + Style Writer | Invalid JSON | One retry with structured feedback |
| Script + Style Writer | Palette contrast <4.5:1 | One retry with specific contrast values |
| Script + Style Writer | pairing_id not in library | One retry with the library menu re-emphasized |
| Script + Style Writer | Hashtag count outside range | One retry with range reminder |
| Script + Style Writer | Hook >6 words | One retry with word count |
| Script + Style Writer | Any other validation | One retry; raise on second failure |
| Designer | Empty HTML | One retry; fallback to `_safe_minimal_html` |
| Designer | Token validator failure | One retry with violations; fallback after |
| Render | Playwright/browser crash | Surface immediately; no retry |
| Layout Check | Geometry violation | Warning only (matches current behavior) |
| Visual Critic | Invalid JSON | One retry; log + auto-ship on second failure |
| Visual Critic | Round-2 REVISE | Auto-ship best-effort; flag in `metadata.yaml.warnings` |

## 13. Edge cases

1. **Bootstrap brand with no `visual_refs/`** — Writer prompt skips the multimodal references block; relies on `brief` prose alone. Drift correction begins after ~3 accepted carousels.
2. **Brand with empty `golden/`** — Same handling; no failure.
3. **Font in chosen pairing fails to load via Google Fonts** — `font_faces.py` validates URL at build time (TODO: currently silent failure — fix as part of this work). Fallback to system serif/sans + warning.
4. **Writer invents a color the brief implicitly forbids** (e.g., neon pink for ETHOS) — Caught by visual critic's `palette_appropriateness` axis. Triggers revision.
5. **Writer's `creative_notes` are post-hoc rationalization** — Critic's `creative_notes_honesty` axis catches it.
6. **Two consecutive carousels look near-identical** — Not enforced upfront. Drift mechanism + critic should catch. If recurring, future enhancement: pass immediately-previous carousel's `pairing_id` + palette to writer with "pick something different unless the topic strongly calls for the same register."
7. **JSON parsing failures from Opus** — Inherited from `claude_cli.query_json()`: strips code fences, finds outermost braces, raises on failure.

## 14. Testing strategy

| Layer | Test type | Verifies |
|---|---|---|
| `angles.py` | Unit + mocked Claude | Prompt assembly, 10-angle JSON parsing, retry behavior |
| `angle_critic.py` | Unit + mocked Claude | Picks valid index, fallback to 0 |
| `writer.py` | Unit + mocked Claude | All validators run; retry feedback well-formed |
| `writer.py` validators | Pure unit | Contrast ratio math, hook word count, pairing membership, hashtag-range, slug-not-in-history |
| `designer.py` | Unit + mocked Claude | HTML uses writer-provided palette tokens; fallback works |
| `critique.py` | Unit + mocked Claude | Parses expanded verdict JSON; populates must_revise_slides |
| `orchestrator.py` | Integration (mocked Claude) | Pipeline wiring; revision loop stops at round 2 |
| End-to-end | Real Claude vs `brands/_test/` | One full pipeline run produces N PNGs + caption.txt + metadata.yaml. Run weekly. |
| Visual regression | Snapshot rendered PNGs | Catches accidental layout/font/render changes |

## 15. Open questions / future work

- **Counter-drift edge case:** if a brand goes through a deliberate visual rebrand, the `visual_refs/` history would resist the change. Future work: add a `--reset-visual-refs` CLI flag or a date-cutoff in `brief.yaml` (`visual_refs_since: 2026-06-01`).
- **Reference image cost vs benefit:** the ~$0.20-0.40 multimodal cost on every Writer call is included. After phase 2 testing, evaluate if 3 images is as effective as 10 — could reduce cost.
- **Critic ensemble:** the visual critic is a single Opus call. If quality plateaus, future work: ensemble 2-3 critics with different framings and require majority REVISE to trigger revision.
- **Brand-specific font sub-libraries:** universal library + brand-level filtering by emotional register tags rather than allowlists. Future work if visual drift becomes brand-specific.
- **Human-in-the-loop after round 2:** currently auto-ships best-effort with a warning. Future work: pause for human approval when the carousel reaches the round-2 cap.

---

## Appendix A — File diff summary

NEW: `angles.py`, `angle_critic.py`, `writer.py`, `layout_moves.py` (constant module), `orchestrator_v2.py` (during migration)

DELETED: `strategist.py`, all `brands/<name>/brand.css`

MODIFIED: `orchestrator.py`, `designer.py`, `critique.py`, `token_validate.py`, `persist.py`, every `brands/<name>/brief.yaml`, `fonts/library.yaml`

UNCHANGED: `claude_cli.py`, `cli.py` (apart from `--v2` flag during migration), `render.py`, `font_faces.py`, `layout_check.py`

## Appendix B — Defaults applied without explicit user decision

- 4-phase strangler-fig migration (rather than rip-and-replace).
- Three operational fields kept in `brief.yaml`: `slide_count_range`, `hashtag_count_range`, `content_guidelines_files`. Everything else is prose.
- Reference images = hook slide + climax slide per accepted carousel; 5 most recent carousels included by default; `golden/` always included if present.
- Visual critic adds three new judgment axes: `palette_appropriateness`, `brand_recognizability`, `creative_notes_honesty`.
- Designer fallback (`_safe_minimal_html`) preserved from current pipeline.
