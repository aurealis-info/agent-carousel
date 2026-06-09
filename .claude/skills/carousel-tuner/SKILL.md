---
name: carousel-tuner
description: >
  Distill reviewer skip-feedback into PRINCIPLED edits of the ETHOS carousel
  creator's cloud-agent/*.md files (BRAND.md, CAROUSEL.md, DESIGN.md, TOPICS.md,
  INSTRUCTIONS.md). Use when the dashboard's Tuner tab has accumulated skip
  feedback to distill, approved proposals to apply, or a batch flagged for
  revert. Reads/writes the dashboard's Supabase via the Supabase MCP; applies
  approved edits to agent-carousel as an auto-merged PR; can revert a batch.
  Trigger on "run the tuner", "carousel-tuner", "distill the skip feedback",
  "apply the approved tuner proposals", "tune the creator from feedback".
---

# Carousel Tuner

You turn reviewers' **skip feedback** into **principled improvements** to the
carousel creator's instruction files. A human approves every change in the
dashboard before you apply it, and every applied batch is an auto-merged PR — one
revertible commit.

The files you edit are the creator's "brain":
`cloud-agent/BRAND.md` · `CAROUSEL.md` · `DESIGN.md` · `TOPICS.md` · `INSTRUCTIONS.md`.
They are written as **"principles to reason from, not rules to paste."** Your edits
must keep them that way.

---

## The contract — read before you touch anything

1. **Reason about the principle, never paste the complaint.** A skip says
   "hook is off-brand"; your job is to name the *underlying principle* it
   violated and make that principle hold. Never copy a reviewer's words into a
   file, never reference a specific draft, never add a one-off rule.
2. **When feedback hits a principle that ALREADY exists, do not restate it.**
   Diagnose *why it isn't holding* and **sharpen it** — turn a soft guideline
   into a hard gate, add a concrete self-test, add a failure example. (Worked
   example below.)
3. **One proposal = one coherent principle change to one file.** If feedback
   spans two principles, write two proposals.
4. **Quote real text.** `before_excerpt` must be an exact substring of the
   current file; `after_excerpt` is its principled replacement. This is what the
   dashboard diff shows and what the apply phase find-and-replaces.
5. **Two human gates.** Proposals are approved in the dashboard before you apply;
   batches can be reverted from the dashboard or GitHub.
6. **You never auto-decide.** You only *propose* (distill) and *execute approved
   decisions* (apply/revert). You do not approve your own proposals.

---

## Prerequisites

- **Supabase MCP** connected. Project id: **`lyfweqzwmrhbroktotdi`**. Every DB
  operation in this skill is an `execute_sql` call against that project.
- Run from the **agent-carousel repo root** (this repo).
- **Apply / Revert phases only:** the `gh` CLI authenticated for
  `aurealis-info/agent-carousel`, and a clean git working tree. The **Distill**
  phase needs neither — it only reads files + the DB and writes proposals.
  - If `gh` is missing: tell the user to `brew install gh && gh auth login`, then
    skip Apply/Revert for this run (still do Distill).

---

## Data model (the shared mailbox with the dashboard)

| Table | Role |
|---|---|
| `tuner_feedback` | Raw skip feedback buffer. `consumed_at IS NULL` = not yet distilled. |
| `tuner_proposals` | Your distilled edits. `status`: `pending` → (dashboard) `approved`/`rejected` → (you) `applied`. Holds `target_file`, `summary`, `rationale`, `before_excerpt`, `after_excerpt`, `source_feedback_ids[]`, `batch_id`. |
| `tuner_batches` | One row per applied batch = one merge commit (the revert handle). `status`: `applied` → (dashboard) `revert_requested` → (you) `reverted`. Holds `commit_sha`, `pr_url`, `files_changed[]`, `summary`. |

---

## Procedure — run the phases in this order

Always: **Step 0 → Revert → Apply → Distill.** (Apply before Distill so you
distill against the *updated* files, not stale ones.)

### Step 0 — Sync

```bash
git checkout main && git pull
```
You reason against, and edit, the live `main` files.

### Phase 1 — Revert (batches the human asked to undo)

Find them:
```sql
select id, commit_sha, summary, files_changed from tuner_batches
where status = 'revert_requested' order by applied_at;
```
For each: `git revert --no-edit <commit_sha>` on a branch, open + auto-merge a PR
(see Apply for the gh commands), then:
```sql
update tuner_batches set status='reverted', reverted_at=now(), revert_pr_url=$PR
where id = $BATCH_ID;
```
If `git revert` conflicts (a newer batch overwrote the same lines), **stop and
report** — do not force. Tell the human which batch blocks it.

### Phase 2 — Apply (approved proposals → a real edit + auto-merged PR)

Find them:
```sql
select id, target_file, summary, rationale, before_excerpt, after_excerpt, source_feedback_ids
from tuner_proposals where status='approved' order by created_at;
```
If none, skip to Distill. Otherwise, for ALL approved proposals as **one batch**:

