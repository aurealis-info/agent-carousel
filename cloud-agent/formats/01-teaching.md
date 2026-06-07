# Format · 01 — Teaching (hook → steps)

**The original ETHOS carousel.** One idea per slide, explained in depth. The workhorse: a hook that stops the scroll, then 3–5 step slides that each teach one thing well.

- **Templates (pick one, rotate over time):** `templates/01-editorial-restrained/` (Playfair + Inter, solid editorial) or `templates/03-annotated-notebook/` (Lora + Inter, graph-paper grid with gold hand-drawn circle/underline annotations + a `@theethosapp` promo). Both render the same hook → steps copy.
- **`metadata.json` stamp:** `"type_pairing_id"` = the template you used (`01-editorial-restrained` or `03-annotated-notebook`).
- **Read `CAROUSEL.md` first** — the shared craft (mission, viewer arc, hook engineering, copy psychology, anti-patterns). This file covers only what's *specific* to the teaching format.

---

## Structure

A teaching carousel is **1 hook slide + N step slides**, where **N is 3–5**. Total slides = N + 1. No CTA slide — the call-to-action is a separate Figma asset appended after rendering; never generate one in HTML/CSS, and never name the app in any slide.

| Slide | Role |
|---|---|
| 1 | **Hook** — stop the scroll |
| 2 … N+1 | **Steps** — one tip/idea each, delivered in depth |

Pick the count the topic actually needs; don't pad to a number, don't cram two ideas to save a slide.

---

## Slide 1 — the Hook

- **The hook line:** 2–6 words, or a short line plus a one-sentence subhead. A pain point or curiosity gap, **not the topic name**.
- **Faith signal is mandatory** (see `CAROUSEL.md` → Hook engineering).
- **Layout:** the `hook` role in `DESIGN.md` (hook-headline + rule + subhead).

---

## Slides 2…N+1 — the Steps (one idea each, in depth)

Each step slide is a single tip/idea, developed enough to be useful on its own. Anatomy (all optional except title + body):

- **Step label** — `STEP 1`, `STEP 2`, … (or `TIP 1` …). The text adapts to the title shape — `TRAIT 1`, `VERSE 1`, `QUESTION 1` (see `TOPICS.md` and `DESIGN.md`).
- **Title** — short, bold, declarative. The idea in a few words.
- **Body** — a few short lines, each its own beat (not a wall of text).
- **Arrow points** — optional `→` bullets that sharpen the application.
- **Closing line** — optional one-line landing that travels (screenshottable).

Rules: **second person**, **one idea per slide**, **genuinely useful** (he can apply it today), **concrete > abstract every line**, **earned Scripture**, **no app mention**.

---

## Fill patterns (vary across posts)

Different ways to fill the steps — each a different mechanic:

- **Listicle** — "N traits / verses / disciplines," **one per slide**. *(Distinct from the dense `02-list` format, which packs many items per slide. If each item deserves a full slide, it's a teaching listicle; if they're sharp one-liners, it's `02-list`.)*
- **Mistakes list** — "N things men get wrong about…" Identification + relief. Brotherly, never sneering.
- **Uncomfortable questions** — each step a question he can't answer comfortably. Use sparingly.
- **Problem / solution** — early steps show the wrong/hard way; later steps the better path.
- **Cultural lens** — frame through a film/book/moment he already inhabits; the substance is still the pillar.

---

## Format-specific anti-pattern

- **Overstuffing.** One idea per step; 3–5 steps. If the topic needs more, it's two carousels — or the `02-list` format.
