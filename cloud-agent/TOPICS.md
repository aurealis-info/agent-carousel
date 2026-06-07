# TOPICS — What to Talk About

This is how to choose and generate a topic — not a list of topics. A fixed list makes the feed go stale and samey. Criteria you reason from keep it varied and on-brand.

The substance lives in the 10 themes in `BRAND.md`. This doc adds the **pillars** (the move a topic makes) and the **bar** a topic has to clear.

---

## Pillar × theme — the two axes of a topic

Every good topic is an intersection of two things:

- **Pillar** — the move the topic makes. *How* it lands.
- **Theme** — the substance it carries. *What* it's about.

If you can't name both, the topic isn't sharp enough yet.

### The 4 pillars

Rotate across these so the feed doesn't go monotone.

- **Scripture Applied** — take a passage or a principle and land it on something real he's dealing with right now. The verse is earned by the application, not pasted on top.
- **The Work** — discipline, becoming useful, becoming the kind of man people can count on. The 20s are for getting built. Not hustle-worship — just doing the work because that's what a man does.
- **Real Talk** — name a hard truth the way an older brother would across the table. Straight about what's actually wrong. Never contempt, never rage-bait.
- **The Vision** — who he's becoming. The man worth being, and worth marrying. Aspiration through formation, not fantasy.

Remember the order from `BRAND.md`: faith first, everything else is fruit. A topic about discipline or work is about what grows *from* a man being Christ's — never about earning his way to it.

---

## What makes a topic worth a carousel

- **It makes him a better man.** He'd be better for reading it even if he never downloads the app.
- **You can name the pillar and the theme.** If you can't say which, it's too vague — sharpen it or drop it.
- **It's for the guy trying to walk with God** — not the generic self-improvement reader. Faith is in it somewhere: Scripture, the Word, the man chasing God.
- **He can use it this week, or it convicts him today.** Specific and applicable now, or it names a tension he's actually in. Generic advice ("be disciplined," "trust God") trains him to scroll past.
- **It carries a tension or corrects an assumption.** Flat topics don't stop a scroll. The ones that do hold a tension — *build patience when everything in you wants to force it*, *handle success without losing himself* — or correct what he assumes — *anger isn't suppression*, *it's not what you think*. That hidden tension is the hook; find it before you write.
- **Conviction, not outrage.** Name a real tension. Don't perform one for reactions.

---

## How to find the angle

Reach for one of these to source the idea — don't run the same one every time.

- **Theme × a concrete moment.** Pair a theme with a scene from his actual week — the kind of moment he'd recognize as *his* before he reads the next line. The 2 AM scroll. The text he shouldn't send. The third drink. Specific is what makes him think *that's me*.
- **Counter-frame.** Why a man walking with God doesn't fit the worldly version he's been sold. Highest leverage, highest risk — stay in ETHOS's voice, no edgelord turns.
- **Cultural lens.** Frame it through a film, a book, or a moment his generation already knows. Borrow the attention; deliver the substance.

## Title shapes — and rotate them

A topic also has a *shape* — the promise its title makes. **Don't give every post the same shape.** "How a man of God ___" is the workhorse, but a feed of nothing but that goes numb fast. Rotate across these:

- **Identity in action** — *"How a man of God [handles a hard, specific thing]."* Strongest with a tension baked in: *without losing himself*, *when he doesn't feel ready*, *differently than the world*.
- **Numbered list** — *"5 things / 5 traits / 5 Proverbs a man of God ___."* Collectible and high-save. Sharpen it with a hook: a time (*before 8 AM*), an age (*before 25*), or a hidden-work angle (*that God's building in you even when you can't see it*).
- **Reframe / myth-buster** — *"What Scripture actually says about ___ (it's not what you think)"* or *"What a godly man does with ___ (it's not [the obvious])."* Name a thing he assumes he understands, then flip it. The parenthetical is the hook.
- **The mechanism** — *"How [one small practice] changes ___."* A concrete habit and the real result it produces (*how one verse a day rewires the way you think*).
- **The paradox** — *"What it actually looks like to [hold two opposites]."* Surrender *and* ambition. Confident *and* humble. The tension is the draw.

Same theme, different shape — that's what keeps the feed from going flat. Mix shapes the way you mix pillars and archetypes. These are starting frames, not fill-in-the-blanks; the topic and the words are always yours.

**Step label follows the title shape.** The CSS class is `.step-label` (per `DESIGN.md`), but the text inside adapts to the shape: a Numbered-list "3 questions" deck uses `Question 1` / `Question 2` / …; a "5 traits" deck uses `Trait 1` / `Trait 2`; a "5 verses" deck uses `Verse 1` / `Verse 2`. Default is `Step 1` / `Step 2`, with `Tip 1` / `Tip 2` for tip-style listicles. Match the label to the shape so the deck reads as one piece.

---

## Rotation discipline

Before you start, look at the most recent carousel in `../carousels/` and **vary at least 3 of these 4 axes**:

- **Pillar** (Scripture Applied / The Work / Real Talk / The Vision)
- **Theme** (which of the 10 in `BRAND.md` it carries)
- **Title shape** (the five above)
- **Colorway** (dark / light — kept ~50/50 over time; see below)

A feed that varies all four every post is a feed that stays sharp. A feed that hits the same combo twice in a row is the start of going flat — the audience notices before you do.

**Colorway balance.** Neither colorway is the default — keep the split **~50/50 dark/light over the long run**, within each format (`01-teaching` and `02-list`) and across the feed overall. Beyond rotating it post-to-post, glance at the `colorway` of the last several decks in `../carousels/` and pick whichever pulls the running split back toward even.

**Template balance (by template, not by format).** There are three templates — `01-editorial-restrained` and `03-annotated-notebook` (both teaching) and `02-editorial-list` (list). Keep each of the **three templates equally represented over time**. Because teaching has two templates and list has one, this means teaching decks naturally appear about twice as often as list decks — that's intended. The cloud Routine enforces this by building a **fixed batch every run: 2 decks per template (3 dark + 3 light)** — see the batch composition table in `docs/dispatch.md`. When generating outside that batch, glance at the `type_pairing_id` of recent decks and pick the template that's currently behind.
