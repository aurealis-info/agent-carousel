# Remote dispatch via Anthropic Routines

This repo runs in the cloud as a Claude Code **Routine**. Routines bill against
your Max subscription (no API key, no pay-per-token), run on Anthropic's
infrastructure (no laptop needed), and can be triggered by schedule, API call,
or GitHub event.

Docs: <https://code.claude.com/docs/en/web-scheduled-tasks>

---

## One-time setup

### 1. Install the Claude GitHub App on the repo

1. Go to <https://github.com/apps/claude>
2. Install on the **`aurealis-info/agent-carousel`** repo (private install is fine)
3. Grant read + write permissions — the routine commits `history/<brand>.yaml`
   back to the repo so future runs avoid topic repeats

### 2. Create the routine

Either via the web form at <https://claude.ai/code/routines> or via `/schedule`
inside any Claude Code session. Web form is easier the first time; switch to
`/schedule` once you know the shape.

Suggested initial routine settings:

| Field | Value |
|---|---|
| **Name** | Generate ETHOS carousel |
| **Repository** | `aurealis-info/agent-carousel` |
| **Branch** | `main` |
| **Setup script** | `bash setup.sh` *(uses the `setup.sh` at repo root — cached ~7 days)* |
| **Trigger** | Schedule → daily at 9am *your timezone* &nbsp; **AND/OR** &nbsp; API trigger (for on-demand) |
| **Branch pushes** | **Enable unrestricted branch pushes** so the routine can commit `history/ethos.yaml` to `main` (default policy only allows `claude/`-prefixed branches) |
| **Network access** | Trusted (default) — covers fonts.googleapis.com, pypi.org, github.com |
| **Connectors** | None required |

### 3. The routine prompt

Paste this verbatim into the routine's prompt field:

```
Generate a new ETHOS Instagram carousel.

Steps:
1. Run the carousel CLI from the repo root. Try the shortcut first; if it's
   not on PATH, fall back to invoking the module directly via the venv setup.sh
   creates at $HOME/.venvs/aurealis-carousel/bin/python:

       aurealis-carousel generate ethos
       # OR if the shortcut isn't on PATH:
       $HOME/.venvs/aurealis-carousel/bin/python -m aurealis_carousel.cli generate ethos

   This invokes the strategist (one Claude call), designer (one call per slide),
   layout-fit validator, vision critic, and Playwright renderer. Expect ~5-10
   minutes total. The strategist auto-picks a topic from the 10 themes in
   marketing/guidelines/GENERAL_CONTENT_GUIDELINES while avoiding the recent
   14 entries in history/ethos.yaml.

2. If the CLI exits 0, commit history + outputs back so the next run avoids
   topic repeats and the team can see the rendered slides:

       git config user.email "noreply@aurealis.app"
       git config user.name "aurealis-carousel-bot"
       git add history/ethos.yaml outputs/ethos/
       git commit -m "carousel: $(ls -t outputs/ethos | head -1) [routine]"
       git push origin main

3. If the CLI exits non-zero, do NOT commit. Report the failure in your final
   message — include the last ~30 lines of stderr/stdout so I can diagnose.

4. In your final message, link to the new outputs/ethos/<slug>/ directory and
   summarize the topic, frame, voice_mode, and any layout-fit warnings from
   metadata.yaml.
```

To target a different brand (lokin, _test) or pass a specific topic, edit the
first command:

```
aurealis-carousel generate ethos --topic "Becoming the man worth marrying"
aurealis-carousel generate lokin
```

### 4. Save the routine