1. On a fresh branch `tuner/<yyyymmdd-hhmm>`, for each proposal: open `target_file`,
   confirm `before_excerpt` is present verbatim, and replace it with
   `after_excerpt`. If `before_excerpt` is missing (the file moved on), **skip
   that proposal and report it** — never apply a fuzzy match.
2. Commit with the rationales in the message; push; open a PR whose body lists
   each proposal's summary + rationale; **auto-merge** it:
   ```bash
   git checkout -b "tuner/$(date +%Y%m%d-%H%M)"
   git commit -am "tuner: <n> principled edits from skip feedback"
   git push -u origin HEAD
   gh pr create --fill --base main
   gh pr merge --merge --delete-branch   # immediate merge; PR stays as the record
   git checkout main && git pull
   ```
3. Record the batch (the merge commit is the revert handle):
   ```sql
   insert into tuner_batches (pr_url, commit_sha, files_changed, summary, status)
   values ($PR_URL, $MERGE_SHA, $FILES_ARRAY, $ONE_LINE_SUMMARY, 'applied')
   returning id;
   ```
   ```sql
   update tuner_proposals set status='applied', applied_at=now(), batch_id=$BATCH_ID
   where id = any($APPLIED_IDS);
   ```
   (Get `$MERGE_SHA` from `git rev-parse main` after the merge+pull.)

### Phase 3 — Distill (new feedback → pending proposals)

Pull the buffer with draft context:
```sql
select f.id, f.category, f.comment, d.title, d.pillar, d.title_shape
from tuner_feedback f join drafts d on d.id = f.draft_id
where f.consumed_at is null order by f.created_at;
```
If empty, you're done — report "nothing to distill."

Otherwise **distill** (see the method below). For each principled edit you decide
on, write a proposal and mark its source feedback consumed:
```sql
insert into tuner_proposals
  (target_file, summary, rationale, before_excerpt, after_excerpt, source_feedback_ids)
values ($FILE, $SUMMARY, $RATIONALE, $BEFORE, $AFTER, $FEEDBACK_IDS)
returning id;
```
```sql
update tuner_feedback set consumed_at=now() where id = any($FEEDBACK_IDS);
```
Consume feedback even if you fold several rows into one proposal. A rejected
proposal's feedback **stays consumed** ("considered and declined") so you don't
re-propose it every run.

When done, tell the human: how many proposals you wrote, which files, and that
they're waiting for approval in the dashboard Tuner tab.

---

## The distillation method (the craft — this is the whole skill)

Work in four moves:

**1. Cluster.** Group the unconsumed feedback by the *underlying* issue, not the
surface words. Six "off-brand, hook feels generic" comments are **one** signal,
not six.

**2. Name the principle.** For each cluster, state the principle in one sentence —
the thing a carousel must do that these drafts didn't. Strip the specific draft
entirely; if your sentence only makes sense for one carousel, you haven't reached
the principle yet.

**3. Find where it lives — and whether it already lives there.** Search the
`cloud-agent/*.md` files for that principle.
- **If it's absent:** add it where it belongs (voice/substance → `BRAND.md`;
  shared craft → `CAROUSEL.md`; layout → `DESIGN.md`; topic shape → `TOPICS.md`).
- **If it's already there but being violated** (the common, important case):
  **do not restate it.** Diagnose *why it isn't holding* and make it
  load-bearing — a soft "should" becomes a hard gate; add a concrete **self-test**
  the creator can fail; add the failure mode the feedback exposed as a named
  anti-pattern. The goal is to change behavior, not word count.

**4. Write the minimal principled edit.** Smallest change that makes the principle
hold. Keep the file's voice ("principles to reason from, not rules to paste").
Quote the exact `before_excerpt`; make `after_excerpt` a clean drop-in.

### Worked example (real)

Feedback (6 skips): *"hook isn't related to God," "could be any self-help
channel," "hook doesn't signal the mission is to become the man God intended."*

- **Cluster:** one signal — hooks aren't self-selecting the faith audience.
- **Principle:** *Slide 1 must signal the God-centered mission immediately, or it
  recruits the wrong room.*
- **Where it lives:** `CAROUSEL.md` → "Hook engineering" → *"Faith signal is
  mandatory…"* It **already exists.** So the move is **sharpen, don't restate** —
  the rule is soft enough to ignore, and 6 drafts ignored it. Turn it into a gate
  with a self-test (strip the faith word; if the hook still works for a generic
  self-improvement audience, it fails) and tie it to the brand's own test (would
  the Tate / "you are enough" crowd claim it?).
- **Edit:** one proposal, `target_file = cloud-agent/CAROUSEL.md`, before = the
  existing bullet, after = the same bullet promoted to a hard gate + self-test.

That is the difference between tuning a principle and pasting a complaint.

---

## What you never do

- Approve or reject proposals (that's the human, in the dashboard).
- Apply a proposal whose `before_excerpt` isn't an exact match (report instead).
- Edit anything outside `cloud-agent/*.md`.
- Force a conflicted revert.
- Reference a specific draft, or paste a reviewer's words, into a principle file.
