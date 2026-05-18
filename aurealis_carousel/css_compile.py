"""Compile per-carousel CSS from writer's palette + the universal base.css.

Output is a single CSS string that the orchestrator writes to a temp file and
passes to render.render_slide as brand_css_path. This is the only place where
the writer's invented palette becomes real CSS variables.
"""
import re
from pathlib import Path

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
BASE_CSS_PATH = Path(__file__).parent / "base.css"


def _validate_hex(name: str, value: str) -> None:
    if not isinstance(value, str) or not HEX_RE.match(value):
        raise ValueError(f"invalid hex for {name!r}: {value!r} (expected #RRGGBB)")


def compile_carousel_css(palette: dict) -> str:
    """Return full CSS: writer's palette as :root vars + universal base.css.

    palette keys: bg, text, text_muted, accent. accent_alt is optional
    (falls back to accent).
    """
    required = ("bg", "text", "text_muted", "accent")
    for k in required:
        if k not in palette:
            raise ValueError(f"palette missing required key {k!r}; got {list(palette)}")
        _validate_hex(k, palette[k])

    accent_alt = palette.get("accent_alt", palette["accent"])
    _validate_hex("accent_alt", accent_alt)

    palette_block = (
        ":root {\n"
        f"  --color-bg: {palette['bg']};\n"
        f"  --color-text: {palette['text']};\n"
        f"  --color-text-muted: {palette['text_muted']};\n"
        f"  --color-primary: {palette['accent']};\n"
        f"  --color-secondary: {palette['accent']};\n"
        f"  --color-accent: {accent_alt};\n"
        "}\n"
    )

    base = BASE_CSS_PATH.read_text()
    return palette_block + "\n" + base
