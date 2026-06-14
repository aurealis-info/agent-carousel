# Format · 02 — List (cover → list slides)

**The dense reference format.** A numbered list of many items with little or no explanation — the post a man screenshots and saves. Where the teaching format explains *one idea per slide*, the list format **names many things sharply** and lets each line do its own persuading.

- **Paired template:** `templates/02-editorial-list/` *(the list layout — built next; its fonts differ from `01`, the colorway stays uniform with the rest of the feed)*
- **`metadata.json` stamp:** `"type_pairing_id": "02-editorial-list"`
- **Read `CAROUSEL.md` first** — the shared craft (mission, viewer arc, hook engineering, copy psychology, anti-patterns). This file covers only what's *specific* to the list format.
- **Layouts ship with the template:** the cover and list-item reference layouts + their type scale live with the `02-editorial-list` template (built next), not in `DESIGN.md`. Until it ships, this file is the spec for that build.
- **The CTA is not your concern.** Every post ends with one of a fixed set of CTA slides (Figma PNGs) a human appends at publish, rotated per post. You never write, word, or format a CTA — just the cover + list slides.

---

## When to use it

Reach for the list format when the topic is a **collection** — things to kill, lies to unlearn, places to go, disciplines to keep, signs to notice — and each item is sharp enough to land without a paragraph. If an item needs a full slide to make sense, it belongs in the teaching format, not here.

---

## Structure

A list carousel is **1 cover slide + M list slides**. No CTA slide — the call-to-action is a separate Figma asset appended after rendering; never generate one in HTML/CSS, and never name the app in any slide.

| Slide | Role |
|---|---|
| 1 | **Cover** — the number + the promise; stop the scroll |
| 2 … | **List slides** — the numbered items, ~5 per slide |

- **Item count = the number in the title.** A "12 Things" deck has exactly 12 items.
- **Density:** ~5 items per slide by default; drop to 4 when the glosses run long, so nothing crowds the 1080×1350 frame. Distribute evenly (20 items → 4 slides of 5).
- **Numbering is continuous** across slides (slide 2 = items 1–5, slide 3 = 6–10, …).

---

## Slide 1 — the Cover

Three parts, top to bottom:

- **Eyebrow** — the category, small and quiet (e.g. `ETHOS`).
- **Headline** — the **number + the promise**, big serif. The number *is* the hook ("10 Lies…", "12 Things…").
- **Italic parenthetical** — the twist underneath, in serif italic: *(That Scripture never taught you)*. This is where the curiosity gap snaps shut.

Faith signal is mandatory on the cover, **in the headline itself** — the number + a faith-coded promise (godly, Scripture, sin, man of God…). The italic parenthetical may reinforce it but can never be the only place it lives (same rule as any ETHOS hook; see `CAROUSEL.md`). A cover whose faith signal sits only in the twist underneath reads as generic self-improvement at a glance — the wrong room.

---

## The list items (the craft is compression)

Each item is **a sharp line + an optional one-line ETHOS gloss**:

```
N. [The thing — named so sharply it barely needs explaining.]
   [Optional: one short gloss line, ETHOS voice, that lands it.]
```

- **The item line does the persuading.** The noun phrase itself should stop the scroll ("The 2 a.m. scroll," "The bottom you swore you'd never hit"). If it needs the gloss to make sense, sharpen the item.
- **The gloss is where the voice lives** — one line, concrete, second person, faith-coded where natural. Cut it on items that are self-evident; keep the deck breathing (a wall of glosses reads heavy).
- **Earned Scripture, sparingly** — at most one verse in a list, attached to the line that built to it. Never one per item.
- **No app mention** — the app belongs to the fixed CTA slides, never the list copy.
- **Imperative lists are fine.** For disciplines/habits/moves ("Make your bed…", "Sit in silence…"), the command frame is allowed — the title supplies the setup, so `CAROUSEL.md`'s "no command hooks without setup" is satisfied at the deck level, not per item.

