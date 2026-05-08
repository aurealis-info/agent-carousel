#!/usr/bin/env bash
# setup.sh — installs runtime deps for aurealis-carousel.
#
# Runs once per Anthropic Routine cloud environment (cached ~7 days). If you
# update pyproject.toml, this script, or pin a new Playwright version, the
# cache busts on the next routine run and this re-runs.
#
# Local dev: you don't need to run this — pip install -e .[dev] + playwright
# install handle it. This script exists so the cloud env can self-provision.

set -euo pipefail

# ---------------------------------------------------------------------------
# 1. Pick a Python interpreter that satisfies pyproject's >=3.12 requirement.
#    Anthropic Routine cloud envs default `python`/`python3` to 3.11 even
#    though python3.12 / python3.13 exist on the path. So we search explicitly.
# ---------------------------------------------------------------------------
PYTHON=""
for py in python3.13 python3.12 python3 python; do
  if command -v "$py" >/dev/null 2>&1; then
    if "$py" -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
      PYTHON="$(command -v "$py")"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "ERROR: no Python >= 3.12 on PATH" >&2
  exit 1
fi
echo "==> Using interpreter: $PYTHON ($("$PYTHON" --version))"

# ---------------------------------------------------------------------------
# 2. Create a venv. Avoids PEP 668 ("externally-managed-environment") which
#    blocks system pip in the routine cloud env. The venv lives outside the
#    repo so re-cloning the repo per run doesn't wipe our installed deps.
# ---------------------------------------------------------------------------
VENV_DIR="$HOME/.venvs/aurealis-carousel"
if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "==> Creating venv at $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR"
fi

# Make the venv first on PATH for the rest of this script.
export PATH="$VENV_DIR/bin:$PATH"
hash -r

# Persist the PATH addition for subsequent shells in this routine session.
PATH_LINE="export PATH=\"$VENV_DIR/bin:\$PATH\""
for rcfile in "$HOME/.bashrc" "$HOME/.profile"; do
  if [ -f "$rcfile" ] || touch "$rcfile" 2>/dev/null; then
    grep -qsF "$VENV_DIR/bin" "$rcfile" || echo "$PATH_LINE" >> "$rcfile"
  fi
done
# BASH_ENV is sourced by non-interactive bash sessions (the kind the agent
# uses for tool calls). If it's set, append to it; if not, leave it alone.
if [ -n "${BASH_ENV:-}" ] && [ -f "$BASH_ENV" ]; then
  grep -qsF "$VENV_DIR/bin" "$BASH_ENV" || echo "$PATH_LINE" >> "$BASH_ENV"
fi

echo "==> Venv python: $(python --version)"

# ---------------------------------------------------------------------------
# 3. Install the package + deps into the venv.
# ---------------------------------------------------------------------------
echo "==> Installing aurealis-carousel package + dependencies"
pip install --upgrade pip --quiet
pip install -e .

# ---------------------------------------------------------------------------
# 4. Resolve Chromium for Playwright.
#    Routine cloud envs ship Chromium pre-baked under /opt/pw-browsers/ at a
#    build that may not match Playwright's expected revision. Strategy:
#      a. Try `playwright install chromium`. If it works, default discovery
#         picks up the bundled binary and we're done.
#      b. If that fails (network policy, version skew), fall back to whichever
#         Chromium is already on disk and export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
#         so render.py / layout_check.py call launch(executable_path=...).
# ---------------------------------------------------------------------------
echo "==> Resolving Chromium for Playwright"
if python -m playwright install chromium 2>/tmp/pw-install.err; then
  echo "  -> playwright-managed Chromium installed"
else
  echo "  -> playwright install failed; searching for preinstalled binary"
  cat /tmp/pw-install.err || true
  CHROMIUM_BIN=""
  for pattern in \
    "/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell" \
    "/opt/pw-browsers/chromium-*/chrome-linux/chrome"; do
    match="$(ls -1 $pattern 2>/dev/null | head -1 || true)"
    if [ -n "$match" ]; then
      CHROMIUM_BIN="$match"
      break
    fi
  done
  if [ -z "$CHROMIUM_BIN" ]; then
    CHROMIUM_BIN="$(command -v chromium || command -v chromium-browser || command -v google-chrome || true)"
  fi
  if [ -z "$CHROMIUM_BIN" ]; then
    echo "ERROR: no Chromium found and playwright install failed" >&2
    exit 1
  fi
  echo "  -> falling back to: $CHROMIUM_BIN"
  CHROMIUM_LINE="export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=\"$CHROMIUM_BIN\""
  export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH="$CHROMIUM_BIN"
  for rcfile in "$HOME/.bashrc" "$HOME/.profile"; do
    grep -qsF "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH" "$rcfile" || echo "$CHROMIUM_LINE" >> "$rcfile"
  done
  if [ -n "${BASH_ENV:-}" ] && [ -f "$BASH_ENV" ]; then
    grep -qsF "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH" "$BASH_ENV" || echo "$CHROMIUM_LINE" >> "$BASH_ENV"
  fi
fi

# ---------------------------------------------------------------------------
# 5. Verify the CLI is reachable.
# ---------------------------------------------------------------------------
echo "==> Verifying CLI is on PATH"
which aurealis-carousel
aurealis-carousel --help | head -5

echo "==> Setup complete"