The routine appears in your dashboard at claude.ai/code/routines with:
- A **session URL** for each run (watch the agent's reasoning in real time)
- An **API trigger endpoint** (if you enabled it) — bearer-token-protected
- Run history with cost tracking (against your Max usage)

---

## Triggering on-demand

If you enabled the **API trigger** when creating the routine, copy the curl
snippet from the routine's settings panel. It looks like:

```bash
curl -X POST https://api.anthropic.com/v1/claude_code/routines/<routine_id>/fire \
  -H "Authorization: Bearer <bearer_token>" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -d '{"text": "manual trigger"}'
```

You can drop this into Slack slash commands, your phone's Shortcuts app, a
deploy hook, or just run it from your terminal.

---

## Limits & gotchas

- **Max plan cap:** 15 routine runs/day (combined across all routines on the
  account). Pro is 5/day, Team/Enterprise 25/day.
- **One-off runs:** Don't count against the daily cap but do consume normal
  Max usage allowance.
- **Setup-script cache:** ~7 days. Change `pyproject.toml` or `setup.sh` and
  the next run does a full reinstall (~3-5 min added to that single run).
- **Branch policy:** Default is `claude/`-prefixed only. The routine commits
  to `main` directly, so flip on **unrestricted branch pushes** in routine
  settings — otherwise the push step fails.
- **Network egress:** Default "Trusted" list covers fonts.googleapis.com,
  pypi.org, github.com, npm. If you add a brand whose pairing pulls fonts
  from a non-Google CDN, allowlist that domain in routine settings.
- **Outputs folder grows over time:** Each run commits ~500KB of PNGs. After
  ~100 runs the repo has ~50MB of carousel PNGs. If that becomes a problem,
  switch the commit step to push only `history/<brand>.yaml` and store PNGs
  elsewhere (S3, releases, or a long-retention artifact bucket).
- **Repo must have the Claude GitHub App installed** (step 1 above). Without
  it the routine can clone but cannot push.

---

## Troubleshooting

Failure modes the routine has actually hit, with fixes:

**`subprocess.TimeoutExpired` after 360s on a designer call**
The `claude -p` subprocess sometimes takes 5-8 minutes per call in cloud
routine envs (vs 2-4 min local) because of auth handshake + queueing
behind the parent session. `CLAUDE_TIMEOUT_SECONDS = 720` covers it. If
you still see timeouts, bump it further in `aurealis_carousel/claude_cli.py`
— honest failures still surface in reasonable wall-clock at higher values.

**Routine ran, but agent had to manually `pip install --break-system-packages`**
This means the routine's **Setup script** field is empty (or wrong). Open
the routine in claude.ai/code/routines, find the Setup script box, and
make sure it contains exactly `bash setup.sh`. Without it the agent has
to bootstrap Python deps on every run — slow, fragile, and skips the
venv path that handles PEP 668 cleanly.

**`pip install` fails with "Package requires Python >= 3.12" or PEP 668**
The cloud env's default `python` is 3.11 even though `python3.12` and
`python3.13` exist. Plus system pip is locked down (PEP 668). `setup.sh`
handles this — it auto-detects the highest 3.12+ interpreter, creates a
venv at `$HOME/.venvs/aurealis-carousel`, and persists the venv on PATH
via `~/.bashrc`/`~/.profile`/`$BASH_ENV`. If the agent still can't find
`aurealis-carousel`, the routine prompt instructs it to fall back to
`$HOME/.venvs/aurealis-carousel/bin/python -m aurealis_carousel.cli ...`.

**`git push origin main` → 403 "Resource not accessible by integration"**
The Claude GitHub App is installed but the routine isn't allowed to push to
`main`. Fix: in the routine's settings → **Behavior** tab, enable
**"Allow unrestricted branch pushes"**. Without it, only `claude/`-prefixed
branch pushes are accepted.

**Playwright "Executable doesn't exist at .../chrome-linux/chrome"**
Cloud env ships a Chromium pre-baked at `/opt/pw-browsers/chromium-<rev>/`
but at a build that doesn't match what `pip install playwright` expects.
`setup.sh` already handles this — it tries `playwright install chromium`,
falls back to the preinstalled binary, and exports
`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` for `render.py` / `layout_check.py`.
If you see this error, check the setup-script log: did it find a binary?

**`error_max_turns` on a strategist or designer call**
Two known causes:
1. CLI v2.1.133+ counts session-init as a turn, so `--max-turns 1` exits
   without producing output. `claude_cli.py` defaults to `max_turns=2`.
2. The parent `claude` session's CLAUDE.md gets auto-discovered by the
   subprocess and turns the strategist into an agentic coder. Fixed by
   running the subprocess with `cwd=/tmp` (no CLAUDE.md there).

If you see `error_max_turns` despite both fixes, a globally-configured MCP
server is leaking in. `claude_cli.py` already passes `--strict-mcp-config`,
but check your routine's connectors list — if you've attached anything
unnecessary (Notion, Figma, etc.), remove it.

**Routine session burns turns running `git status` / listing files**
Same root cause as #2 above (CLAUDE.md leaking into subprocess). The fix
is committed; if you see it again, verify `claude_cli.py` still passes
`cwd=SUBPROCESS_CWD`.

---

## Local dev (when you don't want a routine)

The CLI runs the same code path locally:

```bash
pip install -e .
python -m playwright install --with-deps chromium
aurealis-carousel generate ethos
aurealis-carousel generate ethos --topic "Becoming the man worth marrying"
```

Local runs use whichever auth your `claude` CLI is logged in with (`claude
login` to use Max). They write to `outputs/<brand>/<slug>/` but don't auto-
commit history.
