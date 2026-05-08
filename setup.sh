#!/usr/bin/env bash
# setup.sh — installs runtime deps for aurealis-carousel.
#
# Runs once per Anthropic Routine cloud environment (cached ~7 days). If you
# update pyproject.toml or pin a new Playwright/Chromium version, the cache
# busts on the next routine run and this script re-runs.
#
# Local dev: you don't need to run this — pip install -e .[dev] + playwright
# install handle it. This script exists so the cloud env can self-provision.

set -euo pipefail

echo "==> Python version"
python --version

echo "==> Installing aurealis-carousel package + dependencies"
pip install --upgrade pip
pip install -e .

echo "==> Installing Playwright Chromium browser"
python -m playwright install --with-deps chromium

echo "==> Verifying CLI is on PATH"
which aurealis-carousel
aurealis-carousel --help | head -5

echo "==> Setup complete"
