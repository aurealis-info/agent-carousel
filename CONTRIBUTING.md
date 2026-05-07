# Contributing

## Adding a new brand

1. **Create the brand folder:**
   ```bash
   mkdir brands/<your-brand>
   ```

2. **Author `brands/<your-brand>/brief.yaml`** following the schema. Required fields:
   - `brand_name`
   - `app.name`, `app.one_line`, `app.store_url`, `app.cta_bridge_phrase`
   - `icp.audience`, `icp.jtbd`, `icp.fears`, `icp.internal_monologue`
   - `voice.principles`, `voice.voice_mode.default` (`guide`/`expert`/`storyteller`)
   - `voice.banned_words` (optional list of brand-specific hard-rejects)
   - `type_pairings.default` (optional; pick from `fonts/library.yaml` IDs)
   - `publishing_mode` (`testing` or `commercial`)
   - `narrative.slide_count` ({min, max, sweet_spot})
   - `narrative.variety_rules` (optional list of brand-opt-in rules)
   - `product.hashtags` ({medium_density, niche, avoid, stack_rule})
   - `brand_lines_in_sand` (optional list)
   - `design.colors`, `design.fonts`, `design.visual_mood`

3. **Author `brands/<your-brand>/brand.css`** with the brand's design tokens. Required CSS variables:
   - `--color-primary`, `--color-secondary`, `--color-accent`, `--color-bg`, `--color-text`, `--color-text-muted`
   - `--font-heading`, `--font-body` (overridden by pairing's @font-face injection at render time)
   - `--type-display`, `--type-h1`, `--type-h2`, `--type-h3`, `--type-body`, `--type-caption`
   - `--sp-1` through `--sp-8` spacing scale
   - `--radius-sm`, `--radius-md`, `--radius-pill`

   Plus the semantic typography classes (`t-display`, `t-h1`, …, `t-body`, `t-label`, `t-handle`), color utilities (`c-*`, `bg-*`), `.scrim-bottom`, `.cta-pill`, `.divider-*`.

   Use `brands/ethos/brand.css` as the canonical example.

4. **Initialize history:**
   ```bash
   echo "[]" > history/<your-brand>.yaml
   ```

5. **Validate:**
   ```bash
   aurealis-carousel doctor <your-brand>
   ```

6. **First run:**
   ```bash
   aurealis-carousel generate <your-brand>
   ```

## Adding a new font pairing

1. Drop the font files into `fonts/library/<pairing-id>/` (TTF or OTF; normalize filenames — no spaces).
2. Add an entry to `fonts/library.yaml` with: id, heading, body, goals, emotions, vibe, pairs_well_with, references, license, license_status. See existing entries.
3. Verify with: `python -c "import yaml; from pathlib import Path; data = yaml.safe_load(Path('fonts/library.yaml').read_text()); ..."`
4. The new pairing is immediately available to all brands by default. Brand briefs can override the default to point at it.

## Updating the playbook

The 6 playbook files in `playbook/` are reference material loaded into Claude prompts. They encode universal craft principles (hooks, narrative, conversion, typography, layout, voice). Edits propagate to every future carousel run.

When updating:
- Keep the writing terse, declarative, opinionated. The playbook is read by Claude; not by humans.
- Use generic `<App Name>` placeholders, not brand-specific app names.
- Frame anti-pattern categories as PRINCIPLES, not enumerated wordlists. Wordlists live in per-brand `voice.banned_words`.

## Tests

```bash
.venv/bin/pytest -v               # all unit + mocked-Claude tests
.venv/bin/pytest --run-live -v    # also runs live tests against the _test brand
```

Live tests cost real Claude credits. Use sparingly.
