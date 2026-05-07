"""Build @font-face CSS rules for a chosen pairing + optional emphasis font.

Used by render.py — injected into the slide-shell template so Playwright
loads the actual local TTF/OTF font files instead of falling back to defaults.
"""
from pathlib import Path
from typing import Optional


def _format_for(file_path: str) -> str:
    """Infer the @font-face format() string from the file extension."""
    ext = Path(file_path).suffix.lower()
    if ext == ".otf":
        return "opentype"
    if ext == ".ttf":
        return "truetype"
    if ext == ".woff2":
        return "woff2"
    if ext == ".woff":
        return "woff"
    return "truetype"   # safe default


def _font_face_rules(family: str, files: list[str], css_var_name: str, repo_root: Path) -> str:
    """Generate @font-face rules + a CSS-variable mapping for a font family."""
    rules = []
    for f in files:
        abs_path = (repo_root / f).resolve()
        fmt = _format_for(f)
        rules.append(
            "@font-face {\n"
            f"  font-family: '{family}';\n"
            f"  src: url('file://{abs_path}') format('{fmt}');\n"
            "  font-display: swap;\n"
            "}"
        )
    # CSS variable that points to the loaded family (string-quoted)
    rules.append(f":root {{ {css_var_name}: '{family}', sans-serif; }}")
    return "\n".join(rules)


def build_font_faces(
    pairing: dict,
    emphasis_font: Optional[dict] = None,
    *,
    repo_root: Optional[Path] = None,
    library: Optional[dict] = None,
) -> str:
    """Build the full @font-face block for a carousel.

    pairing: a single pairing entry from fonts/library.yaml (the primary).
    emphasis_font: optional dict with from_pairing, family, role; the family
                   is loaded from another pairing in the library.
    repo_root: absolute path to the repo (so file:// URLs resolve correctly).
    library: parsed library.yaml — required if emphasis_font is set.
    """
    if repo_root is None:
        repo_root = Path.cwd()
    repo_root = Path(repo_root).resolve()

    blocks = []
    blocks.append(_font_face_rules(
        pairing["heading"]["family"], pairing["heading"]["files"],
        "--font-heading", repo_root,
    ))
    blocks.append(_font_face_rules(
        pairing["body"]["family"], pairing["body"]["files"],
        "--font-body", repo_root,
    ))

    if emphasis_font and library:
        target = next(
            (p for p in library["pairings"] if p["id"] == emphasis_font["from_pairing"]),
            None,
        )
        if target:
            family = emphasis_font["family"]
            files = []
            if target["heading"]["family"] == family:
                files = target["heading"]["files"]
            elif target["body"]["family"] == family:
                files = target["body"]["files"]
            if files:
                blocks.append(_font_face_rules(family, files, "--font-emphasis", repo_root))

    return "\n\n".join(blocks)
