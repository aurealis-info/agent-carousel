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

echo "==> Python version"
python --version

echo "==> Installing aurealis-carousel package + dependencies"
pip install --upgrade pip
pip install -e .

echo "==> Resolving Chromium for Playwright"
# Some cloud envs (Anthropic Routines) ship Chromium pre-baked under
# /opt/pw-browsers/chromium-<rev>/chrome-linux/chrome but at a build that
# doesn't match the version Playwright would download. Two-step strategy:
#
# 1. Try `playwright install chromium`. If it succeeds, default discovery
#    works and we're done.
# 2. If that fails (network policy or version skew), fall back to whichever
#    Chromium is already on disk and export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
#    so render.py / layout_check.py call launch(executable_path=...).
if python -m playwright install chromium 2>/tmp/pw-install.err; then
  echo "  -> playwright-managed Chromium installed"
else
  echo "  -> playwright install failed; searching for preinstalled binary"
  cat /tmp/pw-install.err || true
  CHROMIUM_BIN="$(ls -1 /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1 || true)"
  if [ -z "$CHROMIUM_BIN" ]; then
    CHROMIUM_BIN="$(command -v chromium || command -v chromium-browser || command -v google-chrome || true)"
  fi
  if [ -z "$CHROMIUM_BIN" ]; then
    echo "ERROR: no Chromium found and playwright install failed" >&2
    exit 1
  fi
  echo "  -> falling back to: $CHROMIUM_BIN"
  # Persist for subsequent commands in the routine session.
  export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH="$CHROMIUM_BIN"
  if [ -n "${BASH_ENV:-}" ]; then
    echo "export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=\"$CHROMIUM_BIN\"" >> "$BASH_ENV"
  fi
  echo "export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=\"$CHROMIUM_BIN\"" >> "$HOME/.bashrc"
  echo "export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=\"$CHROMIUM_BIN\"" >> "$HOME/.profile"
fi

echo "==> Verifying CLI is on PATH"
which aurealis-carousel
aurealis-carousel --help | head -5

echo "==> Setup complete"
