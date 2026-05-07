---
name: carousel
description: Generate an Instagram carousel for a configured Aurealis brand. Triggers when the user asks to create, generate, or make a carousel for a brand they have configured (e.g., "make a carousel for ETHOS about discipline" or "generate today's carousel for lokin"). The skill invokes the aurealis-carousel CLI which runs the full strategist→designer→critic pipeline with vision feedback.
---

# Carousel Generator

Generates a brand-disciplined, text-first Instagram carousel using the `aurealis-carousel` CLI. Each run executes the full pipeline: strategist (full creative spec) → designer (per-slide HTML) → token-validator + Playwright render + layout-fit check → vision critic → optional revision pass → persist.

## Workflow

1. Confirm a brand exists by running `aurealis-carousel list-brands`. If the user asked for a brand that isn't listed, surface the available brands and ask which to use.

2. Optionally accept a `--topic "..."` hint from the user. If absent, the strategist autonomously picks today's topic based on the brand brief + last 14 history entries.

3. Run:
   ```bash
   aurealis-carousel generate <brand> [--topic "..."]
   ```
   For routine / autonomous runs (cloud Routines, scheduled jobs), add `--auto-commit` to commit + push outputs to the repo automatically.

4. After the run completes, inspect `outputs/<brand>/<date>-<slug>/metadata.yaml` for the result. Report back to the user:
   - The output slug + absolute path to `outputs/<brand>/<slug>/`
   - Slide count
   - Chosen `voice_mode` + `type_pairing_id`
   - Any `warnings` from `metadata.yaml` (validator fallbacks, layout issues, critic-flagged revisions)
   - Whether the run was committed (only with `--auto-commit`)

5. If the user wants to inspect visually:
   ```bash
   aurealis-carousel preview <slug>
   ```
   This opens the carousel directory in Finder (macOS) so they can see the rendered PNGs.

## Adding a new brand

If the user asks you to set up a new brand:

1. Create `brands/<brand>/brief.yaml` and `brands/<brand>/brand.css`. Use `brands/_test/` as a minimal template; use `brands/ethos/` for a full schema example.
2. Initialize `history/<brand>.yaml` with `[]`.
3. Run `aurealis-carousel doctor <brand>` to validate the brief schema + font availability.
4. Generate the first carousel: `aurealis-carousel generate <brand>`.

## Notes

- The pipeline is text-first: no AI image generation. All visual interest comes from typography + color + composition + 6 universal font pairings indexed by goal/emotion.
- Brand consistency comes from voice + ICP + design tokens + brand.css. The strategist has open access to all 6 font pairings; the brand sets a `default` as a light anchor.
- Vision critic uses adversarial framing — biased toward rejecting mediocrity. Some carousels will trigger a revision pass.
- Three execution surfaces share the same engine: this skill (interactive), the CLI (manual / cron-equivalent), and Anthropic Routines (cloud-hosted autonomous).
