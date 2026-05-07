"""Build font-face CSS for a chosen pairing + optional emphasis font.

Used by render.py — injected into the slide-shell template so Playwright loads
the right fonts. Two source modes are supported:

  - source: "google"  → emit @import url(https://fonts.googleapis.com/css2?...)
                        + a :root { --font-heading/body/emphasis } variable map.
  - source: "local"   → emit @font-face { src: url(file://...) } for each file.

Google Fonts is the default since it's commercial-safe and renders without
shipping font binaries in the repo.
"""
from pathlib import Path
from typing import Optional


def _format_for(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".otf":
        return "opentype"
    if ext == ".ttf":
        return "truetype"
    if ext == ".woff2":
        return "woff2"
    if ext == ".woff":
        return "woff"
    return "truetype"


def _local_font_face_rules(family: str, files: list[str], repo_root: Path) -> str:
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
    return "\n".join(rules)


def _google_import_url(families: list[str]) -> str:
    """Combine multiple family-spec strings into a single Google Fonts CSS2 URL.

    families is a list of strings like:
      ["Playfair+Display:ital,wght@0,700;0,900;1,700",
       "DM+Sans:wght@400;500;700"]
    The Google Fonts CSS2 endpoint accepts multiple `family=` query params.
    """
    qs = "&".join(f"family={fam}" for fam in families)
    return f"https://fonts.googleapis.com/css2?{qs}&display=swap"


def _block_for_font(spec: dict, css_var: str, repo_root: Path) -> str:
    """Produce the @font-face / @import block for one font (heading/body/emphasis)."""
    source = spec.get("source", "local")
    family = spec["family"]
    if source == "google":
        url = _google_import_url(spec["families"])
        return (
            f"@import url('{url}');\n"
            f":root {{ {css_var}: '{family}', sans-serif; }}"
        )
    files = spec["files"]
    rules = _local_font_face_rules(family, files, repo_root)
    return rules + f"\n:root {{ {css_var}: '{family}', sans-serif; }}"


def build_font_faces(
    pairing: dict,
    emphasis_font: Optional[dict] = None,
    *,
    repo_root: Optional[Path] = None,
    library: Optional[dict] = None,
) -> str:
    """Build the full font-face / @import block for a carousel.

    pairing: a single pairing entry from fonts/library.yaml (the primary).
    emphasis_font: optional dict with from_pairing, family, role; the family
                   is loaded from another pairing in the library.
    repo_root: absolute path to the repo (used for file:// URLs on local sources).
    library: parsed library.yaml — required if emphasis_font is set.
    """
    if repo_root is None:
        repo_root = Path.cwd()
    repo_root = Path(repo_root).resolve()

    blocks = []
    blocks.append(_block_for_font(pairing["heading"], "--font-heading", repo_root))
    blocks.append(_block_for_font(pairing["body"], "--font-body", repo_root))

    if emphasis_font and library:
        target = next(
            (p for p in library["pairings"] if p["id"] == emphasis_font["from_pairing"]),
            None,
        )
        if target:
            family = emphasis_font["family"]
            spec = None
            if target["heading"]["family"] == family:
                spec = dict(target["heading"])
            elif target["body"]["family"] == family:
                spec = dict(target["body"])
            if spec:
                blocks.append(_block_for_font(spec, "--font-emphasis", repo_root))

    return "\n\n".join(blocks)
