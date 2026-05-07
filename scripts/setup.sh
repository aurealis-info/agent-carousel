#!/bin/bash
# Cloud routine setup script — runs once per cold session, then cached ~7 days.
# Anthropic-hosted routine environment runs this on first session start.
set -euo pipefail

# System deps for Chromium
apt-get update -qq
apt-get install -y --no-install-recommends \
    fonts-liberation libnss3 libgbm1 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxrandr2 libxss1 libxtst6 ca-certificates

# Python deps
uv pip install --system -r requirements.txt
uv pip install --system -e .

# Playwright Chromium
playwright install chromium
playwright install-deps chromium

echo "setup complete"
