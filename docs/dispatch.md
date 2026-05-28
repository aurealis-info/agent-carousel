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
| **Name** | Generate ETHOS Carousel |
| **Repository** | `aurealis-info/agent-carousel` |
| **Branch** | `main` |
| **Setup Script** | *(Leave blank)* — The routine does not require any package installations or setup. |
| **Trigger** | Schedule (e.g., daily at 9:00 AM) or API trigger. |
| **Branch Pushes** | **Enable unrestricted branch pushes** so the routine can commit directly to `main`. |
| **Network Access** | Trusted (default). |

### 3. The Routine Prompt
Copy and paste this prompt verbatim into the Routine's prompt field:

```text
Generate a new ETHOS Instagram carousel.

Steps:
1. Read `cloud-agent/INSTRUCTIONS.md` to understand your role, the brand voice, and the design constraints.
2. Read the existing folders under `carousels/` (if any exist) and their `metadata.json` files to see what topics, pillars, themes, and colorways were used recently.
3. Choose a new topic by following the rotation discipline in `cloud-agent/TOPICS.md`. You must vary at least 3 of the 4 axes (Pillar, Theme, Title Shape, Colorway) compared to the most recent carousel.
4. Generate the carousel files under `carousels/<slug>/`:
   - `deck.css`: Create this by concatenating the correct theme stylesheet (from `cloud-agent/themes/brand-{dark,light}.css`) and the restraint layout stylesheet (from `cloud-agent/templates/01-editorial-restrained/template.css`).
   - `slide-01.html` through `slide-NN.html`: Author each slide as a standalone, complete HTML document conforming to the brand specs.
   - `metadata.json`: Write the metadata config containing the title, slug, caption, tags, pillar, theme, colorway, dimensions, and the ordered `slides` list.
5. If everything looks correct and passes your internal quality checks:
   - Configure Git:
     git config user.email "noreply@aurealis.app"
     git config user.name "aurealis-carousel-bot"
   - Stage, commit, and push the new carousel:
     git add carousels/<slug>/
     git commit -m "carousel: generate <slug> [routine]"
     git push origin main
```

---

## The Build & Publishing Pipeline (CI/CD)

The Claude Routine does **not** generate PNGs or talk to Cloudflare R2 directly. This keeps the routine runs extremely fast and keeps secrets out of the Routine's environment.

Instead:
1. The Routine pushes the generated HTML/CSS/JSON files to `main`.
2. The **GitHub Actions Workflow** (`.github/workflows/render-carousels.yml`) is triggered on the push.
3. The runner spins up a virtual machine, installs node and playwright dependencies.
4. It runs `npm run render` (executing `scripts/render.js`), which:
   - Automatically detects the newly added/modified folders under `carousels/`.
   - Screenshots each slide to a `1080x1350` PNG.
   - Uploads the PNGs and the `metadata.json` verbatim to the Cloudflare R2 bucket.
