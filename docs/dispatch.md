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

HOW MANY + WHICH FORMATS (keep the formats evenly balanced):
- List the formats available in `cloud-agent/formats/` (currently two: `01-teaching` and `02-list`).
- Generate an EQUAL number of carousels per format, at least 4 carousels total. With 2 formats that is 2 teaching + 2 list. If formats are added later, keep the per-format counts equal and keep the total ≥4 and divisible by the number of formats (e.g. 3 formats → 6 total = 2 each, or 3 total = 1 each if you prefer fewer — never lopsided toward one format).

For EACH carousel in the batch:
1. Read `cloud-agent/INSTRUCTIONS.md` (your role, the read-order, the workflow) and the format file for the format you're building (`cloud-agent/formats/01-teaching.md` or `cloud-agent/formats/02-list.md`).
2. Read the existing folders under `carousels/` and their `metadata.json` files to see recent topics, pillars, themes, colorways, and the running colorway split.
3. Choose a topic per `cloud-agent/TOPICS.md`: vary at least 3 of the 4 axes (Pillar, Theme, Title Shape, Colorway) from the most recent carousels, AND keep the colorway ~50/50 dark/light across this batch and over time. For teaching decks, ALSO vary the template (`01-editorial-restrained` vs `03-annotated-notebook`) and keep that split balanced over time too.
4. Build `carousels/<slug>/`:
   - `deck.css`: concatenate the colorway theme (`cloud-agent/themes/brand-{dark,light}.css`) + the template for the chosen format. Teaching has TWO templates — pick one (rotate to keep them balanced): `cloud-agent/templates/01-editorial-restrained/template.css` or `cloud-agent/templates/03-annotated-notebook/template.css`. List uses `cloud-agent/templates/02-editorial-list/template.css`. Each template's README gives the exact Google Fonts `<link>` to put in every slide's `<head>` (the templates use different faces).
   - `slide-01.html` … `slide-NN.html`: standalone, complete HTML documents using that format's roles (teaching: hook + 3–5 steps; list: cover + numbered list slides, ~5 items per slide). NO CTA slide — the call-to-action is a separate fixed asset added later; never name the app ("ETHOS") in the copy.
   - `metadata.json`: title, slug, caption, tags, pillar, theme, colorway, `type_pairing_id` (the template you used: `01-editorial-restrained`, `02-editorial-list`, or `03-annotated-notebook`), dimensions, and the ordered `slides` list.
5. Make the carousels in the batch distinct from one another (different topics / pillars / title shapes), and keep the batch's colorway split even.

When every carousel passes the quality checklist in `cloud-agent/INSTRUCTIONS.md`, commit and push the whole batch:
   git config user.email "noreply@aurealis.app"
   git config user.name "aurealis-carousel-bot"
   git add carousels/
   git commit -m "carousel: batch generate <N> decks [routine]"
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
