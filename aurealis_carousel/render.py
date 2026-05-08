"""HTML/CSS → 1080x1350 PNG via Playwright."""
import glob
import os
import tempfile
from pathlib import Path
from typing import Optional

from jinja2 import Template
from playwright.sync_api import sync_playwright

CANVAS_W, CANVAS_H = 1080, 1350

# Glob patterns Anthropic Routine cloud envs use for pre-baked Chromium.
# Both forms have been observed; we scan all of them for defense-in-depth.
_PW_BROWSERS_GLOBS = (
    "/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell",
    "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
)


def _resolve_chromium_executable() -> Optional[str]:
    """Return a Chromium executable path if PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
    is set or a pre-baked binary is found under /opt/pw-browsers, else None.

    Returning None means "let Playwright pick its bundled binary" — the right
    behavior for local dev where `playwright install` worked normally.
    """
    exe = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    if exe:
        return exe
    for pattern in _PW_BROWSERS_GLOBS:
        matches = sorted(glob.glob(pattern))
        if matches:
            return matches[0]
    return None


def _launch_chromium(p):
    exe = _resolve_chromium_executable()
    if exe:
        return p.chromium.launch(executable_path=exe)
    return p.chromium.launch()


def render_slide(
    *,
    slide_body: str,
    brand_css_path: Path,
    slide_shell_path: Path,
    output_path: Path,
    pairing_font_faces: Optional[str] = None,
) -> Path:
    """Render a slide body into a 1080x1350 PNG.

    pairing_font_faces is a string of @font-face rules to inject for the
    chosen primary pairing + emphasis font; loaded from local TTF/OTF
    files via file://.
    """
    template = Template(slide_shell_path.read_text())
    html = template.render(
        brand_css_path=str(brand_css_path),
        slide_body=slide_body,
        pairing_font_faces=pairing_font_faces or "",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, dir=output_path.parent
    ) as tmp:
        tmp.write(html)
        tmp_path = Path(tmp.name)

    try:
        with sync_playwright() as p:
            browser = _launch_chromium(p)
            ctx = browser.new_context(viewport={"width": CANVAS_W, "height": CANVAS_H})
            page = ctx.new_page()
            page.goto(f"file://{tmp_path}")
            page.wait_for_load_state("networkidle")
            page.evaluate("document.fonts.ready")  # defeat FOUT
            page.screenshot(
                path=str(output_path),
                clip={"x": 0, "y": 0, "width": CANVAS_W, "height": CANVAS_H},
            )
            browser.close()
    finally:
        tmp_path.unlink(missing_ok=True)
    return output_path