---

## Cross-list discipline (matters more here than for teaching)

You'll run several lists across a feed. If "confession to a brother" or "the phone at night" recurs in three lists, the account starts to feel like it has four ideas. **Each list owns its own lane** — de-duplicate item *ideas* across recent lists, not just within one deck.

---

## Worked examples (4 finalized lists, ready to build)

Item line in **bold**, then the gloss as its own short sentence (no em dashes anywhere in ETHOS copy).

### "10 Lies You Inherited About Godly Manhood" *(That Scripture never taught you)*
1. **A real man doesn't need anyone.** Isolation isn't strength. It's where men rot.
2. **Provide and you've done your job.** They need your presence, not just your paycheck.
3. **Anger means you've lost control.** Anger's a signal. What you do with it is the test.
4. **Lust is just how men are wired.** You were built for desire, not enslaved to it.
5. **Confidence is the goal.** Confidence cracks under pressure. Character doesn't.
6. **Lead by being the loudest.** The man everyone follows is usually the calmest in the room.
7. **You're enough exactly as you are.** You're loved as you are. You're not meant to *stay* as you are.
8. **Faith is a private thing.** A faith no one can see is a faith you've never tested.
9. **Numb it and move on.** What you bury alive doesn't stay buried. It runs you.
10. **You'll change when you feel ready.** You won't feel ready. You'll decide, or you'll drift.

### "12 Sins to Kill Before You're 25" *(While it's still easy)*
1. **Doom scrolling at 2 a.m.** Nothing you find at 2 a.m. is worth what it costs you at 8.
2. **The private tab.** What you feed in the dark feeds on you in the light.
3. **Waiting to feel motivated.** Discipline shows up on the days motivation doesn't.
4. **Performing three versions of yourself.** Gym, church, group chat. Same guy, or none of them are real.
5. **The "I'll start Monday" voice.** Monday is a coward's word for *never*.
6. **Borrowing your worth from the comments.** A number can't tell you who you are.
7. **Outrage as a personality.** Being against everything isn't the same as standing for something.
8. **Keeping score in your friendships.** Brotherhood isn't a transaction.
9. **The group chat that makes you smaller.** Some rooms you have to leave to grow.
10. **Comparing your chapter 1 to his chapter 20.** Envy never finished a race.
11. **Treating your body like it's disposable.** It's the only one the work gets done in.
12. **Quitting the second it goes quiet.** Most men quit right before it gets good.

### "9 Places a Man Actually Meets God" *(None of them are a Sunday service)*
1. **The work you do when no one's watching.** Discipline is a quiet form of worship.
2. **The apology you don't want to make.** Pride finally meets grace there.
3. **The hospital waiting room.** He's closest when you're most out of control.
4. **The bottom you swore you'd never hit.** He meets men in the wreckage, not the highlight reel.
5. **The wilderness season when nothing's working.** He did some of His best work in deserts.
6. **The person you forgave who never said sorry.** The grace you give is the grace you finally understand.
7. **The temptation you walked away from.** Every "no" is a place you met Him.
8. **The mirror, the morning after a failure.** Grace hits hardest once you stop pretending.
9. **The ordinary Tuesday you almost wasted.** He's not only on the mountaintop. He's in the routine.

### "7 Godly Disciplines That Outlast Motivation" *(Pick three, not all seven)*
1. **Make your bed before you make excuses.** Win the first rep of the day.
2. **One page of Scripture before one notification.** Whoever you feed first wins the day.
3. **Move your body daily, not perfectly.** Showing up beats showing off.
4. **Tell one man the truth this week.** Light is the only thing that breaks the grip. *(James 5:16: "Confess your sins to one another, that you may be healed.")*
5. **Keep your word to yourself.** Trusting God starts with trusting you.
6. **Sit in ten minutes of silence.** You can't hear Him over your own noise.
7. **End the day with thanks, not the feed.** Gratitude is the opposite of scrolling.
