# Remote Dispatch via Claude Code Routines

This repository is set up to generate Instagram carousels autonomously using a **Claude Code Routine**.

Routines run in Anthropic's secure cloud infrastructure, meaning no local machine or background process is required. They can be triggered by a cron schedule, on-demand via API, or by GitHub/GitLab webhook events.

---

## One-Time Routine Setup

### 1. Link your Repository
1. Install the Claude GitHub/GitLab App on the repository: `aurealis-info/agent-carousel`.
2. Grant read/write permissions. The Routine needs write access to commit new carousels directly to `main`.

### 2. Create the Routine
You can create the routine on the web dashboard at [claude.ai/code/routines](https://claude.ai/code/routines) or by using the `/schedule` command inside a Claude Code session.

Use the following settings:

| Field | Value |
|---|---|
| **Name** | Generate ETHOS Carousels |
| **Repository** | `aurealis-info/agent-carousel` |
| **Branch** | `main` |
| **Setup Script** | *(Leave blank)* — the routine only authors HTML/CSS/JSON; it does not render, so no package installation is required. |
| **Trigger** | Schedule (e.g., daily at 9:00 AM) or API trigger. Each run produces a **batch** of carousels (see the prompt), so pick the cadence accordingly. |
| **Branch Pushes** | **Enable unrestricted branch pushes** so the routine can commit directly to `main`. |
| **Network Access** | Trusted (default). |

> **Updating the prompt:** the live Routine uses whatever prompt is pasted into its config — editing this file does **not** update the Routine automatically. After changing the prompt below, re-paste it into the Routine on the dashboard.

### 3. The Routine Prompt
Copy and paste this prompt verbatim into the Routine's prompt field:

```text
Generate a BATCH of new ETHOS Instagram carousels for this run.

THIS RUN PRODUCES EXACTLY 6 CAROUSELS — not 1, not 4, SIX. The single most common failure is stopping after the first deck; do not. The run is NOT finished, and you may NOT commit, until all 6 deck folders exist under `carousels/` and each one passes the checklist.

FIXED BATCH COMPOSITION — build these exact 6 decks, one per row. This composition is what makes the templates equal and the colorway 50/50 automatically, so do not deviate from it:

  #  type_pairing_id (template)   format     colorway
  1  01-editorial-restrained      teaching   dark
  2  01-editorial-restrained      teaching   light
  3  03-annotated-notebook        teaching   dark
  4  03-annotated-notebook        teaching   light
  5  02-editorial-list            list       dark
  6  02-editorial-list            list       light

That is 2 decks per template (every template equally represented — balance is by TEMPLATE, not by format, so teaching naturally appears more than list) and 3 dark + 3 light (50/50). Hold this composition on every run. If a template is ever added or removed, keep the rule "2 decks per template, half dark and half light" and set the total accordingly.

For EACH of the 6 rows above, in order:
1. Read `cloud-agent/INSTRUCTIONS.md` (your role, the read-order, the workflow) and the format file for THIS row's format (`cloud-agent/formats/01-teaching.md` for rows 1–4, `cloud-agent/formats/02-list.md` for rows 5–6).
2. Read the existing folders under `carousels/` and their `metadata.json` files to see recent topics, pillars, themes, and title shapes — so this batch doesn't repeat them.
3. Choose a topic per `cloud-agent/TOPICS.md`. The template and colorway are ALREADY FIXED by this row — your job is to vary the EDITORIAL axes: vary at least 3 of {Pillar, Theme, Title Shape} from the most recent carousels AND from the other decks already built in this batch. Six decks in one run must be six distinct topics.
4. Build `carousels/<slug>/`:
   - `deck.css`: concatenate THIS row's colorway theme (`cloud-agent/themes/brand-dark.css` or `cloud-agent/themes/brand-light.css`) + THIS row's template CSS (`cloud-agent/templates/<type_pairing_id>/template.css`). Each template's README gives the exact Google Fonts `<link>` to put in every slide's `<head>` (the templates use different faces).
   - `slide-01.html` … `slide-NN.html`: standalone, complete HTML documents using that format's roles (teaching: hook + 3–5 steps; list: cover + numbered list slides, ~5 items per slide). NO CTA slide — the call-to-action is a separate fixed asset added later; never name the app ("ETHOS") in the copy.
   - `metadata.json`: title, slug, caption, tags, pillar, theme, `colorway` (this row's), `type_pairing_id` (this row's template), dimensions, and the ordered `slides` list.
5. Keep the 6 decks distinct from one another (different topics / pillars / themes / title shapes).

6. SELF-CHECK before committing. Confirm ALL of the following; if any fails, fix it before you commit:
   - Exactly 6 NEW folders under `carousels/`, each with a `metadata.json` and its `slide-NN.html` files.
   - `type_pairing_id` counts across the 6 are exactly: 2× `01-editorial-restrained`, 2× `03-annotated-notebook`, 2× `02-editorial-list`.
   - `colorway` counts across the 6 are exactly: 3 `dark` and 3 `light`.
   - 6 distinct topics; each deck passes the quality checklist in `cloud-agent/INSTRUCTIONS.md`.

Only once all 6 pass the self-check, commit and push the whole batch in ONE commit:
   git config user.email "noreply@aurealis.app"
   git config user.name "aurealis-carousel-bot"
   git add carousels/
   git commit -m "carousel: batch generate 6 decks [routine]"
   git push origin main
```

---

## The Build & Publishing Pipeline (CI/CD)

The Claude Routine does **not** generate images or talk to Cloudflare R2 directly. This keeps the routine runs extremely fast and keeps secrets out of the Routine's environment.

Instead:
1. The Routine pushes the generated HTML/CSS/JSON files (one folder per carousel) to `main`.
2. The **GitHub Actions Workflow** (`.github/workflows/render-carousels.yml`) is triggered on the push.
3. The runner spins up a virtual machine and installs node + playwright dependencies.
4. It runs `npm run render` (executing `scripts/render.js`), which:
   - Automatically detects **every** newly added/modified folder under `carousels/` (so a batch of 4 renders all 4) — it is template-agnostic and screenshots whatever HTML each `metadata.json` lists.
   - Screenshots each slide to a `1080x1350` JPEG.
   - Uploads the JPEGs and the `metadata.json` verbatim to the Cloudflare R2 bucket, then notifies the dashboard.
