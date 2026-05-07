from pathlib import Path

import yaml

from aurealis_carousel.font_faces import build_font_faces

REPO = Path(__file__).parent.parent
LIBRARY = REPO / "fonts" / "library.yaml"


def _library():
    return yaml.safe_load(LIBRARY.read_text())


def _pairing(library, pid):
    return next(p for p in library["pairings"] if p["id"] == pid)


def test_build_font_faces_emits_google_imports():
    """All v2 pairings are Google Fonts; build returns @import URLs + CSS variables."""
    lib = _library()
    pairing = _pairing(lib, "recoleta-berthold")
    css = build_font_faces(pairing, repo_root=REPO)
    assert "@import url('https://fonts.googleapis.com/css2?" in css
    assert pairing["heading"]["family"] in css
    assert pairing["body"]["family"] in css
    assert "--font-heading" in css
    assert "--font-body" in css


def test_build_font_faces_with_emphasis_font_includes_third_family():
    lib = _library()
    pairing = _pairing(lib, "recoleta-berthold")
    emphasis = {
        "from_pairing": "citadel-helvetica",
        "family": "Pinyon Script",
        "role": "hero-word-only",
    }
    css = build_font_faces(pairing, emphasis_font=emphasis, repo_root=REPO, library=lib)
    assert "Pinyon Script" in css
    assert "--font-emphasis" in css


def test_build_font_faces_omits_emphasis_when_none():
    lib = _library()
    pairing = _pairing(lib, "recoleta-berthold")
    css = build_font_faces(pairing, emphasis_font=None, repo_root=REPO)
    assert "--font-emphasis" not in css


def test_google_import_url_combines_multiple_families():
    """When pairing's heading and body each have multiple weight specs, both get included."""
    lib = _library()
    pairing = _pairing(lib, "inter-tempting")
    css = build_font_faces(pairing, repo_root=REPO)
    # Both Caveat (heading) and Inter (body) should be in the import URL set
    assert "Caveat" in css
    assert "Inter" in css
    # Each pairing-side gets its own @import line
    assert css.count("@import url(") == 2
